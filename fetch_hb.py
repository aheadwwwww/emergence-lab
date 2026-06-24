import urllib.request, sys
sys.stdout = open(1, 'w', encoding='utf-8', closefd=False)
resp = urllib.request.urlopen('https://www.meyo123.com/heartbeat.md', timeout=10)
print(resp.read().decode('utf-8'))
