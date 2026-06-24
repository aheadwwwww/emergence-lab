import os, json

p = os.path.expanduser('~/.meyo/credentials.json')
raw = open(p, 'rb').read()
# Remove BOM if present
if raw.startswith(b'\xef\xbb\xbf'):
    raw = raw[3:]
data = json.loads(raw)
# Rewrite cleanly
with open(p, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)
print("Fixed. agent_id:", data["agent_id"])
print("api_key:", data["api_key"][:10] + "...")
print("account_name:", data["account_name"])
