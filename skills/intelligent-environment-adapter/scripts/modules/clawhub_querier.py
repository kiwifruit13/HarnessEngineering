"""
ClawHub 查询建议生成器模块

职责：生成查询 ClawHub 的建议方案（仅生成建议，不执行真实 API 调用）

作为 Coze Skill 的候补选项，当 Coze 市场无法满足需求时，提供 ClawHub 查询建议
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ClawHubQuerySuggestion:
    """ClawHub 查询建议数据结构"""
    suggested_tags: List[str]           # 建议的能力标签
    suggested_keywords: List[str]       # 建议的搜索关键词
    query_parameters: Dict[str, Any]    # 建议的查询参数
    reasoning: str                      # 生成建议的理由
    fallback_skills: List[str]          # 本地候补技能列表


class ClawHubQuerySuggester:
    """
    ClawHub 查询建议生成器（仅生成方案，不执行 API 调用）

    职责边界：
    - 根据需求生成 ClawHub 查询建议
    - 提供候补技能列表（本地已有）
    - 不调用任何外部 API
    - 不需要任何凭证配置
    """

    # ClawHub 常见能力标签映射
    CAPABILITY_TAG_MAPPING = {
        # 知识类能力
        "knowledge": ["knowledge-base", "information-retrieval", "research", "domain-knowledge"],
        "法律": ["legal", "law", "compliance", "regulation"],
        "金融": ["finance", "trading", "investment", "banking", "fintech"],
        "技术": ["programming", "development", "engineering", "devops"],
        "医疗": ["healthcare", "medical", "diagnosis", "pharma"],
        "教育": ["education", "learning", "tutoring", "training"],
        
        # 技能类能力
        "skill": ["tool", "utility", "plugin", "addon"],
        "数据分析": ["data-analysis", "analytics", "statistics", "visualization"],
        "文档处理": ["document-processing", "parsing", "extraction", "ocr"],
        "图像处理": ["image-processing", "computer-vision", "image-generation"],
        "自然语言": ["nlp", "text-processing", "sentiment-analysis", "translation"],
        "API集成": ["api-integration", "webhooks", "integration"],
        
        # 编排类能力
        "orchestration": ["workflow", "automation", "orchestration", "pipeline"],
        "监控": ["monitoring", "logging", "alerting", "observability"],
        "调度": ["scheduling", "cron", "task-automation"],
        
        # 优化类能力
        "optimization": ["optimization", "tuning", "performance"],
        "缓存": ["caching", "memory", "acceleration"],
    }

    def __init__(self):
        pass

    def generate_query_suggestion(
        self,
        capability_tags: List[str],
        domain: Optional[str] = None,
        complexity: Optional[str] = None
    ) -> ClawHubQuerySuggestion:
        """
        根据能力标签生成 ClawHub 查询建议

        Args:
            capability_tags: 需要的能力标签列表
            domain: 领域（可选）
            complexity: 复杂度（可选）

        Returns:
            ClawHubQuerySuggestion: 查询建议
        """
        # 生成扩展的标签列表
        suggested_tags = self._expand_tags(capability_tags)
        
        # 生成搜索关键词
        suggested_keywords = self._generate_keywords(capability_tags, domain)
        
        # 生成查询参数
        query_parameters = {
            "tags": suggested_tags,
            "query": " ".join(suggested_keywords),
            "coze_compatible": True,  # 优先选择 Coze 兼容的工具
            "sort_by": "rating",       # 按评分排序
            "limit": 10
        }
        
        # 生成理由
        reasoning = self._generate_reasoning(capability_tags, domain, complexity)
        
        # 生成候补技能列表（本地已有）
        fallback_skills = self._get_local_fallbacks(capability_tags)

        return ClawHubQuerySuggestion(
            suggested_tags=suggested_tags,
            suggested_keywords=suggested_keywords,
            query_parameters=query_parameters,
            reasoning=reasoning,
            fallback_skills=fallback_skills
        )

    def _expand_tags(self, tags: List[str]) -> List[str]:
        """扩展能力标签"""
        expanded = []
        for tag in tags:
            expanded.append(tag)
            # 添加映射的标签
            mapped = self.CAPABILITY_TAG_MAPPING.get(tag, [])
            expanded.extend(mapped)
        # 去重
        return list(set(expanded))

    def _generate_keywords(
        self, 
        tags: List[str], 
        domain: Optional[str]
    ) -> List[str]:
        """生成搜索关键词"""
        keywords = list(tags)
        if domain:
            keywords.append(domain)
        return keywords

    def _generate_reasoning(
        self,
        tags: List[str],
        domain: Optional[str],
        complexity: Optional[str]
    ) -> str:
        """生成建议理由"""
        reasons = []
        if tags:
            reasons.append(f"需要能力: {', '.join(tags)}")
        if domain:
            reasons.append(f"领域: {domain}")
        if complexity:
            reasons.append(f"复杂度: {complexity}")
        return "；".join(reasons) if reasons else "通用查询"

    def _get_local_fallbacks(self, tags: List[str]) -> List[str]:
        """获取本地候补技能（示例）"""
        fallbacks = []
        for tag in tags:
            # 这里可以根据本地能力清单返回候补建议
            # 目前返回示例数据
            if tag == "数据分析":
                fallbacks.append("建议使用内置数据分析模块（模块B）")
            elif tag == "文档处理":
                fallbacks.append("建议使用内置文档处理能力")
        return fallbacks

    def suggest_alternative_searches(
        self,
        failed_queries: List[str]
    ) -> List[str]:
        """
        当查询失败时，提供替代搜索建议

        Args:
            failed_queries: 之前失败的查询列表

        Returns:
            替代搜索建议列表
        """
        alternatives = []
        
        for query in failed_queries:
            # 生成更通用的替代搜索
            alternatives.append(f"扩展搜索: {query} + related")
            alternatives.append(f"简化搜索: {' '.join(query.split()[:2])}")
        
        # 添加通用替代方案
        alternatives.extend([
            "尝试更通用的标签: tool, utility",
            "尝试更具体的标签: [具体领域] + tool",
            "使用分类浏览代替关键词搜索"
        ])
        
        return alternatives

    def convert_to_model_guidance(
        self, 
        suggestion: ClawHubQuerySuggestion
    ) -> str:
        """
        将查询建议转换为模型可以理解的指导文本

        Args:
            suggestion: 查询建议

        Returns:
            指导文本
        """
        guidance = f"""## ClawHub 查询建议

**建议查询参数：**
```json
{json.dumps(suggestion.query_parameters, ensure_ascii=False, indent=2)}
```

**推荐使用的查询标签：**
{', '.join(suggestion.suggested_tags)}

**搜索关键词：**
{', '.join(suggestion.suggested_keywords)}

**查询理由：**
{suggestion.reasoning}

**本地候补方案：**
"""
        if suggestion.fallback_skills:
            for fallback in suggestion.fallback_skills:
                guidance += f"- {fallback}\n"
        else:
            guidance += "无本地候补方案，建议继续在 ClawHub 查找\n"
        
        return guidance


def main():
    """命令行接口（用于测试）"""
    import argparse

    parser = argparse.ArgumentParser(description="ClawHub 查询建议生成器")
    parser.add_argument("--tags", help="能力标签（逗号分隔）")
    parser.add_argument("--domain", help="领域")
    parser.add_argument("--complexity", help="复杂度")
    parser.add_argument("--output", help="输出文件路径")

    args = parser.parse_args()

    suggester = ClawHubQuerySuggester()
    
    # 生成建议
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
    suggestion = suggester.generate_query_suggestion(
        capability_tags=tags,
        domain=args.domain,
        complexity=args.complexity
    )
    
    # 转换为模型指导文本
    guidance = suggester.convert_to_model_guidance(suggestion)

    # 输出
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(guidance)
        print(f"建议已保存到: {args.output}")
    else:
        print(guidance)


if __name__ == "__main__":
    main()
