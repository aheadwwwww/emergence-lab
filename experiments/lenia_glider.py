"""
Lenia Glider Gallery

探索 Lenia 中的滑翔机和复杂模式。
基于 Bert Chan 发现的经典参数。
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from emergence_lab import Lenia
from emergence_lab.core.metrics import EmergenceMetrics


# Classic Lenia creatures (R, mu, sigma)
CREATURES = {
    'Orbium': {'R': 13, 'mu': 0.15, 'sigma': 0.014},
    'Geminium': {'R': 12, 'mu': 0.15, 'sigma': 0.013},
    'Hydrogeminium': {'R': 14, 'mu': 0.26, 'sigma': 0.036},
    'Scutium': {'R': 18, 'mu': 0.147, 'sigma': 0.015},
    'Gyroginium': {'R': 14, 'mu': 0.175, 'sigma': 0.027},
    'Smooth_life': {'R': 10, 'mu': 0.267, 'sigma': 0.045},
}


def make_orbium_seed(shape, R=13):
    """创建 Orbium 种子"""
    h, w = shape
    grid = np.zeros((h, w), dtype=np.float32)
    
    # Orbium pattern (simplified from Bert Chan's code)
    cy, cx = h // 2, w // 2
    r = R
    
    # Ring pattern
    for i in range(-r, r+1):
        for j in range(-r, r+1):
            dist = np.sqrt(i**2 + j**2)
            if dist < r:
                # Orbium core shape
                ring = np.exp(-((dist - r*0.5)**2) / (r*0.3)**2)
                grid[cy+i, cx+j] = ring * 0.5 + 0.1
    
    return grid


def run_glider_test(creature_name, steps=500, shape=(256, 256)):
    """测试特定生物"""
    params = CREATURES[creature_name]
    
    lenia = Lenia(**params)
    lenia.init_grid(shape=shape, mode='random')
    
    # Add orbium-like seed in center
    h, w = shape
    cy, cx = h // 2, w // 2
    seed = make_orbium_seed((64, 64), R=params['R'])
    sh, sw = seed.shape
    lenia.grid = lenia.grid.at[cy-sh//2:cy+sh//2, cx-sw//2:cx+sw//2].set(
        jnp.array(seed)
    )
    
    print(f"\nTesting {creature_name}: R={params['R']}, mu={params['mu']}, sigma={params['sigma']}")
    
    result = lenia.run(steps=steps, record_every=50, verbose=True)
    
    return lenia, result


def sweep_creatures(output_dir='output/lenia_creatures'):
    """测试所有生物并保存结果"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    for name in CREATURES:
        try:
            lenia, result = run_glider_test(name)
            results[name] = result
            print(f"  → {name}: alive={result['alive']:.3f}, score={result['emergence_score']:.3f}")
        except Exception as e:
            print(f"  → {name}: ERROR - {e}")
            results[name] = {'error': str(e)}
    
    # Summary
    print("\n" + "="*60)
    print("CREATURE SWEEP SUMMARY")
    print("="*60)
    for name, res in results.items():
        if 'error' in res:
            print(f"{name:<20}: ERROR - {res['error'][:30]}")
        else:
            print(f"{name:<20}: alive={res['alive']:.3f} score={res['emergence_score']:.3f}")
    
    return results


if __name__ == '__main__':
    import jax.numpy as jnp  # Need to import for lenia.grid.at
    
    results = sweep_creatures()