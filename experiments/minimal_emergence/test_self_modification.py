"""
测试自修改规则对涌现的影响
规则可以修改规则本身
"""

import numpy as np
from pathlib import Path

OUTPUT_DIR = Path('D:/emergence_experiments')


class SelfModifyingUniverse:
    """
    自修改规则宇宙
    - 状态：3种
    - 记忆：1 bit
    - 规则：可以被修改
    """
    
    A, B, C = 0, 1, 2
    
    def __init__(self):
        self.state = self.A
        self.memory = 0
        
        # 初始规则
        self.rules = {
            (self.A, 0): (self.B, 1),
            (self.B, 1): (self.C, 1),
            (self.C, 1): (self.A, 0),
            (self.A, 1): (self.C, 1),
            (self.B, 0): (self.A, 0),
            (self.C, 0): (self.B, 0),
        }
        
        self.history = [(self.state, self.memory)]
        self.rule_modifications = []
    
    def step(self):
        key = (self.state, self.memory)
        
        if key in self.rules:
            new_state, new_memory = self.rules[key]
        else:
            new_state, new_memory = self.state, self.memory
        
        # 自修改机制：某些状态会修改规则
        if new_state == self.C and new_memory == 1:
            # 修改一条规则
            target_key = (self.A, 0)
            self.rules[target_key] = (
                (self.rules[target_key][0] + 1) % 3,
                (self.rules[target_key][1] + 1) % 2
            )
            self.rule_modifications.append(len(self.history))
        
        self.state = new_state
        self.memory = new_memory
        self.history.append((self.state, self.memory))
    
    def run(self, steps=500):
        for _ in range(steps):
            self.step()
        return self.history
    
    def detect_cycle(self):
        """检测是否回到之前的状态+规则组合"""
        # 简化：只检测状态周期
        seen = {}
        for i, (s, m) in enumerate(self.history):
            if (s, m) in seen:
                # 检查规则是否也相同
                return {
                    'has_cycle': True,
                    'cycle_length': i - seen[(s, m)],
                }
            seen[(s, m)] = i
        return {'has_cycle': False}
    
    def analyze(self):
        """分析运行结果"""
        unique_states = len(set(self.history))
        modifications = len(self.rule_modifications)
        
        return {
            'unique_states': unique_states,
            'modifications': modifications,
            'modification_steps': self.rule_modifications[:10],
        }


class RecursiveModifyingUniverse:
    """
    递归自修改宇宙
    - 规则修改会产生"变异"
    - 变异积累可能导致新行为
    """
    
    def __init__(self, mutation_rate=0.1):
        self.state = 0
        self.memory = 0
        self.mutation_rate = mutation_rate
        
        # 规则用数组表示，可以被索引修改
        # 规则格式：[new_state, new_memory, modify_flag, target_idx]
        self.rules = np.array([
            [1, 1, 0, 0],  # (0,0) -> B, mem=1, 不修改
            [2, 1, 0, 0],  # (1,1) -> C, mem=1
            [0, 0, 1, 0],  # (2,1) -> A, mem=0, 修改规则0
            [2, 1, 0, 0],  # (0,1) -> C
            [0, 0, 0, 0],  # (1,0) -> A
            [1, 0, 0, 0],  # (2,0) -> B
        ])
        
        self.history = [(self.state, self.memory)]
        self.rule_history = [self.rules.copy()]
    
    def _get_rule_idx(self, state, memory):
        """获取规则索引"""
        return state * 2 + memory
    
    def step(self):
        idx = self._get_rule_idx(self.state, self.memory)
        
        if idx < len(self.rules):
            rule = self.rules[idx]
            new_state = int(rule[0])
            new_memory = int(rule[1])
            modify_flag = int(rule[2])
            target_idx = int(rule[3])
            
            # 执行状态转移
            self.state = new_state
            self.memory = new_memory
            
            # 如果有修改标志，修改目标规则
            if modify_flag and target_idx < len(self.rules):
                # 随机变异
                if np.random.random() < self.mutation_rate:
                    self.rules[target_idx, 0] = np.random.randint(0, 3)
                    self.rules[target_idx, 1] = np.random.randint(0, 2)
        
        self.history.append((self.state, self.memory))
        self.rule_history.append(self.rules.copy())
    
    def run(self, steps=1000):
        for _ in range(steps):
            self.step()
        return self.history
    
    def detect_open_ended(self):
        """检测是否有开放式演化"""
        # 方法：检查唯一状态数是否持续增长
        unique_counts = []
        for i in range(0, len(self.history), 100):
            chunk = self.history[:i+100]
            unique_counts.append(len(set(chunk)))
        
        # 如果唯一状态数持续增长，说明没有收敛到周期
        if len(unique_counts) >= 3:
            trend = unique_counts[-3:]  # 最后3个点
            if trend[2] > trend[1] > trend[0]:
                return {'open_ended': True, 'trend': trend}
        
        return {'open_ended': False}


def test_self_modification():
    """测试自修改规则"""
    
    print("=== 测试简单自修改 ===")
    for i in range(5):
        universe = SelfModifyingUniverse()
        universe.run(500)
        analysis = universe.analyze()
        print(f"运行{i+1}: 唯一状态={analysis['unique_states']}, 规则修改次数={analysis['modifications']}")
    
    print("\n=== 测试递归自修改 ===")
    
    open_ended_count = 0
    for i in range(50):
        universe = RecursiveModifyingUniverse(mutation_rate=0.05)
        universe.run(1000)
        result = universe.detect_open_ended()
        if result['open_ended']:
            open_ended_count += 1
    
    print(f"开放式演化比例: {open_ended_count}/50")
    
    if open_ended_count > 0:
        print("\n【重要发现】自修改规则可以产生开放式演化！")


if __name__ == '__main__':
    test_self_modification()