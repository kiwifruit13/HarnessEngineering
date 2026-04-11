#!/usr/bin/env python3
"""
天赋库加载器 - 支持内置天赋库和外部配置文件

功能：
- 加载内置天赋库（从references/talent-attribute-library.md）
- 从YAML/JSON文件加载自定义天赋配置
- 支持天赋库合并和覆盖
"""

import os
import re
import json
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
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


@dataclass
class TalentConstraint:
    """天赋约束"""
    talent_id: str
    talent_name: str
    core_ability: str
    constraints: List[str]
    best_scenario: str
    priority: int


@dataclass
class TalentConfig:
    """天赋配置（用于外部配置文件）"""
    id: str
    name: str
    description: str
    constraints: List[str]
    features: Dict[str, Any]
    weights: Dict[str, float]


class TalentLoader:
    """天赋配置加载器"""

    def __init__(self):
        self.loaded_talents: Dict[str, TalentConfig] = {}

    def load_from_yaml(self, file_path: str) -> Dict[str, TalentConfig]:
        """从YAML文件加载天赋配置"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"天赋配置文件不存在: {file_path}")

        with open(path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        return self._parse_config(config)

    def load_from_json(self, file_path: str) -> Dict[str, TalentConfig]:
        """从JSON文件加载天赋配置"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"天赋配置文件不存在: {file_path}")

        with open(path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        return self._parse_config(config)

    def _parse_config(self, config: Dict[str, Any]) -> Dict[str, TalentConfig]:
        """解析配置文件内容"""
        version = config.get('version', '1.0')
        if version != '1.0':
            print(f"警告: 配置版本 {version} 可能不完全兼容")

        talents_dict = {}
        talents_list = config.get('talents', [])

        for talent_data in talents_list:
            if not self._validate_talent_data(talent_data):
                print(f"警告: 跳过无效天赋配置: {talent_data.get('id', 'unknown')}")
                continue

            talent_config = TalentConfig(
                id=talent_data['id'],
                name=talent_data['name'],
                description=talent_data['description'],
                constraints=talent_data['constraints'],
                features=talent_data['features'],
                weights=talent_data.get('weights', {})
            )

            talents_dict[talent_config.id] = talent_config

        print(f"成功加载 {len(talents_dict)} 个天赋配置")
        return talents_dict

    def _validate_talent_data(self, data: Dict[str, Any]) -> bool:
        """验证天赋配置数据"""
        required_fields = ['id', 'name', 'description', 'constraints', 'features']
        for field in required_fields:
            if field not in data:
                return False

        if not isinstance(data['constraints'], list) or len(data['constraints']) == 0:
            return False

        if not isinstance(data['features'], dict):
            return False

        return True

    def save_to_yaml(self, talents: Dict[str, TalentConfig], file_path: str):
        """保存天赋配置到YAML文件"""
        config = {
            'version': '1.0',
            'talents': [asdict(talent) for talent in talents.values()]
        }

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

        print(f"已保存 {len(talents)} 个天赋配置到 {file_path}")

    def save_to_json(self, talents: Dict[str, TalentConfig], file_path: str):
        """保存天赋配置到JSON文件"""
        config = {
            'version': '1.0',
            'talents': [asdict(talent) for talent in talents.values()]
        }

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        print(f"已保存 {len(talents)} 个天赋配置到 {file_path}")


def talent_config_to_constraint(config: TalentConfig) -> TalentConstraint:
    """
    将TalentConfig转换为TalentConstraint

    Args:
        config: TalentConfig对象

    Returns:
        TalentConstraint对象
    """
    # 提取priority
    priority = config.weights.get('priority', config.features.get('priority', 5))

    # 提取best_scenario
    best_scenario = config.features.get('best_scenario', config.description)

    return TalentConstraint(
        talent_id=config.id,
        talent_name=config.name,
        core_ability=config.description,
        constraints=config.constraints,
        best_scenario=best_scenario,
        priority=priority
    )


def load_talent_library(library_path: str = None) -> List[TalentConstraint]:
    """
    从Markdown文件加载天赋库

    Args:
        library_path: 天赋库文件路径

    Returns:
        天赋约束列表
    """
    if library_path is None:
        # 默认路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        library_path = os.path.join(current_dir, "../references/talent-attribute-library.md")

    if not os.path.exists(library_path):
        raise FileNotFoundError(f"天赋库文件不存在: {library_path}")

    with open(library_path, 'r', encoding='utf-8') as f:
        content = f.read()

    return _parse_talent_library(content)


def _parse_talent_library(content: str) -> List[TalentConstraint]:
    """
    解析天赋库Markdown内容

    Args:
        content: Markdown内容

    Returns:
        天赋约束列表
    """
    talents = []

    # 使用正则表达式匹配每个天赋块
    # 格式：### 天赋名称 ... 【基本信息】 ... 【能力定义】 ... 【触发条件】 ... ---
    pattern = r'###\s*([^\n]+)\s*\n\n\*\*【基本信息】\*\*.*?\*\*【能力定义】\*\*\s*\n-\s*核心能力：(.*?)\s*\n.*?\*\*【触发条件】\*\*\s*\n-\s*最佳场景：(.*?)\s*\n.*?强度等级：(\d+)/10'
    matches = re.findall(pattern, content, re.DOTALL)

    for i, match in enumerate(matches):
        name, core_ability, best_scenario, priority_str = match

        # 生成约束描述（基于核心能力）
        constraints = [
            f"保持{core_ability}的核心能力",
            "能识别关键要素和核心问题",
            "避免被表面现象干扰"
        ]

        priority = int(priority_str)

        # 生成talent_id
        talent_id = name.strip().lower().replace(' ', '_').replace('（', '').replace('）', '').replace('、', '_')

        talent = TalentConstraint(
            talent_id=talent_id,
            talent_name=name.strip(),
            core_ability=core_ability.strip(),
            constraints=constraints,
            best_scenario=best_scenario.strip(),
            priority=priority
        )

        talents.append(talent)

    print(f"从天赋库加载了 {len(talents)} 个天赋")
    return talents


def create_talent_loader() -> TalentLoader:
    """创建天赋加载器实例"""
    return TalentLoader()
