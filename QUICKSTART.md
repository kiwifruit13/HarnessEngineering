# Harness Engineering - 快速开始指南

> 5 分钟快速上手 Harness Engineering 合集

## 🚀 30 秒快速安装

```bash
# 一条命令安装所有 16 个技能
skillhub install harness-engineering

# 验证安装
ls ~/.qclaw/workspace/skills/ | grep -E "web-search|brain-framework|rag-optimization"
```

## 📚 核心技能速览

### 1️⃣ 网络搜索 - web-search-free

**用途**：实时搜索网络信息

```bash
# 搜索最新 AI 新闻
bash "$SKILLS_ROOT/web-search-free/scripts/search.sh" "AI 最新进展 2026" 5

# 搜索技术文档
bash "$SKILLS_ROOT/web-search-free/scripts/search.sh" "Python asyncio 教程" 3
```

**何时使用**：
- 需要最新信息
- 查找技术文档
- 研究特定话题

---

### 2️⃣ 代码改造 - brain-framework

**用途**：系统化的代码库改造

```bash
# 分析代码库
python "$SKILLS_ROOT/brain-framework/scripts/research.py" \
  --task "添加类型检查" \
  --codebase-root "."

# 生成改造计划
python "$SKILLS_ROOT/brain-framework/scripts/plan.py" \
  --task "添加类型检查" \
  --research "research.md"

# 执行改造
python "$SKILLS_ROOT/brain-framework/scripts/implement.py" \
  --plan "plan.md" \
  --codebase-root "."
```

**何时使用**：
- 大规模代码重构
- 添加新功能
- 改进代码质量

---

### 3️⃣ RAG 优化 - rag-optimization

**用途**：优化检索增强生成系统

```bash
# 诊断 RAG 系统
python "$SKILLS_ROOT/rag-optimization/scripts/evaluate.py" \
  --config "config.json"

# 应用优化策略
# - 语义分块
# - 由小到大检索
# - 查询转换
# - 重排序
```

**何时使用**：
- 构建知识库问答系统
- 提升检索准确率
- 优化 LLM 应用

---

### 4️⃣ 天赋认知 - talent-cognition

**用途**：识别和发展个人天赋

```bash
# 通过对话进行天赋探索
# 使用 12 个 Prompt 框架之一：
# - T.A.G（快速澄清）
# - C.O.A.S.T（场景化探索）
# - B.R.O.K.E（行动转化）
# - R.O.S.E.S（完整方案）
```

**何时使用**：
- 个人发展规划
- 团队能力评估
- 职业方向探索

---

### 5️⃣ 执行规范 - skill-behavior-guide

**用途**：确保 AI 智能体执行质量

```bash
# 遵循执行规范
# 1. 理解规范要求
# 2. 执行前检查
# 3. 执行中对照
# 4. 执行后验证
```

**何时使用**：
- 提升任务完成质量
- 减少执行错误
- 建立规范流程

---

## 🎯 常见使用场景

### 场景 1：构建 RAG 知识库系统

```bash
# 第一步：获取信息
bash "$SKILLS_ROOT/web-search-free/scripts/search.sh" "主题关键词" 10

# 第二步：优化检索
python "$SKILLS_ROOT/rag-optimization/scripts/evaluate.py" --config "config.json"

# 第三步：深度理解
# 使用 deep-reading 技能进行深度分析

# 第四步：生成摘要
# 使用 summarize 技能生成内容摘要
```

**预期结果**：准确率从 0.3 提升到 0.85+

---

### 场景 2：代码库重构

```bash
# 第一步：分析现状
python "$SKILLS_ROOT/brain-framework/scripts/research.py" \
  --task "重构为微服务架构" \
  --codebase-root "."

# 第二步：制定计划
python "$SKILLS_ROOT/brain-framework/scripts/plan.py" \
  --task "重构为微服务架构" \
  --research "research.md"

# 第三步：用户批注
python "$SKILLS_ROOT/brain-framework/scripts/annotate.py" \
  --plan "plan.md" \
  --annotations "批准，开始实施"

# 第四步：执行改造
python "$SKILLS_ROOT/brain-framework/scripts/implement.py" \
  --plan "plan.md" \
  --codebase-root "."
```

**预期结果**：系统化、可追溯的代码改造

---

### 场景 3：个人发展规划

```bash
# 第一步：识别天赋
# 使用 talent-cognition 的 C.O.A.S.T 框架

# 第二步：认知跃迁
# 使用 meta-wisdom-transfer 进行深度思考

# 第三步：学习新知识
# 使用 deep-reading 进行深度阅读

# 第四步：制定计划
# 使用 planning-with-files 制定成长计划
```

**预期结果**：清晰的个人发展路径

---

## 💡 技能组合使用

### 组合 1：信息研究 + 深度理解

```
web-search-free
    ↓
deep-reading
    ↓
summarize
```

**用途**：快速研究某个主题

---

### 组合 2：代码改造 + 质量保证

```
brain-framework
    ↓
skill-behavior-guide
    ↓
agent-memory
```

**用途**：高质量的代码改造

---

### 组合 3：RAG 系统构建

```
web-search-free
    ↓
rag-optimization
    ↓
deep-reading
    ↓
summarize
```

**用途**：完整的 RAG 系统构建

---

## 🔧 配置快速参考

### 环境变量

```bash
# 设置 API Key
export MATON_API_KEY="your_key"
export BAIDU_API_KEY="your_key"

# 设置 Skills 根目录
export SKILLS_ROOT="~/.qclaw/workspace/skills"
```

### 常用命令

```bash
# 查看技能文档
cat "$SKILLS_ROOT/brain-framework/SKILL.md"

# 查看参考资料
cat "$SKILLS_ROOT/rag-optimization/references/quickstart.md"

# 运行脚本
bash "$SKILLS_ROOT/web-search-free/scripts/search.sh" "查询" 5
```

---

## 📊 技能速查表

| 技能 | 功能 | 使用场景 | 学习时间 |
|------|------|---------|---------|
| web-search-free | 网络搜索 | 获取最新信息 | 5 分钟 |
| brain-framework | 代码改造 | 代码重构 | 15 分钟 |
| rag-optimization | RAG 优化 | 知识库系统 | 20 分钟 |
| talent-cognition | 天赋认知 | 个人发展 | 10 分钟 |
| skill-behavior-guide | 执行规范 | 质量保证 | 10 分钟 |
| deep-reading | 深度阅读 | 文档理解 | 10 分钟 |
| summarize | 文本摘要 | 内容总结 | 5 分钟 |
| agent-memory | 记忆管理 | 状态保存 | 10 分钟 |
| meta-wisdom-transfer | 感悟传递 | 认知跃迁 | 15 分钟 |
| planning-with-files | 项目规划 | 任务管理 | 10 分钟 |

---

## ❓ 常见问题

### Q1: 如何只安装某些技能？

```bash
# 只安装 web-search-free
cp -r ~/.qclaw/workspace/skills/web-search-free ~/my-skills/

# 只安装 brain-framework
cp -r ~/.qclaw/workspace/skills/brain-framework ~/my-skills/
```

### Q2: 如何更新技能？

```bash
# 进入技能目录
cd ~/.qclaw/workspace/skills/brain-framework

# 拉取最新版本
git pull origin main
```

### Q3: 如何卸载技能？

```bash
# 删除技能目录
rm -rf ~/.qclaw/workspace/skills/brain-framework
```

### Q4: 技能之间有依赖关系吗？

大多数技能是独立的，但某些技能可以组合使用以获得更好的效果。

### Q5: 如何获取帮助？

1. 查看技能的 SKILL.md 文件
2. 查看 references/ 目录中的文档
3. 提交 Issue 到 GitHub
4. 查看 README.md 中的支持信息

---

## 🎓 下一步

1. **深入学习** - 阅读感兴趣的技能的完整文档
2. **实践操作** - 在实际项目中使用这些技能
3. **组合使用** - 尝试不同的技能组合
4. **反馈改进** - 提交 Issue 和建议

---

## 📞 获取支持

- 📖 完整文档：[README.md](README.md)
- 📋 安装指南：[INSTALLATION.md](INSTALLATION.md)
- 🐛 问题报告：[GitHub Issues](https://github.com/kiwifruit/HarnessEngineering/issues)

---

**Happy learning! 🚀**

*最后更新: 2026-03-29*
