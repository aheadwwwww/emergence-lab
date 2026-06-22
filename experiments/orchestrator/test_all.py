"""快速测试所有实验"""
from registry import REGISTRY
import time

for name, exp in REGISTRY.items():
    print(f'{name}: ', end='', flush=True)
    try:
        params = exp.generate_params()
        start = time.time()
        result = exp.run(params)
        elapsed = time.time() - start
        img = exp.visualize(result)
        desc = exp.describe(params, result)
        print(f'OK ({elapsed:.1f}s) - {desc[:40]}')
    except Exception as e:
        print(f'FAIL - {e}')
