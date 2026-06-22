"""
Creativity - 创造力

组合式创新：新想法 = 旧想法的组合
模拟创造性跳跃

本实验模拟想法组合产生创新
"""

import numpy as np
from PIL import Image, ImageDraw
import random

class Idea:
    def __init__(self, elements):
        self.elements = elements  # 想法的元素组合
        self.novelty = 0
        self.usefulness = 0

class CreativitySimulation:
    def __init__(self, n_ideas=50, n_elements=10):
        self.n_elements = n_elements
        self.ideas = []
        
        # 初始化想法池
        for _ in range(n_ideas):
            n = random.randint(1, 3)
            elements = tuple(sorted(random.sample(range(n_elements), n)))
            self.ideas.append(Idea(elements))
        
        # 已存在的组合（用于计算新颖性）
        self.existing_combinations = set()
        self.history = []
    
    def evaluate_novelty(self, idea):
        """新颖性：组合从未出现过"""
        if idea.elements in self.existing_combinations:
            return 0.1
        return 1.0
    
    def evaluate_usefulness(self, idea):
        """有用性：随机（模拟现实的不确定性）"""
        base = sum(idea.elements) / len(idea.elements) / self.n_elements
        return base + random.gauss(0, 0.2)
    
    def combine(self, idea1, idea2):
        """组合两个想法产生新想法"""
        new_elements = tuple(sorted(set(idea1.elements) | set(idea2.elements)))
        return Idea(new_elements)
    
    def step(self):
        """一步创新过程"""
        # 随机选择两个想法组合
        i1, i2 = random.sample(range(len(self.ideas)), 2)
        new_idea = self.combine(self.ideas[i1], self.ideas[i2])
        
        # 评估
        new_idea.novelty = self.evaluate_novelty(new_idea)
        new_idea.usefulness = max(0, min(1, self.evaluate_usefulness(new_idea)))
        
        # 如果足够好，加入想法池
        if new_idea.novelty > 0.5 and new_idea.usefulness > 0.3:
            self.ideas.append(new_idea)
            self.existing_combinations.add(new_idea.elements)
        
        # 记录
        self.history.append({
            'pool_size': len(self.ideas),
            'avg_novelty': np.mean([i.novelty for i in self.ideas if i.novelty > 0]),
            'avg_usefulness': np.mean([i.usefulness for i in self.ideas])
        })
    
    def run(self, steps=500):
        for _ in range(steps):
            self.step()

def visualize_creativity(sim, output_path):
    """可视化创新过程"""
    SIZE = 800
    MARGIN = 80
    
    img = Image.new('RGB', (SIZE, SIZE), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    WIDTH = SIZE - 2 * MARGIN
    HEIGHT = SIZE - 2 * MARGIN
    
    # 绘制想法池增长
    pool_sizes = [h['pool_size'] for h in sim.history]
    max_pool = max(pool_sizes) if pool_sizes else 1
    
    for i in range(1, len(pool_sizes)):
        x1 = MARGIN + (i-1) / len(pool_sizes) * WIDTH
        y1 = SIZE - MARGIN - pool_sizes[i-1] / max_pool * HEIGHT
        x2 = MARGIN + i / len(pool_sizes) * WIDTH
        y2 = SIZE - MARGIN - pool_sizes[i] / max_pool * HEIGHT
        draw.line([x1, y1, x2, y2], fill=(100, 200, 255), width=2)
    
    draw.text((SIZE//2 - 30, 20), "Creativity", fill=(255, 255, 255))
    draw.text((MARGIN + 10, MARGIN + 20), f"Final ideas: {pool_sizes[-1]}", fill=(100, 200, 255))
    draw.text((MARGIN + 10, MARGIN + 40), "New = Old + Old", fill=(200, 200, 200))
    
    img.save(output_path)
    print(f'Saved: {output_path}')

if __name__ == '__main__':
    output_dir = r'C:\Users\许耀仁\.openclaw\workspace\experiments'
    
    print('=== Creativity ===')
    
    sim = CreativitySimulation(n_ideas=30, n_elements=8)
    sim.run(steps=500)
    
    print(f'Initial ideas: 30')
    print(f'Final ideas: {len(sim.ideas)}')
    
    visualize_creativity(sim, f'{output_dir}/creativity.png')
    
    print('Done')