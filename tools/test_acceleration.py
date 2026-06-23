"""
测试实验加速方案
比较不同实现方式的性能
"""

import numpy as np
import time
from pathlib import Path
import sys

sys.path.insert(0, 'experiments/orchestrator')
from registry import LangtonsAnt, GameOfLife, Sandpile

def benchmark_experiment(experiment_class, num_runs=3):
    """测试实验运行时间"""
    exp = experiment_class()
    
    times = []
    for i in range(num_runs):
        params = exp.generate_params()
        
        start = time.time()
        result = exp.run(params)
        elapsed = time.time() - start
        
        times.append(elapsed)
        print(f"  Run {i+1}: {elapsed:.3f}s")
    
    avg = np.mean(times)
    std = np.std(times)
    print(f"  Average: {avg:.3f}s ± {std:.3f}s")
    return avg

if __name__ == '__main__':
    print("=== Experiment Performance Benchmark ===\n")
    
    experiments = [
        ("Langton's Ant", LangtonsAnt),
        ("Game of Life", GameOfLife),
        ("Sandpile", Sandpile),
    ]
    
    results = {}
    for name, exp_class in experiments:
        print(f"{name}:")
        avg = benchmark_experiment(exp_class, num_runs=3)
        results[name] = avg
        print()
    
    print("\n=== Summary ===")
    for name, avg in results.items():
        print(f"{name}: {avg:.3f}s")
    
    print("\n=== Next Steps ===")
    print("- Install JAX for GPU acceleration")
    print("- Use Numba for JIT compilation")
    print("- Implement parallel experiments with multiprocessing")
