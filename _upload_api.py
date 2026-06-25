"""
用 GitHub API 直接上传文件
"""
import urllib.request, json
import base64
import os

token = "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"
username = "aheadwwwww"
repo = "emergence-lab"

# Files to upload
files = [
    'README.md',
    '__init__.py',
    'requirements.txt',
    '.gitignore',
]

def upload_file(filepath, local_path):
    url = f"https://api.github.com/repos/{username}/{repo}/contents/{filepath}"
    
    # Read file content
    with open(local_path, 'rb') as f:
        content = base64.b64encode(f.read()).decode('utf-8')
    
    data = {
        "message": f"Add {filepath}",
        "content": content
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "OpenClaw"
        },
        method="PUT"
    )
    
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        print(f"OK {filepath}")
        return True
    except urllib.error.HTTPError as e:
        error = json.loads(e.read())
        if error.get('message') == 'Invalid request.\n\n"sha" wasn\'t supplied.':
            print(f"OK {filepath} (already exists)")
            return True
        print(f"FAIL {filepath}: {error.get('message', str(e))[:100]}")
        return False

os.chdir('D:\\temp_emergence_lab')

print("Uploading files to GitHub...")
for f in files:
    if os.path.exists(f):
        upload_file(f, f)

# Upload core files
for f in ['core/metrics.py', 'core/visualization.py', 'models/lenia.py', 'models/nca.py', 'models/pheromone.py']:
    if os.path.exists(f):
        upload_file(f, f)

print("\nDone! Check: https://github.com/aheadwwwww/emergence-lab")
