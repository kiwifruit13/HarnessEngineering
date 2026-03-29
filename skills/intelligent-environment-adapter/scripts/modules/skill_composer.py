#!/usr/bin/env python3
"""
技能组合模块
基于编排规划方案，生成可执行的技能组合
支持多方案输出和错误诊断
"""

import json
import argparse
from typing import Dict, List, Any
from pathlib import Path


def match_skills(
    required_skills: List[str],
    available_skills: List[Dict[str, Any]]
) -> Dict[str, Dict[str, Any]]:
    """
    匹配所需的技能

    Args:
        required_skills: 需要的技能列表
        available_skills: 可用的技能列表

    Returns:
        技能匹配结果
    """
    matches = {}

    for required in required_skills:
        # 查找匹配的技能
        candidates = [
            skill for skill in available_skills
            if required in skill.get("capabilities", [])
        ]

        # 选择最佳匹配（优先选择高评分的技能）
        if candidates:
            best_match = max(
                candidates,
                key=lambda s: s.get("rating", 0)
            )
            matches[required] = {
                "skill_name": best_match.get("name", ""),
                "skill_id": best_match.get("id", ""),
                "match_score": 1.0,
                "capabilities": best_match.get("capabilities", [])
            }
        else:
            # 没有找到匹配的技能
            matches[required] = {
                "skill_name": "",
                "skill_id": "",
                "match_score": 0.0,
                "status": "not_found",
                "suggestion": f"搜索技能: {required}"
            }

    return matches


def generate_adapters(
    subtask_a: Dict[str, Any],
    subtask_b: Dict[str, Any],
    skill_a: Dict[str, Any],
    skill_b: Dict[str, Any]
) -> Dict[str, Any]:
    """
    生成技能间的适配器

    Args:
        subtask_a: 前一个子任务
        subtask_b: 后一个子任务
        skill_a: 前一个技能
        skill_b: 后一个技能

    Returns:
        适配器配置
    """
    adapter = {
        "type": "data_transform",
        "input_from": f"${subtask_a['id']}.output",
        "output_to": f"${subtask_b['id']}.input",
        "transformations": []
    }

    # 检查输入输出格式是否需要转换
    output_format_a = subtask_a.get("output_format", {})
    input_format_b = subtask_b.get("input_format", {})

    if output_format_a.get("type") != input_format_b.get("type"):
        # 需要格式转换
        adapter["transformations"].append({
            "type": "format_conversion",
            "from": output_format_a.get("type"),
            "to": input_format_b.get("type")
        })

    # 检查是否需要数据映射
    if output_format_a.get("description") != input_format_b.get("description"):
        adapter["transformations"].append({
            "type": "data_mapping",
            "mapping_rules": "auto_generate"
        })

    # 如果不需要转换，标记为直通
    if not adapter["transformations"]:
        adapter["type"] = "pass_through"

    return adapter


def generate_plan_execution_details(
    plan: Dict[str, Any],
    available_skills: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    生成单个方案的执行详情

    Args:
        plan: 编排方案（主方案或备选方案）
        available_skills: 可用的技能列表

    Returns:
        执行详情
    """
    subtasks = plan.get("task_decomposition", plan.get("subtasks", []))
    execution_order = plan.get("execution_order", [])
    data_flow = plan.get("data_flow", {})

    # 收集所有需要的技能
    all_required_skills = set()
    for subtask in subtasks:
        all_required_skills.update(subtask.get("required_skills", []))

    # 匹配技能
    skill_matches = match_skills(list(all_required_skills), available_skills)

    # 生成工作流
    workflow = []
    skills_to_load = set()
    adapters = []

    for i, order_item in enumerate(execution_order):
        subtask_id = order_item["id"]
        subtask = next((s for s in subtasks if s["id"] == subtask_id), None)

        if not subtask:
            continue

        required_skills = subtask.get("required_skills", [])
        matched_skills_for_subtask = []

        # 为每个子任务匹配技能
        for required_skill in required_skills:
            match_result = skill_matches.get(required_skill, {})
            if match_result.get("match_score", 0) > 0:
                matched_skills_for_subtask.append(match_result)
                skills_to_load.add(match_result.get("skill_id", ""))

        # 构建工作流步骤
        workflow_step = {
            "step": i + 1,
            "subtask_id": subtask_id,
            "subtask_name": subtask.get("name", ""),
            "required_skills": required_skills,
            "matched_skills": matched_skills_for_subtask,
            "action": "load_and_execute",
            "params": {
                "input": data_flow.get(subtask_id, {}).get("input", {}),
                "input_from": data_flow.get(subtask_id, {}).get("input_from")
            },
            "output": data_flow.get(subtask_id, {}).get("output", {})
        }

        workflow.append(workflow_step)

        # 如果不是第一个步骤，生成适配器
        if i > 0:
            previous_step = workflow[i - 1]
            current_step = workflow_step

            previous_subtask = next(
                (s for s in subtasks if s["id"] == previous_step["subtask_id"]),
                None
            )

            if previous_subtask and subtask:
                adapter = generate_adapters(
                    previous_subtask,
                    subtask,
                    previous_step.get("matched_skills", [{}])[0],
                    current_step.get("matched_skills", [{}])[0]
                )
                adapter["between_steps"] = f"{i} -> {i + 1}"
                adapters.append(adapter)

    # 生成执行指南
    execution_guide = {
        "entry_point": workflow[0]["subtask_id"] if workflow else None,
        "exit_point": workflow[-1]["subtask_id"] if workflow else None,
        "total_steps": len(workflow),
        "estimated_time": f"{plan.get('estimated_time', len(workflow) * 40)}秒",
        "estimated_tokens": f"{len(workflow) * 1000}-{len(workflow) * 2000}",
        "expected_output": workflow[-1]["output"] if workflow else None
    }

    return {
        "workflow": workflow,
        "skills_to_load": list(skills_to_load),
        "adapters": adapters,
        "skill_matches": skill_matches,
        "execution_guide": execution_guide,
        "metadata": {
            "total_subtasks": len(subtasks),
            "matched_skills_count": len([s for s in skill_matches.values() if s.get("match_score", 0) > 0]),
            "missing_skills_count": len([s for s in skill_matches.values() if s.get("match_score", 0) == 0]),
            "requires_additional_skills": len([s for s in skill_matches.values() if s.get("match_score", 0) == 0]) > 0
        }
    }


def generate_error_diagnosis(
    orchestration_plan: Dict[str, Any]
) -> Dict[str, Any]:
    """
    生成错误诊断信息

    Args:
        orchestration_plan: 编排规划方案

    Returns:
        错误诊断信息
    """
    error_diagnosis = {
        "potential_errors": [],
        "recommendations": []
    }

    risk_analysis = orchestration_plan.get("risk_analysis", {})
    risks = risk_analysis.get("risks", [])

    # 为每个风险生成错误诊断
    for risk in risks:
        error_type = risk.get("type")
        error_diagnosis["potential_errors"].append({
            "error_type": error_type,
            "probability": risk.get("probability"),
            "impact": risk.get("impact"),
            "possible_causes": _get_error_causes(error_type),
            "recommended_solutions": _get_error_solutions(error_type)
        })

    # 添加通用建议
    if risk_analysis.get("overall_risk_level") == "high":
        error_diagnosis["recommendations"].append({
            "type": "use_fallback",
            "message": "建议使用备选方案以降低风险",
            "fallback_plan_index": 0
        })

    return error_diagnosis


def _get_error_causes(error_type: str) -> List[str]:
    """获取错误可能原因"""
    causes_map = {
        "api_unavailable": ["网络连接不稳定", "外部API服务暂时不可用", "API密钥过期或无效"],
        "data_format_error": ["数据源格式不一致", "字段缺失或类型错误", "编码问题"],
        "execution_timeout": ["子任务过多", "网络延迟", "数据量过大"]
    }
    return causes_map.get(error_type, ["未知原因"])


def _get_error_solutions(error_type: str) -> List[str]:
    """获取错误推荐解决方案"""
    solutions_map = {
        "api_unavailable": ["重试操作", "检查网络连接", "使用备用数据源", "切换到备选方案"],
        "data_format_error": ["检查数据格式规范", "使用数据转换工具", "联系数据提供方", "切换到备选方案"],
        "execution_timeout": ["简化任务", "增加时间预算", "使用并行处理", "切换到备选方案"]
    }
    return solutions_map.get(error_type, ["联系技术支持"])


def generate_orchestration_result(
    orchestration_plan: Dict[str, Any],
    available_skills: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    生成技能编排方案（包含主方案和备选方案）

    Args:
        orchestration_plan: 编排规划方案
        available_skills: 可用的技能列表

    Returns:
        技能编排方案
    """
    # 生成主方案的执行详情
    primary_plan = orchestration_plan.get("primary_plan", {})
    primary_execution = generate_plan_execution_details(primary_plan, available_skills)

    # 生成备选方案的执行详情
    fallback_plans = orchestration_plan.get("fallback_plans", [])
    fallback_executions = []

    for fallback_plan in fallback_plans:
        fallback_execution = generate_plan_execution_details(fallback_plan, available_skills)
        fallback_execution["plan_metadata"] = {
            "name": fallback_plan.get("name"),
            "description": fallback_plan.get("description"),
            "expected_improvement": fallback_plan.get("expected_improvement"),
            "estimated_time": fallback_plan.get("estimated_time"),
            "complexity": fallback_plan.get("complexity"),
            "risk_level": fallback_plan.get("risk_level"),
            "recommended_for": fallback_plan.get("recommended_for"),
            "trade_offs": fallback_plan.get("trade_offs")
        }
        fallback_executions.append(fallback_execution)

    # 生成错误诊断
    error_diagnosis = generate_error_diagnosis(orchestration_plan)

    # 生成技能编排方案
    orchestration_result = {
        "primary_plan": {
            "orchestration_plan": {
                "workflow": primary_execution["workflow"],
                "skills_to_load": primary_execution["skills_to_load"],
                "adapters": primary_execution["adapters"],
                "skill_matches": primary_execution["skill_matches"]
            },
            "execution_guide": primary_execution["execution_guide"],
            "metadata": primary_execution["metadata"]
        },
        "fallback_plans": fallback_executions,
        "risk_analysis": orchestration_plan.get("risk_analysis", {}),
        "error_diagnosis": error_diagnosis,
        "meta": orchestration_plan.get("meta", {}),
        "total_plans": 1 + len(fallback_executions)
    }

    # 添加增量编排信息
    if "reuse_info" in orchestration_plan:
        orchestration_result["reuse_info"] = orchestration_plan["reuse_info"]

    return orchestration_result


def main():
    parser = argparse.ArgumentParser(description="技能组合模块")
    parser.add_argument("--orchestration-plan", required=True, help="编排规划方案JSON文件路径")
    parser.add_argument("--available-skills", required=True, help="可用技能列表JSON文件路径")
    parser.add_argument("--output", required=True, help="输出文件路径")

    args = parser.parse_args()

    # 读取输入文件
    with open(args.orchestration_plan, 'r', encoding='utf-8') as f:
        orchestration_plan = json.load(f)

    with open(args.available_skills, 'r', encoding='utf-8') as f:
        available_skills = json.load(f)

    # 生成技能编排方案
    result = generate_orchestration_result(orchestration_plan, available_skills)

    # 输出结果
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"技能编排方案已生成: {output_path}")
    print(f"主方案步骤数: {result['primary_plan']['execution_guide']['total_steps']}")
    print(f"备选方案数量: {len(result['fallback_plans'])}")
    print(f"整体风险等级: {result['risk_analysis']['overall_risk_level']}")


if __name__ == "__main__":
    main()
