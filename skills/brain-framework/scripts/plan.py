#!/usr/bin/env python3
"""
Plan 阶段脚本 - 生成实施计划

功能：
1. 基于研究结果生成详细实施计划
2. 列出需要修改的文件清单
3. 记录技术选型和权衡决策

依赖：
- pydantic >= 2.0.0
- pyyaml >= 6.0
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from datetime import datetime


class FileChange:
    """文件变更描述"""
    def __init__(self, file_path: str, operation: str, description: str):
        self.file_path = file_path
        self.operation = operation  # "CREATE" | "MODIFY" | "DELETE"
        self.description = description
        self.dependencies: List[str] = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "operation": self.operation,
            "description": self.description,
            "dependencies": self.dependencies
        }


class TradeOff:
    """决策权衡记录"""
    def __init__(self, decision_point: str, options: List[str], 
                 chosen: str, reason: str):
        self.decision_point = decision_point
        self.options = options
        self.chosen = chosen
        self.reason = reason
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_point": self.decision_point,
            "options": self.options,
            "chosen": self.chosen,
            "reason": self.reason
        }


class PlanOutput:
    """Plan 阶段输出数据模型"""
    def __init__(self, plan_md_path: str, change_files: List[FileChange],
                 trade_offs: List[TradeOff], estimated_complexity: str):
        self.plan_md_path = plan_md_path
        self.change_files = change_files
        self.trade_offs = trade_offs
        self.approval_required = True
        self.estimated_complexity = estimated_complexity
    
    def to_json(self) -> str:
        return json.dumps({
            "plan_md_path": self.plan_md_path,
            "change_files": [f.to_dict() for f in self.change_files],
            "trade_offs": [t.to_dict() for t in self.trade_offs],
            "approval_required": self.approval_required,
            "estimated_complexity": self.estimated_complexity
        }, indent=2, ensure_ascii=False)


def parse_research_summary(research_md_path: str) -> str:
    """
    解析 research.md 获取摘要信息
    
    Args:
        research_md_path: research.md 文件路径
    
    Returns:
        摘要文本
    """
    if not os.path.exists(research_md_path):
        return "未提供 Research 结果"
    
    with open(research_md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 提取前 30 行作为摘要
    summary_lines = []
    for i, line in enumerate(lines[:30]):
        summary_lines.append(line)
        if "关键发现" in line:
            break
    
    return "".join(summary_lines)


def generate_plan_markdown(task: str, research_summary: str, 
                          constraints: List[str]) -> str:
    """
    生成 plan.md 内容
    
    Args:
        task: 任务描述
        research_summary: Research 阶段摘要
        constraints: 约束条件列表
    
    Returns:
        Markdown 格式的实施计划
    """
    lines = [
        f"# Implementation Plan - {task}",
        "",
        f"**创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "> ⚠️ **当前状态**: 方案设计阶段，**尚未实施**",
        "> 📝 **请批注**: 直接在本文件上进行修改和批注",
        "> 🔄 **迭代**: 会根据批注更新方案",
        "> ✅ **批准**: 审查完成后告诉我\"批准，开始实施\"",
        "> 🚫 **重要**: don't implement yet",
        "",
        "---",
        "",
        "## 任务目标",
        "",
        f"{task}",
        "",
        "## Research 摘要",
        "",
        research_summary if research_summary else "无 Research 阶段",
        "",
        "## 约束条件",
        "",
    ]
    
    if constraints:
        for constraint in constraints:
            lines.append(f"- {constraint}")
    else:
        lines.append("- 无特定约束")
    
    lines.extend([
        "",
        "## 实施方案",
        "",
        "### 阶段划分",
        "",
        "1. **准备阶段**: 环境配置、依赖安装",
        "2. **核心实现**: 主要功能开发",
        "3. **测试验证**: 单元测试、集成测试",
        "4. **文档更新**: API 文档、使用说明",
        "",
        "### 文件变更清单",
        "",
        "| 文件路径 | 操作类型 | 描述说明 | 依赖项 |",
        "|---------|---------|---------|--------|",
        "| - | - | - | - |",
        "",
        "> 请在此处填写需要修改的文件清单",
        "",
        "### 技术选型",
        "",
        "> 请在此处填写技术选型说明",
        "",
        "### 权衡决策",
        "",
        "| 决策点 | 可选方案 | 选定方案 | 原因说明 |",
        "|-------|---------|---------|---------|",
        "| - | - | - | - |",
        "",
        "> 请在此处记录重要的技术决策和权衡",
        "",
        "## 风险评估",
        "",
        "- [ ] 破坏现有功能",
        "- [ ] 引入新依赖导致兼容性问题",
        "- [ ] 性能下降",
        "- [ ] 安全漏洞",
        "",
        "## 回滚计划",
        "",
        "> 请在此处填写回滚方案",
        "",
        "---",
        "",
        "## 审查批注区",
        "",
        "> 用户批注将追加到这里...",
        "",
        "---",
        "",
        "> 本计划由 plan.py 生成，请审查后批准实施",
    ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="生成实施计划 - Plan 阶段")
    parser.add_argument("--task", required=True, help="任务描述")
    parser.add_argument("--research", help="research.md 文件路径（可选）")
    parser.add_argument("--output", default="plan.md", help="输出文件路径")
    parser.add_argument("--constraint", action="append", default=[], 
                       help="约束条件（可多次使用）")
    
    args = parser.parse_args()
    
    try:
        # 解析 research 摘要
        research_summary = ""
        if args.research:
            print(f"[Plan] 读取 Research 结果: {args.research}")
            research_summary = parse_research_summary(args.research)
        
        # 生成计划
        markdown_content = generate_plan_markdown(
            args.task, research_summary, args.constraint
        )
        
        # 写入文件
        output_path = Path(args.output)
        output_path.write_text(markdown_content, encoding='utf-8')
        
        print(f"[Plan] 计划已生成: {args.output}")
        
        # 构建输出对象
        output = PlanOutput(
            plan_md_path=str(output_path.absolute()),
            change_files=[],
            trade_offs=[],
            estimated_complexity="medium"
        )
        
        # 输出 JSON 结果
        print(output.to_json())
        
        print(f"[Plan] 请审查 {args.output} 后提供批注或批准")
        sys.exit(0)
        
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
