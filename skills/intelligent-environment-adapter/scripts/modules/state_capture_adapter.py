"""
状态捕获适配器模块

职责：接收 LangGraph 的执行状态快照，转换为 Skill 可理解的格式
"""

import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ExecutionSnapshot:
    """执行状态快照"""
    timestamp: str
    current_node: str
    node_history: list
    state_data: dict
    execution_metrics: dict


class StateCaptureAdapter:
    """
    状态捕获适配器

    职责边界：
    - 接收 LangGraph 状态快照
    - 解析状态并转换为 Skill 格式
    - 提供状态查询接口
    - 不直接调用 LangGraph API
    - 不修改执行流程
    """

    def __init__(self):
        self.snapshots: List[ExecutionSnapshot] = []
        self.latest_snapshot: Optional[ExecutionSnapshot] = None

    def capture_state(
        self,
        langgraph_state: Dict[str, Any],
        current_node: str,
        node_history: Optional[list] = None
    ) -> ExecutionSnapshot:
        """
        捕获 LangGraph 状态快照

        Args:
            langgraph_state: LangGraph 的 State 对象
            current_node: 当前执行的节点名称
            node_history: 节点执行历史

        Returns:
            ExecutionSnapshot: 标准化的执行快照
        """
        snapshot = ExecutionSnapshot(
            timestamp=datetime.now().isoformat(),
            current_node=current_node,
            node_history=node_history or [],
            state_data=self._extract_key_state(langgraph_state),
            execution_metrics=self._calculate_metrics(langgraph_state, node_history)
        )

        self.snapshots.append(snapshot)
        self.latest_snapshot = snapshot

        return snapshot

    def _extract_key_state(self, langgraph_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        提取关键状态信息

        Args:
            langgraph_state: 原始状态对象

        Returns:
            提取的关键状态
        """
        key_fields = [
            "task_description",
            "environment_profile",
            "mapping_result",
            "diagnostic_report",
            "remediation_plan",
            "orchestration_plan",
            "orchestration_result",
            "execution_status",
            "error_info"
        ]

        extracted = {}
        for field in key_fields:
            if field in langgraph_state:
                extracted[field] = langgraph_state[field]

        return extracted

    def _calculate_metrics(
        self,
        langgraph_state: Dict[str, Any],
        node_history: Optional[list]
    ) -> Dict[str, Any]:
        """
        计算执行指标

        Args:
            langgraph_state: 状态对象
            node_history: 节点历史

        Returns:
            执行指标
        """
        metrics = {
            "total_nodes_executed": len(node_history) if node_history else 0,
            "execution_progress": 0.0,
            "error_count": 0,
            "retry_count": 0
        }

        # 计算执行进度
        if node_history:
            # 假设完整流程有 8 个节点（A-H）
            total_nodes = 8
            metrics["execution_progress"] = len(node_history) / total_nodes

        # 统计错误和重试
        if node_history:
            for node_info in node_history:
                if isinstance(node_info, dict):
                    if node_info.get("status") == "error":
                        metrics["error_count"] += 1
                    if node_info.get("retry_count", 0) > 0:
                        metrics["retry_count"] += 1

        return metrics

    def get_latest_snapshot(self) -> Optional[ExecutionSnapshot]:
        """获取最新快照"""
        return self.latest_snapshot

    def get_state_for_analysis(self) -> Dict[str, Any]:
        """
        获取用于分析的状态数据（兼容现有模块）

        Returns:
            标准化的执行状态数据
        """
        if not self.latest_snapshot:
            return {
                "current_step": 0,
                "status": "not_started",
                "timestamp": None
            }

        # 转换为 execution_monitor.py 期望的格式
        return {
            "current_step": self.latest_snapshot.execution_metrics.get("total_nodes_executed", 0),
            "status": self._determine_status(),
            "current_node": self.latest_snapshot.current_node,
            "node_history": self.latest_snapshot.node_history,
            "state_data": self.latest_snapshot.state_data,
            "error_info": self.latest_snapshot.state_data.get("error_info"),
            "metrics": self.latest_snapshot.execution_metrics,
            "timestamp": self.latest_snapshot.timestamp
        }

    def _determine_status(self) -> str:
        """确定执行状态"""
        if not self.latest_snapshot:
            return "not_started"

        state_data = self.latest_snapshot.state_data

        # 检查是否有错误
        if state_data.get("error_info"):
            return "failed"

        # 检查是否有新需求
        if state_data.get("new_requirement"):
            return "new_requirement"

        # 检查进度
        progress = self.latest_snapshot.execution_metrics.get("execution_progress", 0)
        if progress >= 1.0:
            return "success"
        elif progress > 0:
            return "running"
        else:
            return "not_started"


def main():
    """命令行接口（用于测试）"""
    import argparse

    parser = argparse.ArgumentParser(description="状态捕获适配器")
    parser.add_argument("--langgraph-state", help="LangGraph状态JSON文件")
    parser.add_argument("--current-node", required=True, help="当前节点名称")
    parser.add_argument("--node-history", help="节点历史JSON文件")
    parser.add_argument("--output", required=True, help="输出文件路径")

    args = parser.parse_args()

    # 创建适配器
    adapter = StateCaptureAdapter()

    # 加载状态
    langgraph_state = {}
    if args.langgraph_state:
        with open(args.langgraph_state, 'r', encoding='utf-8') as f:
            langgraph_state = json.load(f)

    node_history = []
    if args.node_history:
        with open(args.node_history, 'r', encoding='utf-8') as f:
            node_history = json.load(f)

    # 捕获状态
    snapshot = adapter.capture_state(langgraph_state, args.current_node, node_history)

    # 输出结果
    output_data = {
        "snapshot": {
            "timestamp": snapshot.timestamp,
            "current_node": snapshot.current_node,
            "node_history": snapshot.node_history,
            "state_data": snapshot.state_data,
            "execution_metrics": snapshot.execution_metrics
        },
        "state_for_analysis": adapter.get_state_for_analysis()
    }

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"状态捕获完成: {args.output}")
    print(f"当前节点: {snapshot.current_node}")
    print(f"执行进度: {snapshot.execution_metrics['execution_progress']:.1%}")


if __name__ == "__main__":
    main()
