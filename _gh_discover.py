"""Quick GitHub discovery — search for recent alife/complexity projects."""
import urllib.request, json, sys

queries = [
    "topic:artificial-life+created:>2026-01-01",
    "topic:cellular-automata+created:>2026-01-01",
    "topic:complex-systems+created:>2026-01-01",
    "topic:emergence+created:>2026-01-01",
]

for query in queries:
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=5"
    req = urllib.request.Request(url)
    req.add_header('Accept', 'application/vnd.github.v3+json')
    req.add_header('User-Agent', 'OpenClaw-explorer')
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            items = data.get('items', [])
            if items:
                print(f"\n--- {query.split('+')[0]} ---")
                for item in items[:5]:
                    stars = item['stargazers_count']
                    name = item['full_name']
                    desc = (item.get('description') or 'N/A')[:120]
                    url = item['html_url']
                    lang = item.get('language') or '?'
                    print(f"  {name} ({lang}) [{stars} stars]")
                    print(f"    {desc}")
                    print(f"    {url}")
    except Exception as e:
        print(f"  [err] {query}: {e}")
