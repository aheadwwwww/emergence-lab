#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 JS 文件中提取 GraphQL 相关信息"""

import re
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

with open("D:\\openclaw_workspace\\meyo\\main.js", "r", encoding="utf-8") as f:
    content = f.read()

print("=" * 60)
print("提取 GraphQL 相关内容")
print("=" * 60)

# 查找可能的 GraphQL 端点
patterns = [
    # 查找 URL 模式
    r'(https?://[^\s"\']+graphql[^\s"\']*)',
    r'(https?://[^\s"\']+gql[^\s"\']*)',
    # 查找 API 路径
    r'["\']([^"\']*(?:graphql|gql)[^"\']*)["\']',
    # 查找 query 定义
    r'query\s+(\w+)\s*[({]',
    r'query\s*:\s*["\']([^"\']+)["\']',
    # 查找 mutation 定义
    r'mutation\s+(\w+)\s*[({]',
    # 查找 API 调用
    r'(fetch|axios|request)\s*\(\s*\{[^}]*url\s*:\s*["\']([^"\']+)["\']',
]

for pattern in patterns:
    matches = re.findall(pattern, content, re.IGNORECASE)
    if matches:
        print(f"\nPattern: {pattern[:50]}...")
        for m in matches[:10]:
            if isinstance(m, tuple):
                print(f"  - {m}")
            else:
                print(f"  - {m}")

# 直接搜索 GraphQL 关键词
print("\n" + "=" * 60)
print("搜索 GraphQL 关键词上下文")
print("=" * 60)

# 找到 query 关键词位置
for match in re.finditer(r'.{50}graphql.{50}', content, re.IGNORECASE):
    print(f"\n>>> {match.group()}")

# 找可能的 API 端点定义
print("\n" + "=" * 60)
print("可能的 API 配置")
print("=" * 60)

# 搜索配置对象
config_patterns = [
    r'const\s+\w*API\w*\s*=\s*["\']([^"\']+)["\']',
    r'const\s+\w*URL\w*\s*=\s*["\']([^"\']+)["\']',
    r'const\s+\w*ENDPOINT\w*\s*=\s*["\']([^"\']+)["\']',
    r'baseURL\s*:\s*["\']([^"\']+)["\']',
]

for pattern in config_patterns:
    matches = re.findall(pattern, content, re.IGNORECASE)
    if matches:
        print(f"\nPattern: {pattern}")
        for m in matches[:5]:
            print(f"  - {m}")
