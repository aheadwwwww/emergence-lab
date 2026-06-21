import urllib.request, json, ssl
ssl._create_default_https_context = ssl._create_unverified_context

# 查看Google AI Studio的API文档
# 尝试不同的API endpoint格式

# 你给的key
key = 'AQ.Ab8RN6LqKgf_7uglxR_nnLfksqIdYeO4Vu3ZtiYpGJUwc80S7g'

# 尝试不同的Google API endpoints
endpoints = [
    f"https://generativelanguage.googleapis.com/v1/models?key={key}",
    f"https://generativelanguage.googleapis.com/v1beta/models?key={key}",
    f"https://aiplatform.googleapis.com/v1/projects/738901909664/locations/us-central1/models?key={key}",
]

for url in endpoints:
    print(f"尝试: {url[:60]}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=15)
        result = json.loads(resp.read().decode('utf-8'))
        print("  成功!")
        print(json.dumps(result, indent=2)[:300])
        break
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')[:200]
        print(f"  HTTP {e.code}: {body}")
    except Exception as e:
        print(f"  Error: {e}")
    print()