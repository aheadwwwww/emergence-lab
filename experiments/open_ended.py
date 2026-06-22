"""
#025 Open-endedness - 开放式进化

没有固定目标，系统持续演化
例：生命进化、文化演化、科技发展

本实验模拟开放式系统
"""

import numpy as np
from PIL import Image, ImageDraw
import random
import string

class OpenEndedWorld:
    def __init__(self, size=50):
        self.size = size
        self.creatures = []
        self.resources = set()
        self.generation = 0
        self.history = []
    
    def spawn_resources(self):
        for _ in range(20):
            x, y = random.randint(0, self.size-1), random.randint(0, self.size-1)
            self.resources.add((x, y, random.choice(['A', 'B', 'C'])))
    
    def add_creature(self, genome=None):
        x, y = random.randint(0, self.size-1), random.randint(0, self.size-1)
        genome = genome or ''.join(random.choices('ABCD', k=20))
        self.creatures.append({
            'x': x, 'y': y,
            'genome': genome,
            'energy': 50,
            'age': 0
        })
    
    def step(self):
        self.spawn_resources()
        
        new_creatures = []
        for c in self.creatures:
            # 根据基因组行动
            gene = c['genome'][c['age'] % len(c['genome'])]
            
            if gene == 'A':  # 移动
                c['x'] = (c['x'] + random.choice([-1, 0, 1])) % self.size
                c['y'] = (c['y'] + random.choice([-1, 0, 1])) % self.size
            elif gene == 'B':  # 吃
                for r in list(self.resources):
                    if r[0] == c['x'] and r[1] == c['y']:
                        c['energy'] += 15
                        self.resources.remove(r)
                        break
            elif gene == 'C':  # 繁殖
                if c['energy'] > 70:
                    c['energy'] -= 30
                    child_genome = ''.join(
                        g if random.random() > 0.1 else random.choice('ABCD')
                        for g in c['genome']
                    )
                    new_creatures.append({
                        'x': c['x'], 'y': c['y'],
                        'genome': child_genome,
                        'energy': 30,
                        'age': 0
                    })
            
            c['energy'] -= 0.5
            c['age'] += 1
        
        # 移除死亡的
        self.creatures = [c for c in self.creatures if c['energy'] > 0]
        self.creatures.extend(new_creatures)
        
        self.generation += 1
        self.history.append({
            'pop': len(self.creatures),
            'avg_energy': np.mean([c['energy'] for c in self.creatures]) if self.creatures else 0,
            'unique_genomes': len(set(c['genome'] for c in self.creatures))
        })

def visualize_open_ended(world, output_path):
    SIZE = 600
    img = Image.new('RGB', (SIZE, SIZE), (15, 15, 25))
    
    # 绘制资源
    scale = SIZE // world.size
    for x, y, t in world.resources:
        color = {'A': (255, 100, 100), 'B': (100, 255, 100), 'C': (100, 100, 255)}[t]
        draw = ImageDraw.Draw(img)
        draw.rectangle([x*scale, y*scale, x*scale+scale-1, y*scale+scale-1], fill=color)
    
    # 绘制生物
    for c in world.creatures:
        x, y = c['x'] * scale, c['y'] * scale
        draw.ellipse([x-2, y-2, x+2, y+2], fill=(200, 200, 100))
    
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), f"Gen: {world.generation}", fill=(255, 255, 255))
    draw.text((10, 30), f"Pop: {len(world.creatures)}", fill=(100, 255, 150))
    
    img.save(output_path)
    print(f'Saved: {output_path}')

if __name__ == '__main__':
    output_dir = r'C:\Users\许耀仁\.openclaw\workspace\experiments'
    
    print('=== Open-endedness ===')
    
    world = OpenEndedWorld(size=40)
    for _ in range(15):
        world.add_creature()
    
    for _ in range(300):
        world.step()
        if len(world.creatures) == 0:
            break
    
    print(f'Final population: {len(world.creatures)}')
    if world.history:
        print(f'Final unique genomes: {world.history[-1]["unique_genomes"]}')
    
    visualize_open_ended(world, f'{output_dir}/open_ended.png')
    
    print('Done')