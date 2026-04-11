"""
图谱导出器 - 支持JSON/SVG/Markdown三种格式导出
严格遵循类型安全协议
"""

from __future__ import annotations

import json
from typing import Optional
from datetime import datetime

from scripts.graph_builder import KnowledgeGraph
from scripts.definitions import TraceType, NodeType, EdgeType


class GraphExporter:
    """
    图谱导出器
    支持导出为JSON、SVG、Markdown三种格式
    """

    def __init__(self, graph: KnowledgeGraph) -> None:
        """
        初始化导出器

        Args:
            graph: 知识图谱实例
        """
        # 使用鸭子类型检查而不是严格的isinstance检查
        if not hasattr(graph, 'add_node') or not hasattr(graph, 'to_data'):
            raise TypeError(f"graph参数必须是KnowledgeGraph类型，实际类型: {type(graph)}")

        self._graph = graph
        self._data = graph.to_data()

    def export_json(self) -> str:
        """
        导出为JSON格式
        返回序列化后的JSON字符串

        Returns:
            str: JSON格式的图谱数据
        """
        try:
            # 确保所有数据可序列化
            json_data = {
                "nodes": self._serialize_nodes(self._data["nodes"]),
                "edges": self._serialize_edges(self._data["edges"]),
                "metadata": self._data["metadata"]
            }

            # 导出为格式化的JSON字符串
            json_str = json.dumps(json_data, indent=2, ensure_ascii=False, default=str)

            return json_str
        except Exception as e:
            raise RuntimeError(f"JSON导出失败: {str(e)}")

    def export_svg(self) -> str:
        """
        导出为SVG格式
        生成可视化的流程图

        Returns:
            str: SVG格式的图形内容
        """
        try:
            # 构建SVG内容
            svg_lines = [
                '<?xml version="1.0" encoding="UTF-8"?>',
                '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800">',
                '<style>',
                '  .qa-node { fill: #E3F2FD; stroke: #2196F3; stroke-width: 2; }',
                '  .command-node { fill: #FFF3E0; stroke: #FF9800; stroke-width: 2; }',
                '  .failed-node { fill: #FFEBEE; stroke: #F44336; stroke-width: 3; }',
                '  .edge { stroke: #666; stroke-width: 2; marker-end: url(#arrowhead); }',
                '  .label { font-family: Arial, sans-serif; font-size: 12px; }',
                '  .node-title { font-weight: bold; font-size: 14px; }',
                '  .error-icon { font-size: 20px; fill: #F44336; }',
                '</style>',
                '<defs>',
                '  <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">',
                '    <polygon points="0 0, 10 3.5, 0 7" fill="#666" />',
                '  </marker>',
                '</defs>'
            ]

            # 绘制节点
            node_positions = self._calculate_node_positions()
            for node_id, pos in node_positions.items():
                node = self._graph.get_node(node_id)
                if node is None:
                    continue

                # 检查节点是否失败
                is_failed = node.get("metadata", {}).get("status") == "failed"

                # 根据状态和轨迹类型选择样式
                if is_failed:
                    css_class = "failed-node"
                elif node["trace_type"] == TraceType.QA_TRACE:
                    css_class = "qa-node"
                else:
                    css_class = "command-node"

                x, y = pos
                width = 200
                height = 80

                # 绘制节点矩形
                svg_lines.append(
                    f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
                    f'class="{css_class}" rx="5" ry="5" />'
                )

                # 绘制节点标签
                label = node["label"][:20] + "..." if len(node["label"]) > 20 else node["label"]
                svg_lines.append(
                    f'<text x="{x + width/2}" y="{y + height/2 - 10}" '
                    f'class="label node-title" text-anchor="middle">{label}</text>'
                )

                # 绘制节点类型
                svg_lines.append(
                    f'<text x="{x + width/2}" y="{y + height/2 + 10}" '
                    f'class="label" text-anchor="middle">[{node["type"].value}]</text>'
                )

                # 如果失败，绘制错误图标
                if is_failed:
                    svg_lines.append(
                        f'<text x="{x + width - 15}" y="{y + 20}" '
                        f'class="label error-icon" text-anchor="middle">⚠️</text>'
                    )

            # 绘制边
            for edge in self._data["edges"]:
                source_pos = node_positions.get(edge["source"])
                target_pos = node_positions.get(edge["target"])

                if source_pos and target_pos:
                    x1, y1 = source_pos
                    x2, y2 = target_pos

                    # 绘制连线
                    svg_lines.append(
                        f'<line x1="{x1 + 200}" y1="{y1 + 40}" '
                        f'x2="{x2}" y2="{y2 + 40}" class="edge" />'
                    )

                    # 绘制边标签
                    if edge["condition"]:
                        mid_x = (x1 + x2) / 2
                        mid_y = (y1 + y2) / 2
                        svg_lines.append(
                            f'<text x="{mid_x}" y="{mid_y - 5}" '
                            f'class="label" text-anchor="middle" fill="#666">{edge["condition"]}</text>'
                        )

            svg_lines.append('</svg>')

            return "\n".join(svg_lines)
        except Exception as e:
            raise RuntimeError(f"SVG导出失败: {str(e)}")

    def export_markdown(self) -> str:
        """
        导出为Markdown格式
        生成结构化的报告，适合作为模型推理锚点

        Returns:
            str: Markdown格式的报告内容
        """
        try:
            md_lines = []

            # 标题
            md_lines.append(f"# LangGraph 执行轨迹报告")
            md_lines.append(f"")
            md_lines.append(f"**任务ID**: `{self._graph.get_task_id()}`")
            md_lines.append(f"**生成时间**: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`")
            md_lines.append(f"")

            # 元数据
            metadata = self._data["metadata"]
            md_lines.append("## 📊 执行统计")
            md_lines.append(f"- 节点总数: {metadata['total_nodes']}")
            md_lines.append(f"- 边总数: {metadata['total_edges']}")
            md_lines.append(f"- 问答轨迹节点数: {metadata['qa_trace_count']}")
            md_lines.append(f"- 命令轨迹节点数: {metadata['command_trace_count']}")

            if metadata.get("start_time"):
                start_time_str = datetime.fromtimestamp(metadata["start_time"]).strftime('%Y-%m-%d %H:%M:%S')
                md_lines.append(f"- 开始时间: {start_time_str}")

            if metadata.get("end_time"):
                end_time_str = datetime.fromtimestamp(metadata["end_time"]).strftime('%Y-%m-%d %H:%M:%S')
                duration = metadata["end_time"] - metadata["start_time"]
                md_lines.append(f"- 结束时间: {end_time_str}")
                md_lines.append(f"- 总耗时: {duration:.2f}秒")

            md_lines.append(f"")

            # 问答轨迹
            qa_nodes = self._graph.get_nodes_by_trace_type(TraceType.QA_TRACE)
            md_lines.append("## 💬 问答轨迹")
            md_lines.append(f"")

            if qa_nodes:
                for i, node in enumerate(qa_nodes, 1):
                    time_str = datetime.fromtimestamp(node["timestamp"]).strftime('%H:%M:%S')
                    status = node.get("metadata", {}).get("status", "unknown")

                    # 如果失败，用红色标题
                    if status == "failed":
                        md_lines.append(f"### ❌ {i}. {node['label']} (FAILED)")
                    else:
                        md_lines.append(f"### {i}. {node['label']}")

                    md_lines.append(f"")
                    md_lines.append(f"- **类型**: {node['type'].value}")
                    md_lines.append(f"- **状态**: {status}")
                    md_lines.append(f"- **时间**: {time_str}")
                    md_lines.append(f"- **内容**:")
                    md_lines.append(f"")
                    md_lines.append(f"```")
                    md_lines.append(f"{node['content'][:500]}{'...' if len(node['content']) > 500 else ''}")
                    md_lines.append(f"```")
                    md_lines.append(f"")

                    # 如果失败，显示错误信息
                    if status == "failed":
                        error_info = node.get("metadata", {}).get("error_info")
                        if error_info:
                            md_lines.append(f"- **错误类型**: {error_info.get('error_type', 'Unknown')}")
                            md_lines.append(f"- **错误消息**: {error_info.get('error_message', 'No message')}")
                            if error_info.get("recovery_suggestion"):
                                md_lines.append(f"- **恢复建议**: {error_info.get('recovery_suggestion')}")
                            md_lines.append(f"")

                    if node["metadata"]:
                        md_lines.append(f"- **元数据**:")
                        md_lines.append(f"```json")
                        md_lines.append(f"{json.dumps(node['metadata'], indent=2, ensure_ascii=False)}")
                        md_lines.append(f"```")
                        md_lines.append(f"")
            else:
                md_lines.append(f"*暂无问答轨迹节点*")
                md_lines.append(f"")

            # 命令轨迹
            command_nodes = self._graph.get_nodes_by_trace_type(TraceType.COMMAND_TRACE)
            md_lines.append("## ⚙️ 命令轨迹")
            md_lines.append(f"")

            if command_nodes:
                for i, node in enumerate(command_nodes, 1):
                    time_str = datetime.fromtimestamp(node["timestamp"]).strftime('%H:%M:%S')
                    status = node.get("metadata", {}).get("status", "unknown")

                    # 如果失败，用红色标题
                    if status == "failed":
                        md_lines.append(f"### ❌ {i}. {node['label']} (FAILED)")
                    else:
                        md_lines.append(f"### {i}. {node['label']}")

                    md_lines.append(f"")
                    md_lines.append(f"- **类型**: {node['type'].value}")
                    md_lines.append(f"- **状态**: {status}")
                    md_lines.append(f"- **时间**: {time_str}")
                    md_lines.append(f"- **内容**:")
                    md_lines.append(f"")
                    md_lines.append(f"```")
                    md_lines.append(f"{node['content'][:500]}{'...' if len(node['content']) > 500 else ''}")
                    md_lines.append(f"```")
                    md_lines.append(f"")

                    # 如果失败，显示错误信息
                    if status == "failed":
                        error_info = node.get("metadata", {}).get("error_info")
                        if error_info:
                            md_lines.append(f"- **错误类型**: {error_info.get('error_type', 'Unknown')}")
                            md_lines.append(f"- **错误消息**: {error_info.get('error_message', 'No message')}")
                            if error_info.get("recovery_suggestion"):
                                md_lines.append(f"- **恢复建议**: {error_info.get('recovery_suggestion')}")
                            md_lines.append(f"")

                    if node["metadata"]:
                        md_lines.append(f"- **元数据**:")
                        md_lines.append(f"```json")
                        md_lines.append(f"{json.dumps(node['metadata'], indent=2, ensure_ascii=False)}")
                        md_lines.append(f"```")
                        md_lines.append(f"")
            else:
                md_lines.append(f"*暂无命令轨迹节点*")
                md_lines.append(f"")

            # 节点关系
            md_lines.append("## 🔗 节点关系")
            md_lines.append(f"")

            if self._data["edges"]:
                for edge in self._data["edges"]:
                    source_node = self._graph.get_node(edge["source"])
                    target_node = self._graph.get_node(edge["target"])

                    source_label = source_node["label"] if source_node else edge["source"]
                    target_label = target_node["label"] if target_node else edge["target"]

                    md_lines.append(f"- `{source_label}` → `{target_label}` ({edge['type'].value})")
                    if edge["condition"]:
                        md_lines.append(f"  - 条件: {edge['condition']}")
            else:
                md_lines.append(f"*暂无节点关系*")

            md_lines.append(f"")
            md_lines.append("---")
            md_lines.append(f"*此报告由LangGraph轨迹记录器生成*")

            return "\n".join(md_lines)
        except Exception as e:
            raise RuntimeError(f"Markdown导出失败: {str(e)}")

    def _serialize_nodes(self, nodes: dict[str, dict[str, any]]) -> dict[str, dict[str, any]]:
        """
        序列化节点数据，确保JSON可序列化

        Args:
            nodes: 节点数据

        Returns:
            dict: 序列化后的节点数据
        """
        serialized = {}
        for node_id, node_data in nodes.items():
            serialized[node_id] = {
                "id": node_data["id"],
                "type": node_data["type"].value,
                "label": node_data["label"],
                "content": node_data["content"],
                "timestamp": node_data["timestamp"],
                "trace_type": node_data["trace_type"].value,
                "metadata": node_data["metadata"]
            }
        return serialized

    def _serialize_edges(self, edges: list[dict[str, any]]) -> list[dict[str, any]]:
        """
        序列化边数据，确保JSON可序列化

        Args:
            edges: 边数据

        Returns:
            list: 序列化后的边数据
        """
        serialized = []
        for edge_data in edges:
            serialized.append({
                "source": edge_data["source"],
                "target": edge_data["target"],
                "type": edge_data["type"].value,
                "condition": edge_data["condition"],
                "weight": edge_data["weight"]
            })
        return serialized

    def _calculate_node_positions(self) -> dict[str, tuple[int, int]]:
        """
        计算节点在SVG中的位置
        使用简单的网格布局算法

        Returns:
            dict: 节点ID到坐标的映射
        """
        positions = {}
        qa_nodes = self._graph.get_nodes_by_trace_type(TraceType.QA_TRACE)
        command_nodes = self._graph.get_nodes_by_trace_type(TraceType.COMMAND_TRACE)

        # 问答轨迹节点放在左侧
        x_offset = 50
        y_offset = 50
        for i, node in enumerate(qa_nodes):
            positions[node["id"]] = (x_offset, y_offset + i * 120)

        # 命令轨迹节点放在右侧
        x_offset = 600
        y_offset = 50
        for i, node in enumerate(command_nodes):
            positions[node["id"]] = (x_offset, y_offset + i * 120)

        return positions
