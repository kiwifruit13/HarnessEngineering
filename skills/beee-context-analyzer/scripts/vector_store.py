"""
简化版向量索引存储

使用 numpy 实现的内存向量索引，支持：
- 向量存储和检索
- 余弦相似度计算
- 欧氏距离计算
- 最近邻搜索（线性扫描）
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
import pickle
import os


class VectorStore:
    """简化版向量存储（Python + numpy）"""

    def __init__(self, dimension: int = 768):
        """
        初始化向量存储

        Args:
            dimension: 向量维度（默认768，兼容大多数嵌入模型）
        """
        self.dimension = dimension
        self.vectors = {}  # node_id -> numpy array
        self.metadata = {}  # node_id -> metadata dict

    def add_vector(self, node_id: str, vector: np.ndarray, metadata: Optional[Dict] = None):
        """
        添加向量

        Args:
            node_id: 节点ID
            vector: 向量（numpy array）
            metadata: 元数据（可选）
        """
        if vector.shape[0] != self.dimension:
            raise ValueError(f"向量维度不匹配: 期望 {self.dimension}, 实际 {vector.shape[0]}")

        self.vectors[node_id] = vector.astype(np.float32)
        if metadata:
            self.metadata[node_id] = metadata

    def get_vector(self, node_id: str) -> Optional[np.ndarray]:
        """获取向量"""
        return self.vectors.get(node_id)

    def cosine_similarity(self, query: np.ndarray, candidate: np.ndarray) -> float:
        """
        计算余弦相似度

        Args:
            query: 查询向量
            candidate: 候选向量

        Returns:
            相似度分数（0-1）
        """
        query_norm = np.linalg.norm(query)
        candidate_norm = np.linalg.norm(candidate)

        if query_norm == 0 or candidate_norm == 0:
            return 0.0

        similarity = np.dot(query, candidate) / (query_norm * candidate_norm)
        return float(similarity)

    def euclidean_distance(self, query: np.ndarray, candidate: np.ndarray) -> float:
        """计算欧氏距离"""
        return float(np.linalg.norm(query - candidate))

    def search(
        self,
        query: np.ndarray,
        top_k: int = 10,
        metric: str = "cosine"
    ) -> List[Tuple[str, float]]:
        """
        搜索最相似的向量（线性扫描）

        Args:
            query: 查询向量
            top_k: 返回前K个结果
            metric: 相似度度量方式（cosine/euclidean）

        Returns:
            [(node_id, score), ...] 按相似度降序排列
        """
        if query.shape[0] != self.dimension:
            raise ValueError(f"查询向量维度不匹配: 期望 {self.dimension}, 实际 {query.shape[0]}")

        results = []

        for node_id, vector in self.vectors.items():
            if metric == "cosine":
                score = self.cosine_similarity(query, vector)
            elif metric == "euclidean":
                score = -self.euclidean_distance(query, vector)  # 距离越小，分数越高
            else:
                raise ValueError(f"不支持的度量方式: {metric}")

            results.append((node_id, score))

        # 按分数降序排序
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:top_k]

    def batch_similarity(
        self,
        query: np.ndarray,
        candidate_ids: List[str]
    ) -> Dict[str, float]:
        """
        批量计算相似度（优化版）

        Args:
            query: 查询向量
            candidate_ids: 候选节点ID列表

        Returns:
            {node_id: similarity, ...}
        """
        query_norm = np.linalg.norm(query)

        results = {}
        for node_id in candidate_ids:
            if node_id not in self.vectors:
                continue

            vector = self.vectors[node_id]
            vector_norm = np.linalg.norm(vector)

            if query_norm == 0 or vector_norm == 0:
                results[node_id] = 0.0
            else:
                similarity = np.dot(query, vector) / (query_norm * vector_norm)
                results[node_id] = float(similarity)

        return results

    def save(self, filepath: str):
        """
        保存向量存储到文件

        Args:
            filepath: 保存路径
        """
        data = {
            'dimension': self.dimension,
            'vectors': {k: v.tolist() for k, v in self.vectors.items()},
            'metadata': self.metadata
        }
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)

    def load(self, filepath: str):
        """
        从文件加载向量存储

        Args:
            filepath: 文件路径
        """
        with open(filepath, 'rb') as f:
            data = pickle.load(f)

        self.dimension = data['dimension']
        self.vectors = {k: np.array(v, dtype=np.float32) for k, v in data['vectors'].items()}
        self.metadata = data.get('metadata', {})

    def size(self) -> int:
        """返回向量数量"""
        return len(self.vectors)

    def clear(self):
        """清空存储"""
        self.vectors.clear()
        self.metadata.clear()


if __name__ == "__main__":
    # 测试代码
    store = VectorStore(dimension=128)

    # 添加测试向量
    for i in range(100):
        vec = np.random.randn(128).astype(np.float32)
        vec = vec / np.linalg.norm(vec)  # 归一化
        store.add_vector(f"node_{i}", vec, {"type": "test", "index": i})

    print(f"向量数量: {store.size()}")

    # 搜索测试
    query = np.random.randn(128).astype(np.float32)
    query = query / np.linalg.norm(query)

    results = store.search(query, top_k=5)
    print("搜索结果:", results)

    # 批量相似度测试
    candidate_ids = [f"node_{i}" for i in range(10)]
    similarities = store.batch_similarity(query, candidate_ids)
    print("批量相似度:", similarities)
