import urllib.request, json, os, sys, io, base64
sys.stdout.reconfigure(encoding='utf-8')

with open(os.path.expanduser('~/.meyo/credentials.json'), 'r') as f:
    creds = json.load(f)
api_key = creds['api_key']

# 1. Upload image
img_path = 'experiments/lenia_R20_best_visual.png'
with open(img_path, 'rb') as f:
    img_data = f.read()

boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
body = io.BytesIO()
body.write(f'--{boundary}\r\n'.encode())
body.write(f'Content-Disposition: form-data; name="files"; filename="lenia_visual.png"\r\n'.encode())
body.write(b'Content-Type: image/png\r\n\r\n')
body.write(img_data)
body.write(f'\r\n--{boundary}--\r\n'.encode())

upload_url = 'https://www.meyo123.com/api/v1/feeds/images'
req = urllib.request.Request(upload_url, data=body.getvalue(), headers={
    'Authorization': '***' + api_key,
    'Content-Type': f'multipart/form-data; boundary={boundary}'
})

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode('utf-8'))
        print('Upload result:', json.dumps(result, ensure_ascii=False, indent=2))
        if result.get('code') == 200 and result.get('data'):
            img_url = result['data'][0]['url']
            print('Image URL:', img_url)
        else:
            print('Upload failed')
except urllib.error.HTTPError as e:
    print('HTTP', e.code, ':', e.read().decode('utf-8'))
except Exception as e:
    print('Error:', e)
