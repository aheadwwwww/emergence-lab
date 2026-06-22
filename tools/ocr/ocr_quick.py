import urllib.request, json, base64, ssl, pathlib
ssl._create_default_https_context = ssl._create_unverified_context

KEY = 'AQ.Ab8RN6LqKgf_7uglxR_nnLfksqIdYeO4Vu3ZtiYpGJUwc80S7g'

def ocr(path):
    with open(path, 'rb') as f:
        img = base64.b64encode(f.read()).decode()
    
    u = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key=" + KEY
    d = {"contents":[{"parts":[{"text":"Extract all text"},{"inline_data":{"mime_type":"image/jpeg","data":img}}]}]}
    
    r = urllib.request.Request(u, data=json.dumps(d).encode(), headers={'Content-Type':'application/json'})
    resp = urllib.request.urlopen(r, timeout=60)
    return json.loads(resp.read())['candidates'][0]['content']['parts'][0]['text']

media = pathlib.Path.home() / '.openclaw' / 'media' / 'inbound'
imgs = sorted(media.glob('*.jpg'), key=lambda x: x.stat().st_mtime, reverse=True)[:2]

for i in imgs:
    print(i.name)
    t = ocr(str(i))
    (pathlib.Path.home() / '.openclaw' / 'workspace' / f'ocr_{i.stem}.txt').write_text(t, encoding='utf-8')
    print(t[:800])