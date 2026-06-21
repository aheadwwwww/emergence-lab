import urllib.request, json, ssl, sys
ssl._create_default_https_context = ssl._create_unverified_context

# Try to fetch free LLM API resources
urls = [
    'https://api.github.com/repos/cheahjs/free-llm-api-resources/contents',
    'https://api.github.com/repos/berriai/litellm/contents',
]

headers = {'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'OpenClaw-Agent'}

results = []
for url in urls:
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        results.append({'url': url, 'status': 'ok', 'count': len(data) if isinstance(data, list) else 1})
    except Exception as e:
        results.append({'url': url, 'status': 'error', 'error': str(e)[:100]})

for r in results:
    print(json.dumps(r, ensure_ascii=False))
