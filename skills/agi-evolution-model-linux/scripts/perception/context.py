# -*- coding: utf-8 -*-
"""
运行时上下文 - 统一上下文管理

整合方案A优点：
- runtime 降级机制：兼容平台绑定与独立运行
- 自动获取用户/会话信息
- 统一 trace_id 生成
"""

import os
import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, Any


@dataclass
class RuntimeContext:
    """
    运行时上下文
    
    设计原则：
    - 优先使用平台提供的 runtime
    - 无平台环境自动创建默认上下文
    - 所有工具共享同一上下文实例
    """
    
    # 基础信息
    trace_id: str
    timestamp: str
    
    # 平台上下文（可选）
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    bot_id: Optional[str] = None
    
    # 工作路径
    workspace_path: str = "."
    
    # 配置选项
    debug: bool = False
    output_format: str = "json"  # "json" | "markdown"
    
    # 元数据
    metadata: dict = field(default_factory=dict)
    
    @classmethod
    def from_runtime(cls, runtime: Any = None, method: str = "") -> 'RuntimeContext':
        """
        从平台 runtime 创建上下文，或创建默认上下文
        
        Args:
            runtime: 平台提供的运行时对象（可选）
            method: 工具方法名，用于 trace_id 生成
            
        Returns:
            RuntimeContext 实例
        """
        if runtime is not None and hasattr(runtime, 'context'):
            # 平台环境：从 runtime.context 提取信息
            return cls._from_platform(runtime.context, method)
        
        # 独立运行：创建默认上下文
        return cls._create_default(method)
    
    @classmethod
    def _from_platform(cls, platform_context: Any, method: str) -> 'RuntimeContext':
        """从平台上下文提取信息"""
        # 尝试获取平台信息
        user_id = getattr(platform_context, 'user_id', None)
        conversation_id = getattr(platform_context, 'conversation_id', None)
        bot_id = getattr(platform_context, 'bot_id', None)
        workspace = getattr(platform_context, 'workspace_path', '.')
        
        # 生成 trace_id
        trace_id = cls._generate_trace_id(method)
        
        return cls(
            trace_id=trace_id,
            timestamp=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            user_id=user_id,
            conversation_id=conversation_id,
            bot_id=bot_id,
            workspace_path=workspace or ".",
            metadata={"source": "platform"}
        )
    
    @classmethod
    def _create_default(cls, method: str) -> 'RuntimeContext':
        """创建默认上下文"""
        trace_id = cls._generate_trace_id(method)
        workspace = os.getenv("COZE_WORKSPACE_PATH", os.getcwd())
        
        return cls(
            trace_id=trace_id,
            timestamp=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            workspace_path=workspace,
            metadata={"source": "standalone"}
        )
    
    @staticmethod
    def _generate_trace_id(method: str) -> str:
        """
        生成 trace_id
        
        格式: trace_{日期}_{uuid前12位}_{method}
        """
        date_str = datetime.utcnow().strftime("%Y%m%d")
        uuid_str = uuid.uuid4().hex[:12]
        
        if method:
            return f"trace_{date_str}_{uuid_str}_{method}"
        return f"trace_{date_str}_{uuid_str}"
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "trace_id": self.trace_id,
            "timestamp": self.timestamp,
            "user_id": self.user_id,
            "conversation_id": self.conversation_id,
            "workspace_path": self.workspace_path,
            "debug": self.debug,
            "output_format": self.output_format,
            "metadata": self.metadata
        }
