"""
模块C：短板诊断模块 (Shortage Diagnosis Module)

职责：生成详细的短板诊断报告
边界：不涉及补齐策略选择
"""

import json
from typing import Dict, Any, List
from dataclasses import dataclass


class ShortageDiagnoser:
    """
    短板诊断模块
    
    职责边界：
    - ✅ 生成诊断报告
    - ✅ 评估短板严重程度
    - ✅ 提供补齐建议方向
    - ❌ 不进行补齐策略选择
    - ❌ 不生成补齐计划
    """
    
    # 补齐建议映射
    REMEDIATION_SUGGESTIONS = {
        "knowledge_gap": [
            "搜索并加载相关领域技能",
            "构建领域知识模型",
            "获取专业文档和参考资料"
        ],
        "data_source_gap": [
            "搜索替代数据源",
            "集成实时数据API",
            "使用缓存数据"
        ],
        "realtime_gap": [
            "集成实时数据API",
            "优化数据更新机制",
            "调整时效性预期"
        ],
        "capability_gap": [
            "搜索并加载特定能力技能",
            "组合多个现有技能",
            "委托人类专家处理"
        ],
        "processing_gap": [
            "优化处理流程",
            "分布式处理任务",
            "简化处理需求"
        ],
        "reasoning_gap": [
            "使用推理增强工具",
            "分解复杂问题",
            "获取专家指导"
        ],
        "presentation_gap": [
            "使用专业模板",
            "加载输出优化技能",
            "参考行业标准格式"
        ],
        "multimodal_gap": [
            "搜索图像生成技能",
            "加载视频处理技能",
            "组合多个媒体处理技能"
        ],
        "integration_gap": [
            "构建适配器层",
            "标准化数据格式",
            "实现错误处理机制"
        ],
        "coordination_gap": [
            "优化任务编排",
            "使用工作流管理工具",
            "简化协作流程"
        ],
        "learning_gap": [
            "实现反馈收集机制",
            "建立经验库",
            "使用强化学习优化"
        ],
        "optimization_gap": [
            "实现自动调优机制",
            "使用A/B测试",
            "建立性能监控"
        ]
    }

    def __init__(self):
        pass

    def execute(self, input_data: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        模块执行入口
        
        Args:
            input_data: {
                "mapping_result": {
                    "match_score": float,
                    "layer_scores": dict,
                    "shortages": list
                },
                "environment_profile": dict  # 可选，用于丰富诊断
            }
        
        Returns:
            {
                "diagnostic_report": {
                    "overall_status": str,
                    "match_score": float,
                    "critical_shortages_count": int,
                    "moderate_shortages_count": int,
                    "minor_shortages_count": int,
                    "shortage_details": list
                }
            }
        """
        mapping_result = input_data.get("mapping_result", {})
        environment_profile = input_data.get("environment_profile", {})
        
        match_score = mapping_result.get("match_score", 0.0)
        shortages = mapping_result.get("shortages", [])
        
        # 生成详细诊断
        shortage_details = self._generate_shortage_details(shortages, environment_profile)
        
        # 统计各严重程度数量
        critical_count = sum(1 for s in shortage_details if s.get("severity") == "critical")
        moderate_count = sum(1 for s in shortage_details if s.get("severity") == "moderate")
        minor_count = sum(1 for s in shortage_details if s.get("severity") == "minor")
        
        # 确定整体状态
        overall_status = self._determine_overall_status(match_score, critical_count)
        
        return {
            "diagnostic_report": {
                "overall_status": overall_status,
                "match_score": match_score,
                "critical_shortages_count": critical_count,
                "moderate_shortages_count": moderate_count,
                "minor_shortages_count": minor_count,
                "shortage_details": shortage_details
            }
        }

    def _generate_shortage_details(
        self, 
        shortages: List[Dict[str, Any]],
        environment_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """生成详细的短板信息"""
        details = []
        
        for shortage in shortages:
            shortage_type = shortage.get("type", "")
            
            # 获取补齐建议
            suggestions = self.REMEDIATION_SUGGESTIONS.get(shortage_type, ["建议补充相关能力"])
            
            detail = {
                **shortage,
                "remediation_suggestions": suggestions,
                "layer_name": self._get_layer_name(shortage.get("layer", "")),
                "possible_causes": self._analyze_causes(shortage, environment_profile)
            }
            details.append(detail)
        
        return details

    def _determine_overall_status(self, match_score: float, critical_count: int) -> str:
        """确定整体状态"""
        if match_score >= 0.85:
            return "excellent"
        elif match_score >= 0.70:
            if critical_count > 0:
                return "fair"
            return "good"
        elif match_score >= 0.60:
            if critical_count > 0:
                return "poor"
            return "fair"
        elif match_score >= 0.40:
            return "poor"
        else:
            return "critical"

    def _get_layer_name(self, layer: str) -> str:
        """获取层级中文名称"""
        names = {
            "L1": "信息获取层",
            "L2": "认知处理层",
            "L3": "创作呈现层",
            "L4": "协作编排层",
            "L5": "自我进化层"
        }
        return names.get(layer, layer)

    def _analyze_causes(
        self, 
        shortage: Dict[str, Any],
        environment_profile: Dict[str, Any]
    ) -> List[str]:
        """分析可能的原因"""
        causes = []
        shortage_type = shortage.get("type", "")
        layer = shortage.get("layer", "")
        
        if shortage_type == "knowledge_gap":
            domain = environment_profile.get("domain", [])
            if domain:
                causes.append(f"缺乏{','.join(domain[:2])}领域的专业知识积累")
            causes.append("可能需要加载专业领域技能")
        
        elif shortage_type == "data_source_gap":
            causes.append("现有数据源无法满足任务需求")
            causes.append("可能需要集成外部数据API")
        
        elif shortage_type == "realtime_gap":
            time_sensitivity = environment_profile.get("time_sensitivity", "")
            if time_sensitivity == "实时":
                causes.append("任务需要实时数据，但缺乏实时数据获取能力")
        
        elif shortage_type == "multimodal_gap":
            causes.append("缺乏多模态内容处理能力")
            causes.append("可能需要图像、视频等处理技能")
        
        elif shortage_type == "capability_gap":
            causes.append("当前技能库缺少特定能力")
        
        else:
            causes.append("需要进一步分析具体原因")
        
        return causes


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="短板诊断模块")
    parser.add_argument("--mapping-result", required=True, help="映射结果JSON文件")
    parser.add_argument("--environment-profile", help="环境画像JSON文件")
    parser.add_argument("--output", required=True, help="输出文件路径")
    
    args = parser.parse_args()
    
    # 读取输入
    with open(args.mapping_result, 'r', encoding='utf-8') as f:
        mapping_result = json.load(f)
    
    input_data = {"mapping_result": mapping_result}
    
    if args.environment_profile:
        with open(args.environment_profile, 'r', encoding='utf-8') as f:
            input_data["environment_profile"] = json.load(f)
    
    # 执行
    diagnoser = ShortageDiagnoser()
    result = diagnoser.execute(input_data)
    
    # 输出
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"短板诊断完成，整体状态: {result['diagnostic_report']['overall_status']}")


if __name__ == "__main__":
    main()
