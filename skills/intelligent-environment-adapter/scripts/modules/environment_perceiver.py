"""
模块A：环境感知模块 (Environment Perception Module)

职责：分析任务特征，生成环境画像
边界：不涉及能力评估、短板诊断
"""

import json
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class EnvironmentProfile:
    """环境画像数据结构"""
    task_type: str           # 任务类型：信息检索/深度分析/内容创作/问题解决
    domain: List[str]        # 涉及的领域列表
    time_sensitivity: str    # 时效性：静态/实时/预测
    data_type: str           # 数据类型：纯文本/多模态/大规模
    complexity: str          # 复杂度：简单/中等/复杂/极复杂


class EnvironmentPerceiver:
    """
    环境感知模块
    
    职责边界：
    - ✅ 分析任务描述，识别任务特征
    - ✅ 生成结构化的环境画像
    - ❌ 不涉及能力评估
    - ❌ 不涉及短板诊断
    """
    
    # 任务类型关键词映射
    TASK_TYPE_KEYWORDS = {
        "信息检索": ["搜索", "查找", "获取", "寻找", "查询", "检索"],
        "深度分析": ["分析", "研究", "评估", "诊断", "对比", "洞察"],
        "内容创作": ["生成", "创作", "编写", "设计", "制作", "撰写"],
        "问题解决": ["解决", "修复", "优化", "处理", "实现", "完成"]
    }
    
    # 时效性关键词映射
    TIME_SENSITIVITY_KEYWORDS = {
        "实时": ["实时", "最新", "当前", "即时", "现在", "今日"],
        "预测": ["预测", "未来", "趋势", "预计", "展望"],
        "静态": ["历史", "过去", "静态", "固定", "不变"]
    }
    
    # 数据类型关键词映射
    DATA_TYPE_KEYWORDS = {
        "多模态": ["图片", "图像", "视频", "音频", "图表", "可视化", "多模态"],
        "大规模": ["大量", "批量", "海量", "大规模", "大数据"],
        "纯文本": ["文本", "文档", "文章", "报告", "文字"]
    }
    
    # 复杂度评估维度
    COMPLEXITY_INDICATORS = {
        "简单": 1,
        "中等": 2,
        "复杂": 3,
        "极复杂": 4
    }

    def __init__(self):
        pass

    def execute(self, input_data: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        模块执行入口
        
        Args:
            input_data: {
                "task_description": str,  # 任务描述
                "context": dict (optional)  # 可选的上下文信息
            }
            config: 可选配置参数
        
        Returns:
            {
                "environment_profile": EnvironmentProfile,
                "confidence": float  # 分析置信度
            }
        """
        task_description = input_data.get("task_description", "")
        context = input_data.get("context", {})
        
        if not task_description:
            raise ValueError("任务描述不能为空")
        
        # 执行环境感知
        profile = self._perceive_environment(task_description, context)
        
        return {
            "environment_profile": {
                "task_type": profile.task_type,
                "domain": profile.domain,
                "time_sensitivity": profile.time_sensitivity,
                "data_type": profile.data_type,
                "complexity": profile.complexity
            },
            "confidence": self._calculate_confidence(task_description, profile)
        }

    def _perceive_environment(self, task_description: str, context: Dict[str, Any]) -> EnvironmentProfile:
        """
        感知环境特征
        """
        # 识别任务类型
        task_type = self._identify_task_type(task_description)
        
        # 识别领域
        domain = self._identify_domain(task_description, context)
        
        # 识别时效性
        time_sensitivity = self._identify_time_sensitivity(task_description)
        
        # 识别数据类型
        data_type = self._identify_data_type(task_description)
        
        # 评估复杂度
        complexity = self._assess_complexity(task_description, domain)
        
        return EnvironmentProfile(
            task_type=task_type,
            domain=domain,
            time_sensitivity=time_sensitivity,
            data_type=data_type,
            complexity=complexity
        )

    def _identify_task_type(self, description: str) -> str:
        """识别任务类型"""
        scores = {}
        for task_type, keywords in self.TASK_TYPE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in description)
            scores[task_type] = score
        
        if max(scores.values()) == 0:
            return "问题解决"  # 默认类型
        
        return max(scores, key=scores.get)

    def _identify_domain(self, description: str, context: Dict[str, Any]) -> List[str]:
        """识别涉及的领域"""
        domains = []
        
        # 领域关键词映射
        domain_keywords = {
            "法律": ["法律", "法规", "政策", "合规", "司法", "合同", "条款"],
            "金融": ["金融", "投资", "股票", "基金", "理财", "贷款", "银行"],
            "技术": ["代码", "编程", "开发", "软件", "系统", "架构", "API"],
            "医疗": ["医疗", "健康", "诊断", "药物", "治疗", "医院"],
            "教育": ["教育", "学习", "课程", "教学", "培训", "考试"],
            "营销": ["营销", "推广", "广告", "品牌", "市场", "销售"],
            "AI": ["AI", "人工智能", "机器学习", "深度学习", "模型", "算法"],
            "数据分析": ["数据", "统计", "分析", "报表", "指标", "可视化"]
        }
        
        for domain, keywords in domain_keywords.items():
            if any(kw in description for kw in keywords):
                domains.append(domain)
        
        # 从上下文获取额外领域信息
        if context and "domain" in context:
            for d in context["domain"]:
                if d not in domains:
                    domains.append(d)
        
        return domains if domains else ["通用"]

    def _identify_time_sensitivity(self, description: str) -> str:
        """识别时效性需求"""
        for sensitivity, keywords in self.TIME_SENSITIVITY_KEYWORDS.items():
            if any(kw in description for kw in keywords):
                return sensitivity
        return "静态"  # 默认静态

    def _identify_data_type(self, description: str) -> str:
        """识别数据类型"""
        for data_type, keywords in self.DATA_TYPE_KEYWORDS.items():
            if any(kw in description for kw in keywords):
                return data_type
        return "纯文本"  # 默认纯文本

    def _assess_complexity(self, description: str, domain: List[str]) -> str:
        """评估任务复杂度"""
        score = 1  # 基础复杂度
        
        # 领域复杂度
        complex_domains = ["法律", "金融", "AI", "技术"]
        score += sum(0.5 for d in domain if d in complex_domains)
        
        # 描述长度
        if len(description) > 100:
            score += 0.5
        if len(description) > 200:
            score += 0.5
        
        # 多领域
        if len(domain) > 2:
            score += 0.5
        
        # 映射到复杂度等级
        if score <= 1.5:
            return "简单"
        elif score <= 2.5:
            return "中等"
        elif score <= 3.5:
            return "复杂"
        else:
            return "极复杂"

    def _calculate_confidence(self, description: str, profile: EnvironmentProfile) -> float:
        """计算分析置信度"""
        confidence = 0.8  # 基础置信度
        
        # 描述越详细，置信度越高
        if len(description) > 50:
            confidence += 0.05
        if len(description) > 100:
            confidence += 0.05
        
        # 识别到的领域越多，置信度越高
        if len(profile.domain) >= 2:
            confidence += 0.05
        
        return min(confidence, 1.0)


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="环境感知模块")
    parser.add_argument("--task-description", required=True, help="任务描述")
    parser.add_argument("--context", help="上下文信息JSON")
    parser.add_argument("--output", required=True, help="输出文件路径")
    
    args = parser.parse_args()
    
    # 构建输入
    input_data = {"task_description": args.task_description}
    if args.context:
        input_data["context"] = json.loads(args.context)
    
    # 执行
    perceiver = EnvironmentPerceiver()
    result = perceiver.execute(input_data)
    
    # 输出
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"环境感知完成，结果已保存到: {args.output}")


if __name__ == "__main__":
    main()
