"""
Redis存储后端实现
提供分布式、持久化的图谱存储能力

**Redis数据结构设计**：
- 节点存储（Hash）: graph:node:{node_id} -> 节点数据（JSON）
- 节点时间索引（Sorted Set）: graph:node:timeline -> node_id, score=timestamp
- 节点类型索引（Set）: graph:node:type:{node_type} -> node_ids
- 节点状态索引（Set）: graph:node:status:{status} -> node_ids
- 节点轨迹类型索引（Set）: graph:node:trace_type:{trace_type} -> node_ids
- 边存储（List）: graph:edges -> [edge_json, ...]
- 边源索引（Hash）: graph:edge:source:{node_id} -> [edge_index, ...]
- 边目标索引（Hash）: graph:edge:target:{node_id} -> [edge_index, ...]
- 导出缓存（String）: graph:cache:{format} -> cached_data, TTL=3600
"""

from __future__ import annotations

import json
import time
from typing import Optional, Any
import redis

from scripts.storage_backend import GraphStorageBackend
from scripts.definitions import (
    NodeData,
    EdgeData,
    NodeType,
    TraceType
)


class RedisGraphStorage(GraphStorageBackend):
    """
    Redis存储后端
    提供分布式、持久化的图谱存储能力

    Attributes:
        redis_client: Redis客户端
        key_prefix: Redis键前缀
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        key_prefix: str = "langgraph",
        **redis_kwargs: Any
    ):
        """
        初始化Redis存储后端

        Args:
            redis_url: Redis连接URL，格式：redis://[host]:[port]/[db]
            key_prefix: Redis键前缀，用于隔离不同应用的数据
            **redis_kwargs: Redis连接参数（socket_timeout等）
        """
        self.redis_client = redis.from_url(
            redis_url,
            decode_responses=True,
            **redis_kwargs
        )
        self.key_prefix = key_prefix

        try:
            self.redis_client.ping()
        except redis.ConnectionError as e:
            raise RuntimeError(f"Redis连接失败: {e}")

    def _make_key(self, *parts: str) -> str:
        """生成Redis键"""
        return f"{self.key_prefix}:" + ":".join(parts)

    def _node_to_json(self, node: NodeData) -> str:
        """将节点数据转换为JSON字符串"""
        data = node.copy()
        if "timestamp" in data:
            data["timestamp"] = data["timestamp"].isoformat()
        return json.dumps(data)

    def _node_from_json(self, json_str: str) -> NodeData:
        """从JSON字符串恢复节点数据"""
        data = json.loads(json_str)
        return NodeData(**data)

    def _edge_to_json(self, edge: EdgeData) -> str:
        """将边数据转换为JSON字符串"""
        return json.dumps(edge)

    def _edge_from_json(self, json_str: str) -> EdgeData:
        """从JSON字符串恢复边数据"""
        data = json.loads(json_str)
        return EdgeData(**data)

    def add_node(self, node_data: NodeData) -> None:
        """添加节点到Redis"""
        node_id = node_data["node_id"]

        if not node_id:
            raise ValueError("节点ID不能为空")

        key = self._make_key("node", node_id)
        if self.redis_client.exists(key):
            raise ValueError(f"节点已存在: {node_id}")

        self.redis_client.hset(
            self._make_key("node", node_id),
            mapping={"data": self._node_to_json(node_data)}
        )

        timestamp = time.time()
        if "timestamp" in node_data and node_data["timestamp"]:
            timestamp = node_data["timestamp"].timestamp()
        self.redis_client.zadd(
            self._make_key("node", "timeline"),
            {node_id: timestamp}
        )

        self.redis_client.sadd(
            self._make_key("node", "type", node_data["node_type"]),
            node_id
        )

        self.redis_client.sadd(
            self._make_key("node", "status", node_data["status"]),
            node_id
        )

        if "trace_type" in node_data and node_data["trace_type"]:
            self.redis_client.sadd(
                self._make_key("node", "trace_type", node_data["trace_type"]),
                node_id
            )

        self._clear_cache()

    def get_node(self, node_id: str) -> Optional[NodeData]:
        """从Redis获取节点数据"""
        key = self._make_key("node", node_id)
        if not self.redis_client.exists(key):
            return None

        data = self.redis_client.hget(key, "data")
        if data is None:
            return None

        return self._node_from_json(data)

    def update_node_status(self, node_id: str, new_status: str) -> None:
        """更新节点状态"""
        node = self.get_node(node_id)
        if node is None:
            raise ValueError(f"节点不存在: {node_id}")

        self.redis_client.srem(
            self._make_key("node", "status", node["status"]),
            node_id
        )

        node["status"] = new_status
        key = self._make_key("node", node_id)
        self.redis_client.hset(
            key,
            mapping={"data": self._node_to_json(node)}
        )

        self.redis_client.sadd(
            self._make_key("node", "status", new_status),
            node_id
        )

        self._clear_cache()

    def get_nodes_by_type(self, node_type: NodeType) -> list[NodeData]:
        """根据节点类型获取节点列表"""
        node_ids = self.redis_client.smembers(
            self._make_key("node", "type", node_type)
        )
        return [self.get_node(nid) for nid in node_ids]

    def get_nodes_by_status(self, status: str) -> list[NodeData]:
        """根据状态获取节点列表"""
        node_ids = self.redis_client.smembers(
            self._make_key("node", "status", status)
        )
        return [self.get_node(nid) for nid in node_ids]

    def get_nodes_by_trace_type(self, trace_type: TraceType) -> list[NodeData]:
        """根据轨迹类型获取节点列表"""
        node_ids = self.redis_client.smembers(
            self._make_key("node", "trace_type", trace_type)
        )
        return [self.get_node(nid) for nid in node_ids]

    def get_failed_nodes(self) -> list[NodeData]:
        """获取所有失败节点"""
        return self.get_nodes_by_status("failed")

    def add_edge(self, edge_data: EdgeData, edge_index: int) -> None:
        """添加边到Redis"""
        source = edge_data["source"]
        target = edge_data["target"]

        if not self.get_node(source):
            raise ValueError(f"源节点不存在: {source}")
        if not self.get_node(target):
            raise ValueError(f"目标节点不存在: {target}")

        self.redis_client.rpush(
            self._make_key("edges"),
            self._edge_to_json(edge_data)
        )

        self.redis_client.lpush(
            self._make_key("edge", "source", source),
            edge_index
        )

        self.redis_client.lpush(
            self._make_key("edge", "target", target),
            edge_index
        )

        self._clear_cache()

    def get_edges_from_node(self, node_id: str) -> list[EdgeData]:
        """获取从指定节点出发的所有边"""
        edge_indices = self.redis_client.lrange(
            self._make_key("edge", "source", node_id),
            0,
            -1
        )

        edges = []
        for idx_str in edge_indices:
            idx = int(idx_str)
            edge = self._get_edge_by_index(idx)
            if edge:
                edges.append(edge)

        return edges

    def get_edges_to_node(self, node_id: str) -> list[EdgeData]:
        """获取指向指定节点的所有边"""
        edge_indices = self.redis_client.lrange(
            self._make_key("edge", "target", node_id),
            0,
            -1
        )

        edges = []
        for idx_str in edge_indices:
            idx = int(idx_str)
            edge = self._get_edge_by_index(idx)
            if edge:
                edges.append(edge)

        return edges

    def _get_edge_by_index(self, index: int) -> Optional[EdgeData]:
        """根据索引获取边数据"""
        edge_json = self.redis_client.lindex(
            self._make_key("edges"),
            index
        )
        if edge_json is None:
            return None

        return self._edge_from_json(edge_json)

    def get_all_nodes(self) -> dict[str, NodeData]:
        """获取所有节点"""
        node_ids = self.redis_client.zrange(
            self._make_key("node", "timeline"),
            0,
            -1
        )

        nodes = {}
        for node_id in node_ids:
            node = self.get_node(node_id)
            if node:
                nodes[node_id] = node

        return nodes

    def get_all_edges(self) -> list[EdgeData]:
        """获取所有边"""
        edge_jsons = self.redis_client.lrange(
            self._make_key("edges"),
            0,
            -1
        )

        return [self._edge_from_json(json_str) for json_str in edge_jsons]

    def get_node_count(self) -> int:
        """获取节点总数"""
        return self.redis_client.zcard(self._make_key("node", "timeline"))

    def get_edge_count(self) -> int:
        """获取边总数"""
        return self.redis_client.llen(self._make_key("edges"))

    def _clear_cache(self) -> None:
        """清除所有导出缓存"""
        pattern = self._make_key("cache", "*")
        keys = self.redis_client.keys(pattern)
        if keys:
            self.redis_client.delete(*keys)

    def get_cached_export(self, format_type: str) -> Optional[str]:
        """获取缓存的导出数据"""
        key = self._make_key("cache", format_type)
        return self.redis_client.get(key)

    def set_cached_export(self, format_type: str, data: str, ttl: int = 3600) -> None:
        """缓存导出数据"""
        key = self._make_key("cache", format_type)
        self.redis_client.setex(key, ttl, data)

    def close(self) -> None:
        """关闭Redis连接"""
        self.redis_client.close()
