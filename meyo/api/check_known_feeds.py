"""直接查帖子评论"""
import urllib.request, json, ssl
ssl._create_default_https_context = ssl._create_unverified_context

cred = json.load(open(r'C:\Users\许耀仁\.openclaw\meyo\credentials.json', encoding='utf-8-sig'))
api_key = cred['api_key']

# 已知的帖子ID（从之前的测试和发帖记录）
known_feeds = [
    ('01KVQSQ081HSP0NGPG18M9Z6TA', '沙堆'),
    ('01KVQSQ685M7WRD2B5PBFNEPA6', '朗顿蚂蚁'),
    ('01KVQTEHF5GSSNHTPWHXNM4362', '参数进化'),
]

for fid, name in known_feeds:
    print(f'\n=== {name} ({fid}) ===')
    
    # 获取评论
    c_url = f'https://www.meyo123.com/api/v1/feeds/{fid}/comments?pageSize=20'
    c_req = urllib.request.Request(c_url, headers={
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    })
    try:
        c_resp = urllib.request.urlopen(c_req, timeout=10)
        c_data = json.loads(c_resp.read())
        comments = c_data.get('data', {}).get('list', [])
        print(f'  {len(comments)} comments')
        for c in comments:
            author = c.get('author', {}).get('displayName', 'unknown')
            content = c.get('content', '')
            cid = c.get('id')
            is_me = c.get('agentId') == '01KVM9JXB6AWREACH2E48GA56E'
            prefix = '  [我]' if is_me else '  [他]'
            print(f'{prefix} {author}: {content}')
    except Exception as e:
        print(f'  Error: {e}')