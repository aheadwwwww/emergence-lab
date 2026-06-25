import urllib.request
import sys
sys.stdout.reconfigure(encoding='utf-8')

req = urllib.request.Request('https://www.meyo123.com/community.md', headers={'User-Agent': 'openclaw'})
resp = urllib.request.urlopen(req, timeout=10)
content = resp.read().decode('utf-8')

# Find the post creation API section
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'POST' in line and 'post' in line.lower():
        print(f"Line {i}: {line}")
        for j in range(max(0, i-2), min(len(lines), i+10)):
            print(f"{j}: {lines[j]}")
        print()
