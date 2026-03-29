# -*- coding: utf-8 -*-
"""
工具注册表 - 统一工具管理

特性：
- 装饰器式注册
- 动态工具发现
- 工具元信息查询
"""

from typing import Dict, Type, List, Optional, Any
from dataclasses import dataclass


@dataclass
class ToolMeta:
    """工具元信息"""
    name: str
    description: str
    version: str = "1.0.0"
    
    # 配置
    cacheable: bool = False
    cache_ttl: int = 600
    cache_key_params: List[str] = None
    
    # 安全标记
    dangerous: bool = False
    
    # 性能预估
    estimated_tokens: Dict[str, Any] = None
    
    # 废弃信息
    deprecated: bool = False
    sunset_date: Optional[str] = None
    replacement: Optional[str] = None


class ToolRegistry:
    """
    工具注册表
    
    使用方式：
    1. 装饰器注册：@tool
    2. 手动注册：ToolRegistry.register(ToolClass)
    3. 查询工具：ToolRegistry.get("tool_name")
    """
    
    _tools: Dict[str, Type] = {}
    _metas: Dict[str, ToolMeta] = {}
    
    @classmethod
    def register(cls, tool_class: Type) -> Type:
        """
        注册工具
        
        Args:
            tool_class: 工具类（必须继承 ToolBase）
            
        Returns:
            原工具类（支持装饰器用法）
        """
        # 获取工具元信息
        meta = cls._extract_meta(tool_class)
        
        # 注册
        cls._tools[meta.name] = tool_class
        cls._metas[meta.name] = meta
        
        return tool_class
    
    @classmethod
    def get(cls, name: str) -> Optional[Type]:
        """获取工具类"""
        return cls._tools.get(name)
    
    @classmethod
    def get_meta(cls, name: str) -> Optional[ToolMeta]:
        """获取工具元信息"""
        return cls._metas.get(name)
    
    @classmethod
    def list_tools(cls) -> List[Dict[str, Any]]:
        """列出所有工具"""
        result = []
        for name, meta in cls._metas.items():
            result.append({
                "name": meta.name,
                "description": meta.description,
                "version": meta.version,
                "cacheable": meta.cacheable,
                "dangerous": meta.dangerous,
                "deprecated": meta.deprecated
            })
        return result
    
    @classmethod
    def list_by_category(cls, category: str = None) -> List[Dict]:
        """按类别列出工具"""
        # TODO: 实现分类逻辑
        return cls.list_tools()
    
    @classmethod
    def exists(cls, name: str) -> bool:
        """检查工具是否存在"""
        return name in cls._tools
    
    @classmethod
    def unregister(cls, name: str) -> bool:
        """注销工具"""
        if name in cls._tools:
            del cls._tools[name]
            del cls._metas[name]
            return True
        return False
    
    @classmethod
    def clear(cls):
        """清空注册表"""
        cls._tools.clear()
        cls._metas.clear()
    
    @staticmethod
    def _extract_meta(tool_class: Type) -> ToolMeta:
        """从工具类提取元信息"""
        return ToolMeta(
            name=getattr(tool_class, 'name', tool_class.__name__),
            description=getattr(tool_class, 'description', tool_class.__doc__ or ""),
            version=getattr(tool_class, 'version', "1.0.0"),
            cacheable=getattr(tool_class, 'cacheable', False),
            cache_ttl=getattr(tool_class, 'cache_ttl', 600),
            cache_key_params=getattr(tool_class, 'cache_key_params', None),
            dangerous=getattr(tool_class, 'dangerous', False),
            estimated_tokens=getattr(tool_class, 'estimated_tokens', None),
            deprecated=getattr(tool_class, 'deprecated', False),
            sunset_date=getattr(tool_class, 'sunset_date', None),
            replacement=getattr(tool_class, 'replacement', None)
        )


# ========== 装饰器 ==========

def tool(cls: Type) -> Type:
    """
    工具注册装饰器
    
    用法：
        @tool
        class FileReadTool(ToolBase):
            name = "file_read"
            ...
    """
    return ToolRegistry.register(cls)


# ========== 便捷函数 ==========

def get_tool(name: str) -> Optional[Type]:
    """获取工具类的便捷函数"""
    return ToolRegistry.get(name)


def list_tools() -> List[Dict]:
    """列出所有工具的便捷函数"""
    return ToolRegistry.list_tools()
