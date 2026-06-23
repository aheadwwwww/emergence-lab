"""
编码修复工具
在所有实验脚本开头 import 这个模块，自动修复 Windows GBK 编码问题
"""

import sys
import io

def fix_encoding():
    """修复 stdout/stderr 编码为 utf-8"""
    if sys.stdout.encoding.lower() != 'utf-8':
        try:
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, 
                encoding='utf-8', 
                errors='replace'
            )
        except (AttributeError, OSError):
            try:
                sys.stdout.reconfigure(encoding='utf-8')
            except Exception:
                pass
    
    if sys.stderr.encoding.lower() != 'utf-8':
        try:
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer,
                encoding='utf-8',
                errors='replace'
            )
        except (AttributeError, OSError):
            try:
                sys.stderr.reconfigure(encoding='utf-8')
            except Exception:
                pass


# 导入时自动执行
fix_encoding()
