import urllib.request, json, sys

def get_readme(name):
    url = f'https://api.github.com/repos/{name}/readme'
    headers = {
        'User-Agent': 'openclaw-explorer',
        'Accept': 'application/vnd.github.v3.raw'
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        text = resp.read().decode('utf-8', errors='replace')
        return text[:1200] if len(text)>1200 else text
    except Exception as e:
        return f'Error: {e}'

repos = [
    ('hunar4321/particle-life', 'Particle Life'),
    ('riveSunder/carles_game', 'CARLES Game - CA Creativity'),
    ('nylki/lindenmayer', 'Lindenmayer System'),
    ('chrxh/alien', 'ALIEN - CUDA Life Sim'),
    ('openalea/lpy', 'LPy - L-System Python'),
]

for name, label in repos:
    print(f"\n{'='*60}")
    print(f"README: {label} ({name})")
    print(f"{'='*60}")
    print(get_readme(name))
