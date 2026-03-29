# BEEE Context Analyzer - 架构说明

## 目录
1. [系统概述](#系统概述)
2. [架构设计](#架构设计)
3. [核心模块](#核心模块)
4. [数据流](#数据流)
5. [性能优化](#性能优化)

## 系统概述

BEEE Context Analyzer 是一个为 AI Agent 提供高密度项目上下文信息的系统。通过语义网构建、权重计算和智能调度，帮助 Agent 更好地理解代码库结构、依赖关系和上下文信息。

### 核心特性

- **零外部依赖**：不依赖 Qdrant/Neo4j/PostgreSQL，使用内置存储
- **Rust 加速**：可选的 Rust 计算核心，提供 SIMD 加速
- **智能调度**：根据任务类型自动预测和分配资源
- **灵活降级**：Rust 核心不可用时自动使用 Python 实现

## 架构设计

### 三层架构

```
┌─────────────────────────────────────────────────┐
│         Layer 3: 调度协调层 (Python)             │
│  - 意图识别                                      │
│  - 依赖展开                                      │
│  - 资源分配                                      │
│  - 上下文摘要生成                                │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│         Layer 2: 计算核心层 (Rust + Python)      │
│  ┌──────────────┐  ┌──────────────┐              │
│  │ 向量相似度   │  │ 依赖图遍历   │              │
│  │ (Rust SIMD)  │  │ (Rust 多线程)│              │
│  └──────────────┘  └──────────────┘              │
│  Python Fallback 降级支持                         │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│         Layer 1: 存储索引层 (Python)             │
│  ┌──────────────┐  ┌──────────────┐              │
│  │ 向量存储     │  │ 图存储       │              │
│  │ (numpy)      │  │ (邻接表)     │              │
│  └──────────────┘  └──────────────┘              │
│  ┌──────────────┐                               │
│  │ 元数据存储   │                               │
│  │ (SQLite)     │                               │
│  └──────────────┘                               │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│         Layer 0: 数据摄入层 (Python)             │
│  - 项目结构分析                                  │
│  - 代码解析                                      │
│  - 依赖提取                                      │
│  - 语义向量生成                                  │
└─────────────────────────────────────────────────┘
```

## 核心模块

### 1. 数据摄入层

#### SemanticBuilder

负责从代码库构建语义网：

```python
builder = SemanticBuilder(project_root="./my-project")
builder.build_semantic_web()
```

**功能**：
- 遍历项目目录，识别代码文件
- 提取函数、类、import 语句
- 生成简化版语义向量
- 构建向量和图索引

**支持的语言**：
- Python, JavaScript, TypeScript, Java
- C/C++, Go, Rust, Ruby, PHP

### 2. 存储索引层

#### VectorStore (向量存储)

使用 numpy 实现的内存向量索引：

```python
store = VectorStore(dimension=768)
store.add_vector(node_id="file1", vector=np.array([...]))
results = store.search(query_vector, top_k=10)
```

**特性**：
- 内存存储，快速访问
- 支持余弦相似度和欧氏距离
- 批量相似度计算

#### GraphStore (图存储)

使用邻接表实现的图存储：

```python
graph = GraphStore()
graph.add_node("module_a", {"type": "module"})
graph.add_edge("module_a", "module_b", "imports", 0.9)
weights = graph.propagate_weights("module_a", max_hops=3)
```

**特性**：
- 支持有向带权图
- BFS/DFS 遍历
- 权重传播算法
- 连通分量检测

#### MetadataStore (元数据存储)

基于 SQLite 的元数据存储：

```python
store = MetadataStore(db_path="metadata.db")
store.add_node(node_id="file1", node_type="file", language="python")
nodes = store.query_nodes(language="python", limit=10)
```

**特性**：
- 持久化存储
- 索引查询
- 事务支持
- Python 内置，零依赖

### 3. 计算核心层

#### WeightCalculator (权重计算)

支持 Rust SIMD 加速的权重计算：

```python
calc = WeightCalculator()  # 自动检测 Rust 核心
scores = calc.compute_similarity(query, candidates)
weights = calc.propagate_weights(start_node, graph_data, max_hops=3)
```

**特性**：
- 自动检测 Rust 核心
- Rust 不可用时降级到 Python
- SIMD 加速的向量计算
- 多线程图遍历

**性能对比**：
- Python 纯实现：1000 节点 ~200ms
- Rust 加速：1000 节点 ~50ms

### 4. 调度协调层

#### Scheduler (预测调度)

智能调度资源：

```python
scheduler = Scheduler(semantic_builder)
result = scheduler.schedule(
    task_description="修复登录功能的bug",
    max_resources=20
)
```

**功能**：
- 意图识别（重构/Bug修复/新功能/优化/测试）
- 依赖展开（2-3跳）
- 资源分配（基于权重）
- 上下文摘要生成

## 数据流

### 构建流程

```
代码文件
    ↓
SemanticBuilder.analyze_project()
    ↓
[提取代码元素]
    ↓
[构建图结构]
    ↓
[生成向量]
    ↓
[存储到 SQLite]
    ↓
语义网完成
```

### 查询流程

```
用户查询
    ↓
IntentRecognizer.recognize()
    ↓
[识别任务类型]
    ↓
DependencyExpander.expand()
    ↓
[展开依赖关系]
    ↓
ResourceAllocator.allocate()
    ↓
[计算权重]
    ↓
[生成摘要]
    ↓
返回结果
```

## 性能优化

### Rust 加速

Rust 核心提供以下优化：

1. **SIMD 指令集**：并行计算向量相似度
2. **多线程**：并行图遍历
3. **零拷贝 FFI**：高效的数据传递

### Python 优化

Python 实现的优化：

1. **Numpy 向量化**：批量计算使用 numpy 矢量操作
2. **缓存机制**：向量索引缓存到内存
3. **懒加载**：按需加载文件内容

### 性能指标

| 操作 | Python 版本 | Rust 版本 |
|-----|------------|----------|
| 向量相似度（1000个） | ~150ms | ~40ms |
| 权重传播（3跳） | ~100ms | ~30ms |
| 资源调度 | ~200ms | ~80ms |

## 适用场景

### 适用

- 中小型项目（<5000 文件）
- 需要快速理解项目结构
- 代码重构和 Bug 修复
- 依赖关系分析

### 不适用

- 超大型项目（>10000 文件）
- 需要实时低延迟响应
- 需要分布式部署
- 需要复杂的语义理解（建议使用完整的 BEEE 系统）

## 扩展性

### 添加新语言支持

在 `semantic_builder.py` 中：

```python
self.file_types['.kt'] = 'kotlin'  # 添加 Kotlin

def _extract_code_elements(self, content, language):
    if language == "kotlin":
        # 实现 Kotlin 代码提取逻辑
        functions = re.findall(r'fun\s+(\w+)\s*\(', content)
        classes = re.findall(r'class\s+(\w+)', content)
        return functions, classes
```

### 添加新的权重因子

在 `weight_calculator.py` 中：

```python
def compute_custom_factor(self, node_id: str) -> float:
    """计算自定义权重因子"""
    # 实现自定义逻辑
    return weight
```

### 添加新的任务类型

在 `scheduler.py` 中：

```python
class TaskType(Enum):
    NEW_TASK_TYPE = "new_task_type"

self.keywords[TaskType.NEW_TASK_TYPE] = ["关键词1", "关键词2"]
```

## 限制

1. **向量维度**：默认 768 维，修改需要重建索引
2. **并发支持**：单线程 SQLite 写入，多线程读取
3. **内存占用**：向量索引全在内存中，大型项目可能需要大量内存
4. **语义理解**：简化版向量生成，不如专业嵌入模型准确
