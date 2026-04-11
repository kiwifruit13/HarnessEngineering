#!/usr/bin/env python3
"""
DeepXiv CLI Wrapper - 封装 DeepXiv SDK 的常用功能
支持论文搜索、渐进式阅读、热点追踪、深度调研
"""

import argparse
import json
import os
import sys
from typing import Optional, List, Dict, Any


def check_installation():
    """检查 deepxiv-sdk 是否已安装"""
    try:
        import deepxiv
        return True
    except ImportError:
        print("❌ deepxiv-sdk 未安装")
        print("请运行: pip install deepxiv-sdk")
        print("或安装完整版: pip install \"deepxiv-sdk[all]\"")
        return False


def search_papers(query: str, limit: int = 20, date_from: Optional[str] = None, 
                  format: str = "text") -> List[Dict[str, Any]]:
    """
    搜索 ArXiv 论文
    
    Args:
        query: 搜索关键词
        limit: 返回数量限制
        date_from: 起始日期 (YYYY-MM-DD)
        format: 输出格式 (text/json)
    
    Returns:
        论文列表
    """
    if not check_installation():
        return []
    
    try:
        from deepxiv import DeepXiv
        
        client = DeepXiv()
        
        # 构建搜索参数
        params = {
            "query": query,
            "limit": limit
        }
        if date_from:
            params["date_from"] = date_from
        
        results = client.search(**params)
        
        if format == "json":
            return results
        else:
            # 文本格式输出
            for i, paper in enumerate(results, 1):
                print(f"\n[{i}] {paper.get('title', 'N/A')}")
                print(f"    arXiv: {paper.get('arxiv_id', 'N/A')}")
                print(f"    日期: {paper.get('published_date', 'N/A')}")
                if paper.get('tl_dr'):
                    print(f"    TL;DR: {paper['tl_dr']}")
            return results
            
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        return []


def get_paper_brief(arxiv_id: str) -> Optional[Dict[str, Any]]:
    """
    快速预览论文核心信息（低 token 消耗）
    
    Args:
        arxiv_id: ArXiv 论文 ID
    
    Returns:
        论文简要信息
    """
    if not check_installation():
        return None
    
    try:
        from deepxiv import DeepXiv
        
        client = DeepXiv()
        brief = client.brief(arxiv_id)
        
        print(f"\n📄 {brief.get('title', 'N/A')}")
        print(f"   arXiv: {arxiv_id}")
        print(f"   日期: {brief.get('published_date', 'N/A')}")
        print(f"   作者: {', '.join(brief.get('authors', []))}")
        if brief.get('tl_dr'):
            print(f"\n   TL;DR: {brief['tl_dr']}")
        if brief.get('keywords'):
            print(f"   关键词: {', '.join(brief['keywords'])}")
        if brief.get('github_url'):
            print(f"   GitHub: {brief['github_url']}")
        print(f"   Token 预算: ~{brief.get('token_count', 'N/A')} tokens")
        
        return brief
        
    except Exception as e:
        print(f"❌ 获取论文预览失败: {e}")
        return None


def get_paper_head(arxiv_id: str) -> Optional[Dict[str, Any]]:
    """
    查看论文结构与章节分布
    
    Args:
        arxiv_id: ArXiv 论文 ID
    
    Returns:
        论文结构信息
    """
    if not check_installation():
        return None
    
    try:
        from deepxiv import DeepXiv
        
        client = DeepXiv()
        head = client.head(arxiv_id)
        
        print(f"\n📑 {head.get('title', 'N/A')}")
        print(f"   总 Token: {head.get('total_tokens', 'N/A')}")
        print(f"\n   章节结构:")
        
        sections = head.get('sections', [])
        for section in sections:
            name = section.get('name', 'Unknown')
            tokens = section.get('token_count', 'N/A')
            print(f"   - {name} (~{tokens} tokens)")
        
        return head
        
    except Exception as e:
        print(f"❌ 获取论文结构失败: {e}")
        return None


def get_paper_section(arxiv_id: str, section: str) -> Optional[str]:
    """
    精读特定章节
    
    Args:
        arxiv_id: ArXiv 论文 ID
        section: 章节名称
    
    Returns:
        章节内容
    """
    if not check_installation():
        return None
    
    try:
        from deepxiv import DeepXiv
        
        client = DeepXiv()
        content = client.section(arxiv_id, section)
        
        print(f"\n📖 [{section}]")
        print("-" * 60)
        print(content)
        print("-" * 60)
        
        return content
        
    except Exception as e:
        print(f"❌ 获取章节失败: {e}")
        return None


def get_trending(days: int = 7, limit: int = 30) -> List[Dict[str, Any]]:
    """
    获取热点论文
    
    Args:
        days: 时间范围（天）
        limit: 返回数量
    
    Returns:
        热点论文列表
    """
    if not check_installation():
        return []
    
    try:
        from deepxiv import DeepXiv
        
        client = DeepXiv()
        results = client.trending(days=days, limit=limit)
        
        print(f"\n🔥 近 {days} 天热点论文:")
        for i, paper in enumerate(results, 1):
            print(f"\n[{i}] {paper.get('title', 'N/A')}")
            print(f"    arXiv: {paper.get('arxiv_id', 'N/A')}")
            if paper.get('popularity'):
                print(f"    热度: {paper['popularity']}")
        
        return results
        
    except Exception as e:
        print(f"❌ 获取热点失败: {e}")
        return []


def deep_research(query: str, verbose: bool = False) -> str:
    """
    深度调研 Agent
    
    Args:
        query: 研究问题
        verbose: 是否显示详细过程
    
    Returns:
        调研结果
    """
    if not check_installation():
        return ""
    
    try:
        # 检查是否安装了完整版
        try:
            from deepxiv import agent
        except ImportError:
            print("❌ Agent 功能需要安装完整版")
            print("请运行: pip install \"deepxiv-sdk[all]\"")
            return ""
        
        print(f"\n🔍 开始深度调研: {query}")
        print("-" * 60)
        
        # 创建 agent 并查询
        research_agent = agent(verbose=verbose)
        result = research_agent.query(query)
        
        print(result)
        print("-" * 60)
        
        return result
        
    except Exception as e:
        print(f"❌ 深度调研失败: {e}")
        return ""


def main():
    parser = argparse.ArgumentParser(
        description="DeepXiv - 科技文献智能体接口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 搜索论文
  %(prog)s search "agent memory" --limit 20
  
  # 快速预览
  %(prog)s brief 2602.16493
  
  # 查看结构
  %(prog)s head 2602.16493
  
  # 精读章节
  %(prog)s section 2602.16493 "Experiments"
  
  # 热点追踪
  %(prog)s trending --days 7
  
  # 深度调研
  %(prog)s research "What are the latest papers about agent memory?"
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # search 命令
    search_parser = subparsers.add_parser("search", help="搜索论文")
    search_parser.add_argument("query", help="搜索关键词")
    search_parser.add_argument("--limit", type=int, default=20, help="返回数量")
    search_parser.add_argument("--date-from", help="起始日期 (YYYY-MM-DD)")
    search_parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    
    # brief 命令
    brief_parser = subparsers.add_parser("brief", help="快速预览论文")
    brief_parser.add_argument("arxiv_id", help="ArXiv 论文 ID")
    
    # head 命令
    head_parser = subparsers.add_parser("head", help="查看论文结构")
    head_parser.add_argument("arxiv_id", help="ArXiv 论文 ID")
    
    # section 命令
    section_parser = subparsers.add_parser("section", help="精读特定章节")
    section_parser.add_argument("arxiv_id", help="ArXiv 论文 ID")
    section_parser.add_argument("section_name", help="章节名称")
    
    # trending 命令
    trending_parser = subparsers.add_parser("trending", help="获取热点论文")
    trending_parser.add_argument("--days", type=int, default=7, help="时间范围（天）")
    trending_parser.add_argument("--limit", type=int, default=30, help="返回数量")
    
    # research 命令
    research_parser = subparsers.add_parser("research", help="深度调研")
    research_parser.add_argument("query", help="研究问题")
    research_parser.add_argument("--verbose", action="store_true", help="显示详细过程")
    
    args = parser.parse_args()
    
    if args.command == "search":
        search_papers(args.query, args.limit, args.date_from, 
                     "json" if args.json else "text")
    
    elif args.command == "brief":
        get_paper_brief(args.arxiv_id)
    
    elif args.command == "head":
        get_paper_head(args.arxiv_id)
    
    elif args.command == "section":
        get_paper_section(args.arxiv_id, args.section_name)
    
    elif args.command == "trending":
        get_trending(args.days, args.limit)
    
    elif args.command == "research":
        deep_research(args.query, args.verbose)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
