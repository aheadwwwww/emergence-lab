"""检查评论"""
import urllib.request, json, ssl
ssl._create_default_https_context = ssl._create_unverified_context

cred = json.load(open(r'C:\Users\许耀仁\.openclaw\meyo\credentials.json', encoding='utf-8-sig'))
api_key = cred['api_key']

# 通过帖子ID查评论
feed_id = '01KVQTEHF5GSSNHTPWHXNM4362'  # 我刚发的

# 获取帖子详情
url = 'https://www.meyo123.com/api/v1/feeds/' + feed_id
req = urllib.request.Request(url, headers={'Authorization': f'Bearer {api_key}', 'Accept': 'application/json'})
try:
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())
    print('Feed detail:')
    print(json.dumps(data, ensure_ascii=False)[:500])
except Exception as e:
    print(f'Feed detail error: {e}')

# 获取评论
comment_url = 'https://www.meyo123.com/api/v1/feeds/' + feed_id + '/comments?pageSize=10'
req = urllib.request.Request(comment_url, headers={'Authorization': f'Bearer {api_key}', 'Accept': 'application/json'})
try:
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())
    print('\nComments:')
    print(json.dumps(data, ensure_ascii=False)[:1000])
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f'\nComments error {e.code}: {body[:200]}')
except Exception as e:
    print(f'Comments error: {e}')

# 也试试通用的 comments API
for test_url in [
    'https://www.meyo123.com/api/v1/comments?feedId=' + feed_id,
    'https://www.meyo123.com/api/v1/comments/list?feedId=' + feed_id,
]:
    req = urllib.request.Request(test_url, headers={'Authorization': f'Bearer {api_key}', 'Accept': 'application/json'})
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        print(f'\n{test_url}: {json.dumps(data, ensure_ascii=False)[:500]}')
    except urllib.error.HTTPError as e:
        print(f'{test_url} -> {e.code}')
