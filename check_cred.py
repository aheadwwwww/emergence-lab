import os, json

p = os.path.expanduser('~/.meyo/credentials.json')
print("Path:", p)
print("Exists:", os.path.exists(p))
if os.path.exists(p):
    with open(p) as f:
        data = json.load(f)
    print("agent_id:", data.get("agent_id", "NOT_FOUND"))
    print("Has api_key:", "api_key" in data)
    print("account_name:", data.get("account_name", "NOT_FOUND"))
else:
    print("CREDENTIALS NOT FOUND")
