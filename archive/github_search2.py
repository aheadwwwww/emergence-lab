import json, urllib.request, ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Try different search terms
queries = [
    "cellular automata",
    "langton ant",
    "game of life simulation",
    "boids flocking"
]

headers = {
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'OpenClaw-Agent'
}

all_repos = []
for q in queries:
    url = f"https://api.github.com/search/repositories?q={q.replace(' ', '+')}&sort=stars&order=desc&per_page=3"
    req = urllib.request.Request(url, headers=headers, method='GET')
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        repos = result.get('items', [])
        for r in repos:
            name = r.get('full_name', '?')
            if name not in [x[0] for x in all_repos]:
                all_repos.append((
                    name,
                    r.get('description', '')[:100] if r.get('description') else '',
                    r.get('stargazers_count', 0),
                    r.get('language', '?'),
                    r.get('html_url', '?')
                ))
    except Exception as e:
        pass

print(f'Found {len(all_repos)} unique repos:\n')
for name, desc, stars, lang, url in all_repos[:10]:
    print(f'{name} ({stars} stars, {lang})')
    print(f'  {desc}')
    print(f'  {url}\n')
