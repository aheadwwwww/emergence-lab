import urllib.request, json, base64, ssl
ssl._create_default_https_context = ssl._create_unverified_context

# 用免费OCR API提取图片文字
# 尝试几个选项

def try_ocr_space(image_path, api_key='helloworld'):
    """OCR.space 免费API"""
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()
    
    url = 'https://api.ocr.space/parse/image'
    data = {
        'base64Image': 'data:image/jpeg;base64,' + image_data,
        'apikey': api_key,
        'language': 'chs'  # 中文
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers={'Content-Type': 'application/json'})
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        if result.get('OCRExitCode') == 1:
            return result['ParsedResults'][0]['ParsedText']
        else:
            return f"OCR失败: {result.get('ErrorMessage', 'unknown')}"
    except Exception as e:
        return f"请求失败: {e}"

# 测试
# print(try_ocr_space('path/to/image.jpg'))