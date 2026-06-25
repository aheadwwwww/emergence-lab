import urllib.request, json

# Search good first issues in popular repos
repos = [
    "microsoft/vscode",
    "facebook/react", 
    "vercel/next.js",
    "python/cpython",
    "tensorflow/tensorflow",
]

print("=== Good First Issues (真实待解决问题) ===\n")

for repo in repos:
    url = f"https://api.github.com/repos/{repo}/issues?labels=good-first-issue&state=open&per_page=3"
    
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
        
        if data:
            print(f"--- {repo} ---")
            for item in data[:3]:
                title = item.get('title', 'N/A')[:80]
                number = item.get('number', 0)
                url_path = item.get('html_url', '')
                print(f"  #{number}: {title}")
            print()
        
    except Exception as e:
        pass