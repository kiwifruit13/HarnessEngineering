# Brain Framework 配置文件格式说明

## 概览
本文档说明 Brain Framework 的配置文件格式（`brain-config.yaml`）。

## 完整配置示例

```yaml
brain_framework:
  # 阶段控制
  skip_research_for_complexity:
    - "simple"      # 简单任务跳过 Research
  
  max_annotate_iterations: 6                 # 批注最大迭代次数
  approval_keywords:                         # 批准关键词列表
    - "批准"
    - "approve"
    - "ok"
    - "go"
    - "👍"
    - "同意"
    - "通过"
  
  # 修改权衡规则
  modification_rules:
    # 红线：必须回 Plan 阶段
    must_rollback:
      - "node_count_change"      # 节点数量变化
      - "edge_relation_change"   # 连接关系变化
      - "state_structure_change" # 状态结构变化
      - "contract_inconsistency" # 数据流契约不一致
      - "new_skill_integration"  # 新技能集成
      - "new_subgraph_or_loop"   # 新增子图/循环
    
    # 绿灯：可在 Implement 阶段
    allow_in_implement:
      - "internal_logic_optimization"  # 函数内部优化
      - "variable_naming"              # 变量命名
      - "comment_format"               # 注释格式
      - "prompt_tuning"                # Prompt 微调
      - "config_parameter"             # 配置参数
  
  # 执行约束
  implement_constraints:
    strict_type_check: true      # 强制类型检查
    forbid_any_type: true        # 禁止 any/unknown
    auto_run_tests: true         # 自动运行测试
    max_retry_on_failure: 3      # 失败重试次数
  
  # 持久化配置
  persistence:
    output_dir: "./brain_output"
    backup_enabled: true         # 启用版本备份
    auto_commit_to_git: false    # 自动提交 Git（可选）
```

## 配置项说明

### brain_framework.skip_research_for_complexity
- 类型: List[str]
- 默认值: ["simple"]
- 说明: 指定哪些复杂度级别跳过 Research 阶段
- 可选值: "simple", "medium", "complex"

### brain_framework.max_annotate_iterations
- 类型: Integer
- 默认值: 6
- 说明: Annotate 阶段的最大迭代次数，超过后建议回滚

### brain_framework.approval_keywords
- 类型: List[str]
- 默认值: ["批准", "approve", "ok", "go", "👍"]
- 说明: 用于检测用户批准的关键词列表

### brain_framework.modification_rules.must_rollback
- 类型: List[str]
- 说明: 触发必须回到 Plan 阶段的修改类型关键词
- 应用: 当修改描述包含这些关键词时，强制回滚

### brain_framework.modification_rules.allow_in_implement
- 类型: List[str]
- 说明: 允许在 Implement 阶段执行的修改类型关键词
- 应用: 当修改描述包含这些关键词时，允许继续实施

### brain_framework.implement_constraints.strict_type_check
- 类型: Boolean
- 默认值: true
- 说明: 是否在实施时强制运行类型检查（mypy）

### brain_framework.implement_constraints.forbid_any_type
- 类型: Boolean
- 默认值: true
- 说明: 是否禁止使用 `any` 类型（需要额外工具支持）

### brain_framework.implement_constraints.auto_run_tests
- 类型: Boolean
- 默认值: true
- 说明: 是否在实施后自动运行测试

### brain_framework.implement_constraints.max_retry_on_failure
- 类型: Integer
- 默认值: 3
- 说明: 失败时的最大重试次数

### brain_framework.persistence.output_dir
- 类型: String
- 默认值: "./brain_output"
- 说明: 输出文件的存储目录

### brain_framework.persistence.backup_enabled
- 类型: Boolean
- 默认值: true
- 说明: 是否启用文件修改前的备份

### brain_framework.persistence.auto_commit_to_git
- 类型: Boolean
- 默认值: false
- 说明: 是否自动提交到 Git（谨慎使用）

## 配置文件位置

默认位置：当前工作目录下的 `brain-config.yaml`

如需自定义位置，可以通过环境变量 `BRAIN_CONFIG_PATH` 指定。

## 使用示例

### 创建最小配置
```yaml
brain_framework:
  max_annotate_iterations: 6
  approval_keywords:
    - "批准"
    - "ok"
```

### 自定义修改规则
```yaml
brain_framework:
  modification_rules:
    must_rollback:
      - "架构"
      - "重构"
      - "新增模块"
    allow_in_implement:
      - "优化"
      - "修复"
      - "调整"
```

## 注意事项

1. 配置文件采用 YAML 格式，注意缩进使用空格而非制表符
2. 所有列表项都使用连字符 `-` 开头
3. 字符串值可以用引号包裹，也可以不用（推荐用引号）
4. 修改配置文件后，需要重启 Skill 或重新加载配置
5. 建议根据项目实际情况调整配置，特别是修改规则部分
