import urllib.request, json, base64, ssl, pathlib
ssl._create_default_https_context = ssl._create_unverified_context

# 完整的API key
GEMINI_API_KEY = 'AQ.Ab8RN6LqKgf_7uglxR_nnLfksqIdYeO4Vu3ZtiYpGJUwc80S7g'

def extract_text_from_image(image_path):
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()
    
    # 构建URL - 不用f-string拼接
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

media_dir = pathlib.Path.home() / '.openclaw' / 'media' / 'inbound'
images = sorted(media_dir.glob('*.jpg'), key=lambda x: x.stat().st_mtime, reverse=True)

print("Found", len(images), "images")

for img in images[:2]:
    print("\n=== Image:", img.name, "===")
    try:
        text = extract_text_from_image(str(img))
        # Save to file instead of printing
        output_file = pathlib.Path.home() / '.openclaw' / 'workspace' / f'ocr_result_{img.stem}.txt'
        output_file.write_text(text, encoding='utf-8')
        print("OCR result saved to:", output_file)
        print("Preview (first 500 chars):")
        print(text[:500])
    except Exception as e:
        print("Error:", str(e))