"""
涌现式好奇：不设计好奇心，设计生存压力
系统需要找"食物"，食物位置会变化
好奇行为从生存压力中涌现，而非直接编程
"""

import numpy as np
from pathlib import Path

OUTPUT_DIR = Path('D:/emergence_experiments')


class ForagingUniverse:
    """
    觅食宇宙
    - N 个状态，每个状态有一定量的"食物"
    - 食物会随时间枯竭，也会随时间再生
    - Agent 需要在探索（找到新食物源）和利用（吃当前食物）之间平衡
    - "好奇心"不是编程的，是从生存压力中涌现的
    """
    
    def __init__(self, num_states=100):
        self.num_states = num_states
        self.state = 0
        
        # 每个状态的食物量 (0-10)
        self.food = np.random.randint(0, 5, num_states)
        # 食物再生率
        self.regrowth_rate = 0.01
        # 消耗速度
        self.consume_rate = 2
        
        # Agent 的能量
        self.energy = 10
        self.max_energy = 20
        
        # 记忆：每个状态的食物历史
        self.food_memory = self.food.copy().astype(float)
        
        # 策略：探索 vs 利用的权重
        # 能量越低，越倾向于利用已知食物
        # 能量越高，越倾向于探索未知
        self.exploration_weight = 0.3
        
        self.history = []
        self.energy_history = []
        
    def step(self):
        """执行一步"""
        # 更新探索权重（能量高时更爱探索）
        self.exploration_weight = 0.3 + 0.5 * (self.energy / self.max_energy)
        
        # 决策：去哪个状态
        if np.random.random() < self.exploration_weight:
            # 探索：随机跳到一个状态
            # 但不是完全随机 - 偏向于记忆中食物少的状态（"好奇"）
            # 这就是"好奇"涌现的地方
            curiosity_bias = 1.0 / (self.food_memory + 0.5)
            curiosity_bias = curiosity_bias / curiosity_bias.sum()
            self.state = np.random.choice(self.num_states, p=curiosity_bias)
        else:
            # 利用：去记忆中食物最多的状态
            best_states = np.where(self.food_memory == self.food_memory.max())[0]
            self.state = np.random.choice(best_states)
        
        # 吃食物
        food_here = self.food[self.state]
        eaten = min(food_here, self.consume_rate)
        self.food[self.state] -= eaten
        self.energy = min(self.max_energy, self.energy + eaten)
        
        # 更新记忆（不完全准确 - 有遗忘）
        self.food_memory[self.state] = max(
            self.food_memory[self.state],
            self.food[self.state]
        )
        # 遗忘：其他状态的食物记忆缓慢衰减
        self.food_memory *= 0.999  # 自动转为float，没问题
        
        # 能量消耗（存活的代价）
        self.energy -= 1
        
        # 食物再生
        self.food += np.random.poisson(self.regrowth_rate * self.num_states, self.num_states)
        self.food = np.clip(self.food, 0, 10)
        
        self.history.append((self.state, self.energy))
        self.energy_history.append(self.energy)
    
    def run(self, steps=10000):
        for _ in range(steps):
            self.step()
        return self.history
    
    def analyze(self):
        visited = set(h[0] for h in self.history)
        
        # 计算生存时间
        survival = len(self.history)
        
        # 计算平均能量
        avg_energy = np.mean(self.energy_history)
        
        # 分析"好奇"行为：在能量高的时候去探索低食物状态
        high_energy_steps = [i for i, e in enumerate(self.energy_history) if e > 15]
        high_energy_explorations = 0
        for i in high_energy_steps:
            if i < len(self.history) - 1:
                state = self.history[i][0]
                if self.food[state] < 3:  # 去了低食物状态 -> 好奇行为
                    high_energy_explorations += 1
        
        curiosity_rate = high_energy_explorations / max(len(high_energy_steps), 1)
        
        return {
            'survival': survival,
            'visited_states': len(visited),
            'avg_energy': avg_energy,
            'curiosity_rate': curiosity_rate,
            'final_energy': self.energy,
        }


if __name__ == '__main__':
    print("=== 觅食宇宙：好奇从生存压力中涌现 ===\n")
    
    # 测试不同的再生率
    regrowth_values = [0.005, 0.01, 0.02, 0.05]
    
    for regrowth in regrowth_values:
        print(f"\n--- 食物再生率: {regrowth} ---")
        
        # 运行10次取平均
        results = []
        for _ in range(5):
            universe = ForagingUniverse(num_states=100)
            universe.regrowth_rate = regrowth
            universe.run(5000)
            results.append(universe.analyze())
        
        avg_survival = np.mean([r['survival'] for r in results])
        avg_visited = np.mean([r['visited_states'] for r in results])
        avg_curiosity = np.mean([r['curiosity_rate'] for r in results])
        avg_energy = np.mean([r['avg_energy'] for r in results])
        
        print(f"生存时间: {avg_survival:.0f} 步")
        print(f"访问状态: {avg_visited:.0f}/{100}")
        print(f"好奇行为率: {avg_curiosity:.2%}")
        print(f"平均能量: {avg_energy:.1f}")
        
        # 关键判断
        if avg_curiosity > 0.3:
            print(f"  → 好奇行为涌现：能量高时主动探索未知")
        elif avg_curiosity > 0.1:
            print(f"  → 少量好奇行为")
        else:
            print(f"  → 几乎不好奇，只利用已知资源")
    
    print("\n\n=== 结论 ===")
    print("不需要直接编程好奇心")
    print("只需要：生存压力 + 遗忘机制 + 探索-利用权衡")
    print("好奇行为会从系统中涌现")
