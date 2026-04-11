#!/usr/bin/env python3
"""
多阶段天赋定制器 - 为任务的不同阶段定制天赋Prompt

核心功能：
- 按阶段定制天赋Prompt
- 基于阶段特征匹配天赋
- 生成阶段特定的约束描述
"""

import os
import sys
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from task_stage import TaskStage, get_stage_preference, get_stage_talent_bonus, get_stage_sequence
from task_feature_extractor import TaskFeatures
from talent_loader import TalentConstraint


@dataclass
class StageCustomizationResult:
    """阶段定制结果"""
    task: str                           # 原始任务
    stage: TaskStage                    # 任务阶段
    task_features: Dict                 # 任务特征
    selected_talents: List[str]         # 选中的天赋ID列表
    custom_stage_prompt: str            # 定制化的阶段Prompt
    customization_rationale: str        # 定制理由


class MultiStageTalentCustomizer:
    """多阶段天赋定制器"""

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
        if "执行" in talent_name or "行动" in talent_name or "效率" in talent_name:
            applicable.append("执行")
        if "审查" in talent_name or "判断" in talent_name or "评估" in talent_name:
            applicable.append("审查")

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

        if "结构" in talent.core_ability or "框架" in talent.core_ability:
            formats.append("结构化")
        if "创意" in talent.core_ability or "想象" in talent.core_ability:
            formats.append("创意")
        if "分析" in talent.core_ability or "数据" in talent.core_ability:
            formats.append("数据")

        if not formats:
            formats.append("文字")

        return formats

    def _extract_applicable_domains(self, talent: TalentConstraint) -> List[str]:
        """提取天赋适用的领域"""
        domains = ["通用"]

        scenario = talent.best_scenario.lower()
        if "技术" in scenario or "编程" in scenario or "数据" in scenario:
            domains.append("技术")
        if "商业" in scenario or "营销" in scenario or "产品" in scenario:
            domains.append("商业")
        if "教育" in scenario or "学习" in scenario:
            domains.append("教育")
        if "职业" in scenario or "工作" in scenario:
            domains.append("职业")

        return domains

    def customize_by_stage(
        self,
        task: str,
        stage: TaskStage,
        task_features: Optional[TaskFeatures] = None
    ) -> StageCustomizationResult:
        """
        按阶段定制天赋Prompt

        Args:
            task: 任务描述
            stage: 任务阶段
            task_features: 任务特征（可选，未提供则自动提取）

        Returns:
            阶段定制结果
        """
        print(f"  [DEBUG] customize_by_stage 接收到参数 stage: {stage}, stage.value: {stage.value}, id(stage): {id(stage)}")

        # 提取任务特征
        if task_features is None:
            from task_feature_extractor import create_feature_extractor
            extractor = create_feature_extractor()
            task_features = extractor.extract(task)

        # 获取阶段偏好
        print(f"  [DEBUG] 调用 get_stage_preference({stage}), id(stage): {id(stage)}")
        stage_pref = get_stage_preference(stage)
        print(f"  [DEBUG] customize_by_stage 获取到 stage_pref.description: {stage_pref.description}")
        print(f"  [DEBUG] customize_by_stage 获取到 stage_pref.stage.value: {stage_pref.stage.value}")

        # 基于阶段特征匹配天赋
        matched_talents = self._match_talents_for_stage(task_features, stage_pref)

        # 生成阶段特定的Prompt
        custom_prompt = self._generate_stage_prompt(
            matched_talents,
            task_features,
            stage_pref
        )

        # 生成定制理由
        rationale = self._generate_customization_rationale(
            matched_talents,
            task_features,
            stage_pref
        )

        return StageCustomizationResult(
            task=task,
            stage=stage,
            task_features=asdict(task_features),
            selected_talents=[t.talent_name for t in matched_talents],
            custom_stage_prompt=custom_prompt,
            customization_rationale=rationale
        )

    def _match_talents_for_stage(
        self,
        task_features: TaskFeatures,
        stage_pref
    ) -> List[TalentConstraint]:
        """
        为特定阶段匹配天赋

        Args:
            task_features: 任务特征
            stage_pref: 阶段偏好

        Returns:
            匹配的天赋列表（按分数排序）
        """
        print(f"    [DEBUG] _match_talents_for_stage 接收到 stage_pref.stage.value: {stage_pref.stage.value}")

        talent_scores = []

        for talent in self.talent_library:
            profile = self.talent_profiles[talent.talent_id]

            # 计算基础分数
            base_score = self._calculate_base_score(task_features, profile)

            # 应用阶段权重加成
            stage_bonus = get_stage_talent_bonus(stage_pref.stage, talent.talent_name)
            final_score = base_score * stage_bonus

            talent_scores.append((talent, final_score))

        # 按分数排序并返回前5个
        talent_scores.sort(key=lambda x: x[1], reverse=True)
        return [t[0] for t in talent_scores[:5]]

    def _calculate_base_score(
        self,
        task_features: TaskFeatures,
        profile: Dict
    ) -> float:
        """计算基础匹配分数"""
        score = 0.0

        # 1. 任务类型匹配（权重：0.3）
        task_type_str = task_features.task_type.value
        if task_type_str in profile["applicable_task_types"]:
            score += 0.3
        elif profile["applicable_task_types"]:
            # 部分匹配
            score += 0.1

        # 2. 复杂度匹配（权重：0.2）
        complexity_str = task_features.complexity.value
        if complexity_str in profile["applicable_complexity"]:
            score += 0.2
        elif "中等" in profile["applicable_complexity"]:
            score += 0.1

        # 3. 输出格式匹配（权重：0.2）
        format_str = task_features.output_format.value
        if format_str in profile["applicable_formats"]:
            score += 0.2
        elif "文字" in profile["applicable_formats"]:
            score += 0.1

        # 4. 优先级加成（权重：0.3）
        priority_score = profile["priority"] / 10.0 * 0.3
        score += priority_score

        return score

    def _generate_stage_prompt(
        self,
        matched_talents: List[TalentConstraint],
        task_features: TaskFeatures,
        stage_pref
    ) -> str:
        """生成阶段特定的Prompt"""
        prompt_parts = []

        # 阶段标识
        print(f"  [DEBUG] _generate_stage_prompt 接收到 stage_pref.description: {stage_pref.description}")
        print(f"  [DEBUG] _generate_stage_prompt 接收到 stage_pref.stage.value: {stage_pref.stage.value}")
        prompt_parts.append(f"### {stage_pref.description}")
        prompt_parts.append("")

        # 当前任务特征
        prompt_parts.append("**当前任务特征**：")
        prompt_parts.append(f"- 任务类型：{task_features.task_type.value}")
        prompt_parts.append(f"- 复杂度：{task_features.complexity.value}")
        prompt_parts.append(f"- 输出格式：{task_features.output_format.value}")
        prompt_parts.append(f"- 当前阶段：{stage_pref.stage.display_name()}")
        prompt_parts.append("")

        # 阶段特定的天赋约束
        prompt_parts.append(f"**{stage_pref.stage.display_name()}的天赋约束**：")

        for i, talent in enumerate(matched_talents, 1):
            # 定制约束描述
            customized_constraint = self._customize_constraint_for_stage(
                talent,
                task_features,
                stage_pref
            )
            prompt_parts.append(f"{i}. {customized_constraint}")

        prompt_parts.append("")

        # 执行指导
        prompt_parts.append("**执行指导**：")
        prompt_parts.append(f"- 请遵循上述{stage_pref.stage.display_name()}的天赋约束")
        prompt_parts.append(f"- 重点关注{stage_pref.description.split('：')[1]}")
        prompt_parts.append("- 确保输出符合阶段目标和要求")
        prompt_parts.append("")

        return "\n".join(prompt_parts)

    def _customize_constraint_for_stage(
        self,
        talent: TalentConstraint,
        task_features: TaskFeatures,
        stage_pref
    ) -> str:
        """为特定阶段定制天赋约束"""
        parts = []

        # 天赋名称
        parts.append(f"**{talent.talent_name}**：")

        # 根据阶段特征调整
        if stage_pref.stage == TaskStage.PLANNING:
            parts.append("注重策略和规划，")
        elif stage_pref.stage == TaskStage.EXECUTION:
            parts.append("聚焦执行和落地，")
        elif stage_pref.stage == TaskStage.OPTIMIZATION:
            parts.append("深入分析和优化，")
        elif stage_pref.stage == TaskStage.REVIEW:
            parts.append("客观评估和审查，")

        # 根据复杂度调整
        if task_features.complexity.value == "复杂":
            parts.append("采用深度方法，")
        elif task_features.complexity.value == "简单":
            parts.append("保持简洁高效，")

        # 添加核心约束
        if talent.constraints:
            parts.append(talent.constraints[0])

        return "".join(parts)

    def _generate_customization_rationale(
        self,
        matched_talents: List[TalentConstraint],
        task_features: TaskFeatures,
        stage_pref
    ) -> str:
        """生成定制理由"""
        talent_names = [t.talent_name for t in matched_talents]

        rationale = f"在{stage_pref.stage.display_name()}，基于任务特征（{task_features.task_type.value}、"
        rationale += f"{task_features.complexity.value}）匹配了{len(talent_names)}个天赋："
        rationale += "、".join(talent_names[:3])
        if len(talent_names) > 3:
            rationale += f"等{len(talent_names)}个天赋"

        return rationale

    def customize_stage(
        self,
        stage: TaskStage,
        task: str,
        task_features: Optional[TaskFeatures] = None,
        max_talents: int = 5
    ) -> StageCustomizationResult:
        """
        按阶段定制天赋Prompt（别名方法，兼容SKILL.md API）

        Args:
            stage: 任务阶段
            task: 任务描述
            task_features: 任务特征（可选，未提供则自动提取）
            max_talents: 最大天赋数量

        Returns:
            阶段定制结果
        """
        return self.customize_by_stage(task, stage, task_features)

    def customize_all_stages(
        self,
        task: str,
        task_features: Optional[TaskFeatures] = None,
        max_talents: int = 5
    ) -> Dict[str, str]:
        """
        为所有阶段定制天赋Prompt

        Args:
            task: 任务描述
            task_features: 任务特征（可选，未提供则自动提取）
            max_talents: 每个阶段的最大天赋数量

        Returns:
            字典形式的Prompt集合，key为stage.value，value为Prompt内容
        """
        from task_stage import get_stage_sequence

        # 提取任务特征（如果未提供）
        if task_features is None:
            from task_feature_extractor import create_feature_extractor
            extractor = create_feature_extractor()
            task_features = extractor.extract(task)

        # 获取所有阶段
        stages = get_stage_sequence()

        # 为每个阶段定制Prompt
        prompts_dict = {}
        for stage in stages:
            result = self.customize_by_stage(task, stage, task_features)
            prompts_dict[stage.value] = result.custom_stage_prompt

        return prompts_dict


def create_multi_stage_customizer(library_path: str = None, external_config_path: str = None) -> MultiStageTalentCustomizer:
    """
    便捷函数：创建多阶段定制器

    Args:
        library_path: 内置天赋库文件路径
        external_config_path: 外部天赋配置文件路径（YAML或JSON）

    Returns:
        MultiStageTalentCustomizer对象
    """
    from talent_customizer import _merge_external_talents, load_talent_library

    # 加载天赋库
    talent_library = load_talent_library(library_path)

    # 如果有外部配置，合并外部天赋
    if external_config_path:
        talent_library = _merge_external_talents(talent_library, external_config_path)

    # 创建定制器
    customizer = MultiStageTalentCustomizer(talent_library)

    return customizer


# 快速测试
if __name__ == '__main__':
    from task_stage import get_stage_sequence

    print("=" * 80)
    print("多阶段天赋定制器测试")
    print("=" * 80)

    # 创建定制器
    customizer = create_multi_stage_customizer()

    # 测试任务
    task = "帮我制定一个详细的3年职业发展计划"

    print(f"\n测试任务: {task}")
    print("\n" + "=" * 80)

    # 为每个阶段定制
    for stage in get_stage_sequence():
        print(f"\n【{stage.display_name()}】")
        print("-" * 80)

        result = customizer.customize_by_stage(task, stage)

        print(f"选中的天赋: {', '.join(result.selected_talents)}")
        print(f"\n定制Prompt（前200字）:")
        print(result.custom_stage_prompt[:200] + "...")
        print(f"\n定制理由: {result.customization_rationale}")

    print("\n" + "=" * 80)
