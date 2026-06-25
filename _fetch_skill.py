import urllib.request
import sys
sys.stdout.reconfigure(encoding='utf-8')

req = urllib.request.Request('https://www.meyo123.com/skill.md', headers={'User-Agent': 'openclaw'})
resp = urllib.request.urlopen(req, timeout=10)
content = resp.read().decode('utf-8')
print(content[:3000])
