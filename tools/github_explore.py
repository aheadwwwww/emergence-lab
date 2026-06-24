import urllib.request, json, sys

def search_github(query, per_page=5):
    url = f'https://api.github.com/search/repositories?q={urllib.request.quote(query)}&sort=stars&order=desc&per_page={per_page}'
    headers = {
        'User-Agent': 'openclaw-explorer',
        'Accept': 'application/vnd.github.v3+json'
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        return data.get('items', [])
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return []

queries = [
    'artificial life simulation',
    'novelty search evolution',
    'lindenmayer system',
    'cellular automata creativity',
]

for query in queries:
    print(f"\n{'='*60}")
    print(f"Search: {query}")
    print('='*60)
    items = search_github(query, per_page=3)
    for item in items:
        print(f"  {item['full_name']} ({item['stargazers_count']}★)")
        print(f"    {item.get('description', 'no description')}")
        print(f"    {item['html_url']}")
    if not items:
        print("  (no results)")
