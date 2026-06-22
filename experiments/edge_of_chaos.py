"""
Edge of Chaos - 混沌边缘

Langton 参数 λ：细胞自动机行为的关键指标
- λ ≈ 0：所有细胞趋向同一状态（冻结）
- λ ≈ 0.5：随机混沌（无序）
- λ ≈ 0.3-0.4：混沌边缘（复杂、有趣的行为）

本实验演示不同 λ 值下的 CA 行为
"""

import numpy as np
from PIL import Image, ImageDraw
import random

def random_rule_table(lambda_param, states=2, neighborhood_size=5):
    """根据 λ 参数生成随机规则表"""
    # λ 是 quiescent state 的比例
    # quiescent state = 0
    rule_size = states ** neighborhood_size
    rule = [0] * rule_size
    
    # 随机选择 (1-λ) 的位置设为非零
    non_zero_count = int(rule_size * (1 - lambda_param))
    non_zero_positions = random.sample(range(rule_size), non_zero_count)
    
    for pos in non_zero_positions:
        rule[pos] = random.randint(1, states - 1)
    
    return rule

def apply_rule(grid, rule, neighborhood_size=5):
    """应用规则到网格"""
    size = len(grid)
    new_grid = [[0] * size for _ in range(size)]
    half = neighborhood_size // 2
    
    for i in range(size):
        for j in range(size):
            # 计算邻域状态（作为规则表索引）
            neighborhood = 0
            for di in range(-half, half + 1):
                for dj in range(-half, half + 1):
                    idx = (di + half) * neighborhood_size + (dj + half)
                    state = grid[(i + di) % size][(j + dj) % size]
                    neighborhood += state * (2 ** idx)
            
            new_grid[i][j] = rule[int(neighborhood) % len(rule)]
    
    return new_grid

def run_ca_1d(rule_number=110, size=200, steps=200):
    """运行 1D CA（Wolfram 规则）"""
    grid = np.zeros((steps, size), dtype=int)
    grid[0, size // 2] = 1  # 中心种子
    
    for t in range(1, steps):
        for i in range(size):
            left = grid[t-1, (i-1) % size]
            center = grid[t-1, i]
            right = grid[t-1, (i+1) % size]
            
            # Wolfram 规则编号转二进制
            pattern = left * 4 + center * 2 + right
            grid[t, i] = (rule_number >> pattern) & 1
    
    return grid

def visualize_ca_1d(grid, output_path, title):
    """可视化 1D CA"""
    steps, size = grid.shape
    SCALE = 4
    
    img = Image.new('RGB', (size * SCALE, steps * SCALE), (15, 15, 25))
    pixels = img.load()
    
    for t in range(steps):
        for i in range(size):
            color = (255, 255, 255) if grid[t, i] else (20, 20, 30)
            for di in range(SCALE):
                for dj in range(SCALE):
                    pixels[i * SCALE + di, t * SCALE + dj] = color
    
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), title, fill=(100, 200, 255))
    
    img.save(output_path)
    print(f'Saved: {output_path}')

def visualize_edge_of_chaos(output_path):
    """可视化混沌边缘：不同规则的行为"""
    # 选择不同类型的规则
    rules = [
        (4, "Rule 4 (Frozen)"),      # Class I: 稳定
        (108, "Rule 108 (Periodic)"), # Class II: 周期
        (110, "Rule 110 (Complex)"),  # Class IV: 复杂
        (30, "Rule 30 (Chaotic)"),    # Class III: 混沌
    ]
    
    SIZE = 400
    MARGIN = 10
    img = Image.new('RGB', (SIZE * 2 + MARGIN, SIZE * 2 + MARGIN), (15, 15, 25))
    
    for idx, (rule_num, label) in enumerate(rules):
        row = idx // 2
        col = idx % 2
        
        grid = run_ca_1d(rule_num, size=100, steps=100)
        
        # 缩放并粘贴
        SCALE = 4
        ca_img = Image.new('RGB', (100 * SCALE, 100 * SCALE), (15, 15, 25))
        pixels = ca_img.load()
        
        for t in range(100):
            for i in range(100):
                color = (255, 255, 255) if grid[t, i] else (20, 20, 30)
                for di in range(SCALE):
                    for dj in range(SCALE):
                        pixels[i * SCALE + di, t * SCALE + dj] = color
        
        x = col * (SIZE + MARGIN)
        y = row * (SIZE + MARGIN)
        img.paste(ca_img, (x + 20, y + 40))
        
        draw = ImageDraw.Draw(img)
        draw.text((x + 20, y + 10), label, fill=(100, 200, 255))
    
    draw = ImageDraw.Draw(img)
    draw.text((SIZE, 5), "Edge of Chaos: Rule 110", fill=(255, 200, 100))
    
    img.save(output_path)
    print(f'Saved: {output_path}')

if __name__ == '__main__':
    from pathlib import Path; output_dir = str(Path(r'D:\emergence_experiments').resolve())
    
    print('=== Edge of Chaos ===')
    
    # 单独可视化几个规则
    for rule_num in [4, 30, 110]:
        grid = run_ca_1d(rule_num, size=200, steps=200)
        visualize_ca_1d(grid, f'{output_dir}/ca_rule{rule_num}.png', f'Rule {rule_num}')
    
    # 混合图
    visualize_edge_of_chaos(f'{output_dir}/edge_of_chaos.png')
    
    print('Done')