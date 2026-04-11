---
name: DeepXiv
description: 科技文献智能体接口 - 专为智能体设计的科技文献基础设施，将论文搜索、渐进式阅读、热点追踪和深度调研变成可调用、可编排、可自动化的能力。已索引290万+ ArXiv论文，支持JSON/Markdown格式，提供CLI、Python SDK和MCP多种接入形态。
---

# DeepXiv - 科技文献智能体接口

## 概述

DeepXiv 是专为智能体设计的科技文献基础设施，将论文搜索、渐进式阅读、热点追踪和深度调研变成可调用、可编排、可自动化的能力。

**核心理念**：让开放科技文献从"人类可读"升级为"智能体可用"

**覆盖规模**：

- 已索引 2,949,129 篇 ArXiv 论文
- T+0 每日同步新发布
- 正在扩展至 PMC、bioRxiv、Semantic Scholar 等，目标 2亿+ 开放文献

## 触发词

- `deepxiv`
- `arxiv search`
- `论文搜索`
- `文献调研`
- `学术论文`
- `deep research`

## 三大核心能力

### 1. 数据接入

- 原生支持 JSON / Markdown 格式
- 智能体直接获取标题、作者、摘要、参考文献等元信息
- 渐进披露：先看少量、再按需展开，避免一次性灌入整篇长文

### 2. 一站式能力集成

- 专属论文搜索引擎
- 问答能力：围绕文献完成信息提取与理解
- 热点追踪：了解每天/每周/每月关于某主题的热点论文
- 深度调研：自动串联搜索、筛选、渐进式阅读、信息提取与归纳整理

### 3. 多种接入形态

- CLI（命令行界面）：核心形态
- Python SDK：定制化科研智能体集成
- MCP 接入：嵌入各类智能体开发框架

## 安装

```bash
# 基础安装
pip install deepxiv-sdk

# 完整安装（包含 Agent 功能）
pip install "deepxiv-sdk[all]"
```

## 使用方式

### CLI 命令

```bash
# 搜索论文
deepxiv search "agent memory" --limit 20 --format json

# 快速预览（低 token 消耗）
deepxiv paper 2602.16493 --brief

# 查看全文结构与章节分布
deepxiv paper 2602.16493 --head

# 精读特定章节
deepxiv paper 2602.16493 --section "Experiments"

# 热点追踪
deepxiv trending --days 7 --limit 30 --json

# 深度调研 Agent
deepxiv agent config  # 配置 API key
deepxiv agent query "What are the latest papers about agent memory?" --verbose
```

### Python SDK

```python
from deepxiv import DeepXiv

# 初始化客户端
client = DeepXiv(api_key="your_api_key")

# 搜索论文
results = client.search("agent memory", limit=20)

# 获取论文元信息
paper = client.paper("2602.16493")

# 渐进式阅读
brief = client.brief("2602.16493")  # 快速预览
head = client.head("2602.16493")    # 结构概览
section = client.section("2602.16493", "Experiments")  # 章节精读

# 深度调研
agent = deepxiv.agent()
response = agent.query("What are the latest papers about agent memory?")
```

## 渐进式阅读流程

DeepXiv 的核心设计是**渐进披露**，按信息价值分配 token 预算：

1. **search** → 先找候选论文
2. **--brief** → 预览核心信息（标题、TL;DR、关键词），低成本判断论文价值
3. **--head** → 掌握全文结构与章节分布
4. **--section** → 按需读取 Introduction、Method、Experiments 等关键章节

**价值**：

- 降低 token 消耗
- 提升检索与阅读效率
- 支持复杂多步科研任务

## 典型工作流

### 工作流 1：进入新研究主题

```bash
# Step 1: 搜索候选论文
deepxiv search "agentic memory" --limit 20

# Step 2: 快速预览判断相关性
deepxiv paper 2506.07398 --brief

# Step 3: 查看结构
deepxiv paper 2506.07398 --head

# Step 4: 精读关键章节
deepxiv paper 2506.07398 --section Experiments
```

### 工作流 2：热点追踪

```bash
# Step 1: 抓取近一周热点
deepxiv trending --days 7 --limit 30 --json

# Step 2: 快速预览
deepxiv paper 2603.28767 --brief

# Step 3: 查看传播热度
deepxiv paper 2603.28767 --popularity
```

### 工作流 3：深度调研

```bash
# 一键深度调研
deepxiv agent query "过去三年关于 Agent Memory 的代表性工作有哪些？" --verbose
```

### 工作流 4：生成 Baseline 表格

```bash
# 搜索 + 批量预览 + 提取实验结果
deepxiv search "multimodal retrieval" --date-from 2025-01-01 --limit 50

# 对每篇论文
deepxiv paper {id} --brief
deepxiv paper {id} --section Experiments

# 整理成 markdown 表格
```

## API 端点

**基础 URL**: `https://data.rag.ac.cn/api`

**渐进式访问**:

- `/arxiv (type=head, id={id})` - 元信息 + 结构概览
- `/arxiv (type=preview, id={id})` - 固定长度前缀（10k chars）
- `/arxiv (type=section, id={id}, section={sec})` - 命名章节
- `/arxiv (type=raw, id={id})` - 完整 Markdown
- `/arxiv (type=json, id={id})` - 完整结构化 JSON

**检索**:

- `/arxiv (type=retrieve, q={...})` - BM25/向量/混合检索

**社交信号**:

- `/arxiv/trending_signal (id={id})` - Twitter 传播热度

## 与 Context Engineering 的协作

DeepXiv 的渐进式阅读理念与我们 Context Engineering 的设计高度契合：

| Context Engineering  | DeepXiv                      |
| -------------------- | ---------------------------- |
| 感知层（实时输入）   | --brief 预览                 |
| 短期层（任务上下文） | --head 结构 + --section 精读 |
| 长期层（持久记忆）   | 完整 JSON 存储               |

**协作模式**：

1. DeepXiv 提供结构化论文数据
2. Context Engineering 提供记忆管理与状态追踪
3. 结合实现"科研 Agent 的长期记忆"

## 技术细节

**PDF → Markdown 转换**：

- 使用 MinerU，8 × 8×H100 GPU 跑 72 小时处理全量 ArXiv

**LLM 增强**：

- Qwen34B-Instruct-2507 提取作者-机构关系、TL;DR、关键词

**混合检索**：

- BGE-m3 向量嵌入
- Elasticsearch 索引

**服务架构**：

- PostgreSQL（元数据）+ 对象存储（内容）
- Redis 缓存高频端点
- Gunicorn + Caddy 反向代理

## 资源链接

- **GitHub**: https://github.com/DeepXiv/deepxiv_sdk
- **PyPI**: https://pypi.org/project/deepxiv-sdk/
- **API 文档**: https://data.rag.ac.cn/api/docs
- **技术报告**: arXiv:2603.00084

## 注意事项

1. **需要注册获取 API Key**：访问 https://data.rag.ac.cn 注册
2. **Token 预算控制**：优先使用 --brief 和 --head，仅在必要时读取全文
3. **缓存策略**：频繁访问的论文建议本地缓存 JSON
