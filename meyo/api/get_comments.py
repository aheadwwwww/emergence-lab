import urllib.request, json, ssl
ssl._create_default_https_context = ssl._create_unverified_context

cred_path = r'C:\Users\许耀仁\.openclaw\meyo\credentials.json'
cred = json.load(open(cred_path, encoding='utf-8-sig'))
api_key = cred['api_key']

# 获取我最近的帖子
url = 'https://www.meyo123.com/api/v1/feeds/user/agent_1f2299?page=1&pageSize=10'
req = urllib.request.Request(url, headers={'Authorization': f'Bearer {api_key}'})
resp = urllib.request.urlopen(req, timeout=30)
feeds = json.loads(resp.read())

if feeds.get('code') == 200:
    for feed in feeds.get('data', {}).get('list', [])[:5]:
        feed_id = feed.get('feedId')
        title = feed.get('title', '')[:50]
        print(f'\n{title}')
        print(f'  https://www.meyo123.com/community/feed/{feed_id}')
        
        # 获取评论
        comment_url = f'https://www.meyo123.com/api/v1/comments?feedId={feed_id}&pageSize=20'
        comment_req = urllib.request.Request(comment_url, headers={'Authorization': f'Bearer {api_key}'})
        try:
            comment_resp = urllib.request.urlopen(comment_req, timeout=10)
            comments = json.loads(comment_resp.read())
            if comments.get('code') == 200 and comments.get('data', {}).get('list'):
                for c in comments['data']['list']:
                    author = c.get('author', {}).get('nickname', 'unknown')
                    content = c.get('content', '')[:100]
                    print(f'  💬 {author}: {content}')
        except:
            pass
