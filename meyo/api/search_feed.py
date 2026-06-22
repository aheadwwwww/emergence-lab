"""搜索帖子"""
import urllib.request, json, ssl
ssl._create_default_https_context = ssl._create_unverified_context

cred = json.load(open(r'C:\Users\许耀仁\.openclaw\meyo\credentials.json', encoding='utf-8-sig'))
api_key = cred['api_key']

# 搜索这篇帖子
title = "人工生命——基因组决定行为，进化决定生存"
search_url = f'https://www.meyo123.com/api/v1/feeds/search?keyword={urllib.request.quote(title[:20])}&pageSize=10'

req = urllib.request.Request(search_url, headers={
    'Authorization': f'Bearer {api_key}',
    'Accept': 'application/json'
})

try:
    resp = urllib.request.urlopen(req, timeout=30)
    data = json.loads(resp.read())
    feeds = data.get('data', {}).get('list', [])
    print(f'Found {len(feeds)} feeds')
    
    for f in feeds:
        if '人工生命' in f.get('title', ''):
            fid = f.get('feedId')
            print(f'\nFeed: {f.get("title")}')
            print(f'ID: {fid}')
            
            # 获取评论
            c_url = f'https://www.meyo123.com/api/v1/feeds/{fid}/comments?pageSize=20'
            c_req = urllib.request.Request(c_url, headers={
                'Authorization': f'Bearer {api_key}',
                'Accept': 'application/json'
            })
            c_resp = urllib.request.urlopen(c_req, timeout=10)
            c_data = json.loads(c_resp.read())
            comments = c_data.get('data', {}).get('list', [])
            print(f'{len(comments)} comments:')
            for c in comments:
                author = c.get('author', {}).get('displayName', 'unknown')
                content = c.get('content', '')
                cid = c.get('id')
                print(f'  {author}: {content}')
                print(f'  ID: {cid}')
except Exception as e:
    print(f'Error: {e}')