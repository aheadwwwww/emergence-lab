#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""探测觅游网站结构"""

import urllib.request
import urllib.error
import ssl
import sys
import re

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

ssl_context = ssl.create_default_context()

def fetch_url(url):
    """获取网页内容"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def main():
    base_url = "https://www.meyo123.com"
    
    print("=" * 60)
    print("探测觅游网站结构")
    print("=" * 60)
    
    # 获取首页
    print(f"\n1. 获取首页: {base_url}")
    html = fetch_url(base_url)
    if html:
        print(f"   首页长度: {len(html)} 字符")
        
        # 查找 API 端点
        api_patterns = [
            r'api["\']?\s*:\s*["\']([^"\']+)["\']',
            r'["\']([^"\']*api[^"\']*)["\']',
            r'/api/([a-zA-Z0-9_/]+)',
            r'fetch\(["\']([^"\']+)["\']\)',
        ]
        
        found_apis = set()
        for pattern in api_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for m in matches:
                if len(m) < 100:  # 过滤太长的
                    found_apis.add(m)
        
        if found_apis:
            print("\n   发现可能的 API 路径:")
            for api in sorted(found_apis)[:20]:
                print(f"   - {api}")
        
        # 查找脚本文件
        script_pattern = r'src=["\']([^"\']*\.js[^"\']*)["\']'
        scripts = re.findall(script_pattern, html)
        if scripts:
            print(f"\n   发现脚本文件 ({len(scripts)} 个):")
            for s in scripts[:10]:
                print(f"   - {s}")
        
        # 查找登录/用户相关
        user_patterns = [
            r'(login|signin|auth|user|account)',
            r'(post|thread|topic|article)',
            r'(comment|reply)',
        ]
        print("\n   搜索功能关键词...")
        for pattern in user_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                print(f"   - {pattern}: 找到 {len(matches)} 处")
    
    # 尝试常见的 API 路径
    print("\n2. 测试常见 API 路径:")
    test_paths = [
        "/api",
        "/api/v1",
        "/api/v2",
        "/api/posts",
        "/api/topics",
        "/api/user",
        "/api/search",
        "/v1/posts",
        "/posts.json",
        "/topics.json",
    ]
    
    for path in test_paths:
        url = f"{base_url}{path}"
        print(f"   测试: {path}...", end=" ")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as resp:
                content = resp.read().decode('utf-8', errors='ignore')[:200]
                print(f"✓ 状态 {resp.status}, 内容: {content[:100]}")
        except urllib.error.HTTPError as e:
            print(f"✗ HTTP {e.code}")
        except Exception as e:
            print(f"✗ {type(e).__name__}")
    
    print("\n完成")

if __name__ == "__main__":
    main()
