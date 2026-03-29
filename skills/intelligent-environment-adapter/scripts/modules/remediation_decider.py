"""
模块D：补齐决策模块 (Remediation Decision Module)

职责：选择补齐策略，生成补齐计划
边界：不涉及编排规划
"""

import json
from typing import Dict, Any, List
from dataclasses import dataclass


class RemediationDecider:
    """
    补齐决策模块
    
    职责边界：
    - ✅ 选择补齐策略
    - ✅ 计算补齐成本
    - ✅ 生成补齐计划
    - ❌ 不涉及编排规划
    - ❌ 不涉及技能匹配
    """
    
    # 策略选择映射
    STRATEGY_SELECTION = {
        "knowledge_gap": {
            "实时": "search_external_knowledge",
            "default": "build_domain_model"
        },
        "capability_gap": {
            "has_skill": "search_and_load_skill",
            "complex": "compose_multiple_skills",
            "default": "delegate_to_human"
        },
        "data_source_gap": {
            "实时": "integrate_realtime_api",
            "default": "search_alternative_sources"
        },
        "processing_gap": {
            "large_scale": "distribute_processing_tasks",
            "default": "optimize_processing_pipeline"
        },
        "integration_gap": {
            "default": "build_adapter_layer"
        },
        "multimodal_gap": {
            "default": "search_and_load_skill"
        }
    }
    
    # 策略成本估算
    STRATEGY_COSTS = {
        "search_external_knowledge": {"time": 45, "tokens": 2000, "compute": "low"},
        "build_domain_model": {"time": 120, "tokens": 5000, "compute": "medium"},
        "fetch_expert_documents": {"time": 75, "tokens": 3000, "compute": "low"},
        "search_and_load_skill": {"time": 45, "tokens": 1500, "compute": "low"},
        "compose_multiple_skills": {"time": 100, "tokens": 4000, "compute": "medium"},
        "delegate_to_human": {"time": 300, "tokens": 500, "compute": "low"},
        "search_alternative_sources": {"time": 45, "tokens": 1500, "compute": "low"},
        "integrate_realtime_api": {"time": 45, "tokens": 1500, "compute": "low"},
        "optimize_processing_pipeline": {"time": 45, "tokens": 1500, "compute": "low"},
        "distribute_processing_tasks": {"time": 60, "tokens": 2000, "compute": "medium"},
        "build_adapter_layer": {"time": 60, "tokens": 2000, "compute": "low"}
    }

    def __init__(self):
        pass

    def execute(self, input_data: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        模块执行入口
        
        Args:
            input_data: {
                "diagnostic_report": dict,
                "environment_profile": dict,
                "cost_budget": dict  # 可选
            }
        
        Returns:
            {
                "remediation_plan": {
                    "overall_strategy": str,
                    "actions": list,
                    "total_estimated_cost": dict
                }
            }
        """
        diagnostic_report = input_data.get("diagnostic_report", {}).get("diagnostic_report", {})
        environment_profile = input_data.get("environment_profile", {})
        cost_budget = input_data.get("cost_budget", {})
        
        match_score = diagnostic_report.get("match_score", 0.0)
        shortage_details = diagnostic_report.get("shortage_details", [])
        
        # 确定整体策略
        overall_strategy = self._determine_overall_strategy(match_score, shortage_details)
        
        if overall_strategy == "ignore":
            return {
                "remediation_plan": {
                    "overall_strategy": overall_strategy,
                    "actions": [],
                    "total_estimated_cost": {"time": 0, "tokens": 0, "compute": "low"}
                }
            }
        
        # 生成补齐行动
        actions = self._generate_actions(shortage_details, environment_profile, cost_budget)
        
        # 计算总成本
        total_cost = self._calculate_total_cost(actions)
        
        return {
            "remediation_plan": {
                "overall_strategy": overall_strategy,
                "actions": actions,
                "total_estimated_cost": total_cost
            }
        }

    def _determine_overall_strategy(
        self, 
        match_score: float,
        shortage_details: List[Dict[str, Any]]
    ) -> str:
        """确定整体策略"""
        critical_count = sum(1 for s in shortage_details if s.get("severity") == "critical")
        
        if match_score >= 0.85:
            return "ignore"
        elif match_score >= 0.70:
            if critical_count > 0:
                return "immediate"
            return "planned"
        elif match_score >= 0.40:
            return "immediate"
        else:
            return "degraded"

    def _generate_actions(
        self,
        shortage_details: List[Dict[str, Any]],
        environment_profile: Dict[str, Any],
        cost_budget: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """生成补齐行动列表"""
        actions = []
        
        for shortage in shortage_details:
            strategy = self._select_strategy(shortage, environment_profile)
            cost = self._estimate_cost(strategy, environment_profile)
            priority = self._calculate_priority(shortage)
            improvement = self._estimate_improvement(strategy, shortage)
            
            action = {
                "shortage_id": shortage.get("id"),
                "strategy": strategy,
                "priority": priority,
                "expected_improvement": improvement,
                "estimated_cost": cost,
                "execution_mode": "sequential"
            }
            actions.append(action)
        
        # 按优先级排序
        actions.sort(key=lambda x: x["priority"], reverse=True)
        
        # 根据预算过滤
        time_limit = cost_budget.get("time_limit", 300)
        token_limit = cost_budget.get("token_limit", 10000)
        
        filtered_actions = []
        total_time = 0
        total_tokens = 0
        
        for action in actions:
            action_time = action["estimated_cost"]["time"]
            action_tokens = action["estimated_cost"]["tokens"]
            
            if total_time + action_time <= time_limit and total_tokens + action_tokens <= token_limit:
                filtered_actions.append(action)
                total_time += action_time
                total_tokens += action_tokens
        
        return filtered_actions

    def _select_strategy(self, shortage: Dict[str, Any], environment_profile: Dict[str, Any]) -> str:
        """选择补齐策略"""
        shortage_type = shortage.get("type", "")
        time_sensitivity = environment_profile.get("time_sensitivity", "")
        complexity = environment_profile.get("complexity", "")
        
        strategy_map = self.STRATEGY_SELECTION.get(shortage_type, {})
        
        # 根据时效性选择
        if time_sensitivity in strategy_map:
            return strategy_map[time_sensitivity]
        
        # 根据复杂度选择
        if complexity in ["复杂", "极复杂"] and "complex" in strategy_map:
            return strategy_map["complex"]
        
        # 默认策略
        return strategy_map.get("default", "search_external_knowledge")

    def _estimate_cost(self, strategy: str, environment_profile: Dict[str, Any]) -> Dict[str, Any]:
        """估算策略成本"""
        base_cost = self.STRATEGY_COSTS.get(strategy, {"time": 30, "tokens": 1000, "compute": "low"})
        
        # 根据复杂度调整
        complexity = environment_profile.get("complexity", "")
        multiplier = 1.0
        if complexity == "中等":
            multiplier = 1.2
        elif complexity == "复杂":
            multiplier = 1.5
        elif complexity == "极复杂":
            multiplier = 2.0
        
        return {
            "time": int(base_cost["time"] * multiplier),
            "tokens": int(base_cost["tokens"] * multiplier),
            "compute": base_cost["compute"]
        }

    def _calculate_priority(self, shortage: Dict[str, Any]) -> float:
        """计算优先级"""
        severity = shortage.get("severity", "moderate")
        impact_core = shortage.get("impact_core", False)
        
        severity_scores = {"critical": 1.0, "moderate": 0.7, "minor": 0.4}
        base_score = severity_scores.get(severity, 0.5)
        
        if impact_core:
            base_score = min(1.0, base_score + 0.2)
        
        return round(base_score, 2)

    def _estimate_improvement(self, strategy: str, shortage: Dict[str, Any]) -> float:
        """估算预期改进"""
        improvement_map = {
            "search_external_knowledge": 0.3,
            "build_domain_model": 0.5,
            "search_and_load_skill": 0.6,
            "compose_multiple_skills": 0.7,
            "integrate_realtime_api": 0.8,
            "delegate_to_human": 0.8
        }
        
        base_improvement = improvement_map.get(strategy, 0.3)
        
        severity = shortage.get("severity", "moderate")
        if severity == "critical":
            base_improvement = min(1.0, base_improvement + 0.2)
        
        return round(base_improvement, 2)

    def _calculate_total_cost(self, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算总成本"""
        total_time = sum(a["estimated_cost"]["time"] for a in actions)
        total_tokens = sum(a["estimated_cost"]["tokens"] for a in actions)
        
        compute_levels = {"low": 0, "medium": 1, "high": 2}
        max_compute = max([compute_levels.get(a["estimated_cost"]["compute"], 0) for a in actions], default=0)
        compute_level = ["low", "medium", "high"][max_compute]
        
        return {
            "time": total_time,
            "tokens": total_tokens,
            "compute": compute_level
        }


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="补齐决策模块")
    parser.add_argument("--diagnostic-report", required=True, help="诊断报告JSON文件")
    parser.add_argument("--environment-profile", required=True, help="环境画像JSON文件")
    parser.add_argument("--cost-budget", help="成本预算JSON文件")
    parser.add_argument("--output", required=True, help="输出文件路径")
    
    args = parser.parse_args()
    
    # 读取输入
    with open(args.diagnostic_report, 'r', encoding='utf-8') as f:
        diagnostic_report = json.load(f)
    
    with open(args.environment_profile, 'r', encoding='utf-8') as f:
        environment_profile = json.load(f)
    
    input_data = {
        "diagnostic_report": diagnostic_report,
        "environment_profile": environment_profile
    }
    
    if args.cost_budget:
        with open(args.cost_budget, 'r', encoding='utf-8') as f:
            input_data["cost_budget"] = json.load(f)
    else:
        input_data["cost_budget"] = {"time_limit": 300, "token_limit": 10000}
    
    # 执行
    decider = RemediationDecider()
    result = decider.execute(input_data)
    
    # 输出
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"补齐决策完成，策略: {result['remediation_plan']['overall_strategy']}")


if __name__ == "__main__":
    main()
