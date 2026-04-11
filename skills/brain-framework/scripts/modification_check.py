#!/usr/bin/env python3
"""
Modification Check 脚本 - 修改类型检查

功能：
1. 判断修改是否触及架构红线
2. 输出 CONTINUE/ROLLBACK/ASK_USER 决策
3. 生成修复建议

依赖：
- pydantic >= 2.0.0
"""

import argparse
import json
import os
import sys
from typing import List, Dict, Any, Optional

# 平台 SDK（运行环境已预装）
try:
    from coze_workload_identity import requests
    COZE_SDK_AVAILABLE = True
except ImportError:
    COZE_SDK_AVAILABLE = False


class ModificationCheckOutput:
    """修改检查输出数据模型"""
    def __init__(self, action: str, modification_type: str, 
                 reason: str, confidence: float, suggested_fix: str = ""):
        self.action = action  # "CONTINUE" | "ROLLBACK_TO_PLAN" | "ASK_USER"
        self.modification_type = modification_type
        self.reason = reason
        self.confidence = confidence
        self.suggested_fix = suggested_fix
    
    def to_json(self) -> str:
        return json.dumps({
            "action": self.action,
            "modification_type": self.modification_type,
            "reason": self.reason,
            "confidence": self.confidence,
            "suggested_fix": self.suggested_fix
        }, indent=2, ensure_ascii=False)


class RuleChecker:
    """规则检查器"""
    
    # 红线规则（必须回 Plan 阶段）
    MUST_ROLLBACK_KEYWORDS = [
        "node_count_change",      # 节点数量变化
        "edge_relation_change",   # 连接关系变化
        "state_structure_change", # 状态结构变化
        "contract_inconsistency", # 数据流契约不一致
        "new_skill_integration",  # 新技能集成
        "new_subgraph_or_loop",   # 新增子图/循环
        "架构变更", "架构调整", "架构重构",
        "新增节点", "删除节点", "节点数量",
        "状态结构", "状态字段",
        "数据流", "契约",
        "外部集成", "第三方集成",
        "子图", "循环结构"
    ]
    
    # 绿灯规则（可在 Implement 阶段）
    ALLOW_IN_IMPLEMENT_KEYWORDS = [
        "internal_logic_optimization",  # 函数内部优化
        "variable_naming",              # 变量命名
        "comment_format",               # 注释格式
        "prompt_tuning",                # Prompt 微调
        "config_parameter",             # 配置参数
        "内部逻辑", "函数优化", "逻辑优化",
        "变量命名", "重命名变量",
        "注释", "注释格式",
        "配置", "参数调整",
        "代码格式", "格式化"
    ]
    
    @staticmethod
    def check(changes_text: str) -> ModificationCheckOutput:
        """
        基于规则的快速检查
        
        Args:
            changes_text: 修改描述文本
        
        Returns:
            检查结果
        """
        changes_lower = changes_text.lower()
        
        # 红线检查
        for keyword in RuleChecker.MUST_ROLLBACK_KEYWORDS:
            if keyword.lower() in changes_lower:
                return ModificationCheckOutput(
                    action="ROLLBACK_TO_PLAN",
                    modification_type="arch_change",
                    reason=f"触及红线规则: {keyword}",
                    confidence=1.0,
                    suggested_fix="请回到 Plan 阶段，更新 plan.md 中的架构设计"
                )
        
        # 绿灯检查
        for keyword in RuleChecker.ALLOW_IN_IMPLEMENT_KEYWORDS:
            if keyword.lower() in changes_lower:
                return ModificationCheckOutput(
                    action="CONTINUE",
                    modification_type="impl_detail",
                    reason=f"符合实现级规则: {keyword}",
                    confidence=0.9
                )
        
        # 未知类型，需要人工判断
        return ModificationCheckOutput(
            action="ASK_USER",
            modification_type="unknown",
            reason="无法确定修改类型（规则未匹配）",
            confidence=0.5,
            suggested_fix="请人工确认：这是架构变更还是实现细节？"
        )


def llm_judge(changes_text: str, plan_summary: str, 
              affected_files: List[str]) -> ModificationCheckOutput:
    """
    使用 LLM 进行语义判断
    
    通过平台提供的 LLM API 进行智能判断，识别修改类型。
    
    Args:
        changes_text: 修改描述文本
        plan_summary: 计划摘要
        affected_files: 受影响文件列表
    
    Returns:
        检查结果
    """
    # 检查 SDK 可用性
    if not COZE_SDK_AVAILABLE:
        return ModificationCheckOutput(
            action="ASK_USER",
            modification_type="unknown",
            reason="LLM SDK 未安装或不可用",
            confidence=0.3,
            suggested_fix="移除 --use-llm 参数，使用规则检查（默认）"
        )
    
    # 构建 LLM 请求
    prompt = f"""你是一个代码架构专家。请判断以下代码修改是"架构变更"还是"实现细节"。

## 修改描述
{changes_text}

## 原计划摘要
{plan_summary if plan_summary else "无"}

## 受影响文件
{', '.join(affected_files) if affected_files else "无"}

## 判断标准
- 架构变更：涉及节点数量变化、连接关系变化、状态结构变化、数据流契约变化、外部集成
- 实现细节：函数内部优化、变量命名、注释格式、配置参数、代码格式

## 输出格式（JSON）
{{"type": "arch_change|impl_detail|unknown", "reason": "判断理由", "confidence": 0.0-1.0}}

请只输出 JSON，不要其他内容。"""

    try:
        # 调用平台 LLM API
        response = requests.post(
            "https://api.coze.cn/v1/chat",
            headers={
                "Content-Type": "application/json",
            },
            json={
                "model": "default",
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code >= 400:
            return ModificationCheckOutput(
                action="ASK_USER",
                modification_type="unknown",
                reason=f"LLM API 调用失败: HTTP {response.status_code}",
                confidence=0.3,
                suggested_fix="请人工判断修改类型"
            )
        
        # 解析响应
        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # 提取 JSON
        import re
        json_match = re.search(r'\{[^}]+\}', content)
        if not json_match:
            return ModificationCheckOutput(
                action="ASK_USER",
                modification_type="unknown",
                reason="LLM 返回格式异常",
                confidence=0.3,
                suggested_fix="请人工判断修改类型"
            )
        
        result = json.loads(json_match.group())
        mod_type = result.get("type", "unknown")
        reason = result.get("reason", "LLM 判断")
        confidence = result.get("confidence", 0.5)
        
        # 映射到决策
        if mod_type == "arch_change":
            return ModificationCheckOutput(
                action="ROLLBACK_TO_PLAN",
                modification_type="arch_change",
                reason=f"LLM 判断为架构变更: {reason}",
                confidence=confidence,
                suggested_fix="请回到 Plan 阶段，更新架构设计"
            )
        elif mod_type == "impl_detail":
            return ModificationCheckOutput(
                action="CONTINUE",
                modification_type="impl_detail",
                reason=f"LLM 判断为实现细节: {reason}",
                confidence=confidence
            )
        else:
            return ModificationCheckOutput(
                action="ASK_USER",
                modification_type="unknown",
                reason=f"LLM 无法确定: {reason}",
                confidence=confidence,
                suggested_fix="请人工确认修改类型"
            )
            
    except json.JSONDecodeError:
        return ModificationCheckOutput(
            action="ASK_USER",
            modification_type="unknown",
            reason="LLM 响应解析失败",
            confidence=0.3,
            suggested_fix="请人工判断修改类型，或移除 --use-llm 使用规则检查"
        )
    except Exception as e:
        error_msg = str(e)
        # 针对常见错误提供更友好的提示
        if "COZE_OUTBOUND_AUTH_PROXY" in error_msg:
            friendly_msg = "平台 LLM 服务未配置（需要在平台环境中运行）"
        elif "timeout" in error_msg.lower():
            friendly_msg = "LLM 请求超时"
        elif "connection" in error_msg.lower():
            friendly_msg = "LLM 服务连接失败"
        else:
            friendly_msg = f"LLM 调用异常: {error_msg}"
        
        return ModificationCheckOutput(
            action="ASK_USER",
            modification_type="unknown",
            reason=friendly_msg,
            confidence=0.3,
            suggested_fix="请人工判断修改类型，或移除 --use-llm 使用规则检查"
        )


def main():
    parser = argparse.ArgumentParser(description="修改类型检查")
    parser.add_argument("--changes", required=True, 
                       help="修改描述（可以是多个，用逗号分隔）")
    parser.add_argument("--plan", help="当前 plan.md 内容摘要")
    parser.add_argument("--affected-files", 
                       help="受影响文件列表（逗号分隔）")
    parser.add_argument("--use-llm", action="store_true",
                       help="使用 LLM 进行语义判断（简化版）")
    parser.add_argument("--output", help="输出 JSON 文件路径")
    
    args = parser.parse_args()
    
    try:
        # 解析输入
        changes_list = [c.strip() for c in args.changes.split(',')]
        changes_text = " ".join(changes_list)
        
        plan_summary = args.plan if args.plan else ""
        affected_files = args.affected_files.split(',') if args.affected_files else []
        
        # 执行检查
        if args.use_llm:
            # 使用 LLM 判断
            print("[ModificationCheck] 使用 LLM 语义判断")
            result = llm_judge(changes_text, plan_summary, affected_files)
        else:
            # 使用规则检查
            print("[ModificationCheck] 使用规则快速检查")
            result = RuleChecker.check(changes_text)
        
        # 输出结果
        print(result.to_json())
        
        # 写入文件（如果指定）
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result.to_json())
            print(f"[ModificationCheck] 结果已写入: {args.output}")
        
        # 返回码
        if result.action == "CONTINUE":
            sys.exit(0)
        elif result.action == "ROLLBACK_TO_PLAN":
            sys.exit(2)  # 特殊退出码表示需要回滚
        else:  # ASK_USER
            sys.exit(3)  # 特殊退出码表示需要人工决策
            
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
