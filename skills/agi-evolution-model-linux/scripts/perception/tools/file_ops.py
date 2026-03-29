# -*- coding: utf-8 -*-
"""
文件操作工具集 - read, write, list, search, delete, move, copy, mkdir, stat

整合方案A优点：
- 多路径查找
- 编码自动降级
- 安全检查
"""

import os
import shutil
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from ..tools.base import ToolBase, ParamValidator, SecurityChecker
from ..context import RuntimeContext
from ..response import ToolResult, ErrorCode
from ..registry import tool


# ========== 辅助函数 ==========

def resolve_path(path: str, workspace: str = ".") -> Tuple[str, bool]:
    """
    多路径查找
    
    整合方案A优点：尝试多个可能的路径
    
    Returns:
        (解析后的路径, 是否找到)
    """
    # 可能的路径列表
    possible_paths = [
        path,  # 直接路径
        os.path.join(workspace, path),  # 工作区相对路径
        os.path.join("assets", path),  # assets 目录
        os.path.join("/tmp", path),  # tmp 目录
    ]
    
    for p in possible_paths:
        if os.path.exists(p):
            return os.path.abspath(p), True
    
    # 都没找到，返回工作区路径
    return os.path.abspath(os.path.join(workspace, path)), False


def read_file_with_encoding(path: str, encoding: str = "utf-8") -> Tuple[bool, str, str]:
    """
    读取文件（支持编码自动降级）
    
    整合方案A优点：UTF-8 → GBK 自动降级
    
    Returns:
        (是否成功, 内容, 实际使用的编码)
    """
    encodings = [encoding, "utf-8", "gbk", "latin-1"]
    tried = set()
    
    for enc in encodings:
        if enc in tried:
            continue
        tried.add(enc)
        
        try:
            with open(path, 'r', encoding=enc) as f:
                content = f.read()
            return True, content, enc
        except UnicodeDecodeError:
            continue
        except Exception as e:
            return False, str(e), enc
    
    return False, "无法识别文件编码", "unknown"


# ========== 文件操作工具 ==========

@tool
class FileReadTool(ToolBase):
    """文件读取工具"""
    
    name = "file_read"
    description = "读取文件内容，支持指定行范围和编码"
    version = "2.0.0"
    
    cacheable = True
    cache_ttl = 60
    
    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        return ParamValidator.require(params, "path")
    
    def execute(self, params: Dict[str, Any], ctx: RuntimeContext) -> ToolResult:
        path = params.get("path", "")
        encoding = params.get("encoding", "utf-8")
        start_line = params.get("start_line", 1)
        end_line = params.get("end_line", -1)
        
        # 多路径查找
        resolved_path, found = resolve_path(path, ctx.workspace_path)
        
        if not found:
            return self.error(
                ErrorCode.FILE_NOT_FOUND,
                f"文件不存在: {path}"
            )
        
        # 安全检查
        ok, msg = SecurityChecker.check_path(resolved_path, write=False)
        if not ok:
            return self.error(ErrorCode.SECURITY_VIOLATION, msg)
        
        # 读取文件
        success, content, used_encoding = read_file_with_encoding(resolved_path, encoding)
        
        if not success:
            return self.error(ErrorCode.EXECUTION_ERROR, content)
        
        # 处理行范围
        lines = content.split('\n')
        total_lines = len(lines)
        
        if end_line == -1:
            end_line = total_lines
        
        start_line = max(1, min(start_line, total_lines))
        end_line = max(start_line, min(end_line, total_lines))
        
        selected_lines = lines[start_line - 1:end_line]
        content = '\n'.join(selected_lines)
        
        return self.success(
            data={
                "content": content,
                "total_lines": total_lines,
                "read_lines": end_line - start_line + 1,
                "start_line": start_line,
                "end_line": end_line,
                "encoding": used_encoding
            }
        ).with_metadata(
            path=resolved_path,
            encoding=used_encoding,
            truncated=end_line < total_lines
        )


@tool
class FileWriteTool(ToolBase):
    """文件写入工具"""
    
    name = "file_write"
    description = "写入文件内容，支持覆盖和追加模式"
    version = "2.0.0"
    
    dangerous = True  # 标记为危险工具
    
    def security_check(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        path = params.get("path", "")
        return SecurityChecker.check_path(path, write=True)
    
    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        ok, msg = ParamValidator.require(params, "path", "content")
        if not ok:
            return ok, msg
        
        mode = params.get("mode", "write")
        if mode not in ["write", "append"]:
            return False, "mode 必须是 'write' 或 'append'"
        
        return True, ""
    
    def execute(self, params: Dict[str, Any], ctx: RuntimeContext) -> ToolResult:
        path = params.get("path", "")
        content = params.get("content", "")
        mode = params.get("mode", "write")
        encoding = params.get("encoding", "utf-8")
        
        # 解析路径
        resolved_path = os.path.abspath(os.path.join(ctx.workspace_path, path))
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
            
            # 写入文件
            write_mode = 'a' if mode == "append" else 'w'
            with open(resolved_path, write_mode, encoding=encoding) as f:
                f.write(content)
            
            bytes_written = len(content.encode(encoding))
            
            return self.success(
                data={
                    "bytes_written": bytes_written,
                    "mode": mode
                }
            ).with_metadata(
                path=resolved_path,
                mode=mode
            )
            
        except Exception as e:
            return self.error(ErrorCode.EXECUTION_ERROR, str(e))


@tool
class FileListTool(ToolBase):
    """目录列表工具"""
    
    name = "file_list"
    description = "列出目录内容，支持递归和显示隐藏文件"
    version = "2.0.0"
    
    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        return ParamValidator.require(params, "path")
    
    def execute(self, params: Dict[str, Any], ctx: RuntimeContext) -> ToolResult:
        path = params.get("path", ".")
        recursive = params.get("recursive", False)
        show_hidden = params.get("show_hidden", False)
        
        # 解析路径
        resolved_path, found = resolve_path(path, ctx.workspace_path)
        
        if not found:
            return self.error(
                ErrorCode.RESOURCE_NOT_FOUND,
                f"目录不存在: {path}"
            )
        
        if not os.path.isdir(resolved_path):
            return self.error(
                ErrorCode.EXECUTION_ERROR,
                f"不是目录: {path}"
            )
        
        try:
            items = []
            path_obj = Path(resolved_path)
            
            if recursive:
                iterator = path_obj.rglob('*')
            else:
                iterator = path_obj.iterdir()
            
            for item in iterator:
                # 过滤隐藏文件
                if not show_hidden and item.name.startswith('.'):
                    continue
                
                item_info = {
                    "name": item.name,
                    "path": str(item.relative_to(path_obj)),
                    "type": "dir" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else 0
                }
                items.append(item_info)
            
            return self.success(
                data={
                    "items": items,
                    "total": len(items),
                    "path": str(path_obj)
                }
            ).with_metadata(
                path=resolved_path,
                recursive=recursive
            )
            
        except Exception as e:
            return self.error(ErrorCode.EXECUTION_ERROR, str(e))


@tool
class FileSearchTool(ToolBase):
    """文件内容搜索工具"""
    
    name = "file_search"
    description = "在文件中搜索匹配的内容"
    version = "2.0.0"
    
    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        return ParamValidator.require(params, "path", "pattern")
    
    def execute(self, params: Dict[str, Any], ctx: RuntimeContext) -> ToolResult:
        path = params.get("path", ".")
        pattern = params.get("pattern", "")
        file_pattern = params.get("file_pattern", "*")
        
        # 解析路径
        resolved_path, found = resolve_path(path, ctx.workspace_path)
        
        if not found:
            return self.error(
                ErrorCode.RESOURCE_NOT_FOUND,
                f"路径不存在: {path}"
            )
        
        try:
            import fnmatch
            
            results = []
            path_obj = Path(resolved_path)
            
            for file_path in path_obj.rglob(file_pattern):
                if not file_path.is_file():
                    continue
                
                try:
                    success, content, _ = read_file_with_encoding(str(file_path))
                    if not success:
                        continue
                    
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if pattern.lower() in line.lower():
                            results.append({
                                "file": str(file_path.relative_to(path_obj)),
                                "line": i,
                                "content": line.strip()[:200]  # 截断长行
                            })
                            
                except Exception:
                    continue
            
            return self.success(
                data={
                    "matches": results,
                    "total": len(results),
                    "pattern": pattern
                }
            ).with_metadata(
                path=resolved_path,
                pattern=pattern
            )
            
        except Exception as e:
            return self.error(ErrorCode.EXECUTION_ERROR, str(e))


@tool
class FileDeleteTool(ToolBase):
    """文件删除工具"""
    
    name = "file_delete"
    description = "删除文件或目录"
    version = "2.0.0"
    
    dangerous = True
    
    def security_check(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        path = params.get("path", "")
        return SecurityChecker.check_path(path, write=True)
    
    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        return ParamValidator.require(params, "path")
    
    def execute(self, params: Dict[str, Any], ctx: RuntimeContext) -> ToolResult:
        path = params.get("path", "")
        recursive = params.get("recursive", False)
        
        # 解析路径
        resolved_path, found = resolve_path(path, ctx.workspace_path)
        
        if not found:
            return self.error(
                ErrorCode.FILE_NOT_FOUND,
                f"文件不存在: {path}"
            )
        
        try:
            if os.path.isfile(resolved_path):
                os.remove(resolved_path)
                deleted_type = "file"
            elif os.path.isdir(resolved_path):
                if not recursive and os.listdir(resolved_path):
                    return self.error(
                        ErrorCode.EXECUTION_ERROR,
                        "目录不为空，需要设置 recursive=True"
                    )
                shutil.rmtree(resolved_path)
                deleted_type = "directory"
            else:
                return self.error(
                    ErrorCode.EXECUTION_ERROR,
                    "未知文件类型"
                )
            
            return self.success(
                data={"deleted_type": deleted_type}
            ).with_metadata(
                path=resolved_path
            )
            
        except Exception as e:
            return self.error(ErrorCode.EXECUTION_ERROR, str(e))


@tool
class FileMoveTool(ToolBase):
    """文件移动工具"""
    
    name = "file_move"
    description = "移动文件或目录"
    version = "2.0.0"
    
    dangerous = True
    
    def security_check(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        dst = params.get("dst", "")
        return SecurityChecker.check_path(dst, write=True)
    
    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        return ParamValidator.require(params, "src", "dst")
    
    def execute(self, params: Dict[str, Any], ctx: RuntimeContext) -> ToolResult:
        src = params.get("src", "")
        dst = params.get("dst", "")
        
        # 解析路径
        src_path, found = resolve_path(src, ctx.workspace_path)
        if not found:
            return self.error(ErrorCode.FILE_NOT_FOUND, f"源文件不存在: {src}")
        
        dst_path = os.path.abspath(os.path.join(ctx.workspace_path, dst))
        
        try:
            shutil.move(src_path, dst_path)
            
            return self.success(
                data={"src": src, "dst": dst}
            ).with_metadata(
                src=src_path,
                dst=dst_path
            )
            
        except Exception as e:
            return self.error(ErrorCode.EXECUTION_ERROR, str(e))


@tool
class FileCopyTool(ToolBase):
    """文件复制工具"""
    
    name = "file_copy"
    description = "复制文件或目录"
    version = "2.0.0"
    
    dangerous = True
    
    def security_check(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        dst = params.get("dst", "")
        return SecurityChecker.check_path(dst, write=True)
    
    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        return ParamValidator.require(params, "src", "dst")
    
    def execute(self, params: Dict[str, Any], ctx: RuntimeContext) -> ToolResult:
        src = params.get("src", "")
        dst = params.get("dst", "")
        
        # 解析路径
        src_path, found = resolve_path(src, ctx.workspace_path)
        if not found:
            return self.error(ErrorCode.FILE_NOT_FOUND, f"源文件不存在: {src}")
        
        dst_path = os.path.abspath(os.path.join(ctx.workspace_path, dst))
        
        try:
            if os.path.isfile(src_path):
                shutil.copy2(src_path, dst_path)
            else:
                shutil.copytree(src_path, dst_path)
            
            return self.success(
                data={"src": src, "dst": dst}
            ).with_metadata(
                src=src_path,
                dst=dst_path
            )
            
        except Exception as e:
            return self.error(ErrorCode.EXECUTION_ERROR, str(e))


@tool
class FileMkdirTool(ToolBase):
    """创建目录工具"""
    
    name = "file_mkdir"
    description = "创建目录，支持创建多级目录"
    version = "2.0.0"
    
    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        return ParamValidator.require(params, "path")
    
    def execute(self, params: Dict[str, Any], ctx: RuntimeContext) -> ToolResult:
        path = params.get("path", "")
        parents = params.get("parents", True)
        
        # 解析路径
        resolved_path = os.path.abspath(os.path.join(ctx.workspace_path, path))
        
        try:
            if parents:
                os.makedirs(resolved_path, exist_ok=True)
            else:
                os.mkdir(resolved_path)
            
            return self.success(
                data={"created": True}
            ).with_metadata(
                path=resolved_path
            )
            
        except Exception as e:
            return self.error(ErrorCode.EXECUTION_ERROR, str(e))


@tool
class FileStatTool(ToolBase):
    """文件信息工具"""
    
    name = "file_stat"
    description = "获取文件或目录的详细信息"
    version = "2.0.0"
    
    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        return ParamValidator.require(params, "path")
    
    def execute(self, params: Dict[str, Any], ctx: RuntimeContext) -> ToolResult:
        path = params.get("path", "")
        
        # 解析路径
        resolved_path, found = resolve_path(path, ctx.workspace_path)
        
        if not found:
            return self.error(
                ErrorCode.FILE_NOT_FOUND,
                f"文件不存在: {path}"
            )
        
        try:
            stat = os.stat(resolved_path)
            path_obj = Path(resolved_path)
            
            data = {
                "path": resolved_path,
                "name": path_obj.name,
                "type": "directory" if path_obj.is_dir() else "file",
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "accessed": stat.st_atime,
                "mode": oct(stat.st_mode)[-3:],
                "is_readable": os.access(resolved_path, os.R_OK),
                "is_writable": os.access(resolved_path, os.W_OK),
                "is_executable": os.access(resolved_path, os.X_OK)
            }
            
            if path_obj.is_file():
                # 计算文件哈希
                try:
                    with open(resolved_path, 'rb') as f:
                        data["md5"] = hashlib.md5(f.read()).hexdigest()
                except Exception:
                    pass
            
            return self.success(data=data).with_metadata(
                path=resolved_path
            )
            
        except Exception as e:
            return self.error(ErrorCode.EXECUTION_ERROR, str(e))
