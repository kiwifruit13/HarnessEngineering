"""
实时分析协调器模块

职责：接收状态快照，协调调用执行监控和动态调整模块，生成实时优化建议
"""

import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

# 导入现有模块
from scripts.modules.execution_monitor import ExecutionMonitor
from scripts.modules.dynamic_adjuster import DynamicAdjuster
from scripts.modules.state_capture_adapter import StateCaptureAdapter


@dataclass
class RealtimeAnalysisResult:
    """实时分析结果"""
    needs_adjustment: bool
    adjustment_type: str
    adjustment_suggestion: Optional[Dict[str, Any]]
    adjustment_plan: Optional[Dict[str, Any]]
    revisit_request: Optional[Dict[str, Any]]
    analysis_timestamp: str
    execution_metrics: Dict[str, Any]


class RealtimeCoordinator:
    """
    实时分析协调器

    职责边界：
    - 接收 LangGraph 状态快照
    - 协调调用执行监控和动态调整
    - 生成实时优化建议
    - 不直接修改执行流程
    - 不调用 LangGraph API
    """

    def __init__(self):
        self.state_adapter = StateCaptureAdapter()
        self.execution_monitor = ExecutionMonitor()
        self.dynamic_adjuster = DynamicAdjuster()

    def analyze_realtime(
        self,
        langgraph_state: Dict[str, Any],
        current_node: str,
        node_history: Optional[list] = None,
        orchestration_plan: Optional[Dict[str, Any]] = None
    ) -> RealtimeAnalysisResult:
        """
        实时分析并生成优化建议

        Args:
            langgraph_state: LangGraph 状态对象
            current_node: 当前节点名称
            node_history: 节点执行历史
            orchestration_plan: 编排方案（如果有）

        Returns:
            RealtimeAnalysisResult: 实时分析结果
        """
        # 1. 捕获状态
        snapshot = self.state_adapter.capture_state(
            langgraph_state, current_node, node_history
        )

        # 2. 获取标准化的执行状态
        execution_status = self.state_adapter.get_state_for_analysis()

        # 3. 执行监控（复用现有模块G）
        adjustment_suggestion = None
        if orchestration_plan:
            try:
                adjustment_suggestion = self.execution_monitor.execute({
                    "execution_status": execution_status,
                    "orchestration_plan": orchestration_plan
                })
            except Exception as e:
                # 如果监控失败，继续执行，不中断流程
                adjustment_suggestion = {
                    "need_adjustment": False,
                    "error": str(e)
                }

        # 4. 动态调整（复用现有模块H）
        adjustment_plan = None
        revisit_request = None

        if adjustment_suggestion and adjustment_suggestion.get("need_adjustment"):
            try:
                adjust_result = self.dynamic_adjuster.execute({
                    "execution_status": execution_status,
                    "adjustment_suggestion": adjustment_suggestion,
                    "orchestration_plan": orchestration_plan or {}
                })

                # 判断是调整方案还是回溯请求
                if "revisit_request" in adjust_result:
                    revisit_request = adjust_result["revisit_request"]
                else:
                    adjustment_plan = adjust_result
            except Exception as e:
                # 如果调整失败，记录错误但不中断
                adjustment_plan = {
                    "error": str(e),
                    "fallback": "continue_current_plan"
                }

        # 5. 生成结果
        return RealtimeAnalysisResult(
            needs_adjustment=adjustment_plan is not None or revisit_request is not None,
            adjustment_type=self._determine_adjustment_type(adjustment_suggestion),
            adjustment_suggestion=adjustment_suggestion,
            adjustment_plan=adjustment_plan,
            revisit_request=revisit_request,
            analysis_timestamp=snapshot.timestamp,
            execution_metrics=snapshot.execution_metrics
        )

    def _determine_adjustment_type(
        self,
        adjustment_suggestion: Optional[Dict[str, Any]]
    ) -> str:
        """确定调整类型"""
        if not adjustment_suggestion:
            return "none"

        adj_type = adjustment_suggestion.get("adjustment_type", "none")
        return adj_type


def main():
    """命令行接口（用于测试）"""
    import argparse

    parser = argparse.ArgumentParser(description="实时分析协调器")
    parser.add_argument("--langgraph-state", help="LangGraph状态JSON文件")
    parser.add_argument("--current-node", required=True, help="当前节点名称")
    parser.add_argument("--node-history", help="节点历史JSON文件")
    parser.add_argument("--orchestration-plan", help="编排方案JSON文件")
    parser.add_argument("--output", required=True, help="输出文件路径")

    args = parser.parse_args()

    # 创建协调器
    coordinator = RealtimeCoordinator()

    # 加载数据
    langgraph_state = {}
    if args.langgraph_state:
        with open(args.langgraph_state, 'r', encoding='utf-8') as f:
            langgraph_state = json.load(f)

    node_history = []
    if args.node_history:
        with open(args.node_history, 'r', encoding='utf-8') as f:
            node_history = json.load(f)

    orchestration_plan = None
    if args.orchestration_plan:
        with open(args.orchestration_plan, 'r', encoding='utf-8') as f:
            orchestration_plan = json.load(f)

    # 实时分析
    result = coordinator.analyze_realtime(
        langgraph_state, args.current_node, node_history, orchestration_plan
    )

    # 输出结果
    output_data = {
        "needs_adjustment": result.needs_adjustment,
        "adjustment_type": result.adjustment_type,
        "adjustment_suggestion": result.adjustment_suggestion,
        "adjustment_plan": result.adjustment_plan,
        "revisit_request": result.revisit_request,
        "analysis_timestamp": result.analysis_timestamp,
        "execution_metrics": result.execution_metrics
    }

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"实时分析完成: {args.output}")
    if result.needs_adjustment:
        print(f"需要调整: {result.adjustment_type}")
        if result.revisit_request:
            print(f"建议回溯: {result.revisit_request}")
        else:
            print(f"调整方案已生成")
    else:
        print("当前状态正常，无需调整")


if __name__ == "__main__":
    main()
