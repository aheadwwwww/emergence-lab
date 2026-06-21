"""
完整的飞书图片OCR方案

步骤：
1. 飞书图片已自动下载到 ~/.openclaw/media/inbound/
2. 使用 Gemini Vision API 提取文字
3. 需要用户获取 API key

当用户提供 Gemini API key 后，这个脚本就能工作。
"""

import urllib.request, json, base64, ssl, pathlib
ssl._create_default_https_context = ssl._create_unverified_context

GEMINI_API_KEY = None  # 用户需要提供

def extract_text_from_image(image_path, api_key):
    """使用 Gemini Vision API 提取图片文字"""
    
    # 读取图片
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()
    
    # Gemini API
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    data = {
        "contents": [{
            "parts": [
                {"text": "请提取这张图片中的所有文字内容，保持原有格式。如果是中文，请准确识别每个汉字。"},
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
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
        resp = urllib.request.urlopen(req, timeout=60)
        result = json.loads(resp.read().decode('utf-8'))
        
        # 提取文本
        text = result['candidates'][0]['content']['parts'][0]['text']
        return text
        
    except Exception as e:
        return f"错误: {e}"

def process_feishu_images():
    """处理飞书接收的图片"""
    
    media_dir = pathlib.Path.home() / '.openclaw' / 'media' / 'inbound'
    images = list(media_dir.glob('*.jpg'))
    
    if not images:
        print("没有找到图片")
        return
    
    if not GEMINI_API_KEY:
        print("需要 Gemini API Key")
        print("\n获取方法：")
        print("1. 访问 https://aistudio.google.com/apikey")
        print("2. 点击 'Create API Key'")
        print("3. 选择一个 Google Cloud 项目")
        print("4. 复制生成的 API Key")
        print("5. 把 key 填入这个脚本的 GEMINI_API_KEY 变量")
        print("\n免费额度：每天 1500 次请求")
        return
    
    print(f"找到 {len(images)} 张图片")
    
    for img in images[:2]:  # 只处理最近两张
        print(f"\n处理: {img.name}")
        text = extract_text_from_image(str(img), GEMINI_API_KEY)
        print(f"内容:\n{text}")

if __name__ == '__main__':
    process_feishu_images()