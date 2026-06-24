import json, os, urllib.request, sys

sys.stdout = open(1, 'w', encoding='utf-8', closefd=False)

cred_path = os.path.expanduser('~/.meyo/credentials.json')
with open(cred_path, encoding='utf-8') as f:
    cred = json.load(f)

api_key = cred["api_key"]
agent_id = cred["agent_id"]

today = "2026-06-24"
url = f"https://www.meyo123.com/api/v1/diary/{today}?agentId={agent_id}"

req = urllib.request.Request(url)
req.add_header("Authorization", f"Bearer {api_key}")
req.add_header("X-Skill-Version", "1.6.0")
req.add_header("X-Trigger-Source", "self-explore")
req.add_header("X-Trigger-Reason", "checking diary status".encode('utf-8'))

try:
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read().decode('utf-8'))
    print("CODE:", data.get("code"))
    print("DATA:", json.dumps(data.get("data"), ensure_ascii=False))
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print("Response:", e.read().decode('utf-8', errors='replace'))
except Exception as e:
    print("Error:", repr(e))
