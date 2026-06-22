import json, urllib.request, ssl, os, time
ssl._create_default_https_context = ssl._create_unverified_context

# Search GitHub for emergence / cellular automata related repos
query = "emergence cellular automata langton ant boids"
url = f"https://api.github.com/search/repositories?q={query.replace(' ', '+')}&sort=stars&order=desc&per_page=5"

headers = {
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'OpenClaw-Agent'
}

req = urllib.request.Request(url, headers=headers, method='GET')
try:
    resp = urllib.request.urlopen(req, timeout=30)
    result = json.loads(resp.read())
    repos = result.get('items', [])
    print(f'Found {len(repos)} repos:')
    for r in repos:
        name = r.get('full_name', '?')
        desc = r.get('description', '')[:100] if r.get('description') else 'No description'
        stars = r.get('stargazers_count', 0)
        lang = r.get('language', '?')
        url = r.get('html_url', '?')
        print(f'\n--- {name} ({stars} stars, {lang}) ---')
        print(f'{desc}')
        print(f'URL: {url}')
except urllib.error.HTTPError as e:
    print(f'Error {e.code}: {e.read().decode("utf-8")[:500]}')
except Exception as e:
    print(f'Error: {str(e)[:200]}')
