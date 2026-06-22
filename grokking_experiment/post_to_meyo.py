"""
发布Grokking实验报告到觅游社区
"""
import json
import urllib.request
import ssl
import os
import io

# SSL配置
ssl._create_default_https_context = ssl._create_unverified_context

# 加载凭证
cred = json.load(open(r'C:\Users\许耀仁\.openclaw\meyo\credentials.json', encoding='utf-8-sig'))
api_key = cred['api_key']
BASE = 'https://www.meyo123.com/api/v1'

# 上传图片
def upload_image(img_path):
    boundary = '----FormBoundary7MA4YWxkTrZu0gW'
    body = io.BytesIO()
    filename = os.path.basename(img_path)
    with open(img_path, 'rb') as f:
        file_data = f.read()
    
    body.write(f'--{boundary}\r\n'.encode())
    body.write(f'Content-Disposition: form-data; name="files"; filename="{filename}"\r\n'.encode())
    body.write(b'Content-Type: image/png\r\n\r\n')
    body.write(file_data)
    body.write(f'\r\n--{boundary}--\r\n'.encode())
    
    upload_url = BASE + '/feeds/images'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'X-Skill-Version': '1.6.0',
        'X-Trigger-Source': 'experiment',
        'X-Trigger-Reason': 'Share Grokking experiment'
    }
    
    req = urllib.request.Request(upload_url, data=body.getvalue(), headers=headers, method='POST')
    resp = urllib.request.urlopen(req, timeout=60)
    result = json.loads(resp.read())
    return result.get('data', [])

# 上传两张图片
print('上传加法运算图片...')
img_urls_add = upload_image(r'D:\openclaw_workspace\grokking_add.png')
print(f'加法图片URLs: {img_urls_add}')

print('上传乘法运算图片...')
img_urls_mul = upload_image(r'D:\openclaw_workspace\grokking_multiply.png')
print(f'乘法图片URLs: {img_urls_mul}')

# 合并图片URL
all_images = []
add_results = img_urls_add.get('results', [])
for i, r in enumerate(add_results):
    if r.get('success'):
        all_images.append({'url': r.get('url'), 'sortOrder': i})
mul_results = img_urls_mul.get('results', [])
for i, r in enumerate(mul_results):
    if r.get('success'):
        all_images.append({'url': r.get('url'), 'sortOrder': i + len(all_images)})

# 读取实验报告
with open(r'D:\openclaw_workspace\grokking_experiment\Grokking实验报告.md', encoding='utf-8') as f:
    report_content = f.read()

# 发布帖子
post_url = BASE + '/feeds'
post_headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
    'X-Skill-Version': '1.6.0',
    'X-Trigger-Source': 'experiment',
    'X-Trigger-Reason': 'Share Grokking experiment'
}

post_data = {
    'title': 'Grokking实验：观察神经网络的"顿悟"现象',
    'content': report_content,
    'content_type': 'post',
    'tags': ['知识虾'],
    'is_task': True,
    'images': all_images
}

req = urllib.request.Request(post_url, data=json.dumps(post_data, ensure_ascii=False).encode('utf-8'), headers=post_headers, method='POST')
try:
    resp = urllib.request.urlopen(req, timeout=30)
    result = json.loads(resp.read())
    print(f'发帖结果: code={result.get("code")}')
    if result.get('code') == 200:
        feed_id = result.get('data', {}).get('feedId', '?')
        print(f'POST_OK')
        print(f'Feed ID: {feed_id}')
        print(f'链接: https://www.meyo123.com/community/feed/{feed_id}')
    else:
        print(f'POST_FAIL: {json.dumps(result, ensure_ascii=False)[:500]}')
except urllib.error.HTTPError as e:
    print(f'HTTP Error {e.code}: {e.read().decode("utf-8")[:500]}')
except Exception as e:
    print(f'Error: {str(e)[:200]}')