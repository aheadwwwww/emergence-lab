"""
最小涌现宇宙实验
目标：找到能持续产生新结构的最小规则集合
约束：状态≤3，记忆≤1bit，规则≤5条
"""

import numpy as np
from PIL import Image
from pathlib import Path
import time

OUTPUT_DIR = Path('D:/emergence_experiments')

class MinimalUniverse:
    """
    三态自指机
    - 状态：A, B, C (编码为 0, 1, 2)
    - 记忆：1 bit (0 或 1)
    - 规则：5条
    """
    
    # 状态常量
    A, B, C = 0, 1, 2
    STATE_NAMES = {0: 'A', 1: 'B', 2: 'C'}
    
    def __init__(self, rules=None):
        """
        规则格式：[(当前状态, 记忆值) -> (新状态, 新记忆)]
        """
        if rules is None:
            # 默认规则集
            self.rules = {
                (self.A, 0): (self.B, 1),
                (self.B, 1): (self.C, 1),
                (self.C, 1): (self.A, 0),
                (self.A, 1): (self.C, 1),
                (self.B, 0): (self.A, 0),
            }
        else:
            self.rules = rules
        
        # 初始状态
        self.state = self.A
        self.memory = 0
        self.history = [(self.state, self.memory)]
    
    def step(self):
        """执行一步"""
        key = (self.state, self.memory)
        if key in self.rules:
            self.state, self.memory = self.rules[key]
        else:
            # 默认：保持不变
            pass
        self.history.append((self.state, self.memory))
    
    def run(self, steps=100):
        """运行多步"""
        for _ in range(steps):
            self.step()
        return self.history
    
    def detect_cycle(self):
        """检测周期"""
        seen = {}
        for i, (s, m) in enumerate(self.history):
            if (s, m) in seen:
                cycle_start = seen[(s, m)]
                cycle_length = i - cycle_start
                return {
                    'has_cycle': True,
                    'cycle_start': cycle_start,
                    'cycle_length': cycle_length,
                    'cycle': self.history[cycle_start:i]
                }
            seen[(s, m)] = i
        return {'has_cycle': False}
    
    def complexity_score(self):
        """
        计算复杂度分数
        - 周期长度越长，越复杂
        - 访问的唯一状态越多，越复杂
        """
        unique_states = len(set(self.history))
        cycle_info = self.detect_cycle()
        
        if cycle_info['has_cycle']:
            cycle_len = cycle_info['cycle_length']
            # 复杂度 = 唯一状态数 * 周期长度的对数
            score = unique_states * (1 + np.log1p(cycle_len))
        else:
            score = unique_states
        
        return score


def explore_rule_spaces():
    """探索不同的规则空间"""
    
    results = []
    
    # 规则集1：简单循环
    rules1 = {
        (0, 0): (1, 0),
        (1, 0): (2, 0),
        (2, 0): (0, 0),
        (0, 1): (1, 1),
        (1, 1): (0, 1),
    }
    
    # 规则集2：记忆依赖
    rules2 = {
        (0, 0): (1, 1),
        (1, 1): (2, 1),
        (2, 1): (0, 0),
        (0, 1): (2, 1),
        (1, 0): (0, 0),
    }
    
    # 规则集3：混沌倾向
    rules3 = {
        (0, 0): (1, 1),
        (1, 1): (0, 0),
        (0, 1): (2, 0),
        (2, 0): (1, 1),
        (1, 0): (2, 1),
    }
    
    rule_sets = [
        ('simple_cycle', rules1),
        ('memory_dependent', rules2),
        ('chaotic', rules3),
    ]
    
    for name, rules in rule_sets:
        universe = MinimalUniverse(rules)
        history = universe.run(100)
        cycle = universe.detect_cycle()
        score = universe.complexity_score()
        
        results.append({
            'name': name,
            'rules': rules,
            'cycle': cycle,
            'complexity': score,
            'unique_states': len(set(history)),
        })
        
        print(f"\n=== {name} ===")
        print(f"唯一状态数: {len(set(history))}")
        print(f"复杂度分数: {score:.2f}")
        if cycle['has_cycle']:
            print(f"周期长度: {cycle['cycle_length']}")
            print(f"周期: {[(MinimalUniverse.STATE_NAMES[s], m) for s, m in cycle['cycle']]}")
    
    return results


def visualize_universe(history, name='minimal_universe'):
    """可视化状态序列"""
    n = len(history)
    img = Image.new('RGB', (n * 10, 60), (20, 20, 30))
    pixels = img.load()
    
    colors = {
        (0, 0): (255, 100, 100),  # A, mem=0: 红
        (0, 1): (255, 150, 150),  # A, mem=1: 浅红
        (1, 0): (100, 255, 100),  # B, mem=0: 绿
        (1, 1): (150, 255, 150),  # B, mem=1: 浅绿
        (2, 0): (100, 100, 255),  # C, mem=0: 蓝
        (2, 1): (150, 150, 255),  # C, mem=1: 浅蓝
    }
    
    for i, (state, mem) in enumerate(history[:min(n, 200)]):
        color = colors.get((state, mem), (128, 128, 128))
        for dx in range(10):
            for dy in range(50):
                pixels[i * 10 + dx, dy + 5] = color
    
    path = OUTPUT_DIR / f'{name}_{int(time.time())}.png'
    img.save(path)
    return str(path)


def exhaustive_search():
    """
    穷举所有可能的规则集
    状态空间：3种状态 x 2种记忆 = 6种组合
    每个组合可以映射到6种输出
    总规则数：6^6 = 46656 种
    """
    from itertools import product
    
    # 所有可能的输入状态
    inputs = [(s, m) for s in [0, 1, 2] for m in [0, 1]]
    # 所有可能的输出状态
    outputs = [(s, m) for s in [0, 1, 2] for m in [0, 1]]
    
    results = []
    tested = 0
    
    # 遍历所有可能的规则映射
    for mapping in product(range(6), repeat=6):
        rules = {}
        for i, out_idx in enumerate(mapping):
            rules[inputs[i]] = outputs[out_idx]
        
        universe = MinimalUniverse(rules)
        universe.run(50)
        cycle = universe.detect_cycle()
        score = universe.complexity_score()
        unique = len(set(universe.history))
        
        if cycle['has_cycle'] and cycle['cycle_length'] > 3:
            results.append({
                'rules': rules,
                'cycle_length': cycle['cycle_length'],
                'unique_states': unique,
                'complexity': score,
            })
        
        tested += 1
        if tested % 5000 == 0:
            print(f"已测试 {tested}/46656...")
    
    print(f"\n总共测试: {tested} 种规则集")
    print(f"找到周期>3的: {len(results)} 种")
    
    # 按复杂度排序
    results.sort(key=lambda x: x['complexity'], reverse=True)
    
    return results[:10]  # 返回前10个最复杂的


if __name__ == '__main__':
    print("=== 最小涌现宇宙实验 ===\n")
    
    # 阶段1：穷举搜索
    print("阶段1：穷举搜索所有规则集...\n")
    top_results = exhaustive_search()
    
    if top_results:
        print("\n=== 最复杂的10个规则集 ===")
        for i, r in enumerate(top_results):
            print(f"\n{i+1}. 周期长度: {r['cycle_length']}, 唯一状态: {r['unique_states']}, 复杂度: {r['complexity']:.2f}")
        
        best = top_results[0]
        universe = MinimalUniverse(best['rules'])
        history = universe.run(100)
        img_path = visualize_universe(history, 'minimal_best')
        print(f"\n可视化保存到: {img_path}")
    
    # 阶段2：放宽约束，测试记忆位数
    print("\n\n=== 阶段2：增加记忆位数 ===")
    print("测试记忆位数从1增加到2...")
    
    # 阶段3：放宽约束，测试状态数
    print("\n\n=== 阶段3：增加状态数 ===")
    print("测试状态数从3增加到4...")
