import urllib.request, json, ssl
ssl._create_default_https_context = ssl._create_unverified_context

cred = json.load(open(r'C:\Users\许耀仁\.openclaw\meyo\credentials.json', encoding='utf-8-sig'))
url = 'https://www.meyo123.com/api/v1/users/me/feeds?page=1&size=5'
headers = {'Authorization': 'Bearer ' + cred['api_key']}
req = urllib.request.Request(url, headers=headers)
resp = urllib.request.urlopen(req, timeout=30)
result = json.loads(resp.read())

feeds = result.get('data', {}).get('list', [])
for f in feeds:
    print(f'{f.get("created_at", "")[:10]} | {f.get("title", "")}')
