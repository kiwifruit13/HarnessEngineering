# Harness Engineering - 合集管理指南

> 如何管理和扩展 Harness Engineering Skill Bundle

## 📁 项目结构

```
HarnessEngineering/
├── 合集文件（9 个）
│   ├── manifest.json
│   ├── SKILL.md
│   ├── README.md
│   ├── QUICKSTART.md
│   ├── INSTALLATION.md
│   ├── PROJECT_STRUCTURE.md
│   ├── MANAGEMENT.md（本文件）
│   ├── LICENSE
│   └── .gitignore
│
└── skills/（技能文件夹）
    ├── web-search-free/
    ├── brain-framework/
    ├── rag-optimization/
    └── ... (其他 13 个技能)
```

## ➕ 添加新技能

### 第一步：创建技能目录

```bash
cd D:\Git\github\HarnessEngineering\skills
mkdir my-new-skill
cd my-new-skill
```

### 第二步：创建 SKILL.md

```bash
cat > SKILL.md <<'EOF'
---
name: my-new-skill
description: 新技能的简短描述
version: 1.0.0
author: your-name
---

# My New Skill

## 功能说明

描述这个技能的功能...

## 使用方法

说明如何使用这个技能...

## 参考资料

- [参考文档](references/guide.md)
EOF
```

### 第三步：创建目录结构

```bash
# 创建脚本目录
mkdir scripts

# 创建参考文档目录
mkdir references

# 创建资源目录（可选）
mkdir assets
```

### 第四步：添加实现代码

```bash
# 添加脚本
cat > scripts/main.py <<'EOF'
#!/usr/bin/env python3
# 你的实现代码
EOF

# 添加参考文档
cat > references/guide.md <<'EOF'
# 使用指南

...
EOF
```

### 第五步：更新 manifest.json

编辑 `manifest.json`，在 `skills` 数组中添加新技能：

```json
{
  "name": "my-new-skill",
  "path": "./skills/my-new-skill",
  "description": "新技能的简短描述"
}
```

同时，如果需要，在 `categories` 中添加分类：

```json
"categories": {
  "my-category": [
    "my-new-skill"
  ]
}
```

### 第六步：更新 README.md

在 README.md 的技能列表中添加新技能的说明。

### 第七步：提交到 Git

```bash
cd D:\Git\github\HarnessEngineering
git add .
git commit -m "Add new skill: my-new-skill"
git push origin main
```

## 🗑️ 删除技能

### 第一步：删除技能目录

```bash
rm -rf skills/old-skill
```

### 第二步：更新 manifest.json

从 `skills` 数组中删除该技能的条目。

### 第三步：更新 README.md

从技能列表中删除该技能的说明。

### 第四步：提交到 Git

```bash
git add .
git commit -m "Remove skill: old-skill"
git push origin main
```

## ✏️ 更新技能

### 修改技能文件

```bash
# 编辑技能文件
cd skills/my-skill
# 修改 SKILL.md、scripts/ 等文件
```

### 更新版本号

在 `SKILL.md` 中更新版本号：

```yaml
---
version: 1.1.0
---
```

### 提交更改

```bash
git add .
git commit -m "Update skill: my-skill to v1.1.0"
git push origin main
```

## 📊 管理技能分类

### 查看当前分类

打开 `manifest.json`，查看 `categories` 部分：

```json
"categories": {
  "web-search": ["web-search-free"],
  "code-engineering": ["brain-framework", "planning-with-files"],
  "rag-optimization": ["rag-optimization"],
  ...
}
```

### 添加新分类

```json
"categories": {
  "my-new-category": [
    "my-new-skill"
  ]
}
```

### 修改分类

直接编辑 `manifest.json` 中的 `categories` 部分。

## 🔍 检查清单

### 添加新技能时

- ✅ 在 `skills/` 中创建新目录
- ✅ 创建 `SKILL.md` 文件（必须）
- ✅ 创建 `scripts/` 目录（如需要）
- ✅ 创建 `references/` 目录（如需要）
- ✅ 添加实现代码
- ✅ 更新 `manifest.json`
- ✅ 更新 `README.md`
- ✅ 提交到 Git

### 删除技能时

- ✅ 删除 `skills/` 中的目录
- ✅ 从 `manifest.json` 中删除条目
- ✅ 从 `README.md` 中删除说明
- ✅ 提交到 Git

### 更新技能时

- ✅ 修改技能文件
- ✅ 更新 `SKILL.md` 中的版本号
- ✅ 更新 `README.md` 中的说明（如需要）
- ✅ 提交到 Git

## 📝 技能命名规范

### 目录名称

- 使用小写字母
- 使用连字符分隔单词
- 示例：`web-search-free`、`brain-framework`、`rag-optimization`

### 技能名称（SKILL.md 中）

- 与目录名称相同
- 示例：`web-search-free`、`brain-framework`

### 描述

- 简洁明了
- 说明主要功能
- 示例：`免费网络搜索 - 无需 API Key 的多引擎网络搜索`

## 🔄 版本管理

### 合集版本

在 `manifest.json` 中更新合集版本：

```json
{
  "version": "1.1.0"
}
```

### 技能版本

在每个技能的 `SKILL.md` 中更新版本：

```yaml
---
version: 1.0.0
---
```

### 版本号格式

使用 Semantic Versioning：
- `MAJOR.MINOR.PATCH`
- 示例：`1.0.0`、`1.1.0`、`1.1.1`

## 📚 文档维护

### README.md

- 保持技能列表最新
- 更新使用场景
- 更新贡献指南

### QUICKSTART.md

- 保持快速开始指南最新
- 更新常见问题
- 更新技能速查表

### INSTALLATION.md

- 保持安装步骤最新
- 更新故障排除指南
- 更新依赖列表

### PROJECT_STRUCTURE.md

- 保持项目结构最新
- 更新文件说明
- 更新管理指南

## 🚀 发布新版本

### 第一步：更新版本号

```bash
# 更新 manifest.json
# 更新 SKILL.md
# 更新各个技能的 SKILL.md
```

### 第二步：更新文档

```bash
# 更新 README.md
# 更新 QUICKSTART.md
# 更新 INSTALLATION.md
```

### 第三步：创建 Git 标签

```bash
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin v1.1.0
```

### 第四步：发布到 SkillHub

访问 SkillHub，更新合集信息。

## 💡 最佳实践

### 1. 保持一致性

- 所有技能使用相同的目录结构
- 所有技能都有 `SKILL.md`
- 所有技能都有清晰的描述

### 2. 文档完善

- 每个技能都有详细的文档
- 提供使用示例
- 提供参考资料

### 3. 版本管理

- 使用 Semantic Versioning
- 为每个版本创建 Git 标签
- 保持更新日志

### 4. 代码质量

- 遵循代码规范
- 提供错误处理
- 提供日志输出

### 5. 社区参与

- 欢迎贡献者
- 提供贡献指南
- 及时回应反馈

## 📞 获取帮助

- 📖 查看 README.md
- 🚀 查看 QUICKSTART.md
- 🔧 查看 INSTALLATION.md
- 📋 查看 PROJECT_STRUCTURE.md
- 🐛 提交 GitHub Issue

## 📊 统计信息

| 指标 | 数值 |
|------|------|
| 合集文件 | 9 个 |
| 技能数量 | 16 个 |
| 技能分类 | 8 个 |
| 总文件数 | 25+ 个 |

---

**Happy managing! 🎉**

*最后更新: 2026-03-29*
