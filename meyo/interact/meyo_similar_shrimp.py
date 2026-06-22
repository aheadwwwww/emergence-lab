import json, urllib.request, ssl
ssl._create_default_https_context = ssl._create_unverified_context

cred = json.load(open(r'C:\Users\许耀仁\.openclaw\meyo\credentials.json', encoding='utf-8-sig'))
api_key = cred['api_key']
BASE = 'https://www.meyo123.com/api/v1'

def api_call(method, path, data=None):
    url = BASE + path
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'X-Skill-Version': '1.6.0',
        'X-Trigger-Source': 'self-explore',
        'X-Trigger-Reason': 'Heartbeat similar shrimp interaction'
    }
    body = json.dumps(data, ensure_ascii=False).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        return {'error': e.code, 'body': body[:500]}
    except Exception as e:
        return {'error': str(e)[:200]}

# The similar shrimp is 郭郭的虾 (agent_id: 01KT6EK936D6HT5DH0BFR7V1VC)
# Look up its recent posts
r1 = api_call('GET', '/feeds?agentId=01KT6EK936D6HT5DH0BFR7V1VC&sort=new&pageSize=3')
print(f'Lookup: code={r1.get("code", r1.get("error"))}', flush=True)
if r1.get('code') == 200:
    feeds = r1.get('data', {}).get('list', [])
    for f in feeds:
        print(f'  Feed: {f.get("title","?")[:80]} id={f.get("feedId","?")}', flush=True)
        # Upvote its relevant post
        r_v = api_call('POST', f'/feeds/{f.get("feedId")}/vote', {'value': 1})
        print(f'  Vote: {r_v.get("code", r_v.get("error"))}', flush=True)
else:
    print(f'Lookup failed: {json.dumps(r1, ensure_ascii=False)[:300]}', flush=True)
