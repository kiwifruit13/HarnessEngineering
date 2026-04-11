"""
存储后端抽象接口
支持多种存储实现（内存、Redis等）
严格遵循类型安全协议
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Any
from scripts.definitions import (
    NodeData,
    EdgeData,
    NodeType,
    EdgeType,
    TraceType
)


class GraphStorageBackend(ABC):
    """
    图谱存储后端抽象接口
    定义所有存储后端必须实现的方法
    """

    @abstractmethod
    def add_node(self, node_data: NodeData) -> None:
        """
        添加节点到存储

        Args:
            node_data: 节点数据

        Raises:
            ValueError: 如果节点ID无效或节点已存在
        """
        pass

    @abstractmethod
    def get_node(self, node_id: str) -> Optional[NodeData]:
        """
        获取节点数据

        Args:
            node_id: 节点ID

        Returns:
            NodeData | None: 节点数据，如果不存在则返回None
        """
        pass

    @abstractmethod
    def update_node_status(self, node_id: str, new_status: str) -> None:
        """
        更新节点状态

        Args:
            node_id: 节点ID
            new_status: 新状态

        Raises:
            ValueError: 如果节点不存在
        """
        pass

    @abstractmethod
    def get_nodes_by_type(self, node_type: NodeType) -> list[NodeData]:
        """
        根据节点类型获取节点列表

        Args:
            node_type: 节点类型

        Returns:
            list[NodeData]: 节点列表
        """
        pass

    @abstractmethod
    def get_nodes_by_status(self, status: str) -> list[NodeData]:
        """
        根据状态获取节点列表

        Args:
            status: 节点状态

        Returns:
            list[NodeData]: 节点列表
        """
        pass

    @abstractmethod
    def get_nodes_by_trace_type(self, trace_type: TraceType) -> list[NodeData]:
        """
        根据轨迹类型获取节点列表

        Args:
            trace_type: 轨迹类型

        Returns:
            list[NodeData]: 节点列表
        """
        pass

    @abstractmethod
    def get_failed_nodes(self) -> list[NodeData]:
        """
        获取所有失败节点

        Returns:
            list[NodeData]: 失败节点列表
        """
        pass

    @abstractmethod
    def add_edge(self, edge_data: EdgeData, edge_index: int) -> None:
        """
        添加边到存储

        Args:
            edge_data: 边数据
            edge_index: 边的索引

        Raises:
            ValueError: 如果节点不存在
        """
        pass

    @abstractmethod
    def get_edges_from_node(self, node_id: str) -> list[EdgeData]:
        """
        获取从指定节点出发的所有边

        Args:
            node_id: 节点ID

        Returns:
            list[EdgeData]: 边列表
        """
        pass

    @abstractmethod
    def get_edges_to_node(self, node_id: str) -> list[EdgeData]:
        """
        获取指向指定节点的所有边

        Args:
            node_id: 节点ID

        Returns:
            list[EdgeData]: 边列表
        """
        pass

    @abstractmethod
    def get_all_nodes(self) -> dict[str, NodeData]:
        """
        获取所有节点

        Returns:
            dict[str, NodeData]: 节点字典
        """
        pass

    @abstractmethod
    def get_all_edges(self) -> list[EdgeData]:
        """
        获取所有边

        Returns:
            list[EdgeData]: 边列表
        """
        pass

    @abstractmethod
    def get_node_count(self) -> int:
        """
        获取节点总数

        Returns:
            int: 节点总数
        """
        pass

    @abstractmethod
    def get_edge_count(self) -> int:
        """
        获取边总数

        Returns:
            int: 边总数
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """
        关闭存储连接
        """
        pass
