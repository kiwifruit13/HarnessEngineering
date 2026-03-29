# -*- coding: utf-8 -*-
"""
感知节点模块 - 统一工具调用接口

架构说明：
- node.py: 感知节点主类
- context.py: 运行时上下文
- registry.py: 工具注册表
- response.py: 统一响应格式
- tools/: 工具插件目录
- _core/: 核心算法（Rust编译目标）
"""

from .node import PerceptionNode
from .context import RuntimeContext
from .response import ToolResult
from .registry import ToolRegistry, tool

__all__ = [
    "PerceptionNode",
    "RuntimeContext", 
    "ToolResult",
    "ToolRegistry",
    "tool",
]

__version__ = "2.0.0"
