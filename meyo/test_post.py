"""Test meyo feed API"""
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
    try:
        resp = urllib.request.urlopen(req, timeout=20)
        return resp.status, json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        return e.code, body
    except Exception as e:
        return 0, str(e)

# Test simple post
post = {
    "title": "测试帖",
    "content": "这是一个测试",
    "tags": ["测试"],
}
code, resp = api("POST", "/feeds", post)
print(f"POST /feeds: {code}")
print(resp)

# Try different endpoint
code, resp = api("POST", "/community/feeds", post)
print(f"\nPOST /community/feeds: {code}")
print(resp)
