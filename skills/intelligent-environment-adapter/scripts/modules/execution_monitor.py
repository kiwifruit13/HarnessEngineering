"""
模块G：执行监控模块 (Execution Monitoring Module)

职责：接收执行状态，判断是否需要调整方案
边界：不执行调整，只提供建议
"""

import json
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class ExecutionStatus(Enum):
    """执行状态枚举"""
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    NEW_REQUIREMENT = "new_requirement"


@dataclass
class AdjustmentSuggestion:
    """调整建议数据结构"""
    need_adjustment: bool
    adjustment_type: str       # simple/complex/revisit
    reason: str
    suggested_action: str
    urgency: str               # high/medium/low


class ExecutionMonitor:
    """
    执行监控模块
    
    职责边界：
    - ✅ 接收执行状态
    - ✅ 分析问题类型
    - ✅ 判断是否需要调整
    - ❌ 不执行调整
    - ❌ 不生成详细调整方案
    """
    
    # 简单问题类型（本地可处理）
    SIMPLE_ISSUES = [
        "skill_unavailable",
        "skill_timeout",
        "parameter_error",
        "rate_limit",
        "network_error"
    ]
    
    # 复杂问题类型（需要动态调整）
    COMPLEX_ISSUES = [
        "capability_not_found",
        "data_format_mismatch",
        "dependency_missing",
        "output_quality_poor"
    ]
    
    # 需要回溯诊断的问题类型
    REVISIT_ISSUES = [
        "new_capability_needed",
        "environment_changed",
        "all_fallbacks_failed"
    ]

    def __init__(self):
        pass

    def execute(self, input_data: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        模块执行入口
        
        Args:
            input_data: {
                "execution_status": {
                    "execution_id": str,
                    "current_step": int,
                    "total_steps": int,
                    "skill": str,
                    "status": str,           # running/success/failed/timeout/new_requirement
                    "error": dict,           # 可选
                    "context": dict          # 可选
                },
                "orchestration_plan": dict   # 当前编排方案
            }
        
        Returns:
            {
                "need_adjustment": bool,
                "adjustment_suggestion": AdjustmentSuggestion
            }
        """
        execution_status = input_data.get("execution_status", {})
        orchestration_plan = input_data.get("orchestration_plan", {})
        
        status = execution_status.get("status", "")
        
        # 成功状态不需要调整
        if status == "success":
            return {
                "need_adjustment": False,
                "adjustment_suggestion": {
                    "need_adjustment": False,
                    "adjustment_type": "none",
                    "reason": "执行成功，无需调整",
                    "suggested_action": "继续执行下一步",
                    "urgency": "none"
                }
            }
        
        # 运行中状态不需要调整
        if status == "running":
            return {
                "need_adjustment": False,
                "adjustment_suggestion": {
                    "need_adjustment": False,
                    "adjustment_type": "none",
                    "reason": "正在执行中",
                    "suggested_action": "等待执行完成",
                    "urgency": "none"
                }
            }
        
        # 分析问题类型
        error_type = self._classify_error(execution_status)
        
        # 判断调整类型
        adjustment_type = self._determine_adjustment_type(error_type)
        
        # 生成建议
        suggestion = self._generate_suggestion(
            error_type, 
            adjustment_type, 
            execution_status,
            orchestration_plan
        )
        
        return {
            "need_adjustment": suggestion.need_adjustment,
            "adjustment_suggestion": {
                "need_adjustment": suggestion.need_adjustment,
                "adjustment_type": suggestion.adjustment_type,
                "reason": suggestion.reason,
                "suggested_action": suggestion.suggested_action,
                "urgency": suggestion.urgency
            }
        }

    def _classify_error(self, execution_status: Dict[str, Any]) -> str:
        """分类错误类型"""
        error = execution_status.get("error", {})
        status = execution_status.get("status", "")
        
        if status == "timeout":
            return "skill_timeout"
        
        if status == "new_requirement":
            return "new_capability_needed"
        
        if not error:
            return "unknown"
        
        # 根据错误信息判断类型
        error_type = error.get("type", "")
        error_message = error.get("message", "").lower()
        
        if error_type:
            return error_type
        
        # 基于错误信息推断类型
        if "not found" in error_message or "不存在" in error_message:
            return "capability_not_found"
        if "timeout" in error_message or "超时" in error_message:
            return "skill_timeout"
        if "rate limit" in error_message or "限制" in error_message:
            return "rate_limit"
        if "network" in error_message or "网络" in error_message:
            return "network_error"
        if "parameter" in error_message or "参数" in error_message:
            return "parameter_error"
        if "format" in error_message or "格式" in error_message:
            return "data_format_mismatch"
        if "unavailable" in error_message or "不可用" in error_message:
            return "skill_unavailable"
        
        return "unknown_error"

    def _determine_adjustment_type(self, error_type: str) -> str:
        """确定调整类型"""
        if error_type in self.SIMPLE_ISSUES:
            return "simple"
        elif error_type in self.COMPLEX_ISSUES:
            return "complex"
        elif error_type in self.REVISIT_ISSUES:
            return "revisit"
        else:
            return "complex"  # 默认复杂类型

    def _generate_suggestion(
        self,
        error_type: str,
        adjustment_type: str,
        execution_status: Dict[str, Any],
        orchestration_plan: Dict[str, Any]
    ) -> AdjustmentSuggestion:
        """生成调整建议"""
        
        if adjustment_type == "simple":
            return self._generate_simple_suggestion(error_type, execution_status)
        elif adjustment_type == "complex":
            return self._generate_complex_suggestion(error_type, execution_status)
        elif adjustment_type == "revisit":
            return self._generate_revisit_suggestion(error_type, execution_status)
        else:
            return AdjustmentSuggestion(
                need_adjustment=True,
                adjustment_type="complex",
                reason=f"未知错误类型: {error_type}",
                suggested_action="调用动态调整模块进行详细分析",
                urgency="medium"
            )

    def _generate_simple_suggestion(
        self, 
        error_type: str,
        execution_status: Dict[str, Any]
    ) -> AdjustmentSuggestion:
        """生成简单调整建议"""
        suggestions = {
            "skill_unavailable": AdjustmentSuggestion(
                need_adjustment=True,
                adjustment_type="simple",
                reason="技能暂时不可用",
                suggested_action="尝试使用备选技能或稍后重试",
                urgency="medium"
            ),
            "skill_timeout": AdjustmentSuggestion(
                need_adjustment=True,
                adjustment_type="simple",
                reason="技能执行超时",
                suggested_action="增加超时时间或简化任务参数",
                urgency="medium"
            ),
            "parameter_error": AdjustmentSuggestion(
                need_adjustment=True,
                adjustment_type="simple",
                reason="参数配置错误",
                suggested_action="调整参数配置后重试",
                urgency="high"
            ),
            "rate_limit": AdjustmentSuggestion(
                need_adjustment=True,
                adjustment_type="simple",
                reason="请求频率受限",
                suggested_action="等待后重试或使用备选方案",
                urgency="low"
            ),
            "network_error": AdjustmentSuggestion(
                need_adjustment=True,
                adjustment_type="simple",
                reason="网络连接问题",
                suggested_action="检查网络后重试或使用离线方案",
                urgency="medium"
            )
        }
        
        return suggestions.get(error_type, AdjustmentSuggestion(
            need_adjustment=True,
            adjustment_type="simple",
            reason="简单问题",
            suggested_action="调用动态调整模块处理",
            urgency="medium"
        ))

    def _generate_complex_suggestion(
        self, 
        error_type: str,
        execution_status: Dict[str, Any]
    ) -> AdjustmentSuggestion:
        """生成复杂调整建议"""
        return AdjustmentSuggestion(
            need_adjustment=True,
            adjustment_type="complex",
            reason=f"复杂问题: {error_type}",
            suggested_action="调用动态调整模块生成详细调整方案",
            urgency="high"
        )

    def _generate_revisit_suggestion(
        self, 
        error_type: str,
        execution_status: Dict[str, Any]
    ) -> AdjustmentSuggestion:
        """生成回溯建议"""
        context = execution_status.get("context", {})
        
        return AdjustmentSuggestion(
            need_adjustment=True,
            adjustment_type="revisit",
            reason=f"需要回溯诊断: {error_type}",
            suggested_action="建议回溯到短板诊断模块重新评估",
            urgency="high",
            **{"revisit_context": context}  # 额外的回溯上下文
        )


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="执行监控模块")
    parser.add_argument("--execution-status", required=True, help="执行状态JSON文件")
    parser.add_argument("--orchestration-plan", required=True, help="编排方案JSON文件")
    parser.add_argument("--output", required=True, help="输出文件路径")
    
    args = parser.parse_args()
    
    # 读取输入
    with open(args.execution_status, 'r', encoding='utf-8') as f:
        execution_status = json.load(f)
    
    with open(args.orchestration_plan, 'r', encoding='utf-8') as f:
        orchestration_plan = json.load(f)
    
    # 执行
    monitor = ExecutionMonitor()
    result = monitor.execute({
        "execution_status": execution_status,
        "orchestration_plan": orchestration_plan
    })
    
    # 输出
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"执行监控完成，需要调整: {result['need_adjustment']}")


if __name__ == "__main__":
    main()
