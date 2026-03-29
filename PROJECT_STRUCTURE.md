# Harness Engineering - 项目结构

```
HarnessEngineering/
│
├── 📄 manifest.json                    # 合集清单（核心文件）
│   └── 定义所有 16 个技能和依赖关系
│
├── 📄 SKILL.md                         # 合集描述（SkillHub 识别）
│   └── 合集的元数据和功能说明
│
├── 📄 README.md                        # 详细文档
│   └── 完整的功能介绍和使用指南
│
├── 📄 QUICKSTART.md                    # 快速开始指南
│   └── 5 分钟快速上手
│
├── 📄 INSTALLATION.md                  # 安装指南
│   └── 详细的安装步骤和故障排除
│
├── 📄 PROJECT_STRUCTURE.md             # 项目结构说明（本文件）
│   └── 完整的目录结构和文件说明
│
├── 📄 COMPLETION_REPORT.md             # 完成报告
│   └── 创建完成的详细报告
│
├── 📄 LICENSE                          # MIT 许可证
│
├── 📄 .gitignore                       # Git 忽略文件
│
└── 📁 skills/                          # 所有技能的统一文件夹
    │
    ├── 🔍 web-search-free/
    │   ├── SKILL.md
    │   ├── scripts/
    │   └── references/
    │
    ├── 🛠️ brain-framework/
    │   ├── SKILL.md
    │   ├── scripts/
    │   ├── references/
    │   └── assets/
    │
    ├── 📋 planning-with-files/
    │   ├── SKILL.md
    │   ├── scripts/
    │   └── references/
    │
    ├── 🧠 rag-optimization/
    │   ├── SKILL.md
    │   ├── scripts/
    │   ├── references/
    │   └── assets/
    │
    ├── 🎯 skill-behavior-guide/
    │   ├── SKILL.md
    │   ├── scripts/
    │   └── references/
    │
    ├── ⚡ using-superpowers/
    │   ├── SKILL.md
    │   └── references/
    │
    ├── 💡 meta-wisdom-transfer/
    │   ├── SKILL.md
    │   └── references/
    │
    ├── 🎓 talent-cognition/
    │   ├── SKILL.md
    │   ├── scripts/
    │   ├── references/
    │   └── assets/
    │
    ├── 📖 deep-reading/
    │   ├── SKILL.md
    │   └── references/
    │
    ├── 💾 agent-memory/
    │   ├── SKILL.md
    │   └── scripts/
    │
    ├── 🚀 agent-reach/
    │   ├── SKILL.md
    │   └── scripts/
    │
    ├── 🔧 intelligent-environment-adapter/
    │   ├── SKILL.md
    │   └── scripts/
    │
    ├── 📊 beee-context-analyzer/
    │   ├── SKILL.md
    │   └── scripts/
    │
    ├── 🤖 agi-evolution-model-linux/
    │   ├── SKILL.md
    │   └── scripts/
    │
    ├── 📚 function-calling-tutorial/
    │   ├── SKILL.md
    │   └── references/
    │
    └── 📝 summarize/
        ├── SKILL.md
        └── scripts/
```

## 📊 文件统计

| 类型 | 数量 | 说明 |
|------|------|------|
| 合集文件 | 9 | manifest.json, SKILL.md, README.md 等 |
| 技能目录 | 16 | 在 skills/ 文件夹中 |
| 总计 | 25 | 1 个合集 + 16 个技能 |

## 🎯 核心文件说明

### 1. manifest.json（必须）
- **作用**：定义合集的元数据和所有技能
- **内容**：
  - 合集名称、版本、描述
  - 16 个技能的列表和路径（现在都在 `./skills/` 下）
  - 技能分类
  - 依赖关系

### 2. SKILL.md（必须）
- **作用**：SkillHub 识别合集的标志
- **内容**：
  - 合集的元数据（name, description, version）
  - 功能概述
  - 快速开始指南
  - 使用场景

### 3. README.md（推荐）
- **作用**：详细的项目文档
- **内容**：
  - 完整的功能介绍
  - 所有 16 个技能的详细说明
  - 使用指南
  - 贡献指南

### 4. QUICKSTART.md（推荐）
- **作用**：快速开始指南
- **内容**：
  - 5 分钟快速安装
  - 核心技能速览
  - 常见使用场景
  - 常见问题

### 5. INSTALLATION.md（推荐）
- **作用**：详细的安装指南
- **内容**：
  - 多种安装方式
  - 验证安装
  - 配置说明
  - 故障排除

### 6. PROJECT_STRUCTURE.md（本文件）
- **作用**：项目结构说明
- **内容**：
  - 完整的目录结构
  - 文件说明
  - 管理指南

### 7. COMPLETION_REPORT.md（推荐）
- **作用**：创建完成报告
- **内容**：
  - 项目概览
  - 已创建的文件
  - 下一步操作

### 8. LICENSE（推荐）
- **作用**：开源许可证
- **内容**：MIT License

### 9. .gitignore（推荐）
- **作用**：Git 忽略文件
- **内容**：Python、Node、IDE 等临时文件

## 📁 skills/ 文件夹说明

### 优势

✅ **统一管理** - 所有技能都在一个文件夹中  
✅ **易于扩展** - 添加新技能只需在 skills/ 中创建新目录  
✅ **清晰结构** - 合集文件和技能文件分离  
✅ **便于维护** - 技能管理更加集中  

### 添加新技能

当需要添加新技能时，只需：

```bash
# 1. 在 skills/ 文件夹中创建新目录
mkdir skills/new-skill

# 2. 创建 SKILL.md
cat > skills/new-skill/SKILL.md <<'EOF'
---
name: new-skill
description: 新技能描述
---
# New Skill
...
EOF

# 3. 添加实现代码
mkdir skills/new-skill/scripts
echo "#!/bin/bash" > skills/new-skill/scripts/main.sh

# 4. 更新 manifest.json
# 在 skills 数组中添加新技能的条目
```

### 更新 manifest.json

添加新技能时，在 `manifest.json` 的 `skills` 数组中添加：

```json
{
  "name": "new-skill",
  "path": "./skills/new-skill",
  "description": "新技能的描述"
}
```

## 🔄 安装流程

```
用户执行命令
    ↓
skillhub install harness-engineering
    ↓
SkillHub 查询索引
    ↓
从 Git 克隆整个仓库
    ↓
检测 manifest.json
    ↓
发现 16 个技能（在 skills/ 中）
    ↓
按依赖顺序安装
    ↓
验证每个技能的 SKILL.md
    ↓
✅ 安装完成
    ↓
所有 16 个技能可用
```

## 📊 技能分类

### 🔍 网络搜索与内容获取（1 个）
- `skills/web-search-free/`

### 🛠️ 代码工程与规划（2 个）
- `skills/brain-framework/`
- `skills/planning-with-files/`

### 🧠 RAG 优化与检索（1 个）
- `skills/rag-optimization/`

### 🎯 AI 行为与执行规范（2 个）
- `skills/skill-behavior-guide/`
- `skills/using-superpowers/`

### 💡 认知发展与学习（3 个）
- `skills/meta-wisdom-transfer/`
- `skills/talent-cognition/`
- `skills/deep-reading/`

### 🤖 智能体系统（4 个）
- `skills/agent-memory/`
- `skills/agent-reach/`
- `skills/intelligent-environment-adapter/`
- `skills/beee-context-analyzer/`

### 🚀 高级模型与教程（2 个）
- `skills/agi-evolution-model-linux/`
- `skills/function-calling-tutorial/`

### 📝 内容处理（1 个）
- `skills/summarize/`

## 🎯 下一步

### 1. 提交到 Git

```bash
cd D:\Git\github\HarnessEngineering
git add .
git commit -m "Reorganize skills into unified folder structure"
git push origin main
```

### 2. 注册到 SkillHub

访问 SkillHub 官网，提交你的合集：
- Git URL: https://github.com/kiwifruit/HarnessEngineering
- 合集名称: harness-engineering
- 描述: Harness Engineering - AI 智能体工程化技能合集

### 3. 测试安装

```bash
skillhub install harness-engineering
```

### 4. 验证功能

```bash
# 检查所有技能是否已安装
ls ~/.qclaw/workspace/skills/ | wc -l
# 应该显示 16
```

## 💡 最佳实践

### 添加新技能时

1. ✅ 在 `skills/` 中创建新目录
2. ✅ 创建 `SKILL.md` 文件
3. ✅ 添加实现代码到 `scripts/` 或 `references/`
4. ✅ 更新 `manifest.json`
5. ✅ 更新 `README.md` 中的技能列表
6. ✅ 提交到 Git

### 删除技能时

1. ✅ 从 `skills/` 中删除目录
2. ✅ 从 `manifest.json` 中删除条目
3. ✅ 更新 `README.md` 中的技能列表
4. ✅ 提交到 Git

### 更新技能时

1. ✅ 修改 `skills/skill-name/` 中的文件
2. ✅ 更新 `SKILL.md` 中的版本号
3. ✅ 提交到 Git

---

**项目结构已优化！🎉**

*最后更新: 2026-03-29*
