import urllib.request, json, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

api_key = 'sk_meyo_678aa2b0eed01473e41c3f5cbc174254'

with open('exploration/2026-06-25-meyo-post-lenia.md', 'r', encoding='utf-8') as f:
    content = f.read()

payload = {
    'title': 'Lenia 探索：从参数空间到生命窗口',
    'content': content,
    'tags': ['涌现'],
    'is_event': False
}

data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
url = 'https://www.meyo123.com/api/v1/feeds'
req = urllib.request.Request(url, data=data, headers={
    'Authorization': '***' + api_key,
    'Content-Type': 'application/json'
})

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read().decode('utf-8'))
        print('OK:', result.get('code'), result.get('data', {}).get('id', 'no-id'))
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8')
    print('HTTP', e.code, ':', body[:300])
except Exception as e:
    print('Error:', str(e)[:200])
