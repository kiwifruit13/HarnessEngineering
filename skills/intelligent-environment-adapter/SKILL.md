---
name: intelligent-environment-adapter
description: 智能编排技能组合方案；当智能体需要处理复杂任务、评估能力边界或获取最优技能编排方案时使用
dependency:
  python: []
  system: []
---

# 智能环境适配器

## 快速开始

本 Skill 提供智能化的技能编排方案生成能力，包含14个功能模块，支持标准编排、动态调整、LangGraph集成、智能补全闭环等场景。

**核心能力**：
- 环境感知 → 能力映射 → 短板诊断 → 智能补全推荐 → 编排规划 → 技能组合
- 执行监控 → 动态调整 → 实时优化
- LangGraph 深度集成（状态捕获 + 实时分析）
- ClawHub 候补技能源（Coze 优先，ClawHub 候补）
- 完整闭环（诊断 → 推荐 → 实施 → 评估 → 学习）

详见：[全局概览文档](references/overview.md)

---

## 操作步骤

### 标准编排流程

```bash
# 1. 环境感知（模块A）
python scripts/modules/environment_perceiver.py \
    --task-description "分析2025年AI法律监管政策趋势" \
    --output environment_profile.json

# 2. 能力映射（模块B）
python scripts/modules/capability_mapper.py \
    --environment-profile environment_profile.json \
    --capability-registry capability_registry.json \
    --output mapping_result.json

# 3. 短板诊断（模块C）
python scripts/modules/shortage_diagnoser.py \
    --mapping-result mapping_result.json \
    --environment-profile environment_profile.json \
    --output diagnostic_report.json

# 4. 智能补全推荐（模块M，推荐使用）
python scripts/modules/intelligent_remedy_recommender.py \
    --diagnostic-report diagnostic_report.json \
    --environment-profile environment_profile.json \
    --learning-db learning_database.json \
    --output remedy_recommendations.json

# 5. 补齐决策（模块D，可选）
python scripts/modules/remediation_decider.py \
    --diagnostic-report diagnostic_report.json \
    --environment-profile environment_profile.json \
    --output remediation_plan.json

# 6. 编排规划（模块E）
python scripts/modules/orchestration_planner.py \
    --remediation-plan remediation_plan.json \
    --environment-profile environment_profile.json \
    --output orchestration_plan.json

# 7. 技能组合（模块F）
python scripts/modules/skill_composer.py \
    --orchestration-plan orchestration_plan.json \
    --available-skills available_skills.json \
    --output orchestration_result.json
```

### 动态调整流程

```bash
# 1. 执行监控（模块G）
python scripts/modules/execution_monitor.py \
    --execution-status execution_status.json \
    --orchestration-plan orchestration_plan.json \
    --output adjustment_suggestion.json

# 2. 动态调整（模块H）
python scripts/modules/dynamic_adjuster.py \
    --execution-status execution_status.json \
    --adjustment-suggestion adjustment_suggestion.json \
    --orchestration-plan orchestration_plan.json \
    --output adjustment_plan.json
```

### LangGraph 集成

```python
from scripts.modules.state_capture_adapter import StateCaptureAdapter
from scripts.modules.realtime_coordinator import RealtimeCoordinator

# 初始化
state_adapter = StateCaptureAdapter()
coordinator = RealtimeCoordinator()

# 在 LangGraph 节点中
def realtime_check_node(state):
    # 实时分析
    result = coordinator.analyze_realtime(
        langgraph_state=state,
        current_node=state["current_node"],
        node_history=state.get("node_history", []),
        orchestration_plan=state.get("orchestration_plan")
    )

    if result.needs_adjustment:
        return {"adjustment_plan": result.adjustment_plan}

    return {"no_adjustment": True}
```

### 技能查询（Coze + ClawHub 建议生成）

```python
from scripts.modules.skill_query_coordinator import SkillQueryCoordinator
from scripts.modules.clawhub_querier import ClawHubQuerySuggester

# 创建协调器
coordinator = SkillQueryCoordinator()

# 创建 ClawHub 查询建议生成器（仅生成方案，不执行 API）
clawhub_suggester = ClawHubQuerySuggester()

# 生成 ClawHub 查询建议
suggestion = clawhub_suggester.generate_query_suggestion(
    capability_tags=["数据分析", "可视化"],
    domain="金融"
)

# 将建议转换为模型可执行的指导
guidance = clawhub_suggester.convert_to_model_guidance(suggestion)
# guidance 包含：
# - 建议的查询参数（tags, keywords, filters）
# - 本地候补方案
# - 替代搜索建议
```

### 智能补全推荐

```python
from scripts.modules.intelligent_remedy_recommender import IntelligentRemedyRecommender

# 创建推荐器
recommender = IntelligentRemedyRecommender()
recommender.set_skill_query_coordinator(coordinator)

# 生成补全推荐
recommendations = recommender.generate_remedy_recommendations(
    diagnostic_report=diagnostic_report,
    environment_profile=environment_profile,
    strategy="balanced"
)

# 查看方案
primary = recommendations['recommendations']['primary_plan']
print(f"预期改善: {primary['expected_improvement']:.1%}")
```

### 效果评估

```python
from scripts.modules.remediation_effectiveness_evaluator import RemediationEffectivenessEvaluator

# 创建评估器
evaluator = RemediationEffectivenessEvaluator()
evaluator.load_lessons_database("lessons_database.json")

# 评估效果
evaluation = evaluator.evaluate_effectiveness(
    pre_remediation_state={"match_score": 0.60},
    post_remediation_state={"match_score": 0.85},
    remedy_plan=remedy_recommendations,
    execution_result={"status": "success"}
)

print(f"综合效果: {evaluation['effectiveness_metrics']['overall_effectiveness']:.2f}")
```

---

## 模块索引

| 模块 | 名称 | 文件 | 用途 |
|------|------|------|------|
| **A** | 环境感知 | `environment_perceiver.py` | 分析任务特征 |
| **B** | 能力映射 | `capability_mapper.py` | 计算匹配度 |
| **C** | 短板诊断 | `shortage_diagnoser.py` | 生成诊断报告 |
| **M** | 智能补全推荐 | `intelligent_remedy_recommender.py` | 智能匹配技能 |
| **D** | 补齐决策 | `remediation_decider.py` | 选择补齐策略 |
| **E** | 编排规划 | `orchestration_planner.py` | 设计编排方案 |
| **F** | 技能组合 | `skill_composer.py` | 生成技能组合 |
| **G** | 执行监控 | `execution_monitor.py` | 监控执行状态 |
| **H** | 动态调整 | `dynamic_adjuster.py` | 生成调整方案 |
| **I** | 状态捕获 | `state_capture_adapter.py` | 捕获 LangGraph 状态 |
| **J** | 实时协调 | `realtime_coordinator.py` | 实时分析优化 |
| **K** | ClawHub查询建议 | `clawhub_querier.py` | 生成 ClawHub 查询方案（不执行API） |
| **L** | 技能查询协调 | `skill_query_coordinator.py` | 协调多源查询 |
| **N** | 效果评估 | `remediation_effectiveness_evaluator.py` | 评估补全效果 |

---

## 资源索引

### 模块脚本
所有模块位于 `scripts/modules/` 目录，详见上方模块索引。

### 工具脚本
- `scripts/utils/validator.py`：数据格式验证
- `scripts/utils/loader.py`：数据加载器

### 参考文档
- `references/overview.md`：全局概览文档（知识图谱）
- `references/capability_layers.md`：五层能力模型
- `references/data_formats.md`：数据格式规范
- `references/remediation_strategies.md`：补齐策略说明
- `references/orchestration_patterns.md`：编排模式参考
- `references/module_specs/overview.md`：模块规范概览

---

## 前置准备

- **依赖**：仅使用 Python 标准库（json, typing, argparse, pathlib, datetime, dataclasses）
- **数据文件**：需要准备 `capability_registry.json`（能力清单）
- **可选**：`learning_database.json`（学习数据库）、`lessons_database.json`（经验数据库）

---

## 核心原则

1. **单一职责**：每个模块只做一件事
2. **明确边界**：模块间通过数据文件交互
3. **只输出方案**：所有模块只输出建议，不执行
4. **状态无感知**：Skill 不管理状态，由外部（如 LangGraph）管理
5. **优先级策略**：Coze 技能优先，ClawHub 作为候补

---

## 注意事项

- 所有模块独立运行，互不依赖
- 输出文件使用 JSON 格式
- 推荐使用模块M（智能补全推荐）替代模块D（补齐决策）
- LangGraph 集成时，建议使用模块I和J实现实时监控
- ClawHub 作为候补选项，优先使用 Coze 技能市场
- 建议定期更新学习数据库和经验数据库

---

## 使用示例

详见各模块的具体使用说明，或参考 `references/overview.md` 获取完整的架构设计和使用场景。
