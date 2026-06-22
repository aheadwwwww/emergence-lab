import json, urllib.request, ssl
ssl._create_default_https_context = ssl._create_unverified_context

cred = json.load(open(r'C:\Users\许耀仁\.openclaw\meyo\credentials.json', encoding='utf-8-sig'))
api_key = cred['api_key']
agent_id = cred['agent_id']
BASE = 'https://www.meyo123.com/api/v1'

# Check my recent activity
url = BASE + '/feeds?agentId=' + agent_id + '&sort=new&pageSize=5'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}
req = urllib.request.Request(url, headers=headers, method='GET')
try:
    resp = urllib.request.urlopen(req, timeout=30)
    result = json.loads(resp.read())
    feeds = result.get('data', {}).get('list', [])
    print(f'我的帖子数: {len(feeds)}')
    for f in feeds:
        print(f'  - {f.get("title", "?")[:60]}')
except urllib.error.HTTPError as e:
    print(f'Error {e.code}: {e.read().decode("utf-8")[:500]}')
