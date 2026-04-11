"""
智能补全推荐引擎模块

职责：深度分析能力缺口，智能匹配技能，生成多方案补全推荐
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CapabilityGap:
    """能力缺口数据结构"""
    gap_id: str
    gap_type: str
    layer: str
    capability: str
    description: str
    impact_score: float  # 影响分数 0-1
    urgency_score: float  # 紧急分数 0-1
    dependency_count: int  # 依赖计数
    difficulty_score: float  # 难度分数 0-1
    priority_score: float  # 综合优先级分数 0-1


@dataclass
class SkillRecommendation:
    """技能推荐数据结构"""
    skill_id: str
    name: str
    description: str
    source: str  # coze 或 clawhub
    match_score: float  # 匹配分数 0-1
    cost_score: float  # 成本分数 0-1（越低越好）
    feasibility_score: float  # 可行性分数 0-1
    priority: int  # 优先级 1-3
    install_steps: List[str]
    estimated_time: str
    cost: str
    expected_improvement: float


@dataclass
class RemedyPlan:
    """补全方案数据结构"""
    plan_type: str  # primary, alternative, quick_fix
    recommended_skills: List[SkillRecommendation]
    implementation_steps: List[str]
    expected_improvement: float
    estimated_time: str
    risk_level: str  # low, medium, high
    total_cost: str


class IntelligentRemedyRecommender:
    """
    智能补全推荐引擎（模块M）

    职责边界：
    - 深度分析能力缺口，评估优先级
    - 智能匹配技能（集成技能查询协调器）
    - 生成多方案补全推荐
    - 规划实施路径
    - 不执行补全操作
    """

    def __init__(self):
        self.skill_query_coordinator = None
        self.learning_database = {}  # 学习数据库

    def set_skill_query_coordinator(self, coordinator):
        """设置技能查询协调器"""
        self.skill_query_coordinator = coordinator

    def load_learning_database(self, db_path: str):
        """加载学习数据库"""
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                self.learning_database = json.load(f)
        except Exception as e:
            print(f"加载学习数据库失败: {e}")
            self.learning_database = {}

    def generate_remedy_recommendations(
        self,
        diagnostic_report: Dict[str, Any],
        environment_profile: Dict[str, Any],
        strategy: str = "balanced"
    ) -> Dict[str, Any]:
        """
        生成补全推荐方案

        Args:
            diagnostic_report: 诊断报告（模块C输出）
            environment_profile: 环境画像（模块A输出）
            strategy: 推荐策略
                - balanced: 平衡方案（默认）
                - quality优先质量
                - cost优先成本
                - speed优先速度

        Returns:
            推荐方案
        """
        # 1. 分析能力缺口
        gaps = self._analyze_capability_gaps(
            diagnostic_report,
            environment_profile
        )

        # 2. 查询候选技能
        candidate_skills = self._query_candidate_skills(gaps)

        # 3. 计算技能匹配度
        matched_skills = self._calculate_skill_matching(
            gaps,
            candidate_skills
        )

        # 4. 生成多个方案
        primary_plan = self._generate_primary_plan(
            gaps,
            matched_skills,
            strategy
        )
        alternative_plan = self._generate_alternative_plan(
            gaps,
            matched_skills,
            strategy
        )
        quick_fix_plan = self._generate_quick_fix_plan(
            gaps,
            matched_skills,
            strategy
        )

        # 5. 生成推荐
        return {
            "gap_analysis": {
                "total_gaps": len(gaps),
                "high_priority_gaps": len([g for g in gaps if g.priority_score >= 0.7]),
                "gaps": [self._gap_to_dict(g) for g in gaps]
            },
            "recommendations": {
                "primary_plan": self._plan_to_dict(primary_plan),
                "alternative_plan": self._plan_to_dict(alternative_plan),
                "quick_fix_plan": self._plan_to_dict(quick_fix_plan)
            },
            "strategy": strategy,
            "generated_at": datetime.now().isoformat()
        }

    def _analyze_capability_gaps(
        self,
        diagnostic_report: Dict[str, Any],
        environment_profile: Dict[str, Any]
    ) -> List[CapabilityGap]:
        """
        分析能力缺口

        Args:
            diagnostic_report: 诊断报告
            environment_profile: 环境画像

        Returns:
            能力缺口列表
        """
        gaps = []

        # 从诊断报告中提取短板
        shortages = diagnostic_report.get("shortages", [])

        for idx, shortage in enumerate(shortages):
            # 计算影响分数（简化版）
            impact_score = shortage.get("severity", 0.5)

            # 计算紧急分数（基于任务类型）
            task_type = environment_profile.get("task_type", "")
            urgency_score = self._calculate_urgency(task_type)

            # 依赖计数（简化版）
            dependency_count = shortage.get("affects", 0)

            # 难度分数（简化版）
            difficulty_score = shortage.get("difficulty", 0.5)

            # 综合优先级分数
            priority_score = (
                0.4 * impact_score +
                0.3 * urgency_score +
                0.2 * min(dependency_count / 5.0, 1.0) +
                0.1 * (1.0 - difficulty_score)
            )

            gap = CapabilityGap(
                gap_id=f"gap_{idx}",
                gap_type=shortage.get("type", "unknown"),
                layer=shortage.get("layer", "unknown"),
                capability=shortage.get("capability", ""),
                description=shortage.get("description", ""),
                impact_score=impact_score,
                urgency_score=urgency_score,
                dependency_count=dependency_count,
                difficulty_score=difficulty_score,
                priority_score=priority_score
            )

            gaps.append(gap)

        # 按优先级排序
        gaps.sort(key=lambda x: x.priority_score, reverse=True)

        return gaps

    def _calculate_urgency(self, task_type: str) -> float:
        """计算紧急分数"""
        if task_type == "实时监控":
            return 0.9
        elif task_type == "问题解决":
            return 0.8
        elif task_type == "深度分析":
            return 0.5
        elif task_type == "信息检索":
            return 0.6
        else:
            return 0.5

    def _query_candidate_skills(
        self,
        gaps: List[CapabilityGap]
    ) -> List[Dict[str, Any]]:
        """
        查询候选技能

        Args:
            gaps: 能力缺口列表

        Returns:
            候选技能列表
        """
        if not self.skill_query_coordinator:
            return []

        # 提取所有能力标签
        capability_tags = list(set([gap.capability for gap in gaps]))

        # 查询技能
        try:
            result = self.skill_query_coordinator.query_skills(
                capability_tags=capability_tags,
                strategy="coze_first"
            )
            return result.aggregated_skills
        except Exception as e:
            print(f"查询技能失败: {e}")
            return []

    def _calculate_skill_matching(
        self,
        gaps: List[CapabilityGap],
        candidate_skills: List[Dict[str, Any]]
    ) -> Dict[str, List[SkillRecommendation]]:
        """
        计算技能匹配度

        Args:
            gaps: 能力缺口列表
            candidate_skills: 候选技能列表

        Returns:
            {缺口ID: [匹配的技能]}
        """
        gap_skills_map = {}

        for gap in gaps:
            matched_skills = []

            for skill in candidate_skills:
                # 计算匹配度
                match_score = self._calculate_match_score(gap, skill)

                # 只保留高匹配度的技能
                if match_score >= 0.6:
                    # 计算成本和可行性
                    cost_score = self._calculate_cost_score(skill)
                    feasibility_score = self._calculate_feasibility_score(skill)

                    # 优先级（综合分数）
                    priority = 3 if match_score >= 0.8 else (2 if match_score >= 0.7 else 1)

                    # 预期改善
                    expected_improvement = match_score * gap.priority_score

                    recommendation = SkillRecommendation(
                        skill_id=skill.get("skill_id", ""),
                        name=skill.get("name", ""),
                        description=skill.get("description", ""),
                        source=skill.get("source", ""),
                        match_score=match_score,
                        cost_score=cost_score,
                        feasibility_score=feasibility_score,
                        priority=priority,
                        install_steps=self._generate_install_steps(skill),
                        estimated_time=self._estimate_install_time(skill),
                        cost=skill.get("cost", "未知"),
                        expected_improvement=expected_improvement
                    )

                    matched_skills.append(recommendation)

            # 按匹配度排序
            matched_skills.sort(key=lambda x: x.match_score, reverse=True)

            # 取前5个
            gap_skills_map[gap.gap_id] = matched_skills[:5]

        return gap_skills_map

    def _calculate_match_score(
        self,
        gap: CapabilityGap,
        skill: Dict[str, Any]
    ) -> float:
        """
        计算技能匹配度

        Args:
            gap: 能力缺口
            skill: 技能信息

        Returns:
            匹配分数 0-1
        """
        # 1. 标签匹配度（60%）
        skill_capabilities = skill.get("capabilities", [])
        tag_match = 0.6 if gap.capability in skill_capabilities else 0.0

        # 2. 描述相似度（30%）- 简化版
        desc_match = 0.0
        gap_desc = gap.description.lower()
        skill_desc = skill.get("description", "").lower()
        if gap_desc and skill_desc:
            common_words = set(gap_desc.split()) & set(skill_desc.split())
            desc_match = 0.3 * len(common_words) / max(len(gap_desc.split()), 1)

        # 3. 历史成功率（10%）- 从学习数据库获取
        history_success = 0.1 * self._get_history_success_rate(skill.get("skill_id", ""))

        return min(tag_match + desc_match + history_success, 1.0)

    def _get_history_success_rate(self, skill_id: str) -> float:
        """获取历史成功率"""
        skill_record = self.learning_database.get(skill_id, {})
        success_count = skill_record.get("success_count", 0)
        total_count = skill_record.get("total_count", 1)
        return success_count / total_count if total_count > 0 else 0.5

    def _calculate_cost_score(self, skill: Dict[str, Any]) -> float:
        """计算成本分数（越低越好）"""
        cost = skill.get("cost", "未知")
        if cost == "免费":
            return 0.0
        elif cost == "低成本":
            return 0.3
        elif cost == "中等成本":
            return 0.6
        else:
            return 1.0

    def _calculate_feasibility_score(self, skill: Dict[str, Any]) -> float:
        """计算可行性分数"""
        coze_compatible = skill.get("coze_compatible", True)
        needs_adaptation = skill.get("needs_adaptation", False)

        if coze_compatible and not needs_adaptation:
            return 1.0
        elif coze_compatible and needs_adaptation:
            return 0.7
        else:
            return 0.4

    def _generate_install_steps(self, skill: Dict[str, Any]) -> List[str]:
        """生成安装步骤"""
        steps = []

        # 基本安装
        install_command = skill.get("install_command", "")
        if install_command:
            steps.append(f"执行: {install_command}")

        # 配置
        if skill.get("needs_configuration", False):
            steps.append("配置技能参数")

        # 适配
        needs_adaptation = skill.get("needs_adaptation", False)
        if needs_adaptation:
            steps.append("适配技能到 Coze 环境")

        return steps if steps else ["直接使用"]

    def _estimate_install_time(self, skill: Dict[str, Any]) -> str:
        """估算安装时间"""
        needs_adaptation = skill.get("needs_adaptation", False)
        if needs_adaptation:
            return "10-15分钟"
        else:
            return "3-5分钟"

    def _generate_primary_plan(
        self,
        gaps: List[CapabilityGap],
        matched_skills: Dict[str, List[SkillRecommendation]],
        strategy: str
    ) -> RemedyPlan:
        """生成最优方案"""
        selected_skills = []

        # 选择高优先级的技能
        for gap in gaps[:3]:  # 前3个高优先级缺口
            skills = matched_skills.get(gap.gap_id, [])
            if skills:
                selected_skills.append(skills[0])  # 取最匹配的

        # 生成实施步骤
        implementation_steps = self._generate_implementation_steps(
            selected_skills,
            strategy
        )

        # 计算预期改善
        expected_improvement = sum([s.expected_improvement for s in selected_skills]) / len(selected_skills) if selected_skills else 0.0

        return RemedyPlan(
            plan_type="primary",
            recommended_skills=selected_skills,
            implementation_steps=implementation_steps,
            expected_improvement=expected_improvement,
            estimated_time="20-30分钟",
            risk_level="low",
            total_cost="免费（使用官方技能）"
        )

    def _generate_alternative_plan(
        self,
        gaps: List[CapabilityGap],
        matched_skills: Dict[str, List[SkillRecommendation]],
        strategy: str
    ) -> RemedyPlan:
        """生成备选方案"""
        selected_skills = []

        # 选择次优技能
        for gap in gaps[:3]:
            skills = matched_skills.get(gap.gap_id, [])
            if len(skills) > 1:
                selected_skills.append(skills[1])  # 取第二匹配的
            elif skills:
                selected_skills.append(skills[0])

        implementation_steps = self._generate_implementation_steps(
            selected_skills,
            strategy
        )

        expected_improvement = sum([s.expected_improvement for s in selected_skills]) / len(selected_skills) if selected_skills else 0.0

        return RemedyPlan(
            plan_type="alternative",
            recommended_skills=selected_skills,
            implementation_steps=implementation_steps,
            expected_improvement=expected_improvement * 0.9,
            estimated_time="15-25分钟",
            risk_level="medium",
            total_cost="低成本"
        )

    def _generate_quick_fix_plan(
        self,
        gaps: List[CapabilityGap],
        matched_skills: Dict[str, List[SkillRecommendation]],
        strategy: str
    ) -> RemedyPlan:
        """生成快速方案"""
        selected_skills = []

        # 选择最容易安装的技能
        for gap in gaps[:2]:  # 只处理前2个缺口
            skills = matched_skills.get(gap.gap_id, [])
            # 选择可行性最高的
            if skills:
                easy_skills = sorted(skills, key=lambda x: x.feasibility_score, reverse=True)
                selected_skills.append(easy_skills[0])

        implementation_steps = self._generate_implementation_steps(
            selected_skills,
            strategy
        )

        expected_improvement = sum([s.expected_improvement for s in selected_skills]) / len(selected_skills) if selected_skills else 0.0

        return RemedyPlan(
            plan_type="quick_fix",
            recommended_skills=selected_skills,
            implementation_steps=implementation_steps,
            expected_improvement=expected_improvement * 0.7,
            estimated_time="5-10分钟",
            risk_level="low",
            total_cost="免费"
        )

    def _generate_implementation_steps(
        self,
        skills: List[SkillRecommendation],
        strategy: str
    ) -> List[str]:
        """生成实施步骤"""
        steps = []

        if not skills:
            return ["无需补全"]

        # 步骤1：准备
        steps.append("1. 评估补全需求和可行性")

        # 步骤2：安装技能
        for idx, skill in enumerate(skills):
            steps.append(f"2.{idx + 1}. 安装技能: {skill.name}")
            steps.extend([f"   - {step}" for step in skill.install_steps])

        # 步骤3：配置和测试
        steps.append("3. 配置技能参数")
        steps.append("4. 测试技能功能")

        # 步骤5：验证
        steps.append("5. 验证补全效果")

        return steps

    def _gap_to_dict(self, gap: CapabilityGap) -> Dict[str, Any]:
        """将缺口对象转换为字典"""
        return {
            "gap_id": gap.gap_id,
            "gap_type": gap.gap_type,
            "layer": gap.layer,
            "capability": gap.capability,
            "description": gap.description,
            "impact_score": gap.impact_score,
            "urgency_score": gap.urgency_score,
            "dependency_count": gap.dependency_count,
            "difficulty_score": gap.difficulty_score,
            "priority_score": gap.priority_score
        }

    def _plan_to_dict(self, plan: RemedyPlan) -> Dict[str, Any]:
        """将方案对象转换为字典"""
        return {
            "plan_type": plan.plan_type,
            "recommended_skills": [
                {
                    "skill_id": s.skill_id,
                    "name": s.name,
                    "description": s.description,
                    "source": s.source,
                    "match_score": s.match_score,
                    "priority": s.priority,
                    "install_steps": s.install_steps,
                    "estimated_time": s.estimated_time,
                    "cost": s.cost,
                    "expected_improvement": s.expected_improvement
                }
                for s in plan.recommended_skills
            ],
            "implementation_steps": plan.implementation_steps,
            "expected_improvement": plan.expected_improvement,
            "estimated_time": plan.estimated_time,
            "risk_level": plan.risk_level,
            "total_cost": plan.total_cost
        }


def main():
    """命令行接口（用于测试）"""
    import argparse

    parser = argparse.ArgumentParser(description="智能补全推荐引擎")
    parser.add_argument("--diagnostic-report", required=True, help="诊断报告JSON文件")
    parser.add_argument("--environment-profile", required=True, help="环境画像JSON文件")
    parser.add_argument("--strategy", default="balanced",
                       choices=["balanced", "quality", "cost", "speed"],
                       help="推荐策略")
    parser.add_argument("--learning-db", help="学习数据库JSON文件")
    parser.add_argument("--output", required=True, help="输出文件路径")

    args = parser.parse_args()

    # 创建推荐器
    recommender = IntelligentRemedyRecommender()

    # 加载数据
    with open(args.diagnostic_report, 'r', encoding='utf-8') as f:
        diagnostic_report = json.load(f)

    with open(args.environment_profile, 'r', encoding='utf-8') as f:
        environment_profile = json.load(f)

    # 加载学习数据库（可选）
    if args.learning_db:
        recommender.load_learning_database(args.learning_db)

    # 生成推荐
    recommendations = recommender.generate_remedy_recommendations(
        diagnostic_report,
        environment_profile,
        strategy=args.strategy
    )

    # 输出结果
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(recommendations, f, ensure_ascii=False, indent=2)

    print(f"推荐方案已生成: {args.output}")
    print(f"缺口总数: {recommendations['gap_analysis']['total_gaps']}")
    print(f"高优先级缺口: {recommendations['gap_analysis']['high_priority_gaps']}")


if __name__ == "__main__":
    main()
