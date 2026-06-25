import json
nb = json.load(open('experiments/self_org_systems/self_replicating_nn/recursively_fertile_self_replicating.ipynb', 'r', encoding='utf-8'))
cells = nb['cells']
print(f'Total cells: {len(cells)}')
for i, c in enumerate(cells[:15]):
    print(f'Cell {i}: {c.get("cell_type", "unknown")} - {len(c.get("source", []))} lines')
