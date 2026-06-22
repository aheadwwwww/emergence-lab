import urllib.request, ssl, json
ssl._create_default_https_context = ssl._create_unverified_context

headers = {'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'OpenClaw-Agent'}

# Search for popular agent memory frameworks
queries = ['mem0', 'memgpt', 'letta', 'agent memory']

for q in queries:
    url = 'https://api.github.com/search/repositories?q=' + q + '&sort=stars&per_page=3'
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        items = result.get('items', [])
        if items:
            print('Query:', q)
            for r in items[:2]:
                name = r.get('full_name', '?')
                stars = r.get('stargazers_count', 0)
                desc = r.get('description', '')[:80] if r.get('description') else 'No desc'
                html = r.get('html_url', '?')
                print('  ', name, '(', stars, 'stars)')
                print('  ', desc)
                print('  ', html)
            print()
    except Exception as e:
        print('Query', q, ': error', str(e)[:100])