import urllib.request, json

# Search recently created repos (past week)
url = "https://api.github.com/search/repositories?q=created:>2026-06-18&sort=stars&order=desc&per_page=30"

req = urllib.request.Request(
    url,
    headers={
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "OpenClaw"
    }
)

try:
    resp = urllib.request.urlopen(req, timeout=20)
    data = json.loads(resp.read())
    
    print(f"最近一周创建的热门仓库 (共 {data['total_count']} 个):\n")
    
    for item in data.get('items', [])[:20]:
        name = item.get('full_name', 'N/A')
        stars = item.get('stargazers_count', 0)
        desc = (item.get('description') or '无描述')[:100]
        lang = item.get('language') or '未知'
        
        print(f"{name} | {lang} | stars={stars}")
        desc_safe = desc.encode('gbk', errors='replace').decode('gbk')
        print(f"  {desc_safe}")
        print()
        
except Exception as e:
    print(f"Error: {str(e)[:200]}")