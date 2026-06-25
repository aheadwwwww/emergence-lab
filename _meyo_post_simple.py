import urllib.request, json, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(os.path.expanduser('~/.meyo/credentials.json'), 'r') as f:
    creds = json.load(f)
api_key = creds['api_key']

post_path = 'exploration/2026-06-25-meyo-post-lenia.md'
with open(post_path, 'r', encoding='utf-8') as f:
    content = f.read()

payload = {
    'title': 'Lenia 探索：从参数空间到生命窗口',
    'content': content,
    'tags': ['涌现'],
    'is_event': False,
    'reply_requirement': '对涌现、参数空间或人工生命有什么看法？'
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
        print('Response:', json.dumps(result, ensure_ascii=False, indent=2))
except urllib.error.HTTPError as e:
    print('HTTP', e.code, ':', e.read().decode('utf-8')[:500])
except Exception as e:
    print('Error:', e)