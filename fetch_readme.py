import urllib.request, ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Direct fetch README
url = 'https://raw.githubusercontent.com/AdrianMargel/evolving-ant-farm/master/README.md'
req = urllib.request.Request(url, headers={'User-Agent': 'OpenClaw-Agent'})
resp = urllib.request.urlopen(req, timeout=30)
readme = resp.read().decode('utf-8')

f = open('C:/Users/许耀仁/.openclaw/workspace/evolving-ant-farm-readme.md', 'w', encoding='utf-8')
f.write(readme)
f.close()
print(f'README saved ({len(readme)} chars)')
print(readme[:500])