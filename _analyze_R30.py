import json
from collections import Counter

for R, grid, fname in [(20, 256, 'lenia_jax_sweep_R20.json'), (30, 256, 'lenia_jax_sweep_R30.json'), (30, 512, 'lenia_jax_sweep_R30_512.json')]:
    try:
        with open(f'experiments/{fname}', 'r') as f:
            data = json.load(f)
        labels = Counter(r['label'] for r in data)
        best = max(data, key=lambda x: x['score'])
        structs = [r for r in data if r['label'] == 'structure']
        alive_vals = [r['alive'] for r in structs] if structs else []
        print(f"R={R:2d} {grid}x{grid:3d} | {len(data)} runs | dead={labels.get('dead',0)} simple={labels.get('simple',0)} structure={labels.get('structure',0)}")
        print(f"      best: mu={best['mu']:.3f} sigma={best['sigma']:.3f} score={best['score']:.4f}")
        if alive_vals:
            print(f"      struct alive range: {min(alive_vals):.3f} - {max(alive_vals):.3f}")
        # Print structure parameters
        if structs:
            print("      structure params:", [(r['mu'], r['sigma']) for r in structs])
        print()
    except Exception as e:
        print(f"R={R}: {e}")
