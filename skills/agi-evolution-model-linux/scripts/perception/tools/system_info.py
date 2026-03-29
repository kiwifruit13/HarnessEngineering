# -*- coding: utf-8 -*-
"""
系统信息工具集 - system, cpu, memory, disk, network, uptime, env

保留原有功能，整合新架构
"""

import os
import platform
import subprocess
from datetime import datetime
from typing import Dict, Any, Tuple

from ..tools.base import ToolBase
from ..context import RuntimeContext
from ..response import ToolResult, ErrorCode
from ..registry import tool


@tool
class SystemInfoTool(ToolBase):
    """系统基本信息工具"""
    
    name = "system_info"
    description = "获取系统基本信息（操作系统、架构、主机名等）"
    version = "2.0.0"
    
    cacheable = True
    cache_ttl = 60
    
    def execute(self, params: Dict[str, Any], ctx: RuntimeContext) -> ToolResult:
        data = {
            "system": platform.system(),
            "node": platform.node(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation()
        }
        
        return self.success(data=data)


@tool
class CpuInfoTool(ToolBase):
    """CPU 信息工具"""
    
    name = "cpu_info"
    description = "获取 CPU 信息和使用率"
    version = "2.0.0"
    
    def execute(self, params: Dict[str, Any], ctx: RuntimeContext) -> ToolResult:
        try:
            # 获取 CPU 核心数
            cpu_count = os.cpu_count() or 1
            
            # 获取 CPU 使用率
            if platform.system() == "Linux":
                try:
                    result = subprocess.run(
                        ["top", "-bn1"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    # 解析 CPU 使用率
                    lines = result.stdout.split('\n')
                    cpu_usage = 0.0
                    for line in lines:
                        if "%Cpu" in line or "Cpu(s)" in line:
                            parts = line.split()
                            for i, p in enumerate(parts):
                                if "%" in p and i > 0:
                                    try:
                                        cpu_usage = 100 - float(p.replace('%', ''))
                                        break
                                    except ValueError:
                                        continue
                except Exception:
                    cpu_usage = 0.0
            else:
                cpu_usage = 0.0
            
            data = {
                "count": cpu_count,
                "usage_percent": round(cpu_usage, 2),
                "architecture": platform.machine()
            }
            
            return self.success(data=data)
            
        except Exception as e:
            return self.error(ErrorCode.EXECUTION_ERROR, str(e))


@tool
class MemoryInfoTool(ToolBase):
    """内存信息工具"""
    
    name = "memory_info"
    description = "获取内存使用情况"
    version = "2.0.0"
    
    def execute(self, params: Dict[str, Any], ctx: RuntimeContext) -> ToolResult:
        try:
            if platform.system() == "Linux":
                # 读取 /proc/meminfo
                meminfo = {}
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        parts = line.split()
                        if len(parts) >= 2:
                            key = parts[0].rstrip(':')
                            value = int(parts[1])
                            meminfo[key] = value
                
                total = meminfo.get('MemTotal', 0)
                free = meminfo.get('MemFree', 0)
                available = meminfo.get('MemAvailable', free)
                used = total - available
                
                data = {
                    "total_mb": total // 1024,
                    "used_mb": used // 1024,
                    "free_mb": free // 1024,
                    "available_mb": available // 1024,
                    "usage_percent": round(used / total * 100, 2) if total > 0 else 0
                }
            else:
                # 其他系统返回基本信息
                data = {
                    "message": "内存信息仅在 Linux 系统上可用"
                }
            
            return self.success(data=data)
            
        except Exception as e:
            return self.error(ErrorCode.EXECUTION_ERROR, str(e))


@tool
class DiskInfoTool(ToolBase):
    """磁盘信息工具"""
    
    name = "disk_info"
    description = "获取磁盘使用情况"
    version = "2.0.0"
    
    def execute(self, params: Dict[str, Any], ctx: RuntimeContext) -> ToolResult:
        path = params.get("path", "/")
        
        try:
            stat = os.statvfs(path)
            
            total = stat.f_blocks * stat.f_frsize
            free = stat.f_bavail * stat.f_frsize
            used = total - free
            
            data = {
                "path": path,
                "total_gb": round(total / (1024**3), 2),
                "used_gb": round(used / (1024**3), 2),
                "free_gb": round(free / (1024**3), 2),
                "usage_percent": round(used / total * 100, 2) if total > 0 else 0
            }
            
            return self.success(data=data)
            
        except Exception as e:
            return self.error(ErrorCode.EXECUTION_ERROR, str(e))


@tool
class NetworkInfoTool(ToolBase):
    """网络接口信息工具"""
    
    name = "network_info"
    description = "获取网络接口信息"
    version = "2.0.0"
    
    def execute(self, params: Dict[str, Any], ctx: RuntimeContext) -> ToolResult:
        try:
            import socket
            
            hostname = socket.gethostname()
            
            # 获取所有网络接口
            interfaces = []
            
            if platform.system() == "Linux":
                try:
                    result = subprocess.run(
                        ["ip", "addr"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    current_interface = None
                    for line in result.stdout.split('\n'):
                        if line.strip() and not line.startswith(' '):
                            parts = line.split(':')
                            if len(parts) >= 2:
                                current_interface = {
                                    "name": parts[1].strip().split('@')[0],
                                    "addresses": []
                                }
                                interfaces.append(current_interface)
                        elif current_interface and "inet " in line:
                            addr = line.strip().split()[1].split('/')[0]
                            current_interface["addresses"].append(addr)
                except Exception:
                    pass
            
            # 获取本机 IP
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
            except Exception:
                local_ip = "127.0.0.1"
            
            data = {
                "hostname": hostname,
                "local_ip": local_ip,
                "interfaces": interfaces
            }
            
            return self.success(data=data)
            
        except Exception as e:
            return self.error(ErrorCode.EXECUTION_ERROR, str(e))


@tool
class UptimeInfoTool(ToolBase):
    """系统运行时间工具"""
    
    name = "uptime_info"
    description = "获取系统运行时间"
    version = "2.0.0"
    
    def execute(self, params: Dict[str, Any], ctx: RuntimeContext) -> ToolResult:
        try:
            if platform.system() == "Linux":
                with open('/proc/uptime', 'r') as f:
                    uptime_seconds = float(f.read().split()[0])
                
                days = int(uptime_seconds // 86400)
                hours = int((uptime_seconds % 86400) // 3600)
                minutes = int((uptime_seconds % 3600) // 60)
                seconds = int(uptime_seconds % 60)
                
                data = {
                    "uptime_seconds": int(uptime_seconds),
                    "days": days,
                    "hours": hours,
                    "minutes": minutes,
                    "seconds": seconds,
                    "formatted": f"{days}d {hours}h {minutes}m {seconds}s"
                }
            else:
                data = {
                    "message": "运行时间信息仅在 Linux 系统上可用"
                }
            
            return self.success(data=data)
            
        except Exception as e:
            return self.error(ErrorCode.EXECUTION_ERROR, str(e))


@tool
class EnvInfoTool(ToolBase):
    """环境变量工具"""
    
    name = "env_info"
    description = "获取环境变量（敏感信息已过滤）"
    version = "2.0.0"
    
    # 敏感环境变量前缀
    SENSITIVE_PREFIXES = [
        'PASSWORD', 'SECRET', 'KEY', 'TOKEN', 'API_KEY',
        'PRIVATE', 'CREDENTIAL', 'AUTH'
    ]
    
    def execute(self, params: Dict[str, Any], ctx: RuntimeContext) -> ToolResult:
        try:
            env_vars = {}
            
            for key, value in os.environ.items():
                # 过滤敏感信息
                is_sensitive = any(
                    prefix in key.upper() 
                    for prefix in self.SENSITIVE_PREFIXES
                )
                
                if is_sensitive:
                    env_vars[key] = "***FILTERED***"
                else:
                    env_vars[key] = value
            
            return self.success(
                data={
                    "variables": env_vars,
                    "count": len(env_vars)
                }
            )
            
        except Exception as e:
            return self.error(ErrorCode.EXECUTION_ERROR, str(e))
