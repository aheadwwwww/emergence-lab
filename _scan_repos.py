import urllib.request, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

queries = [
    'swarm intelligence emergence',
    'multi-agent coordination',
    'cellular automata life',
    'pheromone agent simulation',
]

results = []

for q in queries:
    url = 'https://api.github.com/search/repositories?q=' + q.replace(' ', '+') + '&sort=stars&per_page=3'
    req = urllib.request.Request(url, headers={'User-Agent': 'openclaw'})
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        print('=== ' + q + ' ===')
        for r in data.get('items', [])[:3]:
            name = r['full_name']
            stars = r['stargazers_count']
            desc = (r.get('description') or 'N/A')[:60]
            print(f"{name} | stars={stars} | {desc}")
            results.append({'query': q, 'repo': name, 'stars': stars, 'desc': desc})
        print()
    except Exception as e:
        print(f'{q}: Error - {str(e)[:50]}')

# Save results
with open('exploration/repo_scan_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"Saved {len(results)} repos to exploration/repo_scan_results.json")
