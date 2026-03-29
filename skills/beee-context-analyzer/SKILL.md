---
name: beee-context-analyzer
description: 提供项目上下文的高密度信息分析，支持代码语义网构建、依赖权重计算和智能资源调度；当用户需要理解新项目结构、分析代码依赖关系、获取相关模块信息、优化工程上下文或进行代码重构时使用
dependency:
  python:
    - numpy>=1.24.0
  system:
    - "cd beee-context-analyzer/scripts/rust_core && cargo build --release 2>/dev/null || true"
---

# 最佳工程执行环境上下文分析器 (BEEE Context Analyzer)

## 任务目标
- 本 Skill 用于：为 AI Agent 提供高密度的项目上下文信息，包括代码结构、语义关系、依赖权重和智能调度
- 能力包含：语义网构建、权重计算、预测调度、状态跟踪
- 触发条件：用户需要理解项目结构、查找相关代码、分析依赖关系、获取上下文摘要

## 前置准备
- 依赖说明：
  - numpy（Python 内置的数值计算库）
- Rust 核心说明：
  - 已包含预编译的 Linux `.so` 文件（538KB）
  - 自动路径验证和完整性检查
  - 如需重新编译或其他平台版本，请参考 [references/rust-build-guide.md](references/rust-build-guide.md)
  - 注意：当前版本使用 Python 实现，Rust 核心保留用于未来优化

## 操作步骤

### 标准流程

1. **项目结构分析**
   - 调用 `scripts/semantic_builder.py` 构建语义网
   - 输入：项目根目录路径
   - 输出：项目结构、技术栈、关键文件索引

2. **权重计算**
   - 调用 `scripts/weight_calculator.py` 计算节点权重
   - 自动检测 Rust 核心是否可用，优先使用加速版本
   - 输出：节点权重列表、依赖关系图

3. **上下文调度**
   - 调用 `scripts/scheduler.py` 根据任务类型预测资源需求
   - 输入：任务类型（重构/新功能/Bug修复/优化/测试）
   - 输出：相关文件列表、权重排序、上下文摘要

### 可选分支

- 当 Rust 核心可用：使用 SIMD 加速的向量计算和多线程图遍历
- 当 Rust 核心不可用：自动降级到 Python 纯实现（功能相同，性能较低）

## 资源索引

- 核心脚本：
  - [scripts/semantic_builder.py](scripts/semantic_builder.py) - 语义网构建模块
  - [scripts/vector_store.py](scripts/vector_store.py) - 向量索引（Python 版）
  - [scripts/graph_store.py](scripts/graph_store.py) - 图存储（Python 版）
  - [scripts/metadata_store.py](scripts/metadata_store.py) - 元数据存储（SQLite）
  - [scripts/weight_calculator.py](scripts/weight_calculator.py) - 权重计算（支持 Rust 加速）
  - [scripts/scheduler.py](scripts/scheduler.py) - 预测调度模块
  - [scripts/rust_core/](scripts/rust_core/) - Rust 高性能计算核心

- 参考文档：
  - [references/architecture.md](references/architecture.md) - 架构设计说明
  - [references/rust-build-guide.md](references/rust-build-guide.md) - Rust 编译指南

## 注意事项

- 首次使用建议先构建语义网索引
- Rust 核心编译是可选的，不编译也能正常运行（使用 Python fallback）
- 支持 1000-5000 节点的项目规模
- 对于超大型项目（>10000 节点），建议使用专业数据库版本

## 使用示例

### 示例1：分析项目结构
```python
from scripts.semantic_builder import SemanticBuilder

builder = SemanticBuilder()
builder.analyze_project("./my-project")
builder.build_semantic_web()

# 获取技术栈
tech_stack = builder.get_tech_stack()
print(tech_stack)  # {'language': 'Python', 'frameworks': ['Django'], 'databases': ['PostgreSQL']}
```

### 示例2：计算模块权重
```python
from scripts.weight_calculator import WeightCalculator

calc = WeightCalculator()
weights = calc.compute_weights(
    query="用户认证模块",
    nodes=builder.get_all_nodes()
)

# 获取最相关的文件
top_files = weights.top_k(10)
```

### 示例3：智能调度
```python
from scripts.scheduler import Scheduler

scheduler = Scheduler()
resources = scheduler.schedule(
    task_type="bug_fix",
    context="登录功能报错"
)

# 获取相关文件和上下文
print(resources.files)
print(resources.summary)
```
