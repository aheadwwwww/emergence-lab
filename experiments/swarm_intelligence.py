"""
Swarm Intelligence - 粒子群优化 (PSO)

群体智能：简单个体通过局部互动解决复杂问题
应用：优化、路径规划、聚类

本实验演示 PSO 寻找函数最小值
"""

import numpy as np
from PIL import Image, ImageDraw
import random

def rastrigin(x, y):
    """Rastrigin 函数 - 多峰测试函数"""
    A = 10
    return A * 2 + (x**2 - A * np.cos(2*np.pi*x)) + (y**2 - A * np.cos(2*np.pi*y))

class Particle:
    def __init__(self, bounds):
        self.position = np.array([
            random.uniform(bounds[0], bounds[1]),
            random.uniform(bounds[0], bounds[1])
        ])
        self.velocity = np.array([
            random.uniform(-1, 1),
            random.uniform(-1, 1)
        ])
        self.best_position = self.position.copy()
        self.best_value = float('inf')
    
    def evaluate(self, objective_func):
        value = objective_func(self.position[0], self.position[1])
        if value < self.best_value:
            self.best_value = value
            self.best_position = self.position.copy()
        return value
    
    def update(self, global_best, w=0.5, c1=1.5, c2=1.5):
        r1, r2 = random.random(), random.random()
        self.velocity = (w * self.velocity +
                        c1 * r1 * (self.best_position - self.position) +
                        c2 * r2 * (global_best - self.position))
        self.position = self.position + self.velocity

class PSO:
    def __init__(self, n_particles=30, bounds=(-5, 5), max_iter=100):
        self.particles = [Particle(bounds) for _ in range(n_particles)]
        self.bounds = bounds
        self.max_iter = max_iter
        self.global_best = None
        self.global_best_value = float('inf')
        self.history = []
    
    def optimize(self, objective_func):
        for iteration in range(self.max_iter):
            for p in self.particles:
                value = p.evaluate(objective_func)
                if value < self.global_best_value:
                    self.global_best_value = value
                    self.global_best = p.position.copy()
            
            for p in self.particles:
                p.update(self.global_best)
            
            self.history.append({
                'iteration': iteration,
                'best_value': self.global_best_value,
                'positions': [p.position.copy() for p in self.particles]
            })
        
        return self.global_best, self.global_best_value

def visualize_pso(pso, output_path):
    """可视化 PSO 收敛过程"""
    SIZE = 600
    img = Image.new('RGB', (SIZE, SIZE), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    # 绘制适应度地形（简化）
    for i in range(SIZE):
        for j in range(SIZE):
            x = -5 + i / SIZE * 10
            y = -5 + j / SIZE * 10
            val = rastrigin(x, y)
            # 归一化到 0-50
            intensity = min(50, int(val / 2))
            draw.point((i, j), fill=(intensity, intensity, intensity+10))
    
    # 绘制最终粒子位置
    for p in pso.particles:
        px = int((p.position[0] + 5) / 10 * SIZE)
        py = int((p.position[1] + 5) / 10 * SIZE)
        draw.ellipse([px-3, py-3, px+3, py+3], fill=(100, 255, 150))
    
    # 绘制全局最优
    if pso.global_best is not None:
        gx = int((pso.global_best[0] + 5) / 10 * SIZE)
        gy = int((pso.global_best[1] + 5) / 10 * SIZE)
        draw.ellipse([gx-6, gy-6, gx+6, gy+6], fill=(255, 100, 100))
    
    draw.text((10, 10), f"Best: {pso.global_best_value:.2f}", fill=(255,255,255))
    draw.text((10, 30), "PSO Optimization", fill=(200,200,200))
    
    img.save(output_path)
    print(f'Saved: {output_path}')

if __name__ == '__main__':
    output_dir = r'C:\Users\许耀仁\.openclaw\workspace\experiments'
    
    print('=== Swarm Intelligence (PSO) ===')
    
    pso = PSO(n_particles=30, bounds=(-5, 5), max_iter=100)
    best_pos, best_val = pso.optimize(rastrigin)
    
    print(f'Best position: {best_pos}')
    print(f'Best value: {best_val}')
    
    visualize_pso(pso, f'{output_dir}/swarm_intelligence.png')
    
    print('Done')