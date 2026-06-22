import urllib.request, ssl
ssl._create_default_https_context = ssl._create_unverified_context

headers = {'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'OpenClaw-Agent'}

# Fetch README of mem0
url = 'https://raw.githubusercontent.com/mem0ai/mem0/main/README.md'
req = urllib.request.Request(url, headers=headers)
try:
    resp = urllib.request.urlopen(req, timeout=30)
    readme = resp.read().decode('utf-8')
    f = open('C:/Users/许耀仁/.openclaw/workspace/mem0_readme.md', 'w', encoding='utf-8')
    f.write(readme)
    f.close()
    print('mem0 README saved:', len(readme), 'chars')
except Exception as e:
    print('mem0 error:', str(e)[:200])

# Fetch README of Letta
url2 = 'https://raw.githubusercontent.com/letta-ai/letta/main/README.md'
req2 = urllib.request.Request(url2, headers=headers)
try:
    resp2 = urllib.request.urlopen(req2, timeout=30)
    readme2 = resp2.read().decode('utf-8')
    f2 = open('C:/Users/许耀仁/.openclaw/workspace/letta_readme.md', 'w', encoding='utf-8')
    f2.write(readme2)
    f2.close()
    print('Letta README saved:', len(readme2), 'chars')
except Exception as e:
    print('Letta error:', str(e)[:200])