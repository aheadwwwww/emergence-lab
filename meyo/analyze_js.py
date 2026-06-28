#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""分析觅游 JS 文件找 API 端点"""

import urllib.request
import urllib.error
import ssl
import sys
import re
import json

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

ssl_context = ssl.create_default_context()

def fetch_url(url):
    """获取内容"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ssl_context, timeout=60) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    # 主要的 JS 文件
    main_js = "https://s3.meituan.net/static-prod01/ws-assets/com.sankuai.ai.meyo.web/4imwJ7XTNI8LrPNR3SopG/assets/index-D18_q29a.js"
    
    print("=" * 60)
    print("分析主 JS 文件")
    print("=" * 60)
    
    print(f"\n下载: {main_js}")
    js_content = fetch_url(main_js)
    
    if not js_content:
        print("下载失败")
        return
    
    print(f"文件大小: {len(js_content)} 字符")
    
    # 查找 API 相关模式
    print("\n" + "=" * 60)
    print("查找 API 端点")
    print("=" * 60)
    
    # 常见的 API 模式
    patterns = [
        # URL 模板
        (r'["\']([^"\']*(?:/api/|/v1/|/v2/)[^"\']*)["\']', "API路径"),
        # fetch/axios 调用
        (r'(?:fetch|axios|request)\s*\(\s*["\']([^"\']+)["\']', "请求调用"),
        # 接口定义
        (r'url\s*:\s*["\']([^"\']+)["\']', "URL定义"),
        # GraphQL
        (r'graphql|query\s*\{', "GraphQL"),
        # 端点
        (r'endpoint\s*:\s*["\']([^"\']+)["\']', "端点"),
    ]
    
    found_urls = set()
    for pattern, desc in patterns:
        matches = re.findall(pattern, js_content, re.IGNORECASE)
        if matches:
            print(f"\n{desc}: {len(matches)} 个")
            for m in matches[:15]:
                if isinstance(m, str) and len(m) < 200 and not m.startswith('data:'):
                    found_urls.add(m)
                    print(f"  - {m}")
    
    # 搜索特定关键词
    keywords = ['meyo', 'post', 'thread', 'topic', 'comment', 'user', 'search', 
                'login', 'auth', 'api', 'graphql', 'query', 'mutation']
    
    print("\n" + "=" * 60)
    print("关键词统计")
    print("=" * 60)
    for kw in keywords:
        count = len(re.findall(kw, js_content, re.IGNORECASE))
        if count > 0:
            print(f"  {kw}: {count} 次")
    
    # 提取 API 基础 URL
    print("\n" + "=" * 60)
    print("可能的 API 基础 URL")
    print("=" * 60)
    
    base_patterns = [
        r'https?://[^"\'>\s]+meyo[^"\'>\s]*',
        r'https?://[^"\'>\s]+meituan[^"\'>\s]+api[^"\'>\s]*',
        r'BASE_URL\s*[:=]\s*["\']([^"\']+)["\']',
        r'API_URL\s*[:=]\s*["\']([^"\']+)["\']',
    ]
    
    for pattern in base_patterns:
        matches = re.findall(pattern, js_content, re.IGNORECASE)
        for m in matches[:10]:
            if isinstance(m, str):
                print(f"  - {m}")
            else:
                print(f"  - {m}")
    
    # 保存 JS 内容供进一步分析
    with open("D:\\openclaw_workspace\\meyo\\main.js", "w", encoding="utf-8") as f:
        f.write(js_content)
    print(f"\nJS 文件已保存到 main.js")

if __name__ == "__main__":
    main()
