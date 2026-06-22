"""
参数进化 - 自动寻找"最美"涌现模式
用遗传算法搜索最优参数组合
"""

import numpy as np
import random
from PIL import Image
import time
from pathlib import Path
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from registry import REGISTRY, OUTPUT_DIR

# ===== 适应度函数 =====

def image_entropy(img):
    """计算图像熵 - 衡量视觉复杂度"""
    if img.mode != 'L':
        img = img.convert('L')
    hist = np.array(img.histogram(), dtype=np.float64)
    hist = hist / hist.sum()
    return -np.sum(hist * np.log2(hist + 1e-10))

def non_uniformity(img):
    """非均匀性评分 - 避免全黑或全白"""
    if img.mode != 'L':
        img = img.convert('L')
    arr = np.array(img, dtype=np.float32)
    return np.std(arr) / 255.0

def edge_density(img):
    """边缘密度 - 检测图案丰富度"""
    if img.mode != 'L':
        img = img.convert('L')
    arr = np.array(img, dtype=np.float32)
    dx = np.abs(np.diff(arr, axis=1))
    dy = np.abs(np.diff(arr, axis=0))
    return (np.mean(dx) + np.mean(dy)) / 510.0

def symmetry_score(img):
    """对称性评分"""
    if img.mode != 'L':
        img = img.convert('L')
    arr = np.array(img)
    h, w = arr.shape
    # 左右对称
    left = arr[:, :w//2]
    right = np.fliplr(arr[:, -w//2:])
    min_w = min(left.shape[1], right.shape[1])
    sym_lr = np.mean(np.abs(left[:, :min_w] - right[:, :min_w]))
    # 上下对称
    top = arr[:h//2, :]
    bottom = np.flipud(arr[-h//2:, :])
    min_h = min(top.shape[0], bottom.shape[0])
    sym_ud = np.mean(np.abs(top[:min_h, :] - bottom[:min_h, :]))
    return 1 - (sym_lr + sym_ud) / 510.0

def compute_fitness(record):
    """综合适应度评分"""
    img_path = record.get('image')
    if not img_path or not Path(img_path).exists():
        return 0.0
    
    # 如果是路径字符串，加载图像
    if isinstance(img_path, str):
        try:
            img = Image.open(img_path)
        except:
            return 0.0
    else:
        img = img_path
    
    ent = image_entropy(img)
    nu = non_uniformity(img)
    ed = edge_density(img)
    sym = symmetry_score(img)
    
    # 综合评分：熵 + 边缘 + 非均匀性 + 对称性
    score = (ent * 0.1) + (ed * 3.0) + (nu * 2.0) + (sym * 0.5)
    
    # 惩罚全黑/全白
    if nu < 0.05:
        score *= 0.1
    
    # 耗时惩罚（不让实验跑太久）
    elapsed = record.get('elapsed', 0)
    if elapsed > 30:
        score *= max(0.5, 30.0 / elapsed)
    
    return round(score, 4)

# ===== 参数进化器 =====

class ParameterEvolution:
    """参数进化器"""
    
    def __init__(self, exp_name, population_size=8, generations=3, mutation_rate=0.3):
        self.exp_name = exp_name
        self.exp = REGISTRY[exp_name]
        self.pop_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.best_score = 0
        self.best_params = None
        self.history = []
    
    def mutate_params(self, params):
        """变异参数"""
        new_params = {}
        for key, value in params.items():
            if random.random() < self.mutation_rate:
                if isinstance(value, bool):
                    new_params[key] = random.choice([True, False])
                elif isinstance(value, int):
                    # 整数变异
                    delta = max(1, int(abs(value) * 0.3))
                    new_params[key] = value + random.randint(-delta, delta)
                    # 确保合理范围
                    new_params[key] = max(1, abs(new_params[key]))
                elif isinstance(value, float):
                    # 浮点数变异
                    delta = abs(value) * 0.3
                    new_params[key] = value + random.uniform(-delta, delta)
                    new_params[key] = max(0.001, abs(new_params[key]))
                elif isinstance(value, str):
                    # 字符串变异（枚举类型）
                    choices = {
                        'system': ['lorenz', 'rossler', 'chen'],
                        'rule': [30, 90, 110, 184, 150]
                    }
                    if key in choices:
                        new_params[key] = random.choice(choices[key])
                    else:
                        new_params[key] = value
                else:
                    new_params[key] = value
            else:
                new_params[key] = value
        return new_params
    
    def crossover_params(self, p1, p2):
        """交叉参数"""
        child = {}
        for key in p1:
            if random.random() < 0.5:
                child[key] = p1[key]
            else:
                child[key] = p2[key]
        return child
    
    def run_trial(self, params):
        """运行单个试验"""
        from orchestrator_v2 import OrchestratorV2
        orch = OrchestratorV2(max_workers=1)
        
        # 覆盖参数
        original_generate = self.exp.generate_params
        self.exp.generate_params = lambda: params
        
        try:
            record = orch.run_single(self.exp_name)
            if record:
                fitness = compute_fitness(record)
                return params, fitness, record
        except Exception as e:
            pass
        finally:
            self.exp.generate_params = original_generate
        
        return params, 0, None
    
    def evolve(self):
        """运行进化"""
        print(f'\n=== Parameter Evolution: {self.exp.name} ===')
        print(f'Population: {self.pop_size}, Generations: {self.generations}')
        
        # 第0代：随机初始化
        population = [self.exp.generate_params() for _ in range(self.pop_size)]
        
        for gen in range(self.generations):
            print(f'\nGeneration {gen+1}/{self.generations}')
            
            # 评估适应度
            scored = []
            with ThreadPoolExecutor(max_workers=4) as pool:
                futures = {pool.submit(self.run_trial, p): p for p in population}
                for f in as_completed(futures):
                    params, fitness, record = f.result()
                    scored.append((fitness, params, record))
                    score_str = f'{fitness:.2f}' if fitness > 0 else '0'
                    print(f'  Score: {score_str}')
            
            scored.sort(reverse=True, key=lambda x: x[0])
            
            best_fit, best_params, best_rec = scored[0]
            if best_fit > self.best_score:
                self.best_score = best_fit
                self.best_params = best_params
            
            self.history.append({
                'generation': gen + 1,
                'best_score': best_fit,
                'all_scores': [s[0] for s in scored]
            })
            
            print(f'  Best: {best_fit:.2f}')
            print(f'  Params: {best_params}')
            
            if gen < self.generations - 1:
                # 选择Top 4 + 变异
                top = [s[1] for s in scored[:max(2, self.pop_size//4)]]
                
                # 繁衍
                new_pop = []
                while len(new_pop) < self.pop_size:
                    if random.random() < 0.3:
                        # 直接变异
                        parent = random.choice(top)
                        child = self.mutate_params(parent)
                    else:
                        # 交叉 + 变异
                        p1, p2 = random.sample(top, 2)
                        child = self.mutate_params(self.crossover_params(p1, p2))
                    new_pop.append(child)
                
                population = new_pop
        
        print(f'\n=== Evolution Complete ===')
        print(f'Best score: {self.best_score:.2f}')
        print(f'Best params: {self.best_params}')
        
        return self.best_params, self.best_score, self.history

# ===== 主入口 =====

def main():
    experiments_to_evolve = ['langtons_ant', 'game_of_life', 'sandpile', 'turing_patterns', 'wolfram_ca']
    
    all_results = {}
    
    for exp_name in experiments_to_evolve:
        evo = ParameterEvolution(exp_name, population_size=6, generations=3)
        best_params, best_score, history = evo.evolve()
        all_results[exp_name] = {
            'best_score': best_score,
            'best_params': {k: str(v) if isinstance(v, (float, int)) else v for k, v in best_params.items()},
            'history': history
        }
    
    # 保存结果
    result_path = OUTPUT_DIR / 'evolution_results.json'
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f'\nResults saved to {result_path}')
    print('\n=== Final Results ===')
    for exp_name, res in all_results.items():
        print(f'{exp_name}: score={res["best_score"]}')

if __name__ == '__main__':
    main()
