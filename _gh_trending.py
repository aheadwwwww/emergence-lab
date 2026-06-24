import urllib.request, json

for repo in ['ikkeseb/vivarium', 'xcontcom/initial-state-evolution']:
    url = f'https://api.github.com/repos/{repo}'
    req = urllib.request.Request(url, headers={'User-Agent': 'openclaw-heartbeat', 'Accept': 'application/vnd.github.v3+json'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
    print(f'=== {repo} ===')
    print(f"Stars: {data['stargazers_count']}, Forks: {data['forks_count']}")
    print(f"Language: {data['language']}")
    print(f"Topics: {data.get('topics', [])}")
    print(f"Desc: {data['description']}")
    print(f"Updated: {data['updated_at']}")
    lic = data.get('license')
    print(f"License: {lic['spdx_id'] if lic else 'N/A'}")
    # Get README
    readme_url = f'https://api.github.com/repos/{repo}/readme'
    req2 = urllib.request.Request(readme_url, headers={'User-Agent': 'openclaw-heartbeat', 'Accept': 'application/vnd.github.v3.raw'})
    with urllib.request.urlopen(req2, timeout=15) as resp2:
        readme = resp2.read().decode('utf-8', errors='replace')[:800]
    print(f"README (first 800 chars):")
    print(readme)
    print()
