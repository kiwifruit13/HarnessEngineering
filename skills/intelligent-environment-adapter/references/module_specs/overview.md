# 模块规范文档

## 概览

智能环境适配器采用模块化架构，共包含8个独立模块，每个模块职责明确、边界清晰。

---

## 模块列表

| 模块ID | 模块名称 | 职责 | 输入 | 输出 |
|--------|---------|------|------|------|
| A | 环境感知模块 | 分析任务特征 | 任务描述 | 环境画像 |
| B | 能力映射模块 | 计算匹配度 | 环境画像 + 能力清单 | 映射结果 |
| C | 短板诊断模块 | 生成诊断报告 | 映射结果 | 诊断报告 |
| D | 补齐决策模块 | 选择补齐策略 | 诊断报告 | 补齐计划 |
| E | 编排规划模块 | 设计编排方案 | 补齐计划 | 编排方案 |
| F | 技能组合模块 | 生成技能组合 | 编排方案 | 编排结果 |
| G | 执行监控模块 | 监控执行状态 | 执行状态 | 调整建议 |
| H | 动态调整模块 | 生成调整方案 | 执行状态 + 建议 | 调整方案 |

---

## 模块边界约束

### 1. 单向数据流

```
A → B → C → D → E → F → [智能体执行] → G → H
```

### 2. 模块间禁止直接调用

- ❌ 模块B不能直接调用模块A
- ✅ 模块B只能接收模块A输出的数据文件

### 3. 无状态设计

- 模块不保存执行状态
- 所有状态通过数据文件传递

---

## 模块详情

### 模块A：环境感知模块

**文件**: `scripts/modules/environment_perceiver.py`

**职责**:
- 分析任务描述
- 识别任务类型、领域、时效性、数据类型
- 生成结构化的环境画像

**输入格式**:
```json
{
  "task_description": "分析2025年AI法律监管政策趋势",
  "context": {}  // 可选
}
```

**输出格式**:
```json
{
  "environment_profile": {
    "task_type": "深度分析",
    "domain": ["法律", "AI"],
    "time_sensitivity": "实时",
    "data_type": "纯文本",
    "complexity": "复杂"
  },
  "confidence": 0.85
}
```

**边界**:
- ✅ 分析任务特征
- ❌ 不评估能力
- ❌ 不诊断短板

---

### 模块B：能力映射模块

**文件**: `scripts/modules/capability_mapper.py`

**职责**:
- 计算任务需求与能力的匹配度
- 识别能力断点

**输入格式**:
```json
{
  "environment_profile": {...},
  "capability_registry": {
    "L1": {...},
    "L2": {...},
    ...
  }
}
```

**输出格式**:
```json
{
  "match_score": 0.75,
  "layer_scores": {"L1": 0.65, ...},
  "shortages": [...]
}
```

**边界**:
- ✅ 计算匹配度
- ❌ 不生成诊断报告
- ❌ 不选择补齐策略

---

### 模块G：执行监控模块

**文件**: `scripts/modules/execution_monitor.py`

**职责**:
- 接收智能体的执行状态
- 判断是否需要调整方案

**输入格式**:
```json
{
  "execution_status": {
    "current_step": 2,
    "status": "failed",
    "error": {...}
  },
  "orchestration_plan": {...}
}
```

**输出格式**:
```json
{
  "need_adjustment": true,
  "adjustment_suggestion": {
    "adjustment_type": "simple",
    "reason": "...",
    "suggested_action": "..."
  }
}
```

**边界**:
- ✅ 分析执行状态
- ✅ 判断调整类型
- ❌ 不执行调整
- ❌ 不生成详细方案

---

### 模块H：动态调整模块

**文件**: `scripts/modules/dynamic_adjuster.py`

**职责**:
- 根据执行状态生成调整方案
- 支持回溯建议

**输入格式**:
```json
{
  "execution_status": {...},
  "adjustment_suggestion": {...},
  "orchestration_plan": {...},
  "environment_profile": {...}
}
```

**输出格式**:
```json
{
  "adjustment_plan": {
    "adjustment_type": "skill_replacement",
    "target_step": 2,
    "new_action": {...},
    "updated_workflow": [...]
  },
  "revisit_request": null
}
```

**边界**:
- ✅ 生成调整方案
- ✅ 支持回溯建议
- ❌ 不执行调整
- ❌ 不直接调用其他模块

---

## 回溯机制

当模块H判断需要回溯时，输出格式为：

```json
{
  "adjustment_plan": null,
  "revisit_request": {
    "action": "revisit_diagnosis",
    "target_module": "shortage_diagnosis",
    "reason": "发现新的能力短板",
    "new_context": {...}
  }
}
```

智能体接收此建议后，决定是否执行回溯。
