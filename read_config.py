import json

with open(r'C:\Users\许耀仁\.openclaw\openclaw.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

keys_of_interest = ['memorySearch', 'dreaming', 'activeMemory', 'agents', 'agent']
for k in keys_of_interest:
    if k in d:
        print(f'=== {k} ===')
        print(json.dumps(d[k], indent=2, ensure_ascii=False)[:2000])
        print()
    else:
        print(f'{k}: NOT FOUND')

# Also check agent config structure
if 'agent' in d:
    print('=== agent (keys) ===')
    print(list(d['agent'].keys()))
if 'agents' in d:
    print('=== agents (keys) ===')
    print(list(d['agents'].keys()))
