"""
智能环境适配器 - 模块包
"""

from .environment_perceiver import EnvironmentPerceiver
from .capability_mapper import CapabilityMapper
from .shortage_diagnoser import ShortageDiagnoser
from .remediation_decider import RemediationDecider
from .execution_monitor import ExecutionMonitor
from .dynamic_adjuster import DynamicAdjuster

# 模块E和F使用函数式接口
from .orchestration_planner import (
    analyze_risks,
    generate_fallback_plans,
    check_context_consistency
)
from .skill_composer import (
    match_skills,
    generate_adapters,
    generate_plan_execution_details
)

__all__ = [
    'EnvironmentPerceiver',
    'CapabilityMapper',
    'ShortageDiagnoser',
    'RemediationDecider',
    'ExecutionMonitor',
    'DynamicAdjuster',
    # 模块E函数
    'analyze_risks',
    'generate_fallback_plans',
    'check_context_consistency',
    # 模块F函数
    'match_skills',
    'generate_adapters',
    'generate_plan_execution_details'
]
