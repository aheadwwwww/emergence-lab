import json
from collections import Counter

# Load all three sweeps
sweeps = {}
for R in [11, 20, 30]:
    path = f'experiments/lenia_jax_sweep_R{R}.json'
    try:
        with open(path, 'r') as f:
            sweeps[R] = json.load(f)
    except:
        print(f"Missing: {path}")

for R, data in sweeps.items():
    labels = Counter(r['label'] for r in data)
    scores = [r['score'] for r in data]
    best = max(data, key=lambda x: x['score'])
    print(f"R={R:2d} | {len(data)} runs | dead={labels.get('dead',0)} simple={labels.get('simple',0)} structure={labels.get('structure',0)}")
    print(f"      best: mu={best['mu']:.3f} sigma={best['sigma']:.3f} score={best['score']:.4f}")
    print(f"      struct%: {labels.get('structure',0)/len(data)*100:.1f}%")
    print()

# Phase diagram summary
print("=== Phase Transition Summary ===")
print("R=11: 几乎无结构 (0%), 生命窗口极窄")
print("R=20: 结构爆发 (79.6%), 最佳生命区 mu~0.14-0.22, sigma~0.024-0.04")
print("R=30: 结构回落 (12.0%), 简单模式占主导 (68%), 核太大导致过度平滑")
print()
print("推论: R=20 是当前配置下的 sweet spot")
print("      R>20 需要更大的网格 (>=512) 才能发挥大核优势")
