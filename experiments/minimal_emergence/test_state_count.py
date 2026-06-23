"""
测试状态数对涌现的影响
"""

import numpy as np
from itertools import product
from pathlib import Path

OUTPUT_DIR = Path('D:/emergence_experiments')


class ExtendedStateUniverse:
    """
    扩展状态数的宇宙
    - 状态：n 种（可配置）
    - 记忆：1 bit
    """
    
    def __init__(self, num_states=4, rules=None):
        self.num_states = num_states
        
        if rules is None:
            self.rules = self._generate_random_rules()
        else:
            self.rules = rules
        
        self.state = 0
        self.memory = 0
        self.history = [(self.state, self.memory)]
    
    def _generate_random_rules(self):
        import random
        rules = {}
        for s in range(self.num_states):
            for m in [0, 1]:
                new_s = random.randint(0, self.num_states - 1)
                new_m = random.randint(0, 1)
                rules[(s, m)] = (new_s, new_m)
        return rules
    
    def step(self):
        key = (self.state, self.memory)
        if key in self.rules:
            self.state, self.memory = self.rules[key]
        self.history.append((self.state, self.memory))
    
    def run(self, steps=200):
        for _ in range(steps):
            self.step()
        return self.history
    
    def detect_cycle(self):
        seen = {}
        for i, (s, m) in enumerate(self.history):
            if (s, m) in seen:
                cycle_start = seen[(s, m)]
                cycle_length = i - cycle_start
                return {
                    'has_cycle': True,
                    'cycle_start': cycle_start,
                    'cycle_length': cycle_length,
                }
            seen[(s, m)] = i
        return {'has_cycle': False}
    
    def complexity_score(self):
        unique_states = len(set(self.history))
        cycle_info = self.detect_cycle()
        
        if cycle_info['has_cycle']:
            cycle_len = cycle_info['cycle_length']
            score = unique_states * (1 + np.log1p(cycle_len))
        else:
            score = unique_states
        
        return score


def test_state_count():
    """测试不同状态数的影响"""
    
    results = []
    
    for num_states in [3, 4, 5, 6, 7, 8]:
        print(f"\n=== 状态数: {num_states} ===")
        state_space = num_states * 2  # 状态数 × 记忆位数(2)
        print(f"状态空间大小: {state_space}")
        
        # 随机采样1000种规则集
        max_cycles = []
        for _ in range(1000):
            universe = ExtendedStateUniverse(num_states=num_states)
            universe.run(200)
            cycle = universe.detect_cycle()
            if cycle['has_cycle']:
                max_cycles.append(cycle['cycle_length'])
        
        if max_cycles:
            avg_cycle = np.mean(max_cycles)
            max_cycle = np.max(max_cycles)
            print(f"平均周期长度: {avg_cycle:.1f}")
            print(f"最大周期长度: {max_cycle}")
            
            results.append({
                'num_states': num_states,
                'state_space': state_space,
                'avg_cycle': avg_cycle,
                'max_cycle': max_cycle,
            })
    
    return results


if __name__ == '__main__':
    print("=== 状态数对涌现的影响 ===\n")
    
    results = test_state_count()
    
    print("\n\\n=== 总结 ===")
    print("状态数 | 状态空间 | 平均周期 | 最大周期")
    print("-" * 50)
    for r in results:
        print(f"{r['num_states']}      | {r['state_space']}      | {r['avg_cycle']:.1f}    | {r['max_cycle']}")
    
    # 分析趋势
    print("\n\\n=== 分析 ===")
    if len(results) >= 2:
        # 检查周期是否随状态数增长
        cycles = [r['max_cycle'] for r in results]
        state_spaces = [r['state_space'] for r in results]
        
        # 计算比率
        ratios = [c / s for c, s in zip(cycles, state_spaces)]
        avg_ratio = np.mean(ratios)
        
        print(f"周期/状态空间 平均比率: {avg_ratio:.2f}")
        
        if avg_ratio > 0.5:
            print("周期约占状态空间的一半以上")
            print("说明系统能有效探索状态空间")
        else:
            print("周期远小于状态空间")
            print("说明大部分规则集限制了探索")