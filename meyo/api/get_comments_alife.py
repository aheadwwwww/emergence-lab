import urllib.request, json, ssl
ssl._create_default_https_context = ssl._create_unverified_context

cred = json.load(open(r'C:\Users\许耀仁\.openclaw\meyo\credentials.json', encoding='utf-8-sig'))
api_key = cred['api_key']

fid = '01KVQAVZR19V6C0G7YEN1J5M5Z'

# 获取评论
c_url = f'https://www.meyo123.com/api/v1/feeds/{fid}/comments?pageSize=20'
c_req = urllib.request.Request(c_url, headers={'Authorization': f'Bearer {api_key}', 'Accept': 'application/json'})
c_resp = urllib.request.urlopen(c_req, timeout=10)
c_data = json.loads(c_resp.read())
comments = c_data.get('data', {}).get('list', [])

print(f'Comments: {len(comments)}')
for c in comments:
    author = c.get('author', {}).get('displayName', 'unknown')
    content = c.get('content', '')
    cid = c.get('id')
    is_mine = c.get('agentId') == '01KVM9JXB6AWREACH2E48GA56E'
    who = 'ME' if is_mine else 'THEM'
    print(f'[{who}] {author}: {content}')
    print(f'  ID: {cid}')
