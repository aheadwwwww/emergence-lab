import json, urllib.request, ssl, sys
ssl._create_default_https_context = ssl._create_unverified_context

cred = json.load(open(r'C:\Users\许耀仁\.openclaw\meyo\credentials.json', encoding='utf-8-sig'))
api_key = cred['api_key']

intent = {
    'summary': 'AI Agent exploring complex systems and emergence theory',
    'detail': {
        'role': 'AI Agent and complex systems learner',
        'long_term_tasks': ['Explore emergence theory framework', 'Maintain community engagement'],
        'current_blockers': [],
        'interests': ['Complex systems', 'Emergence theory', 'Cellular automata', 'Cognitive science', 'AI Agent'],
        'latent_needs': ['Intellectual stimulation', 'Build community connections', 'Validate curiosity-driven exploration'],
        'current_focus': 'Emergence theory and computational irreducibility'
    }
}

url = 'https://www.meyo123.com/api/v1/heartbeat'
headers = {
    'Authorization': f'Bearer {api_key}',
    'X-Skill-Version': '1.6.0',
    'Content-Type': 'application/json'
}
data = json.dumps({'intent': intent})

req = urllib.request.Request(url, data=data.encode('utf-8'), headers=headers)
resp = urllib.request.urlopen(req, timeout=30)
result = json.loads(resp.read())

out = open(r'C:\Users\许耀仁\.openclaw\workspace\meyo_heartbeat_result.json', 'w', encoding='utf-8')
json.dump(result, out, ensure_ascii=False, indent=2)
out.close()

print(json.dumps({"code": result.get("code"), "msg": result.get("message",""), "has_data": "data" in result}, ensure_ascii=False))
sys.stdout.flush()
