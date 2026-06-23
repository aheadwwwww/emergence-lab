"""
探索驱动型自扩展宇宙
系统有动力去访问未访问的状态
"""

import numpy as np
from pathlib import Path

OUTPUT_DIR = Path('D:/emergence_experiments')


class ExploringUniverse:
    """
    探索驱动型宇宙
    - 状态数可以增长
    - 系统倾向于访问"未访问"的状态
    - 类似好奇心驱动
    """
    
    def __init__(self):
        self.state = 0
        self.memory = 0
        self.state_count = 1
        
        # 记录每个状态的访问次数
        self.visit_counts = {0: 0}
        
        # 规则
        self.rules = {(0, 0): (0, 1), (0, 1): (0, 0)}
        
        self.history = []
        self.bifurcations = []
    
    def _add_state(self):
        """添加新状态"""
        new_state = self.state_count
        self.state_count += 1
        self.visit_counts[new_state] = 0
        
        # 新状态的规则：倾向于跳转到访问次数少的状态
        least_visited = min(self.visit_counts.keys(), 
                          key=lambda s: self.visit_counts[s])
        
        for m in [0, 1]:
            self.rules[(new_state, m)] = (
                least_visited if np.random.random() < 0.7 else np.random.randint(0, self.state_count),
                np.random.randint(0, 2)
            )
        
        self.bifurcations.append((len(self.history), self.state, new_state))
    
    def step(self):
        """执行一步"""
        # 记录访问
        self.visit_counts[self.state] = self.visit_counts.get(self.state, 0) + 1
        
        # 分裂触发：当前状态访问次数过多时分裂
        if self.visit_counts[self.state] > 20 and self.state_count < 300:
            self._add_state()
        
        key = (self.state, self.memory)
        
        # 规则执行 + 随机扰动
        if key in self.rules:
            self.state, self.memory = self.rules[key]
        else:
            # 默认：跳转到访问次数最少的状态
            least_visited = min(self.visit_counts.keys(),
                              key=lambda s: self.visit_counts[s])
            self.state = least_visited
            self.memory = np.random.randint(0, 2)
        
        # 随机扰动：5%概率跳转到任意状态
        if np.random.random() < 0.05 and self.state_count > 1:
            self.state = np.random.randint(0, self.state_count)
        
        self.history.append((self.state, self.memory, self.state_count))
    
    def run(self, steps=10000):
        for _ in range(steps):
            self.step()
        return self.history
    
    def analyze(self):
        """分析演化结果"""
        visited_states = set(h[0] for h in self.history)
        
        # 计算访问分布
        visit_dist = {s: self.visit_counts.get(s, 0) for s in range(self.state_count)}
        
        # 计算探索分数：访问越均匀越好
        if len(visit_dist) > 0:
            total_visits = sum(visit_dist.values())
            if total_visits > 0:
                uniformity = min(visit_dist.values()) / max(visit_dist.values()) if max(visit_dist.values()) > 0 else 0
            else:
                uniformity = 0
        else:
            uniformity = 0
        
        return {
            'total_states': self.state_count,
            'visited_states': len(visited_states),
            'visit_distribution': visit_dist,
            'uniformity': uniformity,
            'bifurcations': len(self.bifurcations),
        }


if __name__ == '__main__':
    print("=== 探索驱动型演化测试（10000步） ===")
    
    universe = ExploringUniverse()
    universe.run(10000)
    analysis = universe.analyze()
    
    print(f"\n总状态数: {analysis['total_states']}")
    print(f"访问的唯一状态: {analysis['visited_states']}")
    print(f"访问均匀度: {analysis['uniformity']:.3f}")
    print(f"分裂次数: {analysis['bifurcations']}")
    
    # 绘制访问分布
    import matplotlib.pyplot as plt
    
    visits = analysis['visit_distribution']
    states = list(visits.keys())
    counts = list(visits.values())
    
    plt.figure(figsize=(14, 5))
    plt.bar(states[:50], counts[:50])
    plt.xlabel('State ID')
    plt.ylabel('Visit Count')
    plt.title('State Visit Distribution (Top 50)')
    plt.savefig('D:/emergence_experiments/visit_distribution.png', dpi=150)
    plt.close()
    
    print(f"\n访问分布图保存到: D:/emergence_experiments/visit_distribution.png")
    
    # 绘制状态增长曲线
    state_counts = [h[2] for h in universe.history]
    plt.figure(figsize=(14, 5))
    plt.plot(state_counts, linewidth=0.5)
    plt.xlabel('Steps')
    plt.ylabel('State Count')
    plt.title('Exploring Universe: State Growth Over Time')
    plt.savefig('D:/emergence_experiments/exploring_growth.png', dpi=150)
    plt.close()
    
    print(f"状态增长曲线保存到: D:/emergence_experiments/exploring_growth.png")