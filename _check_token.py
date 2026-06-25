import urllib.request, json

token = "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"

# Check token validity
url = "https://api.github.com/user"
req = urllib.request.Request(
    url,
    headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "OpenClaw"
    }
)

try:
    resp = urllib.request.urlopen(req, timeout=15)
    result = json.loads(resp.read())
    print("Token valid!")
    print(f"User: {result.get('login')}")
    print(f"Name: {result.get('name')}")
except urllib.error.HTTPError as e:
    error = json.loads(e.read())
    print(f"Error: {error.get('message', str(e))}")
except Exception as e:
    print(f"Error: {str(e)}")