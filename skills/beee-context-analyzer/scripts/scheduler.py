"""
预测调度模块

根据任务类型和上下文，智能预测和分配资源：
- 意图识别
- 依赖展开
- 资源分配
- 上下文摘要生成
"""

from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
import re
from datetime import datetime

from scripts.semantic_builder import SemanticBuilder
from scripts.weight_calculator import WeightCalculator


class TaskType(Enum):
    """任务类型枚举"""
    REFACTORING = "refactoring"        # 重构
    NEW_FEATURE = "new_feature"        # 新功能开发
    BUG_FIX = "bug_fix"                # Bug 修复
    OPTIMIZATION = "optimization"      # 性能优化
    TESTING = "testing"                # 测试
    DOCUMENTATION = "documentation"    # 文档编写
    REVIEW = "review"                  # 代码审查


class IntentRecognizer:
    """意图识别器"""

    def __init__(self):
        """初始化意图识别器"""
        self.keywords = {
            TaskType.REFACTORING: [
                "重构", "refactor", "重构代码", "代码优化", "清理", "优化代码",
                "improve", "clean up", "restructure", "modernize"
            ],
            TaskType.NEW_FEATURE: [
                "新增", "添加功能", "实现", "开发", "build", "add feature",
                "implement", "create", "develop", "新功能", "feature"
            ],
            TaskType.BUG_FIX: [
                "修复", "bug", "错误", "error", "fix", "修复bug", "解决错误",
                "debug", "问题", "issue", "故障", "exception"
            ],
            TaskType.OPTIMIZATION: [
                "优化性能", "性能", "optimize", "performance", "加速",
                "提升性能", "提高速度", "slow", "卡顿", "延迟"
            ],
            TaskType.TESTING: [
                "测试", "test", "单元测试", "集成测试", "unit test",
                "验证", "verify", "测试用例", "test case"
            ],
            TaskType.DOCUMENTATION: [
                "文档", "document", "说明", "readme", "注释", "comment",
                "文档编写", "添加注释", "说明文档"
            ],
            TaskType.REVIEW: [
                "审查", "review", "代码审查", "code review", "检查", "check",
                "review code", "检查代码"
            ]
        }

    def recognize(self, text: str) -> Tuple[TaskType, float]:
        """
        识别任务意图

        Args:
            text: 用户输入文本

        Returns:
            (task_type, confidence)
        """
        text_lower = text.lower()

        scores = {}

        for task_type, keywords in self.keywords.items():
            score = 0.0
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    score += 1.0

            scores[task_type] = score

        # 找到得分最高的任务类型
        max_score = max(scores.values())

        if max_score == 0:
            return TaskType.NEW_FEATURE, 0.0

        # 归一化得分
        total_score = sum(scores.values())
        normalized_scores = {k: v / total_score if total_score > 0 else 0 for k, v in scores.items()}

        best_task = max(normalized_scores.items(), key=lambda x: x[1])

        return best_task


class DependencyExpander:
    """依赖展开器"""

    def __init__(self, semantic_builder: SemanticBuilder):
        """
        初始化依赖展开器

        Args:
            semantic_builder: 语义网构建器
        """
        self.builder = semantic_builder

    def expand(
        self,
        start_nodes: List[str],
        max_hops: int = 2,
        edge_types: Optional[List[str]] = None
    ) -> Set[str]:
        """
        展开依赖关系

        Args:
            start_nodes: 起始节点列表
            max_hops: 最大跳数
            edge_types: 边类型过滤（可选）

        Returns:
            相关节点集合
        """
        related_nodes = set()

        for node_id in start_nodes:
            # 从图存储中获取依赖
            weights = self.builder.graph_store.propagate_weights(
                node_id,
                max_hops=max_hops
            )

            # 如果指定了边类型，过滤结果
            if edge_types:
                for related_id, weight in weights.items():
                    # 检查是否有指定类型的边
                    neighbors = self.builder.graph_store.get_neighbors(related_id)
                    for neighbor_id, _ in neighbors:
                        if neighbor_id in start_nodes:
                            related_nodes.add(related_id)
                            break
            else:
                related_nodes.update(weights.keys())

        return related_nodes

    def expand_by_imports(self, file_node_id: str) -> Set[str]:
        """
        基于导入关系展开

        Args:
            file_node_id: 文件节点ID

        Returns:
            被导入的模块集合
        """
        imports = self.builder.graph_store.get_neighbors(
            file_node_id,
            edge_type="imports"
        )

        return {node_id for node_id, _ in imports}


class ResourceAllocator:
    """资源分配器"""

    def __init__(self, semantic_builder: SemanticBuilder):
        """
        初始化资源分配器

        Args:
            semantic_builder: 语义网构建器
        """
        self.builder = semantic_builder
        self.calculator = WeightCalculator()

    def allocate(
        self,
        related_nodes: Set[str],
        task_type: TaskType,
        max_resources: int = 20
    ) -> Dict[str, float]:
        """
        分配资源（计算节点权重）

        Args:
            related_nodes: 相关节点集合
            task_type: 任务类型
            max_resources: 最大资源数量

        Returns:
            {node_id: weight, ...}
        """
        if not related_nodes:
            return {}

        # 获取节点元数据
        weights = {}

        for node_id in related_nodes:
            node = self.builder.metadata_store.get_node(node_id)

            if not node:
                continue

            # 基础权重
            base_weight = 1.0

            # 根据任务类型调整权重
            if task_type == TaskType.BUG_FIX:
                # Bug修复：优先核心模块
                if node.get("type") == "file":
                    tags = node.get("tags", [])
                    if "core" in tags or "critical" in tags:
                        base_weight *= 2.0

            elif task_type == TaskType.OPTIMIZATION:
                # 性能优化：优先大文件
                line_count = node.get("line_count", 0)
                if line_count > 500:
                    base_weight *= 1.5

            elif task_type == TaskType.DOCUMENTATION:
                # 文档编写：优先未文档化的模块
                if node.get("type") in ["function", "class"]:
                    base_weight *= 1.2

            weights[node_id] = base_weight

        # 归一化
        weights = self.calculator.normalize_weights(weights, method="max")

        # 获取 Top-K
        top_k = self.calculator.top_k(weights, k=max_resources)

        return dict(top_k)


class Scheduler:
    """预测调度器"""

    def __init__(self, semantic_builder: Optional[SemanticBuilder] = None):
        """
        初始化调度器

        Args:
            semantic_builder: 语义网构建器（可选，如果未提供则创建一个）
        """
        if semantic_builder is None:
            self.builder = SemanticBuilder()
            self.builder.analyze_project()
            self.builder.build_semantic_web()
        else:
            self.builder = semantic_builder

        self.intent_recognizer = IntentRecognizer()
        self.dependency_expander = DependencyExpander(self.builder)
        self.resource_allocator = ResourceAllocator(self.builder)

    def schedule(
        self,
        task_description: Optional[str] = None,
        task_type: Optional[str] = None,
        context: Optional[str] = None,
        context_nodes: Optional[List[str]] = None,
        max_resources: int = 20
    ) -> Dict:
        """
        智能调度资源

        Args:
            task_description: 任务描述（兼容旧版本）
            task_type: 任务类型（"bug_fix", "new_feature", "refactoring" 等）
            context: 上下文描述
            context_nodes: 上下文节点列表（可选）
            max_resources: 最大资源数量

        Returns:
            {
                "task_type": TaskType,
                "confidence": float,
                "files": List[Dict],
                "summary": str
            }
        """
        # 兼容 SKILL.md 中的调用方式
        if task_type and context:
            # 新的调用方式：scheduler.schedule(task_type="bug_fix", context="...")
            task_description = f"{task_type}: {context}"
        elif not task_description:
            task_description = "default task"

        # 1. 识别意图
        recognized_type, confidence = self.intent_recognizer.recognize(task_description)

        # 如果明确指定了 task_type，使用指定的类型
        if task_type:
            try:
                # 尝试匹配 TaskType 枚举
                from scripts.scheduler import TaskType
                for t in TaskType:
                    if t.value == task_type or t.name == task_type.upper():
                        recognized_type = t
                        break
            except:
                pass

        print(f"识别到任务类型: {recognized_type.value} (置信度: {confidence:.2f})")

        # 2. 确定起始节点
        start_nodes = []

        if context_nodes:
            start_nodes = context_nodes
        else:
            # 如果没有指定上下文节点，使用语义搜索找到相关文件
            search_results = self.builder.search_similar_files(task_description, top_k=5)
            start_nodes = [node_id for node_id, _ in search_results]

        if not start_nodes:
            # 如果还是没有，获取所有文件节点
            all_nodes = self.builder.get_all_nodes()
            start_nodes = [node.get("node_id") for node in all_nodes if node.get("type") == "file"][:5]

        # 3. 展开依赖
        related_nodes = self.dependency_expander.expand(start_nodes, max_hops=2)

        # 4. 分配资源（计算权重）
        allocated = self.resource_allocator.allocate(
            related_nodes,
            recognized_type,
            max_resources
        )

        # 5. 生成文件列表
        files = []
        for node_id, weight in allocated.items():
            node = self.builder.metadata_store.get_node(node_id)
            if node:
                files.append({
                    "node_id": node_id,
                    "path": node.get("file_path"),
                    "type": node.get("type"),
                    "language": node.get("language"),
                    "line_count": node.get("line_count"),
                    "weight": weight
                })

        # 按权重排序
        files.sort(key=lambda x: x["weight"], reverse=True)

        # 6. 生成摘要
        summary = self._generate_summary(recognized_type, files, task_description)

        return {
            "task_type": recognized_type,
            "confidence": confidence,
            "files": files,
            "summary": summary
        }

    def _generate_summary(
        self,
        task_type: TaskType,
        files: List[Dict],
        task_description: str
    ) -> str:
        """生成上下文摘要"""
        if not files:
            return "未找到相关文件"

        # 统计信息
        total_files = len([f for f in files if f["type"] == "file"])
        total_functions = len([f for f in files if f["type"] == "function"])
        total_classes = len([f for f in files if f["type"] == "class"])

        languages = set(f["language"] for f in files if f.get("language"))
        total_lines = sum(f.get("line_count") or 0 for f in files)

        # 生成摘要
        summary = f"## 任务上下文摘要\n\n"
        summary += f"**任务类型**: {task_type.value}\n"
        summary += f"**涉及文件**: {total_files} 个\n"
        summary += f"**涉及函数**: {total_functions} 个\n"
        summary += f"**涉及类**: {total_classes} 个\n"
        summary += f"**代码行数**: {total_lines} 行\n"
        summary += f"**编程语言**: {', '.join(languages) if languages else 'N/A'}\n\n"

        summary += f"### 相关文件（按相关性排序）\n\n"

        for i, file_info in enumerate(files[:10], 1):
            path = file_info.get("path", "Unknown")
            weight = file_info.get("weight", 0)
            file_type = file_info.get("type", "file")

            summary += f"{i}. **[{path}]** ({file_type}, 权重: {weight:.2f})\n"

        summary += f"\n### 任务说明\n\n{task_description}"

        return summary


if __name__ == "__main__":
    # 测试代码
    print("构建语义网...")
    builder = SemanticBuilder("./test_project")
    builder.build_semantic_web()

    print("\n初始化调度器...")
    scheduler = Scheduler(builder)

    print("\n测试意图识别...")
    intent, conf = scheduler.intent_recognizer.recognize("需要重构用户登录模块")
    print(f"意图: {intent.value}, 置信度: {conf:.2f}")

    print("\n测试资源调度...")
    result = scheduler.schedule(
        task_description="修复登录功能的bug",
        max_resources=10
    )

    print(f"任务类型: {result['task_type'].value}")
    print(f"置信度: {result['confidence']:.2f}")
    print(f"相关文件数量: {len(result['files'])}")

    print("\n摘要:")
    print(result["summary"])
