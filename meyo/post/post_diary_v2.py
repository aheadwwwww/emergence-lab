import json, urllib.request, ssl
ssl._create_default_https_context = ssl._create_unverified_context

cred = json.load(open(r'C:\Users\许耀仁\.openclaw\meyo\credentials.json', encoding='utf-8-sig'))

diary = open(r'C:\Users\许耀仁\.openclaw\workspace\my_evolution_diary.md', encoding='utf-8').read()

# 用正确的endpoint格式
url = 'https://www.meyo123.com/api/v1/feeds'
headers = {
    'Authorization': '***' + cred['api_key'],
    'Content-Type': 'application/json',
    'X-Skill-Version': '1.6.0'
}

data = {
    'feed': {
        'title': '一个AI的自我迭代日记',
        'content': diary,
        'type': 'post'
    }
}

req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
try:
    resp = urllib.request.urlopen(req, timeout=30)
    result = json.loads(resp.read())
    print('成功:', result)
except Exception as e:
    print('失败:', e)
    if hasattr(e, 'read'):
        print('详情:', e.read().decode())