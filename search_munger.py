import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 搜索 mental models 相关仓库
queries = [
    'mental-models',
    'charlie-munger-almanack',
    'thinking-tools'
]

for query in queries:
    url = f'https://api.github.com/search/repositories?q={query}&sort=stars&order=desc'
    resp = urllib.request.urlopen(url)
    data = json.loads(resp.read())
    
    print(f"\n=== Query: {query} ===")
    for item in data['items'][:10]:
        desc = item.get('description', '') or ''
        desc = desc.encode('ascii', 'ignore').decode('ascii')
        print(f"{item['full_name']}: {item['stargazers_count']} stars - {desc}")