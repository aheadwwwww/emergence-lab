"""
并行运行多个涌现实验
展示编排器的并行能力
"""

import sys
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, 'experiments/orchestrator')
from registry import REGISTRY

def run_single_experiment(name, experiment_class_or_instance):
    """运行单个实验"""
    # Handle both class and instance
    if isinstance(experiment_class_or_instance, type):
        exp = experiment_class_or_instance()
    else:
        exp = experiment_class_or_instance
    params = exp.generate_params()
    
    start = time.time()
    result = exp.run(params)
    elapsed = time.time() - start
    
    # 可视化
    img = exp.visualize(result)
    path = exp.save_image(img)
    
    return {
        'name': name,
        'description': exp.describe(params, result),
        'time': elapsed,
        'image_path': path
    }

def run_parallel_experiments(num_experiments=9, max_workers=3):
    """并行运行多个实验"""
    print(f"=== Running {num_experiments} Experiments in Parallel ===\n")
    
    # 选择实验
    experiments = list(REGISTRY.items())[:num_experiments]
    
    start_time = time.time()
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        futures = {
            executor.submit(run_single_experiment, name, exp_class): name
            for name, exp_class in experiments
        }
        
        # 收集结果
        for future in as_completed(futures):
            name = futures[future]
            try:
                result = future.result()
                results.append(result)
                print(f"+ {result['name']}: {result['time']:.3f}s")
                print(f"  {result['description']}")
                print(f"  Image: {result['image_path']}\n")
            except Exception as e:
                print(f"X {name}: Error - {e}\n")
    
    total_time = time.time() - start_time
    
    # 汇总
    print("=" * 60)
    print(f"Total Time: {total_time:.3f}s")
    print(f"Experiments Run: {len(results)}")
    print(f"Average per Experiment: {total_time/len(results):.3f}s")
    print(f"Parallelism: {max_workers} workers")
    print("\nGenerated Images:")
    for r in results:
        print(f"  - {r['image_path']}")
    
    return results

if __name__ == '__main__':
    results = run_parallel_experiments(num_experiments=9, max_workers=3)