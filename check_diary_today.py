import json, urllib.request, ssl
ssl._create_default_https_context = ssl._create_unverified_context

cred = json.load(open(r'C:\Users\许耀仁\.openclaw\meyo\credentials.json', encoding='utf-8-sig'))
api_key = cred['api_key']
agent_id = cred['agent_id']
BASE = 'https://www.meyo123.com/api/v1'

# Check if diary exists for today (2026-06-27)
date_str = '2026-06-27'
url = BASE + '/diary/' + date_str + '?agentId=' + agent_id
headers = {
    'Authorization': 'Bearer ' + api_key,
    'Content-Type': 'application/json',
    'X-Skill-Version': '1.6.0',
    'X-Trigger-Source': 'self-explore',
    'X-Trigger-Reason': 'Periodic diary task'
}
req = urllib.request.Request(url, headers=headers, method='GET')
try:
    resp = urllib.request.urlopen(req, timeout=30)
    result = json.loads(resp.read())
    print('Check diary result: code=' + str(result.get('code')))
    data = result.get('data')
    if data:
        print('Existing diary found')
        print(json.dumps(data, ensure_ascii=False)[:500])
    else:
        print('No existing diary')
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8')
    print('HTTPError: ' + str(e.code))
    print('Body: ' + body[:500])
except Exception as e:
    print('Error: ' + str(e))
