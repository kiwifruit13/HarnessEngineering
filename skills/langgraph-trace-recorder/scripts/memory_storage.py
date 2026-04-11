"""
内存存储后端实现
提供高性能的内存存储能力，适合单机和临时数据场景

**特点**：
- O(1)索引查询
- 线程安全（使用RLock）
- 内存占用优化
"""

from __future__ import annotations

from typing import Optional
from collections import OrderedDict
import threading

from scripts.storage_backend import GraphStorageBackend
from scripts.definitions import (
    NodeData,
    EdgeData,
    NodeType,
    TraceType
)


class MemoryGraphStorage(GraphStorageBackend):
    """
    内存存储后端
    提供高性能的内存存储能力

    Attributes:
        _nodes: 节点数据字典
        _edges: 边数据列表
        _lock: 线程锁（RLock）
    """

    def __init__(self) -> None:
        """初始化内存存储"""
        self._nodes: dict[str, NodeData] = OrderedDict()
        self._edges: list[EdgeData] = []

        # 性能优化：索引机制
        self._nodes_by_type: dict[NodeType, list[str]] = {}
        self._nodes_by_status: dict[str, list[str]] = {}
        self._nodes_by_trace_type: dict[TraceType, list[str]] = {}
        self._edges_by_source: dict[str, list[int]] = {}
        self._edges_by_target: dict[str, list[int]] = {}

        # 线程锁
        self._lock: threading.RLock = threading.RLock()

    def add_node(self, node_data: NodeData) -> None:
        """
        添加节点到内存

        Args:
            node_data: 节点数据

        Raises:
            ValueError: 如果节点ID无效或节点已存在
        """
        node_id = node_data["id"]

        if not node_id:
            raise ValueError("节点ID不能为空")

        if node_id in self._nodes:
            raise ValueError(f"节点已存在: {node_id}")

        # 添加节点
        self._nodes[node_id] = node_data

        # 更新索引
        self._nodes_by_type.setdefault(node_data["type"], []).append(node_id)
        self._nodes_by_trace_type.setdefault(node_data["trace_type"], []).append(node_id)

        # 添加状态索引
        status = node_data.get("metadata", {}).get("status", "unknown")
        self._nodes_by_status.setdefault(status, []).append(node_id)

    def get_node(self, node_id: str) -> Optional[NodeData]:
        """
        获取节点数据

        Args:
            node_id: 节点ID

        Returns:
            NodeData | None: 节点数据，如果不存在则返回None
        """
        return self._nodes.get(node_id)

    def update_node_status(self, node_id: str, new_status: str) -> None:
        """
        更新节点状态

        Args:
            node_id: 节点ID
            new_status: 新状态

        Raises:
            ValueError: 如果节点不存在
        """
        if node_id not in self._nodes:
            raise ValueError(f"节点不存在: {node_id}")

        node = self._nodes[node_id]
        old_status = node.get("metadata", {}).get("status", "unknown")

        # 更新节点状态
        if "metadata" not in node:
            node["metadata"] = {}
        node["metadata"]["status"] = new_status

        # 更新索引
        if old_status in self._nodes_by_status:
            try:
                self._nodes_by_status[old_status].remove(node_id)
            except ValueError:
                pass

        self._nodes_by_status.setdefault(new_status, []).append(node_id)

    def get_nodes_by_type(self, node_type: NodeType) -> list[NodeData]:
        """
        根据节点类型获取节点列表

        Args:
            node_type: 节点类型

        Returns:
            list[NodeData]: 节点列表
        """
        node_ids = self._nodes_by_type.get(node_type, [])
        return [self._nodes[node_id] for node_id in node_ids]

    def get_nodes_by_status(self, status: str) -> list[NodeData]:
        """
        根据状态获取节点列表

        Args:
            status: 节点状态

        Returns:
            list[NodeData]: 节点列表
        """
        node_ids = self._nodes_by_status.get(status, [])
        return [self._nodes[node_id] for node_id in node_ids]

    def get_nodes_by_trace_type(self, trace_type: TraceType) -> list[NodeData]:
        """
        根据轨迹类型获取节点列表

        Args:
            trace_type: 轨迹类型

        Returns:
            list[NodeData]: 节点列表
        """
        node_ids = self._nodes_by_trace_type.get(trace_type, [])
        return [self._nodes[node_id] for node_id in node_ids]

    def get_failed_nodes(self) -> list[NodeData]:
        """
        获取所有失败节点

        Returns:
            list[NodeData]: 失败节点列表
        """
        return self.get_nodes_by_status("failed")

    def add_edge(self, edge_data: EdgeData, edge_index: int) -> None:
        """
        添加边到内存

        Args:
            edge_data: 边数据
            edge_index: 边的索引

        Raises:
            ValueError: 如果节点不存在
        """
        source = edge_data["source"]
        target = edge_data["target"]

        if source not in self._nodes:
            raise ValueError(f"源节点不存在: {source}")
        if target not in self._nodes:
            raise ValueError(f"目标节点不存在: {target}")

        # 添加边
        self._edges.append(edge_data)

        # 更新索引
        self._edges_by_source.setdefault(source, []).append(edge_index)
        self._edges_by_target.setdefault(target, []).append(edge_index)

    def get_edges_from_node(self, node_id: str) -> list[EdgeData]:
        """
        获取从指定节点出发的所有边

        Args:
            node_id: 节点ID

        Returns:
            list[EdgeData]: 边列表
        """
        edge_indices = self._edges_by_source.get(node_id, [])
        return [self._edges[i] for i in edge_indices]

    def get_edges_to_node(self, node_id: str) -> list[EdgeData]:
        """
        获取指向指定节点的所有边

        Args:
            node_id: 节点ID

        Returns:
            list[EdgeData]: 边列表
        """
        edge_indices = self._edges_by_target.get(node_id, [])
        return [self._edges[i] for i in edge_indices]

    def get_all_nodes(self) -> dict[str, NodeData]:
        """
        获取所有节点

        Returns:
            dict[str, NodeData]: 节点字典
        """
        return dict(self._nodes)

    def get_all_edges(self) -> list[EdgeData]:
        """
        获取所有边

        Returns:
            list[EdgeData]: 边列表
        """
        return list(self._edges)

    def get_node_count(self) -> int:
        """
        获取节点总数

        Returns:
            int: 节点总数
        """
        return len(self._nodes)

    def get_edge_count(self) -> int:
        """
        获取边总数

        Returns:
            int: 边总数
        """
        return len(self._edges)

    def close(self) -> None:
        """关闭存储（内存存储无需操作）"""
        pass
