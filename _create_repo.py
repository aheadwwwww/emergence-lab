import urllib.request, json

token = "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"

# Create repo
url = "https://api.github.com/user/repos"
data = {
    "name": "emergence-lab",
    "description": "Programmable emergence experiment framework - Lenia, NCA, PheromoneCA",
    "private": False,
    "has_issues": True,
    "has_projects": True,
    "auto_init": False
}

req = urllib.request.Request(
    url,
    data=json.dumps(data).encode('utf-8'),
    headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "OpenClaw"
    },
    method="POST"
)

try:
    resp = urllib.request.urlopen(req, timeout=15)
    result = json.loads(resp.read())
    print("Repository created!")
    print(f"URL: {result['html_url']}")
    print(f"Clone URL: {result['clone_url']}")
except urllib.error.HTTPError as e:
    error = json.loads(e.read())
    print(f"Error: {error.get('message', str(e))}")
except Exception as e:
    print(f"Error: {str(e)}")