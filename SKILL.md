---
name: harness-engineering
description: Harness Engineering - 一套完整的 AI 智能体工程化技能合集，包含网络搜索、代码改造、RAG 优化、天赋认知、思考模式切换等 16 个高级技能
version: 1.0.0
author: kiwifruit
license: MIT
repository: https://github.com/kiwifruit/HarnessEngineering
keywords:
  - ai-engineering
  - skills-bundle
  - agent-optimization
  - rag-optimization
  - code-refactoring
  - talent-development
metadata:
  openclaw:
    emoji: 🎯
    type: bundle
    skillCount: 16
    categories:
      - web-search
      - code-engineering
      - rag-optimization
      - ai-behavior
      - cognition-development
      - agent-systems
      - advanced-models
      - content-processing
---

# Harness Engineering - AI 智能体工程化技能合集

> 一套完整的 AI 智能体工程化技能合集，旨在提升 AI 智能体的执行质量、思考深度和工程化能力。

## 📦 合集概览

**Harness Engineering** 包含 16 个精心设计的高级技能，覆盖以下领域：

- 🔍 **网络搜索与内容获取** - 实时信息获取和内容处理
- 🛠️ **代码工程与规划** - 系统化的代码改造和项目规划
- 🧠 **RAG 优化** - 17+ 种检索增强生成优化策略
- 🎯 **AI 行为规范** - 执行质量保证和规范遵循
- 💡 **认知发展** - 天赋识别、感悟传递、深度阅读
- 🤖 **智能体系统** - 记忆管理、能力扩展、环境适配
- 🚀 **高级模型** - AGI 进化模型、函数调用教程
- 📝 **内容处理** - 文本摘要和总结

## 🎓 包含的技能

### 1. web-search-free
**免费网络搜索** - 无需 API Key 的多引擎网络搜索

- 支持 17 个搜索引擎（8 个国内 + 9 个国际）
- 支持高级搜索操作符和时间过滤
- 支持 WolframAlpha 知识查询

### 2. brain-framework
**代码库改造框架** - 基于 Boris Tane 方法论的系统化改造方案

- Research 阶段：代码库深度分析
- Plan 阶段：生成详细实施计划
- Annotate 阶段：用户批注与迭代
- Implement 阶段：执行代码变更
- Modification Check：架构红线检查

### 3. planning-with-files
**文件规划系统** - 基于文件的项目规划工具

- 项目规划和任务管理
- 文件组织和结构设计
- 进度跟踪和反馈

### 4. rag-optimization
**RAG 系统优化方案** - 17+ 种检索增强生成优化策略

- 语义分块、由小到大检索、查询转换
- 混合检索、重排序、上下文压缩
- 引用溯源、幻觉检测、Graph RAG
- 准确率可从 0.3 提升到 0.85+

### 5. skill-behavior-guide
**Skill 执行行为指导** - AI 智能体执行规范和质量保证

- 规范遵循策略
- 执行质量提升
- 自我修正机制
- 任务拆解方法
- 用户交互策略

### 6. using-superpowers
**超能力使用指南** - Skill 使用规范和最佳实践

- Skill 调用规范
- 优先级管理
- 红旗识别
- 最佳实践

### 7. meta-wisdom-transfer
**元感悟传递引擎** - 传递完整的认知跃迁过程

- 完整的悟性产生过程
- 从困惑到质疑再到清晰的思维轨迹
- 六阶段认知跃迁

### 8. talent-cognition
**天赋认知框架** - 系统化的天赋识别和发展指导

- 12 个 Prompt 框架
- 42 个核心天赋属性库
- 天赋配置算法
- 自我探索工具

### 9. deep-reading
**深度阅读技能** - 文档和论文的深度理解工具

- 文档深度分析
- 论文阅读指导
- 知识提取和总结

### 10. agent-memory
**AI 智能体记忆管理系统**

- 长期记忆管理
- 上下文保存
- 决策记录

### 11. agent-reach
**AI 智能体能力扩展框架**

- 能力评估
- 能力扩展
- 能力整合

### 12. intelligent-environment-adapter
**智能环境适配器** - 自适应环境配置系统

- 环境检测
- 自适应配置
- 资源优化

### 13. beee-context-analyzer
**BEEE 上下文分析器**

- 上下文分析
- 信息提取
- 关系识别

### 14. agi-evolution-model-linux
**AGI 进化模型（Linux 版本）**

- AGI 发展路径
- 能力演进
- 系统优化

### 15. function-calling-tutorial
**函数调用教程** - 学习如何有效使用函数调用

- 函数调用基础
- 高级用法
- 最佳实践

### 16. summarize
**文本摘要技能** - 高效的内容摘要和总结工具

- 文本摘要
- 内容总结
- 关键信息提取

## 🚀 快速开始

### 安装整个合集

```bash
skillhub install harness-engineering
```

### 验证安装

```bash
# 查看已安装的技能
ls ~/.qclaw/workspace/skills/

# 应该看到所有 16 个技能目录
```

### 使用技能

```bash
# 使用 web-search-free 进行搜索
bash "$SKILLS_ROOT/web-search-free/scripts/search.sh" "查询内容" 5

# 使用 brain-framework 进行代码改造
python brain-framework/scripts/research.py --task "任务描述"

# 使用 rag-optimization 优化 RAG 系统
python rag-optimization/scripts/evaluate.py --config "config.json"
```

## 📚 文档结构

```
harness-engineering/
├── manifest.json                    # 合集清单
├── SKILL.md                         # 合集描述（本文件）
├── README.md                        # 详细文档
├── LICENSE                          # 许可证
│
├── web-search-free/
│   ├── SKILL.md
│   ├── scripts/
│   └── references/
│
├── brain-framework/
│   ├── SKILL.md
│   ├── scripts/
│   ├── references/
│   └── assets/
│
├── rag-optimization/
│   ├── SKILL.md
│   ├── scripts/
│   ├── references/
│   └── assets/
│
└── ... (其他 13 个技能)
```

## 🎯 使用场景

### 场景 1：构建 RAG 系统

1. 使用 `web-search-free` 获取最新信息
2. 使用 `rag-optimization` 优化检索效果
3. 使用 `deep-reading` 进行深度理解
4. 使用 `summarize` 生成摘要

### 场景 2：代码库重构

1. 使用 `brain-framework` 进行系统分析
2. 使用 `planning-with-files` 制定计划
3. 使用 `skill-behavior-guide` 确保质量
4. 使用 `agent-memory` 记录决策

### 场景 3：个人发展

1. 使用 `talent-cognition` 识别天赋
2. 使用 `meta-wisdom-transfer` 进行认知跃迁
3. 使用 `deep-reading` 学习新知识
4. 使用 `planning-with-files` 制定成长计划

### 场景 4：AI 智能体优化

1. 使用 `using-superpowers` 规范执行
2. 使用 `skill-behavior-guide` 提升质量
3. 使用 `thinking-mode-switcher` 动态调整
4. 使用 `agent-memory` 管理状态

## 🔧 配置

### 环境变量

```bash
# 设置 API Key（如需要）
export MATON_API_KEY="your_key"
export BAIDU_API_KEY="your_key"

# 设置工作目录
export SKILLS_ROOT="~/.qclaw/workspace/skills"
```

### 依赖

- Python 3.8+
- Git
- Node.js 14+ (可选)
- npm (可选)

## 📖 详细文档

详见 [README.md](README.md) 和各个技能的 SKILL.md 文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📝 许可证

MIT License

## 📞 支持

- 📧 Email: support@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/kiwifruit/HarnessEngineering/issues)

---

**Made with ❤️ by kiwifruit**

*最后更新: 2026-03-29*
