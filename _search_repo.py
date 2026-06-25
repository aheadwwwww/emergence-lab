import urllib.request, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

url = 'https://api.github.com/search/repositories?q=ALIFE+self-replicating&sort=stars&per_page=5'
req = urllib.request.Request(url, headers={'User-Agent': 'openclaw'})
resp = urllib.request.urlopen(req, timeout=10)
data = json.loads(resp.read())

for r in data.get('items', [])[:5]:
    desc = (r.get('description') or 'N/A')[:80]
    print(f"{r['full_name']} | stars={r['stargazers_count']} | {desc}")
