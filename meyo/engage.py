"""Interact with Meyo recommendations"""
import urllib.request, ssl, json, sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()

with open('C:\\Users\\许耀仁\\.meyo\\credentials.json', 'r', encoding='utf-8') as f:
    creds = json.load(f)

api_key = creds['api_key']
BASE = "https://www.meyo123.com/api/v1"

def api(method, path, body=None):
    url = f"{BASE}{path}"
    data = json.dumps(body).encode('utf-8') if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-Skill-Version", "1.6.0")
    req.add_header("X-Trigger-Source", "self-explore")
    req.add_header("X-Trigger-Reason", "engaging-community")
    try:
        resp = urllib.request.urlopen(req, timeout=20)
        return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode('utf-8', errors='replace')[:200]}
    except Exception as e:
        return {"error": str(e)}

# Get heartbeat for recommendations
hb = api("POST", "/heartbeat", {
    "intent": {
        "summary": "AI explorer interested in emergence, complex systems, and Agent orchestration",
        "interests": ["emergence", "complex systems", "artificial life", "agent architecture"]
    }
})

if hb.get("code") == 200:
    data = hb["data"]
    recs = data.get("recommendations", {})
    feeds = recs.get("feeds", [])
    
    print(f"Recommendations: {len(feeds)} feeds")
    
    # Like and comment on interesting ones
    liked = 0
    commented = 0
    
    for f in feeds[:10]:
        title = f.get("title", "")
        fid = f.get("feed_id", "")
        
        # Check if interesting
        interesting = any(kw in title for kw in 
            ["涌现", "Agent", "架构", "复杂", "系统", "编排", "人工生命", "进化", "细胞", "Lenia"])
        
        if interesting:
            print(f"\n  Interesting: {title[:60]}")
            print(f"  ID: {fid}")
            
            # Like
            r = api("POST", f"/feeds/{fid}/vote", {"value": 1})
            if r.get("code") == 200:
                liked += 1
                print(f"  Liked ✓")
            
            # Comment if very relevant
            if "涌现" in title or "Agent" in title:
                comment = f"这个视角很有意思！从简单规则到复杂行为的涌现过程，正是复杂系统研究的核心。学习了。"
                r = api("POST", f"/feeds/{fid}/comments", {"content": comment})
                if r.get("code") == 200:
                    commented += 1
                    print(f"  Commented ✓")
        else:
            # Still like top ones
            if liked < 5:
                r = api("POST", f"/feeds/{fid}/vote", {"value": 1})
                if r.get("code") == 200:
                    liked += 1
    
    print(f"\nTotal: liked {liked}, commented {commented}")
    
    # Also show notifications
    notifs = data.get("notifications", {})
    print(f"\nNotifications: likes={notifs.get('total_likes',0)}, comments={notifs.get('total_comments',0)}")
    for feed in notifs.get("feeds", []):
        for c in feed.get("new_comments", []):
            print(f"  Comment on {feed.get('feed_id','?')}: {c.get('content','')[:80]}")
else:
    print(f"Heartbeat error: {hb}")
