# -*- coding: utf-8 -*-
"""
核心算法模块

此模块包含性能关键的核心算法。
优先尝试加载 Rust 编译的 .so 文件，失败则使用 Python 回退实现。

Rust 编译目标：
- generate_trace_id(): 生成追踪 ID
- calculate_cache_key(): 计算缓存键
- normalize_weights(): 权重归一化
- calculate_similarity(): 向量相似度计算
"""

import os
import sys
import hashlib
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

# 尝试加载 Rust 扩展
try:
    # 直接从当前目录导入 .so 文件
    import importlib.util
    _current_dir = os.path.dirname(os.path.abspath(__file__))
    _so_path = os.path.join(_current_dir, '_core_rust.so')
    
    if os.path.exists(_so_path):
        spec = importlib.util.spec_from_file_location("_core_rust", _so_path)
        _core = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_core)
        _RUST_AVAILABLE = True
        print("✅ Rust 扩展已加载")
    else:
        raise ImportError(f"_core_rust.so not found at {_so_path}")
    
except Exception as e:
    _RUST_AVAILABLE = False
    print(f"⚠️ Rust 扩展不可用，使用 Python 回退实现: {e}")


# ========== Python 回退实现 ==========

def _py_generate_trace_id(method: str = "") -> str:
    """
    Python 实现：生成 Trace ID
    
    格式: trace_{日期}_{uuid前12位}_{method}
    """
    date_str = datetime.utcnow().strftime("%Y%m%d")
    uuid_str = uuid.uuid4().hex[:12]
    
    if method:
        return f"trace_{date_str}_{uuid_str}_{method}"
    return f"trace_{date_str}_{uuid_str}"


def _py_calculate_cache_key(tool_name: str, params: Dict, key_params: List[str] = None) -> str:
    """
    Python 实现：计算缓存键
    """
    if key_params:
        filtered = {k: v for k, v in params.items() if k in key_params}
    else:
        filtered = params
    
    params_str = str(sorted(filtered.items()))
    return hashlib.md5(f"{tool_name}:{params_str}".encode()).hexdigest()


def _py_normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    """
    Python 实现：权重归一化
    
    将权重字典归一化，使所有值之和为 1.0
    """
    total = sum(weights.values())
    
    if total == 0:
        # 避免除零，返回均匀分布
        n = len(weights)
        return {k: 1.0 / n for k in weights}
    
    return {k: v / total for k, v in weights.items()}


def _py_calculate_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Python 实现：计算向量相似度（余弦相似度）
    """
    if len(vec1) != len(vec2):
        raise ValueError("向量长度不一致")
    
    if len(vec1) == 0:
        return 0.0
    
    # 计算点积
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    
    # 计算模长
    norm1 = sum(a * a for a in vec1) ** 0.5
    norm2 = sum(b * b for b in vec2) ** 0.5
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)


def _py_hash_string(s: str) -> str:
    """
    Python 实现：字符串哈希
    """
    return hashlib.sha256(s.encode()).hexdigest()[:16]


# ========== 公开接口 ==========

if _RUST_AVAILABLE:
    # 使用 Rust 实现
    generate_trace_id = _core.generate_trace_id
    calculate_cache_key = _core.calculate_cache_key
    normalize_weights = _core.normalize_weights
    calculate_similarity = _core.calculate_similarity
    hash_string = _core.hash_string
else:
    # 使用 Python 回退实现
    generate_trace_id = _py_generate_trace_id
    calculate_cache_key = _py_calculate_cache_key
    normalize_weights = _py_normalize_weights
    calculate_similarity = _py_calculate_similarity
    hash_string = _py_hash_string


# ========== 导出 ==========

__all__ = [
    'generate_trace_id',
    'calculate_cache_key',
    'normalize_weights',
    'calculate_similarity',
    'hash_string',
    'is_rust_available'
]


def is_rust_available() -> bool:
    """检查 Rust 扩展是否可用"""
    return _RUST_AVAILABLE


def get_implementation() -> str:
    """获取当前使用的实现类型"""
    return "rust" if _RUST_AVAILABLE else "python"
