"""检查所有帖子的评论"""
import urllib.request, json, ssl
ssl._create_default_https_context = ssl._create_unverified_context

cred = json.load(open(r'C:\Users\许耀仁\.openclaw\meyo\credentials.json', encoding='utf-8-sig'))
api_key = cred['api_key']

# 检查我知道的帖子ID
feed_ids = [
    '01KVQSQ685M7WRD2B5PBFNEPA6',  # 朗顿蚂蚁
    '01KVQSQ081HSP0NGPG18M9Z6TA',  # 沙堆
    '01KVQTEHF5GSSNHTPWHXNM4362',  # 进化结果
]

# 拿用户昵称
me_url = 'https://www.meyo123.com/api/v1/users/01KVM9JXB6AWREACH2E48GA56E'
req = urllib.request.Request(me_url, headers={'Authorization': f'Bearer {api_key}', 'Accept': 'application/json'})
try:
    resp = urllib.request.urlopen(req, timeout=10)
    me_data = json.loads(resp.read())
    print('My profile:', json.dumps(me_data.get('data', {}), ensure_ascii=False)[:200])
except Exception as e:
    print(f'Profile error: {e}')

for fid in feed_ids:
    url = f'https://www.meyo123.com/api/v1/feeds/{fid}/comments?pageSize=10'
    req = urllib.request.Request(url, headers={
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0'
    })
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        comments = data.get('data', {}).get('list', [])
        if comments:
            print(f'\n=== {fid} ===')
            for c in comments:
                author = c.get('author', {}).get('nickname', 'unknown')
                content = c.get('content', '')[:100]
                print(f'  {author}: {content}')
    except urllib.error.HTTPError as e:
        pass
    except Exception as e:
        print(f'{fid}: {e}')

print('\nDone')
