"""
进化式自修改规则
引入选择压力：保留"成功"的变异
"""

import numpy as np
from pathlib import Path

OUTPUT_DIR = Path('D:/emergence_experiments')


class EvolvingUniverse:
    """
    进化式宇宙
    - 规则会变异
    - 变异会被选择（基于某种适应度）
    - 保留高适应度的规则集
    """
    
    def __init__(self, state_count=3, memory_bits=1):
        self.state_count = state_count
        self.memory_max = 2 ** memory_bits
        
        # 初始规则：随机
        self.rules = self._random_rules()
        
        # 历史和适应度
        self.state = 0
        self.memory = 0
        self.history = []
        self.fitness_history = []
        
        # 进化记录
        self.generation = 0
        self.best_rules = self.rules.copy()
        self.best_fitness = 0
    
    def _random_rules(self):
        rules = {}
        for s in range(self.state_count):
            for m in range(self.memory_max):
                rules[(s, m)] = (
                    np.random.randint(0, self.state_count),
                    np.random.randint(0, self.memory_max)
                )
        return rules
    
    def step(self):
        key = (self.state, self.memory)
        if key in self.rules:
            self.state, self.memory = self.rules[key]
        self.history.append((self.state, self.memory))
    
    def calculate_fitness(self):
        """
        适应度函数：
        - 唯一状态数越多越好
        - 周期长度越长越好
        - 但不要重复太频繁
        """
        unique = len(set(self.history[-100:]))  # 最近100步的唯一状态
        
        # 简单适应度：唯一状态数
        return unique
    
    def mutate(self):
        """随机变异一条规则"""
        keys = list(self.rules.keys())
        key = keys[np.random.randint(len(keys))]
        
        # 变异
        old_val = self.rules[key]
        self.rules[key] = (
            np.random.randint(0, self.state_count),
            np.random.randint(0, self.memory_max)
        )
        
        return key, old_val
    
    def run_generation(self, steps=200):
        """运行一代"""
        # 重置状态
        self.state = 0
        self.memory = 0
        self.history = []
        
        # 运行
        for _ in range(steps):
            self.step()
        
        # 计算适应度
        fitness = self.calculate_fitness()
        self.fitness_history.append(fitness)
        
        # 选择：如果适应度提高，保留变异
        if fitness > self.best_fitness:
            self.best_fitness = fitness
            self.best_rules = self.rules.copy()
        
        return fitness
    
    def evolve(self, generations=100):
        """进化多代"""
        for gen in range(generations):
            # 运行当前规则
            fitness = self.run_generation()
            
            # 变异
            self.mutate()
            
            # 测试变异后的适应度
            new_fitness = self.run_generation()
            
            # 选择：保留更好的
            if new_fitness < fitness:
                # 恢复
                self.rules = self.best_rules.copy()
            
            self.generation += 1
            
            if (gen + 1) % 20 == 0:
                print(f"代 {gen+1}: 最佳适应度 {self.best_fitness}")
        
        return self.best_fitness, self.best_rules


class MetaEvolvingUniverse:
    """
    元进化宇宙
    - 规则不仅决定状态转移，还决定何时变异
    - 进化策略本身也在进化
    """
    
    def __init__(self):
        self.state = 0
        self.memory = 0
        
        # 主规则
        self.rules = {
            (0, 0): (1, 1),
            (1, 1): (2, 0),
            (2, 0): (0, 1),
            (0, 1): (2, 0),
            (1, 0): (0, 0),
            (2, 1): (1, 1),
        }
        
        # 元规则：何时触发变异
        self.meta_rules = {
            'trigger_states': [2],  # 在状态2时触发变异
            'mutation_target': [(0, 0)],  # 变异的目标规则
        }
        
        self.history = []
        self.mutations = []
    
    def step(self):
        key = (self.state, self.memory)
        
        # 主规则执行
        if key in self.rules:
            new_state, new_memory = self.rules[key]
        else:
            new_state, new_memory = self.state, self.memory
        
        # 元规则：检查是否触发变异
        if new_state in self.meta_rules['trigger_states']:
            target = self.meta_rules['mutation_target'][0]
            if target in self.rules:
                # 变异：小幅度修改
                old = self.rules[target]
                self.rules[target] = (
                    (old[0] + np.random.choice([-1, 0, 1])) % 3,
                    (old[1] + np.random.choice([-1, 0, 1])) % 2
                )
                self.mutations.append((len(self.history), target, old, self.rules[target]))
        
        self.state = new_state
        self.memory = new_memory
        self.history.append((self.state, self.memory))
    
    def run(self, steps=2000):
        for _ in range(steps):
            self.step()
        return self.history
    
    def analyze(self):
        """分析进化结果"""
        unique_states = len(set(self.history))
        mutation_count = len(self.mutations)
        
        # 检查是否产生新模式
        chunks = []
        chunk_size = 100
        for i in range(0, len(self.history), chunk_size):
            chunk = self.history[i:i+chunk_size]
            chunks.append(set(chunk))
        
        # 新模式：后期的唯一状态比前期多
        early_unique = len(chunks[0]) if chunks else 0
        late_unique = len(chunks[-1]) if chunks else 0
        
        return {
            'unique_states': unique_states,
            'mutations': mutation_count,
            'early_unique': early_unique,
            'late_unique': late_unique,
            'innovation': late_unique > early_unique,
        }


def test_evolution():
    """测试进化式系统"""
    
    print("=== 测试简单进化 ===")
    universe1 = EvolvingUniverse()
    best_fitness, best_rules = universe1.evolve(generations=50)
    print(f"最终最佳适应度: {best_fitness}")
    
    print("\n=== 测试元进化 ===")
    
    innovations = 0
    for i in range(20):
        universe2 = MetaEvolvingUniverse()
        universe2.run(2000)
        analysis = universe2.analyze()
        
        if analysis['innovation']:
            innovations += 1
        
        if i == 0:
            print(f"示例运行: 唯一状态={analysis['unique_states']}, 变异次数={analysis['mutations']}")
    
    print(f"\n产生新模式的次数: {innovations}/20")
    
    if innovations > 10:
        print("\n【发现】元进化能持续产生新行为！")


if __name__ == '__main__':
    test_evolution()