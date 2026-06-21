"""
直接调用免费OCR API

不需要安装Python包，直接用urllib发送请求
"""

import urllib.request, json, base64, ssl
ssl._create_default_https_context = ssl._create_unverified_context

def ocr_with_ocrspace(image_path, api_key='helloworld'):
    """
    OCR.space 提供免费API（用'helloworld'作为测试key）
    """
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()
    
    url = 'https://api.ocr.space/parse/image'
    
    # 构建multipart/form-data
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    body = []
    body.append(f'--{boundary}')
    body.append('Content-Disposition: form-data; name="apikey"')
    body.append('')
    body.append(api_key)
    body.append(f'--{boundary}')
    body.append('Content-Disposition: form-data; name="language"')
    body.append('')
    body.append('chs')
    body.append(f'--{boundary}')
    body.append('Content-Disposition: form-data; name="base64Image"')
    body.append('')
    body.append(f'data:image/jpeg;base64,{image_data[:100]}...')  # 截断显示
    body.append(f'--{boundary}--')
    
    print(f"准备发送请求到 OCR.space...")
    print(f"图片大小: {len(image_data)} bytes")
    
    # 使用免费key测试
    data = {
        'base64Image': f'data:image/jpeg;base64,{image_data}',
        'apikey': 'helloworld',  # 免费测试key
        'language': 'chs',
        'isOverlayRequired': False
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
        
        if result.get('OCRExitCode') == 1:
            return result['ParsedResults'][0]['ParsedText']
        else:
            return f"OCR失败: {result.get('ErrorMessage', result)}"
    except Exception as e:
        return f"请求失败: {e}"

# 测试
if __name__ == '__main__':
    import pathlib
    workspace = pathlib.Path.home() / '.openclaw' / 'workspace'
    images = list(workspace.rglob('*.png'))[:1]
    
    if images:
        print(f"测试图片: {images[0]}")
        result = ocr_with_ocrspace(str(images[0]))
        print(f"结果: {result[:200] if result else 'None'}...")