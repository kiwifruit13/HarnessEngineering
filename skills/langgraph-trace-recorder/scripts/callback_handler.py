"""
LangGraph Callback Handler
用于捕获LangGraph执行状态并构建知识图谱
严格遵循类型安全协议
"""

from __future__ import annotations

import traceback
from typing import Any, Optional, TYPE_CHECKING
from datetime import datetime

from scripts.definitions import (
    LangGraphCallbackData,
    NodeType,
    EdgeType,
    TraceType,
    ErrorInfo,
    get_current_timestamp
)
from scripts.graph_builder import KnowledgeGraph
from scripts.classifier import NodeClassifier
from scripts.storage_backend import GraphStorageBackend

# 避免循环导入
if TYPE_CHECKING:
    from langchain_core.callbacks import BaseCallbackHandler


class TraceRecorderCallback:
    """
    LangGraph轨迹记录回调处理器
    自动捕获执行状态并构建知识图谱
    """

    def __init__(
        self,
        task_id: Optional[str] = None,
        storage_backend: Optional[GraphStorageBackend] = None
    ) -> None:
        """
        初始化Callback Handler

        Args:
            task_id: 任务ID（可选）
            storage_backend: 存储后端（可选，默认使用内存存储）
        """
        self._graph = KnowledgeGraph(task_id=task_id, storage_backend=storage_backend)
        self._classifier = NodeClassifier()
        self._last_node_id: Optional[str] = None
        self._node_counter: int = 0

    def get_graph(self) -> KnowledgeGraph:
        """
        获取知识图谱实例

        Returns:
            KnowledgeGraph: 知识图谱实例
        """
        return self._graph

    def on_node_start(
        self,
        node_name: str,
        input_data: dict[str, Any],
        **kwargs: Any
    ) -> None:
        """
        节点开始执行时的回调

        Args:
            node_name: 节点名称
            input_data: 输入数据
            **kwargs: 其他参数
        """
        try:
            # 验证输入数据类型
            if not isinstance(input_data, dict):
                input_data = {"input": str(input_data)}

            # 生成节点ID
            node_id = f"node_{self._node_counter}"
            self._node_counter += 1

            # 构建节点内容
            content = self._build_node_content(input_data, node_name)

            # 分类节点类型
            node_type, trace_type = self._classifier.classify(node_name, content)

            # 添加节点到图谱
            self._graph.add_node(
                node_id=node_id,
                node_type=node_type,
                label=node_name,
                content=content,
                trace_type=trace_type,
                timestamp=get_current_timestamp(),
                metadata={
                    "status": "running",
                    "input_summary": self._summarize_data(input_data)
                }
            )

            # 如果存在上一个节点，添加边
            if self._last_node_id is not None:
                self._graph.add_edge(
                    source=self._last_node_id,
                    target=node_id,
                    edge_type=EdgeType.FOLLOWS
                )

            # 更新上一个节点ID
            self._last_node_id = node_id

        except Exception as e:
            # 静默处理异常，避免影响LangGraph执行
            print(f"[TraceRecorder] on_node_start error: {str(e)}")
            traceback.print_exc()

    def on_node_end(
        self,
        node_name: str,
        output_data: Optional[dict[str, Any]] = None,
        **kwargs: Any
    ) -> None:
        """
        节点执行结束时的回调

        Args:
            node_name: 节点名称
            output_data: 输出数据（可选）
            **kwargs: 其他参数
        """
        try:
            # 验证输出数据类型
            if output_data is None:
                output_data = {}
            elif not isinstance(output_data, dict):
                output_data = {"output": str(output_data)}

            # 更新最后一个节点的状态
            if self._last_node_id is not None:
                node = self._graph.get_node(self._last_node_id)
                if node:
                    # 更新节点元数据
                    node["metadata"]["status"] = "completed"
                    node["metadata"]["output_summary"] = self._summarize_data(output_data)

                    # 使用索引更新方法
                    self._graph.update_node_status(self._last_node_id, "completed")

                    # 如果输出数据较丰富，更新节点内容
                    if len(str(output_data)) > len(node["content"]):
                        node["content"] = self._build_node_content(output_data, node_name)

        except Exception as e:
            # 静默处理异常，避免影响LangGraph执行
            print(f"[TraceRecorder] on_node_end error: {str(e)}")
            traceback.print_exc()

    def on_node_error(
        self,
        node_name: str,
        error: Exception,
        **kwargs: Any
    ) -> None:
        """
        节点执行出错时的回调

        Args:
            node_name: 节点名称
            error: 异常对象
            **kwargs: 其他参数
        """
        try:
            # 更新最后一个节点的状态为失败
            if self._last_node_id is not None:
                node = self._graph.get_node(self._last_node_id)
                if node:
                    # 记录错误信息
                    error_info: ErrorInfo = {
                        "error_type": type(error).__name__,
                        "error_message": str(error),
                        "stack_trace": traceback.format_exc(),
                        "recovery_suggestion": self._generate_recovery_suggestion(error),
                        "timestamp": get_current_timestamp()
                    }

                    # 更新节点元数据
                    node["metadata"]["status"] = "failed"
                    node["metadata"]["error_info"] = error_info
                    node["metadata"]["output_summary"] = f"ERROR: {error}"

                    # 使用索引更新方法
                    self._graph.update_node_status(self._last_node_id, "failed")

        except Exception as e:
            # 静默处理异常，避免影响LangGraph执行
            print(f"[TraceRecorder] on_node_error error: {str(e)}")
            traceback.print_exc()

    def finalize(self) -> None:
        """
        完成记录
        标记图谱为完成状态
        """
        try:
            self._graph.finalize()
        except Exception as e:
            print(f"[TraceRecorder] finalize error: {str(e)}")
            traceback.print_exc()

    def _build_node_content(self, data: dict[str, Any], node_name: str) -> str:
        """
        构建节点内容描述

        Args:
            data: 节点数据
            node_name: 节点名称

        Returns:
            str: 节点内容
        """
        if not data:
            return f"节点 {node_name} 执行完成"

        # 优先提取有意义的信息
        content_parts = []

        # 尝试提取常见字段
        for key in ["query", "question", "response", "answer", "result", "output"]:
            if key in data and data[key]:
                value = str(data[key])
                content_parts.append(f"{key}: {value[:200]}")
                break

        # 如果没有找到常见字段，提取前几个键值对
        if not content_parts:
            for key, value in list(data.items())[:3]:
                content_parts.append(f"{key}: {str(value)[:200]}")

        return " | ".join(content_parts) if content_parts else f"节点 {node_name} 执行完成"

    def _summarize_data(self, data: dict[str, Any]) -> str:
        """
        汇总数据信息

        Args:
            data: 待汇总的数据

        Returns:
            str: 汇总信息
        """
        if not data:
            return "{}"

        summary_parts = []
        for key, value in list(data.items())[:5]:
            value_str = str(value)
            if len(value_str) > 100:
                value_str = value_str[:100] + "..."
            summary_parts.append(f'"{key}": {value_str}')

        return "{" + ", ".join(summary_parts) + "}"

    def _generate_recovery_suggestion(self, error: Exception) -> str | None:
        """
        根据错误类型生成恢复建议

        Args:
            error: 异常对象

        Returns:
            str | None: 恢复建议，如果无法生成则返回None
        """
        error_type = type(error).__name__
        error_message = str(error).lower()

        # 超时错误
        if "timeout" in error_type or "timeout" in error_message:
            return "建议：增加超时时间配置，或优化查询减少执行时长"

        # 权限错误
        elif "permission" in error_type or "permission" in error_message or "access denied" in error_message:
            return "建议：检查文件或资源的访问权限，确保有足够的操作权限"

        # 值错误（参数问题）
        elif "value" in error_type or "invalid" in error_message:
            return "建议：检查输入参数的格式和类型，确保符合API要求"

        # 键错误（缺少字段）
        elif "key" in error_type or "not found" in error_message:
            return "建议：检查数据结构，确保所有必需字段都存在"

        # 连接错误（网络问题）
        elif "connection" in error_type or "network" in error_message or "unreachable" in error_message:
            return "建议：检查网络连接，或重试请求"

        # 未找到错误（资源不存在）
        elif "notfound" in error_type or "not found" in error_message or "404" in error_message:
            return "建议：检查资源是否存在，或验证URL路径"

        # 其他错误
        else:
            return "建议：查看完整的错误堆栈信息，定位具体问题原因"


def create_callback_handler(
    task_id: Optional[str] = None,
    storage_backend: Optional[GraphStorageBackend] = None
) -> TraceRecorderCallback:
    """
    创建Callback Handler实例的便捷函数

    Args:
        task_id: 任务ID（可选）
        storage_backend: 存储后端（可选，默认使用内存存储）

    Returns:
        TraceRecorderCallback: Callback Handler实例
    """
    return TraceRecorderCallback(task_id=task_id, storage_backend=storage_backend)
