"""
简化版图存储

使用邻接表实现的图存储，支持：
- 节点和边的增删改查
- BFS/DFS 遍历
- 依赖关系传播
- 权重计算
"""

from typing import Dict, List, Set, Optional, Tuple
from collections import deque, defaultdict
import json


class GraphStore:
    """简化版图存储（邻接表实现）"""

    def __init__(self):
        """初始化图存储"""
        # 节点数据: node_id -> {data dict}
        self.nodes: Dict[str, Dict] = {}

        # 邻接表: node_id -> [(to_node, edge_type, weight), ...]
        self.adjacency: Dict[str, List[Tuple[str, str, float]]] = defaultdict(list)

        # 反向邻接表（用于反向遍历）
        self.reverse_adjacency: Dict[str, List[Tuple[str, str, float]]] = defaultdict(list)

    def add_node(self, node_id: str, data: Optional[Dict] = None):
        """
        添加节点

        Args:
            node_id: 节点ID
            data: 节点数据（可选）
        """
        if node_id not in self.nodes:
            self.nodes[node_id] = data or {}

    def add_edge(
        self,
        from_id: str,
        to_id: str,
        edge_type: str = "related",
        weight: float = 1.0,
        bidirectional: bool = False
    ):
        """
        添加边

        Args:
            from_id: 起始节点
            to_id: 目标节点
            edge_type: 边类型（如 imports, depends_on, implements）
            weight: 边权重
            bidirectional: 是否双向边
        """
        # 确保节点存在
        self.add_node(from_id)
        self.add_node(to_id)

        # 添加正向边
        self.adjacency[from_id].append((to_id, edge_type, weight))

        # 添加反向边（用于反向遍历）
        self.reverse_adjacency[to_id].append((from_id, edge_type, weight))

        # 如果是双向边，添加反向连接
        if bidirectional:
            self.adjacency[to_id].append((from_id, edge_type, weight))
            self.reverse_adjacency[from_id].append((to_id, edge_type, weight))

    def get_node(self, node_id: str) -> Optional[Dict]:
        """获取节点数据"""
        return self.nodes.get(node_id)

    def get_neighbors(
        self,
        node_id: str,
        edge_type: Optional[str] = None
    ) -> List[Tuple[str, float]]:
        """
        获取邻居节点

        Args:
            node_id: 节点ID
            edge_type: 边类型过滤（可选）

        Returns:
            [(neighbor_id, weight), ...]
        """
        if node_id not in self.adjacency:
            return []

        neighbors = self.adjacency[node_id]

        if edge_type:
            neighbors = [(n, e, w) for n, e, w in neighbors if e == edge_type]

        return [(n, w) for n, e, w in neighbors]

    def get_reverse_neighbors(
        self,
        node_id: str,
        edge_type: Optional[str] = None
    ) -> List[Tuple[str, float]]:
        """
        获取反向邻居节点（即哪些节点指向当前节点）

        Args:
            node_id: 节点ID
            edge_type: 边类型过滤（可选）

        Returns:
            [(neighbor_id, weight), ...]
        """
        if node_id not in self.reverse_adjacency:
            return []

        neighbors = self.reverse_adjacency[node_id]

        if edge_type:
            neighbors = [(n, e, w) for n, e, w in neighbors if e == edge_type]

        return [(n, w) for n, e, w in neighbors]

    def bfs(
        self,
        start_id: str,
        max_hops: int = 3,
        edge_type: Optional[str] = None
    ) -> Dict[str, int]:
        """
        BFS 遍历

        Args:
            start_id: 起始节点
            max_hops: 最大跳数
            edge_type: 边类型过滤（可选）

        Returns:
            {node_id: distance, ...}
        """
        if start_id not in self.nodes:
            return {}

        visited = {start_id: 0}
        queue = deque([start_id])

        while queue and len(visited) < 10000:  # 限制遍历规模
            current = queue.popleft()
            current_distance = visited[current]

            if current_distance >= max_hops:
                continue

            neighbors = self.get_neighbors(current, edge_type)
            for neighbor_id, _ in neighbors:
                if neighbor_id not in visited:
                    visited[neighbor_id] = current_distance + 1
                    queue.append(neighbor_id)

        return visited

    def dfs(
        self,
        start_id: str,
        max_depth: int = 3,
        edge_type: Optional[str] = None
    ) -> List[str]:
        """
        DFS 遍历

        Args:
            start_id: 起始节点
            max_depth: 最大深度
            edge_type: 边类型过滤（可选）

        Returns:
            [node_id, ...] 访问顺序
        """
        if start_id not in self.nodes:
            return []

        visited = set()
        result = []

        def _dfs(node_id: str, depth: int):
            if depth > max_depth or node_id in visited:
                return

            visited.add(node_id)
            result.append(node_id)

            neighbors = self.get_neighbors(node_id, edge_type)
            for neighbor_id, _ in neighbors:
                _dfs(neighbor_id, depth + 1)

        _dfs(start_id, 0)
        return result

    def propagate_weights(
        self,
        start_id: str,
        max_hops: int = 3,
        decay_factor: float = 0.8,
        edge_type: Optional[str] = None
    ) -> Dict[str, float]:
        """
        权重传播（2-3跳依赖传播）

        Args:
            start_id: 起始节点
            max_hops: 最大跳数
            decay_factor: 衰减因子（每跳衰减）
            edge_type: 边类型过滤（可选）

        Returns:
            {node_id: propagated_weight, ...}
        """
        if start_id not in self.nodes:
            return {}

        weights = {start_id: 1.0}
        visited = {start_id: 0}
        queue = deque([(start_id, 1.0, 0)])  # (node_id, weight, hop)

        while queue:
            current_id, current_weight, current_hop = queue.popleft()

            if current_hop >= max_hops:
                continue

            neighbors = self.get_neighbors(current_id, edge_type)

            for neighbor_id, edge_weight in neighbors:
                # 计算传播后的权重
                new_weight = current_weight * edge_weight * decay_factor

                if neighbor_id not in weights:
                    weights[neighbor_id] = new_weight
                    visited[neighbor_id] = current_hop + 1
                    queue.append((neighbor_id, new_weight, current_hop + 1))
                else:
                    # 如果已经访问过，累加权重
                    weights[neighbor_id] = max(weights[neighbor_id], new_weight)

        return weights

    def get_weakly_connected_components(self) -> List[Set[str]]:
        """
        获取弱连通分量

        Returns:
            [{node_ids}, ...]
        """
        visited = set()
        components = []

        for node_id in self.nodes:
            if node_id not in visited:
                # 从当前节点开始 BFS
                component = set()
                queue = deque([node_id])

                while queue:
                    current = queue.popleft()
                    if current in visited:
                        continue

                    visited.add(current)
                    component.add(current)

                    # 添加正向和反向邻居
                    neighbors = self.get_neighbors(current)
                    reverse_neighbors = self.get_reverse_neighbors(current)

                    for neighbor_id, _ in neighbors + reverse_neighbors:
                        if neighbor_id not in visited:
                            queue.append(neighbor_id)

                components.append(component)

        return components

    def save(self, filepath: str):
        """保存图到 JSON 文件"""
        data = {
            'nodes': self.nodes,
            'adjacency': {k: list(v) for k, v in self.adjacency.items()},
            'reverse_adjacency': {k: list(v) for k, v in self.reverse_adjacency.items()}
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, filepath: str):
        """从 JSON 文件加载图"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.nodes = data['nodes']
        self.adjacency = defaultdict(list, {k: list(v) for k, v in data['adjacency'].items()})
        self.reverse_adjacency = defaultdict(list, {
            k: list(v) for k, v in data['reverse_adjacency'].items()
        })

    def size(self) -> Tuple[int, int]:
        """
        返回图的大小

        Returns:
            (节点数, 边数)
        """
        num_edges = sum(len(edges) for edges in self.adjacency.values())
        return len(self.nodes), num_edges

    def clear(self):
        """清空图"""
        self.nodes.clear()
        self.adjacency.clear()
        self.reverse_adjacency.clear()


if __name__ == "__main__":
    # 测试代码
    graph = GraphStore()

    # 添加测试节点和边
    graph.add_node("module_a", {"type": "module", "name": "A"})
    graph.add_node("module_b", {"type": "module", "name": "B"})
    graph.add_node("module_c", {"type": "module", "name": "C"})
    graph.add_node("module_d", {"type": "module", "name": "D"})

    graph.add_edge("module_a", "module_b", "imports", 0.9)
    graph.add_edge("module_b", "module_c", "imports", 0.8)
    graph.add_edge("module_c", "module_d", "imports", 0.7)
    graph.add_edge("module_a", "module_c", "depends_on", 0.5)

    print(f"图大小: {graph.size()}")

    # BFS 测试
    bfs_result = graph.bfs("module_a", max_hops=2)
    print("BFS 结果:", bfs_result)

    # 权重传播测试
    weights = graph.propagate_weights("module_a", max_hops=3)
    print("权重传播结果:", weights)

    # 连通分量测试
    components = graph.get_weakly_connected_components()
    print(f"连通分量数量: {len(components)}")
