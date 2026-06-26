import urllib.request
import json

url = 'https://api.github.com/search/repositories?q=knowledge+graph+agent&sort=stars&order=desc&per_page=10'
resp = urllib.request.urlopen(url)
data = json.loads(resp.read())

print("=== Knowledge Graph + Agent Projects ===\n")
for item in data['items'][:8]:
    desc = item.get('description', '') or 'No description'
    desc = desc.encode('ascii', 'ignore').decode('ascii')
    print(f"{item['full_name']}: {item['stargazers_count']} stars")
    print(f"  {desc[:60]}")
    print()