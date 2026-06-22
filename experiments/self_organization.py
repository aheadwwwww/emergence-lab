"""
Self-Organization - 自组织

没有外部协调，系统自发形成有序结构
例：市场、语言、社会规范

本实验模拟简单的自组织排序
"""

import numpy as np
from PIL import Image, ImageDraw
import random

def self_sorting_particles(n=100, size=100, steps=200):
    """自组织排序：粒子自发分成两组"""
    # 初始化：两种粒子随机分布
    grid = np.zeros((size, size), dtype=int)  # 0=空, 1=A类, 2=B类
    positions = []
    
    for i in range(n):
        x, y = random.randint(0, size-1), random.randint(0, size-1)
        while grid[x, y] != 0:
            x, y = random.randint(0, size-1), random.randint(0, size-1)
        particle_type = 1 if i < n // 2 else 2
        grid[x, y] = particle_type
        positions.append((x, y, particle_type))
    
    history = []
    
    for step in range(steps):
        # 每个粒子尝试移动到更"舒服"的位置
        for idx, (x, y, ptype) in enumerate(positions):
            # 计算当前满意度（同类型邻居比例）
            neighbors = []
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = (x + dx) % size, (y + dy) % size
                    neighbors.append(grid[nx, ny])
            
            same_type = sum(1 for n in neighbors if n == ptype)
            total_neighbors = sum(1 for n in neighbors if n != 0)
            
            if total_neighbors == 0:
                satisfaction = 0.5
            else:
                satisfaction = same_type / total_neighbors
            
            # 如果不满意，尝试移动
            if satisfaction < 0.5:
                # 随机选择一个空位置
                new_x, new_y = random.randint(0, size-1), random.randint(0, size-1)
                attempts = 0
                while grid[new_x, new_y] != 0 and attempts < 20:
                    new_x, new_y = random.randint(0, size-1), random.randint(0, size-1)
                    attempts += 1
                
                if grid[new_x, new_y] == 0:
                    grid[x, y] = 0
                    grid[new_x, new_y] = ptype
                    positions[idx] = (new_x, new_y, ptype)
        
        history.append(grid.copy())
    
    return history

def visualize_self_organization(history, output_path):
    """可视化自组织过程"""
    frames = [0, len(history)//4, len(history)//2, len(history)-1]
    
    SIZE = 600
    img = Image.new('RGB', (SIZE * 2, SIZE * 2), (15, 15, 25))
    
    grid_size = history[0].shape[0]
    
    for idx, frame in enumerate(frames):
        grid = history[frame]
        row = idx // 2
        col = idx % 2
        
        panel_size = SIZE
        scale = panel_size // grid_size
        
        for i in range(grid_size):
            for j in range(grid_size):
                x = col * SIZE + j * scale
                y = row * SIZE + i * scale
                
                if grid[i, j] == 1:
                    color = (255, 100, 100)
                elif grid[i, j] == 2:
                    color = (100, 100, 255)
                else:
                    continue  # 跳过空格
                
                # 用矩形代替逐像素
                draw = ImageDraw.Draw(img)
                draw.rectangle([x, y, x+scale-1, y+scale-1], fill=color)
        
        draw = ImageDraw.Draw(img)
        draw.text((col * SIZE + 10, row * SIZE + 10), f"Step {frame}", fill=(255, 255, 255))
    
    draw = ImageDraw.Draw(img)
    draw.text((SIZE, 5), "Self-Organization", fill=(255, 200, 100))
    
    img.save(output_path)
    print(f'Saved: {output_path}')

if __name__ == '__main__':
    output_dir = r'C:\Users\许耀仁\.openclaw\workspace\experiments'
    
    print('=== Self-Organization ===')
    
    history = self_sorting_particles(n=200, size=80, steps=100)
    
    print(f'Initial: particles randomly distributed')
    print(f'Final: particles self-organized')
    
    visualize_self_organization(history, f'{output_dir}/self_organization.png')
    
    print('Done')