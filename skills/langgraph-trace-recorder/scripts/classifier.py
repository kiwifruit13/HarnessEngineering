"""
节点分类器 - 基于规则识别问答/命令类型
严格遵循类型安全协议
"""

from __future__ import annotations

import re
from typing import Literal, Pattern
from scripts.definitions import NodeType, TraceType


class NodeClassifier:
    """
    节点分类器
    根据节点名称、输出内容等特征自动识别节点类型
    """

    # 问答类型节点的命名模式（正则表达式）
    QA_PATTERNS: list[Pattern[str]] = [
        re.compile(r"query", re.IGNORECASE),
        re.compile(r"answer", re.IGNORECASE),
        re.compile(r"respond", re.IGNORECASE),
        re.compile(r"reason", re.IGNORECASE),
        re.compile(r"chat", re.IGNORECASE),
        re.compile(r"llm", re.IGNORECASE),
        re.compile(r"generate", re.IGNORECASE),
        re.compile(r"explain", re.IGNORECASE),
    ]

    # 命令类型节点的命名模式（正则表达式）
    COMMAND_PATTERNS: list[Pattern[str]] = [
        re.compile(r"execute", re.IGNORECASE),
        re.compile(r"run", re.IGNORECASE),
        re.compile(r"call", re.IGNORECASE),
        re.compile(r"tool", re.IGNORECASE),
        re.compile(r"action", re.IGNORECASE),
        re.compile(r"function", re.IGNORECASE),
        re.compile(r"api", re.IGNORECASE),
        re.compile(r"script", re.IGNORECASE),
        re.compile(r"command", re.IGNORECASE),
        re.compile(r"operation", re.IGNORECASE),
    ]

    @staticmethod
    def classify_by_name(
        node_name: str,
        default_type: NodeType = NodeType.RESULT
    ) -> NodeType:
        """
        根据节点名称分类节点类型

        Args:
            node_name: 节点名称
            default_type: 默认节点类型（无法分类时返回）

        Returns:
            NodeType: 节点类型
        """
        if not isinstance(node_name, str):
            return default_type

        # 检查问答类型模式
        for pattern in NodeClassifier.QA_PATTERNS:
            if pattern.search(node_name):
                return NodeType.ANSWER

        # 检查命令类型模式
        for pattern in NodeClassifier.COMMAND_PATTERNS:
            if pattern.search(node_name):
                return NodeType.COMMAND

        # 无法识别，返回默认类型
        return default_type

    @staticmethod
    def classify_by_content(
        content: str,
        default_type: NodeType = NodeType.RESULT
    ) -> NodeType:
        """
        根据内容特征分类节点类型

        Args:
            content: 节点内容
            default_type: 默认节点类型（无法分类时返回）

        Returns:
            NodeType: 节点类型
        """
        if not isinstance(content, str):
            return default_type

        # 检查是否包含工具调用的特征
        tool_indicators = ["tool_calls", "function_call", "execute", "result:"]
        for indicator in tool_indicators:
            if indicator in content.lower():
                return NodeType.COMMAND

        # 检查是否包含自然语言文本的特征
        if len(content) > 50 and not any(indicator in content.lower() for indicator in tool_indicators):
            return NodeType.ANSWER

        return default_type

    @staticmethod
    def determine_trace_type(node_type: NodeType) -> TraceType:
        """
        根据节点类型确定轨迹类型

        Args:
            node_type: 节点类型

        Returns:
            TraceType: 轨迹类型
        """
        if node_type in (NodeType.QUESTION, NodeType.ANSWER, NodeType.REASONING):
            return TraceType.QA_TRACE
        elif node_type in (NodeType.COMMAND, NodeType.RESULT):
            return TraceType.COMMAND_TRACE
        else:
            # 默认归入命令轨迹
            return TraceType.COMMAND_TRACE

    @classmethod
    def classify(
        cls,
        node_name: str,
        content: str,
        default_type: NodeType = NodeType.RESULT
    ) -> tuple[NodeType, TraceType]:
        """
        综合分类节点类型和轨迹类型

        Args:
            node_name: 节点名称
            content: 节点内容
            default_type: 默认节点类型

        Returns:
            tuple[NodeType, TraceType]: (节点类型, 轨迹类型)
        """
        # 优先根据节点名称分类
        node_type = cls.classify_by_name(node_name, default_type)

        # 如果无法根据名称分类，则根据内容分类
        if node_type == default_type:
            node_type = cls.classify_by_content(content, default_type)

        # 确定轨迹类型
        trace_type = cls.determine_trace_type(node_type)

        return node_type, trace_type


def classify_node(
    node_name: str,
    content: str,
    default_type: NodeType = NodeType.RESULT
) -> tuple[NodeType, TraceType]:
    """
    节点分类的便捷函数

    Args:
        node_name: 节点名称
        content: 节点内容
        default_type: 默认节点类型

    Returns:
        tuple[NodeType, TraceType]: (节点类型, 轨迹类型)
    """
    classifier = NodeClassifier()
    return classifier.classify(node_name, content, default_type)
