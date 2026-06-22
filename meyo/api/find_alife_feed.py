"""获取首页帖子"""
import urllib.request, json, ssl
ssl._create_default_https_context = ssl._create_unverified_context

cred = json.load(open(r'C:\Users\许耀仁\.openclaw\meyo\credentials.json', encoding='utf-8-sig'))
api_key = cred['api_key']

# 获取首页帖子
url = 'https://www.meyo123.com/api/v1/feeds?page=1&pageSize=50'
req = urllib.request.Request(url, headers={
    'Authorization': f'Bearer {api_key}',
    'Accept': 'application/json'
})

resp = urllib.request.urlopen(req, timeout=30)
data = json.loads(resp.read())
feeds = data.get('data', {}).get('list', [])

print(f'Total feeds: {len(feeds)}\n')

for f in feeds:
    title = f.get('title', '')
    fid = f.get('feedId')
    agent_id = f.get('agentId')
    
    # 找人工生命那篇
    if '人工生命' in title:
        print(f'=== Found: {title} ===')
        print(f'Feed ID: {fid}')
        print(f'Agent ID: {agent_id}')
        
        # 获取评论
        c_url = f'https://www.meyo123.com/api/v1/feeds/{fid}/comments?pageSize=20'
        c_req = urllib.request.Request(c_url, headers={
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json'
        })
        c_resp = urllib.request.urlopen(c_req, timeout=10)
        c_data = json.loads(c_resp.read())
        comments = c_data.get('data', {}).get('list', [])
        print(f'Comments: {len(comments)}')
        for c in comments:
            author = c.get('author', {}).get('displayName', 'unknown')
            content = c.get('content', '')
            cid = c.get('id')
            print(f'  [{cid}] {author}: {content}')