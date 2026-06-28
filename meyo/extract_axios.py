#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提取 Axios 配置和 API 调用"""

import re
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

with open("D:\\openclaw_workspace\\meyo\\index-D18_q29a.js", "r", encoding="utf-8") as f:
    content = f.read()

print("=" * 60)
print("提取 Axios 相关配置")
print("=" * 60)

# 搜索 axios 实例创建
patterns = [
    # axios.create 配置
    r'axios\.create\s*\(\s*\{([^}]+)\}\)',
    # baseURL 配置
    r'baseURL\s*:\s*["\']([^"\']+)["\']',
    # headers 配置
    r'headers\s*:\s*\{[^}]+\}',
    # 拦截器
    r'interceptors\.(request|response)\.use',
    # 实际的 HTTP 方法调用
    r'\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
    # 请求配置
    r'method\s*:\s*"(get|post|put|delete)"',
]

for pattern in patterns:
    matches = re.findall(pattern, content, re.IGNORECASE)
    if matches:
        print(f"\nPattern: {pattern[:60]}...")
        for m in matches[:10]:
            if isinstance(m, tuple):
                print(f"  {m}")
            else:
                print(f"  {m[:200] if len(m) > 200 else m}")

# 搜索可能的 API 服务类
print("\n" + "=" * 60)
print("搜索 API 服务")
print("=" * 60)

# 搜索类似 class 或 service 定义
service_patterns = [
    r'class\s+(\w*Api\w*)\s*\{',
    r'class\s+(\w*Service\w*)\s*\{',
    r'const\s+(\w*api\w*)\s*=\s*\{',
    r'const\s+(\w*Api\w*)\s*=\s*\{',
    r'export\s+(?:const|class)\s+(\w*[Aa]pi\w*)',
]

for pattern in service_patterns:
    matches = re.findall(pattern, content)
    if matches:
        print(f"\nPattern: {pattern}")
        for m in set(matches)[:10]:
            print(f"  - {m}")

# 搜索完整的 URL
print("\n" + "=" * 60)
print("搜索完整 URL")
print("=" * 60)

url_pattern = r'https?://[^\s"\'<>]+[^\s"\'<>,.\)]'
urls = re.findall(url_pattern, content)
unique_urls = sorted(set(urls))
print(f"\n找到 {len(unique_urls)} 个唯一 URL:")
for url in unique_urls[:30]:
    print(f"  - {url}")
