"""
Phase Transitions - 相变实验
模拟物质从有序到无序的临界转变
"""

import numpy as np
from PIL import Image
import random
import time
from pathlib import Path
from registry import BaseExperiment, OUTPUT_DIR

class PhaseTransitions(BaseExperiment):
    """
    Ising 模型相变模拟
    - 模拟磁铁从顺磁到铁磁的转变
    - 临界温度附近涌现大规模磁畴
    """
    name = "phase_transitions"
    description = "相变实验 - Ising 模型临界现象"
    
    def generate_params(self):
        return {
            'size': random.choice([100, 150]),
            'steps': random.randint(500, 1000),
            'temperature': random.uniform(1.5, 3.0),  # 临界点约 2.27
            'field': random.choice([0, 0.01, 0.05])
        }
    
    def run(self, params):
        size = params['size']
        steps = params['steps']
        T = params['temperature']
        H = params['field']
        
        # 初始化自旋网格 (+1 或 -1)
        grid = np.random.choice([-1, 1], size=(size, size))
        
        # Metropolis 算法
        for step in range(steps):
            # 每步更新 size^2/10 个随机格点
            for _ in range(size * size // 10):
                i = random.randint(0, size - 1)
                j = random.randint(0, size - 1)
                
                # 计算能量变化
                spin = grid[i, j]
                neighbors = (
                    grid[(i+1) % size, j] +
                    grid[(i-1) % size, j] +
                    grid[i, (j+1) % size] +
                    grid[i, (j-1) % size]
                )
                dE = 2 * spin * (neighbors + H)
                
                # Metropolis 准则
                if dE < 0 or random.random() < np.exp(-dE / T):
                    grid[i, j] = -spin
        
        # 计算磁化强度
        magnetization = np.abs(np.mean(grid))
        
        return {
            'grid': grid,
            'temperature': T,
            'magnetization': magnetization,
            'phase': 'ordered' if magnetization > 0.5 else 'disordered'
        }
    
    def visualize(self, result):
        grid = result['grid']
        size = len(grid)
        T = result['temperature']
        mag = result['magnetization']
        
        img = Image.new('RGB', (size * 3, size * 3 + 40), (10, 10, 20))
        pixels = img.load()
        
        # 画网格
        for i in range(size):
            for j in range(size):
                if grid[i, j] == 1:
                    c = (255, 100, 100)  # 红色 = +1
                else:
                    c = (100, 100, 255)  # 蓝色 = -1
                for di in range(3):
                    for dj in range(3):
                        pixels[j * 3 + dj, i * 3 + di] = c
        
        # 添加温度和磁化强度信息
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        info = f"T={T:.2f} |M|={mag:.2f} phase={result['phase']}"
        draw.text((5, size * 3 + 10), info, fill=(200, 200, 200))
        
        return img
    
    def describe(self, params, result):
        phase_emoji = "🧲" if result['phase'] == 'ordered' else "🌀"
        return f"Ising Model T={result['temperature']:.2f} |M|={result['magnetization']:.2f} {phase_emoji}"

if __name__ == '__main__':
    exp = PhaseTransitions()
    params = exp.generate_params()
    print(f'Params: {params}')
    
    result = exp.run(params)
    print(f'Done: {exp.describe(params, result)}')
    
    img = exp.visualize(result)
    path = exp.save_image(img)
    print(f'Saved: {path}')
