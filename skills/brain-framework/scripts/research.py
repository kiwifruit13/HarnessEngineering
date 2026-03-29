#!/usr/bin/env python3
"""
Research 阶段脚本 - 代码库深度分析

功能：
1. 遍历代码库，分析文件结构和依赖关系
2. 识别关键文件和潜在风险点
3. 生成 research.md 分析报告

依赖：
- pydantic >= 2.0.0
- pyyaml >= 6.0
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import json


class ResearchOutput:
    """Research 阶段输出数据模型"""
    
    def __init__(self, research_md_path: str, key_findings: List[str], 
                 risk_points: List[str], confidence_score: float):
        self.research_md_path = research_md_path
        self.key_findings = key_findings
        self.risk_points = risk_points
        self.confidence_score = confidence_score
    
    def to_json(self) -> str:
        """序列化为 JSON"""
        return json.dumps({
            "research_md_path": self.research_md_path,
            "key_findings": self.key_findings,
            "risk_points": self.risk_points,
            "confidence_score": self.confidence_score
        }, indent=2, ensure_ascii=False)


def analyze_codebase(codebase_root: str, task: str) -> Dict[str, Any]:
    """
    分析代码库结构
    
    Args:
        codebase_root: 代码库根目录路径
        task: 任务描述，用于聚焦分析重点
    
    Returns:
        包含分析结果的字典
    """
    root = Path(codebase_root)
    
    # 收集所有代码文件
    code_files = []
    for pattern in ["*.py", "*.js", "*.ts", "*.java", "*.go", "*.rs"]:
        code_files.extend(root.rglob(pattern))
    
    # 过滤掉测试文件和虚拟环境
    code_files = [
        f for f in code_files 
        if "test" not in f.name.lower() 
        and "node_modules" not in str(f)
        and "venv" not in str(f)
        and ".venv" not in str(f)
        and "__pycache__" not in str(f)
    ]
    
    # 分析文件结构
    structure = {}
    for file_path in code_files:
        rel_path = file_path.relative_to(root)
        parts = list(rel_path.parts[:-1])
        current = structure
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]
    
    # 识别关键文件（基于文件名和目录）
    key_files = []
    for file_path in code_files:
        name_lower = file_path.name.lower()
        # 识别常见的核心文件
        if any(keyword in name_lower for keyword in 
               ["main", "app", "index", "config", "core", "base", "init"]):
            key_files.append(str(file_path.relative_to(root)))
    
    # 识别潜在风险点（基于文件大小和复杂度）
    risk_points = []
    for file_path in code_files:
        try:
            size = file_path.stat().st_size
            # 超过 10KB 的文件可能需要特别关注
            if size > 10240:
                risk_points.append(f"大文件: {file_path.relative_to(root)} ({size} bytes)")
            
            # 统计行数（简单启发式）
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = sum(1 for _ in f)
                if lines > 500:
                    risk_points.append(f"长文件: {file_path.relative_to(root)} ({lines} lines)")
        except Exception as e:
            risk_points.append(f"无法读取: {file_path.relative_to(root)} - {str(e)}")
    
    return {
        "total_files": len(code_files),
        "structure": structure,
        "key_files": key_files,
        "risk_points": risk_points,
        "languages": list(set(f.suffix for f in code_files))
    }


def generate_research_markdown(task: str, codebase_root: str, 
                              analysis: Dict[str, Any]) -> str:
    """
    生成 research.md 内容
    
    Args:
        task: 任务描述
        codebase_root: 代码库根目录
        analysis: 分析结果
    
    Returns:
        Markdown 格式的研究报告
    """
    lines = [
        f"# Research Report - {task}",
        "",
        f"**代码库路径**: `{codebase_root}`",
        f"**分析时间**: {os.popen('date').read().strip()}",
        "",
        "## 概览",
        "",
        f"- **总文件数**: {analysis['total_files']}",
        f"- **涉及语言**: {', '.join(analysis['languages'])}",
        f"- **关键文件数**: {len(analysis['key_files'])}",
        f"- **风险点数**: {len(analysis['risk_points'])}",
        "",
        "## 目录结构",
        "",
    ]
    
    # 输出目录结构
    def print_structure(structure: Dict, indent: int = 0):
        for key, value in structure.items():
            lines.append("  " * indent + f"- {key}/")
            if value:
                print_structure(value, indent + 1)
    
    print_structure(analysis['structure'])
    
    lines.extend([
        "",
        "## 关键文件",
        "",
    ])
    
    for file_path in analysis['key_files']:
        lines.append(f"- `{file_path}`")
    
    lines.extend([
        "",
        "## 风险点",
        "",
    ])
    
    for risk in analysis['risk_points']:
        lines.append(f"- ⚠️ {risk}")
    
    lines.extend([
        "",
        "## 关键发现",
        "",
        "请 AI 智能体根据以上分析，识别以下内容：",
        "",
        "1. **核心模块识别**: 哪些文件/模块是系统的核心？",
        "2. **依赖关系**: 模块之间的依赖关系是什么？",
        "3. **潜在影响**: 修改这些文件可能影响哪些其他模块？",
        "4. **建议策略**: 建议采用什么策略进行改造？",
        "",
        "---",
        "",
        "> 本报告由 research.py 自动生成",
    ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="代码库深度分析 - Research 阶段")
    parser.add_argument("--task", required=True, help="任务描述")
    parser.add_argument("--codebase-root", required=True, help="代码库根目录路径")
    parser.add_argument("--output", default="research.md", help="输出文件路径")
    parser.add_argument("--depth", default="medium", 
                       choices=["shallow", "medium", "deep"],
                       help="分析深度")
    
    args = parser.parse_args()
    
    # 验证代码库路径
    if not os.path.exists(args.codebase_root):
        print(f"错误: 代码库路径不存在: {args.codebase_root}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # 分析代码库
        print(f"[Research] 开始分析代码库: {args.codebase_root}")
        analysis = analyze_codebase(args.codebase_root, args.task)
        print(f"[Research] 找到 {analysis['total_files']} 个代码文件")
        
        # 生成报告
        markdown_content = generate_research_markdown(
            args.task, args.codebase_root, analysis
        )
        
        # 写入文件
        output_path = Path(args.output)
        output_path.write_text(markdown_content, encoding='utf-8')
        
        print(f"[Research] 报告已生成: {args.output}")
        
        # 构建输出对象
        key_findings = [
            f"代码库包含 {analysis['total_files']} 个文件",
            f"涉及 {len(analysis['languages'])} 种编程语言",
            f"识别到 {len(analysis['key_files'])} 个关键文件",
        ]
        
        output = ResearchOutput(
            research_md_path=str(output_path.absolute()),
            key_findings=key_findings,
            risk_points=analysis['risk_points'],
            confidence_score=0.8  # 基于分析结果估算
        )
        
        # 输出 JSON 结果
        print(output.to_json())
        
        # 返回码
        if len(analysis['risk_points']) > 10:
            print("[Research] 警告: 发现较多风险点，建议谨慎处理", file=sys.stderr)
            sys.exit(0)
        else:
            sys.exit(0)
            
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
