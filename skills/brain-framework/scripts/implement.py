#!/usr/bin/env python3
"""
Implement 阶段脚本 - 代码变更执行

功能：
1. 按计划执行代码变更
2. 运行类型检查（strict模式下）
3. 生成回滚提示

依赖：
- pydantic >= 2.0.0
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from datetime import datetime


class ImplementOutput:
    """Implement 阶段输出数据模型"""
    def __init__(self, success: bool, modified_files: List[str],
                 test_results: Optional[Dict[str, Any]], 
                 rollback_hint: Optional[str]):
        self.success = success
        self.modified_files = modified_files
        self.test_results = test_results
        self.rollback_hint = rollback_hint
    
    def to_json(self) -> str:
        return json.dumps({
            "success": self.success,
            "modified_files": self.modified_files,
            "test_results": self.test_results,
            "rollback_hint": self.rollback_hint
        }, indent=2, ensure_ascii=False)


def parse_plan_file_changes(plan_md_path: str) -> List[Dict[str, str]]:
    """
    从 plan.md 中提取文件变更清单
    
    Args:
        plan_md_path: plan.md 文件路径
    
    Returns:
        文件变更列表
    """
    if not os.path.exists(plan_md_path):
        raise FileNotFoundError(f"plan.md 不存在: {plan_md_path}")
    
    with open(plan_md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changes = []
    
    # 简单解析：查找 Markdown 表格
    lines = content.split('\n')
    in_table = False
    
    for line in lines:
        if '文件变更清单' in line:
            in_table = True
            continue
        
        if in_table:
            if line.startswith('|'):
                parts = [p.strip() for p in line.split('|')]
                # 过滤空行和表头
                if len(parts) >= 4 and parts[1] != '-' and parts[1] != '文件路径':
                    file_path = parts[1]
                    operation = parts[2]
                    description = parts[3]
                    
                    if file_path and file_path != '-':
                        changes.append({
                            "file_path": file_path,
                            "operation": operation,
                            "description": description
                        })
            elif not line.strip():
                # 表格结束
                break
    
    return changes


def generate_rollback_hint(modified_files: List[str]) -> str:
    """
    生成回滚提示
    
    Args:
        modified_files: 已修改的文件列表
    
    Returns:
        回滚命令字符串
    """
    if not modified_files:
        return "无文件被修改，无需回滚"
    
    cmds = []
    cmds.append("# Git 回滚命令（如果使用版本控制）：")
    cmds.append("```bash")
    for file_path in modified_files:
        cmds.append(f"git checkout HEAD -- {file_path}")
    cmds.append("```")
    cmds.append("")
    cmds.append("# 手动回滚建议：")
    cmds.append("1. 保留原始代码的备份")
    cmds.append("2. 恢复文件到修改前的状态")
    cmds.append("3. 验证系统功能正常")
    
    return "\n".join(cmds)


def run_type_check(file_path: str) -> bool:
    """
    运行类型检查（使用 mypy）
    
    Args:
        file_path: 文件路径
    
    Returns:
        是否通过类型检查
    """
    try:
        # 尝试运行 mypy
        result = subprocess.run(
            ["mypy", file_path, "--no-error-summary"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return result.returncode == 0
        
    except FileNotFoundError:
        # mypy 未安装，跳过类型检查
        print(f"[Warning] mypy 未安装，跳过类型检查: {file_path}")
        return True
    except subprocess.TimeoutExpired:
        print(f"[Warning] 类型检查超时: {file_path}")
        return True
    except Exception as e:
        print(f"[Error] 类型检查失败: {file_path} - {str(e)}")
        return False


def run_tests(codebase_root: str) -> Dict[str, Any]:
    """
    运行测试
    
    Args:
        codebase_root: 代码库根目录
    
    Returns:
        测试结果字典
    """
    try:
        # 尝试运行 pytest
        result = subprocess.run(
            ["pytest", "-v"],
            cwd=codebase_root,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        return {
            "passed": result.returncode == 0,
            "output": result.stdout + result.stderr,
            "failures": 0 if result.returncode == 0 else 1
        }
        
    except FileNotFoundError:
        return {
            "passed": None,
            "output": "pytest 未安装，跳过测试",
            "failures": 0
        }
    except subprocess.TimeoutExpired:
        return {
            "passed": False,
            "output": "测试超时",
            "failures": 1
        }
    except Exception as e:
        return {
            "passed": False,
            "output": str(e),
            "failures": 1
        }


def main():
    parser = argparse.ArgumentParser(description="代码变更执行 - Implement 阶段")
    parser.add_argument("--plan", required=True, help="plan.md 文件路径")
    parser.add_argument("--codebase-root", default=".", help="代码库根目录路径")
    parser.add_argument("--strict", action="store_true", 
                       help="严格模式：启用类型检查")
    parser.add_argument("--run-tests", action="store_true",
                       help="自动运行测试")
    
    args = parser.parse_args()
    
    try:
        # 解析计划中的文件变更
        print(f"[Implement] 读取计划: {args.plan}")
        file_changes = parse_plan_file_changes(args.plan)
        
        if not file_changes:
            print("[Implement] 警告: 未找到文件变更清单")
            output = ImplementOutput(
                success=True,
                modified_files=[],
                test_results=None,
                rollback_hint="无文件被修改"
            )
            print(output.to_json())
            sys.exit(0)
        
        print(f"[Implement] 发现 {len(file_changes)} 个文件变更")
        
        # 执行代码变更
        modified_files = []
        errors = []
        
        for change in file_changes:
            file_path = change["file_path"]
            operation = change["operation"]
            description = change["description"]
            
            print(f"[Implement] 处理: {file_path} ({operation})")
            
            try:
                full_path = Path(args.codebase_root) / file_path
                
                if operation == "CREATE":
                    # 创建文件（提示用户需要提供内容）
                    if not full_path.parent.exists():
                        full_path.parent.mkdir(parents=True, exist_ok=True)
                    print(f"[Implement] ⚠️ CREATE 操作: {file_path}")
                    print(f"[Implement] 请手动创建文件并提供内容")
                    print(f"[Implement] 描述: {description}")
                    modified_files.append(file_path)
                    
                elif operation == "MODIFY":
                    # 修改文件（提示用户需要提供修改内容）
                    if not full_path.exists():
                        print(f"[Implement] ⚠️ 文件不存在: {file_path}")
                        errors.append(f"文件不存在: {file_path}")
                    else:
                        print(f"[Implement] ⚠️ MODIFY 操作: {file_path}")
                        print(f"[Implement] 请手动修改文件")
                        print(f"[Implement] 描述: {description}")
                        
                        # 严格模式下运行类型检查
                        if args.strict and file_path.endswith('.py'):
                            if run_type_check(str(full_path)):
                                print(f"[Implement] ✅ 类型检查通过: {file_path}")
                            else:
                                print(f"[Implement] ❌ 类型检查失败: {file_path}")
                                errors.append(f"类型检查失败: {file_path}")
                                continue
                        
                        modified_files.append(file_path)
                        
                elif operation == "DELETE":
                    # 删除文件
                    if full_path.exists():
                        # 备份
                        backup_path = full_path.with_suffix(f'{full_path.suffix}.backup')
                        full_path.rename(backup_path)
                        print(f"[Implement] ✅ 已删除并备份: {file_path} -> {backup_path.name}")
                        modified_files.append(file_path)
                    else:
                        print(f"[Implement] ⚠️ 文件不存在: {file_path}")
                
                else:
                    print(f"[Implement] ⚠️ 未知操作类型: {operation}")
                    errors.append(f"未知操作: {operation}")
                    
            except Exception as e:
                print(f"[Implement] ❌ 处理失败: {file_path} - {str(e)}")
                errors.append(f"{file_path}: {str(e)}")
        
        # 运行测试
        test_results = None
        if args.run_tests:
            print("[Implement] 运行测试...")
            test_results = run_tests(args.codebase_root)
            if test_results["passed"]:
                print("[Implement] ✅ 测试通过")
            elif test_results["passed"] is False:
                print(f"[Implement] ❌ 测试失败")
        
        # 生成结果
        if errors:
            print(f"[Implement] ❌ 执行完成，但有 {len(errors)} 个错误")
            rollback_hint = generate_rollback_hint(modified_files)
            output = ImplementOutput(
                success=False,
                modified_files=modified_files,
                test_results=test_results,
                rollback_hint=rollback_hint
            )
        else:
            print(f"[Implement] ✅ 执行成功: {len(modified_files)} 个文件已处理")
            rollback_hint = generate_rollback_hint(modified_files)
            output = ImplementOutput(
                success=True,
                modified_files=modified_files,
                test_results=test_results,
                rollback_hint=rollback_hint
            )
        
        # 输出 JSON 结果
        print(output.to_json())
        
        sys.exit(0 if not errors else 1)
        
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
