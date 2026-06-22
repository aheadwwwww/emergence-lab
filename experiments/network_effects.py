"""
Network Effects - 网络效应

Metcalfe 定律：网络价值 ∝ n²
病毒传播、信息扩散、级联效应

本实验模拟网络上的信息传播
"""

import numpy as np
from PIL import Image, ImageDraw
import random
from collections import deque

class Network:
    def __init__(self, n_nodes=100, edge_prob=0.05):
        self.n = n_nodes
        self.edges = {i: set() for i in range(n_nodes)}
        
        # 随机图（Erdos-Renyi）
        for i in range(n_nodes):
            for j in range(i+1, n_nodes):
                if random.random() < edge_prob:
                    self.edges[i].add(j)
                    self.edges[j].add(i)
    
    def get_neighbors(self, node):
        return self.edges[node]

class InformationDiffusion:
    def __init__(self, network, seed_nodes=None, threshold=0.3):
        self.network = network
        self.threshold = threshold
        self.infected = set(seed_nodes) if seed_nodes else set([0])
        self.history = [self.infected.copy()]
    
    def step(self):
        """一步传播"""
        new_infected = set()
        for node in range(self.network.n):
            if node in self.infected:
                continue
            
            # 计算被感染的比例
            neighbors = self.network.get_neighbors(node)
            if len(neighbors) == 0:
                continue
            
            infected_neighbors = len(neighbors & self.infected)
            ratio = infected_neighbors / len(neighbors)
            
            if ratio >= self.threshold:
                new_infected.add(node)
        
        self.infected |= new_infected
        self.history.append(self.infected.copy())
        return len(new_infected) > 0
    
    def run(self, max_steps=50):
        for _ in range(max_steps):
            if not self.step():
                break

def visualize_network(network, infected, output_path):
    """可视化网络和感染状态"""
    SIZE = 600
    img = Image.new('RGB', (SIZE, SIZE), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    # 计算节点位置（圆形布局）
    positions = {}
    center = SIZE // 2
    radius = SIZE // 2 - 40
    
    for i in range(network.n):
        angle = 2 * np.pi * i / network.n
        x = center + radius * np.cos(angle)
        y = center + radius * np.sin(angle)
        positions[i] = (x, y)
    
    # 绘制边
    for i in range(network.n):
        for j in network.edges[i]:
            if j > i:
                x1, y1 = positions[i]
                x2, y2 = positions[j]
                draw.line([x1, y1, x2, y2], fill=(40, 40, 50), width=1)
    
    # 绘制节点
    for i in range(network.n):
        x, y = positions[i]
        color = (255, 100, 100) if i in infected else (50, 100, 150)
        draw.ellipse([x-4, y-4, x+4, y+4], fill=color)
    
    # 统计
    infected_count = len(infected)
    total = network.n
    draw.text((10, 10), f"Infected: {infected_count}/{total}", fill=(255,255,255))
    draw.text((10, 30), f"Network Effects", fill=(200,200,200))
    
    img.save(output_path)
    print(f'Saved: {output_path}')

def visualize_diffusion_history(history, output_path):
    """可视化传播曲线"""
    SIZE = 600
    MARGIN = 60
    WIDTH = SIZE - 2 * MARGIN
    HEIGHT = SIZE - 2 * MARGIN
    
    img = Image.new('RGB', (SIZE, SIZE), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    # 坐标轴
    draw.line([MARGIN, MARGIN, MARGIN, SIZE-MARGIN], fill=(80,80,80), width=2)
    draw.line([MARGIN, SIZE-MARGIN, SIZE-MARGIN, SIZE-MARGIN], fill=(80,80,80), width=2)
    
    # 曲线
    max_val = max(len(h) for h in history) if history else 1
    steps = len(history)
    
    for i in range(1, steps):
        x1 = MARGIN + (i-1) / steps * WIDTH
        y1 = SIZE - MARGIN - len(history[i-1]) / max_val * HEIGHT
        x2 = MARGIN + i / steps * WIDTH
        y2 = SIZE - MARGIN - len(history[i]) / max_val * HEIGHT
        draw.line([x1, y1, x2, y2], fill=(100, 255, 150), width=2)
    
    draw.text((SIZE//2-30, 20), "Information Diffusion", fill=(255,255,255))
    draw.text((10, MARGIN), f"{max_val}", fill=(200,200,200))
    draw.text((MARGIN, SIZE-40), "0", fill=(200,200,200))
    
    img.save(output_path)
    print(f'Saved: {output_path}')

if __name__ == '__main__':
    output_dir = r'C:\Users\许耀仁\.openclaw\workspace\experiments'
    
    print('=== Network Effects ===')
    
    # 创建网络
    network = Network(n_nodes=100, edge_prob=0.15)
    
    # 信息传播
    diffusion = InformationDiffusion(network, seed_nodes=[0, 5, 10], threshold=0.15)
    diffusion.run(max_steps=30)
    
    print(f'Initial infected: 2')
    print(f'Final infected: {len(diffusion.infected)}')
    print(f'Steps: {len(diffusion.history)}')
    
    # 可视化
    visualize_network(network, diffusion.infected, f'{output_dir}/network_effects.png')
    visualize_diffusion_history(diffusion.history, f'{output_dir}/diffusion_curve.png')
    
    print('Done')