# -*- coding: utf-8 -*-
"""
工具基类 - 统一工具接口

设计原则：
- 所有工具必须继承此基类
- 统一的参数验证和安全检查
- 支持缓存和重试配置
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional, List

from ..context import RuntimeContext
from ..response import ToolResult, ErrorCode


class ToolBase(ABC):
    """
    工具基类
    
    子类必须实现：
    - name: 工具名称
    - description: 工具描述
    - execute(): 执行逻辑
    
    可选实现：
    - validate_params(): 参数验证
    - security_check(): 安全检查
    """
    
    # ========== 必须定义的类属性 ==========
    
    name: str = ""  # 工具名称（snake_case）
    description: str = ""  # 工具描述
    
    # ========== 可选的类属性 ==========
    
    version: str = "1.0.0"
    
    # 缓存配置
    cacheable: bool = False
    cache_ttl: int = 600
    cache_key_params: List[str] = None  # 参与缓存键的参数
    
    # 安全标记
    dangerous: bool = False  # 是否为危险工具
    
    # 性能预估
    estimated_tokens: Dict[str, Any] = None
    
    # 废弃信息
    deprecated: bool = False
    sunset_date: Optional[str] = None
    replacement: Optional[str] = None
    
    # ========== 核心方法 ==========
    
    @abstractmethod
    def execute(self, params: Dict[str, Any], ctx: RuntimeContext) -> ToolResult:
        """
        执行工具逻辑
        
        Args:
            params: 工具参数
            ctx: 运行时上下文
            
        Returns:
            ToolResult 执行结果
        """
        pass
    
    # ========== 生命周期钩子 ==========
    
    def before_execute(self, params: Dict[str, Any], ctx: RuntimeContext) -> Tuple[bool, str]:
        """
        执行前钩子
        
        Returns:
            (是否继续执行, 错误信息)
        """
        return True, ""
    
    def after_execute(self, params: Dict[str, Any], ctx: RuntimeContext, result: ToolResult) -> ToolResult:
        """
        执行后钩子
        
        Returns:
            处理后的结果
        """
        return result
    
    # ========== 验证方法 ==========
    
    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """
        参数验证
        
        Returns:
            (是否有效, 错误信息)
        """
        return True, ""
    
    def security_check(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """
        安全检查
        
        危险工具（dangerous=True）必须重写此方法
        
        Returns:
            (是否安全, 错误信息)
        """
        if self.dangerous:
            return False, "危险工具必须实现 security_check 方法"
        return True, ""
    
    # ========== 辅助方法 ==========
    
    def get_param(self, params: Dict[str, Any], key: str, default: Any = None) -> Any:
        """安全获取参数"""
        return params.get(key, default)
    
    def require_param(self, params: Dict[str, Any], key: str) -> Tuple[bool, Any]:
        """
        获取必需参数
        
        Returns:
            (是否存在, 参数值)
        """
        if key not in params:
            return False, None
        return True, params[key]
    
    def error(self, code: str, message: str, **kwargs) -> ToolResult:
        """创建错误结果的便捷方法"""
        return ToolResult.error(code, message, **kwargs)
    
    def success(self, data: Any = None, **kwargs) -> ToolResult:
        """创建成功结果的便捷方法"""
        return ToolResult.success(data, **kwargs)
    
    # ========== 元数据方法 ==========
    
    def get_meta(self) -> Dict[str, Any]:
        """获取工具元信息"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "cacheable": self.cacheable,
            "dangerous": self.dangerous,
            "deprecated": self.deprecated
        }


# ========== 安全检查工具类 ==========

class SecurityChecker:
    """
    安全检查器
    
    整合方案A优点：危险命令拦截
    """
    
    # 危险命令黑名单
    DANGEROUS_COMMANDS = [
        'rm -rf /',
        'rm -rf /*',
        'mkfs',
        'dd if=',
        ':(){:|:&};:',  # fork bomb
        'chmod 777 /',
        'chown -R',
        '> /dev/sda',
        'mv /* /dev/null',
        'wget | sh',
        'curl | sh',
    ]
    
    # 敏感路径黑名单
    SENSITIVE_PATHS = [
        '/etc/passwd',
        '/etc/shadow',
        '/root/.ssh',
        '/var/log',
        '/proc',
        '/sys',
    ]
    
    @classmethod
    def check_command(cls, command: str) -> Tuple[bool, str]:
        """
        检查命令是否安全
        
        Returns:
            (是否安全, 错误信息)
        """
        command_lower = command.lower()
        
        for dangerous in cls.DANGEROUS_COMMANDS:
            if dangerous.lower() in command_lower:
                return False, f"命令包含危险操作: {dangerous}"
        
        return True, ""
    
    @classmethod
    def check_path(cls, path: str, write: bool = False) -> Tuple[bool, str]:
        """
        检查路径是否安全
        
        Args:
            path: 文件路径
            write: 是否为写入操作
            
        Returns:
            (是否安全, 错误信息)
        """
        import os
        abs_path = os.path.abspath(path)
        
        for sensitive in cls.SENSITIVE_PATHS:
            if abs_path.startswith(sensitive):
                if write:
                    return False, f"禁止写入系统敏感路径: {sensitive}"
                # 读取敏感路径需要额外检查
                if sensitive in ['/etc/shadow', '/root/.ssh']:
                    return False, f"禁止访问敏感路径: {sensitive}"
        
        return True, ""


# ========== 参数验证工具类 ==========

class ParamValidator:
    """参数验证工具"""
    
    @staticmethod
    def require(params: Dict, *keys) -> Tuple[bool, str]:
        """检查必需参数"""
        missing = [k for k in keys if k not in params]
        if missing:
            return False, f"缺少必需参数: {', '.join(missing)}"
        return True, ""
    
    @staticmethod
    def type_check(params: Dict, key: str, expected_type: type) -> Tuple[bool, str]:
        """检查参数类型"""
        if key not in params:
            return True, ""  # 不存在则跳过
        
        value = params[key]
        if not isinstance(value, expected_type):
            return False, f"参数 '{key}' 类型错误，期望 {expected_type.__name__}，实际 {type(value).__name__}"
        return True, ""
    
    @staticmethod
    def range_check(params: Dict, key: str, min_val: Any = None, max_val: Any = None) -> Tuple[bool, str]:
        """检查参数范围"""
        if key not in params:
            return True, ""
        
        value = params[key]
        
        if min_val is not None and value < min_val:
            return False, f"参数 '{key}' 值 {value} 小于最小值 {min_val}"
        
        if max_val is not None and value > max_val:
            return False, f"参数 '{key}' 值 {value} 大于最大值 {max_val}"
        
        return True, ""
    
    @staticmethod
    def enum_check(params: Dict, key: str, allowed: List) -> Tuple[bool, str]:
        """检查参数是否在允许列表中"""
        if key not in params:
            return True, ""
        
        value = params[key]
        if value not in allowed:
            return False, f"参数 '{key}' 值 '{value}' 不在允许列表中: {allowed}"
        return True, ""
