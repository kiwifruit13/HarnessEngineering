# -*- coding: utf-8 -*-
"""
统一响应格式 - ToolResult

特性：
- 支持两种输出格式：JSON 和 Markdown
- 统一错误处理
- 完整的元数据支持
"""

import json
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Any, Optional, Dict


@dataclass
class ToolResult:
    """
    工具执行结果
    
    设计原则：
    - 结构化数据存储，支持多种输出格式
    - 错误信息标准化
    - 元数据完整追踪
    """
    
    # 核心字段（带默认值，兼容 Python 3.13）
    success: bool = True
    status: str = "success"  # "success" | "error"
    
    # 数据字段
    data: Any = None
    error: Optional[Dict[str, Any]] = None
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 时间戳
    timestamp: str = field(default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
    
    # ========== 工厂方法 ==========
    
    @classmethod
    def success(cls, data: Any = None, metadata: Dict = None, **kwargs) -> 'ToolResult':
        """创建成功结果"""
        return cls(
            success=True,
            status="success",
            data=data,
            metadata=metadata or {},
            **kwargs
        )
    
    @classmethod
    def error(cls, code: str, message: str, metadata: Dict = None, **kwargs) -> 'ToolResult':
        """创建错误结果"""
        return cls(
            success=False,
            status="error",
            error={
                "code": code,
                "message": message,
                "retryable": kwargs.get("retryable", False)
            },
            metadata=metadata or {},
            **kwargs
        )
    
    # ========== 输出格式转换 ==========
    
    def to_json(self) -> dict:
        """转换为 JSON 字典"""
        result = {
            "success": self.success,
            "status": self.status,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }
        
        if self.success and self.data is not None:
            result["data"] = self.data
        
        if not self.success and self.error:
            result["error"] = self.error
        
        return result
    
    def to_json_string(self, indent: int = 2) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_json(), ensure_ascii=False, indent=indent)
    
    def to_markdown(self) -> str:
        """
        转换为 Markdown 格式
        
        整合方案A优点：LLM 友好的输出格式
        """
        if self.success:
            return self._format_success_markdown()
        else:
            return self._format_error_markdown()
    
    def _format_success_markdown(self) -> str:
        """格式化成功结果的 Markdown"""
        lines = ["## ✅ 操作成功\n"]
        
        # 添加元数据
        if self.metadata:
            lines.append("### 执行信息\n")
            for key, value in self.metadata.items():
                if value is not None:
                    lines.append(f"**{key}**: {value}")
            lines.append("")
        
        # 添加数据
        if self.data is not None:
            lines.append("### 结果数据\n")
            if isinstance(self.data, dict):
                for key, value in self.data.items():
                    lines.append(f"**{key}**: {value}")
            elif isinstance(self.data, list):
                for i, item in enumerate(self.data, 1):
                    lines.append(f"{i}. {item}")
            else:
                lines.append(f"```\n{self.data}\n```")
        
        return "\n".join(lines)
    
    def _format_error_markdown(self) -> str:
        """格式化错误结果的 Markdown"""
        lines = ["## ❌ 操作失败\n"]
        
        if self.error:
            lines.append("### 错误信息\n")
            lines.append(f"**错误码**: `{self.error.get('code', 'UNKNOWN')}`")
            lines.append(f"**错误描述**: {self.error.get('message', '未知错误')}")
            
            if self.error.get('retryable'):
                lines.append("\n⚠️ 此错误可重试")
        
        if self.metadata:
            lines.append("\n### 上下文信息\n")
            for key, value in self.metadata.items():
                if value is not None:
                    lines.append(f"**{key}**: {value}")
        
        return "\n".join(lines)
    
    # ========== 便捷方法 ==========
    
    def with_metadata(self, **kwargs) -> 'ToolResult':
        """添加元数据（链式调用）"""
        self.metadata.update(kwargs)
        return self
    
    def with_data(self, **kwargs) -> 'ToolResult':
        """添加数据（链式调用）"""
        if self.data is None:
            self.data = {}
        if isinstance(self.data, dict):
            self.data.update(kwargs)
        return self


# ========== 常用错误码定义 ==========

class ErrorCode:
    """错误码常量"""
    
    # 工具相关
    TOOL_NOT_FOUND = "TOOL_NOT_FOUND"
    TOOL_DEPRECATED = "TOOL_DEPRECATED"
    
    # 参数相关
    INVALID_PARAMS = "INVALID_PARAMS"
    MISSING_PARAMS = "MISSING_PARAMS"
    
    # 安全相关
    SECURITY_VIOLATION = "SECURITY_VIOLATION"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    DANGEROUS_OPERATION = "DANGEROUS_OPERATION"
    
    # 执行相关
    EXECUTION_ERROR = "EXECUTION_ERROR"
    TIMEOUT = "TIMEOUT"
    NETWORK_ERROR = "NETWORK_ERROR"
    
    # 资源相关
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    
    # 其他
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
