# Harness Engineering - 安装指南

## 📦 安装方式

### 方式 1：从 SkillHub 安装（推荐）

当这个合集注册到 SkillHub 后，你可以使用以下命令一键安装：

```bash
skillhub install harness-engineering
```

这会自动：
1. 从 Git 仓库克隆所有文件
2. 检测 manifest.json 中的所有技能
3. 将每个技能安装到 `~/.qclaw/workspace/skills/` 目录
4. 验证所有技能的 SKILL.md 文件

### 方式 2：从 Git 直接克隆

如果还没注册到 SkillHub，可以直接克隆：

```bash
# 克隆到本地
git clone https://github.com/kiwifruit/HarnessEngineering.git

# 进入目录
cd HarnessEngineering

# 手动安装所有技能
mkdir -p ~/.qclaw/workspace/skills

# 复制所有技能目录
cp -r */ ~/.qclaw/workspace/skills/
```

### 方式 3：选择性安装

如果只想安装某些技能：

```bash
# 只安装 brain-framework
cp -r brain-framework ~/.qclaw/workspace/skills/

# 只安装 rag-optimization
cp -r rag-optimization ~/.qclaw/workspace/skills/

# 只安装 web-search-free
cp -r web-search-free ~/.qclaw/workspace/skills/
```

## ✅ 验证安装

### 检查技能是否已安装

```bash
# 列出所有已安装的技能
ls ~/.qclaw/workspace/skills/

# 应该看到以下目录：
# agent-memory/
# agent-reach/
# agi-evolution-model-linux/
# beee-context-analyzer/
# brain-framework/
# deep-reading/
# function-calling-tutorial/
# intelligent-environment-adapter/
# meta-wisdom-transfer/
# planning-with-files/
# rag-optimization/
# skill-behavior-guide/
# summarize/
# talent-cognition/
# using-superpowers/
# web-search-free/
```

### 验证单个技能

```bash
# 检查 brain-framework 是否正确安装
cat ~/.qclaw/workspace/skills/brain-framework/SKILL.md

# 检查 rag-optimization 是否正确安装
cat ~/.qclaw/workspace/skills/rag-optimization/SKILL.md
```

## 🔧 配置

### 1. 设置环境变量

某些技能可能需要 API Key：

```bash
# 设置 Maton API Key（用于 GitHub API）
export MATON_API_KEY="your_maton_api_key"

# 设置百度 API Key（用于百度搜索）
export BAIDU_API_KEY="your_baidu_api_key"

# 设置 Skills 根目录
export SKILLS_ROOT="~/.qclaw/workspace/skills"
```

### 2. 验证依赖

检查是否安装了必要的依赖：

```bash
# 检查 Python
python3 --version

# 检查 Git
git --version

# 检查 Node（可选）
node --version
npm --version
```

### 3. 安装缺失的依赖

如果缺少某些依赖，可以使用 qclaw-env skill：

```bash
# 安装 Python 依赖
skillhub install qclaw-env
python ~/.qclaw/workspace/skills/qclaw-env/scripts/install.py --python3

# 安装 Node 依赖
python ~/.qclaw/workspace/skills/qclaw-env/scripts/install.py --node
```

## 🚀 快速测试

### 测试 web-search-free

```bash
# 执行一个简单的搜索
bash "$SKILLS_ROOT/web-search-free/scripts/search.sh" "Python 教程" 3
```

### 测试 brain-framework

```bash
# 查看 brain-framework 的文档
cat "$SKILLS_ROOT/brain-framework/SKILL.md"
```

### 测试 rag-optimization

```bash
# 查看 rag-optimization 的快速开始指南
cat "$SKILLS_ROOT/rag-optimization/references/quickstart.md"
```

## 🐛 故障排除

### 问题 1：找不到 skillhub 命令

**解决方案：**
```bash
# 安装 skillhub CLI
pip install skillhub

# 或者使用 qclaw-env skill
skillhub install qclaw-env
```

### 问题 2：权限被拒绝

**解决方案：**
```bash
# 给脚本添加执行权限
chmod +x ~/.qclaw/workspace/skills/*/scripts/*.sh
chmod +x ~/.qclaw/workspace/skills/*/scripts/*.py
```

### 问题 3：找不到 Python 模块

**解决方案：**
```bash
# 安装缺失的 Python 模块
pip install -r requirements.txt

# 或者为每个技能安装依赖
cd ~/.qclaw/workspace/skills/brain-framework
pip install -r requirements.txt
```

### 问题 4：Git 克隆失败

**解决方案：**
```bash
# 检查网络连接
ping github.com

# 检查 Git 配置
git config --list

# 使用 HTTPS 而不是 SSH
git clone https://github.com/kiwifruit/HarnessEngineering.git
```

## 📚 后续步骤

安装完成后，你可以：

1. **阅读文档** - 查看每个技能的 SKILL.md 文件
2. **运行示例** - 尝试每个技能的示例脚本
3. **集成到项目** - 在你的项目中使用这些技能
4. **自定义配置** - 根据需要调整配置文件

## 🔄 更新

### 更新整个合集

```bash
# 进入合集目录
cd ~/path/to/HarnessEngineering

# 拉取最新更改
git pull origin main

# 重新安装技能
cp -r */ ~/.qclaw/workspace/skills/
```

### 更新单个技能

```bash
# 进入技能目录
cd ~/.qclaw/workspace/skills/brain-framework

# 拉取最新更改
git pull origin main
```

## 🤝 获取帮助

如果遇到问题，可以：

1. 查看技能的 README.md 文件
2. 查看技能的 references/ 目录中的文档
3. 提交 Issue 到 GitHub
4. 联系技能的维护者

## 📝 许可证

MIT License - 详见 LICENSE 文件

---

**Happy coding! 🚀**
