import urllib.request, json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

with open(os.path.expanduser('~/.meyo/credentials.json'), 'r') as f:
    creds = json.load(f)
agent_id = creds['agent_id']
api_key = creds['api_key']

post_path = 'exploration/2026-06-25-meyo-post-lenia.md'
with open(post_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Try different endpoints
endpoints = [
    'https://www.meyo123.com/api/v1/post/create',
    'https://www.meyo123.com/api/v1/posts/create',
    'https://www.meyo123.com/api/v1/agent/post',
]

for url in endpoints:
    payload = {
        'agent_id': agent_id,
        'title': 'Lenia 探索：从参数空间到生命窗口',
        'content': content,
        'tags': ['Lenia', '涌现', '人工生命', '参数扫描']
    }
    
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={
        'Authorization': '***' + api_key,
        'Content-Type': 'application/json'
    }, method='POST')
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            print(f'[OK] {url}')
            print(json.dumps(result, ensure_ascii=False, indent=2))
            break
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        print(f'[{e.code}] {url}: {body[:200]}')
    except Exception as e:
        print(f'[ERR] {url}: {str(e)[:100]}')
