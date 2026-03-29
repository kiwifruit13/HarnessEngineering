# -*- coding: utf-8 -*-
"""
命令执行工具 - bash_execute

整合方案A优点：
- 危险命令拦截
- 超时控制
- 安全的工作目录
"""

import os
import subprocess
import shlex
from typing import Dict, Any, Tuple

from ..tools.base import ToolBase, ParamValidator, SecurityChecker
from ..context import RuntimeContext
from ..response import ToolResult, ErrorCode
from ..registry import tool


@tool
class BashExecuteTool(ToolBase):
    """Shell 命令执行工具"""
    
    name = "bash_execute"
    description = "执行 Shell 命令，支持超时控制和安全检查"
    version = "2.0.0"
    
    dangerous = True
    
    # 默认超时时间（秒）
    DEFAULT_TIMEOUT = 30
    MAX_TIMEOUT = 300
    
    def security_check(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        command = params.get("command", "")
        return SecurityChecker.check_command(command)
    
    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        ok, msg = ParamValidator.require(params, "command")
        if not ok:
            return ok, msg
        
        # 检查超时范围
        timeout = params.get("timeout", self.DEFAULT_TIMEOUT)
        if isinstance(timeout, int) and (timeout < 1 or timeout > self.MAX_TIMEOUT):
            return False, f"超时时间必须在 1-{self.MAX_TIMEOUT} 秒之间"
        
        return True, ""
    
    def execute(self, params: Dict[str, Any], ctx: RuntimeContext) -> ToolResult:
        command = params.get("command", "")
        timeout = params.get("timeout", self.DEFAULT_TIMEOUT)
        cwd = params.get("cwd", None)
        
        # 确定工作目录
        if cwd:
            work_dir = os.path.abspath(os.path.join(ctx.workspace_path, cwd))
            if not os.path.exists(work_dir):
                return self.error(
                    ErrorCode.RESOURCE_NOT_FOUND,
                    f"工作目录不存在: {cwd}"
                )
        else:
            work_dir = ctx.workspace_path
        
        try:
            # 执行命令
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=work_dir
            )
            
            # 构建返回数据
            data = {
                "command": command,
                "return_code": result.returncode,
                "stdout": result.stdout[:10000] if result.stdout else "",  # 截断长输出
                "stderr": result.stderr[:5000] if result.stderr else "",
                "success": result.returncode == 0,
                "timeout": timeout,
                "cwd": work_dir
            }
            
            # 添加输出摘要
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                data["stdout_lines"] = len(lines)
            
            return self.success(data=data).with_metadata(
                command=command[:100],
                return_code=result.returncode,
                cwd=work_dir
            )
            
        except subprocess.TimeoutExpired:
            return self.error(
                ErrorCode.TIMEOUT,
                f"命令执行超时（超过 {timeout} 秒）"
            ).with_metadata(
                command=command[:100],
                timeout=timeout
            )
            
        except Exception as e:
            return self.error(
                ErrorCode.EXECUTION_ERROR,
                f"命令执行失败: {str(e)}"
            ).with_metadata(
                command=command[:100]
            )


# 别名，保持向后兼容
BashTool = BashExecuteTool
