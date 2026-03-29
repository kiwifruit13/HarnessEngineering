---
name: intelligent-environment-adapter
description: 智能编排技能组合方案；当智能体需要处理复杂任务、评估能力边界或获取最优技能编排方案时使用
dependency:
  python: []
  system: []
---

# 智能环境适配器

## 任务目标
- 本 Skill 用于：分析用户任务特征，评估当前skills与任务需求的匹配度，识别能力短板，设计最优技能编排方案
- 能力包含：环境感知、能力映射、短板诊断、补齐决策、编排规划、技能组合、执行监控、动态调整
- 触发条件：智能体处理复杂任务前、发现任务需要特定领域知识、需要评估当前能力是否充足

---

## 模块化架构

本适配器采用**模块化设计**，共包含8个独立模块，职责明确、边界清晰。

### 模块列表

| 模块 | 名称 | 职责 | 边界 |
|------|------|------|------|
| **A** | 环境感知 | 分析任务特征，生成环境画像 | 不涉及能力评估 |
| **B** | 能力映射 | 计算匹配度，识别能力断点 | 不生成诊断报告 |
| **C** | 短板诊断 | 生成详细诊断报告 | 不选择补齐策略 |
| **D** | 补齐决策 | 选择补齐策略，生成计划 | 不涉及编排规划 |
| **E** | 编排规划 | 设计技能编排方案 | 不涉及技能匹配 |
| **F** | 技能组合 | 生成可执行的技能组合 | 不执行 |
| **G** | 执行监控 | 接收执行状态，判断调整需求 | 不执行调整 |
| **H** | 动态调整 | 生成调整方案 | 不执行调整 |

### 核心原则

```
原则1：单一职责 - 每个模块只做一件事
原则2：明确边界 - 模块间通过数据文件交互
原则3：无交叉调用 - 模块间不直接调用
原则4：只输出方案 - 所有模块只输出建议，不执行
```

---

## 数据流

```
任务描述
    ↓
[模块A] 环境感知 → environment_profile.json
    ↓
[模块B] 能力映射 → mapping_result.json
    ↓
[模块C] 短板诊断 → diagnostic_report.json
    ↓
[模块D] 补齐决策 → remediation_plan.json
    ↓
[模块E] 编排规划 → orchestration_plan.json
    ↓
[模块F] 技能组合 → orchestration_result.json
    ↓
    输出给智能体
    ↓
智能体执行 → execution_status.json
    ↓
[模块G] 执行监控 → adjustment_suggestion.json
    ↓
[模块H] 动态调整 → adjustment_plan.json
    ↓
    输出给智能体继续执行
```

---

## 前置准备
- 依赖说明：本 Skill 的脚本仅使用 Python 标准库（json, typing, argparse, pathlib），无需额外安装
- 非标准文件/文件夹准备：无

---

## 操作步骤

### 标准流程（初次编排）

#### 1. 环境感知（模块A）
```bash
python scripts/modules/environment_perceiver.py \
    --task-description "分析2025年AI法律监管政策趋势" \
    --output environment_profile.json
```

#### 2. 能力映射（模块B）
```bash
python scripts/modules/capability_mapper.py \
    --environment-profile environment_profile.json \
    --capability-registry capability_registry.json \
    --output mapping_result.json
```

#### 3. 短板诊断（模块C）
```bash
python scripts/modules/shortage_diagnoser.py \
    --mapping-result mapping_result.json \
    --environment-profile environment_profile.json \
    --output diagnostic_report.json
```

#### 4. 补齐决策（模块D）
```bash
python scripts/modules/remediation_decider.py \
    --diagnostic-report diagnostic_report.json \
    --environment-profile environment_profile.json \
    --output remediation_plan.json
```

#### 5. 编排规划（模块E）
```bash
python scripts/modules/orchestration_planner.py \
    --remediation-plan remediation_plan.json \
    --environment-profile environment_profile.json \
    --output orchestration_plan.json
```

#### 6. 技能组合（模块F）
```bash
python scripts/modules/skill_composer.py \
    --orchestration-plan orchestration_plan.json \
    --available-skills available_skills.json \
    --output orchestration_result.json
```

---

### 动态调整流程（执行中）

当智能体执行编排方案遇到问题时：

#### 1. 执行监控（模块G）
```bash
python scripts/modules/execution_monitor.py \
    --execution-status execution_status.json \
    --orchestration-plan orchestration_plan.json \
    --output adjustment_suggestion.json
```

#### 2. 动态调整（模块H）
```bash
python scripts/modules/dynamic_adjuster.py \
    --execution-status execution_status.json \
    --adjustment-suggestion adjustment_suggestion.json \
    --orchestration-plan orchestration_plan.json \
    --output adjustment_plan.json
```

#### 3. 回溯处理（如需要）

如果模块H输出 `revisit_request`，智能体可以决定是否回溯：

```json
{
  "revisit_request": {
    "action": "revisit_diagnosis",
    "target_module": "shortage_diagnosis",
    "reason": "发现新的能力短板"
  }
}
```

智能体执行回溯：
```bash
# 重新调用模块C
python scripts/modules/shortage_diagnoser.py \
    --mapping-result mapping_result.json \
    --environment-profile environment_profile.json \
    --previous-diagnostic previous_diagnostic.json \
    --output updated_diagnostic.json
```

---

## 可选分支

- **匹配度 >= 0.85**：直接输出基础编排方案
- **0.60 <= 匹配度 < 0.85**：生成完整编排方案 + 补齐建议
- **匹配度 < 0.60**：输出降级方案或建议重新定义任务

---

## 资源索引

### 模块脚本
- `scripts/modules/environment_perceiver.py`：模块A - 环境感知
- `scripts/modules/capability_mapper.py`：模块B - 能力映射
- `scripts/modules/shortage_diagnoser.py`：模块C - 短板诊断
- `scripts/modules/remediation_decider.py`：模块D - 补齐决策
- `scripts/modules/orchestration_planner.py`：模块E - 编排规划
- `scripts/modules/skill_composer.py`：模块F - 技能组合
- `scripts/modules/execution_monitor.py`：模块G - 执行监控
- `scripts/modules/dynamic_adjuster.py`：模块H - 动态调整

### 工具脚本
- `scripts/utils/validator.py`：数据格式验证
- `scripts/utils/loader.py`：数据加载器

### 领域参考
- `references/module_specs/overview.md`：模块规范概览
- `references/capability_layers.md`：五层能力模型
- `references/remediation_strategies.md`：补齐策略说明
- `references/data_formats.md`：数据格式规范
- `references/orchestration_patterns.md`：编排模式参考

---

## 注意事项

### 1. 模块边界
- 模块间通过数据文件交互，不直接调用
- 每个模块只负责一个明确的任务
- 所有模块只输出方案，不执行操作

### 2. 智能体职责
- 智能体负责调用模块、传递数据文件
- 智能体决定是否采纳方案
- 智能体负责执行编排方案
- 智能体决定是否回溯

### 3. 动态调整
- 模块G判断问题类型（简单/复杂/回溯）
- 模块H生成调整方案或回溯建议
- 智能体决定是否执行调整或回溯

### 4. 数据格式
- 所有数据文件使用JSON格式
- 符合 `references/data_formats.md` 的规范

---

## 使用示例

### 示例：法律分析任务

```python
# 1. 环境感知
result_a = EnvironmentPerceiver().execute({
    "task_description": "分析2025年AI法律监管政策趋势"
})
# 输出: environment_profile

# 2. 能力映射
result_b = CapabilityMapper().execute({
    "environment_profile": result_a["environment_profile"],
    "capability_registry": {...}
})
# 输出: match_score=0.70, shortages=[...]

# 3-6. 继续调用其他模块...
# 最终输出: orchestration_result

# 7. 智能体执行，遇到问题

# 8. 执行监控
result_g = ExecutionMonitor().execute({
    "execution_status": {"current_step": 2, "status": "failed", ...},
    "orchestration_plan": {...}
})
# 输出: need_adjustment=true, adjustment_type="simple"

# 9. 动态调整
result_h = DynamicAdjuster().execute({
    "execution_status": {...},
    "adjustment_suggestion": result_g["adjustment_suggestion"],
    "orchestration_plan": {...}
})
# 输出: adjustment_plan 或 revisit_request

# 10. 智能体根据建议继续执行
```

---

## 智能体学习责任

适配器保持无状态，智能体负责：
- 记录编排方案的执行效果
- 基于历史优化策略选择
- 积累领域知识

详见 `references/orchestration_patterns.md` 中的"智能体学习指南"。
