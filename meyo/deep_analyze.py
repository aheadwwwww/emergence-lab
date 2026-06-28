#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""深入分析觅游网站的网络请求"""

import urllib.request
import urllib.error
import ssl
import sys
import re
import json
from html.parser import HTMLParser

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

ssl_context = ssl.create_default_context()

def fetch_html(url):
    """获取 HTML"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ssl_context, timeout=30) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    print("=" * 60)
    print("深入分析觅游网站")
    print("=" * 60)
    
    # 1. 获取首页
    html = fetch_html("https://www.meyo123.com")
    if not html:
        return
    
    # 保存首页
    with open("D:\\openclaw_workspace\\meyo\\index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"首页已保存 ({len(html)} 字符)")
    
    # 2. 分析 JS 文件中的 API 调用
    print("\n" + "=" * 60)
    print("分析主 JS 文件中的 API 调用")
    print("=" * 60)
    
    # 读取之前保存的 main.js
    with open("D:\\openclaw_workspace\\meyo\\main.js", "r", encoding="utf-8") as f:
        js_content = f.read()
    
    # 搜索 fetch 调用
    print("\n搜索 fetch 调用...")
    fetch_pattern = r'fetch\s*\(\s*["\']([^"\']+)["\']'
    fetch_calls = re.findall(fetch_pattern, js_content)
    if fetch_calls:
        print(f"找到 {len(fetch_calls)} 个 fetch 调用:")
        for call in set(fetch_calls)[:15]:
            print(f"  - {call}")
    
    # 搜索 axios 调用
    print("\n搜索 axios 模式...")
    axios_patterns = [
        r'axios\.get\s*\(\s*["\']([^"\']+)["\']',
        r'axios\.post\s*\(\s*["\']([^"\']+)["\']',
        r'axios\s*\(\s*\{[^}]*url\s*:\s*["\']([^"\']+)["\']',
    ]
    for pattern in axios_patterns:
        matches = re.findall(pattern, js_content, re.DOTALL)
        if matches:
            print(f"  Pattern: {pattern[:40]}...")
            for m in set(matches)[:5]:
                print(f"    - {m}")
    
    # 搜索 request 调用
    print("\n搜索 request 调用...")
    request_pattern = r'\.request\s*\(\s*\{[^}]*url\s*:\s*["\']([^"\']+)["\']'
    request_calls = re.findall(request_pattern, js_content, re.DOTALL)
    if request_calls:
        print(f"找到 {len(request_calls)} 个 request 调用:")
        for call in set(request_calls)[:10]:
            print(f"  - {call}")
    
    # 搜索可能的服务端点
    print("\n搜索服务端点定义...")
    service_patterns = [
        r'const\s+\w+\s*=\s*\{[^}]*url\s*:\s*["\']([^"\']+)["\']',
        r'endpoint\s*:\s*["\']([^"\']+)["\']',
        r'api\s*:\s*["\']([^"\']+)["\']',
    ]
    for pattern in service_patterns:
        matches = re.findall(pattern, js_content, re.IGNORECASE)
        if matches:
            print(f"  Pattern: {pattern[:50]}...")
            for m in set(matches)[:5]:
                print(f"    - {m}")
    
    # 3. 搜索 meyo 相关的域名和路径
    print("\n" + "=" * 60)
    print("搜索 meyo 相关路径")
    print("=" * 60)
    
    meyo_patterns = [
        r'https?://[^"\'>\s]*meyo[^"\'>\s]*',
        r'/api/[^"\'>\s]*',
        r'/v[0-9]/[^"\'>\s]*',
    ]
    
    for pattern in meyo_patterns:
        matches = re.findall(pattern, js_content, re.IGNORECASE)
        if matches:
            print(f"\n{pattern}:")
            for m in sorted(set(matches))[:10]:
                print(f"  - {m}")
    
    # 4. 搜索具体的接口路径关键词
    print("\n" + "=" * 60)
    print("搜索接口关键词上下文")
    print("=" * 60)
    
    keywords = ['post', 'thread', 'topic', 'comment', 'search', 'user', 'login']
    for kw in keywords:
        # 找到关键词附近的 URL 模式
        pattern = rf'.{{0,50}}["\']([^"\']*(?:{kw})[^"\']*)["\'].{{0,50}}'
        matches = re.findall(pattern, js_content, re.IGNORECASE)
        if matches:
            relevant = [m for m in matches if '/' in m and len(m) < 100][:5]
            if relevant:
                print(f"\n{kw}:")
                for m in relevant:
                    print(f"  - {m}")

if __name__ == "__main__":
    main()