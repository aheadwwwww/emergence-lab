import json
from collections import Counter

with open('experiments/lenia_jax_sweep_R20.json', 'r') as f:
    data = json.load(f)

sorted_data = sorted(data, key=lambda x: x['score'], reverse=True)
print('Top 10 by score:')
for r in sorted_data[:10]:
    mu = r['mu']
    sigma = r['sigma']
    label = r['label']
    score = r['score']
    entropy = r['entropy']
    edge = r['edge_density']
    print(f"  mu={mu:.3f} sigma={sigma:.3f} label={label:12s} score={score:.4f} entropy={entropy:.4f} edge={edge:.4f}")

labels = Counter(r['label'] for r in data)
print()
print('Label distribution:', dict(labels))
print(f'Total: {len(data)}')
