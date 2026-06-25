import urllib.request, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Search for programmable emergence, emergence framework
queries = [
    'emergence framework',
    'programmable emergence',
    'emergence simulation tool',
    'multi-agent emergence platform',
]

for q in queries:
    url = 'https://api.github.com/search/repositories?q=' + q.replace(' ', '+') + '&sort=stars&per_page=5'
    req = urllib.request.Request(url, headers={'User-Agent': 'openclaw'})
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        print('=== ' + q + ' ===')
        for r in data.get('items', [])[:5]:
            name = r['full_name']
            stars = r['stargazers_count']
            desc = (r.get('description') or 'N/A')[:80]
            print(f"{name} | stars={stars} | {desc}")
        print()
    except Exception as e:
        print(f'{q}: Error - {str(e)[:50]}')