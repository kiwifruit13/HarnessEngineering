---
name: brain-framework
description: 基于Boris Tane方法论的代码库改造框架，包含Research/Plan/Annotate/Implement四阶段流程，支持修改权衡检查和自动回滚机制
dependency:
  python:
    - pydantic>=2.0.0
    - pyyaml>=6.0
    - langchain-openai>=1.0.0
  system: []
---

# Brain Framework - 造脑子框架

## 任务目标
本 Skill 用于系统化的代码库改造，通过四阶段流程确保改造质量：
- 能力包含：代码库深度分析、实施计划生成、用户批注管理、代码变更执行、修改类型自动检查
- 触发条件：需要对代码库进行系统性改造、重构或功能扩展时

## 前置准备
### 依赖安装
```bash
pip install pydantic>=2.0.0 pyyaml>=6.0 langchain-openai>=1.0.0
```

### 配置文件
创建 `brain-config.yaml` 配置文件（格式见 [references/config.md](references/config.md)）

## 操作步骤
### 标准流程

#### 1. Research 阶段（代码库深度分析）
调用脚本：
```bash
python scripts/research.py \
  --task "任务描述" \
  --codebase-root "代码库根目录" \
  --output "research.md"
```

脚本功能：
- 遍历代码库，分析文件结构和依赖关系
- 识别关键文件和潜在风险点
- 生成 `research.md` 分析报告

**由智能体处理**：
- 根据任务描述确定需要重点关注的文件
- 设定研究深度（shallow/medium/deep）
- 解读 `research.md` 中的关键发现和风险点

#### 2. Plan 阶段（生成实施计划）
调用脚本：
```bash
python scripts/plan.py \
  --task "任务描述" \
  --research "research.md" \
  --output "plan.md"
```

脚本功能：
- 基于研究结果生成详细实施计划
- 列出需要修改的文件清单
- 记录技术选型和权衡决策

**由智能体处理**：
- 审查 `plan.md` 的完整性和可行性
- 评估技术选型的合理性
- 识别潜在的架构影响

#### 3. Annotate 阶段（批注与迭代）
调用脚本：
```bash
python scripts/annotate.py \
  --plan "plan.md" \
  --annotations "用户批注内容"
```

脚本功能：
- 解析用户批注并更新计划
- 检测批准关键词（批准/approve/ok/go/👍）
- 管理迭代次数（最多6次）

**由智能体处理**：
- 根据 `plan.md` 内容，智能体分析并决定是否需要批注
- 当需要修改计划时，生成批注内容
- 确认批准后进入实施阶段

#### 4. Implement 阶段（代码变更执行）
调用脚本：
```bash
python scripts/implement.py \
  --plan "plan.md" \
  --codebase-root "代码库根目录" \
  --strict
```

脚本功能：
- 按计划执行代码变更
- 运行类型检查（strict模式下）
- 生成回滚提示

**由智能体处理**：
- 监控实施进度，处理执行错误
- 验证代码变更的正确性
- 根据回滚提示决定是否回退

#### 5. Modification Check（修改类型检查）
调用脚本：
```bash
python scripts/modification_check.py \
  --changes "修改描述" \
  --plan "plan.md摘要" \
  --output "check_result.json"
```

脚本功能：
- 判断修改是否触及架构红线
- 输出 CONTINUE/ROLLBACK/ASK_USER 决策
- 生成修复建议

**由智能体处理**：
- 解读检查结果，决定下一步行动
- ROLLBACK 时回到 Plan 阶段重新设计
- ASK_USER 时提供人工决策建议

### 分支流程
- **简单任务**（1-2个节点）：可跳过 Research 阶段，直接进入 Plan
- **架构变更**（触及红线）：必须回到 Plan 阶段重新设计
- **批注超限**（6次迭代未批准）：建议回滚任务

## 资源索引
- 必要脚本：
  - [scripts/research.py](scripts/research.py) - 代码库分析
  - [scripts/plan.py](scripts/plan.py) - 计划生成
  - [scripts/annotate.py](scripts/annotate.py) - 批注管理
  - [scripts/implement.py](scripts/implement.py) - 代码执行
  - [scripts/modification_check.py](scripts/modification_check.py) - 修改检查
- 领域参考：
  - [references/config.md](references/config.md) - 配置文件格式（执行前）
  - [references/workflow.md](references/workflow.md) - 完整工作流说明（遇到问题时）
- 输出资产：
  - [assets/prompts/research.md](assets/prompts/research.md) - Research prompt模板
  - [assets/prompts/plan.md](assets/prompts/plan.md) - Plan prompt模板
  - [assets/prompts/implement.md](assets/prompts/implement.md) - Implement prompt模板

## 注意事项
- **人决策，AI 执行**：Plan 阶段必须输出可执行计划，避免 AI 幻觉污染代码
- **文档即共享状态**：所有中间结果（research.md、plan.md）应持久化存储
- **修改权衡守卫**：Implement 阶段的任何架构级修改必须经过 ModificationCheck
- **回滚友好**：每个阶段都应生成回滚提示，降低试错成本
- **仅在有不确定性时调用 ModificationCheck**：明确是架构变更还是实现细节时无需调用

## 使用示例

### 示例1：简单功能扩展（跳过Research）
```bash
# Plan阶段
python scripts/plan.py \
  --task "在用户模块添加邮箱验证功能" \
  --output "plan.md"

# 批注与批准
python scripts/annotate.py \
  --plan "plan.md" \
  --annotations "批准，开始实施"

# 实施阶段
python scripts/implement.py \
  --plan "plan.md" \
  --codebase-root "." \
  --strict
```

### 示例2：复杂架构重构（完整流程）
```bash
# Research阶段
python scripts/research.py \
  --task "将单体架构改造为微服务架构" \
  --codebase-root "." \
  --output "research.md"

# Plan阶段
python scripts/plan.py \
  --task "将单体架构改造为微服务架构" \
  --research "research.md" \
  --output "plan.md"

# 批注迭代（多次）
python scripts/annotate.py \
  --plan "plan.md" \
  --annotations "建议增加服务发现机制"

# 检查修改类型
python scripts/modification_check.py \
  --changes "新增服务注册中心，修改所有服务间调用" \
  --plan "plan.md摘要" \
  --output "check_result.json"

# 实施阶段
python scripts/implement.py \
  --plan "plan.md" \
  --codebase-root "." \
  --strict
```
