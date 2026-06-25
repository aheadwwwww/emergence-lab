import urllib.request, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

url = 'https://api.github.com/search/repositories?q=artificial+life+cellular+automata+emergence&sort=updated&order=desc&per_page=5'
req = urllib.request.Request(url, headers={'User-Agent': 'openclaw-heartbeat', 'Accept': 'application/vnd.github.v3+json'})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
    for item in data.get('items', [])[:5]:
        name = item['full_name']
        stars = item['stargazers_count']
        lang = item.get('language', 'N/A')
        desc = (item.get('description') or 'N/A')[:120]
        topics = item.get('topics', [])
        url = item['html_url']
        print(f"{name} | stars={stars} | {lang}")
        print(f"  desc: {desc}")
        print(f"  topics: {topics}")
        print(f"  url: {url}")
        print()
    print(f"Total results: {data.get('total_count', 0)}")
except Exception as e:
    print(f'Error: {e}')
