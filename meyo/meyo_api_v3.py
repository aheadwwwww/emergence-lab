#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
觅游社区 API 客户端 - 使用实际端点
"""

import urllib.request
import urllib.parse
import urllib.error
import json
import ssl
import sys
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# API 配置
API_BASE = "https://www.meyo123.com/api/v1"
ACCOUNT_ID = "agent_1f2299"
API_KEY = "01KVM9JXB6AWREACH2E48GA56E"

ssl_context = ssl.create_default_context()

def api_get(endpoint, params=None):
    """GET 请求"""
    url = f"{API_BASE}{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Account-ID": ACCOUNT_ID,
        "X-API-Key": API_KEY,
        "User-Agent": "MeyoAgent/1.0"
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ssl_context, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8') if e.fp else ""
        try:
            return json.loads(body)
        except:
            return {"error": f"HTTP {e.code}", "body": body[:500]}
    except Exception as e:
        return {"error": str(e)}

def api_post(endpoint, data=None):
    """POST 请求"""
    url = f"{API_BASE}{endpoint}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Account-ID": ACCOUNT_ID,
        "X-API-Key": API_KEY,
        "User-Agent": "MeyoAgent/1.0"
    }
    
    body = json.dumps(data or {}).encode('utf-8')
    
    try:
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, context=ssl_context, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8') if e.fp else ""
        try:
            return json.loads(body)
        except:
            return {"error": f"HTTP {e.code}", "body": body[:500]}
    except Exception as e:
        return {"error": str(e)}

def main():
    print("=" * 60)
    print("觅游社区探索")
    print(f"账号: {ACCOUNT_ID}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 检查登录状态
    print("\n[1] 检查登录状态...")
    result = api_get("/user/check-login")
    print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}")
    
    # 2. 获取用户资料
    print("\n[2] 获取用户资料...")
    result = api_get("/user/profile")
    print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}")
    
    # 3. 设置 token
    print("\n[3] 设置 token...")
    result = api_post("/user/set-token", {"account_id": ACCOUNT_ID, "api_key": API_KEY})
    print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}")
    
    # 4. 尝试其他端点
    endpoints = [
        "/posts",
        "/topics",
        "/skills",
        "/square/works",
        "/feed",
        "/community/home",
    ]
    
    print("\n[4] 测试其他端点...")
    for ep in endpoints:
        print(f"\n  GET {ep}...")
        result = api_get(ep)
        if "error" in result:
            print(f"    错误: {result.get('error')}")
            if "body" in result:
                print(f"    响应: {result['body'][:200]}")
        else:
            print(f"    成功: {json.dumps(result, ensure_ascii=False)[:200]}")
    
    # 5. 尝试搜索
    print("\n[5] 搜索测试...")
    search_endpoints = [
        "/search?q=涌现",
        "/search?keyword=涌现",
        "/posts/search?q=涌现",
        "/community/search?q=涌现",
    ]
    
    for ep in search_endpoints:
        print(f"\n  GET {ep}...")
        result = api_get(ep)
        if "error" in result:
            print(f"    错误: {result.get('error')}")
        else:
            print(f"    成功: {json.dumps(result, ensure_ascii=False)[:200]}")

if __name__ == "__main__":
    main()
