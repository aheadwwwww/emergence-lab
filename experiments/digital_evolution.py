"""
Digital Evolution - 数字进化

模拟进化过程：
- 个体有基因（随机行为策略）
- 适应度 = 存活时间 + 繁殖次数
- 选择 + 变异 → 适应度提升

本实验模拟简单的进化场景
"""

import numpy as np
from PIL import Image, ImageDraw
import random

class Creature:
    def __init__(self, x, y, genes=None):
        self.x = x
        self.y = y
        self.energy = 100
        self.age = 0
        # 基因：8个方向的移动概率 + 突变率
        if genes:
            self.genes = genes.copy()
        else:
            self.genes = [random.random() for _ in range(8)]
            # 归一化
            total = sum(self.genes)
            self.genes = [g / total for g in self.genes]
        self.mutation_rate = 0.1
    
    def move(self, world_size):
        # 根据基因选择移动方向
        direction = random.choices(range(8), weights=self.genes)[0]
        dx = [0, 1, 1, 1, 0, -1, -1, -1][direction]
        dy = [-1, -1, 0, 1, 1, 1, 0, -1][direction]
        self.x = (self.x + dx) % world_size
        self.y = (self.y + dy) % world_size
        self.energy -= 1
        self.age += 1
    
    def reproduce(self):
        if self.energy > 150:
            self.energy -= 50
            # 复制基因 + 变异
            child_genes = self.genes.copy()
            if random.random() < self.mutation_rate:
                # 随机改变一个基因
                idx = random.randint(0, 7)
                child_genes[idx] = max(0.01, child_genes[idx] + random.gauss(0, 0.1))
                total = sum(child_genes)
                child_genes = [g / total for g in child_genes]
            return Creature(self.x, self.y, child_genes)
        return None

class World:
    def __init__(self, size=100, food_density=0.02):
        self.size = size
        self.food_density = food_density
        self.creatures = []
        self.food = set()
        self.generation = 0
        self.stats = []
    
    def add_creature(self, creature):
        self.creatures.append(creature)
    
    def spawn_food(self):
        for _ in range(int(self.size * self.size * self.food_density)):
            x, y = random.randint(0, self.size-1), random.randint(0, self.size-1)
            self.food.add((x, y))
    
    def step(self):
        # 生成食物
        self.spawn_food()
        
        # 所有生物行动
        new_creatures = []
        for c in self.creatures:
            c.move(self.size)
            
            # 吃食物
            if (c.x, c.y) in self.food:
                c.energy += 30
                self.food.remove((c.x, c.y))
            
            # 繁殖
            child = c.reproduce()
            if child:
                new_creatures.append(child)
        
        # 移除死亡的生物
        self.creatures = [c for c in self.creatures if c.energy > 0]
        self.creatures.extend(new_creatures)
        
        # 统计
        if self.creatures:
            avg_genes = np.mean([c.genes for c in self.creatures], axis=0)
            self.stats.append({
                'population': len(self.creatures),
                'avg_age': np.mean([c.age for c in self.creatures]),
                'avg_genes': avg_genes.tolist()
            })
    
    def run(self, steps=500):
        for _ in range(steps):
            self.step()
            if len(self.creatures) == 0:
                break

def visualize_evolution(stats, output_path):
    """可视化进化过程"""
    if not stats:
        print('No stats to visualize')
        return
    
    SIZE = 800
    MARGIN = 80
    WIDTH = SIZE - 2 * MARGIN
    HEIGHT = SIZE - 2 * MARGIN
    
    img = Image.new('RGB', (SIZE, SIZE), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    # 坐标轴
    draw.line([MARGIN, MARGIN, MARGIN, SIZE-MARGIN], fill=(80,80,80), width=2)
    draw.line([MARGIN, SIZE-MARGIN, SIZE-MARGIN, SIZE-MARGIN], fill=(80,80,80), width=2)
    
    # 绘制种群数量
    pops = [s['population'] for s in stats]
    max_pop = max(pops) if pops else 1
    
    for i in range(1, len(pops)):
        x1 = MARGIN + (i-1) / len(pops) * WIDTH
        y1 = SIZE - MARGIN - pops[i-1] / max_pop * HEIGHT
        x2 = MARGIN + i / len(pops) * WIDTH
        y2 = SIZE - MARGIN - pops[i] / max_pop * HEIGHT
        draw.line([x1, y1, x2, y2], fill=(100, 255, 150), width=2)
    
    draw.text((SIZE//2 - 50, 20), "Digital Evolution", fill=(255,255,255))
    draw.text((MARGIN+10, MARGIN+20), f"Final Pop: {pops[-1]}", fill=(100,255,150))
    draw.text((MARGIN+10, MARGIN+40), f"Generations: {len(stats)}", fill=(200,200,200))
    
    img.save(output_path)
    print(f'Saved: {output_path}')

if __name__ == '__main__':
    output_dir = r'C:\Users\许耀仁\.openclaw\workspace\experiments'
    
    print('=== Digital Evolution ===')
    
    # 初始化世界
    world = World(size=50, food_density=0.03)
    
    # 添加初始种群
    for _ in range(20):
        x, y = random.randint(0, 49), random.randint(0, 49)
        world.add_creature(Creature(x, y))
    
    # 运行进化
    world.run(steps=300)
    
    print(f'Final population: {len(world.creatures)}')
    print(f'Generations: {len(world.stats)}')
    
    # 可视化
    visualize_evolution(world.stats, f'{output_dir}/digital_evolution.png')
    
    print('Done')