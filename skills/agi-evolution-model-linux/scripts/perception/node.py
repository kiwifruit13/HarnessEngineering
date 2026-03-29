# -*- coding: utf-8 -*-
"""
感知节点主类 - 统一工具调用入口

核心功能：
- 统一的工具调用接口
- 缓存机制
- 重试机制
- 全链路追踪
- SSE 流式响应
- 可观测性
"""

import time
import hashlib
import logging
from collections import OrderedDict
from typing import Dict, Any, Optional, List, Callable

from .context import RuntimeContext
from .response import ToolResult, ErrorCode
from .registry import ToolRegistry
from .tools.base import ToolBase

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('perception_node')


# ==================== 缓存实现 ====================

class ToolCache:
    """工具结果缓存（LRU）"""
    
    def __init__(self, max_size: int = 1000):
        self.cache: OrderedDict[str, tuple] = OrderedDict()
        self.max_size = max_size
    
    def get_key(self, tool_name: str, params: dict, key_params: List[str] = None) -> str:
        """生成缓存键"""
        if key_params:
            filtered = {k: v for k, v in params.items() if k in key_params}
        else:
            filtered = params
        
        params_str = str(sorted(filtered.items()))
        return hashlib.md5(f"{tool_name}:{params_str}".encode()).hexdigest()
    
    def get(self, tool_name: str, params: dict, key_params: List[str] = None) -> Optional[ToolResult]:
        """获取缓存结果"""
        key = self.get_key(tool_name, params, key_params)
        
        if key in self.cache:
            result, cached_time, ttl = self.cache[key]
            
            # 检查是否过期
            if time.time() - cached_time < ttl:
                # 更新访问顺序
                self.cache.move_to_end(key)
                
                # 标记为缓存命中
                result.metadata['cache'] = {
                    'hit': True,
                    'cached_at': cached_time
                }
                
                logger.info(f"Cache hit for {tool_name}")
                return result
            else:
                del self.cache[key]
        
        return None
    
    def set(self, tool_name: str, params: dict, result: ToolResult, 
            key_params: List[str] = None, ttl: int = 600) -> None:
        """设置缓存结果"""
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)
        
        key = self.get_key(tool_name, params, key_params)
        self.cache[key] = (result, time.time(), ttl)
        logger.info(f"Cached result for {tool_name}")
    
    def clear(self) -> None:
        """清空缓存"""
        self.cache.clear()
        logger.info("Cache cleared")


# ==================== 可观测性管理器 ====================

class ObservabilityManager:
    """可观测性管理器"""
    
    def __init__(self):
        self.metrics = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_time_ms": 0
        }
    
    def record_call(self, tool_name: str, trace_id: str) -> None:
        self.metrics["total_calls"] += 1
        logger.info(f"Tool called: {tool_name}", extra={"trace_id": trace_id})
    
    def record_success(self, tool_name: str, trace_id: str, time_ms: float) -> None:
        self.metrics["successful_calls"] += 1
        self.metrics["total_time_ms"] += time_ms
        logger.info(f"Tool completed: {tool_name} ({time_ms:.2f}ms)", extra={"trace_id": trace_id})
    
    def record_error(self, tool_name: str, trace_id: str, error: str) -> None:
        self.metrics["failed_calls"] += 1
        logger.error(f"Tool failed: {tool_name} - {error}", extra={"trace_id": trace_id})
    
    def record_cache_hit(self) -> None:
        self.metrics["cache_hits"] += 1
    
    def record_cache_miss(self) -> None:
        self.metrics["cache_misses"] += 1
    
    def get_metrics(self) -> dict:
        metrics = self.metrics.copy()
        if metrics["total_calls"] > 0:
            metrics["success_rate"] = metrics["successful_calls"] / metrics["total_calls"]
            metrics["avg_time_ms"] = metrics["total_time_ms"] / metrics["total_calls"]
        return metrics


# ==================== 感知节点主类 ====================

class PerceptionNode:
    """
    感知节点 - 统一工具调用入口
    
    使用方式：
        node = PerceptionNode()
        result = node.call_tool("file_read", {"path": "./data.txt"})
        print(result.to_json())
        print(result.to_markdown())
    """
    
    def __init__(self):
        self._cache = ToolCache()
        self._observability = ObservabilityManager()
        
        # 中间件列表
        self._middlewares: List[Callable] = []
        
        # 自动加载所有工具
        self._load_tools()
    
    def _load_tools(self):
        """加载所有工具"""
        # 导入工具模块，触发注册
        from .tools import basic, file_ops, system_info, process, executor
        
        tool_count = len(ToolRegistry.list_tools())
        logger.info(f"Loaded {tool_count} tools")
    
    # ========== 核心方法 ==========
    
    def call_tool(
        self,
        tool_name: str,
        params: Dict[str, Any],
        runtime: Any = None,
        **options
    ) -> ToolResult:
        """
        调用工具（统一入口）
        
        Args:
            tool_name: 工具名称
            params: 工具参数
            runtime: 平台运行时对象（可选）
            options: 可选配置
                - enable_cache: 是否启用缓存（默认 True）
                - debug: 调试模式
                - output_format: 输出格式（"json" 或 "markdown"）
        
        Returns:
            ToolResult 执行结果
        """
        # 1. 创建上下文
        ctx = RuntimeContext.from_runtime(runtime, tool_name)
        ctx.debug = options.get('debug', False)
        ctx.output_format = options.get('output_format', 'json')
        
        trace_id = ctx.trace_id
        
        # 2. 记录调用
        self._observability.record_call(tool_name, trace_id)
        
        start_time = time.time()
        
        # 3. 获取工具
        tool_class = ToolRegistry.get(tool_name)
        
        if not tool_class:
            return self._create_error_result(
                ErrorCode.TOOL_NOT_FOUND,
                f"工具不存在: {tool_name}",
                trace_id
            )
        
        tool = tool_class()
        meta = ToolRegistry.get_meta(tool_name)
        
        # 4. 检查废弃状态
        if meta and meta.deprecated:
            return self._create_deprecated_result(meta, trace_id)
        
        # 5. 参数验证
        ok, msg = tool.validate_params(params)
        if not ok:
            return self._create_error_result(
                ErrorCode.INVALID_PARAMS,
                msg,
                trace_id
            )
        
        # 6. 安全检查
        ok, msg = tool.security_check(params)
        if not ok:
            return self._create_error_result(
                ErrorCode.SECURITY_VIOLATION,
                msg,
                trace_id
            )
        
        # 7. 缓存检查
        if options.get('enable_cache', True) and meta and meta.cacheable:
            cached = self._cache.get(tool_name, params, meta.cache_key_params)
            if cached:
                self._observability.record_cache_hit()
                return cached
            else:
                self._observability.record_cache_miss()
        
        # 8. 执行工具
        try:
            result = tool.execute(params, ctx)
            
            # 执行后钩子
            result = tool.after_execute(params, ctx, result)
            
            # 添加元数据
            execution_time = (time.time() - start_time) * 1000
            result.metadata.update({
                "tool_name": tool_name,
                "trace_id": trace_id,
                "execution_time_ms": round(execution_time, 2)
            })
            
            # 记录成功
            self._observability.record_success(tool_name, trace_id, execution_time)
            
            # 缓存结果
            if options.get('enable_cache', True) and meta and meta.cacheable and result.success:
                self._cache.set(
                    tool_name, params, result,
                    meta.cache_key_params, meta.cache_ttl
                )
            
            # 调试信息
            if ctx.debug:
                result.metadata["debug"] = {
                    "tool_version": meta.version if meta else "unknown",
                    "cacheable": meta.cacheable if meta else False,
                    "params": params
                }
            
            # 格式转换
            if ctx.output_format == "markdown":
                result._markdown_output = result.to_markdown()
            
            return result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            self._observability.record_error(tool_name, trace_id, str(e))
            
            return self._create_error_result(
                ErrorCode.EXECUTION_ERROR,
                f"执行错误: {str(e)}",
                trace_id
            ).with_metadata(
                execution_time_ms=round(execution_time, 2)
            )
    
    def _create_error_result(self, code: str, message: str, trace_id: str) -> ToolResult:
        """创建错误结果"""
        return ToolResult.error(code, message).with_metadata(
            trace_id=trace_id
        )
    
    def _create_deprecated_result(self, meta, trace_id: str) -> ToolResult:
        """创建废弃提示结果"""
        return ToolResult.error(
            ErrorCode.TOOL_DEPRECATED,
            f"工具 '{meta.name}' 已废弃，请使用 '{meta.replacement}'"
        ).with_metadata(
            trace_id=trace_id,
            replacement=meta.replacement,
            sunset_date=meta.sunset_date
        )
    
    # ========== 便捷方法 ==========
    
    def get_metrics(self) -> dict:
        """获取可观测性指标"""
        return self._observability.get_metrics()
    
    def clear_cache(self) -> None:
        """清空缓存"""
        self._cache.clear()
    
    def list_tools(self) -> List[dict]:
        """列出所有工具"""
        return ToolRegistry.list_tools()
    
    def register_tool(self, tool_class: type) -> None:
        """注册新工具"""
        ToolRegistry.register(tool_class)
    
    # ========== 流式响应支持 ==========
    
    def call_tool_streaming(
        self,
        tool_name: str,
        params: Dict[str, Any],
        runtime: Any = None,
        **options
    ):
        """
        流式调用工具（SSE）
        
        Yields:
            SSE 事件字典
        """
        import asyncio
        
        ctx = RuntimeContext.from_runtime(runtime, tool_name)
        trace_id = ctx.trace_id
        
        # 进度事件
        def progress_event(progress: int, message: str):
            return {
                "event": "tool_progress",
                "id": f"evt_{trace_id}_{progress}",
                "data": {
                    "progress": progress,
                    "message": message,
                    "tool_name": tool_name,
                    "trace_id": trace_id
                }
            }
        
        # 开始事件
        yield progress_event(0, f"开始执行工具: {tool_name}")
        
        # 执行工具
        try:
            # 模拟进度
            for i in [25, 50, 75]:
                yield progress_event(i, f"处理中... {i}%")
            
            result = self.call_tool(tool_name, params, runtime, **options)
            
            # 完成事件
            yield {
                "event": "tool_result",
                "id": f"evt_{trace_id}_100",
                "data": result.to_json()
            }
            
        except Exception as e:
            # 错误事件
            yield {
                "event": "tool_error",
                "id": f"evt_{trace_id}_error",
                "data": {
                    "success": False,
                    "error": {
                        "code": ErrorCode.EXECUTION_ERROR,
                        "message": str(e)
                    },
                    "trace_id": trace_id
                }
            }


# ========== 便捷函数 ==========

def create_node() -> PerceptionNode:
    """创建感知节点实例"""
    return PerceptionNode()


def call_tool(tool_name: str, params: dict, runtime=None, **options) -> ToolResult:
    """便捷函数：直接调用工具"""
    node = PerceptionNode()
    return node.call_tool(tool_name, params, runtime, **options)
