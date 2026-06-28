import urllib.request, ssl, sys, io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ctx = ssl.create_default_context()

# Try main branch first, then master
for branch in ['main', 'master']:
    url = f'https://raw.githubusercontent.com/eze-is/web-access/{branch}/README.md'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
            content = r.read().decode('utf-8')
            print(f"=== README from {branch} ({len(content)} chars) ===")
            print(content[:5000])
            print(f"\n... ({len(content)} total chars)")
            break
    except Exception as e:
        print(f"{branch}: {e}")
