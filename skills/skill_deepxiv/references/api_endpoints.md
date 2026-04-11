# DeepXiv API 端点速查表

**基础 URL**: `https://data.rag.ac.cn/api`

**认证方式**: Bearer Token

## 渐进式访问端点

| 端点 | 说明 | Token 成本 |
|------|------|-----------|
| `/arxiv?type=head&id={id}` | 元信息 + 结构概览 | 最低 |
| `/arxiv?type=preview&id={id}` | 固定长度前缀（10k chars） | 低 |
| `/arxiv?type=section&id={id}&section={sec}` | 命名章节 | 中 |
| `/arxiv?type=raw&id={id}` | 完整 Markdown | 高 |
| `/arxiv?type=json&id={id}` | 完整结构化 JSON | 最高 |

## 检索端点

```
POST /arxiv?type=retrieve
```

**请求体**:
```json
{
  "query": "agent memory",
  "limit": 20,
  "filters": {
    "date_from": "2026-01-01",
    "categories": ["cs.AI", "cs.CL"],
    "authors": ["author_name"]
  },
  "mode": "hybrid"  // "bm25" | "vector" | "hybrid"
}
```

**响应**:
```json
{
  "results": [
    {
      "arxiv_id": "2602.16493",
      "title": "Paper Title",
      "authors": ["Author 1", "Author 2"],
      "published_date": "2026-02-28",
      "categories": ["cs.AI"],
      "tl_dr": "One sentence summary",
      "score": 0.95
    }
  ],
  "total": 150
}
```

## 社交信号端点

```
GET /arxiv/trending_signal?id={id}
```

**响应**:
```json
{
  "arxiv_id": "2602.16493",
  "total_views": 1500,
  "total_likes": 120,
  "total_reposts": 45,
  "trending_score": 0.85
}
```

## 使用统计端点

```
GET /stats/usage?days={n}
```

**响应**:
```json
{
  "total_requests": 50000,
  "requests_by_endpoint": {
    "search": 20000,
    "brief": 15000,
    "section": 10000,
    "full": 5000
  },
  "quota_remaining": 45000
}
```

## PMC 扩展端点

```
GET /pmc?type=head&id={pmc_id}
GET /pmc?type=json&id={pmc_id}
```

## curl 示例

```bash
# 搜索论文
curl -X POST "https://data.rag.ac.cn/api/arxiv?type=retrieve" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "agent memory", "limit": 20}'

# 获取论文预览
curl "https://data.rag.ac.cn/api/arxiv?type=head&id=2602.16493" \
  -H "Authorization: Bearer YOUR_API_KEY"

# 获取章节
curl "https://data.rag.ac.cn/api/arxiv?type=section&id=2602.16493&section=Experiments" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## 错误码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（API Key 无效） |
| 404 | 论文不存在 |
| 429 | 请求频率超限 |
| 500 | 服务器错误 |

## 速率限制

- 搜索：100 次/分钟
- 预览：500 次/分钟
- 章节读取：200 次/分钟
- 全文获取：50 次/分钟
