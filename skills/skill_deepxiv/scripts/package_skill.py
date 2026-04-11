#!/usr/bin/env python3
"""
打包 DeepXiv skill 到虾评兼容格式
避免 ZIP 时间戳问题
"""

import os
import zipfile
from datetime import datetime
from pathlib import Path


def create_skill_package():
    """创建技能 ZIP 包"""
    
    skill_dir = Path(__file__).parent
    output_zip = skill_dir / "skill_deepxiv.zip"
    
    # 需要打包的文件和目录
    files_to_include = [
        "SKILL.md",
        "scripts/deepxiv_client.py",
        "references/api_endpoints.md"
    ]
    
    # 排除的文件/目录
    exclude_patterns = [
        "__pycache__",
        "*.pyc",
        ".DS_Store"
    ]
    
    # 固定时间戳（2026-04-09）
    fixed_time = (2026, 4, 9, 0, 0, 0)
    
    print("📦 开始打包 DeepXiv skill...")
    
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            for file in files:
                file_path = Path(root) / file
                
                # 排除不需要的文件
                if any(pattern in file_path.name for pattern in exclude_patterns):
                    continue
                
                # 计算相对路径
                rel_path = file_path.relative_to(skill_dir)
                
                # 写入 ZIP
                zinfo = zipfile.ZipInfo.from_file(file_path)
                zinfo.date_time = fixed_time
                zinfo.compress_type = zipfile.ZIP_DEFLATED
                zf.writestr(zinfo, file_path.read_bytes())
                print(f"   ✓ {rel_path}")
    
    file_size = output_zip.stat().st_size
    print(f"\n✅ 打包完成: {output_zip}")
    print(f"   大小: {file_size / 1024:.2f} KB")
    
    return output_zip


if __name__ == "__main__":
    create_skill_package()
