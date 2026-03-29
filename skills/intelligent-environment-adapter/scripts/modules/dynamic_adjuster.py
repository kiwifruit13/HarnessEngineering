"""
模块H：动态调整模块 (Dynamic Adjustment Module)

职责：根据执行状态生成调整方案
边界：不执行调整，只生成方案
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class AdjustmentType(Enum):
    """调整类型枚举"""
    SKILL_REPLACEMENT = "skill_replacement"
    PARAMETER_TUNING = "parameter_tuning"
    FALLBACK_SWITCH = "fallback_switch"
    WORKFLOW_SIMPLIFICATION = "workflow_simplification"
    INCREMENTAL_PLANNING = "incremental_planning"
    REVISIT_DIAGNOSIS = "revisit_diagnosis"


@dataclass
class AdjustmentPlan:
    """调整方案数据结构"""
    adjustment_type: str
    target_step: int
    original_action: Dict[str, Any]
    new_action: Dict[str, Any]
    reason: str
    expected_impact: Dict[str, str]
    updated_workflow: List[Dict[str, Any]]


class DynamicAdjuster:
    """
    动态调整模块
    
    职责边界：
    - ✅ 分析执行失败原因
    - ✅ 生成调整方案
    - ✅ 支持回溯建议
    - ❌ 不执行调整
    - ❌ 不直接调用其他模块
    """
    
    # 技能替换映射
    SKILL_REPLACEMENTS = {
        "data_fetcher": ["web_search", "api_client", "file_reader"],
        "legal_analyzer": ["doc_analyzer", "text_analyzer", "summarizer"],
        "report_generator": ["template_writer", "markdown_generator", "doc_creator"],
        "web_search": ["data_fetcher", "knowledge_base_search"],
        "image_generator": ["template_image", "chart_generator"]
    }

    def __init__(self):
        pass

    def execute(self, input_data: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        模块执行入口
        
        Args:
            input_data: {
                "execution_status": dict,          # 执行状态
                "adjustment_suggestion": dict,     # 监控模块的建议
                "orchestration_plan": dict,        # 当前编排方案
                "environment_profile": dict,       # 环境画像
                "available_skills": list           # 可用技能列表
            }
        
        Returns:
            {
                "adjustment_plan": AdjustmentPlan or None,
                "revisit_request": dict or None    # 回溯请求（如果需要）
            }
        """
        execution_status = input_data.get("execution_status", {})
        adjustment_suggestion = input_data.get("adjustment_suggestion", {})
        orchestration_plan = input_data.get("orchestration_plan", {})
        environment_profile = input_data.get("environment_profile", {})
        available_skills = input_data.get("available_skills", [])
        
        adjustment_type = adjustment_suggestion.get("adjustment_type", "complex")
        
        # 如果需要回溯
        if adjustment_type == "revisit":
            return self._generate_revisit_request(execution_status, environment_profile)
        
        # 根据错误类型生成调整方案
        error_type = self._get_error_type(execution_status)
        
        if adjustment_type == "simple":
            plan = self._generate_simple_adjustment(
                error_type, 
                execution_status, 
                orchestration_plan,
                available_skills
            )
        else:
            plan = self._generate_complex_adjustment(
                error_type,
                execution_status,
                orchestration_plan,
                environment_profile,
                available_skills
            )
        
        return {
            "adjustment_plan": plan,
            "revisit_request": None
        }

    def _get_error_type(self, execution_status: Dict[str, Any]) -> str:
        """获取错误类型"""
        error = execution_status.get("error", {})
        return error.get("type", "unknown")

    def _generate_revisit_request(
        self, 
        execution_status: Dict[str, Any],
        environment_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成回溯请求"""
        context = execution_status.get("context", {})
        error = execution_status.get("error", {})
        
        return {
            "adjustment_plan": None,
            "revisit_request": {
                "action": "revisit_diagnosis",
                "target_module": "shortage_diagnosis",
                "reason": error.get("message", "发现新的能力短板"),
                "new_context": {
                    "additional_capability_needed": context.get("new_capability"),
                    "execution_feedback": {
                        "failed_step": execution_status.get("current_step"),
                        "failed_skill": execution_status.get("skill")
                    }
                },
                "estimated_cost": {
                    "time": 30,
                    "tokens": 2000
                }
            }
        }

    def _generate_simple_adjustment(
        self,
        error_type: str,
        execution_status: Dict[str, Any],
        orchestration_plan: Dict[str, Any],
        available_skills: List[str]
    ) -> Optional[Dict[str, Any]]:
        """生成简单调整方案"""
        current_step = execution_status.get("current_step", 1)
        failed_skill = execution_status.get("skill", "")
        
        workflow = orchestration_plan.get("workflow", [])
        
        # 技能替换
        if error_type in ["skill_unavailable", "capability_not_found"]:
            replacement = self._find_skill_replacement(failed_skill, available_skills)
            if replacement:
                return self._create_skill_replacement_plan(
                    current_step,
                    failed_skill,
                    replacement,
                    workflow
                )
        
        # 参数调整
        if error_type == "parameter_error":
            return self._create_parameter_tuning_plan(current_step, workflow)
        
        # 超时处理
        if error_type == "skill_timeout":
            return self._create_timeout_handling_plan(current_step, failed_skill, workflow)
        
        # 切换备选方案
        fallback_plans = orchestration_plan.get("fallback_plans", [])
        if fallback_plans:
            return self._create_fallback_switch_plan(current_step, fallback_plans[0])
        
        return None

    def _generate_complex_adjustment(
        self,
        error_type: str,
        execution_status: Dict[str, Any],
        orchestration_plan: Dict[str, Any],
        environment_profile: Dict[str, Any],
        available_skills: List[str]
    ) -> Optional[Dict[str, Any]]:
        """生成复杂调整方案"""
        current_step = execution_status.get("current_step", 1)
        failed_skill = execution_status.get("skill", "")
        workflow = orchestration_plan.get("workflow", [])
        
        # 数据格式不匹配
        if error_type == "data_format_mismatch":
            return self._create_adapter_insertion_plan(current_step, workflow)
        
        # 依赖缺失
        if error_type == "dependency_missing":
            return self._create_dependency_fix_plan(current_step, workflow)
        
        # 输出质量问题
        if error_type == "output_quality_poor":
            return self._create_quality_enhancement_plan(current_step, workflow)
        
        # 默认：尝试技能替换
        replacement = self._find_skill_replacement(failed_skill, available_skills)
        if replacement:
            return self._create_skill_replacement_plan(
                current_step,
                failed_skill,
                replacement,
                workflow
            )
        
        # 最后手段：工作流简化
        return self._create_workflow_simplification_plan(current_step, workflow)

    def _find_skill_replacement(self, failed_skill: str, available_skills: List[str]) -> Optional[str]:
        """查找技能替换"""
        replacements = self.SKILL_REPLACEMENTS.get(failed_skill, [])
        
        for replacement in replacements:
            if replacement in available_skills:
                return replacement
        
        return None

    def _create_skill_replacement_plan(
        self,
        step: int,
        original_skill: str,
        replacement_skill: str,
        workflow: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """创建技能替换方案"""
        updated_workflow = []
        
        for w_step in workflow:
            if w_step.get("step") == step:
                updated_step = w_step.copy()
                updated_step["skill"] = replacement_skill
                updated_step["adjustment_note"] = f"从 {original_skill} 替换为 {replacement_skill}"
                updated_workflow.append(updated_step)
            else:
                updated_workflow.append(w_step)
        
        return {
            "adjustment_type": "skill_replacement",
            "target_step": step,
            "original_action": {"skill": original_skill},
            "new_action": {"skill": replacement_skill},
            "reason": f"{original_skill} 执行失败，使用 {replacement_skill} 替代",
            "expected_impact": {
                "quality": "slight_decrease",
                "time": "similar"
            },
            "updated_workflow": updated_workflow
        }

    def _create_parameter_tuning_plan(self, step: int, workflow: List[Dict[str, Any]]) -> Dict[str, Any]:
        """创建参数调整方案"""
        current_step_data = next((s for s in workflow if s.get("step") == step), {})
        original_params = current_step_data.get("params", {})
        
        # 简化参数
        tuned_params = {k: v for k, v in original_params.items() 
                       if k in ["query", "input", "data"]}
        
        return {
            "adjustment_type": "parameter_tuning",
            "target_step": step,
            "original_action": {"params": original_params},
            "new_action": {"params": tuned_params},
            "reason": "参数配置错误，简化参数后重试",
            "expected_impact": {
                "quality": "similar",
                "time": "faster"
            },
            "updated_workflow": workflow
        }

    def _create_timeout_handling_plan(
        self, 
        step: int, 
        skill: str,
        workflow: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """创建超时处理方案"""
        return {
            "adjustment_type": "parameter_tuning",
            "target_step": step,
            "original_action": {"skill": skill, "timeout": "default"},
            "new_action": {"skill": skill, "timeout": "extended", "retry": 3},
            "reason": "执行超时，增加超时时间并添加重试机制",
            "expected_impact": {
                "quality": "similar",
                "time": "longer"
            },
            "updated_workflow": workflow
        }

    def _create_fallback_switch_plan(self, step: int, fallback: Dict[str, Any]) -> Dict[str, Any]:
        """创建备选方案切换计划"""
        return {
            "adjustment_type": "fallback_switch",
            "target_step": step,
            "original_action": {"workflow": "primary"},
            "new_action": {"workflow": "fallback", "fallback_id": fallback.get("id")},
            "reason": "主方案执行失败，切换到备选方案",
            "expected_impact": {
                "quality": "acceptable",
                "time": "varies"
            },
            "updated_workflow": fallback.get("workflow", [])
        }

    def _create_adapter_insertion_plan(self, step: int, workflow: List[Dict[str, Any]]) -> Dict[str, Any]:
        """创建适配器插入方案"""
        updated_workflow = []
        
        for w_step in workflow:
            if w_step.get("step") == step:
                # 在当前步骤前插入适配器步骤
                adapter_step = {
                    "step": step,
                    "type": "adapter",
                    "description": "数据格式转换",
                    "action": "transform_data_format",
                    "output": f"adapted_data_{step}"
                }
                updated_workflow.append(adapter_step)
                
                # 更新原步骤
                updated_step = w_step.copy()
                updated_step["step"] = step + 1
                updated_step["input"] = f"adapted_data_{step}"
                updated_workflow.append(updated_step)
            else:
                if w_step.get("step", 0) > step:
                    updated_step = w_step.copy()
                    updated_step["step"] = updated_step["step"] + 1
                    updated_workflow.append(updated_step)
                else:
                    updated_workflow.append(w_step)
        
        return {
            "adjustment_type": "incremental_planning",
            "target_step": step,
            "original_action": {},
            "new_action": {"insert_adapter": True},
            "reason": "数据格式不匹配，插入适配器进行转换",
            "expected_impact": {
                "quality": "similar",
                "time": "slightly_longer"
            },
            "updated_workflow": updated_workflow
        }

    def _create_dependency_fix_plan(self, step: int, workflow: List[Dict[str, Any]]) -> Dict[str, Any]:
        """创建依赖修复方案"""
        return {
            "adjustment_type": "incremental_planning",
            "target_step": step,
            "original_action": {},
            "new_action": {"add_dependency_step": True},
            "reason": "依赖缺失，添加前置步骤安装/准备依赖",
            "expected_impact": {
                "quality": "similar",
                "time": "longer"
            },
            "updated_workflow": workflow
        }

    def _create_quality_enhancement_plan(self, step: int, workflow: List[Dict[str, Any]]) -> Dict[str, Any]:
        """创建质量增强方案"""
        return {
            "adjustment_type": "parameter_tuning",
            "target_step": step,
            "original_action": {},
            "new_action": {
                "add_validation": True,
                "quality_check": True,
                "fallback_on_low_quality": True
            },
            "reason": "输出质量不佳，添加质量检查和回退机制",
            "expected_impact": {
                "quality": "improved",
                "time": "longer"
            },
            "updated_workflow": workflow
        }

    def _create_workflow_simplification_plan(self, step: int, workflow: List[Dict[str, Any]]) -> Dict[str, Any]:
        """创建工作流简化方案"""
        # 跳过非关键步骤
        simplified_workflow = [s for s in workflow if s.get("step", 0) < step or s.get("critical", True)]
        
        return {
            "adjustment_type": "workflow_simplification",
            "target_step": step,
            "original_action": {"workflow": "full"},
            "new_action": {"workflow": "simplified"},
            "reason": "工作流复杂度过高，简化非关键步骤",
            "expected_impact": {
                "quality": "acceptable",
                "time": "faster"
            },
            "updated_workflow": simplified_workflow
        }


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="动态调整模块")
    parser.add_argument("--execution-status", required=True, help="执行状态JSON文件")
    parser.add_argument("--adjustment-suggestion", required=True, help="监控建议JSON文件")
    parser.add_argument("--orchestration-plan", required=True, help="编排方案JSON文件")
    parser.add_argument("--environment-profile", help="环境画像JSON文件")
    parser.add_argument("--available-skills", help="可用技能JSON文件")
    parser.add_argument("--output", required=True, help="输出文件路径")
    
    args = parser.parse_args()
    
    # 读取输入
    with open(args.execution_status, 'r', encoding='utf-8') as f:
        execution_status = json.load(f)
    
    with open(args.adjustment_suggestion, 'r', encoding='utf-8') as f:
        adjustment_suggestion = json.load(f)
    
    with open(args.orchestration_plan, 'r', encoding='utf-8') as f:
        orchestration_plan = json.load(f)
    
    input_data = {
        "execution_status": execution_status,
        "adjustment_suggestion": adjustment_suggestion,
        "orchestration_plan": orchestration_plan
    }
    
    if args.environment_profile:
        with open(args.environment_profile, 'r', encoding='utf-8') as f:
            input_data["environment_profile"] = json.load(f)
    
    if args.available_skills:
        with open(args.available_skills, 'r', encoding='utf-8') as f:
            input_data["available_skills"] = json.load(f)
    
    # 执行
    adjuster = DynamicAdjuster()
    result = adjuster.execute(input_data)
    
    # 输出
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    if result.get("revisit_request"):
        print(f"建议回溯到短板诊断模块")
    elif result.get("adjustment_plan"):
        print(f"生成调整方案: {result['adjustment_plan']['adjustment_type']}")
    else:
        print("无法生成调整方案")


if __name__ == "__main__":
    main()
