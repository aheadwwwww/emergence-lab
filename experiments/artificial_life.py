"""
Artificial Life - 人工生命

模拟生命的核心特征：繁殖、变异、选择
例：Tierra、Avida、evolving-ant-farm

本实验模拟简单的生态演化
"""

import numpy as np
from PIL import Image, ImageDraw
import random

class Organism:
    def __init__(self, x, y, genome=None):
        self.x = x
        self.y = y
        self.energy = 50
        self.age = 0
        self.genome = genome if genome else ''.join(random.choice('ABCD') for _ in range(10))
    
    def act(self, world):
        # 基因决定行为
        gene = self.genome[self.age % len(self.genome)]
        
        if gene == 'A':  # 移动
            dx, dy = random.choice([(0,1), (0,-1), (1,0), (-1,0)])
            self.x = (self.x + dx) % world.size
            self.y = (self.y + dy) % world.size
            self.energy -= 1
        
        elif gene == 'B':  # 吃
            if (self.x, self.y) in world.food:
                self.energy += 20
                world.food.remove((self.x, self.y))
        
        elif gene == 'C':  # 繁殖
            if self.energy > 80:
                self.energy -= 40
                child_genome = self.mutate()
                return Organism(self.x, self.y, child_genome)
        
        elif gene == 'D':  # 休息
            pass
        
        self.age += 1
        return None
    
    def mutate(self):
        genome = list(self.genome)
        if random.random() < 0.1:
            idx = random.randint(0, len(genome) - 1)
            genome[idx] = random.choice('ABCD')
        return ''.join(genome)

class World:
    def __init__(self, size=50, food_rate=10):
        self.size = size
        self.food = set()
        self.organisms = []
        self.food_rate = food_rate
        self.history = []
    
    def add_organism(self, org):
        self.organisms.append(org)
    
    def step(self):
        # 生成食物
        for _ in range(self.food_rate):
            x, y = random.randint(0, self.size-1), random.randint(0, self.size-1)
            self.food.add((x, y))
        
        # 所有生物行动
        new_orgs = []
        for org in self.organisms:
            child = org.act(self)
            if child:
                new_orgs.append(child)
            org.energy -= 0.5  # 基础消耗
        
        # 移除死亡的
        self.organisms = [o for o in self.organisms if o.energy > 0]
        self.organisms.extend(new_orgs)
        
        # 统计
        self.history.append({
            'population': len(self.organisms),
            'avg_energy': np.mean([o.energy for o in self.organisms]) if self.organisms else 0,
            'food_count': len(self.food)
        })
    
    def run(self, steps=200):
        for _ in range(steps):
            self.step()
            if len(self.organisms) == 0:
                break

def visualize_ecosystem(world, output_path):
    """可视化生态系统"""
    SIZE = 600
    SCALE = SIZE // world.size
    
    img = Image.new('RGB', (SIZE, SIZE), (15, 15, 25))
    
    # 绘制食物
    for x, y in world.food:
        for dx in range(SCALE):
            for dy in range(SCALE):
                img.putpixel((x * SCALE + dx, y * SCALE + dy), (50, 150, 50))
    
    # 绘制生物
    for org in world.organisms:
        x, y = org.x * SCALE, org.y * SCALE
        energy_color = min(255, int(org.energy * 2))
        color = (energy_color, 100, 100)
        for dx in range(SCALE):
            for dy in range(SCALE):
                if 0 <= x + dx < SIZE and 0 <= y + dy < SIZE:
                    img.putpixel((x + dx, y + dy), color)
    
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), f"Pop: {len(world.organisms)}", fill=(255, 255, 255))
    draw.text((10, 30), f"Food: {len(world.food)}", fill=(50, 200, 50))
    draw.text((SIZE // 2 - 30, 10), "Artificial Life", fill=(255, 200, 100))
    
    img.save(output_path)
    print(f'Saved: {output_path}')

if __name__ == '__main__':
    output_dir = r'C:\Users\许耀仁\.openclaw\workspace\experiments'
    
    print('=== Artificial Life ===')
    
    world = World(size=50, food_rate=15)
    
    # 初始种群
    for _ in range(20):
        x, y = random.randint(0, 49), random.randint(0, 49)
        world.add_organism(Organism(x, y))
    
    world.run(steps=200)
    
    print(f'Final population: {len(world.organisms)}')
    if world.history:
        print(f'Final avg energy: {world.history[-1]["avg_energy"]:.1f}')
    
    visualize_ecosystem(world, f'{output_dir}/artificial_life.png')
    
    print('Done')