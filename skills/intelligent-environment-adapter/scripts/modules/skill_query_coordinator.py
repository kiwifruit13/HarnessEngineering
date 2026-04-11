"""
智能技能查询协调器模块

职责：协调 Coze 技能市场和 ClawHub 的查询，实现智能降级和候补策略
优先使用 Coze 技能市场，不足时从 ClawHub 生成查询方案
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class SkillQueryResult:
    """技能查询结果"""
    coze_skills: List[Dict[str, Any]]
    clawhub_skills: List[Dict[str, Any]]
    aggregated_skills: List[Dict[str, Any]]
    query_strategy: str
    match_count: int
    recommendation: str


class SkillQueryCoordinator:
    """
    智能技能查询协调器

    职责边界：
    - 协调 Coze 和 ClawHub 的查询
    - 实现智能降级策略
    - 聚合和去重结果
    - 提供推荐建议
    """

    def __init__(self):
        self.coze_querier = None  # Coze 技能市场查询器（待实现）
        self.clawhub_querier = None  # ClawHub 查询建议生成器

    def set_coze_querier(self, coze_querier):
        """设置 Coze 查询器"""
        self.coze_querier = coze_querier

    def set_clawhub_querier(self, clawhub_querier):
        """设置 ClawHub 查询器"""
        self.clawhub_querier = clawhub_querier

    def query_skills(
        self,
        capability_tags: List[str],
        strategy: str = "coze_first",
        min_match_count: int = 3,
        min_coze_score: float = 0.7
    ) -> SkillQueryResult:
        """
        查询技能（智能降级策略）

        Args:
            capability_tags: 能力标签列表
            strategy: 查询策略
                - coze_first: 优先 Coze，不足时生成 ClawHub 查询方案
                - coze_only: 仅查询 Coze
                - clawhub_first: 生成 ClawHub 查询方案
                - all: 同时查询所有来源
            min_match_count: 最小匹配数量
            min_coze_score: Coze 技能最小匹配分数

        Returns:
            SkillQueryResult: 查询结果
        """
        coze_skills = []
        clawhub_skills = []

        # 根据策略查询
        if strategy == "coze_first":
            # 优先 Coze
            if self.coze_querier:
                coze_skills = self._query_coze(capability_tags)

            # 评估是否需要生成 ClawHub 查询方案
            need_clawhub = self._should_query_clawhub(
                coze_skills, min_match_count, min_coze_score
            )

            if need_clawhub and self.clawhub_querier:
                clawhub_skills = self._query_clawhub(capability_tags, coze_skills)

        elif strategy == "coze_only":
            # 仅查询 Coze
            if self.coze_querier:
                coze_skills = self._query_coze(capability_tags)

        elif strategy == "clawhub_first":
            # 生成 ClawHub 查询方案
            if self.clawhub_querier:
                clawhub_skills = self._query_clawhub(capability_tags, [])

            # 补充 Coze
            if self.coze_querier:
                coze_skills = self._query_coze(capability_tags)

        elif strategy == "all":
            # 同时查询所有来源
            if self.coze_querier:
                coze_skills = self._query_coze(capability_tags)
            if self.clawhub_querier:
                clawhub_skills = self._query_clawhub(capability_tags, coze_skills)

        # 聚合结果
        aggregated_skills = self._aggregate_skills(coze_skills, clawhub_skills)

        # 生成推荐
        recommendation = self._generate_recommendation(
            coze_skills, clawhub_skills, aggregated_skills
        )

        return SkillQueryResult(
            coze_skills=coze_skills,
            clawhub_skills=clawhub_skills,
            aggregated_skills=aggregated_skills,
            query_strategy=strategy,
            match_count=len(aggregated_skills),
            recommendation=recommendation
        )

    def _should_query_clawhub(
        self,
        coze_skills: List[Dict[str, Any]],
        min_match_count: int,
        min_coze_score: float
    ) -> bool:
        """
        判断是否需要生成 ClawHub 查询方案

        Args:
            coze_skills: Coze 技能列表
            min_match_count: 最小匹配数量
            min_coze_score: 最小匹配分数

        Returns:
            是否需要查询 ClawHub
        """
        # 条件1: Coze 技能数量不足
        if len(coze_skills) < min_match_count:
            return True

        # 条件2: Coze 技能质量不高
        high_quality_count = sum(
            1 for skill in coze_skills
            if skill.get("match_score", 0) >= min_coze_score
        )
        if high_quality_count < min_match_count:
            return True

        return False

    def _query_coze(self, capability_tags: List[str]) -> List[Dict[str, Any]]:
        """
        查询 Coze 技能市场

        Args:
            capability_tags: 能力标签列表

        Returns:
            Coze 技能列表
        """
        if not self.coze_querier:
            return []

        try:
            skills = self.coze_querier.query_by_capabilities(capability_tags)
            # 标记优先级
            for skill in skills:
                skill["priority"] = 1  # Coze 优先级为 1
            return skills
        except Exception as e:
            print(f"查询 Coze 技能市场失败: {e}")
            return []

    def _query_clawhub(
        self,
        capability_tags: List[str],
        existing_skills: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        生成 ClawHub 查询方案（不执行真实 API 调用）

        Args:
            capability_tags: 能力标签列表
            existing_skills: 已存在的技能列表

        Returns:
            ClawHub 查询建议列表（方案而非结果）
        """
        if not self.clawhub_querier:
            return []

        try:
            # 判断 querier 类型
            if hasattr(self.clawhub_querier, 'generate_query_suggestion'):
                # ClawHubQuerySuggester：生成查询建议（仅方案）
                suggestion = self.clawhub_querier.generate_query_suggestion(capability_tags)
                
                # 将建议转换为技能格式（作为方案输出）
                skills = [{
                    "skill_id": f"clawhub_suggestion_{tag}",
                    "name": f"ClawHub 查询方案: {tag}",
                    "description": suggestion.reasoning,
                    "capabilities": suggestion.suggested_tags,
                    "source": "clawhub_suggestion",
                    "priority": 2,
                    "query_parameters": suggestion.query_parameters
                } for tag in capability_tags]
                
            else:
                # 旧版 ClawHubQuerier：执行真实 API 调用（已废弃）
                tools = self.clawhub_querier.query_tools_by_capability(capability_tags)
                skills = [self.clawhub_querier.convert_to_coze_skill_format(tool) for tool in tools]

            # 去重：排除已存在的技能
            existing_ids = {skill.get("skill_id") for skill in existing_skills}
            skills = [skill for skill in skills if skill.get("skill_id") not in existing_ids]

            return skills
        except Exception as e:
            print(f"生成 ClawHub 查询建议失败: {e}")
            return []

    def _aggregate_skills(
        self,
        coze_skills: List[Dict[str, Any]],
        clawhub_skills: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        聚合技能（去重和排序）

        Args:
            coze_skills: Coze 技能列表
            clawhub_skills: ClawHub 技能列表

        Returns:
            聚合后的技能列表
        """
        # 合并
        all_skills = coze_skills + clawhub_skills

        # 去重（按 skill_id）
        seen = {}
        for skill in all_skills:
            skill_id = skill.get("skill_id")
            if skill_id and skill_id not in seen:
                seen[skill_id] = skill

        # 排序：优先级 > 评分 > 下载量
        sorted_skills = sorted(
            seen.values(),
            key=lambda x: (
                x.get("priority", 999),
                x.get("rating", 0),
                x.get("downloads", 0)
            ),
            reverse=False  # 优先级越小越好
        )

        return sorted_skills

    def _generate_recommendation(
        self,
        coze_skills: List[Dict[str, Any]],
        clawhub_skills: List[Dict[str, Any]],
        aggregated_skills: List[Dict[str, Any]]
    ) -> str:
        """
        生成推荐建议

        Args:
            coze_skills: Coze 技能列表
            clawhub_skills: ClawHub 技能列表
            aggregated_skills: 聚合技能列表

        Returns:
            推荐建议文本
        """
        recommendations = []

        # Coze 技能推荐
        if coze_skills:
            coze_count = len(coze_skills)
            recommendations.append(f"✅ 找到 {coze_count} 个 Coze 官方技能（优先推荐）")

        # ClawHub 技能推荐
        if clawhub_skills:
            clawhub_count = len(clawhub_skills)
            compatible_count = sum(
                1 for skill in clawhub_skills
                if skill.get("coze_compatible", False)
            )
            suggestions = sum(
                1 for skill in clawhub_skills
                if skill.get("source") == "clawhub_suggestion"
            )
            if suggestions > 0:
                recommendations.append(
                    f"💡 生成了 {suggestions} 个 ClawHub 查询方案（可手动查询获取详情）"
                )
            else:
                recommendations.append(
                    f"⚡ 找到 {clawhub_count} 个 ClawHub 社区技能"
                    f"（其中 {compatible_count} 个可直接使用）"
                )

        # 总体推荐
        if aggregated_skills:
            recommendations.append(
                f"🎯 共 {len(aggregated_skills)} 个匹配技能/方案"
            )
        else:
            recommendations.append(
                "⚠️ 未找到匹配技能，建议调整能力需求或手动构建"
            )

        return "\n".join(recommendations)


def main():
    """命令行接口（用于测试）"""
    import argparse

    parser = argparse.ArgumentParser(description="智能技能查询协调器")
    parser.add_argument("--capabilities", required=True, help="能力标签（逗号分隔）")
    parser.add_argument("--strategy", default="coze_first",
                       choices=["coze_first", "coze_only", "clawhub_first", "all"],
                       help="查询策略")
    parser.add_argument("--min-match", type=int, default=3, help="最小匹配数量")
    parser.add_argument("--min-score", type=float, default=0.7, help="最小匹配分数")
    parser.add_argument("--output", help="输出文件路径")

    args = parser.parse_args()

    # 创建协调器
    coordinator = SkillQueryCoordinator()

    # 设置查询器（这里使用模拟数据，实际使用时需要真实的查询器）
    # coordinator.set_coze_querier(CozeMarketQuerier())
    # coordinator.set_clawhub_querier(ClawHubQuerySuggester())

    # 解析能力标签
    capability_tags = [tag.strip() for tag in args.capabilities.split(",")]

    # 查询技能
    result = coordinator.query_skills(
        capability_tags=capability_tags,
        strategy=args.strategy,
        min_match_count=args.min_match,
        min_coze_score=args.min_score
    )

    # 输出结果
    output_data = {
        "query_strategy": result.query_strategy,
        "match_count": result.match_count,
        "recommendation": result.recommendation,
        "coze_skills_count": len(result.coze_skills),
        "clawhub_skills_count": len(result.clawhub_skills),
        "aggregated_skills": result.aggregated_skills
    }

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到: {args.output}")
    else:
        print(f"推荐建议:\n{result.recommendation}")
        print(f"\n聚合技能: {len(result.aggregated_skills)} 个")
        print(json.dumps(output_data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
