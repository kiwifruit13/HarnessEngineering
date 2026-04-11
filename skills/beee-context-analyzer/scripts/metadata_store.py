"""
元数据存储（基于 SQLite）

使用 Python 内置的 sqlite3 实现的元数据存储，支持：
- 节点元数据的 CRUD 操作
- 索引查询
- 事务支持
- 持久化存储
"""

import sqlite3
import json
from typing import Dict, List, Optional, Any
from contextlib import contextmanager


class MetadataStore:
    """元数据存储（SQLite）"""

    def __init__(self, db_path: Optional[str] = None):
        """
        初始化元数据存储

        Args:
            db_path: 数据库路径，默认为临时文件（如果未指定则创建临时文件）
        """
        if db_path is None:
            import tempfile
            import os
            fd, db_path = tempfile.mkstemp(suffix='.db', prefix='beee_metadata_')
            os.close(fd)
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        """获取数据库连接（上下文管理器）"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 支持字典式访问
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self):
        """初始化数据库表结构"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 节点元数据表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS nodes (
                    node_id TEXT PRIMARY KEY,
                    type TEXT,
                    language TEXT,
                    file_path TEXT,
                    line_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata_json TEXT,
                    tags TEXT
                )
            """)

            # 边元数据表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS edges (
                    from_id TEXT,
                    to_id TEXT,
                    edge_type TEXT,
                    weight REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata_json TEXT,
                    PRIMARY KEY (from_id, to_id, edge_type)
                )
            """)

            # 项目信息表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS project_info (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_nodes_type
                ON nodes(type)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_nodes_language
                ON nodes(language)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_edges_from
                ON edges(from_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_edges_to
                ON edges(to_id)
            """)

    def add_node(
        self,
        node_id: str,
        node_type: str,
        language: Optional[str] = None,
        file_path: Optional[str] = None,
        line_count: Optional[int] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None
    ):
        """
        添加节点

        Args:
            node_id: 节点ID
            node_type: 节点类型（如 file, function, class, module）
            language: 编程语言
            file_path: 文件路径
            line_count: 代码行数
            metadata: 额外元数据（JSON）
            tags: 标签列表
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO nodes
                (node_id, type, language, file_path, line_count, metadata_json, tags, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                node_id,
                node_type,
                language,
                file_path,
                line_count,
                json.dumps(metadata) if metadata else None,
                ",".join(tags) if tags else None
            ))

    def get_node(self, node_id: str) -> Optional[Dict]:
        """获取节点"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM nodes WHERE node_id = ?
            """, (node_id,))

            row = cursor.fetchone()
            if row:
                return self._row_to_dict(row)
            return None

    def update_node(self, node_id: str, **kwargs):
        """
        更新节点

        Args:
            node_id: 节点ID
            **kwargs: 要更新的字段
        """
        if not kwargs:
            return

        # 构建更新语句
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])

        # 处理特殊字段
        values = []
        for key, value in kwargs.items():
            if key == "metadata":
                values.append(json.dumps(value) if value else None)
            elif key == "tags":
                values.append(",".join(value) if value else None)
            else:
                values.append(value)

        values.append(node_id)

        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(f"""
                UPDATE nodes
                SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                WHERE node_id = ?
            """, values)

    def delete_node(self, node_id: str):
        """删除节点"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("DELETE FROM nodes WHERE node_id = ?", (node_id,))
            cursor.execute("DELETE FROM edges WHERE from_id = ? OR to_id = ?", (node_id, node_id))

    def add_edge(
        self,
        from_id: str,
        to_id: str,
        edge_type: str,
        weight: float = 1.0,
        metadata: Optional[Dict] = None
    ):
        """
        添加边

        Args:
            from_id: 起始节点
            to_id: 目标节点
            edge_type: 边类型（如 imports, calls, inherits）
            weight: 边权重
            metadata: 额外元数据
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO edges
                (from_id, to_id, edge_type, weight, metadata_json)
                VALUES (?, ?, ?, ?, ?)
            """, (
                from_id,
                to_id,
                edge_type,
                weight,
                json.dumps(metadata) if metadata else None
            ))

    def get_edges(
        self,
        from_id: Optional[str] = None,
        to_id: Optional[str] = None,
        edge_type: Optional[str] = None
    ) -> List[Dict]:
        """
        查询边

        Args:
            from_id: 起始节点过滤（可选）
            to_id: 目标节点过滤（可选）
            edge_type: 边类型过滤（可选）

        Returns:
            [edge_dict, ...]
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM edges WHERE 1=1"
            params = []

            if from_id:
                query += " AND from_id = ?"
                params.append(from_id)

            if to_id:
                query += " AND to_id = ?"
                params.append(to_id)

            if edge_type:
                query += " AND edge_type = ?"
                params.append(edge_type)

            cursor.execute(query, params)

            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def query_nodes(
        self,
        node_type: Optional[str] = None,
        language: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        查询节点

        Args:
            node_type: 节点类型过滤（可选）
            language: 语言过滤（可选）
            tags: 标签过滤（可选，匹配任意一个标签）
            limit: 返回结果数量限制（可选）

        Returns:
            [node_dict, ...]
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM nodes WHERE 1=1"
            params = []

            if node_type:
                query += " AND type = ?"
                params.append(node_type)

            if language:
                query += " AND language = ?"
                params.append(language)

            if tags:
                # 使用 OR 条件匹配任意一个标签
                tag_conditions = " OR ".join(["tags LIKE ?" for _ in tags])
                query += f" AND ({tag_conditions})"
                params.extend([f"%{tag}%" for tag in tags])

            query += " ORDER BY updated_at DESC"

            if limit:
                query += " LIMIT ?"
                params.append(limit)

            cursor.execute(query, params)

            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def set_project_info(self, key: str, value: Any):
        """
        设置项目信息

        Args:
            key: 键
            value: 值（会自动转换为 JSON）
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO project_info (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, json.dumps(value)))

    def get_project_info(self, key: str) -> Optional[Any]:
        """
        获取项目信息

        Args:
            key: 键

        Returns:
            值（自动从 JSON 解析）
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT value FROM project_info WHERE key = ?
            """, (key,))

            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return None

    def get_all_project_info(self) -> Dict[str, Any]:
        """获取所有项目信息"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT key, value FROM project_info")

            return {row[0]: json.loads(row[1]) for row in cursor.fetchall()}

    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        """将数据库行转换为字典"""
        d = dict(row)

        # 解析 JSON 字段
        if d.get("metadata_json"):
            d["metadata"] = json.loads(d["metadata_json"])
        else:
            d["metadata"] = {}

        if d.get("tags"):
            d["tags"] = d["tags"].split(",")
        else:
            d["tags"] = []

        # 移除 JSON 原始字段
        d.pop("metadata_json", None)

        return d

    def get_stats(self) -> Dict[str, int]:
        """
        获取统计信息

        Returns:
            {
                "node_count": 节点数量,
                "edge_count": 边数量,
                "node_types": {type: count, ...}
            }
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 节点数量
            cursor.execute("SELECT COUNT(*) FROM nodes")
            node_count = cursor.fetchone()[0]

            # 边数量
            cursor.execute("SELECT COUNT(*) FROM edges")
            edge_count = cursor.fetchone()[0]

            # 节点类型统计
            cursor.execute("""
                SELECT type, COUNT(*) as count
                FROM nodes
                GROUP BY type
            """)
            node_types = {row[0]: row[1] for row in cursor.fetchall()}

            return {
                "node_count": node_count,
                "edge_count": edge_count,
                "node_types": node_types
            }

    def export_to_file(self, filepath: str):
        """导出数据库到文件"""
        with self._get_connection() as conn:
            # 使用 SQLite 的备份 API
            backup = sqlite3.connect(filepath)
            conn.backup(backup)
            backup.close()

    def clear(self):
        """清空所有数据"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("DELETE FROM nodes")
            cursor.execute("DELETE FROM edges")
            cursor.execute("DELETE FROM project_info")


if __name__ == "__main__":
    # 测试代码
    store = MetadataStore()

    # 添加测试节点
    store.add_node(
        node_id="file1.py",
        node_type="file",
        language="python",
        file_path="src/file1.py",
        line_count=100,
        metadata={"author": "user"},
        tags=["core", "utils"]
    )

    store.add_node(
        node_id="function1",
        node_type="function",
        language="python",
        file_path="src/file1.py",
        metadata={"name": "process_data"}
    )

    # 添加测试边
    store.add_edge("file1.py", "function1", "contains", 1.0)

    # 查询测试
    node = store.get_node("file1.py")
    print("节点:", node)

    edges = store.get_edges(from_id="file1.py")
    print("边:", edges)

    # 统计信息
    stats = store.get_stats()
    print("统计:", stats)
