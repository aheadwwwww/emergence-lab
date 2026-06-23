"""
测试反馈对涌现的影响
加入环境反馈：系统的输出会影响下一次的规则选择
"""

import numpy as np
from pathlib import Path

OUTPUT_DIR = Path('D:/emergence_experiments')


class FeedbackUniverse:
    """
    带反馈的最小宇宙
    - 状态：3种
    - 记忆：1 bit
    - 反馈：输出影响下一步的规则选择
    """
    
    A, B, C = 0, 1, 2
    
    def __init__(self):
        self.state = self.A
        self.memory = 0
        
        # 两套规则，根据输出切换
        self.rules_a = self._generate_rules('simple')
        self.rules_b = self._generate_rules('alternate')
        self.current_rules = self.rules_a
        
        self.history = [(self.state, self.memory)]
        self.rule_history = ['A']
    
    def _generate_rules(self, mode='simple'):
        if mode == 'simple':
            return {
                (self.A, 0): (self.B, 1),
                (self.B, 1): (self.C, 1),
                (self.C, 1): (self.A, 0),
                (self.A, 1): (self.C, 1),
                (self.B, 0): (self.A, 0),
                (self.C, 0): (self.B, 0),
            }
        else:
            return {
                (self.A, 0): (self.C, 1),
                (self.C, 1): (self.B, 0),
                (self.B, 0): (self.A, 1),
                (self.A, 1): (self.B, 1),
                (self.B, 1): (self.C, 0),
                (self.C, 0): (self.A, 0),
            }
    
    def step(self):
        key = (self.state, self.memory)
        if key in self.current_rules:
            new_state, new_memory = self.current_rules[key]
        else:
            new_state, new_memory = self.state, self.memory
        
        # 反馈机制：根据输出切换规则集
        if new_memory == 1:
            self.current_rules = self.rules_b
            rule_label = 'B'
        else:
            self.current_rules = self.rules_a
            rule_label = 'A'
        
        self.state = new_state
        self.memory = new_memory
        self.history.append((self.state, self.memory))
        self.rule_history.append(rule_label)
    
    def run(self, steps=200):
        for _ in range(steps):
            self.step()
        return self.history
    
    def detect_cycle(self):
        # 检测（状态，记忆，规则集）的周期
        combined = list(zip(self.history, self.rule_history))
        seen = {}
        for i, item in enumerate(combined):
            if item in seen:
                cycle_start = seen[item]
                cycle_length = i - cycle_start
                return {
                    'has_cycle': True,
                    'cycle_length': cycle_length,
                }
            seen[item] = i
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


class EnvironmentFeedbackUniverse:
    """
    更强的反馈：环境状态影响系统
    - 系统：3状态 + 1bit记忆
    - 环境：简单的计数器（0-3循环）
    - 反馈：环境状态改变规则选择
    """
    
    def __init__(self):
        self.state = 0
        self.memory = 0
        self.env = 0  # 环境状态
        
        # 4套规则，根据环境状态选择
        self.rules = self._generate_all_rules()
        
        self.history = [(self.state, self.memory, self.env)]
    
    def _generate_all_rules(self):
        import random
        rules = {}
        for env_state in range(4):
            rules[env_state] = {}
            for s in range(3):
                for m in [0, 1]:
                    rules[env_state][(s, m)] = (
                        random.randint(0, 2),
                        random.randint(0, 1)
                    )
        return rules
    
    def step(self):
        # 根据当前环境选择规则
        current_rules = self.rules[self.env]
        key = (self.state, self.memory)
        
        if key in current_rules:
            self.state, self.memory = current_rules[key]
        
        # 环境反馈：根据系统输出更新环境
        if self.memory == 1:
            self.env = (self.env + 1) % 4  # 推进环境
        else:
            self.env = (self.env - 1) % 4  # 回退环境
        
        self.history.append((self.state, self.memory, self.env))
    
    def run(self, steps=500):
        for _ in range(steps):
            self.step()
        return self.history
    
    def detect_cycle(self):
        seen = {}
        for i, state in enumerate(self.history):
            if state in seen:
                cycle_start = seen[state]
                cycle_length = i - cycle_start
                return {
                    'has_cycle': True,
                    'cycle_length': cycle_length,
                }
            seen[state] = i
        return {'has_cycle': False}


def test_feedback():
    """测试不同反馈机制的影响"""
    
    print("=== 测试简单反馈 ===")
    universe1 = FeedbackUniverse()
    universe1.run(100)
    cycle1 = universe1.detect_cycle()
    print(f"周期: {cycle1.get('cycle_length', '未检测到')}")
    
    print("\n=== 测试环境反馈 ===")
    
    # 测试100次，记录最大周期
    max_cycles = []
    for i in range(100):
        universe2 = EnvironmentFeedbackUniverse()
        universe2.run(500)
        cycle2 = universe2.detect_cycle()
        if cycle2['has_cycle']:
            max_cycles.append(cycle2['cycle_length'])
        if (i + 1) % 20 == 0:
            print(f"已测试 {i+1}/100...")
    
    if max_cycles:
        print(f"\n平均周期: {np.mean(max_cycles):.1f}")
        print(f"最大周期: {np.max(max_cycles)}")
        
        # 状态空间 = 3状态 × 2记忆 × 4环境 = 24
        state_space = 24
        ratio = np.max(max_cycles) / state_space
        print(f"周期/状态空间比率: {ratio:.2f}")
        
        if np.max(max_cycles) > state_space:
            print("\n【重要发现】周期超过状态空间！")
            print("这说明系统产生了更复杂的动力学")
    else:
        print("未检测到周期（可能在开放式演化）")


if __name__ == '__main__':
    print("=== 测试更强反馈：环境状态=8 ===")
    
    max_cycles = []
    for i in range(200):
        # 环境0-7循环，状态空间=3×2×8=48
        env_universe = EnvironmentFeedbackUniverse()
        env_universe.env = 0
        env_universe.rules = {}
        for env_state in range(8):
            env_universe.rules[env_state] = {}
            for s in range(3):
                for m in [0, 1]:
                    env_universe.rules[env_state][(s, m)] = (
                        hash(f"{i}_{env_state}_{s}_{m}") % 3,
                        hash(f"{i}_{env_state}_{s}_{m}_m") % 2
                    )
        
        env_universe.run(1000)
        cycle = env_universe.detect_cycle()
        if cycle['has_cycle']:
            max_cycles.append(cycle['cycle_length'])
    
    if max_cycles:
        print(f"平均周期: {np.mean(max_cycles):.1f}")
        print(f"最大周期: {np.max(max_cycles)}")
        print(f"状态空间: 48")
        
        if np.max(max_cycles) > 48:
            print("\n【发现】周期超过状态空间！")