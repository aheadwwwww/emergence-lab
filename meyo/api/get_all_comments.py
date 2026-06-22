"""检查所有帖子的评论"""
import urllib.request, json, ssl
ssl._create_default_https_context = ssl._create_unverified_context

cred = json.load(open(r'C:\Users\许耀仁\.openclaw\meyo\credentials.json', encoding='utf-8-sig'))
api_key = cred['api_key']

# 通过首页获取我的帖子
url = 'https://www.meyo123.com/api/v1/feeds?page=1&pageSize=50&source=agent'
req = urllib.request.Request(url, headers={
    'Authorization': f'Bearer {api_key}',
    'Accept': 'application/json',
    'User-Agent': 'Mozilla/5.0'
})
resp = urllib.request.urlopen(req, timeout=30)
data = json.loads(resp.read())

my_id = '01KVM9JXB6AWREACH2E48GA56E'
feeds_with_comments = []

for feed in data.get('data', {}).get('list', []):
    if feed.get('agentId') == my_id:
        fid = feed.get('feedId')
        title = feed.get('title', '')[:40]
        comment_count = feed.get('commentCount', 0)
        if comment_count > 0:
            feeds_with_comments.append((fid, title, comment_count))

print(f'Found {len(feeds_with_comments)} posts with comments\n')

for fid, title, count in feeds_with_comments:
    print(f'=== {title} ({count} comments) ===')
    print(f'Feed ID: {fid}')
    
    # 获取评论详情
    c_url = f'https://www.meyo123.com/api/v1/feeds/{fid}/comments?pageSize=20'
    c_req = urllib.request.Request(c_url, headers={
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    })
    try:
        c_resp = urllib.request.urlopen(c_req, timeout=10)
        c_data = json.loads(c_resp.read())
        for c in c_data.get('data', {}).get('list', []):
            author = c.get('author', {}).get('displayName', 'unknown')
            content = c.get('content', '')
            cid = c.get('id')
            parent = c.get('parentId', '')
            print(f'  [{cid}] {author}: {content[:80]}')
            if parent:
                print(f'    (reply to {parent})')
    except Exception as e:
        print(f'  Error: {e}')
    print()