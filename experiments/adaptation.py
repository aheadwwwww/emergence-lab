"""
Adaptation - 适应

环境变化 → 行为调整
反馈学习、强化学习

本实验模拟简单的适应过程
"""

import numpy as np
from PIL import Image, ImageDraw
import random

class AdaptiveAgent:
    def __init__(self, n_actions=4):
        self.n_actions = n_actions
        # Q表：状态-动作值
        self.q_table = {}
        self.learning_rate = 0.1
        self.discount = 0.9
        self.epsilon = 0.2  # 探索率
    
    def get_action(self, state):
        """根据Q表选择动作（ε-贪婪）"""
        if random.random() < self.epsilon:
            return random.randint(0, self.n_actions - 1)
        
        if state not in self.q_table:
            self.q_table[state] = [0.0] * self.n_actions
        
        return max(range(self.n_actions), key=lambda a: self.q_table[state][a])
    
    def update(self, state, action, reward, next_state):
        """Q-learning更新"""
        if state not in self.q_table:
            self.q_table[state] = [0.0] * self.n_actions
        if next_state not in self.q_table:
            self.q_table[next_state] = [0.0] * self.n_actions
        
        current = self.q_table[state][action]
        best_next = max(self.q_table[next_state])
        
        self.q_table[state][action] = current + self.learning_rate * (reward + self.discount * best_next - current)

class AdaptiveEnvironment:
    def __init__(self, size=10):
        self.size = size
        self.agent_pos = (0, 0)
        self.goal_pos = (size-1, size-1)
        self.obstacles = set()
        
        # 随机障碍物
        for _ in range(size * size // 10):
            x, y = random.randint(0, size-1), random.randint(0, size-1)
            if (x, y) != (0, 0) and (x, y) != (size-1, size-1):
                self.obstacles.add((x, y))
    
    def get_state(self):
        return self.agent_pos
    
    def step(self, action):
        """执行动作，返回奖励和新状态"""
        dx, dy = [(0, -1), (0, 1), (-1, 0), (1, 0)][action]
        new_x = max(0, min(self.size-1, self.agent_pos[0] + dx))
        new_y = max(0, min(self.size-1, self.agent_pos[1] + dy))
        
        # 检查障碍物
        if (new_x, new_y) in self.obstacles:
            reward = -10
        elif (new_x, new_y) == self.goal_pos:
            reward = 100
            self.agent_pos = (new_x, new_y)
        else:
            reward = -1  # 每步惩罚
            self.agent_pos = (new_x, new_y)
        
        return reward, self.get_state(), (new_x, new_y) == self.goal_pos
    
    def reset(self):
        self.agent_pos = (0, 0)

def train_agent(env, agent, episodes=100):
    """训练智能体"""
    successes = []
    steps_per_episode = []
    
    for ep in range(episodes):
        env.reset()
        steps = 0
        
        for _ in range(200):  # 最大步数
            state = env.get_state()
            action = agent.get_action(state)
            reward, next_state, done = env.step(action)
            agent.update(state, action, reward, next_state)
            steps += 1
            
            if done:
                successes.append(1)
                steps_per_episode.append(steps)
                break
        
        if not done:
            successes.append(0)
            steps_per_episode.append(200)
    
    return successes, steps_per_episode

def visualize_adaptation(successes, output_path):
    """可视化学习过程"""
    SIZE = 600
    MARGIN = 60
    
    img = Image.new('RGB', (SIZE, SIZE), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    WIDTH = SIZE - 2 * MARGIN
    HEIGHT = SIZE - 2 * MARGIN
    
    # 绘制成功率（窗口平均）
    window = 10
    success_rate = []
    for i in range(len(successes)):
        start = max(0, i - window)
        rate = sum(successes[start:i+1]) / (i - start + 1)
        success_rate.append(rate)
    
    for i in range(1, len(success_rate)):
        x1 = MARGIN + (i-1) / len(success_rate) * WIDTH
        y1 = SIZE - MARGIN - success_rate[i-1] * HEIGHT
        x2 = MARGIN + i / len(success_rate) * WIDTH
        y2 = SIZE - MARGIN - success_rate[i] * HEIGHT
        draw.line([x1, y1, x2, y2], fill=(100, 255, 150), width=2)
    
    draw.text((SIZE//2-30, 20), "Adaptation", fill=(255,255,255))
    draw.text((MARGIN+10, MARGIN+20), f"Final rate: {success_rate[-1]:.0%}", fill=(100,255,150))
    draw.text((MARGIN+10, MARGIN+40), f"Episodes: {len(successes)}", fill=(200,200,200))
    
    img.save(output_path)
    print(f'Saved: {output_path}')

if __name__ == '__main__':
    output_dir = r'C:\Users\许耀仁\.openclaw\workspace\experiments'
    
    print('=== Adaptation ===')
    
    env = AdaptiveEnvironment(size=8)
    agent = AdaptiveAgent(n_actions=4)
    
    successes, steps = train_agent(env, agent, episodes=100)
    
    print(f'Success rate: {sum(successes)/len(successes):.0%}')
    print(f'Average steps (last 20): {np.mean(steps[-20:]):.1f}')
    
    visualize_adaptation(successes, f'{output_dir}/adaptation.png')
    
    print('Done')