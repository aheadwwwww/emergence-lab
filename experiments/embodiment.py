"""
Embodiment - 具身性

身体塑造认知：感知-行动循环
例：蚂蚁的简单身体+简单规则=复杂行为

本实验模拟具身智能体
"""

import numpy as np
from PIL import Image, ImageDraw
import random

class EmbodiedAgent:
    def __init__(self, x, y, sensors=4):
        self.x = x
        self.y = y
        self.sensors = sensors  # 传感器数量（方向）
        self.direction = 0  # 朝向
        
    def sense(self, grid, size):
        """感知环境"""
        readings = []
        for i in range(self.sensors):
            # 每个传感器感知前方
            angle = self.direction + i * (360 // self.sensors)
            dx = int(np.cos(np.radians(angle)))
            dy = int(np.sin(np.radians(angle)))
            
            # 感知前方几格
            reading = 0
            for dist in range(1, 4):
                nx = (self.x + dx * dist) % size
                ny = (self.y + dy * dist) % size
                if grid[nx, ny] > 0:
                    reading = grid[nx, ny]
                    break
            readings.append(reading)
        
        return readings
    
    def act(self, readings, size):
        """根据感知行动（简单反射）"""
        # 如果前方有障碍，转向
        if readings[0] > 0:  # 前方
            self.direction = (self.direction + 90) % 360
        # 如果左边有食物，转向左
        elif readings[3] == 2:  # 左边有食物
            self.direction = (self.direction - 90) % 360
        # 否则前进
        else:
            dx = int(np.cos(np.radians(self.direction)))
            dy = int(np.sin(np.radians(self.direction)))
            self.x = (self.x + dx) % size
            self.y = (self.y + dy) % size

def run_embodied_simulation(size=50, steps=200):
    """运行具身模拟"""
    grid = np.zeros((size, size), dtype=int)
    
    # 添加食物
    for _ in range(size * 2):
        x, y = random.randint(0, size-1), random.randint(0, size-1)
        grid[x, y] = 2  # 食物
    
    # 添加障碍
    for _ in range(size * 3):
        x, y = random.randint(0, size-1), random.randint(0, size-1)
        grid[x, y] = 1  # 障碍
    
    agent = EmbodiedAgent(size//2, size//2)
    collected = 0
    history = [(agent.x, agent.y)]
    
    for _ in range(steps):
        readings = agent.sense(grid, size)
        agent.act(readings, size)
        
        # 检查是否收集到食物
        if grid[agent.x, agent.y] == 2:
            collected += 1
            grid[agent.x, agent.y] = 0
        
        history.append((agent.x, agent.y))
    
    return grid, agent, collected, history

def visualize_embodiment(grid, history, output_path):
    """可视化具身行为"""
    SIZE = 600
    scale = SIZE // grid.shape[0]
    
    img = Image.new('RGB', (SIZE, SIZE), (15, 15, 25))
    
    # 绘制环境
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            x, y = i * scale, j * scale
            if grid[i, j] == 1:
                color = (80, 80, 80)
            elif grid[i, j] == 2:
                color = (50, 150, 50)
            else:
                continue
            
            draw = ImageDraw.Draw(img)
            draw.rectangle([x, y, x+scale-1, y+scale-1], fill=color)
    
    # 绘制轨迹
    draw = ImageDraw.Draw(img)
    for i in range(1, len(history)):
        x1, y1 = history[i-1]
        x2, y2 = history[i]
        draw.line([x1*scale, y1*scale, x2*scale, y2*scale], fill=(100, 200, 255), width=1)
    
    draw.text((10, 10), "Embodied Agent", fill=(255,255,255))
    
    img.save(output_path)
    print(f'Saved: {output_path}')

if __name__ == '__main__':
    output_dir = r'C:\Users\许耀仁\.openclaw\workspace\experiments'
    
    print('=== Embodiment ===')
    
    grid, agent, collected, history = run_embodied_simulation(size=50, steps=300)
    
    print(f'Food collected: {collected}')
    print(f'Steps taken: {len(history)}')
    
    visualize_embodiment(grid, history, f'{output_dir}/embodiment.png')
    
    print('Done')