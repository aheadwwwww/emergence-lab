import urllib.request, json

# Search GitHub issues with "annoying" or "frustrating" labels
url = "https://api.github.com/search/issues?q=annoying+OR+frustrating+OR+tedious+label:enhancement&sort=comments&per_page=20"

req = urllib.request.Request(
    url,
    headers={
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "OpenClaw"
    }
)

try:
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read())
    
    print(f"找到 {data['total_count']} 个相关 issue\n")
    
    for item in data.get('items', [])[:10]:
        title = item.get('title', 'N/A')[:80]
        repo = item.get('repository_url', '').replace('https://api.github.com/repos/', '')
        comments = item.get('comments', 0)
        print(f"{repo} | comments={comments}")
        print(f"  {title}")
        print()
        
except Exception as e:
    print(f"Error: {str(e)[:100]}")