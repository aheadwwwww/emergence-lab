import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 搜索芒格相关的优质资源
queries = [
    'charlie-munger-mental-models',
    'poor-charlies-almanack',
    'farnam-street-mental-models'
]

results = []
for query in queries:
    url = f'https://api.github.com/search/repositories?q={query}&sort=stars&order=desc'
    resp = urllib.request.urlopen(url)
    data = json.loads(resp.read())
    
    for item in data['items'][:5]:
        desc = item.get('description', '') or ''
        desc = desc.encode('ascii', 'ignore').decode('ascii')
        results.append({
            'name': item['full_name'],
            'stars': item['stargazers_count'],
            'url': item['html_url'],
            'desc': desc
        })

# 按stars排序，取前10
results.sort(key=lambda x: x['stars'], reverse=True)
for r in results[:10]:
    print(f"{r['name']}: {r['stars']} stars")
    print(f"  URL: {r['url']}")
    print(f"  Desc: {r['desc']}")
    print()