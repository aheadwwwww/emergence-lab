import urllib.request, ssl

ctx = ssl.create_default_context()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

url = 'https://www.meyo123.com/community'
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
    html = r.read().decode('utf-8')

# Print full HTML
print(html[:5000])
