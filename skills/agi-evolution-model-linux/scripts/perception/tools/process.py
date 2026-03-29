# -*- coding: utf-8 -*-
"""
进程管理工具集 - list, info, tree, kill

保留原有功能，整合新架构
"""

import os
import signal
import platform
import subprocess
from typing import Dict, Any, List, Tuple, Optional

from ..tools.base import ToolBase, ParamValidator, SecurityChecker
from ..context import RuntimeContext
from ..response import ToolResult, ErrorCode
from ..registry import tool


@tool
class ProcessListTool(ToolBase):
    """进程列表工具"""
    
    name = "process_list"
    description = "获取进程列表，支持按用户和名称过滤"
    version = "2.0.0"
    
    def execute(self, params: Dict[str, Any], ctx: RuntimeContext) -> ToolResult:
        user_only = params.get("user_only", False)
        name_filter = params.get("name_filter", None)
        
        try:
            processes = []
            system = platform.system()
            
            if system in ["Linux", "Darwin"]:
                # 使用 ps 命令获取进程列表
                result = subprocess.run(
                    ['ps', 'aux'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    lines = result.stdout.split('\n')[1:]  # 跳过标题行
                    
                    for line in lines:
                        if not line.strip():
                            continue
                        
                        parts = line.split(None, 10)
                        if len(parts) < 11:
                            continue
                        
                        username = parts[0]
                        pid = int(parts[1])
                        cpu = float(parts[2])
                        mem = float(parts[3])
                        command = parts[10]
                        
                        # 过滤条件
                        if user_only:
                            try:
                                current_user = os.getlogin()
                                if username != current_user:
                                    continue
                            except Exception:
                                pass
                        
                        if name_filter and name_filter.lower() not in command.lower():
                            continue
                        
                        processes.append({
                            "pid": pid,
                            "user": username,
                            "cpu_percent": cpu,
                            "memory_percent": mem,
                            "command": command[:100]  # 截断长命令
                        })
            
            elif system == "Windows":
                # 使用 tasklist 命令
                result = subprocess.run(
                    ['tasklist', '/fo', 'csv'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    import csv
                    lines = result.stdout.split('\n')[1:]
                    
                    for line in lines:
                        if not line.strip():
                            continue
                        
                        try:
                            reader = csv.reader([line])
                            for row in reader:
                                if len(row) >= 5:
                                    name = row[0].strip('"')
                                    pid = int(row[1].strip('"'))
                                    mem = row[4].strip('"')
                                    
                                    if name_filter and name_filter.lower() not in name.lower():
                                        continue
                                    
                                    processes.append({
                                        "pid": pid,
                                        "name": name,
                                        "memory": mem,
                                        "command": name
                                    })
                        except Exception:
                            continue
            
            return self.success(
                data={
                    "processes": processes,
                    "count": len(processes),
                    "filter": {
                        "user_only": user_only,
                        "name_filter": name_filter
                    }
                }
            )
            
        except Exception as e:
            return self.error(ErrorCode.EXECUTION_ERROR, str(e))


@tool
class ProcessInfoTool(ToolBase):
    """进程详情工具"""
    
    name = "process_info"
    description = "获取指定进程的详细信息"
    version = "2.0.0"
    
    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        return ParamValidator.require(params, "pid")
    
    def execute(self, params: Dict[str, Any], ctx: RuntimeContext) -> ToolResult:
        pid = params.get("pid")
        
        try:
            pid = int(pid)
        except (ValueError, TypeError):
            return self.error(ErrorCode.INVALID_PARAMS, "pid 必须是整数")
        
        try:
            system = platform.system()
            
            if system in ["Linux", "Darwin"]:
                # 读取 /proc/[pid]/stat
                proc_path = f"/proc/{pid}"
                
                if not os.path.exists(proc_path):
                    return self.error(
                        ErrorCode.RESOURCE_NOT_FOUND,
                        f"进程不存在: PID {pid}"
                    )
                
                # 读取状态
                with open(f"{proc_path}/stat", 'r') as f:
                    stat = f.read().split()
                
                # 读取命令行
                try:
                    with open(f"{proc_path}/cmdline", 'r') as f:
                        cmdline = f.read().replace('\x00', ' ').strip()
                except Exception:
                    cmdline = ""
                
                # 解析状态
                data = {
                    "pid": pid,
                    "state": stat[2],
                    "ppid": int(stat[3]),
                    "command": cmdline[:200] if cmdline else stat[1].strip('()'),
                    "threads": int(stat[19]),
                    "utime": float(stat[13]) / 100,  # 用户态时间（秒）
                    "stime": float(stat[14]) / 100,  # 内核态时间（秒）
                }
                
            else:
                data = {
                    "pid": pid,
                    "message": "进程详情仅在 Linux/macOS 系统上可用"
                }
            
            return self.success(data=data)
            
        except FileNotFoundError:
            return self.error(
                ErrorCode.RESOURCE_NOT_FOUND,
                f"进程不存在: PID {pid}"
            )
        except Exception as e:
            return self.error(ErrorCode.EXECUTION_ERROR, str(e))


@tool
class ProcessTreeTool(ToolBase):
    """进程树工具"""
    
    name = "process_tree"
    description = "获取进程树（父子关系）"
    version = "2.0.0"
    
    def execute(self, params: Dict[str, Any], ctx: RuntimeContext) -> ToolResult:
        root_pid = params.get("root_pid", None)
        
        try:
            if platform.system() not in ["Linux", "Darwin"]:
                return self.error(
                    ErrorCode.EXECUTION_ERROR,
                    "进程树仅在 Linux/macOS 系统上可用"
                )
            
            # 获取所有进程
            result = subprocess.run(
                ['ps', '-ef'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return self.error(ErrorCode.EXECUTION_ERROR, "获取进程列表失败")
            
            # 构建进程树
            processes = {}
            lines = result.stdout.split('\n')[1:]
            
            for line in lines:
                if not line.strip():
                    continue
                
                parts = line.split(None, 7)
                if len(parts) < 8:
                    continue
                
                try:
                    pid = int(parts[1])
                    ppid = int(parts[2])
                    command = parts[7][:50]
                    
                    processes[pid] = {
                        "pid": pid,
                        "ppid": ppid,
                        "command": command,
                        "children": []
                    }
                except (ValueError, IndexError):
                    continue
            
            # 构建父子关系
            tree = []
            for pid, proc in processes.items():
                ppid = proc["ppid"]
                if ppid in processes:
                    processes[ppid]["children"].append(proc)
                elif root_pid is None or pid == root_pid:
                    tree.append(proc)
            
            # 如果指定了根进程
            if root_pid is not None:
                root_pid = int(root_pid)
                if root_pid in processes:
                    tree = [processes[root_pid]]
                else:
                    return self.error(
                        ErrorCode.RESOURCE_NOT_FOUND,
                        f"进程不存在: PID {root_pid}"
                    )
            
            return self.success(
                data={
                    "tree": tree,
                    "total_processes": len(processes)
                }
            )
            
        except Exception as e:
            return self.error(ErrorCode.EXECUTION_ERROR, str(e))


@tool
class ProcessKillTool(ToolBase):
    """终止进程工具"""
    
    name = "process_kill"
    description = "终止指定进程"
    version = "2.0.0"
    
    dangerous = True
    
    # 保护进程列表（不允许终止）
    PROTECTED_PROCESSES = [
        "init", "systemd", "kernel", "kthreadd"
    ]
    
    def security_check(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        pid = params.get("pid")
        
        # 不允许终止 PID 1
        if pid == 1:
            return False, "不允许终止 PID 1 进程"
        
        # 不允许终止当前进程
        if pid == os.getpid():
            return False, "不允许终止当前进程"
        
        return True, ""
    
    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        return ParamValidator.require(params, "pid")
    
    def execute(self, params: Dict[str, Any], ctx: RuntimeContext) -> ToolResult:
        pid = params.get("pid")
        signal_name = params.get("signal", "TERM")
        
        try:
            pid = int(pid)
        except (ValueError, TypeError):
            return self.error(ErrorCode.INVALID_PARAMS, "pid 必须是整数")
        
        # 解析信号
        signal_map = {
            "TERM": signal.SIGTERM,
            "KILL": signal.SIGKILL,
            "INT": signal.SIGINT,
            "HUP": signal.SIGHUP
        }
        
        sig = signal_map.get(signal_name.upper(), signal.SIGTERM)
        
        try:
            # 检查进程是否存在
            try:
                os.kill(pid, 0)  # 发送信号0检查进程是否存在
            except OSError:
                return self.error(
                    ErrorCode.RESOURCE_NOT_FOUND,
                    f"进程不存在: PID {pid}"
                )
            
            # 终止进程
            os.kill(pid, sig)
            
            return self.success(
                data={
                    "pid": pid,
                    "signal": signal_name,
                    "action": "terminated"
                }
            ).with_metadata(
                pid=pid,
                signal=signal_name
            )
            
        except PermissionError:
            return self.error(
                ErrorCode.PERMISSION_DENIED,
                f"没有权限终止进程: PID {pid}"
            )
        except Exception as e:
            return self.error(ErrorCode.EXECUTION_ERROR, str(e))
