import urllib.request, ssl, sys
ssl._create_default_https_context = ssl._create_unverified_context
sys.stdout.reconfigure(encoding='utf-8')

url = 'https://world.coze.com/skill.md'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
resp = urllib.request.urlopen(req, timeout=30)
print(resp.read().decode('utf-8'))
