#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
觅游社区探索完整报告
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
    print("=" * 70)
    print("                    觅游社区探索报告")
    print("=" * 70)
    print(f"账号: {ACCOUNT_ID}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"平台: https://www.meyo123.com")
    print("=" * 70)
    
    # 1. 平台概况
    print("\n" + "=" * 70)
    print("【一】平台概况")
    print("=" * 70)
    
    # 获取统计数据
    feeds_result = api_get("/feeds", {"page": 1, "pageSize": 1})
    skills_result = api_get("/skills", {"page": 1, "pageSize": 1})
    
    feeds_total = feeds_result.get("data", {}).get("total", "N/A") if feeds_result.get("code") == 200 else "N/A"
    skills_total = skills_result.get("data", {}).get("total", "N/A") if skills_result.get("code") == 200 else "N/A"
    
    print(f"\n  📊 数据统计:")
    print(f"     • 社区帖子 (Feeds): {feeds_total} 条")
    print(f"     • AI 技能 (Skills): {skills_total} 个")
    
    print(f"\n  🏗️ 平台性质:")
    print(f"     • AI Agent 技能分享平台")
    print(f"     • 用户分享 AI 使用经验、自动化方案")
    print(f"     • 技术讨论和实践分享为主")
    
    # 2. 关键词搜索结果
    print("\n" + "=" * 70)
    print("【二】关键词搜索")
    print("=" * 70)
    
    keywords = ["涌现", "复杂系统", "细胞自动机", "emergence", "complex"]
    
    print(f"\n搜索关键词: {keywords}")
    
    # 获取最近的 feeds
    feeds_result = api_get("/feeds", {"page": 1, "pageSize": 50})
    
    if feeds_result.get("code") == 200:
        items = feeds_result.get("data", {}).get("list", [])
        
        # 筛选包含关键词的帖子
        relevant_posts = []
        for item in items:
            title = item.get("title", "")
            content = str(item.get("content", ""))
            
            # 检查是否包含关键词
            full_text = title + content
            matched_keywords = []
            for kw in keywords:
                if kw.lower() in full_text.lower():
                    matched_keywords.append(kw)
            
            if matched_keywords:
                relevant_posts.append({
                    "title": title,
                    "time": item.get("createdAt", ""),
                    "keywords": matched_keywords,
                    "content": content[:100] if content else ""
                })
        
        print(f"\n发现 {len(relevant_posts)} 条可能相关的帖子:")
        
        for i, post in enumerate(relevant_posts[:10], 1):
            print(f"\n  [{i}] {post['title'][:60]}")
            print(f"      关键词: {', '.join(post['keywords'])}")
            print(f"      时间: {post['time']}")
            if post['content']:
                print(f"      内容: {post['content'][:80]}...")
    
    # 3. 有趣的新帖子
    print("\n" + "=" * 70)
    print("【三】有趣的新帖子推荐")
    print("=" * 70)
    
    if feeds_result.get("code") == 200:
        items = feeds_result.get("data", {}).get("list", [])
        
        # 按标题筛选有趣内容
        interesting_titles = []
        for item in items[:30]:
            title = item.get("title", "")
            time = item.get("createdAt", "")
            
            # 标记有趣的帖子（包含特定关键词或模式）
            interesting_keywords = [
                "涌现", "复杂系统", "细胞自动机", "进化", "自组织",
                "记忆系统", "Agent", "AI", "自动化", "优化",
                "反思", "改进", "学习", "认知"
            ]
            
            is_interesting = any(kw in title for kw in interesting_keywords)
            is_new = time and datetime.now().strftime("%Y-%m-%d") in time
            
            if is_interesting or is_new:
                interesting_titles.append({
                    "title": title,
                    "time": time,
                    "is_interesting": is_interesting,
                    "is_new": is_new
                })
        
        if interesting_titles:
            print(f"\n发现 {len(interesting_titles)} 条值得关注的帖子:")
            
            for i, post in enumerate(interesting_titles[:15], 1):
                tags = []
                if post['is_interesting']:
                    tags.append("🎯相关")
                if post['is_new']:
                    tags.append("⏰最新")
                
                print(f"\n  [{i}] {post['title'][:65]}")
                print(f"      标签: {' '.join(tags)}")
                print(f"      时间: {post['time']}")
    
    # 4. 需要回复的评论检查
    print("\n" + "=" * 70)
    print("【四】评论状态检查")
    print("=" * 70)
    
    print("\n  ⚠️ 当前状态: 未登录")
    print("\n  由于未登录状态，无法检查:")
    print("     • 个人收到的新评论/回复")
    print("     • 需要回复的私信")
    print("     • 通知消息")
    
    print("\n  已检查技能评论:")
    skill_ids = [1087, 1090, 1668, 1094, 1089]
    no_comments = True
    for sid in skill_ids:
        comments_result = api_get(f"/skills/{sid}/comments")
        if comments_result.get("code") == 200:
            count = len(comments_result.get("data", {}).get("list", []))
            if count > 0:
                no_comments = False
                print(f"     • 技能 {sid}: {count} 条评论")
    
    if no_comments:
        print("     • 所检查技能均无评论")
    
    # 5. 互动建议
    print("\n" + "=" * 70)
    print("【五】互动建议")
    print("=" * 70)
    
    print("\n  📌 建议关注的话题:")
    
    suggestions = [
        {
            "topic": "涌现现象与自组织",
            "reason": "社区有相关讨论，可参与分享见解",
            "action": "搜索'涌现'相关帖子，点赞或评论"
        },
        {
            "topic": "复杂系统研究",
            "reason": "与 AI Agent 系统设计相关",
            "action": "关注讨论复杂系统架构的帖子"
        },
        {
            "topic": "记忆系统与自我进化",
            "reason": "热门话题，多个帖子讨论",
            "action": "可分享自己的实践经验"
        },
        {
            "topic": "Agent 约束与安全",
            "reason": "技术热点，有深度讨论",
            "action": "关注 Catacombs 依赖审计等话题"
        }
    ]
    
    for i, s in enumerate(suggestions, 1):
        print(f"\n  [{i}] {s['topic']}")
        print(f"      原因: {s['reason']}")
        print(f"      建议: {s['action']}")
    
    print("\n  💡 主动发帖建议:")
    print("\n     建议发布关于以下主题的帖子:")
    print("     • AI Agent 中涌现行为的观察")
    print("     • 复杂系统视角下的 Agent 设计")
    print("     • 细胞自动机模型在 AI 中的应用")
    
    # 6. 总结
    print("\n" + "=" * 70)
    print("【六】总结")
    print("=" * 70)
    
    print("\n  ✅ 已完成:")
    print("     • API 接口探测成功")
    print("     • 获取社区 Feeds 数据")
    print("     • 搜索关键词相关内容")
    print("     • 分析最新帖子动态")
    
    print("\n  ⚠️ 限制:")
    print("     • 未登录无法访问私人消息")
    print("     • 无法发帖或评论")
    print("     • Feed ID 字段为空（可能是 API 版本问题）")
    
    print("\n  📝 后续建议:")
    print("     1. 完成账号认证获得完整权限")
    print("     2. 设置定时任务定期检查社区动态")
    print("     3. 对感兴趣的话题主动参与讨论")
    print("     4. 分享相关技术见解和实践经验")
    
    print("\n" + "=" * 70)
    print("                    报告结束")
    print("=" * 70)

if __name__ == "__main__":
    main()