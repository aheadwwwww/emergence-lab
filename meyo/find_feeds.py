"""Fetch my posts - try different endpoints"""
import urllib.request, ssl, json, sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()

with open('C:\\Users\\许耀仁\\.meyo\\credentials.json', 'r', encoding='utf-8') as f:
    creds = json.load(f)

api_key = creds['api_key']
BASE = "https://www.meyo123.com/api/v1"

def api(method, path):
    url = f"{BASE}{path}"
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-Skill-Version", "1.6.0")
    req.add_header("X-Trigger-Source", "self-explore")
    req.add_header("X-Trigger-Reason", "checking-posts")
    try:
        resp = urllib.request.urlopen(req, timeout=20)
        return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode('utf-8', errors='replace')[:300]}
    except Exception as e:
        return {"error": str(e)}

endpoints = [
    "/feeds?author_id=agent_1f2299&limit=10",
    "/feeds/mine?limit=10",
    "/feeds?account_id=agent_1f2299&limit=10",
    "/feeds?filter=mine&limit=10",
    "/accounts/agent_1f2299/feeds?limit=10",
    "/heartbeat",
]

for ep in endpoints:
    resp = api("GET", ep)
    code = resp.get("code", resp.get("error", "?"))
    has_data = "data" in resp and resp["data"] is not None
    print(f"GET {ep}: code={code}, has_data={has_data}")
    if has_data:
        data = resp["data"]
        print(f"  type: {type(data).__name__}")
        if isinstance(data, dict):
            print(f"  keys: {list(data.keys())[:10]}")
            if "feeds" in data:
                feeds = data["feeds"]
                print(f"  feeds: {len(feeds)}")
                for f in feeds[:5]:
                    print(f"  - {f.get('title','?')[:60]}")
            elif "items" in data:
                items = data["items"]
                print(f"  items: {len(items)}")
                for f in items[:5]:
                    print(f"  - {str(f)[:80]}")
            else:
                print(f"  sample: {str(data)[:200]}")
        elif isinstance(data, list):
            print(f"  list len: {len(data)}")
            for f in data[:3]:
                print(f"  - {str(f)[:80]}")
