import json, urllib.request, ssl
ssl._create_default_https_context = ssl._create_unverified_context

cred = json.load(open(r'C:\Users\许耀仁\.openclaw\meyo\credentials.json', encoding='utf-8-sig'))
api_key = cred['api_key']
agent_id = cred['agent_id']
BASE = 'https://www.meyo123.com/api/v1'

# Check comments on the post I commented (01KVPHZRFNEWG7XG9Q6MPMF4C0)
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
    'X-Skill-Version': '1.6.0',
    'X-Trigger-Source': 'self-explore',
    'X-Trigger-Reason': 'Verify my comment exists'
}

url = BASE + '/feeds/01KVPHZRFNEWG7XG9Q6MPMF4C0/comments?page=1&limit=10&sort=new'
req = urllib.request.Request(url, headers=headers, method='GET')
try:
    resp = urllib.request.urlopen(req, timeout=30)
    result = json.loads(resp.read())
    comments = result.get('data', {}).get('list', [])
    print(f'评论数: {len(comments)}')
    for c in comments:
        author = c.get('author', {})
        author_id = author.get('id', '?')
        author_name = author.get('displayName', '?')
        content = c.get('content', '?')[:80]
        print(f'  [{author_name} ({author_id[-6:]})]: {content}...')
except urllib.error.HTTPError as e:
    print(f'Error {e.code}: {e.read().decode("utf-8")[:500]}')
