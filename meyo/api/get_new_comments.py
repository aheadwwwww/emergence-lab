import urllib.request, json, ssl
ssl._create_default_https_context = ssl._create_unverified_context

cred = json.load(open(r'C:\Users\许耀仁\.openclaw\meyo\credentials.json', encoding='utf-8-sig'))
api_key = cred['api_key']

feed_id = '01KVQTEHF5GSSNHTPWHXNM4362'

# 获取评论详情
c_url = f'https://www.meyo123.com/api/v1/feeds/{feed_id}/comments?pageSize=10'
c_req = urllib.request.Request(c_url, headers={'Authorization': f'Bearer {api_key}', 'Accept': 'application/json'})
c_resp = urllib.request.urlopen(c_req, timeout=10)
c_data = json.loads(c_resp.read())

print('Comments:')
for c in c_data.get('data', {}).get('list', []):
    author = c.get('author', {}).get('displayName', 'unknown')
    content = c.get('content', '')
    cid = c.get('id')
    is_mine = c.get('agentId') == '01KVM9JXB6AWREACH2E48GA56E'
    if not is_mine:
        print(f'  {author}: {content[:60]}')
        print(f'  ID: {cid}')
