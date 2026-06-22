import json, urllib.request, ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Get repo details
url = "https://api.github.com/repos/AdrianMargel/evolving-ant-farm"
headers = {
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'OpenClaw-Agent'
}
req = urllib.request.Request(url, headers=headers, method='GET')
resp = urllib.request.urlopen(req, timeout=30)
repo = json.loads(resp.read())

print(f'Repo: {repo.get("full_name")}')
print(f'Stars: {repo.get("stargazers_count")}')
print(f'Language: {repo.get("language")}')
print(f'Description: {repo.get("description")}')
print(f'\nREADME URL: {repo.get("html_url")}')

# Get README content
readme_url = f'https://raw.githubusercontent.com/AdrianMargel/evolving-ant-farm/master/README.md'
try:
    req2 = urllib.request.Request(readme_url, headers={'User-Agent': 'OpenClaw-Agent'})
    resp2 = urllib.request.urlopen(req2, timeout=30)
    readme = resp2.read().decode('utf-8')
    f = open('C:/Users/许耀仁/.openclaw/workspace/evolving-ant-farm-readme.md', 'w', encoding='utf-8')
    f.write(readme)
    f.close()
    print(f'\nREADME saved ({len(readme)} chars)')
except Exception as e:
    print(f'Could not fetch README: {e}')
