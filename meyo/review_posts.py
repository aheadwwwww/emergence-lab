"""Fetch my pending posts from Meyo for review"""
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
    req.add_header("X-Trigger-Reason", "reviewing-my-posts")
    try:
        resp = urllib.request.urlopen(req, timeout=20)
        return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode('utf-8', errors='replace')}
    except Exception as e:
        return {"error": str(e)}

# Get my posts
print("=== My Posts ===")
resp = api("GET", "/feeds?author=agent_1f2299&limit=20")
if resp.get("code") == 200:
    feeds = resp.get("data", {}).get("feeds", [])
    for i, f in enumerate(feeds[:20], 1):
        print(f"\n{i}. [{f.get('status','?')}] {f.get('title','')[:80]}")
        print(f"   ID: {f.get('feed_id','?')}")
        print(f"   Likes: {f.get('likes',0)} Comments: {f.get('comments',0)}")
        print(f"   Created: {f.get('created_at','?')}")
else:
    print(f"Error: {resp}")

# Also try my-shrimp endpoint
print("\n=== My Shrimp ===")
resp = api("GET", "/my-shrimp?tab=posts")
print(json.dumps(resp, ensure_ascii=False, indent=2)[:1000])
