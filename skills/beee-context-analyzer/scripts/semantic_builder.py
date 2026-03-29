"""
语义网构建模块

负责从代码库构建语义网，包括：
- 项目结构分析
- 代码解析
- 依赖关系提取
- 语义嵌入生成（简化版）
- 向量索引构建
- 知识图谱构建
"""

import os
import re
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path
import hashlib

from vector_store import VectorStore
from graph_store import GraphStore
from metadata_store import MetadataStore


class SemanticBuilder:
    """语义网构建器"""

    def __init__(self, project_root: str = "."):
        """
        初始化语义网构建器

        Args:
            project_root: 项目根目录
        """
        self.project_root = Path(project_root).resolve()
        self.vector_store = VectorStore()
        self.graph_store = GraphStore()
        self.metadata_store = MetadataStore()

        # 文件类型映射
        self.file_types = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
        }

        # 忽略的目录
        self.ignore_dirs = {
            '.git', '.svn', '.hg',
            '__pycache__', 'node_modules', 'venv', 'env',
            '.venv', '.env', 'dist', 'build',
            '.idea', '.vscode',
        }

        # 忽略的文件
        self.ignore_files = {
            '.DS_Store', 'Thumbs.db',
        }

    def analyze_project(self) -> Dict:
        """
        分析项目结构

        Returns:
            {
                "languages": {language: count, ...},
                "file_count": int,
                "directory_count": int,
                "config_files": [paths, ...],
                "frameworks": [framework_names, ...]
            }
        """
        languages = {}
        file_count = 0
        directory_count = 0
        config_files = []

        # 遍历项目目录
        for root, dirs, files in os.walk(self.project_root):
            # 过滤忽略的目录
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]

            directory_count += 1

            for file in files:
                if file in self.ignore_files:
                    continue

                file_path = Path(root) / file
                file_ext = file_path.suffix.lower()

                # 统计语言
                if file_ext in self.file_types:
                    lang = self.file_types[file_ext]
                    languages[lang] = languages.get(lang, 0) + 1
                    file_count += 1

                # 识别配置文件
                if self._is_config_file(file_path):
                    config_files.append(str(file_path.relative_to(self.project_root)))

        # 识别框架
        frameworks = self._detect_frameworks()

        return {
            "languages": languages,
            "file_count": file_count,
            "directory_count": directory_count,
            "config_files": config_files,
            "frameworks": frameworks
        }

    def build_semantic_web(self) -> Dict:
        """
        构建语义网

        Returns:
            构建统计信息
        """
        stats = {
            "files_processed": 0,
            "nodes_created": 0,
            "edges_created": 0,
            "vectors_created": 0
        }

        # 遍历所有代码文件
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]

            for file in files:
                if file in self.ignore_files:
                    continue

                file_path = Path(root) / file
                file_ext = file_path.suffix.lower()

                if file_ext not in self.file_types:
                    continue

                # 处理代码文件
                self._process_code_file(file_path, stats)

        return stats

    def _process_code_file(self, file_path: Path, stats: Dict):
        """
        处理单个代码文件

        Args:
            file_path: 文件路径
            stats: 统计信息
        """
        relative_path = str(file_path.relative_to(self.project_root))
        node_id = self._generate_node_id(relative_path)

        # 读取文件内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"无法读取文件 {file_path}: {e}")
            return

        line_count = len(content.splitlines())

        # 识别语言
        language = self.file_types[file_path.suffix.lower()]

        # 添加文件节点到元数据存储
        self.metadata_store.add_node(
            node_id=node_id,
            node_type="file",
            language=language,
            file_path=relative_path,
            line_count=line_count,
            metadata={
                "size": file_path.stat().st_size,
                "content_hash": hashlib.md5(content.encode()).hexdigest()
            }
        )

        # 提取函数和类
        functions, classes = self._extract_code_elements(content, language)

        # 添加函数节点
        for func_name in functions:
            func_node_id = f"{node_id}::function::{func_name}"
            self.metadata_store.add_node(
                node_id=func_node_id,
                node_type="function",
                language=language,
                file_path=relative_path,
                metadata={"name": func_name}
            )

            # 添加文件到函数的边
            self.graph_store.add_edge(node_id, func_node_id, "contains", 1.0)
            self.metadata_store.add_edge(node_id, func_node_id, "contains", 1.0)
            stats["edges_created"] += 1

        # 添加类节点
        for class_name in classes:
            class_node_id = f"{node_id}::class::{class_name}"
            self.metadata_store.add_node(
                node_id=class_node_id,
                node_type="class",
                language=language,
                file_path=relative_path,
                metadata={"name": class_name}
            )

            # 添加文件到类的边
            self.graph_store.add_edge(node_id, class_node_id, "contains", 1.0)
            self.metadata_store.add_edge(node_id, class_node_id, "contains", 1.0)
            stats["edges_created"] += 1

        # 提取 import 依赖
        imports = self._extract_imports(content, language)
        for imported_module in imports:
            import_node_id = f"module::{imported_module}"

            # 添加模块节点（如果不存在）
            if not self.metadata_store.get_node(import_node_id):
                self.metadata_store.add_node(
                    node_id=import_node_id,
                    node_type="module",
                    language=language,
                    metadata={"name": imported_module}
                )

            # 添加导入边
            self.graph_store.add_edge(node_id, import_node_id, "imports", 0.8)
            self.metadata_store.add_edge(node_id, import_node_id, "imports", 0.8)
            stats["edges_created"] += 1

        # 生成简化版的语义向量（基于文件名和路径）
        vector = self._generate_simple_vector(relative_path, functions, classes, language)
        self.vector_store.add_vector(node_id, vector, {"path": relative_path})
        stats["vectors_created"] += 1

        stats["files_processed"] += 1
        stats["nodes_created"] += 1 + len(functions) + len(classes)

    def _extract_code_elements(self, content: str, language: str) -> Tuple[List[str], List[str]]:
        """
        提取代码元素（函数和类）

        Args:
            content: 代码内容
            language: 编程语言

        Returns:
            (functions, classes)
        """
        functions = []
        classes = []

        if language == "python":
            # 提取函数定义
            functions = re.findall(r'^def\s+(\w+)\s*\(', content, re.MULTILINE)
            # 提取类定义
            classes = re.findall(r'^class\s+(\w+)\s*[:\(]', content, re.MULTILINE)

        elif language in ["javascript", "typescript"]:
            # 提取函数定义
            functions = re.findall(r'function\s+(\w+)\s*\(', content)
            functions.extend(re.findall(r'(\w+)\s*=\s*function\s*\(', content))
            functions.extend(re.findall(r'(\w+)\s*:\s*function\s*\(', content))
            functions.extend(re.findall(r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>', content))
            # 提取类定义
            classes = re.findall(r'class\s+(\w+)\s*{', content)

        elif language == "java":
            # 提取类定义
            classes = re.findall(r'(?:public|private|protected)?\s*(?:abstract\s+)?class\s+(\w+)', content)
            # 提取方法定义
            functions = re.findall(r'(?:public|private|protected)?\s*(?:static\s+)?[\w<>]+\s+(\w+)\s*\(', content)

        elif language == "go":
            # 提取函数定义
            functions = re.findall(r'func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\(', content)
            # 提取类型定义
            classes = re.findall(r'type\s+(\w+)\s+struct', content)

        elif language == "rust":
            # 提取函数定义
            functions = re.findall(r'fn\s+(\w+)\s*\(', content)
            # 提取结构体定义
            classes = re.findall(r'struct\s+(\w+)', content)

        # 去重
        functions = list(set(functions))
        classes = list(set(classes))

        return functions, classes

    def _extract_imports(self, content: str, language: str) -> List[str]:
        """
        提取导入语句

        Args:
            content: 代码内容
            language: 编程语言

        Returns:
            [imported_modules, ...]
        """
        imports = []

        if language == "python":
            # 提取 import 和 from ... import
            imports.extend(re.findall(r'^import\s+(\S+)', content, re.MULTILINE))
            imports.extend(re.findall(r'^from\s+(\S+)\s+import', content, re.MULTILINE))

        elif language in ["javascript", "typescript"]:
            # 提取 require 和 import
            imports.extend(re.findall(r'require\([\'"]([^\'"]+)[\'"]\)', content))
            imports.extend(re.findall(r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]', content))
            imports.extend(re.findall(r'import\s+[\'"]([^\'"]+)[\'"]', content))

        elif language == "java":
            # 提取 import 语句
            imports.extend(re.findall(r'^import\s+([\w.]+);', content, re.MULTILINE))

        elif language == "go":
            # 提取 import 语句
            import_blocks = re.findall(r'import\s*\((.*?)\)', content, re.DOTALL)
            for block in import_blocks:
                imports.extend(re.findall(r'"([^"]+)"', block))
            # 单行 import
            imports.extend(re.findall(r'import\s+"([^"]+)"', content))

        # 清理导入列表
        cleaned_imports = []
        for imp in imports:
            # 提取顶层模块名
            parts = imp.split('.')
            if parts:
                cleaned_imports.append(parts[0])
            else:
                cleaned_imports.append(imp)

        return list(set(cleaned_imports))

    def _generate_simple_vector(
        self,
        file_path: str,
        functions: List[str],
        classes: List[str],
        language: str
    ) -> List[float]:
        """
        生成简化版的语义向量

        注意：这是简化实现，实际应该使用嵌入模型（如 CodeBERT）
        这里使用基于文件名和内容的特征生成伪向量

        Args:
            file_path: 文件路径
            functions: 函数列表
            classes: 类列表
            language: 编程语言

        Returns:
            向量（768维）
        """
        # 使用文件路径、函数名、类名生成特征
        text = f"{file_path} {language} {' '.join(functions)} {' '.join(classes)}"

        # 简化的哈希特征生成（实际应该使用嵌入模型）
        # 这里使用伪随机向量作为示例
        vector = []
        seed = hash(text)

        for i in range(768):
            # 伪随机数生成
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            value = (seed % 10000) / 10000.0  # 归一化到 [0, 1]
            vector.append(value - 0.5)  # 转换到 [-0.5, 0.5]

        # 归一化向量
        import numpy as np
        vector = np.array(vector, dtype=np.float32)
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector.tolist()

    def _is_config_file(self, file_path: Path) -> bool:
        """判断是否为配置文件"""
        config_extensions = {
            '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg',
            '.xml', '.properties', '.env'
        }

        config_names = {
            'package.json', 'requirements.txt', 'pyproject.toml',
            'setup.py', 'setup.cfg', 'Makefile', 'CMakeLists.txt',
            'dockerfile', 'docker-compose.yml', '.dockerignore',
            '.gitignore', '.gitattributes',
            'tsconfig.json', 'webpack.config.js', 'vite.config.js'
        }

        return (
            file_path.suffix.lower() in config_extensions or
            file_path.name.lower() in config_names
        )

    def _detect_frameworks(self) -> List[str]:
        """检测使用的框架"""
        frameworks = []

        # 检查 package.json
        package_json = self.project_root / "package.json"
        if package_json.exists():
            try:
                import json
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}

                    if 'react' in deps:
                        frameworks.append('React')
                    if 'vue' in deps:
                        frameworks.append('Vue')
                    if 'angular' in deps:
                        frameworks.append('Angular')
                    if 'next' in deps:
                        frameworks.append('Next.js')
                    if 'express' in deps:
                        frameworks.append('Express')
                    if 'electron' in deps:
                        frameworks.append('Electron')
            except:
                pass

        # 检查 requirements.txt
        requirements_txt = self.project_root / "requirements.txt"
        if requirements_txt.exists():
            try:
                with open(requirements_txt, 'r') as f:
                    content = f.read().lower()

                    if 'django' in content:
                        frameworks.append('Django')
                    if 'flask' in content:
                        frameworks.append('Flask')
                    if 'fastapi' in content:
                        frameworks.append('FastAPI')
                    if 'pytest' in content:
                        frameworks.append('pytest')
            except:
                pass

        # 检查 pom.xml (Maven Java)
        if (self.project_root / "pom.xml").exists():
            frameworks.append('Maven')

        # 检查 build.gradle (Gradle)
        if (self.project_root / "build.gradle").exists():
            frameworks.append('Gradle')

        return frameworks

    def _generate_node_id(self, path: str) -> str:
        """生成节点ID"""
        # 使用路径的哈希作为ID
        return f"file::{hashlib.md5(path.encode()).hexdigest()}"

    def get_tech_stack(self) -> Dict:
        """获取技术栈"""
        analysis = self.analyze_project()

        return {
            "languages": list(analysis["languages"].keys()),
            "frameworks": analysis["frameworks"],
            "primary_language": max(analysis["languages"].items(), key=lambda x: x[1])[0] if analysis["languages"] else None
        }

    def get_all_nodes(self) -> List[Dict]:
        """获取所有节点"""
        return self.metadata_store.query_nodes()

    def search_similar_files(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        搜索相似的文件

        Args:
            query: 查询文本
            top_k: 返回前K个结果

        Returns:
            [(node_id, similarity), ...]
        """
        # 生成查询向量
        import numpy as np

        # 简化实现：使用查询文本生成伪向量
        query_vector = self._generate_simple_vector(query, [], [], "query")
        query_array = np.array(query_vector, dtype=np.float32)

        # 搜索
        results = self.vector_store.search(query_array, top_k=top_k)

        return results

    def get_file_dependencies(self, node_id: str, max_hops: int = 3) -> Dict[str, float]:
        """
        获取文件依赖

        Args:
            node_id: 文件节点ID
            max_hops: 最大跳数

        Returns:
            {node_id: weight, ...}
        """
        return self.graph_store.propagate_weights(node_id, max_hops=max_hops)

    def save(self, output_dir: str):
        """保存语义网"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 保存向量存储
        self.vector_store.save(str(output_path / "vectors.pkl"))

        # 保存图存储
        self.graph_store.save(str(output_path / "graph.json"))

        # 保存元数据存储
        self.metadata_store.export_to_file(str(output_path / "metadata.db"))

        print(f"语义网已保存到: {output_path}")

    def load(self, input_dir: str):
        """加载语义网"""
        input_path = Path(input_dir)

        # 加载向量存储
        self.vector_store.load(str(input_path / "vectors.pkl"))

        # 加载图存储
        self.graph_store.load(str(input_path / "graph.json"))

        # 加载元数据存储
        self.metadata_store = MetadataStore(str(input_path / "metadata.db"))

        print(f"语义网已从 {input_path} 加载")


if __name__ == "__main__":
    # 测试代码
    builder = SemanticBuilder("./test_project")

    print("分析项目结构...")
    analysis = builder.analyze_project()
    print(f"分析结果: {analysis}")

    print("\n构建语义网...")
    stats = builder.build_semantic_web()
    print(f"构建统计: {stats}")

    print("\n技术栈:")
    tech_stack = builder.get_tech_stack()
    print(tech_stack)

    print("\n搜索相似文件...")
    results = builder.search_similar_files("用户认证", top_k=5)
    print(f"搜索结果: {results}")
