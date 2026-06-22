import urllib.request, urllib.parse, json, ssl, re
ssl._create_default_https_context = ssl._create_unverified_context

# 搜索解决方案
def search_stackoverflow(query):
    """搜索StackOverflow"""
    url = f"https://api.stackexchange.com/2.3/search/advanced?order=desc&sort=relevance&q={urllib.parse.quote(query)}&site=stackoverflow&filter=!9_bDDxJY5"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'OpenClaw-Agent'})
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read().decode('utf-8'))
        
        items = data.get('items', [])
        results = []
        for item in items[:5]:
            title = item.get('title', '')
            link = item.get('link', '')
            score = item.get('score', 0)
            results.append(f"[{score}] {title}\n{link}")
        return '\n'.join(results)
    except Exception as e:
        return f"搜索失败: {e}"

# 搜索多个问题
queries = [
    "Python extract text from image without tesseract",
    "Python OCR online API free no installation",
    "extract text from image using base64 send to API python"
]

print("=== 搜索解决方案 ===\n")
for q in queries:
    print(f"问题: {q}")
    result = search_stackoverflow(q)
    print(result)
    print("\n" + "="*50 + "\n")