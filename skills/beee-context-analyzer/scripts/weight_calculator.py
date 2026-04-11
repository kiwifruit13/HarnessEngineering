"""
权重计算模块

支持多种计算策略：
- 余弦相似度计算
- 依赖图权重传播
- 时序衰减
- 组合权重

支持 Rust 加速（如果可用）：
- 自动检测 Rust 核心是否可用
- 完整的路径验证机制
- 如果不可用，降级到 Python 实现
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import ctypes
import os
import sys
import hashlib


# ============================================================================
# C 结构体定义（用于 Rust FFI）
# ============================================================================

class EdgeC(ctypes.Structure):
    """C 结构体：边"""
    _fields_ = [
        ("from_node", ctypes.c_char_p),
        ("to_node", ctypes.c_char_p),
        ("weight", ctypes.c_float),
    ]


class NodeWeightC(ctypes.Structure):
    """C 结构体：节点权重"""
    _fields_ = [
        ("node_id", ctypes.c_char_p),
        ("weight", ctypes.c_float),
    ]


class FactorC(ctypes.Structure):
    """C 结构体：因子"""
    _fields_ = [
        ("node_id", ctypes.c_char_p),
        ("weight", ctypes.c_float),
    ]


class WeightResult:
    """权重计算结果"""

    def __init__(self, weights: Dict[str, float], calculator: 'WeightCalculator'):
        """
        初始化权重结果

        Args:
            weights: 权重字典
            calculator: 权重计算器引用（用于调用 top_k）
        """
        self.weights = weights
        self.calculator = calculator

    def top_k(self, k: int = 10) -> List[Tuple[str, float]]:
        """
        获取权重最高的 K 个节点

        Args:
            k: 返回前K个

        Returns:
            [(node_id, weight), ...] 按权重降序排列
        """
        return self.calculator.top_k(self.weights, k)


class WeightCalculator:
    """权重计算器（支持 Rust 加速）"""

    def __init__(self):
        """初始化权重计算器"""
        self.rust_lib = None
        self._load_rust_core()

    def _load_rust_core(self):
        """加载 Rust 计算核心（如果可用）"""
        # 获取脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Rust 核心库路径
        so_path = os.path.join(script_dir, "rust_core/libbeee_core.so")

        if not os.path.exists(so_path):
            print("ℹ️ 未找到 Rust 核心文件，使用 Python 实现")
            return

        # 验证文件
        if not self._validate_rust_lib(so_path):
            print(f"⚠️ Rust 核心文件验证失败 ({so_path})，使用 Python 实现")
            return

        # 尝试加载
        try:
            self.rust_lib = ctypes.CDLL(so_path)
            print(f"✅ Rust 核心已加载: {so_path}")
            print(f"   文件大小: {os.path.getsize(so_path) / 1024:.1f} KB")
            print(f"   文件权限: {oct(os.stat(so_path).st_mode)[-3:]}")

            # 配置 Rust 函数签名
            self._configure_rust_functions()

            # 验证加载后的库
            if not self._validate_loaded_lib():
                print("⚠️ Rust 核心加载后验证失败，使用 Python 实现")
                self.rust_lib = None

        except Exception as e:
            print(f"⚠️ 加载 Rust 核心失败: {e}")
            self.rust_lib = None

    def _configure_rust_functions(self):
        """配置 Rust 函数的参数和返回类型"""
        # cosine_similarity_c
        self.rust_lib.cosine_similarity_c.argtypes = [
            ctypes.POINTER(ctypes.c_float),  # query_ptr
            ctypes.c_size_t,                 # query_len
            ctypes.POINTER(ctypes.c_float),  # candidate_ptr
            ctypes.c_size_t,                 # candidate_len
        ]
        self.rust_lib.cosine_similarity_c.restype = ctypes.c_float

        # compute_similarity_batch_c
        self.rust_lib.compute_similarity_batch_c.argtypes = [
            ctypes.POINTER(ctypes.c_float),  # query_ptr
            ctypes.c_size_t,                 # query_len
            ctypes.POINTER(ctypes.c_float),  # candidates_ptr
            ctypes.c_size_t,                 # n_candidates
            ctypes.POINTER(ctypes.c_float),  # results_ptr
        ]
        self.rust_lib.compute_similarity_batch_c.restype = ctypes.c_int

        # propagate_weights_c
        self.rust_lib.propagate_weights_c.argtypes = [
            ctypes.c_char_p,                  # start_node_ptr
            ctypes.POINTER(EdgeC),            # edges_ptr
            ctypes.c_size_t,                 # n_edges
            ctypes.c_size_t,                 # max_hops
            ctypes.c_float,                  # decay_factor
            ctypes.POINTER(NodeWeightC),     # results_ptr
            ctypes.c_size_t,                 # max_results
        ]
        self.rust_lib.propagate_weights_c.restype = ctypes.c_int

        # combine_factors_c
        self.rust_lib.combine_factors_c.argtypes = [
            ctypes.POINTER(FactorC),          # factors_ptr
            ctypes.c_size_t,                 # n_factors
            ctypes.POINTER(ctypes.c_float),  # coefficients_ptr
            ctypes.c_size_t,                 # n_coefficients
            ctypes.POINTER(NodeWeightC),     # results_ptr
            ctypes.c_size_t,                 # max_results
        ]
        self.rust_lib.combine_factors_c.restype = ctypes.c_int

        # normalize_weights_c
        self.rust_lib.normalize_weights_c.argtypes = [
            ctypes.POINTER(NodeWeightC),     # weights_ptr
            ctypes.c_size_t,                 # n_weights
            ctypes.c_char_p,                 # method_ptr
            ctypes.POINTER(NodeWeightC),     # results_ptr
            ctypes.c_size_t,                 # max_results
        ]
        self.rust_lib.normalize_weights_c.restype = ctypes.c_int

    def _validate_rust_lib(self, so_path: str) -> bool:
        """
        验证 Rust 库文件

        Args:
            so_path: 库文件路径

        Returns:
            验证是否通过
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(so_path):
                print(f"   ✗ 文件不存在")
                return False

            # 检查文件是否可读
            if not os.access(so_path, os.R_OK):
                print(f"   ✗ 文件不可读")
                return False

            # 检查文件大小（应该至少 100KB）
            file_size = os.path.getsize(so_path)
            if file_size < 100 * 1024:
                print(f"   ✗ 文件过小: {file_size} bytes (期望 >= 100KB)")
                return False

            if file_size > 10 * 1024 * 1024:  # 10MB
                print(f"   ✗ 文件过大: {file_size / 1024 / 1024:.1f} MB (期望 <= 10MB)")
                return False

            # 检查文件扩展名
            if not so_path.endswith('.so'):
                print(f"   ✗ 文件扩展名错误: {os.path.splitext(so_path)[1]} (期望: .so)")
                return False

            # 检查文件是否为 ELF 文件（Linux 共享库）
            with open(so_path, 'rb') as f:
                header = f.read(4)
                if header != b'\x7fELF':
                    print(f"   ✗ 不是有效的 ELF 文件")
                    return False

            # 计算 MD5 哈希（用于追踪）
            md5_hash = self._compute_file_hash(so_path)
            print(f"   ✓ 文件验证通过")
            print(f"   ✓ 文件大小: {file_size / 1024:.1f} KB")
            print(f"   ✓ MD5: {md5_hash[:16]}...")

            return True

        except Exception as e:
            print(f"   ✗ 验证过程出错: {e}")
            return False

    def _validate_loaded_lib(self) -> bool:
        """
        验证已加载的库

        Returns:
            验证是否通过
        """
        try:
            # 检查库句柄
            if self.rust_lib is None:
                print("   ✗ 库句柄为空")
                return False

            # 检查是否为有效的 ctypes.CDLL 对象
            if not isinstance(self.rust_lib, ctypes.CDLL):
                print("   ✗ 不是有效的 CDLL 对象")
                return False

            # 检查库的 _name 属性
            if not hasattr(self.rust_lib, '_name'):
                print("   ✗ 库缺少 _name 属性")
                return False

            # 尝试调用一个简单的 Rust 函数来验证
            test_query = (ctypes.c_float * 2)(1.0, 0.0)
            test_candidate = (ctypes.c_float * 2)(1.0, 0.0)
            result = self.rust_lib.cosine_similarity_c(
                test_query, 2,
                test_candidate, 2
            )

            if abs(result - 1.0) > 0.001:
                print(f"   ✗ Rust 函数测试失败: 预期 1.0, 实际 {result}")
                return False

            print(f"   ✓ 库验证通过: {self.rust_lib._name}")
            print(f"   ✓ Rust 函数测试通过")
            return True

        except Exception as e:
            print(f"   ✗ 验证过程出错: {e}")
            return False

    def _compute_file_hash(self, file_path: str, algorithm: str = 'md5') -> str:
        """
        计算文件哈希

        Args:
            file_path: 文件路径
            algorithm: 哈希算法（md5/sha1/sha256）

        Returns:
            哈希值（十六进制字符串）
        """
        hash_func = hashlib.new(algorithm)

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_func.update(chunk)

        return hash_func.hexdigest()

    def compute_weights(self, query: str, nodes: List) -> WeightResult:
        """
        根据查询计算节点权重

        Args:
            query: 查询字符串
            nodes: 节点列表（可以是节点对象或节点ID列表）

        Returns:
            WeightResult 对象
        """
        # 生成查询向量
        import hashlib
        query_vector = []
        seed = hash(query)

        for i in range(768):
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            value = (seed % 10000) / 10000.0
            query_vector.append(value - 0.5)

        # 归一化
        import numpy as np
        query_vector = np.array(query_vector, dtype=np.float32)
        norm = np.linalg.norm(query_vector)
        if norm > 0:
            query_vector = query_vector / norm

        # 如果没有节点，返回空结果
        if not nodes:
            return WeightResult({}, self)

        # 计算权重（这里使用简化的方法，实际应该查询向量存储）
        weights = {}

        # 假设 nodes 是节点对象列表
        for i, node in enumerate(nodes):
            if isinstance(node, dict):
                node_id = node.get('node_id') or node.get('id', str(i))
            else:
                node_id = str(node)

            # 简化的权重计算（基于节点ID的哈希）
            seed = hash(f"{query}:{node_id}")
            weight = (seed % 10000) / 10000.0
            weights[node_id] = weight

        return WeightResult(weights, self)

    # ============================================================================
    # 相似度计算
    # ============================================================================

    def compute_similarity(
        self,
        query: np.ndarray,
        candidates: List[np.ndarray],
        method: str = "cosine"
    ) -> List[float]:
        """
        计算相似度

        Args:
            query: 查询向量
            candidates: 候选向量列表
            method: 相似度方法（cosine/euclidean）

        Returns:
            [similarity_scores, ...]
        """
        # 优先使用 Rust 实现
        if self.rust_lib is not None and method == "cosine":
            try:
                return self._compute_similarity_rust(query, candidates, method)
            except Exception as e:
                print(f"⚠️ Rust 计算失败，降级到 Python 实现: {e}")

        return self._compute_similarity_python(query, candidates, method)

    def _compute_similarity_rust(
        self,
        query: np.ndarray,
        candidates: List[np.ndarray],
        method: str
    ) -> List[float]:
        """Rust 实现的相似度计算"""
        scores = []

        # 转换 query 为 ctypes 数组
        query_array = (ctypes.c_float * len(query))(*query.astype(np.float32))

        for candidate in candidates:
            # 转换 candidate 为 ctypes 数组
            candidate_array = (ctypes.c_float * len(candidate))(*candidate.astype(np.float32))

            # 调用 Rust 函数
            similarity = self.rust_lib.cosine_similarity_c(
                query_array, len(query),
                candidate_array, len(candidate)
            )

            scores.append(float(similarity))

        return scores

    def _compute_similarity_python(
        self,
        query: np.ndarray,
        candidates: List[np.ndarray],
        method: str
    ) -> List[float]:
        """Python 实现的相似度计算"""
        scores = []

        query_norm = np.linalg.norm(query)

        for candidate in candidates:
            if method == "cosine":
                candidate_norm = np.linalg.norm(candidate)

                if query_norm == 0 or candidate_norm == 0:
                    similarity = 0.0
                else:
                    similarity = np.dot(query, candidate) / (query_norm * candidate_norm)

            elif method == "euclidean":
                similarity = -np.linalg.norm(query - candidate)  # 距离越小，分数越高

            else:
                raise ValueError(f"不支持的相似度方法: {method}")

            scores.append(float(similarity))

        return scores

    # ============================================================================
    # 批量相似度计算
    # ============================================================================

    def compute_batch_similarity(
        self,
        query: np.ndarray,
        candidate_vectors: np.ndarray,
        method: str = "cosine"
    ) -> np.ndarray:
        """
        批量计算相似度（优化版）

        Args:
            query: 查询向量 (dim,)
            candidate_vectors: 候选向量矩阵 (n, dim)
            method: 相似度方法（cosine/euclidean）

        Returns:
            similarity_scores (n,)
        """
        # 优先使用 Rust 实现
        if self.rust_lib is not None and method == "cosine":
            try:
                return self._compute_batch_similarity_rust(query, candidate_vectors, method)
            except Exception as e:
                print(f"⚠️ Rust 批量计算失败，降级到 Python 实现: {e}")

        return self._compute_batch_similarity_python(query, candidate_vectors, method)

    def _compute_batch_similarity_rust(
        self,
        query: np.ndarray,
        candidate_vectors: np.ndarray,
        method: str
    ) -> np.ndarray:
        """Rust 实现的批量相似度计算"""
        n, dim = candidate_vectors.shape

        # 转换 query 为 ctypes 数组
        query_array = (ctypes.c_float * len(query))(*query.astype(np.float32))

        # 扁平化候选向量矩阵
        candidates_flat = candidate_vectors.flatten().astype(np.float32)
        candidates_array = (ctypes.c_float * len(candidates_flat))(*candidates_flat)

        # 预分配结果数组
        results_array = (ctypes.c_float * n)()

        # 调用 Rust 函数
        ret = self.rust_lib.compute_similarity_batch_c(
            query_array, len(query),
            candidates_array, n,
            results_array
        )

        if ret != 0:
            raise RuntimeError("Rust 批量计算失败")

        return np.array(results_array, dtype=np.float32)

    def _compute_batch_similarity_python(
        self,
        query: np.ndarray,
        candidate_vectors: np.ndarray,
        method: str
    ) -> np.ndarray:
        """Python 实现的批量相似度计算（使用 numpy 向量化）"""
        if method == "cosine":
            # 向量化余弦相似度计算
            query_norm = np.linalg.norm(query)
            candidate_norms = np.linalg.norm(candidate_vectors, axis=1)

            # 避免除零
            denominator = query_norm * candidate_norms
            denominator[denominator == 0] = 1

            similarities = np.dot(candidate_vectors, query) / denominator

        elif method == "euclidean":
            # 向量化欧氏距离计算
            similarities = -np.linalg.norm(candidate_vectors - query, axis=1)

        else:
            raise ValueError(f"不支持的相似度方法: {method}")

        return similarities

    # ============================================================================
    # 权重传播
    # ============================================================================

    def propagate_weights(
        self,
        start_node: str,
        graph_data: Dict[str, List[Tuple[str, float]]],
        max_hops: int = 3,
        decay_factor: float = 0.8
    ) -> Dict[str, float]:
        """
        权重传播（依赖图遍历）

        Args:
            start_node: 起始节点
            graph_data: 图数据 {node_id: [(neighbor_id, weight), ...]}
            max_hops: 最大跳数
            decay_factor: 衰减因子

        Returns:
            {node_id: propagated_weight, ...}
        """
        # 优先使用 Rust 实现
        if self.rust_lib is not None:
            try:
                return self._propagate_weights_rust(start_node, graph_data, max_hops, decay_factor)
            except Exception as e:
                print(f"⚠️ Rust 权重传播失败，降级到 Python 实现: {e}")

        return self._propagate_weights_python(start_node, graph_data, max_hops, decay_factor)

    def _propagate_weights_rust(
        self,
        start_node: str,
        graph_data: Dict[str, List[Tuple[str, float]]],
        max_hops: int,
        decay_factor: float
    ) -> Dict[str, float]:
        """Rust 实现的权重传播"""
        # 构建边列表
        edges = []
        for from_node, neighbors in graph_data.items():
            for to_node, weight in neighbors:
                edges.append((from_node, to_node, weight))

        # 创建 EdgeC 数组
        edges_array = (EdgeC * len(edges))()
        for i, (from_node, to_node, weight) in enumerate(edges):
            edges_array[i].from_node = from_node.encode('utf-8')
            edges_array[i].to_node = to_node.encode('utf-8')
            edges_array[i].weight = ctypes.c_float(weight)

        # 预分配结果数组
        max_results = 1000  # 估计最大结果数
        results_array = (NodeWeightC * max_results)()

        # 调用 Rust 函数
        ret = self.rust_lib.propagate_weights_c(
            start_node.encode('utf-8'),
            edges_array,
            len(edges),
            max_hops,
            ctypes.c_float(decay_factor),
            results_array,
            max_results
        )

        if ret < 0:
            raise RuntimeError("Rust 权重传播失败")

        # 提取结果
        weights = {}
        for i in range(ret):
            node_id = results_array[i].node_id.decode('utf-8')
            weight = float(results_array[i].weight)
            weights[node_id] = weight
            # 注意：Rust 分配的字符串内存会有轻微泄漏
            # 对于短期运行，这是可以接受的

        return weights

    def _propagate_weights_python(
        self,
        start_node: str,
        graph_data: Dict[str, List[Tuple[str, float]]],
        max_hops: int,
        decay_factor: float
    ) -> Dict[str, float]:
        """Python 实现的权重传播"""
        from collections import deque

        weights = {start_node: 1.0}
        visited = {start_node: 0}
        queue = deque([(start_node, 1.0, 0)])

        while queue:
            current_id, current_weight, current_hop = queue.popleft()

            if current_hop >= max_hops:
                continue

            neighbors = graph_data.get(current_id, [])

            for neighbor_id, edge_weight in neighbors:
                new_weight = current_weight * edge_weight * decay_factor

                if neighbor_id not in weights:
                    weights[neighbor_id] = new_weight
                    visited[neighbor_id] = current_hop + 1
                    queue.append((neighbor_id, new_weight, current_hop + 1))
                else:
                    weights[neighbor_id] = max(weights[neighbor_id], new_weight)

        return weights

    # ============================================================================
    # 时序衰减
    # ============================================================================

    def apply_temporal_decay(
        self,
        base_weights: Dict[str, float],
        timestamps: Dict[str, int],
        decay_rate: float = 0.1,
        current_time: Optional[int] = None
    ) -> Dict[str, float]:
        """
        应用时序衰减

        Args:
            base_weights: 基础权重
            timestamps: 时间戳 {node_id: timestamp}
            decay_rate: 衰减率
            current_time: 当前时间戳（默认使用最新时间戳）

        Returns:
            {node_id: decayed_weight, ...}
        """
        if current_time is None:
            current_time = max(timestamps.values()) if timestamps else 0

        decayed_weights = {}

        for node_id, weight in base_weights.items():
            if node_id in timestamps:
                time_diff = current_time - timestamps[node_id]
                # 指数衰减
                decay_factor = np.exp(-decay_rate * time_diff)
                decayed_weights[node_id] = weight * decay_factor
            else:
                decayed_weights[node_id] = weight

        return decayed_weights

    # ============================================================================
    # 组合因子
    # ============================================================================

    def combine_factors(
        self,
        factors: List[Dict[str, float]],
        coefficients: Optional[List[float]] = None
    ) -> Dict[str, float]:
        """
        组合多个权重因子

        Args:
            factors: 权重因子列表 [{node_id: weight, ...}, ...]
            coefficients: 系数列表（默认均匀权重）

        Returns:
            {node_id: combined_weight, ...}
        """
        # 优先使用 Rust 实现
        if self.rust_lib is not None:
            try:
                return self._combine_factors_rust(factors, coefficients)
            except Exception as e:
                print(f"⚠️ Rust 组合因子失败，降级到 Python 实现: {e}")

        return self._combine_factors_python(factors, coefficients)

    def _combine_factors_rust(
        self,
        factors: List[Dict[str, float]],
        coefficients: Optional[List[float]] = None
    ) -> Dict[str, float]:
        """Rust 实现的组合因子"""
        if not factors:
            return {}

        if coefficients is None:
            coefficients = [1.0] * len(factors)

        if len(factors) != len(coefficients):
            raise ValueError("因子数量和系数数量不匹配")

        # 扁平化因子
        factors_flat = []
        for idx, factor in enumerate(factors):
            for node_id, weight in factor.items():
                factors_flat.append((node_id, weight, idx))

        # 创建 FactorC 数组
        factors_array = (FactorC * len(factors_flat))()
        for i, (node_id, weight, _) in enumerate(factors_flat):
            factors_array[i].node_id = node_id.encode('utf-8')
            factors_array[i].weight = ctypes.c_float(weight)

        # 创建系数数组
        coeff_array = (ctypes.c_float * len(coefficients))(*coefficients)

        # 预分配结果数组
        max_results = 1000
        results_array = (NodeWeightC * max_results)()

        # 调用 Rust 函数
        ret = self.rust_lib.combine_factors_c(
            factors_array,
            len(factors_flat),
            coeff_array,
            len(coefficients),
            results_array,
            max_results
        )

        if ret < 0:
            raise RuntimeError("Rust 组合因子失败")

        # 提取结果
        weights = {}
        for i in range(ret):
            node_id = results_array[i].node_id.decode('utf-8')
            weight = float(results_array[i].weight)
            weights[node_id] = weight

        return weights

    def _combine_factors_python(
        self,
        factors: List[Dict[str, float]],
        coefficients: Optional[List[float]] = None
    ) -> Dict[str, float]:
        """Python 实现的组合因子"""
        if not factors:
            return {}

        if coefficients is None:
            coefficients = [1.0 / len(factors)] * len(factors)

        if len(factors) != len(coefficients):
            raise ValueError("因子数量和系数数量不匹配")

        combined = {}

        for factor_dict, coeff in zip(factors, coefficients):
            for node_id, weight in factor_dict.items():
                if node_id not in combined:
                    combined[node_id] = 0.0
                combined[node_id] += weight * coeff

        return combined

    # ============================================================================
    # 归一化权重
    # ============================================================================

    def normalize_weights(
        self,
        weights: Dict[str, float],
        method: str = "max"
    ) -> Dict[str, float]:
        """
        归一化权重

        Args:
            weights: 原始权重
            method: 归一化方法（max/sum/min_max/z_score）

        Returns:
            {node_id: normalized_weight, ...}
        """
        # 优先使用 Rust 实现
        if self.rust_lib is not None and method in ["min_max", "z_score", "sum"]:
            try:
                return self._normalize_weights_rust(weights, method)
            except Exception as e:
                print(f"⚠️ Rust 归一化失败，降级到 Python 实现: {e}")

        return self._normalize_weights_python(weights, method)

    def _normalize_weights_rust(
        self,
        weights: Dict[str, float],
        method: str
    ) -> Dict[str, float]:
        """Rust 实现的归一化权重"""
        if not weights:
            return {}

        # 创建权重数组
        weights_array = (NodeWeightC * len(weights))()
        for i, (node_id, weight) in enumerate(weights.items()):
            weights_array[i].node_id = node_id.encode('utf-8')
            weights_array[i].weight = ctypes.c_float(weight)

        # 预分配结果数组
        max_results = len(weights)
        results_array = (NodeWeightC * max_results)()

        # 调用 Rust 函数
        ret = self.rust_lib.normalize_weights_c(
            weights_array,
            len(weights),
            method.encode('utf-8'),
            results_array,
            max_results
        )

        if ret < 0:
            raise RuntimeError("Rust 归一化失败")

        # 提取结果
        normalized = {}
        for i in range(ret):
            node_id = results_array[i].node_id.decode('utf-8')
            weight = float(results_array[i].weight)
            normalized[node_id] = weight

        return normalized

    def _normalize_weights_python(
        self,
        weights: Dict[str, float],
        method: str
    ) -> Dict[str, float]:
        """Python 实现的归一化权重"""
        if not weights:
            return {}

        if method == "max":
            max_weight = max(weights.values())
            if max_weight > 0:
                return {k: v / max_weight for k, v in weights.items()}
            else:
                return weights

        elif method == "sum":
            total = sum(weights.values())
            if total > 0:
                return {k: v / total for k, v in weights.items()}
            else:
                return weights

        elif method == "min_max":
            max_weight = max(weights.values())
            min_weight = min(weights.values())
            range_val = max_weight - min_weight

            if range_val > 0:
                return {k: (v - min_weight) / range_val for k, v in weights.items()}
            else:
                return {k: 0.5 for k in weights.keys()}

        elif method == "z_score":
            mean = sum(weights.values()) / len(weights)
            variance = sum((v - mean) ** 2 for v in weights.values()) / len(weights)
            std = variance ** 0.5

            if std > 0:
                return {k: (v - mean) / std for k, v in weights.items()}
            else:
                return {k: 0.0 for k in weights.keys()}

        else:
            raise ValueError(f"不支持的归一化方法: {method}")

    # ============================================================================
    # Top-K
    # ============================================================================

    def top_k(self, weights: Dict[str, float], k: int = 10) -> List[Tuple[str, float]]:
        """
        获取权重最高的 K 个节点

        Args:
            weights: 权重字典
            k: 返回前K个

        Returns:
            [(node_id, weight), ...] 按权重降序排列
        """
        sorted_items = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        return sorted_items[:k]


# ============================================================================
# 测试代码
# ============================================================================

if __name__ == "__main__":
    # 测试代码
    calc = WeightCalculator()

    # 测试相似度计算
    print("=" * 60)
    print("测试相似度计算...")
    print("=" * 60)
    query = np.random.randn(128).astype(np.float32)
    query = query / np.linalg.norm(query)

    candidates = [np.random.randn(128).astype(np.float32) for _ in range(100)]
    candidates = [c / np.linalg.norm(c) for c in candidates]

    scores = calc.compute_similarity(query, candidates[:5])
    print(f"相似度分数: {scores}")

    # 测试批量相似度
    print("\n" + "=" * 60)
    print("测试批量相似度计算...")
    print("=" * 60)
    candidate_matrix = np.array(candidates)
    batch_scores = calc.compute_batch_similarity(query, candidate_matrix)
    print(f"批量相似度分数（前10个）: {batch_scores[:10]}")

    # 测试权重传播
    print("\n" + "=" * 60)
    print("测试权重传播...")
    print("=" * 60)
    graph_data = {
        "A": [("B", 0.9), ("C", 0.8)],
        "B": [("D", 0.7), ("E", 0.6)],
        "C": [("F", 0.5)],
        "D": [("G", 0.4)],
    }

    propagated = calc.propagate_weights("A", graph_data, max_hops=3)
    print(f"传播权重: {propagated}")

    # 测试组合因子
    print("\n" + "=" * 60)
    print("测试组合因子...")
    print("=" * 60)
    factor1 = {"A": 0.8, "B": 0.6, "C": 0.4}
    factor2 = {"A": 0.5, "B": 0.9, "D": 0.3}
    combined = calc.combine_factors([factor1, factor2])
    print(f"组合权重: {combined}")

    # 测试归一化
    print("\n" + "=" * 60)
    print("测试归一化...")
    print("=" * 60)
    normalized = calc.normalize_weights(combined, method="sum")
    print(f"归一化权重: {normalized}")

    # 测试 Top-K
    print("\n" + "=" * 60)
    print("测试 Top-K...")
    print("=" * 60)
    top_k = calc.top_k(combined, k=2)
    print(f"Top-2: {top_k}")

    print("\n" + "=" * 60)
    print("✅ 所有测试完成！")
    print("=" * 60)
