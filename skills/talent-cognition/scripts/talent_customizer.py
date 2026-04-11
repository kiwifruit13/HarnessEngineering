#!/usr/bin/env python3
"""
天赋定制器 - 为任务定制天赋Prompt

核心功能：
- 基于任务特征匹配天赋
- 根据任务特征定制天赋约束
- 生成定制化的天赋Prompt
"""
import os
import sys
from typing import List, Dict, Any
from dataclasses import dataclass, asdict

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from talent_loader import TalentConstraint, load_talent_library, TalentLoader, TalentConfig
from task_feature_extractor import TaskFeatures


@dataclass
class TalentCustomizationResult:
    """天赋定制结果"""
    task: str                           # 原始任务
    task_features: Dict                 # 任务特征
    selected_talents: List[str]         # 选中的天赋ID列表
    custom_talent_prompt: str           # 定制化的天赋Prompt
    customization_rationale: str        # 定制理由


class TalentCustomizer:
    """天赋定制器"""

    def __init__(self, talent_library: List[TalentConstraint]):
        self.talent_library = talent_library
        self._build_talent_profiles()

    def _build_talent_profiles(self):
        """构建天赋画像"""
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
        # 基于天赋名称和最佳场景推断
        applicable = []

        talent_name = talent.talent_name
        best_scenario = talent.best_scenario

        # 简单的规则映射
        if "分析" in talent_name or "洞察" in talent_name or "推理" in talent_name:
            applicable.append("分析")
        if "创作" in talent_name or "创意" in talent_name or "想象" in talent_name:
            applicable.append("创作")
        if "决策" in talent_name or "规划" in talent_name or "战略" in talent_name:
            applicable.append("规划")
        if "表达" in talent_name or "沟通" in talent_name or "倾听" in talent_name:
            applicable.append("沟通")
        if "学习" in talent_name or "研究" in talent_name:
            applicable.append("学习")

        return applicable

    def _extract_applicable_complexity(self, talent: TalentConstraint) -> List[str]:
        """提取天赋适用的复杂度"""
        # 基于天赋的强度等级判断
        if talent.priority >= 8:
            return ["复杂", "中等", "简单"]
        elif talent.priority >= 5:
            return ["中等", "简单"]
        else:
            return ["简单"]

    def _extract_applicable_formats(self, talent: TalentConstraint) -> List[str]:
        """提取天赋适用的输出格式"""
        # 基于天赋能力推断
        formats = []

        if "结构" in talent.core_ability or "框架" in talent.core_ability:
            formats.append("结构化")
        if "创意" in talent.core_ability or "想象" in talent.core_ability:
            formats.append("创意")
        if "分析" in talent.core_ability or "数据" in talent.core_ability:
            formats.append("数据")

        return formats if formats else ["文字"]

    def _extract_applicable_domains(self, talent: TalentConstraint) -> List[str]:
        """提取天赋适用的领域"""
        # 默认通用，特定天赋可以指定
        return ["通用"]

    def customize(
        self,
        task: str,
        task_features: TaskFeatures,
        max_talents: int = 5
    ) -> TalentCustomizationResult:
        """
        为任务定制天赋Prompt

        Args:
            task: 任务描述
            task_features: 任务特征
            max_talents: 最大天赋数量

        Returns:
            天赋定制结果
        """
        # 1. 基于任务特征匹配天赋
        matched_talents = self._match_talents_by_features(task_features)

        # 2. 限制数量
        matched_talents = matched_talents[:max_talents]

        # 3. 定制天赋约束
        customized_constraints = []
        for talent in matched_talents:
            constraint = self._customize_constraint(talent, task_features)
            customized_constraints.append(constraint)

        # 4. 生成定制Prompt
        custom_prompt = self._build_custom_prompt(
            task,
            customized_constraints,
            task_features
        )

        # 5. 构建理由
        rationale = self._build_rationale(task_features, matched_talents)

        return TalentCustomizationResult(
            task=task,
            task_features=asdict(task_features),
            selected_talents=[t.talent_id for t in matched_talents],
            custom_talent_prompt=custom_prompt,
            customization_rationale=rationale
        )

    def _match_talents_by_features(
        self,
        task_features: TaskFeatures
    ) -> List[TalentConstraint]:
        """
        基于任务特征匹配天赋

        Args:
            task_features: 任务特征

        Returns:
            匹配的天赋列表（按适配度排序）
        """
        scored_talents = []

        for talent in self.talent_library:
            profile = self.talent_profiles[talent.talent_id]
            score = self._calculate_match_score(task_features, profile, talent)

            if score > 0:
                scored_talents.append((score, talent))

        # 按分数排序
        scored_talents.sort(key=lambda x: x[0], reverse=True)

        # 返回天赋对象
        return [talent for score, talent in scored_talents]

    def _calculate_match_score(
        self,
        task_features: TaskFeatures,
        profile: Dict,
        talent: TalentConstraint
    ) -> float:
        """计算匹配分数"""
        score = 0.0

        # 1. 任务类型匹配（权重：0.4）
        task_type_str = task_features.task_type.value
        if task_type_str in profile["applicable_task_types"]:
            score += 0.4

        # 2. 复杂度匹配（权重：0.2）
        complexity_str = task_features.complexity.value
        if complexity_str in profile["applicable_complexity"]:
            score += 0.2
        elif "中等" in profile["applicable_complexity"]:
            # 中等复杂度可以作为默认匹配
            score += 0.1

        # 3. 输出格式匹配（权重：0.2）
        format_str = task_features.output_format.value
        if format_str in profile["applicable_formats"]:
            score += 0.2
        elif "文字" in profile["applicable_formats"]:
            # 文字可以作为默认匹配
            score += 0.1

        # 4. 优先级加成（权重：0.2）
        priority_score = talent.priority / 10.0 * 0.2
        score += priority_score

        return score

    def _customize_constraint(
        self,
        talent: TalentConstraint,
        task_features: TaskFeatures
    ) -> str:
        """
        根据任务特征定制天赋约束

        Args:
            talent: 天赋约束
            task_features: 任务特征

        Returns:
            定制化的约束描述
        """
        parts = []

        # 天赋名称
        parts.append(f"**{talent.talent_name}**：")

        # 根据复杂度调整
        if task_features.complexity.value == "复杂":
            parts.append("采用深度分析，")
        elif task_features.complexity.value == "简单":
            parts.append("保持简洁高效，")

        # 根据输出格式调整
        if task_features.output_format.value == "结构化":
            parts.append("提供结构化输出，")
        elif task_features.output_format.value == "创意":
            parts.append("发挥创意思维，")

        # 根据时间压力调整
        if task_features.time_pressure.value == "紧急":
            parts.append("快速响应，")

        # 添加核心能力
        if talent.core_ability:
            parts.append(talent.core_ability)

        # 组合
        constraint = " ".join(parts)

        return constraint

    def _build_custom_prompt(
        self,
        task: str,
        customized_constraints: List[str],
        task_features: TaskFeatures
    ) -> str:
        """
        构建定制化的天赋Prompt

        Args:
            task: 任务描述
            customized_constraints: 定制化的约束列表
            task_features: 任务特征

        Returns:
            定制化的Prompt
        """
        prompt_parts = []

        # 标题
        prompt_parts.append("### 天赋增强指导")
        prompt_parts.append("")

        # 任务说明
        prompt_parts.append("**当前任务特征**：")
        prompt_parts.append(f"- 任务类型：{task_features.task_type.value}")
        prompt_parts.append(f"- 复杂度：{task_features.complexity.value}")
        prompt_parts.append(f"- 输出格式：{task_features.output_format.value}")
        prompt_parts.append(f"- 精度要求：{task_features.precision.value}")
        prompt_parts.append("")

        # 天赋约束
        prompt_parts.append("**定制天赋约束**：")
        for i, constraint in enumerate(customized_constraints, 1):
            prompt_parts.append(f"{i}. {constraint}")
        prompt_parts.append("")

        # 执行指导
        prompt_parts.append("**执行指导**：")
        prompt_parts.append("- 请严格遵循上述天赋约束执行任务")
        prompt_parts.append("- 根据任务特征调整输出风格")
        prompt_parts.append("- 确保输出符合精度和格式要求")

        # 组合
        full_prompt = "\n".join(prompt_parts)

        return full_prompt

    def _build_rationale(
        self,
        task_features: TaskFeatures,
        matched_talents: List[TalentConstraint]
    ) -> str:
        """构建定制理由"""
        rationale_parts = []

        rationale_parts.append(f"基于任务特征分析：")
        rationale_parts.append(f"- 任务类型：{task_features.task_type.value}")
        rationale_parts.append(f"- 复杂度：{task_features.complexity.value}")

        rationale_parts.append(f"\n匹配到{len(matched_talents)}个天赋：")
        for talent in matched_talents:
            rationale_parts.append(f"- {talent.talent_name}：{talent.core_ability[:30]}...")

        return "\n".join(rationale_parts)


def create_customizer(library_path: str = None, external_config_path: str = None) -> TalentCustomizer:
    """
    便捷函数：创建定制器

    Args:
        library_path: 内置天赋库文件路径
        external_config_path: 外部天赋配置文件路径（YAML或JSON）

    Returns:
        TalentCustomizer对象
    """
    # 加载内置天赋库
    talent_library = load_talent_library(library_path)

    # 如果有外部配置，合并外部天赋
    if external_config_path:
        talent_library = _merge_external_talents(talent_library, external_config_path)

    # 创建定制器
    customizer = TalentCustomizer(talent_library)

    return customizer


def _merge_external_talents(
    built_in_library: List[TalentConstraint],
    external_config_path: str
) -> List[TalentConstraint]:
    """
    合并内置天赋库和外部天赋配置

    Args:
        built_in_library: 内置天赋库
        external_config_path: 外部配置文件路径

    Returns:
        合并后的天赋库
    """
    loader = TalentLoader()

    # 根据文件扩展名选择加载方式
    if external_config_path.endswith('.yaml') or external_config_path.endswith('.yml'):
        external_configs = loader.load_from_yaml(external_config_path)
    elif external_config_path.endswith('.json'):
        external_configs = loader.load_from_json(external_config_path)
    else:
        raise ValueError(f"不支持的配置文件格式: {external_config_path}")

    # 转换为TalentConstraint对象
    merged = list(built_in_library)  # 复制内置库
    talent_id_set = {t.talent_id for t in built_in_library}  # 已存在的天赋ID

    for config in external_configs.values():
        # 如果外部天赋ID与内置天赋冲突，覆盖内置天赋
        if config.id in talent_id_set:
            print(f"覆盖内置天赋: {config.id}")
            # 移除旧的
            merged = [t for t in merged if t.talent_id != config.id]
            talent_id_set.remove(config.id)

        # 转换TalentConfig为TalentConstraint
        talent_constraint = TalentConstraint(
            talent_id=config.id,
            talent_name=config.name,
            core_ability=config.description,
            constraints=config.constraints,
            best_scenario=_generate_best_scenario(config.features),
            priority=_calculate_priority(config.weights)
        )

        merged.append(talent_constraint)
        talent_id_set.add(config.id)

    print(f"合并后天赋库总数: {len(merged)}")
    return merged


def _generate_best_scenario(features: Dict[str, Any]) -> str:
    """从特征生成最佳场景描述"""
    scenario_parts = []

    if 'task_types' in features and features['task_types']:
        task_type_map = {
            'planning': '规划类',
            'execution': '执行类',
            'analysis': '分析类',
            'creation': '创作类',
            'decision': '决策类'
        }
        types_str = '、'.join([task_type_map.get(t, t) for t in features['task_types']])
        scenario_parts.append(f"适用于{types_str}任务")

    if 'complexity' in features and features['complexity']:
        scenario_parts.append(f"处理{features['complexity'][0]}及以上复杂度问题")

    return '；'.join(scenario_parts) if scenario_parts else "通用场景"


def _calculate_priority(weights: Dict[str, float]) -> int:
    """根据权重计算优先级（1-10）"""
    if not weights:
        return 5

    # 计算权重总和，归一化到1-10
    total = sum(weights.values())
    if total == 0:
        return 5

    avg_weight = total / len(weights)
    priority = int(avg_weight * 10)
    return max(1, min(10, priority))


if __name__ == '__main__':
    # 测试定制器
    from task_feature_extractor import create_feature_extractor

    customizer = create_customizer()
    extractor = create_feature_extractor()

    # 测试用例
    test_cases = [
        "帮我制定一个详细的3年职业发展计划",
        "我想设计一个创意的产品方案",
        "如何快速分析这个复杂的问题"
    ]

    for task in test_cases:
        print(f"\n{'='*60}")
        print(f"任务: {task}")
        print('='*60)

        # 提取特征
        features = extractor.extract(task)

        # 定制天赋
        result = customizer.customize(task, features)

        print(f"\n任务特征:")
        for key, value in result.task_features.items():
            if isinstance(value, str):
                print(f"  {key}: {value}")

        print(f"\n选中的天赋: {result.selected_talents}")

        print(f"\n定制理由:")
        print(result.customization_rationale)

        print(f"\n定制Prompt:")
        print(result.custom_talent_prompt)
