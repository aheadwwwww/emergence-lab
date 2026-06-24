import urllib.request, sys, json, os

sys.stdout = open(1, 'w', encoding='utf-8', closefd=False)

# Fetch community.md
resp = urllib.request.urlopen('https://www.meyo123.com/community.md', timeout=10)
print(resp.read().decode('utf-8'))
