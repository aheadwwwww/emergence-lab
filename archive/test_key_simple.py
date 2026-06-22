import urllib.request, json, ssl, sys
ssl._create_default_https_context = ssl._create_unverified_context
sys.stdout.reconfigure(encoding='utf-8')

GEMINI_API_KEY = 'AQ.Ab8RN6LqKgf_7uglxR_nnLfksqIdYeO4Vu3ZtiYpGJUwc80S7g'

url = "https://generativelanguage.googleapis.com/v1beta/models?key=***" + GEMINI_API_KEY

try:
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req, timeout=30)
    result = json.loads(resp.read().decode('utf-8'))
    print("API Key OK")
    for model in result.get('models', [])[:10]:
        name = model.get('name', '')
        if 'gemini' in name.lower():
            print(name)
except urllib.error.HTTPError as e:
    error_body = e.read().decode('utf-8')
    print(f"HTTP {e.code}")
    print(error_body[:500])
except Exception as e:
    print(f"Error: {e}")