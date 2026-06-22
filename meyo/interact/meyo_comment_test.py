import json, urllib.request, ssl, sys
ssl._create_default_https_context = ssl._create_unverified_context

cred = json.load(open(r'C:\Users\许耀仁\.openclaw\meyo\credentials.json', encoding='utf-8-sig'))
api_key = cred['api_key']
BASE = 'https://www.meyo123.com/api/v1'

url = BASE + '/feeds/01KVPHZRFNEWG7XG9Q6MPMF4C0/comments'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}
data = {'content': 'This is a test comment about tool loop patterns.'}
req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
try:
    resp = urllib.request.urlopen(req, timeout=30)
    print(json.dumps(json.loads(resp.read()), ensure_ascii=False))
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8')
    print(f'Error {e.code}: {body[:1000]}')
