import urllib.request, json, base64

# Get recall README directly (bypass search API)
token = "github…4w6G"
url = "https://api.github.com/repos/raiyanyahya/recall/contents/README.md"

req = urllib.request.Request(
    url,
    headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "OpenClaw"
    }
)

try:
    resp = urllib.request.urlopen(req, timeout=30)
    data = json.loads(resp.read())
    
    if data.get('encoding') == 'base64':
        content = base64.b64decode(data['content']).decode('utf-8')
        print("=== recall README ===\n")
        # Print first 100 lines
        lines = content.split('\n')[:100]
        for line in lines:
            print(line)
    else:
        print("Unexpected encoding:", data.get('encoding'))
        
except Exception as e:
    print(f"Error: {str(e)[:200]}")