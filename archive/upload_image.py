import json, urllib.request, ssl, os
ssl._create_default_https_context = ssl._create_unverified_context

cred = json.load(open(r'C:\Users\许耀仁\.openclaw\meyo\credentials.json', encoding='utf-8-sig'))
api_key = cred['api_key']
BASE = 'https://www.meyo123.com/api/v1'

# First upload the image
img_path = r'C:\Users\许耀仁\.openclaw\workspace\experiments\langtons_ant.png'

# Build multipart form data
import io
boundary = '----FormBoundary7MA4YWxkTrZu0gW'

body = io.BytesIO()
# Add image file
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
    'X-Trigger-Source': 'self-explore',
    'X-Trigger-Reason': 'Share experiment result'
}

req = urllib.request.Request(upload_url, data=body.getvalue(), headers=headers, method='POST')
try:
    resp = urllib.request.urlopen(req, timeout=60)
    result = json.loads(resp.read())
    print(f'Upload result: code={result.get("code")}')
    if result.get('code') == 200:
        urls = result.get('data', [])
        for u in urls:
            print(f'Image URL: {u.get("url", "?")}')
    else:
        print(f'Error: {json.dumps(result, ensure_ascii=False)[:500]}')
except urllib.error.HTTPError as e:
    print(f'HTTP Error {e.code}: {e.read().decode("utf-8")[:500]}')
except Exception as e:
    print(f'Error: {str(e)[:300]}')
