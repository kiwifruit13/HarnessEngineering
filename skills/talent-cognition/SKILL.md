---
name: talent-cognition
description: 基于任务特征为模型定制最契合的天赋Prompt；当用户需要任务适配、多阶段优化、LangGraph状态注入或动态天赋配置时使用
dependency:
  python:
    - PyYAML
  system: []
---

# Talent Cognition - 天赋认知系统

## 任务目标
本系统通过分析任务特征，智能匹配最佳天赋，动态生成定制化Prompt，帮助模型更精准地完成任务。支持单阶段和多阶段两种模式，深度集成LangGraph状态机制，在合适的时机注入定制Prompt。

适用场景：
- 任务适配优化：为不同类型任务匹配最合适的模型行为模式
- 多阶段流程控制：在任务的不同阶段注入不同的Prompt策略
- LangGraph工作流集成：无侵入式地增强状态图的节点能力
- 动态配置管理：通过外部配置文件灵活管理天赋定义

---

## 快速开始

### 单阶段模式（5行代码）
```python
from scripts.task_feature_extractor import TaskFeatureExtractor
from scripts.talent_matcher import TalentMatcher
from scripts.talent_customizer import TalentCustomizer

# 1. 提取任务特征
feature = TaskFeatureExtractor.extract("分析Python代码的性能瓶颈")

# 2. 匹配最佳天赋
talent = TalentMatcher.match_best(feature)

# 3. 生成定制Prompt
custom_prompt = TalentCustomizer.customize(feature, talent)

# 4. 注入到模型上下文
model.generate(custom_prompt)
```

### 多阶段模式（完整集成）
```python
from scripts.multi_stage_customizer import MultiStageCustomizer

# 创建多阶段定制器
customizer = MultiStageCustomizer()

# 为任务的所有阶段定制Prompt
prompts = customizer.customize_all_stages(
    task_description="开发一个高性能API服务",
    feature=feature
)

# prompts = {
#     "PLANNING": "规划阶段的定制Prompt...",
#     "EXECUTION": "执行阶段的定制Prompt...",
#     "OPTIMIZATION": "优化阶段的定制Prompt...",
#     "REVIEW": "审查阶段的定制Prompt..."
# }
```

### LangGraph集成（自动注入）
```python
from scripts.langgraph_guardrail import create_talent_guardrail

# 创建状态图
workflow = StateGraph(TaskState)

# 添加天赋注入节点（在任务节点之前）
workflow.add_node("talent_injector", create_talent_guardrail())
workflow.add_node("task_processor", process_task)

# 添加边
workflow.add_edge("talent_injector", "task_processor")
```

---

## 操作步骤

### 场景1：基础使用（单阶段注入）

**步骤1：任务特征提取**
```python
from scripts.task_feature_extractor import TaskFeatureExtractor

feature = TaskFeatureExtractor.extract("你的任务描述")
```
- 自动提取7个维度特征：任务类型、复杂度、领域、风格、输出格式、时间约束、质量要求

**步骤2：天赋匹配**
```python
from scripts.talent_matcher import TalentMatcher

talent = TalentMatcher.match_best(feature)
```
- 使用加权评分算法匹配最佳天赋
- 返回最匹配的天赋对象及其匹配分数

**步骤3：Prompt定制**
```python
from scripts.talent_customizer import TalentCustomizer

custom_prompt = TalentCustomizer.customize(feature, talent)
```
- 基于任务特征动态生成定制Prompt
- 包含任务描述、特征约束、天赋赋能、输出规范

**步骤4：使用定制Prompt**
```python
# 直接传递给模型
response = model.generate(custom_prompt)
```

---

### 场景2：多阶段注入（复杂任务）

**步骤1：识别任务阶段**
```python
from scripts.task_stage import TaskStage

# 系统会自动识别任务涉及的阶段
stages = [TaskStage.PLANNING, TaskStage.EXECUTION, TaskStage.REVIEW]
```

**步骤2：多阶段定制**
```python
from scripts.multi_stage_customizer import MultiStageCustomizer

customizer = MultiStageCustomizer()
prompts = customizer.customize_all_stages(
    task_description="开发一个完整的数据分析系统",
    feature=feature
)
```
- 为每个阶段独立匹配天赋并定制Prompt
- 返回字典形式的Prompt集合

**步骤3：分阶段注入**
```python
# 在LangGraph工作流中使用
state["planning_prompt"] = prompts["PLANNING"]
state["execution_prompt"] = prompts["EXECUTION"]
state["review_prompt"] = prompts["REVIEW"]
```

---

### 场景3：使用外部配置（灵活管理）

**步骤1：准备配置文件**
创建 `custom-talents.yaml`（参考 [assets/custom-talents.yaml](assets/custom-talents.yaml)）

**步骤2：加载外部天赋库**
```python
from scripts.talent_loader import TalentLoader

loader = TalentLoader()
loader.load_from_yaml("./custom-talents.yaml")
```

**步骤3：使用加载的天赋**
```python
# 后续的匹配和定制流程会自动使用加载的天赋库
talent = TalentMatcher.match_best(feature)
```

---

### 场景4：LangGraph深度集成

**步骤1：定义State结构**
```python
from typing import TypedDict

class TaskState(TypedDict):
    task_description: str
    # 单阶段模式
    talent_prompt: str
    # 多阶段模式
    planning_prompt: Optional[str]
    execution_prompt: Optional[str]
    optimization_prompt: Optional[str]
    review_prompt: Optional[str]
    result: str
```

**步骤2：创建Guardrail节点**
```python
from scripts.langgraph_guardrail import create_talent_guardrail

workflow = StateGraph(TaskState)
workflow.add_node("talent_injector", create_talent_guardrail())
```

**步骤3：构建工作流**
```python
workflow.add_node("task_processor", process_task)
workflow.add_edge("talent_injector", "task_processor")
workflow.set_entry_point("talent_injector")
workflow.set_finish_point("task_processor")
```

**步骤4：执行并获取结果**
```python
graph = workflow.compile()
state = {
    "task_description": "分析Python代码性能",
    "task_mode": "single_stage"
}
result = graph.invoke(state)
```

---

## 资源索引

### 核心脚本
1. [scripts/task_feature_extractor.py](scripts/task_feature_extractor.py) - 任务特征提取器，从任务描述中提取7个维度特征
2. [scripts/talent_matcher.py](scripts/talent_matcher.py) - 天赋匹配器，使用加权评分算法匹配最佳天赋
3. [scripts/talent_customizer.py](scripts/talent_customizer.py) - Prompt定制器，动态生成定制化Prompt
4. [scripts/multi_stage_customizer.py](scripts/multi_stage_customizer.py) - 多阶段定制器，支持4个阶段的独立定制
5. [scripts/talent_loader.py](scripts/talent_loader.py) - 天赋加载器，支持从YAML/JSON加载外部配置
6. [scripts/task_stage.py](scripts/task_stage.py) - 任务阶段定义，定义4个标准阶段常量

### 集成工具
- [scripts/langgraph_guardrail.py](scripts/langgraph_guardrail.py) - LangGraph状态集成，提供Guardrail节点创建函数

### 参考文档
- [references/system-overview.md](references/system-overview.md) - 全局概览，包含系统架构、知识图谱、流程图等详细设计文档

### 配置资源
- [assets/custom-talents.yaml](assets/custom-talents.yaml) - 外部配置示例，展示如何定义自定义天赋

---

## 关键API调用声明

### 1. 单阶段模式API
```python
from scripts.task_feature_extractor import TaskFeatureExtractor
from scripts.talent_matcher import TalentMatcher
from scripts.talent_customizer import TalentCustomizer

# 提取任务特征
feature = TaskFeatureExtractor.extract("任务描述")

# 匹配最佳天赋
talent = TalentMatcher.match_best(feature)

# 生成定制Prompt
custom_prompt = TalentCustomizer.customize(feature, talent)
```

### 2. 多阶段模式API
```python
from scripts.multi_stage_customizer import MultiStageCustomizer

customizer = MultiStageCustomizer()

# 为所有阶段定制Prompt
prompts = customizer.customize_all_stages(
    task_description="任务描述",
    feature=feature
)

# 为单个阶段定制
planning_prompt = customizer.customize_stage(
    stage=TaskStage.PLANNING,
    task_description="任务描述",
    feature=feature
)
```

### 3. 动态天赋库API
```python
from scripts.talent_loader import TalentLoader

loader = TalentLoader()

# 从YAML加载
loader.load_from_yaml("custom-talents.yaml")

# 从JSON加载
loader.load_from_json("custom-talents.json")

# 获取所有天赋
all_talents = loader.get_all_talents()

# 按领域查询
tech_talents = loader.get_talents_by_domain("technology")
```

### 4. LangGraph集成API
```python
from scripts.langgraph_guardrail import create_talent_guardrail

# 创建Guardrail节点
guardrail_node = create_talent_guardrail()

# 集成到工作流
workflow.add_node("talent_injector", guardrail_node)
workflow.add_edge("talent_injector", "task_processor")
```

---

## 注意事项

### 系统设计原则
1. **特征驱动**：基于任务的多维度特征进行匹配，而非简单关键词匹配
2. **本地计算**：所有特征提取和匹配都在本地完成，不调用任何外部API
3. **无侵入集成**：作为附加属性注入State，不影响原有流程
4. **灵活配置**：支持通过外部配置文件管理天赋定义

### 性能考虑
- 特征提取：O(n)，n为任务描述长度
- 天赋匹配：O(m)，m为天赋库大小
- 建议：天赋库大小控制在100个以内以保证性能

### 扩展建议
- 自定义匹配算法：继承 `TalentMatcher` 实现自定义评分逻辑
- 新增特征维度：扩展 `TaskFeature` 类添加新的特征字段
- 自定义Prompt模板：在外部配置文件中定义自定义模板

### 最佳实践
1. 先从单阶段模式开始，熟悉后再使用多阶段模式
2. 使用外部配置文件管理天赋定义，便于维护和更新
3. 在LangGraph集成时，将天赋注入节点作为入口节点
4. 定期评估匹配效果，调整天赋权重和模板

---

## 深入学习

想要了解系统的详细设计、架构原理和实现细节，请查看：
- **[全局概览文档](references/system-overview.md)** - 包含完整的系统架构、知识图谱、流程图和关键决策说明

---

## 快速参考

### 任务特征维度
| 维度 | 说明 | 取值范围 |
|------|------|---------|
| task_type | 任务类型 | 分析/创作/问答/编程/翻译/总结/推理 |
| complexity | 复杂度 | 1-5分 |
| domain | 领域 | 通用/技术/创意/商业/学术 |
| style | 风格 | 正式/简洁/详细/创意/专业 |
| output_format | 输出格式 | 文本/代码/列表/结构化数据 |
| time_constraint | 时间约束 | 紧急/正常/宽松 |
| quality_requirement | 质量要求 | 高/中/低 |

### 任务阶段
| 阶段 | 说明 | 适用场景 |
|------|------|---------|
| PLANNING | 规划阶段 | 任务分解、策略制定 |
| EXECUTION | 执行阶段 | 核心任务执行 |
| OPTIMIZATION | 优化阶段 | 结果优化、迭代改进 |
| REVIEW | 审查阶段 | 质量检查、问题识别 |

### 配置文件格式
参考 [assets/custom-talents.yaml](assets/custom-talents.yaml) 了解详细配置规范。
