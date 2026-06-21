import urllib.request, json, base64, ssl, pathlib
ssl._create_default_https_context = ssl._create_unverified_context

GEMINI_API_KEY = 'AQ.Ab8RN6KdFZLlW8JVkBtUd7117dup-jsnNiQ8vrb4e9XNysJVpQ'

# 先测试API key是否有效
def test_api_key():
    """测试API key"""
    url = "https://generativelanguage.googleapis.com/v1beta/models?key=***" + GEMINI_API_KEY
    
    try:
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read().decode('utf-8'))
        print("API Key 有效！可用模型：")
        for model in result.get('models', [])[:5]:
            print(f"  - {model.get('name', 'unknown')}")
        return True
    except Exception as e:
        print(f"API Key 测试失败: {e}")
        # 尝试读取错误响应
        if hasattr(e, 'read'):
            error_body = e.read().decode('utf-8')
            print(f"错误详情: {error_body}")
        return False

test_api_key()