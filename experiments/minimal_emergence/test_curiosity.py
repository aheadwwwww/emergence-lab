"""
好奇心驱动型宇宙
系统获得"奖励"当访问新状态
类似强化学习中的好奇心机制
"""

import numpy as np
from pathlib import Path

OUTPUT_DIR = Path('D:/emergence_experiments')


class CuriosityUniverse:
    """
    好奇心驱动型宇宙
    - 内部奖励：访问新状态获得"好奇心满足"
    - 系统会记住哪些状态"有趣"
    - 倾向于探索未访问或低访问的状态
    """
    
    def __init__(self):
        self.state = 0
        self.memory = 0
        self.state_count = 1
        
        # 访问记录
        self.visit_counts = {0: 0}
        
        # 好奇心分数：每个状态的"新鲜度"
        self.curiosity_scores = {0: 1.0}
        
        # 规则
        self.rules = {}
        
        # 历史和奖励
        self.history = []
        self.reward_history = []
        self.total_reward = 0
    
    def _update_curiosity(self):
        """更新好奇心分数"""
        for s in range(self.state_count):
            visits = self.visit_counts.get(s, 0)
            # 新鲜度：访问越少，好奇心越高
            self.curiosity_scores[s] = 1.0 / (1.0 + visits)
    
    def _add_state(self):
        """添加新状态"""
        new_state = self.state_count
        self.state_count += 1
        self.visit_counts[new_state] = 0
        self.curiosity_scores[new_state] = 1.0  # 新状态最有趣
        
        # 新状态的规则：跳转到好奇心高的状态
        most_curious = max(range(self.state_count),
                          key=lambda s: self.curiosity_scores.get(s, 0))
        
        for m in [0, 1]:
            if np.random.random() < 0.6:
                self.rules[(new_state, m)] = (most_curious, np.random.randint(0, 2))
            else:
                self.rules[(new_state, m)] = (np.random.randint(0, self.state_count), np.random.randint(0, 2))
    
    def step(self):
        """执行一步，计算好奇心奖励"""
        # 记录访问
        old_visits = self.visit_counts.get(self.state, 0)
        self.visit_counts[self.state] = old_visits + 1
        
        # 好奇心奖励：访问低访问状态获得奖励
        reward = self.curiosity_scores.get(self.state, 0)
        self.total_reward += reward
        self.reward_history.append(self.total_reward)
        
        # 更新好奇心分数
        self._update_curiosity()
        
        # 分裂触发：当好奇心奖励过低时，分裂出新状态
        if reward < 0.1 and self.state_count < 500 and len(self.history) % 100 == 0:
            self._add_state()
        
        key = (self.state, self.memory)
        
        if key in self.rules:
            next_state, next_memory = self.rules[key]
        else:
            # 选择好奇心最高的状态
            most_curious = max(range(self.state_count),
                              key=lambda s: self.curiosity_scores.get(s, 0))
            next_state = most_curious
            next_memory = np.random.randint(0, 2)
        
        # 随机扰动：避免局部最优
        if np.random.random() < 0.1 and self.state_count > 1:
            next_state = np.random.randint(0, self.state_count)
        
        self.state = next_state
        self.memory = next_memory
        self.history.append((self.state, self.memory, self.state_count))
    
    def run(self, steps=10000):
        for _ in range(steps):
            self.step()
        return self.history
    
    def analyze(self):
        visited = set(h[0] for h in self.history)
        
        return {
            'total_states': self.state_count,
            'visited_states': len(visited),
            'total_reward': self.total_reward,
            'avg_reward': self.total_reward / len(self.history) if self.history else 0,
            'visit_distribution': self.visit_counts,
        }


if __name__ == '__main__':
    print("=== 好奇心驱动型演化测试（50000步） ===")
    
    universe = CuriosityUniverse()
    universe.run(50000)
    analysis = universe.analyze()
    
    print(f"\n总状态数: {analysis['total_states']}")
    print(f"访问的唯一状态: {analysis['visited_states']}")
    print(f"总好奇心奖励: {analysis['total_reward']:.2f}")
    print(f"平均奖励: {analysis['avg_reward']:.4f}")
    
    # 绘制奖励曲线
    import matplotlib.pyplot as plt
    
    plt.figure(figsize=(14, 5))
    plt.plot(universe.reward_history)
    plt.xlabel('Steps')
    plt.ylabel('Cumulative Curiosity Reward')
    plt.title('Curiosity-Driven Universe: Reward Over Time')
    plt.savefig('D:/emergence_experiments/curiosity_reward.png', dpi=150)
    plt.close()
    
    # 绘制访问分布
    visits = analysis['visit_distribution']
    states = sorted(visits.keys())
    counts = [visits[s] for s in states]
    
    plt.figure(figsize=(14, 5))
    plt.bar(states[:min(50, len(states))], counts[:min(50, len(counts))])
    plt.xlabel('State ID')
    plt.ylabel('Visit Count')
    plt.title('Curiosity-Driven Universe: Visit Distribution')
    plt.savefig('D:/emergence_experiments/curiosity_visits.png', dpi=150)
    plt.close()
    
    print(f"\n奖励曲线保存到: D:/emergence_experiments/curiosity_reward.png")
    print(f"访问分布保存到: D:/emergence_experiments/curiosity_visits.png")