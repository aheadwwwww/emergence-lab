import urllib.request, json, base64, ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Gemini Vision API 调用方法
# 文档：https://ai.google.dev/tutorials/python_quickstart

def call_gemini_vision(image_path, prompt="Extract all text from this image", api_key=None):
    """
    调用 Gemini Vision API 提取图片文字
    
    如果没有api_key，返回如何获取的说明
    """
    
    if not api_key:
        return """
需要 Gemini API Key。

获取方法：
1. 访问 https://aistudio.google.com/apikey
2. 点击 "Create API Key"
3. 选择一个 Google Cloud 项目
4. 复制生成的 API Key

免费额度：
- Gemini 1.5 Flash: 每天 1500 次请求
- 完全免费，无需信用卡
"""
    
    # 读取图片
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()
    
    # Gemini API endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    # 请求体
    data = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": image_data
                    }
                }
            ]
        }]
    }
    
    headers = {'Content-Type': 'application/json'}
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers
        )
        resp = urllib.request.urlopen(req, timeout=60)
        result = json.loads(resp.read().decode('utf-8'))
        
        # 提取文本
        text = result['candidates'][0]['content']['parts'][0]['text']
        return text
    except Exception as e:
        return f"API调用失败: {e}"

# 测试
if __name__ == '__main__':
    print(call_gemini_vision(None))  # 显示如何获取API key
    
    # 如果有API key，可以这样调用：
    # result = call_gemini_vision("path/to/image.jpg", api_key="YOUR_KEY")
    # print(result)