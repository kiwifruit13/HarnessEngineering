---
name: agent-memory
description: 当智能体涉及"memory"与"Context"的操作时触发skill；智能体底层记忆基础设施，完整实现Context Engineering五大核心能力：选择（噪声过滤+相关性筛选）、压缩（因果结构提取+工具结果压缩）、检索（结果重排序+多样性保证）、状态（任务进度追踪+目标对齐）、记忆（冲突检测+跨会话关联）；认知模型层支持认知模型构建、因果链提取、知识缺口识别、检索时机决策、质量评估、状态一致性校验、状态推理、跨会话关联、遗忘机制；作为元技能强制常驻运行
always: true
dependency:
  python:
    - pydantic>=2.0.0
    - typing-extensions>=4.0.0
    - cryptography>=41.0.0
    - redis>=4.5.0
    - tiktoken>=0.5.0
    - mmh3>=3.0.0
license: GPL-3.0
author: kiwifruit
---

# Agent Memory System

**版权所有 © 2024 kiwifruit**

本程序采用 GNU General Public License v3.0 许可证。

详见: [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html)

## 任务目标

- 本 Skill 用于：为智能体构建完整的记忆能力基础设施，实现 Context Engineering 核心能力
- 触发条件：**元技能，强制常驻运行**（`always: true`）
- 核心能力：
  - **选择**：噪声过滤 + 相关性筛选
  - **压缩**：因果结构提取 + 工具结果压缩
  - **检索**：结果重排序 + 多样性保证
  - **状态**：任务进度追踪 + 目标对齐
  - **记忆**：冲突检测 + 跨会话关联

## 前置准备

### 依赖安装

```bash
pip install pydantic>=2.0.0 typing-extensions>=4.0.0 cryptography>=41.0.0 redis>=4.5.0 tiktoken>=0.5.0 mmh3>=3.0.0
```

### 存储路径配置

所有模块初始化时**必须指定存储路径**：

```python
base_path = "./memory_data"
key_storage_path = f"{base_path}/keys"
sync_state_path = f"{base_path}/sync_state"
index_storage_path = f"{base_path}/memory_index"
credential_path = f"{base_path}/credentials"
```

### Redis 连接（可选，推荐）

```python
from scripts import create_redis_adapter

redis_adapter = create_redis_adapter(host="localhost", port=6379)
if redis_adapter.is_available():
    print("Redis 连接成功")
```

## 操作步骤

### Step 1: 隐私配置（必需）

在使用记忆功能前，必须初始化隐私管理器并获取用户同意。

```python
from scripts import PrivacyManager, ConsentStatus

privacy_manager = PrivacyManager(user_id="user_123")
if privacy_manager.get_consent_status("memory_storage") == ConsentStatus.NOT_REQUESTED:
    privacy_manager.request_consent(
        consent_type="memory_storage",
        description="是否允许存储交互记忆以提供个性化服务？"
    )
```

### Step 2: 感知与短期记忆

感知记忆用于实时对话存储，短期记忆用于语义分类存储。

```python
from scripts import PerceptionMemoryStore, ShortTermMemoryManager, SemanticBucketType

# 感知记忆
perception = PerceptionMemoryStore()
session_id = perception.create_session()

# 短期记忆
short_term = ShortTermMemoryManager()
item_id = short_term.store_with_semantics(
    content="用户想要实现登录功能",
    bucket_type=SemanticBucketType.USER_INTENT,
    topic_label="用户登录",
    relevance_score=0.85,
)
```

### Step 3: 长期记忆

长期记忆用于持久化用户画像和程序性知识。

```python
from scripts import LongTermMemoryManager

long_term = LongTermMemoryManager()
long_term.update_user_profile(profile_data)
long_term.apply_heat_policy()
```

### Step 4: 上下文重构与洞察

从记忆中重构上下文，并生成洞察。

```python
from scripts import ContextReconstructor, InsightModule

reconstructor = ContextReconstructor()
insight_module = InsightModule()

context = reconstructor.reconstruct(situation, long_term.get_all_memories())
insights = insight_module.process(context, long_term.get_all_memories())
```

### Step 5: 全局状态捕捉（LangGraph集成）

捕捉和同步全局状态，支持 LangGraph 集成。

```python
from scripts import GlobalStateCapture, StateEventType

capture = GlobalStateCapture(
    user_id="user_123",
    storage_path="./state_storage",
)

# 从 LangGraph 同步
checkpoint_id = capture.sync_from_langgraph(
    state={"phase": "executing", "current_task": "create_memory"},
    node_name="executor",
)

# 事件订阅
subscription_id = capture.subscribe(
    event_types=[StateEventType.PHASE_CHANGE, StateEventType.TASK_SWITCH],
    callback=on_phase_change,
)
```

### Step 6: Context Orchestrator（总控层）

使用上下文编排器统一管理记忆和上下文准备。

```python
from scripts import create_context_orchestrator, SemanticBucketType

orchestrator = create_context_orchestrator(
    user_id="user_123",
    session_id="session_456",
    max_context_tokens=32000,
)

# 存储记忆
orchestrator.store_memory(
    content="用户想要实现登录功能",
    bucket_type=SemanticBucketType.USER_INTENT,
    topic_label="用户登录",
)

# 准备上下文
context = orchestrator.prepare_context(
    user_input="帮我分析这段代码的性能问题",
    system_instruction="你是一个代码分析专家",
    retrieval_results=["性能优化最佳实践"],
    tool_results=["代码分析结果..."],
)

# 结束会话
final_stats = orchestrator.end_session()
```

### 更多功能模块

以下功能模块提供高级能力，详细使用示例请参阅 [references/usage_guide.md](references/usage_guide.md)：

- **认知模型构建**：构建任务认知模型
- **因果链提取**：提取因果关系
- **知识缺口识别**：识别知识缺口
- **检索决策与评估**：决定是否检索
- **结果压缩**：压缩长文本
- **任务进度追踪**：追踪任务进度
- **链式推理增强**：增强推理反思能力

## 资源索引

### 核心参考文档

| 文档 | 用途 | 何时读取 |
|------|------|----------|
| [architecture_overview.md](references/architecture_overview.md) | 架构总览 | 需要全局架构视角 |
| [architecture_execution_model.md](references/architecture_execution_model.md) | 执行模型说明 | 理解 Skill 运行方式和执行模型 |
| [module_index.md](references/module_index.md) | 模块索引 | 查看所有模块和分类 |
| [usage_guide.md](references/usage_guide.md) | 使用指南 | 查看详细使用示例 |
| [api_enums.md](references/api_enums.md) | 枚举参考 | 查阅枚举类型定义 |
| [api_class_reference.md](references/api_class_reference.md) | API 类参考 | 查看所有导出类名和职责 |

### 专题参考文档

| 文档 | 主题 | 何时读取 |
|------|------|----------|
| [memory_types.md](references/memory_types.md) | 记忆结构 | 深入理解记忆结构 |
| [chain_reasoning_guide.md](references/chain_reasoning_guide.md) | 链式推理 | 链式推理增强集成 |
| [encryption_guide.md](references/encryption_guide.md) | 数据加密 | 了解数据加密机制 |
| [privacy_guide.md](references/privacy_guide.md) | 隐私配置 | 隐私配置和合规要求 |
| [insight_design.md](references/insight_design.md) | 洞察生成 | 洞察生成机制设计 |
| [activation_mechanism.md](references/activation_mechanism.md) | 记忆激活 | 记忆激活机制 |

### 集成参考文档

| 文档 | 主题 | 何时读取 |
|------|------|----------|
| [agent_loops_integration.md](references/agent_loops_integration.md) | 智能体循环集成 | 与 Agent Loop 集成 |
| [agent_loops_advanced.md](references/agent_loops_advanced.md) | Agent Loop 架构演进 | 深入理解架构演进 |
| [index_sync_guide.md](references/index_sync_guide.md) | 索引同步 | 索引同步机制 |
| [short_term_insight_guide.md](references/short_term_insight_guide.md) | 短期记忆洞察 | 短期记忆洞察分析 |

## 注意事项

1. **路径必传**：所有存储路径无默认值，必须显式传入
2. **隐私优先**：处理用户数据前必须初始化 `PrivacyManager` 并获取同意
3. **敏感数据**：系统自动识别密码、账号等敏感信息，默认不存储
4. **类型安全**：所有函数必须有类型注解，禁止使用裸 dict
5. **异步优先**：提炼、热度计算等后台异步执行
6. **降级策略**：模块故障时自动降级，保证核心流程可用
7. **统一入口**：推荐使用 `ContextOrchestrator` 作为统一入口，避免直接调用内部模块
8. **Skill 定位**：本 Skill 是能力扩展包，由智能体动态加载，非独立应用

## 快速开始

```python
from scripts import (
    PerceptionMemoryStore,
    ShortTermMemoryManager,
    LongTermMemoryManager,
    ContextReconstructor,
    SemanticBucketType,
    PrivacyManager,
    ConsentStatus,
)

# 1. 隐私配置
privacy_manager = PrivacyManager(user_id="user_123")
if privacy_manager.get_consent_status("memory_storage") != ConsentStatus.GRANTED:
    privacy_manager.request_consent(
        consent_type="memory_storage",
        description="是否允许存储交互记忆？"
    )

# 2. 初始化核心模块
perception = PerceptionMemoryStore()
short_term = ShortTermMemoryManager()
long_term = LongTermMemoryManager()
reconstructor = ContextReconstructor()

# 3. 处理对话
session_id = perception.create_session()
perception.store_conversation(session_id, user_message, system_response)

# 4. 短期记忆
short_term.store_with_semantics(
    user_message,
    SemanticBucketType.USER_INTENT,
    "话题",
    0.8
)

# 5. 上下文重构
context = reconstructor.reconstruct(situation, long_term.get_all_memories())

# 6. 推荐使用统一入口（可选）
from scripts import create_context_orchestrator

orchestrator = create_context_orchestrator(
    user_id="user_123",
    session_id="session_456",
    max_context_tokens=32000,
)
```

## 常见问题

### Q: 如何选择存储方案？

**A**:
- **文件存储**：默认方案，适合大多数场景，无需额外依赖
- **Redis 存储**：高性能场景，需要部署 Redis 服务器

### Q: 如何优化 Token 使用？

**A**: 使用 `ContextOrchestrator` 自动管理 Token 预算，系统会智能压缩和筛选内容。

### Q: 如何处理记忆冲突？

**A**: 系统自动检测和解决冲突，无需手动处理。`ContextOrchestrator` 内置冲突解决机制。

### Q: 如何导出和导入记忆数据？

**A**: 使用 `LongTermMemoryManager` 的 `export()` 和 `import()` 方法。

### Q: 如何监控记忆系统性能？

**A**: 系统内置监控能力，可通过 `ContextOrchestrator` 获取性能统计信息。

### Q: Skill 如何运行？

**A**: 本 Skill 是智能体的能力扩展包，由智能体动态加载和执行。不需要独立启动服务器或监听端口。所有交互通过智能体与用户的对话完成。

详见 [architecture_execution_model.md](references/architecture_execution_model.md)。
