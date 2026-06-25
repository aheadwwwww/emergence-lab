"""
Lenia Multi-Channel Parameter Scan
Scan different RGB parameter combinations to find best configurations.
"""

import jax
import jax.numpy as jnp
import numpy as np
from pathlib import Path
import time

from lenia_multichannel import run_lenia_multichannel

np.set_printoptions(precision=3)

print('=== Lenia Multi-Channel Parameter Scan ===')
print('Goal: Find best RGB parameter combinations\n')

# Test configurations: different R and growth params per channel
configs = [
    # Name, R_list, mu_list, sigma_list
    ('uniform', [15,15,15], [0.15,0.15,0.15], [0.015,0.015,0.015]),
    ('diverse-small', [12,15,18], [0.12,0.15,0.18], [0.012,0.015,0.018]),
    ('diverse-wide', [12,15,18], [0.15,0.15,0.15], [0.025,0.015,0.008]),
    ('sweet-spot', [20,20,20], [0.22,0.22,0.22], [0.04,0.04,0.04]),
    ('mixed-sweet', [18,20,22], [0.20,0.22,0.24], [0.035,0.04,0.045]),
    ('high-diversity', [10,20,30], [0.10,0.22,0.30], [0.01,0.04,0.06]),
]

results = []

for name, R_list, mu_list, sigma_list in configs:
    print(f'Testing {name}...')
    
    # Run simulation
    start = time.time()
    result = run_lenia_multichannel(
        shape=(64, 64),
        R_list=R_list,
        mu_list=mu_list,
        sigma_list=sigma_list,
        steps=200,
        init='random',
        record_every=50,
        save_timeline=None
    )
    elapsed = time.time() - start
    
    final_grid = result['final']  # (C, H, W)
    
    # Analyze final state
    alive = float(np.mean(final_grid > 0.1))
    variance = float(np.std(final_grid))
    
    # Channel-wise analysis
    channel_stats = []
    for c in range(3):
        ch = final_grid[c]
        ch_alive = float(np.mean(ch > 0.1))
        ch_std = float(np.std(ch))
        channel_stats.append((ch_alive, ch_std))
    
    result = {
        'name': name,
        'alive': alive,
        'variance': variance,
        'channels': channel_stats,
        'time': elapsed
    }
    results.append(result)
    
    ch_str = ', '.join([f'R{c}:{stats[0]:.2f}' for c, stats in enumerate(channel_stats)])
    print(f'  alive={alive:.3f} | var={variance:.4f} | [{ch_str}] | {elapsed:.2f}s')

# Find best
best = max(results, key=lambda r: r['alive'] + r['variance'])
print(f'\n=== Result ===')
print(f'Best config: {best["name"]}')
print(f'  alive={best["alive"]:.3f}, variance={best["variance"]:.4f}')
print(f'  Channel stats: {best["channels"]}')
print('\nKey insight: Diverse parameters → diverse structures → ecosystem emergence')