"""
模块B：能力映射模块 (Capability Mapping Module)

职责：计算任务需求与当前能力的匹配度，识别能力断点
边界：不涉及诊断报告生成、补齐决策
"""

import json
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class Shortage:
    """短板数据结构"""
    id: str
    layer: str              # L1-L5
    type: str               # 短板类型
    description: str
    severity: str           # critical/moderate/minor
    impact_core: bool       # 是否影响核心任务


class CapabilityMapper:
    """
    能力映射模块
    
    职责边界：
    - ✅ 计算匹配度
    - ✅ 识别能力断点
    - ❌ 不生成诊断报告
    - ❌ 不进行补齐决策
    """
    
    # 各层权重
    LAYER_WEIGHTS = {
        "L1": 0.20,
        "L2": 0.25,
        "L3": 0.25,
        "L4": 0.15,
        "L5": 0.15
    }
    
    # 短板阈值
    CRITICAL_THRESHOLD = 0.5
    MODERATE_THRESHOLD = 0.6
    MINOR_THRESHOLD = 0.7

    def __init__(self):
        pass

    def execute(self, input_data: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        模块执行入口
        
        Args:
            input_data: {
                "environment_profile": dict,  # 环境画像
                "capability_registry": dict   # 能力清单
            }
        
        Returns:
            {
                "match_score": float,
                "layer_scores": dict,
                "shortages": list
            }
        """
        environment_profile = input_data.get("environment_profile", {})
        capability_registry = input_data.get("capability_registry", {})
        
        if not environment_profile:
            raise ValueError("环境画像不能为空")
        if not capability_registry:
            raise ValueError("能力清单不能为空")
        
        # 计算各层评分
        layer_scores = self._calculate_layer_scores(capability_registry)
        
        # 计算整体匹配度
        match_score = self._calculate_match_score(layer_scores)
        
        # 识别短板
        shortages = self._identify_shortages(
            layer_scores, 
            environment_profile, 
            capability_registry
        )
        
        return {
            "match_score": match_score,
            "layer_scores": layer_scores,
            "shortages": [self._shortage_to_dict(s) for s in shortages]
        }

    def _calculate_layer_scores(self, capability_registry: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """计算各层评分"""
        layer_scores = {}
        
        for layer_name in ["L1", "L2", "L3", "L4", "L5"]:
            layer_caps = capability_registry.get(layer_name, {})
            if layer_caps:
                avg_score = sum(layer_caps.values()) / len(layer_caps)
                layer_scores[layer_name] = round(avg_score, 2)
            else:
                layer_scores[layer_name] = 0.0
        
        return layer_scores

    def _calculate_match_score(self, layer_scores: Dict[str, float]) -> float:
        """计算整体匹配度"""
        total_score = 0.0
        
        for layer_name, score in layer_scores.items():
            weight = self.LAYER_WEIGHTS.get(layer_name, 0.0)
            total_score += score * weight
        
        return round(total_score, 2)

    def _identify_shortages(
        self, 
        layer_scores: Dict[str, float],
        environment_profile: Dict[str, Any],
        capability_registry: Dict[str, Dict[str, float]]
    ) -> List[Shortage]:
        """识别能力短板"""
        shortages = []
        shortage_id = 1
        
        for layer_name, score in layer_scores.items():
            if score < self.MINOR_THRESHOLD:
                # 确定严重程度
                if score < self.CRITICAL_THRESHOLD:
                    severity = "critical"
                elif score < self.MODERATE_THRESHOLD:
                    severity = "moderate"
                else:
                    severity = "minor"
                
                # 确定短板类型
                shortage_type = self._determine_shortage_type(
                    layer_name, 
                    capability_registry.get(layer_name, {}),
                    environment_profile
                )
                
                # 判断是否影响核心任务
                impact_core = self._assess_core_impact(
                    layer_name, 
                    shortage_type, 
                    environment_profile
                )
                
                shortage = Shortage(
                    id=f"shortage_{shortage_id}",
                    layer=layer_name,
                    type=shortage_type,
                    description=self._generate_description(layer_name, shortage_type, environment_profile),
                    severity=severity,
                    impact_core=impact_core
                )
                shortages.append(shortage)
                shortage_id += 1
        
        return shortages

    def _determine_shortage_type(
        self, 
        layer_name: str, 
        layer_caps: Dict[str, float],
        environment_profile: Dict[str, Any]
    ) -> str:
        """确定短板类型"""
        type_mapping = {
            "L1": {
                "realtime_capability": "realtime_gap",
                "data_source_availability": "data_source_gap",
                "default": "knowledge_gap"
            },
            "L2": {
                "domain_knowledge": "knowledge_gap",
                "logical_reasoning": "reasoning_gap",
                "default": "processing_gap"
            },
            "L3": {
                "multimodal_support": "multimodal_gap",
                "output_format": "capability_gap",
                "default": "presentation_gap"
            },
            "L4": {
                "skill_composition": "integration_gap",
                "default": "coordination_gap"
            },
            "L5": {
                "optimization_mechanism": "optimization_gap",
                "default": "learning_gap"
            }
        }
        
        layer_mapping = type_mapping.get(layer_name, {})
        
        # 找出最低分的能力维度
        if layer_caps:
            min_cap = min(layer_caps, key=layer_caps.get)
            if min_cap in layer_mapping:
                return layer_mapping[min_cap]
        
        return layer_mapping.get("default", "unknown")

    def _assess_core_impact(
        self, 
        layer_name: str, 
        shortage_type: str,
        environment_profile: Dict[str, Any]
    ) -> bool:
        """评估是否影响核心任务"""
        # L1层短板通常影响核心
        if layer_name == "L1":
            if shortage_type in ["realtime_gap", "data_source_gap"]:
                return True
        
        # L2层知识缺口影响分析类任务
        if layer_name == "L2" and shortage_type == "knowledge_gap":
            if environment_profile.get("task_type") in ["深度分析", "内容创作"]:
                return True
        
        # L3层多模态缺口影响多模态任务
        if layer_name == "L3" and shortage_type == "multimodal_gap":
            if environment_profile.get("data_type") == "多模态":
                return True
        
        # L4层短板影响复杂任务
        if layer_name == "L4":
            if environment_profile.get("complexity") in ["复杂", "极复杂"]:
                return True
        
        return False

    def _generate_description(
        self, 
        layer_name: str, 
        shortage_type: str,
        environment_profile: Dict[str, Any]
    ) -> str:
        """生成短板描述"""
        descriptions = {
            "knowledge_gap": "专业知识不足",
            "data_source_gap": "数据源不足",
            "realtime_gap": "实时性能力不足",
            "capability_gap": "特定能力缺失",
            "processing_gap": "处理能力不足",
            "reasoning_gap": "推理能力不足",
            "presentation_gap": "呈现质量不足",
            "multimodal_gap": "多模态支持不足",
            "integration_gap": "集成能力不足",
            "coordination_gap": "协调能力不足",
            "learning_gap": "学习能力不足",
            "optimization_gap": "优化能力不足"
        }
        
        base_desc = descriptions.get(shortage_type, "能力不足")
        
        # 添加领域上下文
        domain = environment_profile.get("domain", [])
        if domain and shortage_type in ["knowledge_gap", "capability_gap"]:
            return f"缺乏{','.join(domain[:2])}领域{base_desc[2:]}"
        
        return base_desc

    def _shortage_to_dict(self, shortage: Shortage) -> Dict[str, Any]:
        """转换短板为字典"""
        return {
            "id": shortage.id,
            "layer": shortage.layer,
            "type": shortage.type,
            "description": shortage.description,
            "severity": shortage.severity,
            "impact_core": shortage.impact_core
        }


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="能力映射模块")
    parser.add_argument("--environment-profile", required=True, help="环境画像JSON文件")
    parser.add_argument("--capability-registry", required=True, help="能力清单JSON文件")
    parser.add_argument("--output", required=True, help="输出文件路径")
    
    args = parser.parse_args()
    
    # 读取输入
    with open(args.environment_profile, 'r', encoding='utf-8') as f:
        environment_profile = json.load(f)
    
    with open(args.capability_registry, 'r', encoding='utf-8') as f:
        capability_registry = json.load(f)
    
    # 执行
    mapper = CapabilityMapper()
    result = mapper.execute({
        "environment_profile": environment_profile,
        "capability_registry": capability_registry
    })
    
    # 输出
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"能力映射完成，匹配度: {result['match_score']}")


if __name__ == "__main__":
    main()
