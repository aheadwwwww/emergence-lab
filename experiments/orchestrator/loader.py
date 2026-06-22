"""
统一实验加载器 - 自动发现和注册所有实验
"""

import importlib.util
import inspect
import sys
from pathlib import Path

# 实验基类定义
EXPERIMENT_BASE = "Experiment"

def discover_experiments(experiments_dir):
    """自动发现 experiments 目录下的所有实验"""
    experiments = {}
    exp_dir = Path(experiments_dir)
    
    # 添加核心实验目录
    search_dirs = [exp_dir]
    for subdir in exp_dir.iterdir():
        if subdir.is_dir() and (subdir / '__init__.py').exists():
            search_dirs.append(subdir)
    
    for search_dir in search_dirs:
        for f in sorted(search_dir.glob('*.py')):
            if f.name.startswith('__') or f.name.startswith('orchestrator'):
                continue
            
            # 动态导入
            spec = importlib.util.spec_from_file_location(f.stem, str(f))
            if spec is None or spec.loader is None:
                continue
            
            try:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 查找 Experiment 子类
                for name, cls in inspect.getmembers(module, inspect.isclass):
                    if (name != EXPERIMENT_BASE and 
                        hasattr(cls, 'name') and 
                        hasattr(cls, 'run') and
                        hasattr(cls, 'visualize')):
                        experiments[cls.name] = cls
                        print(f'  [OK] {name} -> {cls.name}')
            except Exception as e:
                print(f'  [ERR] {f.name}: {e}')
    
    return experiments

if __name__ == '__main__':
    print('Discovering experiments...')
    exps = discover_experiments('D:/openclaw_workspace/experiments')
    print(f'\nFound {len(exps)} experiments:')
    for name, cls in exps.items():
        print(f'  {name}: {cls.__name__}')
