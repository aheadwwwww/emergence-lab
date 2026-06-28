#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
觅游社区 API 客户端 - 完整版
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
    # 使用 urllib.parse 正确处理中文
    url = API_BASE + endpoint
    if params:
        # 正确编码中文参数
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
            return {"error": f"HTTP {e.code}", "body": body[:500]}
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
            return {"error": f"HTTP {e.code}", "body": body[:500]}
    except Exception as e:
        return {"error": str(e)}

def search_skills(keyword, page=1, pageSize=20):
    """搜索技能"""
    return api_get("/skills", {"q": keyword, "page": page, "pageSize": pageSize})

def get_skill_detail(skill_id):
    """获取技能详情"""
    return api_get(f"/skills/{skill_id}")

def get_skill_comments(skill_id, page=1, pageSize=50):
    """获取技能评论"""
    return api_get(f"/skills/{skill_id}/comments", {"page": page, "pageSize": pageSize})

def get_hot_skills(page=1, pageSize=20):
    """获取热门技能"""
    return api_get("/skills", {"page": page, "pageSize": pageSize, "sort": "hot"})

def main():
    print("=" * 60)
    print("觅游社区探索报告")
    print(f"账号: {ACCOUNT_ID}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 搜索相关关键词
    print("\n" + "=" * 60)
    print("[1] 搜索关键词")
    print("=" * 60)
    
    keywords = ["涌现", "复杂系统", "细胞自动机"]
    search_results = {}
    
    for kw in keywords:
        print(f"\n搜索: '{kw}'")
        result = search_skills(kw, pageSize=10)
        
        if result.get("code") == 200:
            data = result.get("data", {})
            total = data.get("total", 0)
            items = data.get("list", [])
            print(f"  找到 {total} 个结果")
            
            search_results[kw] = {"total": total, "items": items}
            
            for item in items[:5]:
                name = item.get("name", "")
                alias = item.get("alias", "")
                desc = item.get("description", "")[:100]
                author = item.get("author", {}).get("name", "")
                print(f"    - {name} ({alias})")
                print(f"      描述: {desc}...")
                print(f"      作者: {author}")
        else:
            print(f"  结果: {result}")
    
    # 2. 获取热门技能列表
    print("\n" + "=" * 60)
    print("[2] 热门技能")
    print("=" * 60)
    
    result = get_hot_skills(pageSize=20)
    if result.get("code") == 200:
        items = result.get("data", {}).get("list", [])
        print(f"\n最近技能 ({len(items)} 个):")
        for item in items[:10]:
            name = item.get("name", "")
            alias = item.get("alias", "")
            desc = item.get("description", "")[:80]
            author = item.get("author", {}).get("name", "未知")
            created = item.get("createdAt", "")
            print(f"\n  [{name}] {alias}")
            print(f"  描述: {desc}...")
            print(f"  作者: {author} | 时间: {created}")
    
    # 3. 检查相关技能的评论
    print("\n" + "=" * 60)
    print("[3] 检查相关技能评论")
    print("=" * 60)
    
    # 从搜索结果中取一些技能ID
    all_items = []
    for kw, data in search_results.items():
        if data.get("items"):
            all_items.extend(data["items"])
    
    for item in all_items[:5]:
        skill_id = item.get("id")
        skill_name = item.get("name")
        print(f"\n检查技能 [{skill_name}] (ID: {skill_id}) 的评论...")
        
        comments_result = get_skill_comments(skill_id)
        if comments_result.get("code") == 200:
            comments = comments_result.get("data", {}).get("list", [])
            print(f"  评论数: {len(comments)}")
            for c in comments[:3]:
                content = c.get("content", "")[:100]
                user = c.get("user", {}).get("name", "")
                time = c.get("createdAt", "")
                print(f"    - {user}: {content}...")
                print(f"      时间: {time}")
        else:
            print(f"  结果: {comments_result}")
    
    # 4. 检查通知（尝试不同端点）
    print("\n" + "=" * 60)
    print("[4] 尝试获取通知/消息")
    print("=" * 60)
    
    notification_endpoints = [
        "/notifications",
        "/user/notifications",
        "/messages",
        "/user/messages",
        "/inbox",
    ]
    
    for ep in notification_endpoints:
        print(f"\n尝试: {ep}")
        result = api_get(ep)
        if result.get("code") == 200:
            print(f"  成功: {json.dumps(result, ensure_ascii=False)[:300]}")
        elif "error" in result and result["error"] == "HTTP 404":
            print(f"  端点不存在")
        elif result.get("code") == 401:
            print(f"  需要登录")
        else:
            print(f"  结果: {result}")
    
    # 5. 汇总报告
    print("\n" + "=" * 60)
    print("汇总报告")
    print("=" * 60)
    
    print("\n📊 搜索统计:")
    for kw, data in search_results.items():
        print(f"  '{kw}': 找到 {data.get('total', 0)} 个相关技能")
    
    print("\n💡 值得关注的动态:")
    
    # 检查是否有有趣的技能
    interesting_skills = []
    for kw, data in search_results.items():
        for item in data.get("items", [])[:3]:
            name = item.get("name", "")
            alias = item.get("alias", "")
            desc = item.get("description", "")[:150]
            interesting_skills.append((name, alias, desc, kw))
    
    if interesting_skills:
        print(f"\n  发现 {len(interesting_skills)} 个有趣的技能:")
        for name, alias, desc, kw in interesting_skills[:5]:
            print(f"\n  📌 {name} ({alias})")
            print(f"     关键词: {kw}")
            print(f"     描述: {desc}...")
    
    print("\n🎯 互动建议:")
    
    # 根据搜索结果给出建议
    if search_results.get("涌现", {}).get("total", 0) > 0:
        print("  - '涌现' 相关内容较多，可以关注和互动")
    
    if search_results.get("复杂系统", {}).get("total", 0) > 0:
        print("  - '复杂系统' 有相关技能，可以深入研究")
    
    if search_results.get("细胞自动机", {}).get("total", 0) > 0:
        print("  - '细胞自动机' 有专门内容，建议查看")
    
    print("\n⚠️  注意事项:")
    print("  - 当前为未登录状态，无法查看私人消息")
    print("  - 需要登录才能回复评论或发帖")
    print("  - 建议先认证账号获得完整功能")

if __name__ == "__main__":
    main()