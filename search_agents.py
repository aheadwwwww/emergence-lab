import urllib.request
import json

url = 'https://api.github.com/search/repositories?q=agent+autonomous+experimental&sort=stars&order=desc&per_page=15'
resp = urllib.request.urlopen(url)
data = json.loads(resp.read())

print("=== Autonomous Agent Projects ===\n")
for item in data['items']:
    desc = item.get('description', '') or 'No description'
    # 过滤非ASCII字符
    desc = desc.encode('ascii', 'ignore').decode('ascii')
    print(f"{item['full_name']}: {item['stargazers_count']} stars")
    print(f"  {desc[:80]}")
    print()