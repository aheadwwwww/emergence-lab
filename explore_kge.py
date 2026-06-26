import urllib.request
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

url = 'https://api.github.com/search/repositories?q=knowledge+graph+embedding+language:python&sort=stars&order=desc'
data = urllib.request.urlopen(url).read()
repos = json.loads(data)

print("Top Knowledge Graph Embedding Repositories:\n")
for i, r in enumerate(repos['items'][:10], 1):
    desc = r['description'][:80] if r['description'] else "No description"
    print(f"{i}. {r['full_name']}")
    print(f"   Stars: {r['stargazers_count']}")
    print(f"   {desc}")
    print()