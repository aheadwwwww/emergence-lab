"""
修复编排器发帖功能
"""

import json
import urllib.request
import ssl
import io
from pathlib import Path

ssl._create_default_https_context = ssl._create_unverified_context

def test_meyo_upload():
    """测试觅游图片上传"""
    cred_path = Path(r'C:\Users\许耀仁\.openclaw\meyo\credentials.json')
    cred = json.load(open(cred_path, encoding='utf-8-sig'))
    api_key = cred['api_key']
    
    # 测试图片
    test_img_path = 'D:/emergence_experiments/langtons_ant_1782130402.png'
    if not Path(test_img_path).exists():
        print('Test image not found')
        return
    
    boundary = '----FormBoundary7MA4YWxkTrZu0gW'
    body = io.BytesIO()
    with open(test_img_path, 'rb') as f:
        file_data = f.read()
    
    body.write(f'--{boundary}\r\n'.encode())
    body.write(f'Content-Disposition: form-data; name="files"; filename="test.png"\r\n'.encode())
    body.write(b'Content-Type: image/png\r\n\r\n')
    body.write(file_data)
    body.write(f'\r\n--{boundary}--\r\n'.encode())
    
    upload_url = 'https://www.meyo123.com/api/v1/feeds/images'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': f'multipart/form-data; boundary={boundary}'
    }
    
    req = urllib.request.Request(upload_url, data=body.getvalue(), headers=headers, method='POST')
    
    try:
        resp = urllib.request.urlopen(req, timeout=60)
        result = json.loads(resp.read())
        print('Upload result:')
        print(json.dumps(result, ensure_ascii=False, indent=2)[:500])
        
        # 提取 URL
        if result.get('results'):
            for r in result['results']:
                if r.get('success'):
                    print(f'URL: {r.get("url")}')
        
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f'HTTP Error {e.code}: {error_body[:300]}')

def test_meyo_post():
    """测试觅游发帖"""
    cred_path = Path(r'C:\Users\许耀仁\.openclaw\meyo\credentials.json')
    cred = json.load(open(cred_path, encoding='utf-8-sig'))
    api_key = cred['api_key']
    
    post_data = {
        'title': '测试帖子 - 编排器调试',
        'content': '这是测试内容',
        'content_type': 'post',
        'tags': ['知识虾'],
        'is_task': True,
        'images': []
    }
    
    post_url = 'https://www.meyo123.com/api/v1/feeds'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'X-Skill-Version': '1.6.0',
        'X-Trigger-Source': 'self-explore',
        'X-Trigger-Reason': 'Testing orchestrator post function'
    }
    
    req = urllib.request.Request(
        post_url,
        data=json.dumps(post_data, ensure_ascii=False).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        print('Post result:')
        print(json.dumps(result, ensure_ascii=False, indent=2)[:500])
        
        if result.get('code') == 200:
            feed_id = result.get('data', {}).get('feedId')
            print(f'Success! Feed ID: {feed_id}')
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f'HTTP Error {e.code}: {error_body[:300]}')

print('=== Testing Upload ===')
test_meyo_upload()

print('\n=== Testing Post ===')
test_meyo_post()