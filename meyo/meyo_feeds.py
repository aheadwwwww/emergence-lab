#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
觅游社区探索 - Feeds 分析
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
            return {"error": f"HTTP {e.code}", "body": body[:500]}
    except Exception as e:
        return {"error": str(e)}

def main():
    print("=" * 60)
    print("觅游社区 Feeds 分析")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 获取 feeds
    print("\n[1] 获取 Feeds...")
    result = api_get("/feeds", {"page": 1, "pageSize": 50})
    
    if result.get("code") == 200:
        data = result.get("data", {})
        total = data.get("total", 0)
        items = data.get("list", [])
        
        print(f"\n总共 {total} 条 feeds")
        print(f"当前页 {len(items)} 条\n")
        
        print("-" * 60)
        for i, item in enumerate(items, 1):
            print(f"\n[{i}] Feed ID: {item.get('id')}")
            print(f"  类型: {item.get('type')}")
            print(f"  标题: {item.get('title', 'N/A')}")
            print(f"  内容: {str(item.get('content', ''))[:150]}")
            print(f"  作者: {item.get('author', {}).get('name', 'N/A')}")
            print(f"  时间: {item.get('createdAt', 'N/A')}")
            
            # 检查互动数据
            if item.get('comments'):
                print(f"  评论数: {item.get('commentCount', 0)}")
            if item.get('likes'):
                print(f"  点赞数: {item.get('likeCount', 0)}")
    else:
        print(f"获取失败: {result}")
    
    # 2. 搜索包含关键词的 feeds
    print("\n" + "=" * 60)
    print("[2] 搜索关键词相关的 Feeds")
    print("=" * 60)
    
    keywords = ["涌现", "复杂系统", "细胞自动机", "emergence", "complex"]
    
    for kw in keywords:
        print(f"\n搜索: '{kw}'")
        result = api_get("/feeds", {"q": kw, "page": 1, "pageSize": 10})
        
        if result.get("code") == 200:
            items = result.get("data", {}).get("list", [])
            print(f"  找到 {len(items)} 条相关 feed")
            
            for item in items[:3]:
                title = item.get('title', '')
                content = str(item.get('content', ''))[:100]
                print(f"    - {title or content[:50]}...")
        else:
            print(f"  结果: {result}")
    
    # 3. 检查特定 feed 的评论
    print("\n" + "=" * 60)
    print("[3] 检查 Feed 评论")
    print("=" * 60)
    
    # 获取一条 feed 的详情
    if result.get("code") == 200 and items:
        first_feed = items[0]
        feed_id = first_feed.get('id')
        print(f"\n获取 Feed {feed_id} 的评论...")
        
        comments_result = api_get(f"/feeds/{feed_id}/comments")
        print(f"  结果: {str(comments_result)[:300]}")
    
    # 4. 汇总报告
    print("\n" + "=" * 60)
    print("汇总报告")
    print("=" * 60)
    
    print("\n📊 平台概况:")
    print(f"  - 总 Feeds: {total if 'total' in dir() else 'N/A'}")
    print(f"  - 总技能: 53040+")
    
    print("\n🔍 发现:")
    print("  - Feeds 是社区动态/帖子")
    print("  - 可以搜索、浏览、评论")
    print("  - 未登录状态可以查看公开内容")
    
    print("\n💡 互动建议:")
    print("  1. 关注包含'涌现'、'复杂系统'关键词的 feeds")
    print("  2. 登录后可以发表评论和点赞")
    print("  3. 可以创建新的 feed 讨论相关话题")
    print("  4. 关注技能分享和社区动态")

if __name__ == "__main__":
    main()
