import urllib.request, json

# Search for tool requests, automation needs
queries = [
    "wish there was a tool",
    "need a script to",
    "automatically generate",
    " tedious manual",
]

for q in queries:
    url = f"https://api.github.com/search/issues?q={q.replace(' ', '+')}+state:open&sort=comments&per_page=5"
    
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
        
        print(f"=== '{q}' ===")
        for item in data.get('items', [])[:3]:
            title = item.get('title', 'N/A')[:100]
            url_path = item.get('html_url', '')
            print(f"  {title}")
            print(f"  {url_path}")
        print()
        
    except Exception as e:
        print(f"Error: {str(e)[:50]}")