import urllib.request
import json
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

# Fetch repo info
url = 'https://api.github.com/repos/google-research/self-organizing-systems'
req = urllib.request.Request(url, headers={'User-Agent': 'OpenClaw-Agent'})
resp = urllib.request.urlopen(req, timeout=10)
data = json.loads(resp.read().decode())

print(f"Name: {data['name']}")
print(f"Description: {data.get('description', 'N/A')}")
print(f"Stars: {data['stargazers_count']}")
print(f"Language: {data.get('language', 'N/A')}")
print(f"Updated: {data['updated_at']}")
print(f"Topics: {', '.join(data.get('topics', []))}")
print(f"\nURL: {data['html_url']}")

# Fetch README
readme_url = f"https://raw.githubusercontent.com/google-research/self-organizing-systems/master/README.md"
try:
    req = urllib.request.Request(readme_url, headers={'User-Agent': 'OpenClaw-Agent'})
    resp = urllib.request.urlopen(req, timeout=10)
    readme = resp.read().decode()
    print("\n" + "="*60)
    print("README.md:")
    print("="*60)
    print(readme[:3000])
except Exception as e:
    print(f"\nCould not fetch README: {e}")
