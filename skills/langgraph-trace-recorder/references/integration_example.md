# LangGraph 集成示例

## 概览

本文档提供LangGraph与轨迹记录器集成的完整示例代码。

## 目录

1. [基础集成](#基础集成)
2. [导出结果](#导出结果)
3. [错误处理](#错误处理)
4. [手动记录推理步骤](#手动记录推理步骤)
5. [自定义配置](#自定义配置)
6. [完整示例](#完整示例)

## 基础集成

### 步骤1：引入Callback Handler

```python
import sys
import os

# 添加scripts目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.callback_handler import create_callback_handler
```

### 步骤2：初始化Handler

```python
# 创建Callback Handler
callback = create_callback_handler(task_id="analysis_task")
```

### 步骤3：编译LangGraph时传入Callback

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from operator import add

# 定义State结构
class State(TypedDict):
    query: str
    response: str
    steps: Annotated[list[str], add]

# 定义节点函数
def query_node(state: State) -> State:
    """查询处理节点"""
    state["response"] = f"处理查询: {state['query']}"
    state["steps"].append("query_processed")
    return state

def analysis_node(state: State) -> State:
    """分析节点"""
    state["response"] += " | 分析完成"
    state["steps"].append("analysis_done")
    return state

# 构建Graph
graph = StateGraph(State)
graph.add_node("query_handler", query_node)
graph.add_node("analyzer", analysis_node)

# 添加边
graph.set_entry_point("query_handler")
graph.add_edge("query_handler", "analyzer")
graph.add_edge("analyzer", END)

# 编译时传入Callback
app = graph.compile(callbacks=[callback])
```

### 步骤4：执行任务

```python
# 执行任务
result = app.invoke({"query": "分析财报", "response": "", "steps": []})

print("执行结果:", result)

# 完成记录
callback.finalize()
```

## 导出结果

### 导出JSON格式

```python
from scripts.graph_exporter import GraphExporter

# 获取图谱
graph = callback.get_graph()

# 创建导出器
exporter = GraphExporter(graph)

# 导出JSON
json_data = exporter.export_json()
print(json_data)

# 保存到文件
with open("trace.json", "w", encoding="utf-8") as f:
    f.write(json_data)
```

### 导出SVG格式

```python
# 导出SVG
svg_content = exporter.export_svg()

# 保存到文件
with open("trace.svg", "w", encoding="utf-8") as f:
    f.write(svg_content)
```

### 导出Markdown格式

```python
# 导出Markdown
md_content = exporter.export_markdown()

# 保存到文件
with open("trace.md", "w", encoding="utf-8") as f:
    f.write(md_content)
```

### 批量导出所有格式

```python
def export_all_formats(graph: KnowledgeGraph, output_dir: str = ".") -> None:
    """导出所有格式"""
    exporter = GraphExporter(graph)

    # 导出JSON
    with open(f"{output_dir}/trace.json", "w", encoding="utf-8") as f:
        f.write(exporter.export_json())

    # 导出SVG
    with open(f"{output_dir}/trace.svg", "w", encoding="utf-8") as f:
        f.write(exporter.export_svg())

    # 导出Markdown
    with open(f"{output_dir}/trace.md", "w", encoding="utf-8") as f:
        f.write(exporter.export_markdown())

# 使用
export_all_formats(graph, output_dir="./output")
```

## 错误处理

### 自动捕获错误信息

LangGraph轨迹记录器会自动捕获节点执行过程中的异常，并记录详细的错误信息：

```python
# 定义一个会抛出异常的节点
def failing_node(state: State) -> State:
    """可能会失败的节点"""
    # 模拟超时错误
    raise TimeoutError("请求超时，无法获取数据")

# 构建Graph
graph = StateGraph(State)
graph.add_node("failing_node", failing_node)
graph.set_entry_point("failing_node")
graph.add_edge("failing_node", END)

# 编译时传入Callback
app = graph.compile(callbacks=[callback])

try:
    # 执行任务（会抛出异常）
    result = app.invoke({"query": "测试", "response": "", "steps": []})
except Exception as e:
    print(f"任务执行失败: {e}")

# 完成记录
callback.finalize()

# 导出结果
exporter = GraphExporter(callback.get_graph())
md_content = exporter.export_markdown()

# 保存报告
with open("error_report.md", "w", encoding="utf-8") as f:
    f.write(md_content)
```

### 失败节点的Markdown报告示例

```markdown
## ⚙️ 命令轨迹

### ❌ 1. failing_node (FAILED)

- **类型**: command
- **状态**: failed
- **时间**: 14:30:25
- **内容**:
```
node: failing_node | input: {"query": "测试"}
```

- **错误类型**: TimeoutError
- **错误消息**: 请求超时，无法获取数据
- **恢复建议**: 建议：增加超时时间配置，或优化查询减少执行时长

- **元数据**:
```json
{
  "status": "failed",
  "input_summary": "{\"query\": \"测试\"}",
  "output_summary": "ERROR: 请求超时，无法获取数据",
  "error_info": {
    "error_type": "TimeoutError",
    "error_message": "请求超时，无法获取数据",
    "stack_trace": "Traceback (most recent call last):\n  ...",
    "recovery_suggestion": "建议：增加超时时间配置，或优化查询减少执行时长",
    "timestamp": 1735689025.0
  }
}
```
```

### SVG中失败节点的可视化

在SVG导出中，失败节点会用红色边框显示，并在右上角显示 ⚠️ 图标：

- 成功节点：蓝色/橙色边框
- 失败节点：红色边框（stroke-width: 3）
- 错误图标：⚠️

### 查询失败节点

```python
from scripts.graph_builder import KnowledgeGraph

graph = callback.get_graph()

# 获取所有失败节点
failed_nodes = [
    node for node in graph._nodes.values()
    if node.get("metadata", {}).get("status") == "failed"
]

print(f"发现 {len(failed_nodes)} 个失败节点:")

for node in failed_nodes:
    error_info = node.get("metadata", {}).get("error_info", {})
    print(f"- {node['label']}: {error_info.get('error_type', 'Unknown')}")
    print(f"  消息: {error_info.get('error_message', 'No message')}")
    print(f"  建议: {error_info.get('recovery_suggestion', 'No suggestion')}")
```

## 手动记录推理步骤

### 使用显式API记录

```python
from scripts.graph_builder import KnowledgeGraph
from scripts.definitions import NodeType, TraceType
import time

# 创建图谱
graph = KnowledgeGraph(task_id="manual_task")

# 记录推理步骤
graph.add_node(
    node_id="reasoning_0",
    node_type=NodeType.REASONING,
    label="决策推理",
    content="我决定先搜索信息，再执行分析",
    trace_type=TraceType.QA_TRACE,
    timestamp=time.time(),
    metadata={
        "context": {
            "query": "分析财报",
            "confidence": 0.95
        }
    }
)

# 记录查询步骤
graph.add_node(
    node_id="query_0",
    node_type=NodeType.QUESTION,
    label="用户查询",
    content="分析公司2023年的财务状况",
    trace_type=TraceType.QA_TRACE,
    timestamp=time.time()
)

# 添加边
graph.add_edge(
    source="reasoning_0",
    target="query_0",
    edge_type=EdgeType.GENERATES
)

# 完成记录
graph.finalize()
```

### 在LangGraph节点中手动记录

```python
def custom_node(state: State) -> State:
    """自定义节点，手动记录推理步骤"""
    # 获取Callback实例
    callback = get_current_callback()  # 需要实现全局获取逻辑

    # 手动记录推理
    graph = callback.get_graph()
    graph.add_node(
        node_id=f"reasoning_{time.time()}",
        node_type=NodeType.REASONING,
        label="推理决策",
        content="根据查询内容，我需要调用搜索工具",
        trace_type=TraceType.QA_TRACE,
        timestamp=time.time()
    )

    # 执行业务逻辑
    state["response"] = "已记录推理步骤"
    return state
```

## 自定义配置

### 使用 Redis 存储后端

当需要分布式部署或数据持久化时，可以使用 Redis 存储后端：

```python
import sys
import os

# 添加scripts目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts import KnowledgeGraph, RedisGraphStorage, create_callback_handler

# 创建Redis存储后端
storage = RedisGraphStorage(
    redis_url="redis://localhost:6379/0",  # Redis连接URL
    key_prefix="langgraph",                 # 键前缀，用于数据隔离
    socket_timeout=5,                       # 连接超时时间（秒）
    socket_connect_timeout=5                # 连接超时时间（秒）
)

# 使用Redis存储后端创建Callback
callback = create_callback_handler(
    task_id="redis_task",
    storage_backend=storage
)

# 编译LangGraph时传入Callback
app = graph.compile(callbacks=[callback])

# 执行任务
result = app.invoke({"query": "测试", "response": "", "steps": []})

# 完成记录
callback.finalize()

# 获取图谱数据
graph = callback.get_graph()

# 导出结果
from scripts.graph_exporter import GraphExporter
exporter = GraphExporter(graph)
md_content = exporter.export_markdown()

# 保存报告
with open("trace.md", "w", encoding="utf-8") as f:
    f.write(md_content)

# 关闭Redis连接
graph.close()
```

**Redis数据结构**：

| Redis键类型 | 键名格式 | 说明 |
|-------------|---------|------|
| Hash | `langgraph:node:{node_id}` | 节点数据（JSON） |
| Sorted Set | `langgraph:node:timeline` | 节点时间索引（score=timestamp） |
| Set | `langgraph:node:type:{type}` | 节点类型索引 |
| Set | `langgraph:node:status:{status}` | 节点状态索引 |
| Set | `langgraph:node:trace_type:{type}` | 节点轨迹类型索引 |
| List | `langgraph:edges` | 边数据列表 |
| List | `langgraph:edge:source:{node_id}` | 边源索引 |
| List | `langgraph:edge:target:{node_id}` | 边目标索引 |
| String | `langgraph:cache:{format}` | 导出缓存（TTL=3600s） |

**Redis性能特点**：

- 查询性能：O(1) 索引查询（与内存存储相当）
- 写入性能：比内存存储稍慢（网络延迟）
- 持久化：数据自动持久化，重启不丢失
- 分布式：支持多进程共享数据

**何时使用Redis存储**：

✅ **推荐使用Redis的场景**：
- 需要多个进程共享数据
- 需要数据持久化，重启不丢失
- 需要跨服务器部署
- 需要长期存储历史轨迹

❌ **不推荐使用Redis的场景**：
- 单机临时测试
- 数据量小且无需持久化
- 对写入性能要求极高（<1ms）

### 自定义节点分类规则

```python
from scripts.classifier import NodeClassifier
from scripts.definitions import NodeType

class CustomNodeClassifier(NodeClassifier):
    """自定义节点分类器"""

    @staticmethod
    def classify_by_name(node_name: str, default_type: NodeType = NodeType.RESULT) -> NodeType:
        """自定义分类逻辑"""
        # 示例：如果节点名包含"search"，归类为命令类型
        if "search" in node_name.lower():
            return NodeType.COMMAND

        # 示例：如果节点名包含"explain"，归类为回答类型
        if "explain" in node_name.lower():
            return NodeType.ANSWER

        # 使用默认分类逻辑
        return super().classify_by_name(node_name, default_type)

# 使用自定义分类器
from scripts.callback_handler import TraceRecorderCallback

callback = TraceRecorderCallback()
callback._classifier = CustomNodeClassifier()
```

### 自定义元数据

```python
# 在Callback中自定义元数据收集
callback = create_callback_handler(task_id="custom_task")

# 执行任务后，添加自定义元数据
graph = callback.get_graph()
graph.get_metadata()["custom_field"] = "custom_value"

# 或者修改节点的元数据
node = graph.get_node("node_0")
if node:
    node["metadata"]["user_id"] = "user_123"
    node["metadata"]["session_id"] = "session_456"
```

## 完整示例

### 示例1：完整的LangGraph应用

```python
#!/usr/bin/env python3
"""
LangGraph轨迹记录完整示例
"""

import sys
import os
import json

# 添加scripts目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from operator import add

from scripts.callback_handler import create_callback_handler
from scripts.graph_exporter import GraphExporter


class State(TypedDict):
    """应用State"""
    query: str
    response: str
    steps: Annotated[list[str], add]


def query_handler(state: State) -> State:
    """查询处理节点"""
    print(f"[query_handler] 处理查询: {state['query']}")
    state["response"] = f"收到查询: {state['query']}"
    state["steps"].append("query_processed")
    return state


def analyzer(state: State) -> State:
    """分析节点"""
    print(f"[analyzer] 分析查询")
    state["response"] += " | 分析完成"
    state["steps"].append("analysis_done")
    return state


def tool_executor(state: State) -> State:
    """工具执行节点"""
    print(f"[tool_executor] 执行工具")
    state["response"] += " | 工具执行完成"
    state["steps"].append("tool_executed")
    return state


def main() -> None:
    """主函数"""
    # 创建Callback Handler
    callback = create_callback_handler(task_id="demo_task")

    # 构建Graph
    graph = StateGraph(State)
    graph.add_node("query_handler", query_handler)
    graph.add_node("analyzer", analyzer)
    graph.add_node("tool_executor", tool_executor)

    # 添加边
    graph.set_entry_point("query_handler")
    graph.add_edge("query_handler", "analyzer")
    graph.add_edge("analyzer", "tool_executor")
    graph.add_edge("tool_executor", END)

    # 编译并传入Callback
    app = graph.compile(callbacks=[callback])

    # 执行任务
    print("=" * 50)
    print("开始执行LangGraph任务")
    print("=" * 50)

    result = app.invoke({
        "query": "分析公司2023年财报",
        "response": "",
        "steps": []
    })

    print("=" * 50)
    print("任务执行完成")
    print("=" * 50)
    print(f"结果: {result}")

    # 完成记录
    callback.finalize()

    # 导出结果
    print("=" * 50)
    print("导出轨迹数据")
    print("=" * 50)

    graph = callback.get_graph()
    exporter = GraphExporter(graph)

    # 导出JSON
    json_data = exporter.export_json()
    with open("output/trace.json", "w", encoding="utf-8") as f:
        f.write(json_data)
    print("✓ JSON已导出到 output/trace.json")

    # 导出SVG
    svg_content = exporter.export_svg()
    with open("output/trace.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    print("✓ SVG已导出到 output/trace.svg")

    # 导出Markdown
    md_content = exporter.export_markdown()
    with open("output/trace.md", "w", encoding="utf-8") as f:
        f.write(md_content)
    print("✓ Markdown已导出到 output/trace.md")

    # 打印统计信息
    metadata = graph.get_metadata()
    print("\n" + "=" * 50)
    print("执行统计")
    print("=" * 50)
    print(f"任务ID: {metadata['task_id']}")
    print(f"节点总数: {metadata['total_nodes']}")
    print(f"边总数: {metadata['total_edges']}")
    print(f"问答轨迹节点数: {metadata['qa_trace_count']}")
    print(f"命令轨迹节点数: {metadata['command_trace_count']}")


if __name__ == "__main__":
    # 创建输出目录
    os.makedirs("output", exist_ok=True)

    # 执行主函数
    main()
```

### 示例2：手动构建图谱

```python
#!/usr/bin/env python3
"""
手动构建知识图谱示例
"""

import sys
import os
import time

# 添加scripts目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.graph_builder import KnowledgeGraph
from scripts.graph_exporter import GraphExporter
from scripts.definitions import NodeType, EdgeType, TraceType


def main() -> None:
    """主函数"""
    # 创建图谱
    graph = KnowledgeGraph(task_id="manual_demo")

    # 添加推理节点
    graph.add_node(
        node_id="reasoning_0",
        node_type=NodeType.REASONING,
        label="决策推理",
        content="我决定先搜索信息，再执行分析",
        trace_type=TraceType.QA_TRACE,
        timestamp=time.time(),
        metadata={
            "confidence": 0.95
        }
    )

    # 添加问题节点
    graph.add_node(
        node_id="question_0",
        node_type=NodeType.QUESTION,
        label="用户查询",
        content="分析公司2023年财报",
        trace_type=TraceType.QA_TRACE,
        timestamp=time.time() + 1
    )

    # 添加回答节点
    graph.add_node(
        node_id="answer_0",
        node_type=NodeType.ANSWER,
        label="模型回答",
        content="需要先获取财报数据，然后进行财务指标分析",
        trace_type=TraceType.QA_TRACE,
        timestamp=time.time() + 2
    )

    # 添加命令节点
    graph.add_node(
        node_id="command_0",
        node_type=NodeType.COMMAND,
        label="下载财报",
        content="执行download_pdf工具，下载2023年财报PDF",
        trace_type=TraceType.COMMAND_TRACE,
        timestamp=time.time() + 3
    )

    # 添加结果节点
    graph.add_node(
        node_id="result_0",
        node_type=NodeType.RESULT,
        label="下载结果",
        content="成功下载财报PDF，文件大小5.2MB",
        trace_type=TraceType.COMMAND_TRACE,
        timestamp=time.time() + 4
    )

    # 添加边
    graph.add_edge("reasoning_0", "question_0", EdgeType.GENERATES)
    graph.add_edge("question_0", "answer_0", EdgeType.GENERATES)
    graph.add_edge("answer_0", "command_0", EdgeType.EXECUTES)
    graph.add_edge("command_0", "result_0", EdgeType.GENERATES)

    # 完成记录
    graph.finalize()

    # 导出结果
    os.makedirs("output", exist_ok=True)

    exporter = GraphExporter(graph)

    # 导出JSON
    with open("output/manual_trace.json", "w", encoding="utf-8") as f:
        f.write(exporter.export_json())
    print("✓ JSON已导出")

    # 导出SVG
    with open("output/manual_trace.svg", "w", encoding="utf-8") as f:
        f.write(exporter.export_svg())
    print("✓ SVG已导出")

    # 导出Markdown
    with open("output/manual_trace.md", "w", encoding="utf-8") as f:
        f.write(exporter.export_markdown())
    print("✓ Markdown已导出")


if __name__ == "__main__":
    main()
```

## 常见问题

### Q1: Callback没有捕获到节点执行？

检查以下几点：
1. 确认在编译Graph时传入了`callbacks=[callback]`
2. 确认节点函数有正确的类型注解
3. 检查LangGraph版本是否支持Callback机制

### Q2: SVG显示乱码？

确保SVG文件以UTF-8编码保存：

```python
with open("trace.svg", "w", encoding="utf-8") as f:
    f.write(svg_content)
```

### Q3: 如何在现有LangGraph应用中集成？

只需在编译Graph时添加Callback参数，无需修改其他代码：

```python
# 原代码
app = graph.compile()

# 修改后
from scripts.callback_handler import create_callback_handler
callback = create_callback_handler()
app = graph.compile(callbacks=[callback])
```

### Q4: 如何处理大规模执行轨迹？

使用增量构建模式，定期导出中间结果：

```python
import time

# 定期导出
def periodic_export(graph: KnowledgeGraph, interval: int = 60) -> None:
    """定期导出图谱"""
    while True:
        time.sleep(interval)
        exporter = GraphExporter(graph)
        with open(f"trace_{int(time.time())}.json", "w") as f:
            f.write(exporter.export_json())

# 在后台线程中运行
import threading
export_thread = threading.Thread(target=periodic_export, args=(graph, 60))
export_thread.daemon = True
export_thread.start()
```
