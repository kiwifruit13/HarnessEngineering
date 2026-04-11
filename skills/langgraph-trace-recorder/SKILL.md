---
name: langgraph-trace-recorder
description: 将模型执行过程（问答+命令）转化为结构化知识图谱，为模型复杂推理提供上下文锚点，为复盘提供结构化依据；当用户需要记录LangGraph任务执行、进行复杂推理分析或复盘执行过程时使用
dependency:
  python:
    - pydantic>=2.0.0
    - graphviz>=0.20.0
    - redis>=5.0.0  # 可选，用于Redis存储后端
---

# LangGraph 轨迹记录器

本 Skill 将 LangGraph 执行过程（问答+命令）转化为结构化知识图谱，支持复杂推理锚点和复盘分析。详见 [全局概览](references/overview.md)。

## 任务目标

实时捕获 LangGraph 执行状态，构建双类型知识图谱（问答轨迹/命令轨迹），支持错误记录和多格式导出。

- **能力**：自动捕获执行状态、分类节点类型、构建知识图谱、记录错误信息、导出多种格式
- **触发**：记录任务执行、复杂推理分析、复盘执行过程、优化决策路径时

## 前置准备

### 依赖说明

```
pydantic>=2.0.0
graphviz>=0.20.0
redis>=5.0.0  # 可选，仅使用Redis存储后端时需要
```

### 存储后端选择

- **内存存储**（默认）：单机、临时数据，无需配置
- **Redis存储**（可选）：分布式、持久化，需要配置Redis

### Redis配置（可选）

```bash
# 启动Redis服务（Docker方式）
docker run -d -p 6379:6379 redis:7-alpine
```

## 操作步骤

### 标准流程

1. **选择存储后端**

   **默认使用内存存储**（推荐）：
   ```python
   from scripts.graph_builder import KnowledgeGraph

   # 使用内存存储（默认）
   graph = KnowledgeGraph(task_id="my_task")

   # 或显式指定
   from scripts.memory_storage import MemoryGraphStorage
   storage = MemoryGraphStorage()
   graph = KnowledgeGraph(task_id="my_task", storage_backend=storage)
   ```

   **可选Redis存储**（分布式场景）：
   ```python
   from scripts.redis_storage import RedisGraphStorage

   storage = RedisGraphStorage(
       redis_url="redis://localhost:6379/0",
       key_prefix="langgraph"
   )
   graph = KnowledgeGraph(task_id="my_task", storage_backend=storage)

   # 使用完毕后关闭连接
   graph.close()
   ```

2. **集成LangGraph Callback**

   在LangGraph应用中引入Callback Handler，编译Graph时传入callback参数。参见 [references/integration_example.md](references/integration_example.md)

3. **执行任务并记录轨迹**

   运行LangGraph应用，Callback自动捕获执行状态，自动分类节点类型（问答/命令），构建知识图谱

4. **导出结果**

   调用 `scripts/graph_exporter.py` 导出图谱数据，支持三种格式：
   - JSON：完整图谱数据
   - SVG：可视化流程图
   - Markdown：结构化报告

### 可选分支

- 手动记录推理过程：使用显式API调用
- 自定义分类规则：修改 `scripts/classifier.py`
- 自定义图谱属性：添加自定义metadata字段
- 分析失败原因：查看Markdown报告中的失败节点详情
- 分布式部署：使用Redis存储后端
- 持久化数据：使用Redis存储后端自动持久化

## 资源索引

### 必要脚本

- [scripts/definitions.py](scripts/definitions.py) - 所有类型定义（TypedDict、Enum、Pydantic Model）
- [scripts/storage_backend.py](scripts/storage_backend.py) - 存储后端抽象接口
- [scripts/memory_storage.py](scripts/memory_storage.py) - 内存存储后端实现（默认）
- [scripts/redis_storage.py](scripts/redis_storage.py) - Redis存储后端实现（可选）
- [scripts/callback_handler.py](scripts/callback_handler.py) - LangGraph Callback Handler实现
- [scripts/classifier.py](scripts/classifier.py) - 节点分类逻辑
- [scripts/graph_builder.py](scripts/graph_builder.py) - 图谱数据构建（支持存储后端选择）
- [scripts/graph_exporter.py](scripts/graph_exporter.py) - 多格式导出（JSON/SVG/Markdown）

### 领域参考

- [references/overview.md](references/overview.md) - 全局概览（核心定位、设计理念、应用场景）
- [references/data_format.md](references/data_format.md) - 状态数据格式定义
- [references/integration_example.md](references/integration_example.md) - LangGraph集成示例

## 注意事项

- **类型安全**：所有函数都有严格的类型注解，禁止隐式Any
- **数据结构**：所有数据结构通过TypedDict或Pydantic Model定义，禁止裸dict传递
- **防御性编程**：外部输入必须经过isinstance检查或类型验证
- **性能考虑**：大规模轨迹建议使用增量构建模式
- **SVG依赖**：导出SVG需要系统安装graphviz工具
- **错误处理**：Callback会自动捕获节点执行异常并记录详细的错误信息（包括堆栈跟踪和恢复建议）
