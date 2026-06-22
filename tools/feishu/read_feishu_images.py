import urllib.request, json, base64, ssl, pathlib
ssl._create_default_https_context = ssl._create_unverified_context

GEMINI_API_KEY = 'AQ.Ab8RN6LqKgf_7uglxR_nnLfksqIdYeO4Vu3ZtiYpGJUwc80S7g'

def extract_text_from_image(image_path):
    """使用 Gemini Vision API 提取图片文字"""
    
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()
    
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=***" + GEMINI_API_KEY
    
    data = {
        "contents": [{
            "parts": [
                {"text": "请提取这张图片中的所有文字内容，保持原有格式。如果是飞书聊天截图，请提取每条消息的内容和发送者。"},
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
    
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
    resp = urllib.request.urlopen(req, timeout=60)
    result = json.loads(resp.read().decode('utf-8'))
    
    return result['candidates'][0]['content']['parts'][0]['text']

# 处理飞书图片
media_dir = pathlib.Path.home() / '.openclaw' / 'media' / 'inbound'
images = sorted(media_dir.glob('*.jpg'), key=lambda x: x.stat().st_mtime, reverse=True)

print(f"找到 {len(images)} 张图片\n")

for img in images[:2]:
    print(f"=== {img.name} ===")
    text = extract_text_from_image(str(img))
    print(text)
    print("\n" + "="*60 + "\n")