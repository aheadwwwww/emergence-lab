import urllib.request
import json

# 搜索更多有趣的agent项目
queries = [
    'llm-agent-framework',
    'autonomous-agent-memory',
    'agent-collaboration'
]

for query in queries:
    url = f'https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=10'
    resp = urllib.request.urlopen(url)
    data = json.loads(resp.read())
    
    print(f"\n=== Query: {query} ===\n")
    for item in data['items'][:8]:
        desc = item.get('description', '') or 'No description'
        desc = desc.encode('ascii', 'ignore').decode('ascii')
        print(f"{item['full_name']}: {item['stargazers_count']} stars")
        print(f"  {desc[:70]}")