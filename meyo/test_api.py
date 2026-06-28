import urllib.request, ssl, json

ctx = ssl.create_default_context()

# Try different API endpoints
endpoints = [
    '/api/posts?limit=5',
    '/api/posts/recent?limit=5',
    '/api/feed?limit=5',
    '/api/community/posts?limit=5',
    '/api/v1/posts?limit=5',
]

for ep in endpoints:
    url = f'https://www.meyo123.com{ep}'
    headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
            body = r.read().decode('utf-8')[:300]
            print(f'[{r.status}] {ep}: {body[:200]}')
    except Exception as e:
        print(f'[ERR] {ep}: {e}')
