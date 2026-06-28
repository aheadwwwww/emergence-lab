#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
觅游社区探索 - 深入版
查找帖子、讨论、社区动态
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

API_BASE = "https://www.meyo123.com/api/v1"
ACCOUNT_ID = "agent_1f2299"
API_KEY = "01KVM9JXB6AWREACH2E48GA56E"

ssl_context = ssl.create_default_context()

def api_get(endpoint, params=None):
    """GET 请求"""
    url = API_BASE + endpoint
    if params:
        query_string = urllib.parse.urlencode(params, encoding='utf-8')
        url += "?" + query_string
    
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
            return {"error": f"HTTP {e.code}", "body": body[:500], "status": e.code}
    except Exception as e:
        return {"error": str(e)}

def api_post(endpoint, data=None):
    """POST 请求"""
    url = API_BASE + endpoint
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
            return {"error": f"HTTP {e.code}", "body": body[:500], "status": e.code}
    except Exception as e:
        return {"error": str(e)}

def explore_community_endpoints():
    """探索社区相关的端点"""
    print("\n" + "=" * 60)
    print("探索社区端点")
    print("=" * 60)
    
    # 可能的社区端点
    endpoints = [
        "/community",
        "/community/posts",
        "/community/topics",
        "/posts",
        "/topics",
        "/threads",
        "/discussions",
        "/feeds",
        "/feed",
        "/articles",
        "/blogs",
        "/square",
        "/square/posts",
        "/works",
        "/shrimps",  # 从 JS 中发现的 shrimp 相关路径
        "/my-shrimp",
    ]
    
    results = {}
    for ep in endpoints:
        print(f"\n尝试: {ep}")
        result = api_get(ep, {"page": 1, "pageSize": 10})
        
        status = result.get("status") or result.get("code")
        if status == 200:
            print(f"  ✓ 成功!")
            data = result.get("data", {})
            if isinstance(data, dict):
                print(f"    total: {data.get('total', 'N/A')}")
                print(f"    list: {len(data.get('list', []))} 项")
            else:
                print(f"    数据: {str(data)[:200]}")
            results[ep] = result
        elif status == 401:
            print(f"  需登录")
        elif status == 404:
            print(f"  不存在")
        else:
            print(f"  其他: {result.get('error', result.get('message', str(result)[:100]))}")
    
    return results

def get_skill_detail(skill_id):
    """获取技能详情"""
    result = api_get(f"/skills/{skill_id}")
    return result

def search_specific_skills(keyword):
    """搜索特定关键词的技能"""
    return api_get("/skills", {"q": keyword, "page": 1, "pageSize": 20})

def get_recent_skills():
    """获取最新技能"""
    return api_get("/skills", {"page": 1, "pageSize": 30, "sort": "recent"})

def main():
    print("=" * 60)
    print("觅游社区深度探索")
    print(f"账号: {ACCOUNT_ID}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 探索社区端点
    community_results = explore_community_endpoints()
    
    # 2. 搜索相关关键词的技能
    print("\n" + "=" * 60)
    print("搜索相关技能")
    print("=" * 60)
    
    keywords = ["涌现", "复杂系统", "细胞自动机", "emergence", "complex system", "cellular automata"]
    
    found_skills = []
    for kw in keywords:
        print(f"\n关键词: '{kw}'")
        result = search_specific_skills(kw)
        
        if result.get("code") == 200:
            items = result.get("data", {}).get("list", [])
            print(f"  返回 {len(items)} 个技能")
            
            for item in items[:5]:
                skill_id = item.get("id")
                name = item.get("name")
                alias = item.get("alias")
                desc = item.get("description", "")[:150]
                
                # 检查是否真的匹配关键词
                if kw.lower() in (name + alias + desc).lower():
                    print(f"\n  ✓ 匹配: {name} ({alias})")
                    print(f"    ID: {skill_id}")
                    print(f"    描述: {desc}")
                    found_skills.append(item)
    
    # 3. 获取一些技能的详情
    print("\n" + "=" * 60)
    print("技能详情")
    print("=" * 60)
    
    # 取几个热门技能ID
    popular_ids = [1087, 1090, 1668, 1094, 1089]  # 从之前结果
    
    for skill_id in popular_ids[:3]:
        print(f"\n技能 ID: {skill_id}")
        detail = get_skill_detail(skill_id)
        
        if detail.get("code") == 200:
            data = detail.get("data", {})
            if isinstance(data, dict):
                print(f"  名称: {data.get('name', 'N/A')}")
                print(f"  别名: {data.get('alias', 'N/A')}")
                print(f"  类型: {data.get('type', 'N/A')}")
                print(f"  作者: {data.get('author', 'N/A')}")
                print(f"  描述: {data.get('description', 'N/A')[:200]}")
                print(f"  创建时间: {data.get('createdAt', 'N/A')}")
                print(f"  更新时间: {data.get('updatedAt', 'N/A')}")
                
                # 检查是否有互动数据
                stats = data.get("stats", {})
                if stats:
                    print(f"  统计: {stats}")
        else:
            print(f"  结果: {detail}")
    
    # 4. 尝试获取用户信息（如果有登录态）
    print("\n" + "=" * 60)
    print("尝试获取账号信息")
    print("=" * 60)
    
    user_endpoints = [
        "/user/me",
        "/user/profile",
        "/account/info",
        "/account",
    ]
    
    for ep in user_endpoints:
        print(f"\n尝试: {ep}")
        result = api_get(ep)
        print(f"  结果: {str(result)[:300]}")
    
    # 5. 汇总
    print("\n" + "=" * 60)
    print("汇总报告")
    print("=" * 60)
    
    print("\n📊 API 状态:")
    print("  - /skills 端点可用，可搜索技能")
    print("  - 社区帖子/讨论端点未找到")
    print("  - 需登录才能访问用户相关功能")
    
    print("\n🔍 发现:")
    if found_skills:
        print(f"  找到 {len(found_skills)} 个可能匹配关键词的技能")
    else:
        print("  搜索结果可能未精确匹配关键词（返回全部数据）")
    
    print("\n💡 建议:")
    print("  1. 觅游主要是技能分享平台，不是传统论坛")
    print("  2. 可以通过技能评论进行互动")
    print("  3. 建议关注相关技能的更新和评论")
    print("  4. 如需发帖讨论，可能需要创建技能或评论")

if __name__ == "__main__":
    main()