# Harness Engineering - AI 智能体工程化技能合集

> 一套完整的 AI 智能体工程化技能合集，包含网络搜索、代码改造、RAG 优化、天赋认知、思考模式切换等 16 个高级技能。

## 📦 合集概览

**Harness Engineering** 是一个精心设计的 Skill 合集，旨在帮助 AI 智能体提升执行质量、思考深度和工程化能力。

### 核心特点

- ✨ **16 个高级技能** - 覆盖搜索、工程、优化、认知等多个领域
- 🎯 **系统化设计** - 技能之间相互配合，形成完整的工程体系
- 📚 **详细文档** - 每个技能都有完整的使用指南和参考资料
- 🚀 **即插即用** - 一条命令安装所有技能
- 🔄 **持续更新** - 定期优化和扩展功能

---

## 🎓 技能分类

### 🔍 **网络搜索与内容获取**

| 技能 | 描述 |
|------|------|
| **web-search-free** | 免费网络搜索 - 无需 API Key 的多引擎网络搜索 |

### 🛠️ **代码工程与规划**

| 技能 | 描述 |
|------|------|
| **brain-framework** | 代码库改造框架 - 基于 Boris Tane 方法论的系统化改造方案 |
| **planning-with-files** | 文件规划系统 - 基于文件的项目规划工具 |

### 🧠 **RAG 优化与检索**

| 技能 | 描述 |
|------|------|
| **rag-optimization** | RAG 系统优化方案 - 17+ 种检索增强生成优化策略 |

### 🎯 **AI 行为与执行规范**

| 技能 | 描述 |
|------|------|
| **skill-behavior-guide** | Skill 执行行为指导 - AI 智能体执行规范和质量保证 |
| **using-superpowers** | 超能力使用指南 - Skill 使用规范和最佳实践 |

### 💡 **认知发展与学习**

| 技能 | 描述 |
|------|------|
| **meta-wisdom-transfer** | 元感悟传递引擎 - 传递完整的认知跃迁过程 |
| **talent-cognition** | 天赋认知框架 - 系统化的天赋识别和发展指导 |
| **deep-reading** | 深度阅读技能 - 文档和论文的深度理解工具 |

### 🤖 **智能体系统**

| 技能 | 描述 |
|------|------|
| **agent-memory** | AI 智能体记忆管理系统 |
| **agent-reach** | AI 智能体能力扩展框架 |
| **intelligent-environment-adapter** | 智能环境适配器 - 自适应环境配置系统 |
| **beee-context-analyzer** | BEEE 上下文分析器 |

### 🚀 **高级模型与教程**

| 技能 | 描述 |
|------|------|
| **agi-evolution-model-linux** | AGI 进化模型（Linux 版本） |
| **function-calling-tutorial** | 函数调用教程 - 学习如何有效使用函数调用 |

### 📝 **内容处理**

| 技能 | 描述 |
|------|------|
| **summarize** | 文本摘要技能 - 高效的内容摘要和总结工具 |

---

## 🚀 快速开始

### 项目结构

```
HarnessEngineering/
├── 📄 manifest.json, SKILL.md, README.md 等（合集文件）
└── 📁 skills/                          # 所有技能统一存放
    ├── web-search-free/
    ├── brain-framework/
    ├── rag-optimization/
    └── ... (其他 13 个技能)
```

### 安装整个合集

```bash
skillhub install harness-engineering
```

这会一次性安装所有 16 个技能到你的本地环境。

### 安装特定技能

```bash
# 只安装某个技能
skillhub install harness-engineering/brain-framework
skillhub install harness-engineering/rag-optimization
```

### 验证安装

```bash
# 查看已安装的技能
ls ~/.qclaw/workspace/skills/

# 应该看到所有 16 个技能目录
```

### 添加新技能

当需要添加新技能时，只需在 `skills/` 文件夹中创建新目录：

```bash
# 1. 创建新技能目录
mkdir skills/my-new-skill

# 2. 创建 SKILL.md
cat > skills/my-new-skill/SKILL.md <<'EOF'
---
name: my-new-skill
description: 新技能描述
---
# My New Skill
...
EOF

# 3. 更新 manifest.json
# 在 skills 数组中添加新技能的条目

# 4. 提交到 Git
git add .
git commit -m "Add new skill: my-new-skill"
git push origin main
```

---

## 📚 使用指南

### 1. 网络搜索

使用 `web-search-free` 进行实时网络搜索：

```bash
# 搜索最新信息
bash "$SKILLS_ROOT/web-search-free/scripts/search.sh" "AI 最新进展" 5
```

### 2. 代码改造

使用 `brain-framework` 进行系统化的代码库改造：

```bash
# Research 阶段：分析代码库
python scripts/research.py --task "任务描述" --codebase-root "."

# Plan 阶段：生成实施计划
python scripts/plan.py --task "任务描述" --research "research.md"

# Implement 阶段：执行改造
python scripts/implement.py --plan "plan.md" --codebase-root "."
```

### 3. RAG 优化

使用 `rag-optimization` 优化你的检索增强生成系统：

```bash
# 诊断 RAG 系统问题
python scripts/evaluate.py --config "config.json"

# 应用优化策略
# - 语义分块
# - 由小到大检索
# - 查询转换
# - 重排序
# - 混合检索
```

### 4. 天赋认知

使用 `talent-cognition` 进行天赋识别和发展规划：

```bash
# 通过 12 个 Prompt 框架进行引导
# - 概念澄清
# - 自我探索
# - 行动转化
# - 长期规划
```

### 5. 思考模式切换

使用 `thinking-mode-switcher` 动态调整思考深度：

```bash
# MODE0：直觉反应（<10ms）
# MODE1：快速启发（100-500ms）
# MODE2：结构化推理（1-10s）
# MODE3：深度反思（5-60s+）
```

---

## 🔗 技能依赖关系

```
web-search-free
    ↓
brain-framework ← planning-with-files
    ↓
rag-optimization
    ↓
skill-behavior-guide ← using-superpowers
    ↓
meta-wisdom-transfer ← talent-cognition ← deep-reading
    ↓
agent-memory ← agent-reach ← intelligent-environment-adapter
    ↓
beee-context-analyzer
    ↓
agi-evolution-model-linux ← function-calling-tutorial
    ↓
summarize
```

---

## 📖 详细文档

每个技能都有完整的文档：

- **SKILL.md** - 技能元数据和使用说明
- **references/** - 详细的参考文档
- **scripts/** - 可执行脚本
- **assets/** - 资源文件和模板

### 快速查看技能文档

```bash
# 查看 brain-framework 的文档
cat brain-framework/SKILL.md

# 查看 rag-optimization 的参考资料
cat rag-optimization/references/quickstart.md
```

---

## 🎯 使用场景

### 场景 1：构建 RAG 系统

```
1. 使用 web-search-free 获取最新信息
2. 使用 rag-optimization 优化检索效果
3. 使用 deep-reading 进行深度理解
4. 使用 summarize 生成摘要
```

### 场景 2：代码库重构

```
1. 使用 brain-framework 进行系统分析
2. 使用 planning-with-files 制定计划
3. 使用 skill-behavior-guide 确保质量
4. 使用 agent-memory 记录决策
```

### 场景 3：个人发展

```
1. 使用 talent-cognition 识别天赋
2. 使用 meta-wisdom-transfer 进行认知跃迁
3. 使用 deep-reading 学习新知识
4. 使用 planning-with-files 制定成长计划
```

### 场景 4：AI 智能体优化

```
1. 使用 using-superpowers 规范执行
2. 使用 skill-behavior-guide 提升质量
3. 使用 thinking-mode-switcher 动态调整
4. 使用 agent-memory 管理状态
```

---

## 🔧 配置与自定义

### 环境变量

```bash
# 设置 API Key（如需要）
export MATON_API_KEY="your_key"
export BAIDU_API_KEY="your_key"

# 设置工作目录
export SKILLS_ROOT="~/.qclaw/workspace/skills"
```

### 配置文件

每个技能可能有自己的配置文件：

```bash
# brain-framework 配置
cat brain-framework/references/config.md

# rag-optimization 配置
cat rag-optimization/assets/config-template.json
```

---

## 📊 技能统计

| 类别 | 数量 | 技能 |
|------|------|------|
| 网络搜索 | 1 | web-search-free |
| 代码工程 | 2 | brain-framework, planning-with-files |
| RAG 优化 | 1 | rag-optimization |
| AI 行为 | 2 | skill-behavior-guide, using-superpowers |
| 认知发展 | 3 | meta-wisdom-transfer, talent-cognition, deep-reading |
| 智能体系统 | 4 | agent-memory, agent-reach, intelligent-environment-adapter, beee-context-analyzer |
| 高级模型 | 2 | agi-evolution-model-linux, function-calling-tutorial |
| 内容处理 | 1 | summarize |
| **总计** | **16** | - |

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个合集！

### 贡献指南

1. Fork 这个仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

---

## 📝 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 📞 支持

- 📧 Email: support@example.com
- 💬 Discord: [Join our community](https://discord.com/invite/example)
- 🐛 Issues: [GitHub Issues](https://github.com/kiwifruit/HarnessEngineering/issues)

---

## 🙏 致谢

感谢所有为这个项目做出贡献的人！

---

## 📈 更新日志

### v1.0.0 (2026-03-29)

- ✨ 初始版本发布
- 📦 包含 16 个高级技能
- 📚 完整的文档和示例
- 🚀 一键安装支持

---

**Made with ❤️ by kiwifruit**

*最后更新: 2026-03-29*
