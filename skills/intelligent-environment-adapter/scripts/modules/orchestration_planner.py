#!/usr/bin/env python3
"""
编排规划模块
基于补齐计划，设计技能编排方案
支持多策略组合、风险分析、增量编排
"""

import json
import argparse
from typing import Dict, List, Any, Optional
from pathlib import Path


def analyze_risks(
    subtasks: List[Dict[str, Any]],
    dependencies: Dict[str, Any]
) -> Dict[str, Any]:
    """
    分析编排方案中的风险

    Args:
        subtasks: 子任务列表
        dependencies: 技能依赖关系

    Returns:
        风险分析报告
    """
    risks = []
    risk_levels = {
        "network_dependency": "low",
        "data_dependency": "low",
        "time_risk": "low"
    }

    # 分析网络依赖风险
    for subtask in subtasks:
        required_skills = subtask.get("required_skills", [])
        for skill in required_skills:
            if any(keyword in skill.lower() for keyword in ["fetcher", "api", "search", "scraper"]):
                if risk_levels["network_dependency"] == "low":
                    risk_levels["network_dependency"] = "medium"
                risks.append({
                    "type": "api_unavailable",
                    "subtask_id": subtask["id"],
                    "probability": 0.3,
                    "impact": "high",
                    "description": "技能需要外部API调用，可能因网络问题不可用",
                    "fallback_plan": "fallback_plans[0]"
                })
                break

    # 分析数据依赖风险
    for subtask in subtasks:
        if len(subtask.get("required_skills", [])) > 3:
            risk_levels["data_dependency"] = "medium"
            risks.append({
                "type": "data_format_error",
                "subtask_id": subtask["id"],
                "probability": 0.2,
                "impact": "medium",
                "description": "子任务需要多个技能，数据格式可能不匹配",
                "fallback_plan": "fallback_plans[0]"
            })

    # 分析时间风险
    if len(subtasks) > 3:
        risk_levels["time_risk"] = "high"
        risks.append({
            "type": "execution_timeout",
            "probability": 0.4,
            "impact": "high",
            "description": "子任务较多，可能超出时间预算",
            "fallback_plan": "fallback_plans[1]"
        })

    return {
        "network_dependency": risk_levels["network_dependency"],
        "data_dependency": risk_levels["data_dependency"],
        "time_risk": risk_levels["time_risk"],
        "risks": risks,
        "overall_risk_level": _calculate_overall_risk(risk_levels)
    }


def _calculate_overall_risk(risk_levels: Dict[str, str]) -> str:
    """计算整体风险等级"""
    if any(level == "high" for level in risk_levels.values()):
        return "high"
    elif any(level == "medium" for level in risk_levels.values()):
        return "medium"
    else:
        return "low"


def generate_fallback_plans(
    primary_plan: Dict[str, Any],
    task_profile: Dict[str, Any],
    environment_profile: Dict[str, Any],
    user_preferences: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    生成备选方案

    Args:
        primary_plan: 主方案
        task_profile: 任务画像
        environment_profile: 环境画像
        user_preferences: 用户偏好

    Returns:
        备选方案列表
    """
    fallback_plans = []

    # 备选方案1：简化策略（减少子任务数量）
    if len(primary_plan.get("subtasks", [])) > 2:
        simplified_subtasks = primary_plan["subtasks"][:2]
        fallback_plans.append({
            "name": "简化策略",
            "description": "减少子任务，快速执行",
            "subtasks": simplified_subtasks,
            "expected_improvement": 0.10,
            "estimated_time": 30,
            "complexity": "medium",
            "risk_level": "low",
            "recommended_for": ["快速场景", "时间敏感"],
            "trade_offs": "效果中等，但速度快"
        })

    # 备选方案2：最小策略（单步执行）
    fallback_plans.append({
        "name": "最小策略",
        "description": "只执行核心任务",
        "subtasks": [primary_plan.get("subtasks", [{}])[0] if primary_plan.get("subtasks") else {}],
        "expected_improvement": 0.05,
        "estimated_time": 10,
        "complexity": "low",
        "risk_level": "very_low",
        "recommended_for": ["保守场景", "资源受限"],
        "trade_offs": "效果最低，但最安全"
    })

    # 备选方案3：保守策略（跳过复杂任务）
    if user_preferences and user_preferences.get("remediation_preference") == "conservative":
        fallback_plans.append({
            "name": "保守策略",
            "description": "使用现有能力，不补齐",
            "subtasks": primary_plan["subtasks"][:1],
            "expected_improvement": 0.0,
            "estimated_time": 5,
            "complexity": "very_low",
            "risk_level": "none",
            "recommended_for": ["低风险场景"],
            "trade_offs": "无效果提升，但零风险"
        })

    return fallback_plans


def check_context_consistency(
    previous_orchestration: Dict[str, Any],
    task_profile: Dict[str, Any],
    environment_profile: Dict[str, Any]
) -> float:
    """
    检查上下文一致性

    Args:
        previous_orchestration: 上次编排方案
        task_profile: 当前任务画像
        environment_profile: 当前环境画像

    Returns:
        一致性分数（0-1）
    """
    consistency_score = 0.0

    # 检查任务类型是否一致
    prev_task_type = previous_orchestration.get("task_profile", {}).get("task_type", "")
    curr_task_type = task_profile.get("task_type", "")
    if prev_task_type == curr_task_type:
        consistency_score += 0.4

    # 检查领域是否一致
    prev_domain = set(previous_orchestration.get("task_profile", {}).get("domain", []))
    curr_domain = set(environment_profile.get("domain", []))
    if prev_domain == curr_domain:
        consistency_score += 0.3
    elif prev_domain & curr_domain:  # 有重叠
        consistency_score += 0.15

    # 检查复杂度是否一致
    prev_complexity = previous_orchestration.get("environment_profile", {}).get("complexity", "")
    curr_complexity = environment_profile.get("complexity", "")
    if prev_complexity == curr_complexity:
        consistency_score += 0.3

    return consistency_score


def apply_incremental_updates(
    previous_orchestration: Dict[str, Any],
    task_profile: Dict[str, Any],
    environment_profile: Dict[str, Any],
    strategy_preference: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    基于上次方案进行增量更新

    Args:
        previous_orchestration: 上次编排方案
        task_profile: 当前任务画像
        environment_profile: 当前环境画像
        strategy_preference: 策略偏好

    Returns:
        增量更新后的方案
    """
    consistency_score = check_context_consistency(
        previous_orchestration, task_profile, environment_profile
    )

    reuse_info = {
        "context_consistency": consistency_score,
        "reused_components": [],
        "updated_components": []
    }

    # 如果一致性高，复用上次方案的核心结构
    if consistency_score >= 0.7:
        reuse_info["reused_components"].append("subtask_structure")
        reuse_info["reused_components"].append("skill_dependencies")

        # 只更新时间预算等参数
        if strategy_preference and "time_budget" in strategy_preference:
            reuse_info["updated_components"].append("time_budget")

    else:
        # 一致性低，重新生成
        reuse_info["updated_components"].append("full_regeneration")

    return reuse_info


def decompose_task(
    task_profile: Dict[str, Any],
    environment_profile: Dict[str, Any],
    strategy_preference: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    将复杂任务分解为可执行的子任务

    Args:
        task_profile: 任务画像
        environment_profile: 环境画像
        strategy_preference: 策略偏好（可选）

    Returns:
        子任务列表
    """
    task_type = task_profile.get("task_type", "")
    domain = environment_profile.get("domain", [])
    data_type = environment_profile.get("data_type", "")
    complexity = environment_profile.get("complexity", "简单")

    # 根据用户偏好调整复杂度
    if strategy_preference:
        complexity_tolerance = strategy_preference.get("complexity_tolerance", "medium")
        if complexity_tolerance == "low" and complexity == "复杂":
            complexity = "中等"
        elif complexity_tolerance == "high" and complexity == "简单":
            complexity = "中等"

    subtasks = []

    # 根据任务类型分解
    if task_type == "深度分析":
        subtasks = [
            {
                "id": "subtask_1",
                "name": "数据获取",
                "description": "获取分析所需的原始数据",
                "required_skills": ["data_fetcher", "data_processor"],
                "input_format": {"type": "query", "description": "搜索查询"},
                "output_format": {"type": "structured_data", "description": "结构化数据"}
            },
            {
                "id": "subtask_2",
                "name": "数据分析",
                "description": "对数据进行深度分析",
                "required_skills": ["analyzer", "domain_expert"],
                "input_format": {"type": "structured_data", "description": "结构化数据"},
                "output_format": {"type": "analysis_result", "description": "分析结果"}
            },
            {
                "id": "subtask_3",
                "name": "结果呈现",
                "description": "生成分析报告",
                "required_skills": ["report_generator", "formatter"],
                "input_format": {"type": "analysis_result", "description": "分析结果"},
                "output_format": {"type": "report", "description": "最终报告"}
            }
        ]

    elif task_type == "内容创作":
        if data_type == "多模态":
            subtasks = [
                {
                    "id": "subtask_1",
                    "name": "内容规划",
                    "description": "规划内容结构和要点",
                    "required_skills": ["content_planner"],
                    "input_format": {"type": "requirements", "description": "创作需求"},
                    "output_format": {"type": "content_outline", "description": "内容大纲"}
                },
                {
                    "id": "subtask_2",
                    "name": "文本创作",
                    "description": "生成文本内容",
                    "required_skills": ["text_generator", "writer"],
                    "input_format": {"type": "content_outline", "description": "内容大纲"},
                    "output_format": {"type": "text_content", "description": "文本内容"}
                },
                {
                    "id": "subtask_3",
                    "name": "视觉创作",
                    "description": "生成图表和视觉元素",
                    "required_skills": ["image_generator", "chart_creator"],
                    "input_format": {"type": "text_content", "description": "文本内容"},
                    "output_format": {"type": "visual_elements", "description": "视觉元素"}
                },
                {
                    "id": "subtask_4",
                    "name": "组合输出",
                    "description": "组合文本和视觉元素",
                    "required_skills": ["content_composer", "formatter"],
                    "input_format": {"type": "multimodal_content", "description": "多模态内容"},
                    "output_format": {"type": "final_output", "description": "最终输出"}
                }
            ]
        else:
            subtasks = [
                {
                    "id": "subtask_1",
                    "name": "内容创作",
                    "description": "创作内容",
                    "required_skills": ["text_generator", "writer"],
                    "input_format": {"type": "requirements", "description": "创作需求"},
                    "output_format": {"type": "text_content", "description": "文本内容"}
                },
                {
                    "id": "subtask_2",
                    "name": "格式化输出",
                    "description": "格式化输出内容",
                    "required_skills": ["formatter"],
                    "input_format": {"type": "text_content", "description": "文本内容"},
                    "output_format": {"type": "final_output", "description": "最终输出"}
                }
            ]

    elif task_type == "实时监控":
        subtasks = [
            {
                "id": "subtask_1",
                "name": "数据采集",
                "description": "实时采集数据",
                "required_skills": ["realtime_fetcher", "api_integrator"],
                "input_format": {"type": "monitor_config", "description": "监控配置"},
                "output_format": {"type": "realtime_data", "description": "实时数据"}
            },
            {
                "id": "subtask_2",
                "name": "数据分析",
                "description": "实时分析数据",
                "required_skills": ["realtime_analyzer", "sentiment_analyzer"],
                "input_format": {"type": "realtime_data", "description": "实时数据"},
                "output_format": {"type": "analysis_result", "description": "分析结果"}
            },
            {
                "id": "subtask_3",
                "name": "结果汇总",
                "description": "汇总分析结果",
                "required_skills": ["result_aggregator", "visualizer"],
                "input_format": {"type": "analysis_result", "description": "分析结果"},
                "output_format": {"type": "final_report", "description": "最终报告"}
            }
        ]

    else:
        # 默认任务分解
        subtasks = [
            {
                "id": "subtask_1",
                "name": "任务执行",
                "description": "执行主要任务",
                "required_skills": ["general_processor"],
                "input_format": {"type": "task_input", "description": "任务输入"},
                "output_format": {"type": "task_output", "description": "任务输出"}
            }
        ]

    return subtasks


def analyze_skill_dependencies(
    subtasks: List[Dict[str, Any]],
    loaded_skills: List[str]
) -> Dict[str, Any]:
    """
    分析技能间的依赖关系

    Args:
        subtasks: 子任务列表
        loaded_skills: 已加载的技能列表

    Returns:
        技能依赖关系
    """
    dependencies = {}

    # 收集所有需要的技能
    all_required_skills = set()
    for subtask in subtasks:
        all_required_skills.update(subtask.get("required_skills", []))

    # 识别缺失的技能
    missing_skills = all_required_skills - set(loaded_skills)

    # 分析技能间的依赖关系
    for subtask in subtasks:
        subtask_id = subtask["id"]
        required_skills = subtask.get("required_skills", [])

        dependencies[subtask_id] = {
            "required_skills": required_skills,
            "missing_skills": [s for s in required_skills if s in missing_skills],
            "dependencies": []  # 子任务间的依赖关系
        }

    # 分析子任务间的依赖关系
    for i in range(len(subtasks)):
        if i > 0:
            current_subtask = subtasks[i]
            previous_subtask = subtasks[i - 1]

            # 检查输入输出格式是否匹配
            if current_subtask["input_format"]["type"] == previous_subtask["output_format"]["type"]:
                dependencies[current_subtask["id"]]["dependencies"].append(previous_subtask["id"])

    return dependencies


def design_execution_order(
    subtasks: List[Dict[str, Any]],
    dependencies: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    设计技能执行顺序（拓扑排序）

    Args:
        subtasks: 子任务列表
        dependencies: 技能依赖关系

    Returns:
        执行顺序
    """
    # 创建子任务ID到子任务的映射
    subtask_map = {subtask["id"]: subtask for subtask in subtasks}

    # 拓扑排序
    visited = set()
    result = []

    def visit(subtask_id):
        if subtask_id in visited:
            return

        visited.add(subtask_id)

        # 先访问依赖的子任务
        for dep_id in dependencies.get(subtask_id, {}).get("dependencies", []):
            visit(dep_id)

        # 添加到结果中
        result.append(subtask_map[subtask_id])

    # 访问所有子任务
    for subtask in subtasks:
        visit(subtask["id"])

    return result


def design_data_flow(
    execution_order: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    设计技能间的数据流

    Args:
        execution_order: 执行顺序

    Returns:
        数据流设计
    """
    data_flow = {}

    for i, subtask in enumerate(execution_order):
        subtask_id = subtask["id"]

        data_flow[subtask_id] = {
            "input": subtask["input_format"],
            "output": subtask["output_format"]
        }

        # 如果不是第一个子任务，添加数据来源
        if i > 0:
            previous_subtask = execution_order[i - 1]
            data_flow[subtask_id]["input_from"] = previous_subtask["id"]
            data_flow[subtask_id]["input_variable"] = f"${previous_subtask['id']}.output"

    return data_flow


def generate_orchestration_plan(
    remediation_plan: Dict[str, Any],
    environment_profile: Dict[str, Any],
    strategy_preference: Optional[Dict[str, Any]] = None,
    previous_orchestration: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    生成编排规划方案

    Args:
        remediation_plan: 补齐计划
        environment_profile: 环境画像
        strategy_preference: 策略偏好（可选）
        previous_orchestration: 上次编排方案（可选）

    Returns:
        编排规划方案
    """
    # 从环境画像中提取任务信息
    task_profile = {
        "task_type": environment_profile.get("task_type", ""),
        "domain": environment_profile.get("domain", []),
        "data_type": environment_profile.get("data_type", "")
    }

    # 获取已加载的技能
    loaded_skills = remediation_plan.get("current_skills", [])

    # 增量编排支持
    reuse_info = None
    if previous_orchestration:
        reuse_info = apply_incremental_updates(
            previous_orchestration, task_profile, environment_profile, strategy_preference
        )

    # 1. 任务分解
    subtasks = decompose_task(task_profile, environment_profile, strategy_preference)

    # 2. 技能依赖分析
    dependencies = analyze_skill_dependencies(subtasks, loaded_skills)

    # 3. 执行顺序设计
    execution_order = design_execution_order(subtasks, dependencies)

    # 4. 数据流设计
    data_flow = design_data_flow(execution_order)

    # 5. 风险分析
    risk_analysis = analyze_risks(subtasks, dependencies)

    # 6. 生成主方案
    primary_plan = {
        "task_decomposition": subtasks,
        "dependencies": dependencies,
        "execution_order": [{"id": s["id"], "name": s["name"]} for s in execution_order],
        "data_flow": data_flow,
        "estimated_complexity": len(subtasks),
        "expected_improvement": 0.18,
        "estimated_time": len(subtasks) * 40,  # 每个子任务40秒
        "complexity": "high" if len(subtasks) > 3 else "medium",
        "requires_additional_skills": any(
            len(dep.get("missing_skills", [])) > 0
            for dep in dependencies.values()
        )
    }

    # 7. 生成备选方案
    fallback_plans = generate_fallback_plans(
        primary_plan, task_profile, environment_profile, strategy_preference
    )

    # 8. 编排规划方案
    orchestration_plan = {
        "primary_plan": primary_plan,
        "fallback_plans": fallback_plans,
        "risk_analysis": risk_analysis,
        "meta": {
            "strategy_source": "agent_preferred" if strategy_preference else "default",
            "has_incremental_support": reuse_info is not None,
            "recommendation": "使用主方案获得最佳效果，或根据风险情况选择备选方案"
        }
    }

    # 9. 添加增量编排信息
    if reuse_info:
        orchestration_plan["reuse_info"] = reuse_info

    return orchestration_plan


def main():
    parser = argparse.ArgumentParser(description="编排规划模块")
    parser.add_argument("--remediation-plan", required=True, help="补齐计划JSON文件路径")
    parser.add_argument("--environment-profile", required=True, help="环境画像JSON文件路径")
    parser.add_argument("--strategy-preference", help="策略偏好JSON文件路径（可选）")
    parser.add_argument("--previous-orchestration", help="上次编排方案JSON文件路径（可选）")
    parser.add_argument("--output", required=True, help="输出文件路径")

    args = parser.parse_args()

    # 读取输入文件
    with open(args.remediation_plan, 'r', encoding='utf-8') as f:
        remediation_plan = json.load(f)

    with open(args.environment_profile, 'r', encoding='utf-8') as f:
        environment_profile = json.load(f)

    # 可选参数
    strategy_preference = None
    if args.strategy_preference:
        with open(args.strategy_preference, 'r', encoding='utf-8') as f:
            strategy_preference = json.load(f)

    previous_orchestration = None
    if args.previous_orchestration:
        with open(args.previous_orchestration, 'r', encoding='utf-8') as f:
            previous_orchestration = json.load(f)

    # 生成编排规划方案
    plan = generate_orchestration_plan(
        remediation_plan,
        environment_profile,
        strategy_preference,
        previous_orchestration
    )

    # 输出结果
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)

    print(f"编排规划方案已生成: {output_path}")
    print(f"主方案复杂度: {plan['primary_plan']['complexity']}")
    print(f"备选方案数量: {len(plan['fallback_plans'])}")
    print(f"整体风险等级: {plan['risk_analysis']['overall_risk_level']}")


if __name__ == "__main__":
    main()
