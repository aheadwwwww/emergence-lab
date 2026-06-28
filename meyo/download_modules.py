#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""下载并分析觅游的子模块 JS"""

import urllib.request
import ssl
import sys
import re
import json

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

ssl_context = ssl.create_default_context()

def fetch_js(url):
    """下载 JS 文件"""
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ssl_context, timeout=60) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def find_api_calls(js_content, filename):
    """在 JS 内容中查找 API 调用"""
    print(f"\n{'='*60}")
    print(f"分析: {filename}")
    print('='*60)
    
    # 各种 API 调用模式
    patterns = [
        (r'fetch\s*\(\s*`([^`]+)`', "fetch template literal"),
        (r'fetch\s*\(\s*["\']([^"\']+)["\']', "fetch string"),
        (r'url\s*:\s*`([^`]+)`', "url template literal"),
        (r'url\s*:\s*["\']([^"\']+)["\']', "url string"),
        (r'path\s*:\s*["\']([^"\']+)["\']', "path string"),
        (r'endpoint\s*:\s*["\']([^"\']+)["\']', "endpoint string"),
        (r'["\']/(api|v[0-9])/[^"\']+["\']', "API path"),
    ]
    
    found = set()
    for pattern, desc in patterns:
        matches = re.findall(pattern, js_content, re.IGNORECASE)
        for m in matches:
            if isinstance(m, str) and len(m) < 200 and not m.startswith('data:'):
                found.add((desc, m))
    
    if found:
        print(f"找到 {len(found)} 个可能的 API 调用:")
        for desc, url in sorted(found, key=lambda x: x[0])[:20]:
            print(f"  [{desc}] {url}")
    
    return found

def main():
    # 从首页提取的资源
    base = "https://s3.meituan.net/static-prod01/ws-assets/com.sankuai.ai.meyo.web/4imwJ7XTNI8LrPNR3SopG/assets/"
    
    modules = [
        "comment-9y8iwT3P.js",
        "SkillCommentTab.vue_vue_type_script_setup_true_lang-B-EObZU6.js", 
        "ShrimpCommentCard-C_fn3Dt5.js",
        "useLoginGuard-cHQJidHl.js",
        "index-D18_q29a.js",  # 主模块
    ]
    
    all_apis = set()
    
    for module in modules:
        url = base + module
        print(f"\n下载: {module}...")
        js = fetch_js(url)
        
        if js:
            # 保存
            safe_name = module.replace('/', '_').replace('?', '_')
            with open(f"D:\\openclaw_workspace\\meyo\\{safe_name}", "w", encoding="utf-8") as f:
                f.write(js)
            print(f"  已保存 ({len(js)} 字符)")
            
            # 分析
            apis = find_api_calls(js, module)
            all_apis.update(apis)
    
    # 汇总
    print("\n" + "=" * 60)
    print("汇总所有发现的 API")
    print("=" * 60)
    for desc, url in sorted(all_apis):
        print(f"  [{desc}] {url}")

if __name__ == "__main__":
    main()
