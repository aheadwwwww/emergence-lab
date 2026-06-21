import urllib.request, json, ssl
ssl._create_default_https_context = ssl._create_unverified_context

GEMINI_API_KEY = 'AQ.Ab8RN6LqKgf_7uglxR_nnLfksqIdYeO4Vu3ZtiYpGJUwc80S7g'

# 测试key有效性
url = "https://generativelanguage.googleapis.com/v1beta/models?key=***" + GEMINI_API_KEY

try:
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req, timeout=30)
    result = json.loads(resp.read().decode('utf-8'))
    print("✓ API Key 有效！")
    print("\n可用模型：")
    for model in result.get('models', [])[:10]:
        name = model.get('name', '')
        if 'gemini' in name.lower():
            print(f"  {name}")
except Exception as e:
    print(f"✗ API Key 无效: {e}")
    if hasattr(e, 'read'):
        error_body = e.read().decode('utf-8')
        print(f"\n错误详情:\n{error_body}")