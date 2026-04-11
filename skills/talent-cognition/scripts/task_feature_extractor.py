#!/usr/bin/env python3
"""
任务特征提取器 - 从任务描述中提取关键特征

核心功能：
- 任务类型分类
- 复杂度评估
- 输出格式识别
- 时间压力判断
- 精度要求评估
- 领域识别
"""
import os
import sys
import re
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class TaskType(Enum):
    """任务类型"""
    ANALYSIS = "分析"
    CREATION = "创作"
    PLANNING = "规划"
    COMMUNICATION = "沟通"
    LEARNING = "学习"
    CONSULTATION = "咨询"
    RESEARCH = "研究"
    DECISION = "决策"


class Complexity(Enum):
    """复杂度"""
    SIMPLE = "简单"
    MEDIUM = "中等"
    COMPLEX = "复杂"


class OutputFormat(Enum):
    """输出格式"""
    TEXT = "文字"
    STRUCTURED = "结构化"
    CREATIVE = "创意"
    DATA = "数据"
    MIXED = "混合"


class TimePressure(Enum):
    """时间压力"""
    URGENT = "紧急"
    NORMAL = "正常"
    RELAXED = "从容"


class Precision(Enum):
    """精度要求"""
    ROUGH = "粗略"
    NORMAL = "正常"
    PRECISE = "精确"


class Interactivity(Enum):
    """交互性"""
    ONE_WAY = "单向"
    INTERACTIVE = "交互"


@dataclass
class TaskFeatures:
    """任务特征"""
    task_type: TaskType              # 任务类型
    complexity: Complexity           # 复杂度
    output_format: OutputFormat      # 输出格式
    time_pressure: TimePressure      # 时间压力
    precision: Precision             # 精度要求
    interactivity: Interactivity     # 交互性
    domain: str                      # 领域
    keywords: List[str]              # 关键词


class TaskFeatureExtractor:
    """任务特征提取器"""

    def __init__(self):
        # 任务类型关键词映射
        self.task_type_keywords = {
            TaskType.ANALYSIS: ["分析", "剖析", "研究", "探究", "诊断", "评估", "判断"],
            TaskType.CREATION: ["创作", "写", "设计", "构思", "创意", "生成", "创作"],
            TaskType.PLANNING: ["规划", "计划", "制定", "设计", "安排", "部署"],
            TaskType.COMMUNICATION: ["沟通", "交流", "表达", "说明", "解释", "传达"],
            TaskType.LEARNING: ["学习", "研究", "探索", "了解", "掌握", "学习"],
            TaskType.CONSULTATION: ["咨询", "建议", "指导", "帮助", "解答", "回答"],
            TaskType.RESEARCH: ["研究", "调研", "调查", "分析", "探索", "查找"],
            TaskType.DECISION: ["决定", "决策", "选择", "判断", "确定"]
        }

        # 复杂度关键词
        self.complexity_keywords = {
            Complexity.SIMPLE: ["简单", "快速", "简要", "简短", "快速"],
            Complexity.MEDIUM: ["详细", "完善", "完整", "系统"],
            Complexity.COMPLEX: ["深入", "全面", "详细", "系统", "复杂", "综合"]
        }

        # 输出格式关键词
        self.output_format_keywords = {
            OutputFormat.TEXT: ["文字", "文本", "描述", "说明"],
            OutputFormat.STRUCTURED: ["结构", "框架", "列表", "表格", "步骤", "计划"],
            OutputFormat.CREATIVE: ["创意", "创新", "独特", "新颖"],
            OutputFormat.DATA: ["数据", "统计", "分析", "报告"],
            OutputFormat.MIXED: ["综合", "完整", "全面"]
        }

        # 时间压力关键词
        self.time_pressure_keywords = {
            TimePressure.URGENT: ["快速", "立即", "马上", "紧急", "尽快"],
            TimePressure.NORMAL: ["正常", "标准"],
            TimePressure.RELAXED: ["从容", "详细", "深入", "仔细"]
        }

        # 精度要求关键词
        self.precision_keywords = {
            Precision.ROUGH: ["粗略", "大概", "简要", "概述"],
            Precision.NORMAL: ["准确", "正确"],
            Precision.PRECISE: ["精确", "详细", "深入", "精准"]
        }

        # 领域关键词
        self.domain_keywords = {
            "技术": ["代码", "编程", "开发", "技术", "系统"],
            "商业": ["商业", "企业", "业务", "市场", "销售"],
            "教育": ["学习", "教育", "培训", "课程", "知识"],
            "生活": ["生活", "日常", "个人", "家庭"],
            "职业": ["职业", "工作", "职场", "事业", "发展"],
            "学术": ["学术", "研究", "论文", "文献"]
        }

    def extract(self, task: str) -> TaskFeatures:
        """
        提取任务特征

        Args:
            task: 任务描述

        Returns:
            任务特征
        """
        # 标准化任务文本
        task_normalized = task.lower()

        # 提取关键词
        keywords = self._extract_keywords(task)

        # 分类特征
        task_type = self._classify_task_type(task_normalized)
        complexity = self._evaluate_complexity(task_normalized, keywords)
        output_format = self._identify_output_format(task_normalized, keywords)
        time_pressure = self._judge_time_pressure(task_normalized)
        precision = self._evaluate_precision(task_normalized, keywords)
        interactivity = self._judge_interactivity(task_normalized)
        domain = self._identify_domain(task_normalized, keywords)

        return TaskFeatures(
            task_type=task_type,
            complexity=complexity,
            output_format=output_format,
            time_pressure=time_pressure,
            precision=precision,
            interactivity=interactivity,
            domain=domain,
            keywords=keywords
        )

    def _extract_keywords(self, task: str) -> List[str]:
        """提取关键词"""
        # 简单的分词和过滤
        words = re.findall(r'[\w\u4e00-\u9fff]+', task)
        # 过滤掉常用词
        stop_words = {"的", "了", "是", "在", "我", "你", "他", "她", "它", "我们", "你们", "他们"}
        keywords = [w for w in words if w not in stop_words and len(w) > 1]
        return keywords

    def _classify_task_type(self, task: str) -> TaskType:
        """分类任务类型"""
        max_score = 0
        best_type = TaskType.ANALYSIS  # 默认

        for task_type, keywords in self.task_type_keywords.items():
            score = sum(1 for kw in keywords if kw in task)
            if score > max_score:
                max_score = score
                best_type = task_type

        return best_type

    def _evaluate_complexity(self, task: str, keywords: List[str]) -> Complexity:
        """评估复杂度"""
        # 基于任务长度和关键词判断
        if len(task) < 20 or any(kw in task for kw in self.complexity_keywords[Complexity.SIMPLE]):
            return Complexity.SIMPLE
        elif any(kw in task for kw in self.complexity_keywords[Complexity.COMPLEX]):
            return Complexity.COMPLEX
        else:
            return Complexity.MEDIUM

    def _identify_output_format(self, task: str, keywords: List[str]) -> OutputFormat:
        """识别输出格式"""
        for output_format, keywords in self.output_format_keywords.items():
            if any(kw in task for kw in keywords):
                return output_format

        return OutputFormat.TEXT  # 默认

    def _judge_time_pressure(self, task: str) -> TimePressure:
        """判断时间压力"""
        if any(kw in task for kw in self.time_pressure_keywords[TimePressure.URGENT]):
            return TimePressure.URGENT
        elif any(kw in task for kw in self.time_pressure_keywords[TimePressure.RELAXED]):
            return TimePressure.RELAXED
        else:
            return TimePressure.NORMAL

    def _evaluate_precision(self, task: str, keywords: List[str]) -> Precision:
        """评估精度要求"""
        if any(kw in task for kw in self.precision_keywords[Precision.ROUGH]):
            return Precision.ROUGH
        elif any(kw in task for kw in self.precision_keywords[Precision.PRECISE]):
            return Precision.PRECISE
        else:
            return Precision.NORMAL

    def _judge_interactivity(self, task: str) -> Interactivity:
        """判断交互性"""
        interactive_keywords = ["讨论", "交流", "对话", "互动", "沟通"]
        if any(kw in task for kw in interactive_keywords):
            return Interactivity.INTERACTIVE
        else:
            return Interactivity.ONE_WAY

    def _identify_domain(self, task: str, keywords: List[str]) -> str:
        """识别领域"""
        for domain, domain_keywords in self.domain_keywords.items():
            if any(kw in task for kw in domain_keywords):
                return domain

        return "通用"


def create_feature_extractor() -> TaskFeatureExtractor:
    """
    便捷函数：创建特征提取器

    Returns:
        TaskFeatureExtractor对象
    """
    return TaskFeatureExtractor()


if __name__ == '__main__':
    # 测试特征提取器
    extractor = create_feature_extractor()

    # 测试用例
    test_cases = [
        "帮我分析这个问题的本质",
        "我想设计一个创意方案",
        "帮我制定一个详细的3年职业发展计划",
        "如何快速提高沟通能力",
        "我不确定该怎么做，需要详细的建议"
    ]

    for task in test_cases:
        print(f"\n{'='*60}")
        print(f"任务: {task}")
        print('='*60)

        features = extractor.extract(task)

        print(f"任务类型: {features.task_type.value}")
        print(f"复杂度: {features.complexity.value}")
        print(f"输出格式: {features.output_format.value}")
        print(f"时间压力: {features.time_pressure.value}")
        print(f"精度要求: {features.precision.value}")
        print(f"交互性: {features.interactivity.value}")
        print(f"领域: {features.domain}")
        print(f"关键词: {features.keywords}")
