# LangGraph Callback 数据格式

## 概览

本文档定义了LangGraph回调数据的格式规范，用于确保类型安全和数据一致性。

**项目定位**：本数据格式的最终目的是将模型的执行过程（问答+命令）转化为结构化知识，为模型的复杂推理提供上下文锚点，为复盘提供结构化依据。

**双轨迹设计**：
- **问答轨迹**：记录模型的认知层（思考、推理、决策、生成）
- **命令轨迹**：记录模型的行动层（工具调用、外部操作、数据获取）

**核心价值**：
- ✅ 推理锚点：查询历史成功路径，复用决策经验
- ✅ 复盘基础：分析失败原因，生成优化建议
- ✅ 知识复用：将执行经验转化为可复用的知识资产

## 目录

1. [节点数据格式](#节点数据格式)
2. [回调事件格式](#回调事件格式)
3. [数据验证规则](#数据验证规则)
4. [示例](#示例)

## 节点数据格式

### 节点类型 (NodeType)

```python
class NodeType(str, Enum):
    QUESTION = "question"      # 用户问题/查询
    ANSWER = "answer"          # 模型回答/响应
    COMMAND = "command"        # 工具命令/执行
    RESULT = "result"          # 执行结果/输出
    REASONING = "reasoning"    # 推理步骤（手动记录）
```

### 轨迹类型 (TraceType)

```python
class TraceType(str, Enum):
    QA_TRACE = "qa_trace"              # 问答轨迹
    COMMAND_TRACE = "command_trace"    # 命令轨迹
```

### NodeData 结构

```typescript
interface NodeData {
    id: string;                        // 节点唯一标识
    type: NodeType;                    // 节点类型（枚举值）
    label: string;                     // 节点标签（显示名称）
    content: string;                   // 节点内容（详细描述）
    timestamp: number;                 // 时间戳（Unix时间戳，秒）
    trace_type: TraceType;             // 所属轨迹类型（枚举值）
    metadata: {                        // 元数据（额外属性）
        [key: string]: any;
    };
}
```

#### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| id | string | 是 | 节点唯一标识，长度1-100，仅包含字母、数字、下划线、连字符 |
| type | NodeType | 是 | 节点类型，必须为NodeType枚举值之一 |
| label | string | 是 | 节点标签，用于显示，长度建议≤50字符 |
| content | string | 是 | 节点内容，详细描述节点执行的信息 |
| timestamp | number | 是 | Unix时间戳（秒），范围：0 ≤ t ≤ 4102444800 |
| trace_type | TraceType | 是 | 轨迹类型，QA_TRACE或COMMAND_TRACE |
| metadata | object | 是 | 元数据字典，可包含任意额外属性 |

#### metadata 常见字段

```typescript
interface NodeMetadata {
    status?: "running" | "completed" | "failed";  // 执行状态
    input_summary?: string;        // 输入数据摘要
    output_summary?: string;       // 输出数据摘要
    execution_time?: number;       // 执行耗时（秒）
    error?: string;                // 错误信息（如果失败）
}
```

## 回调事件格式

### LangGraphCallbackData 结构

```typescript
interface LangGraphCallbackData {
    event_type: "on_node_start" | "on_node_end" | "on_chain_start" | "on_chain_end";
    node_name: string;                     // 节点名称
    node_id?: string;                      // 节点ID（可选）
    input_data: {                          // 输入数据
        [key: string]: any;
    };
    output_data?: {                        // 输出数据（仅on_node_end事件）
        [key: string]: any;
    };
    timestamp: number;                     // 时间戳
    metadata: {                            // 元数据
        [key: string]: any;
    };
}
```

### 事件类型说明

| 事件类型 | 触发时机 | 必需字段 |
|---------|---------|---------|
| on_node_start | 节点开始执行 | node_name, input_data, timestamp |
| on_node_end | 节点执行结束 | node_name, output_data, timestamp |
| on_chain_start | 链开始执行 | node_name, input_data, timestamp |
| on_chain_end | 链执行结束 | node_name, output_data, timestamp |

## 数据验证规则

### 节点ID验证

- 必须为字符串类型
- 长度：1 ≤ length ≤ 100
- 允许字符：a-z, A-Z, 0-9, -, _
- 示例：`node_0`, `query_handler`, `tool_execute_1`

### 时间戳验证

- 必须为数字类型（浮点数）
- 范围：0 ≤ timestamp ≤ 4102444800（2100-01-01）
- 单位：Unix时间戳（秒）

### 权重验证

- 必须为数字类型（浮点数）
- 范围：0 ≤ weight ≤ 100
- 默认值：1.0

### 类型安全要求

1. **禁止隐式Any**：所有函数参数和返回值必须有明确的类型注解
2. **禁止裸dict**：涉及数据结构必须使用TypedDict或Pydantic Model定义
3. **防御性编程**：外部输入必须经过类型检查或验证
4. **严格区分**：数据对象与序列化字符串必须明确区分

## 示例

### 示例1：问答节点

```json
{
    "id": "node_0",
    "type": "answer",
    "label": "query_handler",
    "content": "query: 如何分析财报 | response: 首先需要获取财报数据...",
    "timestamp": 1735689600.0,
    "trace_type": "qa_trace",
    "metadata": {
        "status": "completed",
        "input_summary": "{\"query\": \"如何分析财报\"}",
        "output_summary": "{\"response\": \"首先需要获取财报数据...\"}"
    }
}
```

### 示例2：命令节点

```json
{
    "id": "node_1",
    "type": "command",
    "label": "download_pdf",
    "content": "url: https://example.com/report.pdf | output: 下载成功",
    "timestamp": 1735689660.0,
    "trace_type": "command_trace",
    "metadata": {
        "status": "completed",
        "execution_time": 2.5,
        "input_summary": "{\"url\": \"https://example.com/report.pdf\"}"
    }
}
```

### 示例3：推理节点（手动记录）

```json
{
    "id": "reasoning_0",
    "type": "reasoning",
    "label": "决策推理",
    "content": "我决定先搜索信息，再执行分析",
    "timestamp": 1735689630.0,
    "trace_type": "qa_trace",
    "metadata": {
        "context": {
            "query": "分析财报",
            "confidence": 0.95
        }
    }
}
```

### 示例4：完整的图谱数据

```json
{
    "nodes": {
        "node_0": {
            "id": "node_0",
            "type": "answer",
            "label": "query_handler",
            "content": "query: 如何分析财报 | response: 首先需要获取财报数据...",
            "timestamp": 1735689600.0,
            "trace_type": "qa_trace",
            "metadata": {
                "status": "completed"
            }
        },
        "node_1": {
            "id": "node_1",
            "type": "command",
            "label": "download_pdf",
            "content": "url: https://example.com/report.pdf | output: 下载成功",
            "timestamp": 1735689660.0,
            "trace_type": "command_trace",
            "metadata": {
                "status": "completed",
                "execution_time": 2.5
            }
        }
    },
    "edges": [
        {
            "source": "node_0",
            "target": "node_1",
            "type": "follows",
            "condition": null,
            "weight": 1.0
        }
    ],
    "metadata": {
        "task_id": "task_1735689600",
        "start_time": 1735689600.0,
        "end_time": 1735689670.0,
        "total_nodes": 2,
        "total_edges": 1,
        "qa_trace_count": 1,
        "command_trace_count": 1
    }
}
```

## 常见问题

### Q1: 如何手动添加节点？

使用`KnowledgeGraph.add_node()`方法：

```python
from scripts.graph_builder import KnowledgeGraph
from scripts.definitions import NodeType, TraceType

graph = KnowledgeGraph(task_id="my_task")
graph.add_node(
    node_id="my_node",
    node_type=NodeType.ANSWER,
    label="My Node",
    content="节点内容描述",
    trace_type=TraceType.QA_TRACE
)
```

### Q2: 如何自定义节点分类规则？

继承并重写`NodeClassifier`类：

```python
from scripts.classifier import NodeClassifier

class CustomClassifier(NodeClassifier):
    @staticmethod
    def classify_by_name(node_name: str, default_type: NodeType = NodeType.RESULT) -> NodeType:
        # 自定义分类逻辑
        if "custom_pattern" in node_name.lower():
            return NodeType.COMMAND
        return super().classify_by_name(node_name, default_type)
```

### Q3: 如何处理类型错误？

使用Pydantic进行验证：

```python
from scripts.definitions import validate_dict_as_node

try:
    node_data = validate_dict_as_node(my_dict)
except ValueError as e:
    print(f"验证失败: {e}")
```
