"""
模型对比实验

对比 Lenia、NCA、PheromoneCA 的涌现特征。
"""

import numpy as np
import time
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from emergence_lab import Lenia, NCA, PheromoneCA
from emergence_lab.core.metrics import EmergenceMetrics


def run_comparison(shape=(128, 128), steps=100, verbose=True):
    """运行三模型对比实验
    
    Returns:
        dict: 各模型的涌现度量
    """
    results = {}
    
    # 1. Lenia
    if verbose:
        print("\n" + "="*50)
        print("Testing Lenia...")
        print("="*50)
    
    lenia = Lenia(R=20, mu=0.15, sigma=0.03)
    lenia.init_grid(shape=shape)
    
    t0 = time.time()
    lenia_result = lenia.run(steps=steps, verbose=verbose)
    lenia_time = time.time() - t0
    
    results['lenia'] = {
        **lenia_result,
        'time': lenia_time,
        'history_len': len(lenia.history),
    }
    
    # 2. NCA
    if verbose:
        print("\n" + "="*50)
        print("Testing NCA...")
        print("="*50)
    
    nca = NCA(channels=16, fire_rate=0.5)
    nca.init_grid(shape=shape)
    
    t0 = time.time()
    nca_result = nca.run(steps=steps, verbose=verbose)
    nca_time = time.time() - t0
    
    results['nca'] = {
        **nca_result,
        'time': nca_time,
        'history_len': len(nca.history),
    }
    
    # 3. PheromoneCA
    if verbose:
        print("\n" + "="*50)
        print("Testing PheromoneCA...")
        print("="*50)
    
    pher = PheromoneCA(channels=3, R=12)
    pher.init_grid(shape=shape)
    
    t0 = time.time()
    pher_result = pher.run(steps=steps, verbose=verbose)
    pher_time = time.time() - t0
    
    results['pheromone'] = {
        **pher_result,
        'time': pher_time,
        'history_len': len(pher.history),
    }
    
    return results


def print_comparison(results):
    """打印对比表格"""
    print("\n" + "="*70)
    print("EMERGENCE COMPARISON")
    print("="*70)
    print(f"{'Model':<15} {'Alive':>10} {'Entropy':>10} {'Edge':>10} {'Score':>10} {'Time':>10}")
    print("-"*70)
    
    for name, data in results.items():
        alive = data.get('alive', 0)
        entropy = data.get('entropy', 0)
        edge = data.get('edge_density', 0)
        score = data.get('emergence_score', 0)
        time_s = data.get('time', 0)
        
        print(f"{name:<15} {alive:>10.3f} {entropy:>10.3f} {edge:>10.3f} {score:>10.3f} {time_s:>10.2f}s")
    
    print("="*70)


if __name__ == '__main__':
    results = run_comparison(shape=(128, 128), steps=100, verbose=True)
    print_comparison(results)
