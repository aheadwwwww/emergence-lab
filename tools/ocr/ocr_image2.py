import urllib.request, json, base64, ssl, pathlib
ssl._create_default_https_context = ssl._create_unverified_context

GEMINI_API_KEY = 'AQ.Ab8RN6LqKgf_7uglxR_nnLfksqIdYeO4Vu3ZtiYpGJUwc80S7g'

def extract_text_from_image(image_path):
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()
    
    base_url = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent"
    url = base_url + "?key=" + GEMINI_API_KEY
    
    data = {
        "contents": [{
            "parts": [
                {"text": "Extract all text from this image. If it's a chat screenshot, extract each message and sender."},
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

# 只处理第二张图片
img_path = pathlib.Path.home() / '.openclaw' / 'media' / 'inbound' / 'e10a2cca-a329-474d-bbc0-a3705a2bd93e.jpg'
print("Processing image 2...")
text = extract_text_from_image(str(img_path))

# 保存到文件
output_file = pathlib.Path.home() / '.openclaw' / 'workspace' / 'ocr_result_image2.txt'
output_file.write_text(text, encoding='utf-8')
print("Saved to:", output_file)
print("\nContent:\n")
print(text)