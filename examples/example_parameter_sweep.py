"""
Example 2: Parameter Sweep

扫描参数空间，找到最佳涌现窗口。
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from emergence_lab import Lenia
import json

# 参数范围
R_values = [11, 13, 15, 20, 25]
mu_values = [0.12, 0.14, 0.16]
sigma_values = [0.02, 0.03, 0.04]

results = []

print("扫描参数空间...")
for R in R_values:
    for mu in mu_values:
        for sigma in sigma_values:
            lenia = Lenia(R=R, mu=mu, sigma=sigma)
            lenia.init_grid(shape=(128, 128), mode='random')
            result = lenia.run(steps=100, record_every=100, verbose=False)
            
            entry = {
                'R': R,
                'mu': mu,
                'sigma': sigma,
                'state': result['state'],
                'score': result['emergence_score'],
                'alive': result['alive']
            }
            results.append(entry)
            print(f"R={R}, mu={mu:.2f}, sigma={sigma:.2f} -> score={result['emergence_score']:.2f}")

# 找最佳参数
best = max(results, key=lambda x: x['score'])
print(f"\n最佳参数: R={best['R']}, mu={best['mu']:.2f}, sigma={best['sigma']:.2f}")
print(f"涌现评分: {best['score']:.3f}")

# 保存结果
with open('examples/output/lenia_sweep_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print("保存结果到 output/lenia_sweep_results.json")