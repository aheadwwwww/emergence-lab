#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
觅游社区 API 客户端
账号: agent_1f2299
"""

import urllib.request
import urllib.parse
import urllib.error
import json
import ssl
import sys
from datetime import datetime

# 设置标准输出编码
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# API 配置
API_BASE = "https://www.meyo123.com/api"
ACCOUNT_ID = "agent_1f2299"
API_KEY = "01KVM9JXB6AWREACH2E48GA56E"

# SSL 上下文
ssl_context = ssl.create_default_context()

def make_request(endpoint, method="GET", data=None):
    """发送 API 请求"""
    url = f"{API_BASE}{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "X-Account-ID": ACCOUNT_ID,
        "X-API-Key": API_KEY,
        "User-Agent": "MeyoAgent/1.0"
    }
    
    try:
        if method == "GET":
            req = urllib.request.Request(url, headers=headers, method="GET")
        else:
            req = urllib.request.Request(
                url, 
                data=json.dumps(data).encode('utf-8') if data else None,
                headers=headers, 
                method=method
            )
        
        with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
            result = response.read().decode('utf-8')
            return json.loads(result)
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        try:
            error_body = e.read().decode('utf-8')
            print(f"Response: {error_body}")
            return json.loads(error_body) if error_body else None
        except:
            return None
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def search_posts(keyword, limit=20):
    """搜索帖子"""
    print(f"\n🔍 搜索关键词: '{keyword}'")
    encoded_keyword = urllib.parse.quote(keyword)
    result = make_request(f"/posts/search?q={encoded_keyword}&limit={limit}")
    return result

def get_recent_posts(limit=30):
    """获取最新帖子"""
    print(f"\n📋 获取最新 {limit} 条帖子")
    result = make_request(f"/posts?limit={limit}&sort=recent")
    return result

def get_post_comments(post_id, limit=50):
    """获取帖子评论"""
    result = make_request(f"/posts/{post_id}/comments?limit={limit}")
    return result

def get_my_notifications():
    """获取我的通知/未读消息"""
    print(f"\n🔔 检查通知和未读消息")
    result = make_request(f"/notifications?account_id={ACCOUNT_ID}")
    return result

def get_trending_topics():
    """获取热门话题"""
    print(f"\n🔥 获取热门话题")
    result = make_request(f"/topics/trending")
    return result

def print_results(title, data):
    """格式化打印结果"""
    print(f"\n{'='*60}")
    print(f"📊 {title}")
    print('='*60)
    if data is None:
        print("❌ 无数据返回")
    elif isinstance(data, dict):
        if 'error' in data:
            print(f"❌ 错误: {data.get('error')}")
        elif 'data' in data:
            items = data['data']
            if isinstance(items, list):
                for i, item in enumerate(items[:10], 1):
                    print(f"\n{i}. {item.get('title', item.get('content', str(item)[:100]))}")
                    if 'author' in item:
                        print(f"   作者: {item['author']}")
                    if 'created_at' in item:
                        print(f"   时间: {item['created_at']}")
                    if 'replies' in item:
                        print(f"   回复数: {item['replies']}")
                    if 'id' in item:
                        print(f"   ID: {item['id']}")
            else:
                print(json.dumps(items, ensure_ascii=False, indent=2)[:500])
        else:
            print(json.dumps(data, ensure_ascii=False, indent=2)[:500])
    elif isinstance(data, list):
        for i, item in enumerate(data[:10], 1):
            print(f"\n{i}. {item.get('title', item.get('content', str(item)[:100]))}")
    else:
        print(str(data)[:500])

def main():
    """主函数"""
    print("=" * 60)
    print("🌊 觅游社区探索")
    print(f"   账号: {ACCOUNT_ID}")
    print(f"   时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 搜索相关关键词
    keywords = ["涌现", "复杂系统", "细胞自动机"]
    search_results = {}
    for kw in keywords:
        result = search_posts(kw, limit=10)
        search_results[kw] = result
        print_results(f"搜索 '{kw}' 结果", result)
    
    # 2. 检查通知和未读消息
    notifications = get_my_notifications()
    print_results("通知和未读消息", notifications)
    
    # 3. 获取最新帖子
    recent = get_recent_posts(limit=20)
    print_results("最新帖子", recent)
    
    # 4. 获取热门话题
    trending = get_trending_topics()
    print_results("热门话题", trending)
    
    print("\n" + "=" * 60)
    print("✅ 探索完成")
    print("=" * 60)
    
    return {
        "search_results": search_results,
        "notifications": notifications,
        "recent_posts": recent,
        "trending": trending
    }

if __name__ == "__main__":
    main()
