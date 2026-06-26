import urllib.request
import json

# Get PyKEEN repo info
url = 'https://api.github.com/repos/pykeen/pykeen'
data = urllib.request.urlopen(url).read()
repo = json.loads(data)

print("=== PyKEEN: Knowledge Graph Embedding Library ===\n")
print(f"Stars: {repo['stargazers_count']}")
print(f"Language: {repo['language']}")
print(f"URL: {repo['html_url']}")
print(f"\nDescription: {repo['description']}")

# Check documentation link
if repo.get('homepage'):
    print(f"\nDocumentation: {repo['homepage']}")

print("\n=== Key Features (from GitHub) ===")
topics = repo.get('topics', [])
for topic in topics[:15]:
    print(f"- {topic}")
