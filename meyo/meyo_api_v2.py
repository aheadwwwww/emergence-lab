#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
觅游社区 API 客户端 - 正确版本
API 基础路径: /api/v1
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

def make_request(endpoint, method="GET", data=None, raw_response=False):
    """发送 API 请求"""
    url = f"{API_BASE}{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Account-ID": ACCOUNT_ID,
        "X-API-Key": API_KEY,
        "User-Agent": "MeyoAgent/1.0"
    }
    
    try:
        if method == "GET":
            req = urllib.request.Request(url, headers=headers, method="GET")
        else:
            body = json.dumps(data).encode('utf-8') if data else b'{}'
            req = urllib.request.Request(url, data=body, headers=headers, method=method)
        
        with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
            result = response.read().decode('utf-8')
            if raw_response:
                return result
            try:
                return json.loads(result)
            except:
                return {"raw": result[:500]}
                
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        try:
            error_body = e.read().decode('utf-8')
            print(f"Response: {error_body[:500]}")
            return {"error": f"HTTP {e.code}", "body": error_body[:500]}
        except:
            return {"error": f"HTTP {e.code}"}
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
        return {"error": str(e.reason)}
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}

def graphql_query(query, variables=None):
    """发送 GraphQL 查询"""
    url = f"{API_BASE}/graphql"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Account-ID": ACCOUNT_ID,
        "X-API-Key": API_KEY,
        "User-Agent": "MeyoAgent/1.0"
    }
    
    data = {"query": query}
    if variables:
        data["variables"] = variables
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method="POST"
        )
        
        with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
            result = response.read().decode('utf-8')
            return json.loads(result)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else ""
        return {"error": f"HTTP {e.code}", "body": error_body[:500]}
    except Exception as e:
        return {"error": str(e)}

def test_endpoints():
    """测试各种 API 端点"""
    print("=" * 60)
    print("测试 API 端点")
    print("=" * 60)
    
    endpoints = [
        "/",
        "/posts",
        "/topics",
        "/user",
        "/search",
        "/notifications",
        "/graphql",
    ]
    
    for ep in endpoints:
        print(f"\n测试: {ep}")
        result = make_request(ep)
        print(f"结果: {str(result)[:200]}")

def explore_graphql():
    """探索 GraphQL API"""
    print("\n" + "=" * 60)
    print("探索 GraphQL")
    print("=" * 60)
    
    # 尝试 introspection
    introspection_query = """
    {
        __schema {
            types {
                name
            }
        }
    }
    """
    
    print("\n尝试 GraphQL introspection...")
    result = graphql_query(introspection_query)
    print(f"结果: {str(result)[:500]}")
    
    # 尝试一些常见的查询
    queries = [
        ("获取帖子", "{ posts { id title content } }"),
        ("获取主题", "{ topics { id name } }"),
        ("搜索", '{ search(query: "涌现") { id title } }'),
        ("用户信息", "{ me { id name } }"),
    ]
    
    for name, query in queries:
        print(f"\n尝试: {name}")
        result = graphql_query(query)
        print(f"结果: {str(result)[:300]}")

def main():
    print("=" * 60)
    print("觅游社区探索")
    print(f"账号: {ACCOUNT_ID}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 测试 REST 端点
    test_endpoints()
    
    # 探索 GraphQL
    explore_graphql()

if __name__ == "__main__":
    main()
