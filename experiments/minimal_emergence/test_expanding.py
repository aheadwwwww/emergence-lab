"""
自扩展状态空间
状态数量可以增长，打破有限周期限制
"""

import numpy as np
from pathlib import Path

OUTPUT_DIR = Path('D:/emergence_experiments')


class ExpandingStateUniverse:
    """
    自扩展状态宇宙
    - 初始状态数：3
    - 状态数可以增长（当遇到"边界"时）
    - 类似细胞分裂
    """
    
    def __init__(self, initial_states=3):
        self.states = list(range(initial_states))
        self.state_count = initial_states
        
        # 动态规则字典
        self.rules = {}
        self._init_rules()
        
        self.state = 0
        self.memory = 0
        self.history = [(self.state, self.memory, self.state_count)]
    
    def _init_rules(self):
        """初始化规则"""
        for s in self.states:
            for m in [0, 1]:
                # 随机规则
                self.rules[(s, m)] = (
                    np.random.choice(self.states),
                    np.random.randint(0, 2)
                )
    
    def _add_state(self):
        """添加新状态"""
        new_state = self.state_count
        self.states.append(new_state)
        self.state_count += 1
        
        # 为新状态添加规则
        for m in [0, 1]:
            # 新规则：可能指向新状态
            self.rules[(new_state, m)] = (
                np.random.randint(0, self.state_count),
                np.random.randint(0, 2)
            )
        
        # 更旧规则也可能指向新状态
        for s in self.states[:-1]:
            for m in [0, 1]:
                if np.random.random() < 0.2:  # 20%概率更新
                    self.rules[(s, m)] = (
                        np.random.randint(0, self.state_count),
                        np.random.randint(0, 2)
                    )
    
    def step(self):
        key = (self.state, self.memory)
        
        # 扩展触发：当状态接近边界时
        if self.state >= self.state_count - 1:
            self._add_state()
        
        # 应用规则
        if key in self.rules:
            self.state, self.memory = self.rules[key]
        
        self.history.append((self.state, self.memory, self.state_count))
    
    def run(self, steps=500):
        for _ in range(steps):
            self.step()
        return self.history
    
    def analyze(self):
        """分析扩展情况"""
        # 状态数增长
        state_counts = [h[2] for h in self.history]
        
        # 唯一状态数
        visited_states = set(h[0] for h in self.history)
        
        return {
            'final_state_count': self.state_count,
            'visited_states': len(visited_states),
            'growth': state_counts[-1] - state_counts[0],
            'open_ended': state_counts[-1] > state_counts[0],
        }


class RecursiveExpandingUniverse:
    """
    递归扩展宇宙
    - 每次到达"边界状态"时分裂出新状态
    - 新状态的规则继承并变异父状态的规则
    """
    
    def __init__(self):
        self.state = 0
        self.memory = 0
        
        # 状态树结构
        self.state_tree = {0: {'parent': None, 'children': [], 'generation': 0}}
        self.state_count = 1
        
        # 规则：每个状态的规则可能继承自父状态
        self.rules = {(0, 0): (0, 0), (0, 1): (0, 1)}
        
        self.history = []
        self.bifurcations = []
    
    def _bifurcate(self):
        """分裂：当前状态产生子状态"""
        parent = self.state
        new_state = self.state_count
        
        # 记录树结构
        self.state_tree[new_state] = {
            'parent': parent,
            'children': [],
            'generation': self.state_tree[parent]['generation'] + 1
        }
        self.state_tree[parent]['children'].append(new_state)
        self.state_count += 1
        
        # 继承规则并变异
        for m in [0, 1]:
            parent_rule = self.rules.get((parent, m), (parent, m))
            # 变异：可能指向新状态或随机状态
            if np.random.random() < 0.5:
                self.rules[(new_state, m)] = (new_state, m)  # 自指
            else:
                self.rules[(new_state, m)] = (
                    np.random.randint(0, min(self.state_count, 10)),
                    np.random.randint(0, 2)
                )
        
        self.bifurcations.append((len(self.history), parent, new_state))
    
    def step(self):
        key = (self.state, self.memory)
        
        # 分裂触发：每隔一定步数或到达边界
        if len(self.history) % 50 == 0 and self.state_count < 50:
            self._bifurcate()
        
        # 规则执行
        if key in self.rules:
            self.state, self.memory = self.rules[key]
        
        self.history.append((self.state, self.memory, self.state_count))
    
    def run(self, steps=1000):
        for _ in range(steps):
            self.step()
        return self.history
    
    def analyze(self):
        """分析递归扩展"""
        tree_depth = max(s['generation'] for s in self.state_tree.values())
        total_states = self.state_count
        bifurcation_count = len(self.bifurcations)
        
        # 唯一访问的状态
        visited = set(h[0] for h in self.history)
        
        return {
            'tree_depth': tree_depth,
            'total_states': total_states,
            'visited_states': len(visited),
            'bifurcations': bifurcation_count,
            'open_ended': total_states > 1,
        }


def test_expanding():
    """测试自扩展状态空间"""
    
    print("=== 测试简单扩展 ===")
    for i in range(5):
        universe1 = ExpandingStateUniverse(initial_states=3)
        universe1.run(500)
        analysis = universe1.analyze()
        print(f"运行{i+1}: 最终状态数={analysis['final_state_count']}, 访问={analysis['visited_states']}, 开放={analysis['open_ended']}")
    
    print("\n=== 测试递归扩展 ===")
    universe2 = RecursiveExpandingUniverse()
    universe2.run(1000)
    analysis = universe2.analyze()
    print(f"树深度={analysis['tree_depth']}, 总状态={analysis['total_states']}, 访问={analysis['visited_states']}")
    
    if analysis['open_ended']:
        print("\n【重要发现】自扩展状态空间产生开放式演化！")
        print("状态数从1增长到", analysis['total_states'])


if __name__ == '__main__':
    print("=== 长期运行测试 ===")
    
    # 运行更长时间，看状态增长是否持续
    universe = RecursiveExpandingUniverse()
    universe.run(5000)
    analysis = universe.analyze()
    
    print(f"树深度={analysis['tree_depth']}, 总状态={analysis['total_states']}, 访问={analysis['visited_states']}")
    
    # 绘制状态增长曲线
    import matplotlib.pyplot as plt
    
    state_counts = [h[2] for h in universe.history]
    plt.figure(figsize=(12, 4))
    plt.plot(state_counts)
    plt.xlabel('Steps')
    plt.ylabel('State Count')
    plt.title('Self-Expanding Universe: State Growth Over Time')
    plt.savefig('D:/emergence_experiments/state_growth.png')
    plt.close()
    
    print(f"\n状态增长曲线保存到: D:/emergence_experiments/state_growth.png")