#!/usr/bin/env python3
"""
天赋匹配器 - 基于任务特征智能匹配最佳天赋

核心功能：
- 基于多维特征进行天赋匹配
- 使用加权评分算法计算匹配度
- 支持最佳匹配和Top-N匹配
- 提供详细的匹配分数分析
"""

import os
import sys
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from talent_loader import TalentConstraint, load_talent_library
from task_feature_extractor import TaskFeatures


@dataclass
class MatchResult:
    """匹配结果"""
    talent: TalentConstraint
    score: float
    details: Dict[str, float] = field(default_factory=dict)


class TalentMatcher:
    """天赋匹配器"""

    def __init__(self, talent_library: Optional[List[TalentConstraint]] = None):
        """
        初始化匹配器

        Args:
            talent_library: 天赋库，如果为None则加载内置天赋库
        """
        if talent_library is None:
            self.talent_library = load_talent_library()
        else:
            self.talent_library = talent_library

        self._build_talent_profiles()

    def _build_talent_profiles(self):
        """构建天赋画像（优化匹配性能）"""
        self.talent_profiles = {}

        for talent in self.talent_library:
            profile = {
                "talent_id": talent.talent_id,
                "talent_name": talent.talent_name,
                "applicable_task_types": self._extract_applicable_task_types(talent),
                "applicable_complexity": self._extract_applicable_complexity(talent),
                "applicable_formats": self._extract_applicable_formats(talent),
                "applicable_domains": self._extract_applicable_domains(talent),
                "core_ability": talent.core_ability,
                "priority": talent.priority
            }
            self.talent_profiles[talent.talent_id] = profile

    def _extract_applicable_task_types(self, talent: TalentConstraint) -> List[str]:
        """提取天赋适用的任务类型"""
        applicable = []

        talent_name = talent.talent_name
        best_scenario = talent.best_scenario
        core_ability = talent.core_ability

        # 基于天赋名称和能力的关键词匹配
        keywords_map = {
            "分析": ["分析", "洞察", "推理", "逻辑", "评估", "诊断"],
            "创作": ["创作", "创意", "想象", "设计", "创新", "构思"],
            "规划": ["规划", "决策", "战略", "布局", "组织", "安排"],
            "沟通": ["表达", "沟通", "倾听", "交流", "说服", "演说"],
            "学习": ["学习", "研究", "探索", "发现", "理解", "掌握"],
            "执行": ["执行", "行动", "效率", "实施", "落地", "推进"],
            "审查": ["审查", "判断", "评估", "检查", "验证", "审核"]
        }

        for task_type, keywords in keywords_map.items():
            if any(keyword in talent_name or keyword in core_ability for keyword in keywords):
                applicable.append(task_type)

        # 如果没有匹配到，默认添加分析
        if not applicable:
            applicable.append("分析")

        return applicable

    def _extract_applicable_complexity(self, talent: TalentConstraint) -> List[str]:
        """提取天赋适用的复杂度"""
        if talent.priority >= 8:
            return ["复杂", "中等", "简单"]
        elif talent.priority >= 5:
            return ["中等", "简单"]
        else:
            return ["简单"]

    def _extract_applicable_formats(self, talent: TalentConstraint) -> List[str]:
        """提取天赋适用的输出格式"""
        formats = []

        core_ability = talent.core_ability

        if "结构" in core_ability or "框架" in core_ability:
            formats.append("结构化")
        if "创意" in core_ability or "想象" in core_ability:
            formats.append("创意")
        if "分析" in core_ability or "数据" in core_ability:
            formats.append("数据")
        if "文本" in core_ability or "文字" in core_ability:
            formats.append("文字")

        return formats if formats else ["文字"]

    def _extract_applicable_domains(self, talent: TalentConstraint) -> List[str]:
        """提取天赋适用的领域"""
        # 默认通用，特定天赋可以指定
        return ["通用"]

    def match_best(self, task_features: TaskFeatures) -> Optional[Tuple[TalentConstraint, float]]:
        """
        匹配最佳天赋

        Args:
            task_features: 任务特征

        Returns:
            (最佳天赋, 匹配分数) 或 None（如果没有匹配）
        """
        results = self.match_all(task_features, top_n=1)
        if results:
            result = results[0]
            return (result.talent, result.score)
        return None

    def match_all(
        self,
        task_features: TaskFeatures,
        top_n: int = 10,
        min_score: float = 0.3
    ) -> List[MatchResult]:
        """
        匹配所有天赋（按分数排序）

        Args:
            task_features: 任务特征
            top_n: 返回前N个结果
            min_score: 最低匹配分数阈值

        Returns:
            匹配结果列表（按分数降序）
        """
        scored_results = []

        for talent in self.talent_library:
            profile = self.talent_profiles[talent.talent_id]
            score, details = self._calculate_match_score(task_features, profile, talent)

            if score >= min_score:
                result = MatchResult(
                    talent=talent,
                    score=score,
                    details=details
                )
                scored_results.append(result)

        # 按分数排序
        scored_results.sort(key=lambda x: x.score, reverse=True)

        # 返回Top-N
        return scored_results[:top_n]

    def _calculate_match_score(
        self,
        task_features: TaskFeatures,
        profile: Dict,
        talent: TalentConstraint
    ) -> Tuple[float, Dict[str, float]]:
        """
        计算匹配分数（加权评分算法）

        权重分配：
        - 任务类型匹配：0.4
        - 复杂度匹配：0.2
        - 输出格式匹配：0.2
        - 优先级加成：0.2

        Args:
            task_features: 任务特征
            profile: 天赋画像
            talent: 天赋约束

        Returns:
            (总分, 详细分数)
        """
        details = {}
        total_score = 0.0

        # 1. 任务类型匹配（权重：0.4）
        task_type_str = task_features.task_type.value
        type_score = 0.0
        if task_type_str in profile["applicable_task_types"]:
            type_score = 0.4
        elif "分析" in profile["applicable_task_types"]:
            # 分析类型可以作为通用默认
            type_score = 0.2
        details["task_type_match"] = type_score
        total_score += type_score

        # 2. 复杂度匹配（权重：0.2）
        complexity_str = task_features.complexity.value
        complexity_score = 0.0
        if complexity_str in profile["applicable_complexity"]:
            complexity_score = 0.2
        elif "中等" in profile["applicable_complexity"]:
            # 中等复杂度可以作为默认匹配
            complexity_score = 0.1
        details["complexity_match"] = complexity_score
        total_score += complexity_score

        # 3. 输出格式匹配（权重：0.2）
        format_str = task_features.output_format.value
        format_score = 0.0
        if format_str in profile["applicable_formats"]:
            format_score = 0.2
        elif "文字" in profile["applicable_formats"]:
            # 文字可以作为默认匹配
            format_score = 0.1
        details["format_match"] = format_score
        total_score += format_score

        # 4. 优先级加成（权重：0.2）
        priority_score = talent.priority / 10.0 * 0.2
        details["priority_bonus"] = priority_score
        total_score += priority_score

        return total_score, details

    def get_talent_by_id(self, talent_id: str) -> Optional[TalentConstraint]:
        """
        根据ID获取天赋

        Args:
            talent_id: 天赋ID

        Returns:
            天赋对象或None
        """
        for talent in self.talent_library:
            if talent.talent_id == talent_id:
                return talent
        return None

    def get_all_talents(self) -> List[TalentConstraint]:
        """
        获取所有天赋

        Returns:
            天赋列表
        """
        return self.talent_library.copy()

    def get_talents_by_domain(self, domain: str) -> List[TalentConstraint]:
        """
        根据领域获取天赋

        Args:
            domain: 领域名称

        Returns:
            天赋列表
        """
        return [
            talent for talent in self.talent_library
            if domain in self.talent_profiles[talent.talent_id]["applicable_domains"]
        ]


# 便捷函数
def match_best_talent(task_features: TaskFeatures) -> Optional[Tuple[TalentConstraint, float]]:
    """
    匹配最佳天赋（便捷函数）

    Args:
        task_features: 任务特征

    Returns:
        (最佳天赋, 匹配分数) 或 None
    """
    matcher = TalentMatcher()
    return matcher.match_best(task_features)


def match_all_talents(
    task_features: TaskFeatures,
    top_n: int = 10,
    min_score: float = 0.3
) -> List[MatchResult]:
    """
    匹配所有天赋（便捷函数）

    Args:
        task_features: 任务特征
        top_n: 返回前N个结果
        min_score: 最低匹配分数阈值

    Returns:
        匹配结果列表
    """
    matcher = TalentMatcher()
    return matcher.match_all(task_features, top_n, min_score)


# 测试代码
if __name__ == "__main__":
    # 测试匹配器
    from task_feature_extractor import TaskFeatureExtractor

    print("测试天赋匹配器...")
    print("=" * 60)

    # 提取任务特征
    task = "分析Python代码的性能瓶颈"
    print(f"任务: {task}\n")

    extractor = TaskFeatureExtractor()
    feature = extractor.extract(task)
    print(f"任务特征:")
    print(f"  - 类型: {feature.task_type.value}")
    print(f"  - 复杂度: {feature.complexity.value}")
    print(f"  - 领域: {feature.domain}")
    print(f"  - 输出格式: {feature.output_format.value}\n")

    # 匹配最佳天赋
    matcher = TalentMatcher()
    best_match = matcher.match_best(feature)

    if best_match:
        talent, score = best_match
        print(f"最佳匹配:")
        print(f"  - 天赋名称: {talent.talent_name}")
        print(f"  - 匹配分数: {score:.3f}")
        print(f"  - 核心能力: {talent.core_ability}")
        print(f"  - 最佳场景: {talent.best_scenario}")
    else:
        print("未找到匹配的天赋")

    print("\n" + "=" * 60)
    print("Top 5 匹配结果:")
    print("=" * 60)

    top_results = matcher.match_all(feature, top_n=5)
    for i, result in enumerate(top_results, 1):
        print(f"\n{i}. {result.talent.talent_name}")
        print(f"   分数: {result.score:.3f}")
        print(f"   详细分数:")
        for key, value in result.details.items():
            print(f"     - {key}: {value:.3f}")

    print("\n" + "=" * 60)
    print("测试完成！")
