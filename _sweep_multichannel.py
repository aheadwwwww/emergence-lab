"""
多通道 Lenia 参数扫描
系统地测试不同 (R, mu, sigma) 组合，找生命窗口
"""

import json
import time
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, 'experiments')

from lenia_multichannel import run_lenia_multichannel

# 扫描配置
R_base = 20  # 固定 R，扫描 mu/sigma
mu_range = np.linspace(0.08, 0.22, 5)
sigma_range = np.linspace(0.02, 0.06, 5)

results = []
t0 = time.time()

for i, mu in enumerate(mu_range):
    for j, sigma in enumerate(sigma_range):
        # 三通道用相同参数（简化扫描）
        result = run_lenia_multichannel(
            shape=(256, 256),
            R_list=[R_base, R_base, R_base],
            mu_list=[mu, mu * 1.1, mu * 0.9],  # 稍微错开
            sigma_list=[sigma, sigma * 1.1, sigma * 0.9],
            steps=200,
            record_every=200,
        )
        
        entry = {
            'mu': round(float(mu), 3),
            'sigma': round(float(sigma), 3),
            'state': result['state'],
            **result['stats'],
            'time': result['time'],
        }
        results.append(entry)
        print(f"[{i*len(sigma_range)+j+1}/{len(mu_range)*len(sigma_range)}] mu={mu:.3f} sigma={sigma:.3f} -> {result['state']} alive={result['stats']['alive']:.3f}")

# 保存结果
out_path = Path('experiments/lenia_multichannel_sweep.json')
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nDone. {len(results)} runs in {time.time()-t0:.1f}s")
print(f"Saved to {out_path}")

# 统计
from collections import Counter
states = Counter(r['state'] for r in results)
print(f"State distribution: {dict(states)}")
