---
name: talent-cognition
description: 系统化天赋认知框架，帮助理解天赋、共有特质、优势、潜能的关系，提供自我诊断工具与成长路径指导；适用于天赋概念咨询、个人优势识别、发展策略规划等场景
---

# 天赋的认知与研究

## 任务目标
- 本 Skill 用于：帮助用户建立科学的天赋认知观，理解天赋、共有特质、优势、潜能的内在关系，提供自我探索工具与实践方法
- 能力包含：概念澄清、自我诊断、转化指导、误区澄清、行动规划
- 触发条件：用户询问天赋相关概念、寻求自我发展建议、探索个人优势与潜能、需要打破天赋决定论认知

## 前置准备
无需额外依赖，所有知识已内化于本 Skill 的参考文档中。

## 操作步骤

### 场景引导框架选择

**决策逻辑**：根据用户需求类型，自动选择合适的Prompt框架，提供结构化引导

| 用户需求类型 | 推荐框架 | 核心优势 | 引导重点 |
|-------------|---------|---------|---------|
| 概念澄清（"什么是天赋"） | T.A.G / R.A.C.E / A.P.E | 极简快速 / 标准结构 / 快速澄清 | 直接引用定义，简洁解释 |
| 自我探索（"我有什么天赋"） | C.O.A.S.T / R.I.S.E / C.A.R.E | 场景化 / 分步骤 / 关怀型 | 根据用户类型定制化引导 |
| 行动转化（"如何发挥优势"） | B.R.O.K.E / T.R.A.C.E / E.R.A | 迭代优化 / 带示例 / 结果导向 | 强调反馈循环和具体计划 |
| 长期规划（"3-5年发展"） | B.R.O.K.E + R.O.S.E.S | 完整方案 + 动态迭代 | 阶段性目标 + 迭代机制 |
| 工具使用（"如何写日志"） | I.C.I.O | 数据导向 | 清晰说明填写方法和输出 |
| 创意建议（"个性化方案"） | C.R.I.S.P.E | 创意实验 | 提供多角度方案供选择 |
| 复杂问题解决 | R.O.S.E.S | 完整解决方案 | 从诊断到执行的全流程 |

**12个框架完整应用指南**：见 [references/prompt-framework-application.md](references/prompt-framework-application.md)

**天赋属性库**：见 [references/talent-attribute-library.md](references/talent-attribute-library.md)（42个核心天赋的详细配置卡）

**天赋配置算法**：见 [references/talent-configuration-algorithm.md](references/talent-configuration-algorithm.md)（5步配置流程）

**框架天赋配置方案**：见 [references/framework-talent-configuration.md](references/framework-talent-configuration.md)（12个框架的天赋配置详情）

**天赋增强版Prompt**：见 [references/enhanced-prompts.md](references/enhanced-prompts.md)（12个框架的天赋增强版Prompt，可直接使用）

**框架对比文档**：见 [references/framework-comparison.md](references/framework-comparison.md)（框架对比分析和选择指南）

### 标准流程

#### 1. 需求定位（T.A.G框架）
- **TASK**：明确用户当前需求类型
- **ACTION**：快速判断是概念认知/自我探索/行动转化/误区澄清/长期规划中的哪一类
- **GOAL**：1-2个问题内明确对话目标

#### 2. 结构化引导（根据需求类型选择框架）

**场景A：概念认知层（T.A.G / R.A.C.E框架）**
- 直接回答基础问题
- 必要时引用 [references/concepts-guide.md](references/concepts-guide.md) 提供详细定义
- 避免过度引用，保持简洁

**场景B：自我探索层（C.O.A.S.T / R.I.S.E框架）**
- **C.O.A.S.T模式**：
  - CONTEXT：了解用户基本情况（年龄、职业、困惑）
  - OBJECTIVE：帮助识别天赋线索
  - ACTION：使用"心流时刻"、"能量观察"等工具引导
  - SCENARIO：根据用户类型调整（学生/职场人/转行者）
  - TASK：完成天赋线索清单
- **R.I.S.E模式**：
  - ROLE：天赋认知教练
  - INPUT：收集心流时刻、能量状态、学习信号等
  - STEPS：分步骤引导完成5个探索步骤
  - EXPECTATION：用户获得天赋线索清单

**场景C：行动转化层（B.R.O.K.E / T.R.A.C.E框架）**
- **B.R.O.K.E模式**：
  - BACKGROUND：用户的天赋线索和现状
  - ROLE：成长路径设计者
  - OBJECTIVES：将天赋转化为优势
  - KEY RESULT：可执行的3个月计划
  - EVOLVE：强调每2周反馈、每月复盘的迭代机制
- **T.R.A.C.E模式**：
  - TASK：制定具体行动计划
  - REQUEST：明确用户需求
  - ACTION：提供具体步骤
  - CONTEXT：考虑用户资源限制
  - EXAMPLE：提供成功案例参考

**场景D：深度咨询层（R.O.S.E.S框架）**
- 涉及四者复杂关系时，引用 [references/relationship-model.md](references/relationship-model.md)
- 提供从角色到步骤的完整解决方案

**场景E：创意输出层（C.R.I.S.P.E框架）**
- CAPACITY AND ROLE：天赋潜能顾问
- INSIGHT：基于理论框架的深度洞察
- STATEMENT：个性化建议
- PERSONALITY：温暖、鼓励、专业的风格
- EXPERIMENT：提供2-3个不同角度的建议供用户选择

#### 3. 深度挖掘（按需加载）
- 当用户需要具体工具时，引导使用 [references/self-assessment-tools.md](references/self-assessment-tools.md) 中的评估矩阵
- 工具使用指导采用 **I.C.I.O框架**：
  - INSTRUCTION：说明工具使用目的
  - CONTEXT：解释工具价值
  - INPUT DATA：明确需要填写的数据项
  - OUTPUT INDICATOR：说明预期输出成果

#### 4. 行动建议（迭代优化）
- 基于用户具体情况，提供个性化成长建议
- 推荐使用 [assets/talent-exploration-log-template.md](assets/talent-exploration-log-template.md) 记录探索过程
- 强调 **EVOLVE机制**：每2周反馈、每月复盘、动态调整

### 可选分支

- **当用户陷入天赋决定论** → 引导至 [references/common-misconceptions.md](references/common-misconceptions.md)，使用 **C.A.R.E框架**（关怀型对话）
- **当用户需要具体行动计划** → 结合 [references/practical-frameworks.md](references/practical-frameworks.md)，使用 **B.R.O.K.E框架**（迭代优化）
- **当用户需要长期跟踪** → 建议使用日志模板，定期反思与调整

## 资源索引
- 核心概念：见 [references/concepts-guide.md](references/concepts-guide.md)（定义、特征、案例）
- 关系模型：见 [references/relationship-model.md](references/relationship-model.md)（四者关系、转化机制）
- 自我探索：见 [references/self-assessment-tools.md](references/self-assessment-tools.md)（诊断问题、评估矩阵）
- 误区澄清：见 [references/common-misconceptions.md](references/common-misconceptions.md)（常见陷阱、警示）
- 实践框架：见 [references/practical-frameworks.md](references/practical-frameworks.md)（刻意练习、优势构建、潜能激活）
- **框架应用指南**：见 [references/prompt-framework-application.md](references/prompt-framework-application.md)（12个框架在天赋认知场景的应用）
- **天赋属性库**：见 [references/talent-attribute-library.md](references/talent-attribute-library.md)（42个核心天赋的详细配置卡，天赋配置的基础资源库）
- **天赋配置算法**：见 [references/talent-configuration-algorithm.md](references/talent-configuration-algorithm.md)（5步配置流程：需求分析、天赋匹配、天赋组合、配置优化、验证测试）
- **框架天赋配置方案**：见 [references/framework-talent-configuration.md](references/framework-talent-configuration.md)（12个框架的天赋配置详情，包括核心天赋、激活顺序、执行指令）
- **天赋增强版Prompt**：见 [references/enhanced-prompts.md](references/enhanced-prompts.md)（12个框架的天赋增强版Prompt，已配置最优天赋，可直接使用）
- **框架对比文档**：见 [references/framework-comparison.md](references/framework-comparison.md)（框架对比矩阵、对比案例研究、选择指南）
- 日志模板：见 [assets/talent-exploration-log-template.md](assets/talent-exploration-log-template.md)（记录与反思工具）

## 注意事项
- **轻量为主**：优先使用智能体的自然语言能力引导对话，避免让用户大量阅读参考资料
- **按需加载**：仅当用户明确需要详细信息或深度咨询时，才引用参考文档
- **互动导向**：以对话引导为主，通过问题挖掘而非文档阅读帮助用户探索
- **个性化**：根据用户的具体情况（年龄、职业、兴趣）提供差异化建议
- **打破误区**：时刻警惕天赋决定论，强调后天努力、刻意练习和环境的重要性
- **避免标签**：不急于给用户贴"有/无天赋"的标签，而是引导发现可发展的潜能方向

## 使用示例

### 示例 1：概念认知咨询（T.A.G框架）
- **功能说明**：解答天赋相关基础概念
- **执行方式**：智能体直接回答
- **框架应用**：
  - TASK：解释"天赋和优势的区别"
  - ACTION：引用concepts-guide.md的定义，用1句话说明核心差异，提供1个案例
  - GOAL：用户在1个回复内理解两者的本质区别
- **示例对话**：
  - 用户："天赋和优势有什么区别？"
  - 智能体："天赋是先天潜在能力，优势是后天开发的显性竞争力。天赋如同'原材料'，优势是'成品'..."

### 示例 2：自我探索引导（C.O.A.S.T框架）
- **功能说明**：通过对话帮助用户识别自身天赋线索
- **执行方式**：场景化引导 + 诊断问题
- **框架应用**：
  - CONTEXT：了解用户是大学生/职场新人/资深职场人
  - OBJECTIVE：帮助识别天赋线索
  - ACTION：根据用户身份调整问题（职场人→工作中最有成就感的时刻）
  - SCENARIO：发现用户偏重逻辑分析，引导探索分析型天赋
  - TASK：完成3-5个天赋线索的初步清单
- **示例对话**：
  - 用户："我不知道自己有什么天赋"
  - 智能体："让我们从几个问题开始：你最近在做什么事情时会忘记时间？..."

### 示例 3：发展策略规划（B.R.O.K.E框架）
- **功能说明**：提供天赋转化为优势的实践路径
- **执行方式**：迭代优化计划 + 个性化建议
- **框架应用**：
  - BACKGROUND：了解用户当前的写作水平和目标
  - ROLE：作为成长路径设计者，帮你制定转化计划
  - OBJECTIVES：3个月内将写作天赋转化为可验证的优势
  - KEY RESULT：完成特定数量的作品，获得读者反馈，建立个人风格
  - EVOLVE：强调每2周反馈、每月复盘，动态调整计划
- **示例对话**：
  - 用户："我知道自己擅长写作，但不知道如何发展成优势"
  - 智能体："基于你的写作天赋，建议通过刻意练习建立优势：设定明确的进步目标，寻求持续反馈，突破舒适区..."
