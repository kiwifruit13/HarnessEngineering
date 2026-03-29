#!/usr/bin/env python3
"""
Annotate 阶段脚本 - 批注管理

功能：
1. 解析用户批注并更新计划
2. 检测批准关键词（批准/approve/ok/go/👍）
3. 管理迭代次数（最多6次）

依赖：
- pydantic >= 2.0.0
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional
import json
from datetime import datetime


class AnnotateOutput:
    """Annotate 阶段输出数据模型"""
    def __init__(self, plan_md_path: str, approved: bool, 
                 next_action: str, iteration_count: int):
        self.plan_md_path = plan_md_path
        self.approved = approved
        self.next_action = next_action  # "continue_annotate" | "proceed_implement" | "rollback"
        self.iteration_count = iteration_count
    
    def to_json(self) -> str:
        return json.dumps({
            "plan_md_path": self.plan_md_path,
            "approved": self.approved,
            "next_action": self.next_action,
            "iteration_count": self.iteration_count
        }, indent=2, ensure_ascii=False)


def check_approval(annotations: str) -> bool:
    """
    检查用户输入是否包含批准关键词
    
    Args:
        annotations: 用户批注内容
    
    Returns:
        是否批准
    """
    if not annotations:
        return False
    
    approval_keywords = ["批准", "approve", "ok", "go", "👍", "同意", "通过"]
    text = annotations.lower()
    
    return any(kw.lower() in text for kw in approval_keywords)


def read_plan(plan_md_path: str) -> str:
    """
    读取 plan.md 内容
    
    Args:
        plan_md_path: plan.md 文件路径
    
    Returns:
        文件内容
    """
    if not os.path.exists(plan_md_path):
        raise FileNotFoundError(f"plan.md 不存在: {plan_md_path}")
    
    with open(plan_md_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_plan(plan_md_path: str, content: str):
    """
    写入 plan.md 内容
    
    Args:
        plan_md_path: plan.md 文件路径
        content: 新内容
    """
    with open(plan_md_path, 'w', encoding='utf-8') as f:
        f.write(content)


def append_annotations(plan_content: str, annotations: str, 
                      iteration_count: int) -> str:
    """
    在 plan.md 中追加批注
    
    Args:
        plan_content: 原始计划内容
        annotations: 用户批注
        iteration_count: 当前迭代次数
    
    Returns:
        更新后的计划内容
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    annotation_block = f"\n\n---\n"
    annotation_block += f"## 📝 用户批注 (迭代 #{iteration_count})\n\n"
    annotation_block += f"**时间**: {timestamp}\n\n"
    annotation_block += f"{annotations}\n"
    
    # 在 "审查批注区" 之后插入
    marker = "## 审查批注区"
    if marker in plan_content:
        parts = plan_content.split(marker, 1)
        if len(parts) == 2:
            # 保留标题和后续内容
            return parts[0] + marker + "\n" + annotation_block + parts[1]
    
    # 如果找不到标记，直接追加到末尾
    return plan_content + annotation_block


def main():
    parser = argparse.ArgumentParser(description="批注管理 - Annotate 阶段")
    parser.add_argument("--plan", required=True, help="plan.md 文件路径")
    parser.add_argument("--annotations", help="用户批注内容")
    parser.add_argument("--iteration", type=int, default=0, 
                       help="当前迭代次数（默认0）")
    parser.add_argument("--max-iterations", type=int, default=6,
                       help="最大迭代次数（默认6）")
    
    args = parser.parse_args()
    
    try:
        # 读取计划
        plan_content = read_plan(args.plan)
        
        # 检查批准状态
        if args.annotations:
            approved = check_approval(args.annotations)
            
            # 更新计划内容
            updated_content = append_annotations(
                plan_content, args.annotations, args.iteration + 1
            )
            write_plan(args.plan, updated_content)
            
            print(f"[Annotate] 批注已追加 (迭代 #{args.iteration + 1})")
        else:
            approved = False
            print("[Annotate] 等待用户批注")
        
        # 决策下一步
        if approved:
            next_action = "proceed_implement"
            print("[Annotate] ✅ 已批准，进入实施阶段")
        elif args.iteration >= args.max_iterations - 1:
            next_action = "rollback"
            print(f"[Annotate] ⚠️ 批注迭代超限 ({args.max_iterations})，建议回滚")
        else:
            next_action = "continue_annotate"
            print(f"[Annotate] 等待下一次批注 (当前: {args.iteration + 1}/{args.max_iterations})")
        
        # 构建输出
        output = AnnotateOutput(
            plan_md_path=str(Path(args.plan).absolute()),
            approved=approved,
            next_action=next_action,
            iteration_count=args.iteration + 1
        )
        
        # 输出 JSON 结果
        print(output.to_json())
        
        sys.exit(0)
        
    except FileNotFoundError as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
