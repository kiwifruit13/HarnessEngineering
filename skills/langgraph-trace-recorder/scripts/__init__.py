"""
LangGraph 轨迹记录器
实时构建双类型知识图谱（问答轨迹/命令轨迹）
支持多种存储后端（内存/Redis）
"""

from scripts.definitions import (
    NodeType,
    EdgeType,
    TraceType,
    NodeData,
    EdgeData,
    GraphData,
    GraphMetadata,
    validate_dict_as_node,
    validate_dict_as_edge,
    get_current_timestamp
)

from scripts.classifier import NodeClassifier, classify_node

from scripts.storage_backend import GraphStorageBackend

from scripts.memory_storage import MemoryGraphStorage

from scripts.graph_builder import KnowledgeGraph, create_graph_from_dict

from scripts.graph_exporter import GraphExporter

from scripts.callback_handler import TraceRecorderCallback, create_callback_handler

# Redis 存储后端是可选的
try:
    from scripts.redis_storage import RedisGraphStorage
    _redis_available = True
except ImportError:
    _redis_available = False
    RedisGraphStorage = None  # type: ignore

__all__ = [
    # Enums
    "NodeType",
    "EdgeType",
    "TraceType",
    # Type Aliases
    "NodeData",
    "EdgeData",
    "GraphData",
    "GraphMetadata",
    # Utilities
    "validate_dict_as_node",
    "validate_dict_as_edge",
    "get_current_timestamp",
    # Storage Backend
    "GraphStorageBackend",
    "MemoryGraphStorage",
    # Classifier
    "NodeClassifier",
    "classify_node",
    # Graph Builder
    "KnowledgeGraph",
    "create_graph_from_dict",
    # Exporter
    "GraphExporter",
    # Callback Handler
    "TraceRecorderCallback",
    "create_callback_handler",
]

# 如果 Redis 可用，添加到导出列表
if _redis_available:
    __all__.append("RedisGraphStorage")

__version__ = "1.1.0"
