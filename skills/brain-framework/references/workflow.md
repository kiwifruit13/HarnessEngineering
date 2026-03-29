# Brain Framework 完整工作流程说明

## 目录
1. [流程概览](#流程概览)
2. [阶段详解](#阶段详解)
3. [分支流程](#分支流程)
4. [常见场景](#常见场景)
5. [最佳实践](#最佳实践)

## 流程概览

Brain Framework 包含四个主要阶段，形成系统化的代码库改造流程：

```
Research（可选）
    ↓
Plan
    ↓
Annotate ←←←←←←←←←←
    ↓                   ↑
Implement ← modification_check
    ↓
Done
```

### 阶段映射到脚本

| 阶段 | 脚本文件 | 输入 | 输出 |
|-----|---------|------|------|
| Research | `scripts/research.py` | task_description, codebase_root | research.md |
| Plan | `scripts/plan.py` | task_description, research.md | plan.md |
| Annotate | `scripts/annotate.py` | plan.md, annotations | 更新的 plan.md |
| Implement | `scripts/implement.py` | plan.md, codebase_root | 修改的文件列表 |
| Modification Check | `scripts/modification_check.py` | proposed_changes | check_result.json |

## 阶段详解

### 1. Research 阶段

**目的**: 深度理解代码库现状，为方案设计提供依据。

**执行脚本**:
```bash
python scripts/research.py \
  --task "任务描述" \
  --codebase-root "代码库路径" \
  --output "research.md"
```

**输出内容**:
- 代码库文件统计
- 目录结构分析
- 关键文件识别
- 风险点列表

**智能体职责**:
- 根据任务描述确定研究重点
- 解读 research.md 中的关键发现
- 评估改造的可行性

**何时跳过**:
- 简单任务（1-2个文件修改）
- 对代码库已经非常熟悉
- 明确知道需要修改哪些文件

### 2. Plan 阶段

**目的**: 生成详细、可执行的实施计划。

**执行脚本**:
```bash
python scripts/plan.py \
  --task "任务描述" \
  --research "research.md" \
  --output "plan.md"
```

**输出内容**:
- 任务目标和约束条件
- 实施方案（阶段划分）
- 文件变更清单（表格形式）
- 技术选型和权衡决策
- 风险评估和回滚计划

**智能体职责**:
- 审查计划的完整性和可行性
- 评估技术选型的合理性
- 识别潜在的架构影响
- 准备批注内容

**关键要点**:
- 必须包含防呆标记（"don't implement yet"）
- 文件变更清单必须完整
- 权衡决策必须记录原因

### 3. Annotate 阶段

**目的**: 管理用户批注，迭代优化计划。

**执行脚本**:
```bash
python scripts/annotate.py \
  --plan "plan.md" \
  --annotations "批注内容" \
  --iteration 0
```

**输出内容**:
- 更新后的 plan.md（追加批注）
- 批准状态（approved: true/false）
- 下一步行动（继续批注/实施/回滚）

**智能体职责**:
- 根据 plan.md 内容分析是否需要批注
- 生成有针对性的批注内容
- 决定是否批准进入实施

**批准关键词**:
- 中文：批准、同意、通过
- 英文：approve、ok、go
- 表情：👍

**迭代机制**:
- 最多 6 次迭代
- 超限后建议回滚
- 每次批注都会记录时间戳

### 4. Implement 阶段

**目的**: 按批准的计划执行代码变更。

**执行脚本**:
```bash
python scripts/implement.py \
  --plan "plan.md" \
  --codebase-root "代码库路径" \
  --strict \
  --run-tests
```

**输出内容**:
- 修改的文件列表
- 测试结果（如果启用）
- 回滚提示

**智能体职责**:
- 监控实施进度
- 处理执行错误
- 验证代码变更的正确性
- 根据需要决定回滚

**严格模式**:
- 启用类型检查（mypy）
- 禁止 `any` 类型
- 自动运行测试

### 5. Modification Check 阶段

**目的**: 在实施过程中判断修改类型，防止架构级破坏。

**执行脚本**:
```bash
python scripts/modification_check.py \
  --changes "修改描述" \
  --plan "plan.md摘要" \
  --affected-files "file1.py,file2.py"
```

**输出内容**:
- 决策（CONTINUE/ROLLBACK_TO_PLAN/ASK_USER）
- 修改类型（架构/实现细节/未知）
- 置信度（0.0-1.0）
- 修复建议

**智能体职责**:
- 解读检查结果
- 决定下一步行动
- ROLLBACK 时回到 Plan 阶段
- ASK_USER 时提供人工决策建议

**检查方式**:
- 规则检查（快速）：基于关键词匹配
- LLM 判断（慢速）：基于语义理解

## 分支流程

### 场景1：简单任务（跳过 Research）
```
Plan → Annotate → Implement → Done
```

**触发条件**:
- 任务只涉及 1-2 个文件
- 不需要深入了解代码库
- 明确知道修改范围

### 场景2：架构变更（回滚到 Plan）
```
Research → Plan → Annotate → Implement 
  ↓ modification_check（返回 ROLLBACK）
Plan（重新设计）→ ...
```

**触发条件**:
- 修改触及架构红线
- 节点数量/连接关系变化
- 引入新的外部集成

### 场景3：批注超限（建议回滚）
```
Plan → Annotate（迭代6次仍未批准）
  ↓
建议回滚或暂停
```

**触发条件**:
- 用户连续6次批注未批准
- 可能是方案不成熟
- 需要重新规划

### 场景4：修改类型不确定（询问用户）
```
Implement → modification_check（返回 ASK_USER）
  ↓
等待人工决策
```

**触发条件**:
- 规则无法判断修改类型
- LLM 置信度低于阈值
- 需要人工确认

## 常见场景

### 场景A：添加新功能
```
Research（了解现有功能）
  ↓
Plan（设计新功能实现方案）
  ↓
Annotate（审查设计细节）
  ↓
Implement（实施代码变更）
```

**关键点**:
- Research 阶段识别现有功能结构
- Plan 阶段明确新功能的集成方式
- Annotate 阶段确认边界条件
- Implement 阶段确保不破坏现有功能

### 场景B：重构代码
```
Research（分析代码质量）
  ↓
Plan（制定重构计划）
  ↓
Annotate（审查重构范围）
  ↓
Modification Check（每次修改前检查）
  ↓
Implement（逐步重构）
```

**关键点**:
- 每次修改前运行 Modification Check
- 小步快跑，频繁提交
- 保持测试通过

### 场景C：修复 Bug
```
Plan（跳过 Research，直接制定修复计划）
  ↓
Annotate（确认修复方案）
  ↓
Implement（快速修复）
```

**关键点**:
- 可以跳过 Research 阶段
- 批注阶段确认修复的副作用
- 尽快验证修复效果

## 最佳实践

### 1. Research 阶段
- ✅ 明确研究范围，避免过度分析
- ✅ 识别关键文件和风险点
- ✅ 记录发现供 Plan 阶段使用
- ❌ 不要试图理解每个文件的细节

### 2. Plan 阶段
- ✅ 文件变更清单必须完整
- ✅ 记录重要的技术决策
- ✅ 提供清晰的回滚方案
- ❌ 不要在计划中包含代码实现细节

### 3. Annotate 阶段
- ✅ 批注要具体、可执行
- ✅ 迭代时保持上下文连贯
- ✅ 批准前确认所有问题已解决
- ❌ 不要在批注中提出与任务无关的要求

### 4. Implement 阶段
- ✅ 严格按计划执行
- ✅ 每次修改后验证
- ✅ 保留回滚选项
- ❌ 不要在实施时改变设计方案

### 5. Modification Check 阶段
- ✅ 明确修改描述
- ✅ 根据检查结果决策
- ✅ ROLLBACK 时记录原因
- ❌ 不要忽视检查结果

### 6. 通用建议
- **人决策，AI 执行**: 关键决策由人做出，AI 负责执行
- **文档即共享状态**: 所有中间结果都持久化
- **小步快跑**: 避免大规模一次性变更
- **测试驱动**: 每次修改后验证

## 故障排查

### 问题1：Research 阶段找不到文件
**原因**: 代码库路径错误或文件权限问题
**解决**: 检查 `--codebase-root` 参数，确保路径正确且有读取权限

### 问题2：Plan 阶段生成的计划不完整
**原因**: Research 摘要不足或任务描述不清晰
**解决**: 补充任务描述，增加约束条件，手动完善 plan.md

### 问题3：Annotate 阶段无法检测批准
**原因**: 批准关键词不匹配
**解决**: 检查批注内容，确保包含批准关键词或修改配置文件

### 问题4：Implement 阶段类型检查失败
**原因**: 代码类型注解不完整或配置了 strict 模式
**解决**: 补充类型注解或暂时禁用 `--strict` 选项

### 问题5：Modification Check 返回 ASK_USER
**原因**: 修改描述不明确
**解决**: 修改描述，使其更具体，或手动决策

## 总结

Brain Framework 提供了系统化的代码库改造方法，通过四阶段流程确保改造质量。核心原则是：
1. 深度理解代码库（Research）
2. 精心设计方案（Plan）
3. 充分审查优化（Annotate）
4. 严格按计划执行（Implement）
5. 守护架构一致性（Modification Check）

遵循本文档的指导，可以高效、安全地完成代码库改造任务。
