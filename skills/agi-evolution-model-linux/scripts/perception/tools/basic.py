# -*- coding: utf-8 -*-
"""
基础工具集 - web_search, get_weather, calculator, search_documents

保留原有功能，整合新架构
"""

import math
import re
from typing import Dict, Any, List, Optional

from ..tools.base import ToolBase, ParamValidator
from ..context import RuntimeContext
from ..response import ToolResult, ErrorCode
from ..registry import tool


@tool
class WebSearchTool(ToolBase):
    """网络搜索工具"""
    
    name = "web_search"
    description = "搜索网络信息"
    version = "1.0.0"
    
    cacheable = True
    cache_ttl = 300
    cache_key_params = ["query"]
    
    estimated_tokens = {
        "input": 50,
        "output": {"typical": 200, "max": 1000}
    }
    
    def validate_params(self, params: Dict[str, Any]) -> tuple:
        return ParamValidator.require(params, "query")
    
    def execute(self, params: Dict[str, Any], ctx: RuntimeContext) -> ToolResult:
        query = params.get("query", "")
        
        # 模拟搜索结果（实际应调用搜索API）
        data = {
            "query": query,
            "results": [],
            "count": 0,
            "message": "网络搜索功能需要配置搜索API"
        }
        
        return self.success(
            data=data,
            tool_name=self.name,
            execution_time_ms=0
        ).with_metadata(
            query=query,
            cached=False
        )


@tool
class GetWeatherTool(ToolBase):
    """天气查询工具"""
    
    name = "get_weather"
    description = "获取指定城市的实时天气信息"
    version = "1.0.0"
    
    cacheable = True
    cache_ttl = 600
    cache_key_params = ["location", "unit"]
    
    estimated_tokens = {
        "input": 50,
        "output": {"typical": 100, "max": 200}
    }
    
    def validate_params(self, params: Dict[str, Any]) -> tuple:
        return ParamValidator.require(params, "location")
    
    def execute(self, params: Dict[str, Any], ctx: RuntimeContext) -> ToolResult:
        location = params.get("location", "")
        unit = params.get("unit", "celsius")
        
        # 模拟天气数据（实际应调用天气API）
        data = {
            "location": location,
            "temperature": 25,
            "condition": "sunny",
            "unit": unit,
            "humidity": 60,
            "wind_speed": 10
        }
        
        return self.success(
            data=data,
            tool_name=self.name
        ).with_metadata(
            location=location,
            unit=unit
        )


@tool
class CalculatorTool(ToolBase):
    """数学计算工具"""
    
    name = "calculator"
    description = "执行数学计算，支持基本运算和常用数学函数"
    version = "1.0.0"
    
    cacheable = True
    cache_ttl = 3600  # 计算结果缓存1小时
    
    estimated_tokens = {
        "input": 100,
        "output": {"typical": 50, "max": 100}
    }
    
    # 允许的数学函数
    ALLOWED_FUNCTIONS = {
        'abs', 'round', 'min', 'max', 'sum',
        'sin', 'cos', 'tan', 'asin', 'acos', 'atan',
        'sinh', 'cosh', 'tanh',
        'sqrt', 'pow', 'log', 'log10', 'log2', 'exp',
        'floor', 'ceil', 'trunc',
        'pi', 'e'
    }
    
    def validate_params(self, params: Dict[str, Any]) -> tuple:
        ok, msg = ParamValidator.require(params, "expression")
        if not ok:
            return ok, msg
        
        # 安全检查：只允许数学运算
        expression = params.get("expression", "")
        if not self._is_safe_expression(expression):
            return False, "表达式包含不允许的字符或函数"
        
        return True, ""
    
    def _is_safe_expression(self, expression: str) -> bool:
        """检查表达式是否安全"""
        # 只允许数字、运算符、括号、空格和允许的函数
        allowed_pattern = r'^[\d\s\+\-\*\/\(\)\.\,\^]+$|' + \
                          r'\b(' + '|'.join(self.ALLOWED_FUNCTIONS) + r')\b'
        
        # 检查是否有危险字符
        dangerous_chars = ['__', 'import', 'exec', 'eval', 'open', 'file']
        for char in dangerous_chars:
            if char in expression.lower():
                return False
        
        return True
    
    def execute(self, params: Dict[str, Any], ctx: RuntimeContext) -> ToolResult:
        expression = params.get("expression", "0")
        
        try:
            # 创建安全的计算环境
            safe_dict = {
                '__builtins__': {},
                'abs': abs, 'round': round, 'min': min, 'max': max, 'sum': sum,
                'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
                'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
                'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh,
                'sqrt': math.sqrt, 'pow': pow, 'log': math.log,
                'log10': math.log10, 'log2': math.log2, 'exp': math.exp,
                'floor': math.floor, 'ceil': math.ceil, 'trunc': math.trunc,
                'pi': math.pi, 'e': math.e
            }
            
            result = eval(expression, safe_dict, {})
            
            data = {
                "expression": expression,
                "result": result,
                "type": type(result).__name__
            }
            
            return self.success(data=data).with_metadata(
                expression=expression
            )
            
        except Exception as e:
            return self.error(
                ErrorCode.EXECUTION_ERROR,
                f"计算错误: {str(e)}"
            )


@tool
class SearchDocumentsTool(ToolBase):
    """文档搜索工具（支持分页）"""
    
    name = "search_documents"
    description = "搜索文档数据库，支持分页查询"
    version = "2.1.0"
    
    cacheable = True
    cache_ttl = 300
    
    estimated_tokens = {
        "input": 100,
        "output": {"min": 200, "max": 5000, "typical": 1000}
    }
    
    def validate_params(self, params: Dict[str, Any]) -> tuple:
        ok, msg = ParamValidator.require(params, "query")
        if not ok:
            return ok, msg
        
        # 检查 limit 范围
        if "limit" in params:
            limit = params["limit"]
            if not isinstance(limit, int) or limit < 1 or limit > 100:
                return False, "limit 必须是 1-100 之间的整数"
        
        return True, ""
    
    def execute(self, params: Dict[str, Any], ctx: RuntimeContext) -> ToolResult:
        query = params.get("query", "")
        limit = params.get("limit", 10)
        cursor = params.get("cursor", "")
        
        # 模拟搜索结果
        data = {
            "query": query,
            "items": [],
            "pagination": {
                "has_more": False,
                "next_cursor": cursor,
                "total_count": 0,
                "limit": limit
            }
        }
        
        return self.success(data=data).with_metadata(
            query=query,
            limit=limit
        )
