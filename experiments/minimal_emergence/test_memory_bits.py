"""
测试记忆位数对涌现的影响
"""

import numpy as np
from minimal_universe import MinimalUniverse, visualize_universe
from itertools import product
from pathlib import Path

OUTPUT_DIR = Path('D:/emergence_experiments')


class ExtendedMemoryUniverse:
    """
    扩展记忆位数的宇宙
    - 状态：A, B, C (3种)
    - 记忆：n bits (可配置)
    """
    
    A, B, C = 0, 1, 2
    
    def __init__(self, memory_bits=2, rules=None):
        self.memory_bits = memory_bits
        self.memory_max = 2 ** memory_bits  # 可能的记忆值数量
        
        if rules is None:
            # 生成默认规则（随机）
            self.rules = self._generate_random_rules()
        else:
            self.rules = rules
        
        self.state = self.A
        self.memory = 0
        self.history = [(self.state, self.memory)]
    
    def _generate_random_rules(self):
        """随机生成规则"""
        import random
        rules = {}
        for s in [self.A, self.B, self.C]:
            for m in range(self.memory_max):
                new_s = random.choice([self.A, self.B, self.C])
                new_m = random.randint(0, self.memory_max - 1)
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


def test_memory_bits():
    """测试不同记忆位数的影响"""
    
    results = []
    
    for bits in [1, 2, 3, 4]:
        print(f"\n=== 记忆位数: {bits} ===")
        state_space = 3 * (2 ** bits)
        print(f"状态空间大小: {state_space}")
        
        # 随机采样1000种规则集
        max_cycles = []
        for _ in range(1000):
            universe = ExtendedMemoryUniverse(memory_bits=bits)
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
                'bits': bits,
                'state_space': state_space,
                'avg_cycle': avg_cycle,
                'max_cycle': max_cycle,
            })
        else:
            print("未检测到周期")
    
    return results


if __name__ == '__main__':
    print("=== 记忆位数对涌现的影响 ===\n")
    
    results = test_memory_bits()
    
    print("\n\\n=== 总结 ===")
    print("记忆位数 | 状态空间 | 平均周期 | 最大周期")
    print("-" * 50)
    for r in results:
        print(f"{r['bits']} bits   | {r['state_space']}      | {r['avg_cycle']:.1f}    | {r['max_cycle']}")
    
    # 结论
    print("\n\\n=== 结论 ===")
    if results:
        best = max(results, key=lambda x: x['max_cycle'])
        print(f"记忆位数 {best['bits']} 产生最长周期 {best['max_cycle']}")
        
        # 判断是否接近状态空间上限
        ratio = best['max_cycle'] / best['state_space']
        if ratio > 0.8:
            print("周期接近状态空间上限，说明系统能遍历大部分状态")
            print("但仍然没有开放式涌现（周期是有限的）")
        else:
            print("周期远小于状态空间，说明规则限制了探索")