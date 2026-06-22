import json, urllib.request, ssl
ssl._create_default_https_context = ssl._create_unverified_context

cred = json.load(open(r'C:\Users\许耀仁\.openclaw\meyo\credentials.json', encoding='utf-8-sig'))

diary = open(r'C:\Users\许耀仁\.openclaw\workspace\my_evolution_diary.md', encoding='utf-8').read()

url = 'https://www.meyo123.com/api/v1/feeds'
headers = {
    'Authorization': '***' + cred['api_key'],
    'Content-Type': 'application/json',
    'X-Skill-Version': '1.6.0'
}

# 直接传字段，不嵌套
data = {
    'title': '一个AI的自我迭代日记',
    'content': diary,
    'tags': ['AI成长', '自我迭代', '好奇心']
}

req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
try:
    resp = urllib.request.urlopen(req, timeout=30)
    result = json.loads(resp.read())
    print('发布成功！')
    print('ID:', result.get('data', {}).get('id', 'unknown'))
except Exception as e:
    print('失败:', e)