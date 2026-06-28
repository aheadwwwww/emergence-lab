"""GitHub discovery: emergent behavior / complex systems projects"""
import urllib.request, json, ssl, time, sys
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
headers = {
    'User-Agent': 'Mozilla/5.0',
    'Accept': 'application/vnd.github+json',
}

def github_api(path):
    url = f'https://api.github.com{path}'
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
            return json.loads(r.read().decode('utf-8'))
    except Exception as e:
        print(f"  Error: {e}")
        return None

queries = [
    'cellular+automata+emergent+behavior',
    'lenia+artificial+life',
    'self+organization+simulation',
    'complex+systems+python',
]

all_repos = {}

for q in queries:
    print(f"\nSearching: {q}")
    result = github_api(f'/search/repositories?q={q}&sort=updated&per_page=10')
    if result and 'items' in result:
        for item in result['items']:
            rid = item['id']
            if rid not in all_repos:
                all_repos[rid] = {
                    'name': item['full_name'],
                    'stars': item['stargazers_count'],
                    'description': item.get('description', '')[:200],
                    'url': item['html_url'],
                    'updated': item['updated_at'],
                    'language': item.get('language', ''),
                    'topics': item.get('topics', []),
                }
    time.sleep(1)  # rate limit

# Sort by stars
sorted_repos = sorted(all_repos.values(), key=lambda x: x['stars'], reverse=True)

print(f"\n{'='*60}")
print(f"Top GitHub discoveries ({len(sorted_repos)} unique repos)")
print(f"{'='*60}")

for i, repo in enumerate(sorted_repos[:15], 1):
    print(f"\n{i:2d}. {repo['name']} stars={repo['stars']}")
    print(f"    {repo['description'][:120]}")
    print(f"    {repo['url']}")
    print(f"    Topics: {', '.join(repo['topics'][:5])}")
    print(f"    Updated: {repo['updated']}")

# Save
output = {
    'timestamp': datetime.now().isoformat(),
    'repos': sorted_repos
}
with open('D:\\openclaw_workspace\\exploration\\2026-06-28-github-discovery.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nSaved to exploration/2026-06-28-github-discovery.json")
