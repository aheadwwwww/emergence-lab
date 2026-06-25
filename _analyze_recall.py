import urllib.request, json

# Get recall repo info
url = "https://api.github.com/repos/raiyanyahya/recall"

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
    
    print("=== recall 项目分析 ===\n")
    print(f"名称: {data.get('full_name')}")
    print(f"Stars: {data.get('stargazers_count')}")
    print(f"语言: {data.get('language')}")
    print(f"描述: {data.get('description')}")
    print(f"URL: {data.get('html_url')}")
    print(f"\nREADME URL: {data.get('html_url')}/blob/main/README.md")
    
except Exception as e:
    print(f"Error: {str(e)[:100]}")