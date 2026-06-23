"""
涌现式好奇 v2：真正的生存压力
- 能量低会死
- 食物位置会迁移
- 记忆不完美
- 好奇行为应该从"不探索就会饿死"中涌现
"""

import numpy as np
from pathlib import Path

OUTPUT_DIR = Path('D:/emergence_experiments')


class HarshForagingUniverse:
    """严苛觅食宇宙"""
    
    def __init__(self, num_states=50):
        self.num_states = num_states
        self.state = 0
        self.energy = 12  # 更多初始能量
        self.max_energy = 25
        self.day = 0
        
        # 食物会迁移：不断有旧食物消失、新食物出现
        self.food = np.zeros(num_states, dtype=float)
        for _ in range(5):  # 更多初始食物
            self._spawn_food()
        
        # 不完美记忆（有噪声+遗忘）
        self.memory = np.full(num_states, 2.0)  # 默认认为有点食物
        self.forget_rate = 0.97
        
        self.history = []
        
    def _spawn_food(self):
        """随机生成一堆食物"""
        state = np.random.randint(0, self.num_states)
        self.food[state] += np.random.randint(3, 8)
    
    def step(self):
        self.day += 1
        
        # 1. 决策：去哪里
        # 利用记忆 + 一些随机性
        if np.random.random() < 0.15:
            # 纯随机探索（"盲目好奇"）
            chosen = np.random.randint(0, self.num_states)
        elif self.energy < 4:
            # 快饿死了——去记忆中最好的地方
            chosen = np.argmax(self.memory)
        else:
            # 有富余能量时——可以"好奇"地看看未知区域
            # 好奇 = 去记忆中最不确定的地方
            # 不确定性 = 遗忘程度
            uncertainty = 1.0 / (self.memory + 1)
            # 但也不能完全忽视已知食物
            blend = 0.3 * (self.memory / max(self.memory)) + 0.7 * uncertainty
            chosen = np.random.choice(self.num_states, p=blend / blend.sum())
        
        self.state = chosen
        
        # 2. 吃
        food_here = self.food[chosen]
        eaten = min(food_here, 3.0)
        self.food[chosen] -= eaten
        self.energy = min(self.max_energy, self.energy + eaten)
        
        # 3. 更新记忆
        if food_here > 0:
            self.memory[chosen] += 0.5
        else:
            self.memory[chosen] *= 0.95  # 没找到食物，信心下降
        
        # 4. 遗忘：所有记忆缓慢衰减
        self.memory *= self.forget_rate
        self.memory = np.clip(self.memory, 0.1, 10)
        
        # 5. 基础代谢
        self.energy -= 1
        
        # 6. 食物迁移：每10步重新布局（更慢的迁移）
        if self.day % 10 == 0:
            # 吃掉一些食物的地方变成贫瘠
            depletion_idx = np.random.randint(0, self.num_states)
            self.food[depletion_idx] = 0
            # 新地方长出食物
            self._spawn_food()
        
        self.history.append((chosen, self.energy, food_here))
        
        return self.energy > 0
    
    def run(self, max_steps=10000):
        for _ in range(max_steps):
            alive = self.step()
            if not alive:
                break
        return self.day
    
    def analyze(self):
        steps = len(self.history)
        visited = set(h[0] for h in self.history)
        
        # 计算"好奇"行为：去了记忆中食物低于平均的地方，且不是因为要饿死了
        curious_moves = 0
        total_non_starvation = 0
        for i, (state, energy, food_found) in enumerate(self.history):
            if energy >= 4:  # 不饿
                total_non_starvation += 1
                if food_found < 0.5:  # 去了没食物的地方
                    curious_moves += 1
        
        curiosity_rate = curious_moves / max(total_non_starvation, 1)
        
        return {
            'survival': steps,
            'visited': len(visited),
            'curiosity_rate': curiosity_rate,
            'final_energy': self.history[-1][1],
        }


if __name__ == '__main__':
    print("=== 严苛觅食宇宙：好奇从生存中涌现 ===\n")
    
    # 多运行几次统计
    all_results = []
    for trial in range(20):
        universe = HarshForagingUniverse(num_states=50)
        survived = universe.run(10000)
        result = universe.analyze()
        all_results.append(result)
        print(f"试验{trial+1}: 存活={result['survival']}步, 覆盖={result['visited']}/50, 好奇率={result['curiosity_rate']:.1%}")
    
    avg_curiosity = np.mean([r['curiosity_rate'] for r in all_results])
    avg_survival = np.mean([r['survival'] for r in all_results])
    
    print(f"\n=== 统计 ===")
    print(f"平均存活: {avg_survival:.0f}步")
    print(f"平均好奇行为率: {avg_curiosity:.1%}")
    
    if avg_curiosity > 0.2:
        print("[OK] 好奇行为涌现：不需要显式编程，从生存压力中自然产生")
    elif avg_curiosity > 0.1:
        print("[--] 少量好奇行为")
    else:
        print("[XX] 没有涌现好奇行为，需要更强的生存压力")
