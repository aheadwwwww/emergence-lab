"""
学习型觅食Agent
用简单神经网络学习觅食策略
不编程好奇，让网络自己学会什么时候探索、什么时候利用
"""
import sys
sys.path.insert(0, 'D:\\openclaw_workspace\\experiments')
import encoding_fix

import numpy as np
from pathlib import Path

OUTPUT_DIR = Path('D:/emergence_experiments')


class NNAgent:
    """神经网络Agent"""
    
    def __init__(self, num_states=50, num_hidden=16):
        self.num_states = num_states
        
        # 极其简单的单层网络
        # 输入: 能量, 当前位置的食物记忆(归一化)
        # 输出: 所有状态的选择概率
        self.W1 = np.random.randn(num_states + 1, num_hidden) * 0.1
        self.b1 = np.zeros(num_hidden)
        self.W2 = np.random.randn(num_hidden, num_states) * 0.1
        self.b2 = np.zeros(num_states)
        
        self.state = 0
        self.energy = 15
        self.max_energy = 30
        self.memory = np.full(num_states, 2.0, dtype=float)
        self.forget_rate = 0.97
        
        # 学习参数
        self.learning_rate = 0.01
        self.gamma = 0.9  # 折扣因子
        
        # 记录
        self.last_input = None
        self.last_hidden = None
        self.last_output = None
        self.total_reward = 0
    
    def forward(self, energy_normalized):
        """前向传播"""
        # 输入: [记忆向量(归一化), 能量(归一化)]
        memory_input = self.memory / 10.0
        energy_input = np.array([energy_normalized])
        x = np.concatenate([memory_input, energy_input])
        self.last_input = x
        
        h = np.tanh(x @ self.W1 + self.b1)
        self.last_hidden = h
        logits = h @ self.W2 + self.b2
        # softmax
        exp_logits = np.exp(logits - np.max(logits))
        probs = exp_logits / exp_logits.sum()
        self.last_output = probs
        
        return probs
    
    def choose_state(self):
        """选择状态（随机采样，不是贪心）"""
        energy_norm = self.energy / self.max_energy
        probs = self.forward(energy_norm)
        return np.random.choice(self.num_states, p=probs)
    
    def learn(self, chosen_state, reward):
        """策略梯度更新"""
        if self.last_hidden is None or self.last_output is None:
            return
        
        # ∇log π = one_hot(a) - π(a)
        grad = -self.last_output.copy()
        grad[chosen_state] += 1
        grad = grad * reward
        
        # 更新输出层
        h = self.last_hidden
        dW2 = np.outer(h, grad)
        self.W2 -= dW2 * self.learning_rate
        self.b2 -= grad * self.learning_rate


class LearningForaging:
    """学习型觅食宇宙"""
    
    def __init__(self, num_states=50):
        self.num_states = num_states
        self.agent = NNAgent(num_states)
        self.day = 0
        
        # 食物
        self.food = np.zeros(num_states, dtype=float)
        for _ in range(8):
            self._spawn_food()
        
        self.history = []
    
    def _spawn_food(self):
        state = np.random.randint(0, self.num_states)
        self.food[state] += np.random.randint(3, 10)
    
    def step(self):
        self.day += 1
        
        # Agent决策
        chosen = self.agent.choose_state()
        self.agent.state = chosen
        
        # 吃
        food_here = self.food[chosen]
        eaten = min(food_here, 3.0)
        self.food[chosen] -= eaten
        self.agent.energy = min(self.agent.max_energy, self.agent.energy + eaten)
        
        # 奖励：吃到食物给正奖励，没吃到给负奖励
        reward = eaten * 2 - 1  # 0食物=-1, 1食物=+1, 2食物=+3, 3食物=+5
        self.agent.total_reward += reward
        
        # 学习
        self.agent.learn(chosen, reward)
        
        # 更新记忆
        if food_here > 0:
            self.agent.memory[chosen] += 0.3
        else:
            self.agent.memory[chosen] *= 0.95
        
        self.agent.memory *= self.agent.forget_rate
        self.agent.memory = np.clip(self.agent.memory, 0.1, 10)
        
        # 代谢
        self.agent.energy -= 1
        
        # 食物迁移
        if self.day % 15 == 0:
            depletion = np.random.randint(0, self.num_states)
            self.food[depletion] = 0
            self._spawn_food()
        
        self.history.append((chosen, self.agent.energy, eaten))
        
        return self.agent.energy > 0
    
    def run(self, max_steps=10000):
        for _ in range(max_steps):
            alive = self.step()
            if not alive:
                break
        return len(self.history)


if __name__ == '__main__':
    print("=== 学习型觅食宇宙 ===\n")
    
    # 与随机策略对比
    print("对比：学习型Agent vs 手动好奇Agent")
    print("-" * 40)
    
    # 学习型
    learning_results = []
    for trial in range(20):
        universe = LearningForaging(num_states=50)
        steps = universe.run(5000)
        learning_results.append({
            'steps': steps,
            'reward': universe.agent.total_reward,
            'visits': len(set(h[0] for h in universe.history))
        })
    
    avg_steps = np.mean([r['steps'] for r in learning_results])
    avg_reward = np.mean([r['reward'] for r in learning_results])
    avg_visits = np.mean([r['visits'] for r in learning_results])
    
    print(f"学习型Agent:")
    print(f"  平均存活: {avg_steps:.1f}步")
    print(f"  平均奖励: {avg_reward:.1f}")
    print(f"  平均覆盖: {avg_visits:.0f}/50")
    
    # 手动好奇Agent（test_foraging_v2的数据）
    print(f"\n手动好奇Agent (参考):")
    print(f"  平均存活: ~27步")
    print(f"  好奇行为率: ~84%")
    
    # 判断
    if avg_steps > 30:
        print(f"\n-> 学习型胜出：神经网络学到了更好的觅食策略")
    elif avg_steps > 20:
        print(f"\n-> 接近：学习型有潜力，需要更多训练")
    else:
        print(f"\n-> 手动好奇更优：神经网络还没学会")
