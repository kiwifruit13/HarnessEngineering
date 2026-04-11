"""
类型定义模块 - 严格类型安全协议
遵循Type Safety Protocol：
1. 所有函数包含参数和返回值类型注解
2. 禁止传递裸dict，使用TypedDict定义数据结构
3. 严格区分数据对象与序列化字符串
4. 防御性编程，外部输入进行类型检查
"""

from __future__ import annotations

from enum import Enum
from typing import TypedDict, Any, Literal, Required
from datetime import datetime
from pydantic import BaseModel, Field, validator


# ============================================================================
# 枚举定义
# ============================================================================

class NodeType(str, Enum):
    """节点类型枚举"""
    QUESTION = "question"      # 用户问题/查询
    ANSWER = "answer"          # 模型回答/响应
    COMMAND = "command"        # 工具命令/执行
    RESULT = "result"          # 执行结果/输出
    REASONING = "reasoning"    # 推理步骤（手动记录）


class EdgeType(str, Enum):
    """边类型枚举"""
    CONTAINS = "contains"      # 包含关系
    GENERATES = "generates"    # 生成关系
    EXECUTES = "executes"      # 执行关系
    FOLLOWS = "follows"        # 顺序关系
    DEPENDS_ON = "depends_on"  # 依赖关系


class TraceType(str, Enum):
    """轨迹类型枚举"""
    QA_TRACE = "qa_trace"      # 问答轨迹
    COMMAND_TRACE = "command_trace"  # 命令轨迹


class NodeStatus(str, Enum):
    """节点状态枚举"""
    RUNNING = "running"        # 运行中
    COMPLETED = "completed"    # 已完成
    FAILED = "failed"          # 失败


# ============================================================================
# TypedDict 定义 - 数据结构
# ============================================================================

class ErrorInfo(TypedDict):
    """错误信息结构"""
    error_type: str                    # 错误类型（如 TimeoutError, ValueError）
    error_message: str                 # 错误消息
    stack_trace: str | None            # 堆栈跟踪（可选）
    recovery_suggestion: str | None    # 恢复建议（可选）
    timestamp: float                   # 错误发生时间


class NodeData(TypedDict):
    """节点数据结构"""
    id: str                                   # 节点唯一标识
    type: NodeType                            # 节点类型
    label: str                                # 节点标签（显示名称）
    content: str                              # 节点内容（详细描述）
    timestamp: float                          # 时间戳（Unix时间戳）
    trace_type: TraceType                     # 所属轨迹类型
    metadata: dict[str, Any]                  # 元数据（额外属性）


class EdgeData(TypedDict):
    """边数据结构"""
    source: str                               # 源节点ID
    target: str                               # 目标节点ID
    type: EdgeType                            # 边类型
    condition: str | None                     # 条件描述（可选）
    weight: float                             # 权重（默认1.0）


class GraphData(TypedDict):
    """图谱数据结构"""
    nodes: dict[str, NodeData]                # 节点集合（id -> NodeData）
    edges: list[EdgeData]                     # 边集合
    metadata: dict[str, Any]                  # 图谱元数据


# ============================================================================
# Pydantic Model 定义 - 数据验证
# ============================================================================

class NodeModel(BaseModel):
    """节点模型 - 用于输入验证"""
    id: str = Field(..., description="节点唯一标识")
    type: NodeType = Field(..., description="节点类型")
    label: str = Field(..., description="节点标签")
    content: str = Field(..., description="节点内容")
    timestamp: float = Field(..., description="时间戳（Unix时间戳）")
    trace_type: TraceType = Field(..., description="轨迹类型")
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")

    @validator('timestamp')
    def validate_timestamp(cls, v: float) -> float:
        """验证时间戳的合理性"""
        if v < 0:
            raise ValueError(f"时间戳不能为负数: {v}")
        # 检查时间戳是否在合理范围内（1970-2100年）
        if v > 4102444800.0:  # 2100-01-01
            raise ValueError(f"时间戳过大: {v}")
        return v

    def to_data(self) -> NodeData:
        """转换为TypedDict类型"""
        return NodeData(
            id=self.id,
            type=self.type,
            label=self.label,
            content=self.content,
            timestamp=self.timestamp,
            trace_type=self.trace_type,
            metadata=self.metadata
        )


class EdgeModel(BaseModel):
    """边模型 - 用于输入验证"""
    source: str = Field(..., description="源节点ID")
    target: str = Field(..., description="目标节点ID")
    type: EdgeType = Field(..., description="边类型")
    condition: str | None = Field(None, description="条件描述")
    weight: float = Field(default=1.0, description="权重")

    @validator('weight')
    def validate_weight(cls, v: float) -> float:
        """验证权重的合理性"""
        if v < 0:
            raise ValueError(f"权重不能为负数: {v}")
        if v > 100:
            raise ValueError(f"权重过大: {v}")
        return v

    def to_data(self) -> EdgeData:
        """转换为TypedDict类型"""
        return EdgeData(
            source=self.source,
            target=self.target,
            type=self.type,
            condition=self.condition,
            weight=self.weight
        )


class GraphMetadata(TypedDict):
    """图谱元数据"""
    task_id: str                              # 任务ID
    start_time: float                         # 开始时间
    end_time: float | None                    # 结束时间
    total_nodes: int                          # 节点总数
    total_edges: int                          # 边总数
    qa_trace_count: int                       # 问答轨迹节点数
    command_trace_count: int                  # 命令轨迹节点数


# ============================================================================
# LangGraph 状态相关定义
# ============================================================================

class LangGraphNodeState(TypedDict):
    """LangGraph节点状态结构"""
    node_id: str                              # 节点ID
    node_name: str                            # 节点名称
    input_data: dict[str, Any]                # 输入数据
    output_data: dict[str, Any] | None        # 输出数据
    timestamp: float                          # 时间戳
    execution_time: float                     # 执行耗时（秒）
    status: Literal["success", "failed", "running"]  # 执行状态


class LangGraphCallbackData(TypedDict):
    """LangGraph回调数据结构"""
    event_type: Literal["on_node_start", "on_node_end", "on_chain_start", "on_chain_end"]
    node_name: str                            # 节点名称
    node_id: str | None                       # 节点ID（可选）
    input_data: dict[str, Any]                # 输入数据
    output_data: dict[str, Any] | None        # 输出数据（仅on_node_end）
    timestamp: float                          # 时间戳
    metadata: dict[str, Any]                  # 元数据


# ============================================================================
# 类型安全工具函数
# ============================================================================

def validate_dict_as_node(data: dict[str, Any]) -> NodeData:
    """
    将dict验证并转换为NodeData类型
    防御性编程：确保输入数据的类型安全

    Args:
        data: 待验证的字典数据

    Returns:
        NodeData: 验证后的节点数据

    Raises:
        ValueError: 如果数据不符合节点结构要求
        TypeError: 如果数据类型错误
    """
    if not isinstance(data, dict):
        raise TypeError(f"输入必须是dict类型，实际类型: {type(data)}")

    try:
        model = NodeModel(**data)
        return model.to_data()
    except Exception as e:
        raise ValueError(f"节点数据验证失败: {str(e)}")


def validate_dict_as_edge(data: dict[str, Any]) -> EdgeData:
    """
    将dict验证并转换为EdgeData类型
    防御性编程：确保输入数据的类型安全

    Args:
        data: 待验证的字典数据

    Returns:
        EdgeData: 验证后的边数据

    Raises:
        ValueError: 如果数据不符合边结构要求
        TypeError: 如果数据类型错误
    """
    if not isinstance(data, dict):
        raise TypeError(f"输入必须是dict类型，实际类型: {type(data)}")

    try:
        model = EdgeModel(**data)
        return model.to_data()
    except Exception as e:
        raise ValueError(f"边数据验证失败: {str(e)}")


def get_current_timestamp() -> float:
    """
    获取当前时间戳

    Returns:
        float: Unix时间戳
    """
    return datetime.now().timestamp()


def is_valid_node_id(node_id: str) -> bool:
    """
    验证节点ID的有效性

    Args:
        node_id: 节点ID

    Returns:
        bool: 是否有效
    """
    if not isinstance(node_id, str):
        return False
    if len(node_id) == 0 or len(node_id) > 100:
        return False
    # 检查是否包含非法字符
    allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
    return all(c in allowed_chars for c in node_id)
