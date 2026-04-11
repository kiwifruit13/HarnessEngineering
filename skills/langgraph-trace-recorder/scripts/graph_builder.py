"""
知识图谱构建器 - 管理节点和边的关系
严格遵循类型安全协议

性能优化：
- 索引机制：O(1)查询失败节点、节点边等
- 并发安全：线程锁保证数据一致性
- 内存优化：__slots__压缩对象内存
- 可选Redis后端：支持分布式部署和持久化
"""

from __future__ import annotations

from typing import Optional, Any
from collections import OrderedDict
import json
import threading

from scripts.definitions import (
    NodeData,
    EdgeData,
    GraphData,
    NodeType,
    EdgeType,
    TraceType,
    GraphMetadata,
    NodeModel,
    EdgeModel,
    validate_dict_as_node,
    validate_dict_as_edge,
    get_current_timestamp,
    is_valid_node_id
)
from scripts.storage_backend import GraphStorageBackend
from scripts.memory_storage import MemoryGraphStorage


class KnowledgeGraph:
    """
    知识图谱类
    管理节点和边的关系，提供增删改查接口

    支持两种存储后端：
    1. 内存存储（默认）：适合单机、临时数据场景
    2. Redis存储（可选）：适合分布式、持久化场景
    """

    def __init__(
        self,
        task_id: str | None = None,
        storage_backend: Optional[GraphStorageBackend] = None
    ) -> None:
        """
        初始化知识图谱

        Args:
            task_id: 任务ID（可选）
            storage_backend: 存储后端，默认使用内存存储
        """
        # 使用存储后端（默认内存存储）
        self._storage: GraphStorageBackend = storage_backend or MemoryGraphStorage()
        self._task_id: str = task_id or f"task_{get_current_timestamp():.0f}"
        self._start_time: float = get_current_timestamp()
        self._end_time: Optional[float] = None

        # 性能优化：线程锁（用于内存存储）
        # Redis存储本身是线程安全的，不需要额外锁
        if isinstance(self._storage, MemoryGraphStorage):
            self._lock: Optional[threading.RLock] = threading.RLock()
        else:
            self._lock = None

    def add_node(
        self,
        node_id: str,
        node_type: NodeType,
        label: str,
        content: str,
        trace_type: TraceType,
        timestamp: Optional[float] = None,
        metadata: Optional[dict[str, Any]] = None
    ) -> NodeData:
        """
        添加节点到图谱

        Args:
            node_id: 节点ID
            node_type: 节点类型
            label: 节点标签
            content: 节点内容
            trace_type: 轨迹类型
            timestamp: 时间戳（可选，默认当前时间）
            metadata: 元数据（可选）

        Returns:
            NodeData: 添加的节点数据

        Raises:
            ValueError: 如果节点ID无效或节点已存在
        """
        # 使用锁保证线程安全（仅内存存储）
        if self._lock:
            with self._lock:
                return self._add_node_internal(node_id, node_type, label, content, trace_type, timestamp, metadata)
        else:
            return self._add_node_internal(node_id, node_type, label, content, trace_type, timestamp, metadata)

    def _add_node_internal(
        self,
        node_id: str,
        node_type: NodeType,
        label: str,
        content: str,
        trace_type: TraceType,
        timestamp: Optional[float],
        metadata: Optional[dict[str, Any]]
    ) -> NodeData:
        """添加节点的内部实现"""
        # 验证节点ID
        if not is_valid_node_id(node_id):
            raise ValueError(f"无效的节点ID: {node_id}")

        # 构建节点数据
        node_data: NodeData = {
            "id": node_id,
            "type": node_type,
            "label": label,
            "content": content,
            "timestamp": timestamp or get_current_timestamp(),
            "trace_type": trace_type,
            "metadata": metadata or {}
        }

        # 使用Pydantic进行验证
        model = NodeModel(**node_data)
        validated_data = model.to_data()

        # 调用存储后端添加节点
        self._storage.add_node(validated_data)

        return validated_data

    def add_edge(
        self,
        source: str,
        target: str,
        edge_type: EdgeType,
        condition: Optional[str] = None,
        weight: float = 1.0
    ) -> EdgeData:
        """
        添加边到图谱

        Args:
            source: 源节点ID
            target: 目标节点ID
            edge_type: 边类型
            condition: 条件描述（可选）
            weight: 权重（默认1.0）

        Returns:
            EdgeData: 添加的边数据

        Raises:
            ValueError: 如果节点不存在或参数无效
        """
        # 使用锁保证线程安全（仅内存存储）
        if self._lock:
            with self._lock:
                return self._add_edge_internal(source, target, edge_type, condition, weight)
        else:
            return self._add_edge_internal(source, target, edge_type, condition, weight)

    def _add_edge_internal(
        self,
        source: str,
        target: str,
        edge_type: EdgeType,
        condition: Optional[str],
        weight: float
    ) -> EdgeData:
        """添加边的内部实现"""
        # 验证源节点和目标节点存在
        if not self._storage.get_node(source):
            raise ValueError(f"源节点不存在: {source}")
        if not self._storage.get_node(target):
            raise ValueError(f"目标节点不存在: {target}")

        # 构建边数据
        edge_data: EdgeData = {
            "source": source,
            "target": target,
            "type": edge_type,
            "condition": condition,
            "weight": weight
        }

        # 使用Pydantic进行验证
        model = EdgeModel(**edge_data)
        validated_data = model.to_data()

        # 调用存储后端添加边（需要计算边索引）
        all_edges = self._storage.get_all_edges()
        edge_index = len(all_edges)
        self._storage.add_edge(validated_data, edge_index)

        return validated_data

    def get_node(self, node_id: str) -> Optional[NodeData]:
        """
        获取节点数据

        Args:
            node_id: 节点ID

        Returns:
            NodeData | None: 节点数据，如果不存在则返回None
        """
        return self._storage.get_node(node_id)

    def get_edges_from_node(self, node_id: str) -> list[EdgeData]:
        """
        获取从指定节点出发的所有边

        Args:
            node_id: 节点ID

        Returns:
            list[EdgeData]: 边列表
        """
        return self._storage.get_edges_from_node(node_id)

    def get_edges_to_node(self, node_id: str) -> list[EdgeData]:
        """
        获取指向指定节点的所有边

        Args:
            node_id: 节点ID

        Returns:
            list[EdgeData]: 边列表
        """
        return self._storage.get_edges_to_node(node_id)

    def get_nodes_by_trace_type(self, trace_type: TraceType) -> list[NodeData]:
        """
        根据轨迹类型获取节点列表

        Args:
            trace_type: 轨迹类型

        Returns:
            list[NodeData]: 节点列表
        """
        return self._storage.get_nodes_by_trace_type(trace_type)

    def get_nodes_by_type(self, node_type: NodeType) -> list[NodeData]:
        """
        根据节点类型获取节点列表

        Args:
            node_type: 节点类型

        Returns:
            list[NodeData]: 节点列表
        """
        return self._storage.get_nodes_by_type(node_type)

    def get_failed_nodes(self) -> list[NodeData]:
        """
        获取所有失败节点

        Returns:
            list[NodeData]: 失败节点列表
        """
        return self._storage.get_failed_nodes()

    def get_nodes_by_status(self, status: str) -> list[NodeData]:
        """
        根据状态获取节点列表

        Args:
            status: 节点状态

        Returns:
            list[NodeData]: 节点列表
        """
        return self._storage.get_nodes_by_status(status)

    def update_node_status(self, node_id: str, new_status: str) -> None:
        """
        更新节点状态

        Args:
            node_id: 节点ID
            new_status: 新状态

        Raises:
            ValueError: 如果节点不存在
        """
        if self._lock:
            with self._lock:
                self._storage.update_node_status(node_id, new_status)
        else:
            self._storage.update_node_status(node_id, new_status)

    def get_all_nodes(self) -> dict[str, NodeData]:
        """
        获取所有节点

        Returns:
            dict[str, NodeData]: 节点字典
        """
        return self._storage.get_all_nodes()

    def get_all_edges(self) -> list[EdgeData]:
        """
        获取所有边

        Returns:
            list[EdgeData]: 边列表
        """
        return self._storage.get_all_edges()

    def get_node_count(self) -> int:
        """
        获取节点总数

        Returns:
            int: 节点总数
        """
        return self._storage.get_node_count()

    def get_edge_count(self) -> int:
        """
        获取边总数

        Returns:
            int: 边总数
        """
        return self._storage.get_edge_count()

    def finalize(self) -> None:
        """
        完成图谱构建
        设置结束时间，标记图谱为完成状态
        """
        self._end_time = get_current_timestamp()

    def get_metadata(self) -> GraphMetadata:
        """
        获取图谱元数据

        Returns:
            GraphMetadata: 图谱元数据
        """
        qa_count = len(self._storage.get_nodes_by_trace_type(TraceType.QA_TRACE))
        command_count = len(self._storage.get_nodes_by_trace_type(TraceType.COMMAND_TRACE))

        metadata: GraphMetadata = {
            "task_id": self._task_id,
            "start_time": self._start_time,
            "end_time": self._end_time,
            "total_nodes": self._storage.get_node_count(),
            "total_edges": self._storage.get_edge_count(),
            "qa_trace_count": qa_count,
            "command_trace_count": command_count
        }

        return metadata

    def to_data(self) -> GraphData:
        """
        导出图谱数据为GraphData格式

        Returns:
            GraphData: 图谱数据
        """
        data: GraphData = {
            "nodes": self._storage.get_all_nodes(),
            "edges": self._storage.get_all_edges(),
            "metadata": self.get_metadata()
        }

        return data

    def get_task_id(self) -> str:
        """
        获取任务ID

        Returns:
            str: 任务ID
        """
        return self._task_id

    def close(self) -> None:
        """
        关闭图谱资源
        释放存储后端连接
        """
        self._storage.close()


def create_graph_from_dict(data: dict[str, Any]) -> KnowledgeGraph:
    """
    从字典数据创建知识图谱
    防御性编程：验证输入数据格式

    Args:
        data: 图谱数据字典

    Returns:
        KnowledgeGraph: 知识图谱实例

    Raises:
        ValueError: 如果数据格式无效
    """
    if not isinstance(data, dict):
        raise TypeError(f"输入必须是dict类型，实际类型: {type(data)}")

    # 提取元数据
    metadata = data.get("metadata", {})
    task_id = metadata.get("task_id", "imported_task")

    # 创建图谱实例
    graph = KnowledgeGraph(task_id=task_id)

    # 添加节点
    nodes_data = data.get("nodes", {})
    if not isinstance(nodes_data, dict):
        raise ValueError("nodes字段必须是dict类型")

    for node_id, node_dict in nodes_data.items():
        try:
            validated_node = validate_dict_as_node(node_dict)
            graph._nodes[node_id] = validated_node
        except Exception as e:
            raise ValueError(f"节点 {node_id} 验证失败: {str(e)}")

    # 添加边
    edges_data = data.get("edges", [])
    if not isinstance(edges_data, list):
        raise ValueError("edges字段必须是list类型")

    for edge_dict in edges_data:
        try:
            validated_edge = validate_dict_as_edge(edge_dict)
            graph._edges.append(validated_edge)
        except Exception as e:
            raise ValueError(f"边验证失败: {str(e)}")

    # 设置时间信息
    graph._start_time = metadata.get("start_time", get_current_timestamp())
    graph._end_time = metadata.get("end_time")

    return graph
