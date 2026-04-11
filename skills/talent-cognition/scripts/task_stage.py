from enum import Enum
from typing import Dict, List, Any
from dataclasses import dataclass


class TaskStage(Enum):
    """任务阶段枚举"""

    PLANNING = "planning"          # 规划阶段
    EXECUTION = "execution"        # 执行阶段
    OPTIMIZATION = "optimization"  # 优化阶段
    REVIEW = "review"              # 审查阶段

    def __str__(self):
        return self.value

    def display_name(self) -> str:
        """获取阶段显示名称"""
        return {
            TaskStage.PLANNING: "规划阶段",
            TaskStage.EXECUTION: "执行阶段",
            TaskStage.OPTIMIZATION: "优化阶段",
            TaskStage.REVIEW: "审查阶段"
        }[self]

print(f"[DEBUG] task_stage.py 加载: __name__={__name__}, id(TaskStage)={id(TaskStage)}, id(TaskStage.EXECUTION)={id(TaskStage.EXECUTION)}")


@dataclass
class StagePreference:
    """阶段偏好配置"""
    stage: TaskStage
    description: str               # 阶段描述
    task_types: List[str]          # 偏好的任务类型
    complexity_preference: str     # 复杂度偏好
    output_format: str             # 输出格式偏好
    typical_talents: List[str]     # 典型天赋
    weight_multiplier: float       # 权重乘数（用于匹配算法）


# 阶段偏好配置字典（使用value作为key）
STAGE_PREFERENCES: Dict[str, StagePreference] = {
    "planning": StagePreference(
        stage=TaskStage.PLANNING,
        description="规划阶段：制定策略、设计方案、确定目标",
        task_types=["规划", "决策", "设计"],
        complexity_preference="中等",
        output_format="结构化",
        typical_talents=[
            "战略决策",
            "系统思维",
            "结构化思维",
            "框架化能力",
            "优先级判断"
        ],
        weight_multiplier=1.2
    ),

    "execution": StagePreference(
        stage=TaskStage.EXECUTION,
        description="执行阶段：落实计划、推进任务、完成工作",
        task_types=["执行", "实施", "操作"],
        complexity_preference="简单",
        output_format="行动",
        typical_talents=[
            "执行力",
            "效率优先",
            "系统执行",
            "持续优化",
            "迭代改进"
        ],
        weight_multiplier=1.1
    ),

    "optimization": StagePreference(
        stage=TaskStage.OPTIMIZATION,
        description="优化阶段：分析结果、改进方案、提升质量",
        task_types=["分析", "优化", "改进"],
        complexity_preference="复杂",
        output_format="分析报告",
        typical_talents=[
            "本质洞察",
            "批判性思维",
            "优化思维",
            "数据化能力",
            "反思能力"
        ],
        weight_multiplier=1.3
    ),

    "review": StagePreference(
        stage=TaskStage.REVIEW,
        description="审查阶段：评估成果、总结经验、风险识别",
        task_types=["审查", "评估", "总结"],
        complexity_preference="中等",
        output_format="评估报告",
        typical_talents=[
            "结果判断",
            "风险判断",
            "反思能力",
            "价值判断",
            "思维监控"
        ],
        weight_multiplier=1.15
    )
}

print(f"[DEBUG] STAGE_PREFERENCES 创建完成, keys={[list(STAGE_PREFERENCES.keys())]}, id(STAGE_PREFERENCES)={id(STAGE_PREFERENCES)}")


def get_stage_preference(stage: TaskStage) -> StagePreference:
    """
    获取阶段偏好配置

    Args:
        stage: 任务阶段

    Returns:
        阶段偏好配置
    """
    # 使用stage.value作为key，避免对象不匹配问题
    result = STAGE_PREFERENCES.get(stage.value, STAGE_PREFERENCES.get("planning"))
    return result


def get_stage_talent_bonus(stage: TaskStage, talent_name: str) -> float:
    """
    获取天赋在特定阶段的加成权重

    Args:
        stage: 任务阶段
        talent_name: 天赋名称

    Returns:
        权重加成（1.0为无加成）
    """
    preference = get_stage_preference(stage)

    # 如果是该阶段的典型天赋，给予加成
    if talent_name in preference.typical_talents:
        return preference.weight_multiplier

    # 检查天赋名称中是否包含阶段关键词
    stage_keywords = {
        TaskStage.PLANNING: ["战略", "规划", "决策", "系统"],
        TaskStage.EXECUTION: ["执行", "效率", "行动", "迭代"],
        TaskStage.OPTIMIZATION: ["优化", "分析", "批判", "数据"],
        TaskStage.REVIEW: ["审查", "判断", "反思", "评估"]
    }

    for keyword in stage_keywords.get(stage, []):
        if keyword in talent_name:
            return 1.1  # 轻微加成

    return 1.0  # 无加成


def get_all_stages() -> List[TaskStage]:
    """获取所有任务阶段列表"""
    return list(TaskStage)


def get_stage_sequence() -> List[TaskStage]:
    """获取标准阶段执行顺序"""
    return [
        TaskStage.PLANNING,
        TaskStage.EXECUTION,
        TaskStage.OPTIMIZATION,
        TaskStage.REVIEW
    ]


def get_next_stage(current_stage: TaskStage) -> TaskStage:
    """
    获取下一个阶段

    Args:
        current_stage: 当前阶段

    Returns:
        下一个阶段（如果是最后一个阶段，返回None）
    """
    sequence = get_stage_sequence()
    try:
        current_index = sequence.index(current_stage)
        if current_index < len(sequence) - 1:
            return sequence[current_index + 1]
    except ValueError:
        pass

    return None


# 快速测试
if __name__ == "__main__":
    print("=" * 80)
    print("任务阶段定义测试")
    print("=" * 80)

    # 测试阶段枚举
    print("\n【阶段枚举】")
    for stage in TaskStage:
        pref = get_stage_preference(stage)
        print(f"\n{pref.description}")
        print(f"  显示名称: {stage.display_name()}")
        print(f"  偏好任务类型: {', '.join(pref.task_types)}")
        print(f"  典型天赋: {', '.join(pref.typical_talents[:3])}...")
        print(f"  权重乘数: {pref.weight_multiplier}")

    # 测试天赋加成
    print("\n【天赋加成测试】")
    test_cases = [
        (TaskStage.PLANNING, "战略决策"),
        (TaskStage.PLANNING, "本质洞察"),
        (TaskStage.EXECUTION, "执行力"),
        (TaskStage.OPTIMIZATION, "批判性思维"),
        (TaskStage.REVIEW, "结果判断"),
    ]

    for stage, talent_name in test_cases:
        bonus = get_stage_talent_bonus(stage, talent_name)
        print(f"{stage.display_name()} - {talent_name}: 权重加成 {bonus:.2f}x")

    # 测试阶段序列
    print("\n【阶段序列】")
    print("标准执行顺序:", " -> ".join([s.display_name() for s in get_stage_sequence()]))

    # 测试下一阶段
    print("\n【下一阶段】")
    for stage in TaskStage:
        next_stage = get_next_stage(stage)
        next_name = next_stage.display_name() if next_stage else "无"
        print(f"{stage.display_name()} -> {next_name}")

    print("\n" + "=" * 80)
