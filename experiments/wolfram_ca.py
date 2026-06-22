"""
Wolfram Elementary Cellular Automata
展示256条一维规则产生的不同模式

规则用8位编码：
111 -> 0/1
110 -> 0/1
101 -> 0/1
100 -> 0/1
011 -> 0/1
010 -> 0/1
001 -> 0/1
000 -> 0/1

Wolfram 分类：
- Class 1: 稳定（规则 0, 4, 8...）
- Class 2: 周期（规则 1, 5, 10...）
- Class 3: 混沌（规则 30, 45, 90, 150...）
- Class 4: 复杂（规则 110, 54...）- 图灵完备！
"""

import numpy as np
from PIL import Image
import os

WIDTH = 200
STEPS = 100

def rule_to_binary(rule_num):
    """Convert rule number (0-255) to 8-bit pattern"""
    return [(rule_num >> i) & 1 for i in range(7, -1, -1)]

def evolve_row(row, rule_bits):
    """Evolve one row using the rule"""
    new_row = np.zeros_like(row)
    for i in range(len(row)):
        # Get 3-cell neighborhood (wrap around)
        left = row[(i - 1) % len(row)]
        center = row[i]
        right = row[(i + 1) % len(row)]
        
        # Convert to index (0-7)
        pattern = int(left * 4 + center * 2 + right)
        new_row[i] = rule_bits[pattern]
    return new_row

def run_rule(rule_num):
    """Run one rule and return image"""
    rule_bits = rule_to_binary(rule_num)
    
    # Initialize: single black cell in center
    grid = np.zeros((STEPS, WIDTH), dtype=np.uint8)
    grid[0, WIDTH // 2] = 1
    
    # Evolve
    for step in range(1, STEPS):
        grid[step] = evolve_row(grid[step - 1], rule_bits)
    
    return grid

def visualize_rules(rules, output_name):
    """Visualize multiple rules side by side"""
    n_rules = len(rules)
    total_width = WIDTH * n_rules
    total_height = STEPS
    
    canvas = np.zeros((total_height, total_width), dtype=np.uint8)
    
    for i, rule_num in enumerate(rules):
        grid = run_rule(rule_num)
        offset = i * WIDTH
        canvas[:, offset:offset + WIDTH] = grid
    
    # Scale up
    scale = 3
    canvas_scaled = np.repeat(np.repeat(canvas, scale, axis=0), scale, axis=1)
    
    # Colorize (black cells = blue, white = light gray)
    img_array = np.zeros((total_height * scale, total_width * scale, 3), dtype=np.uint8)
    img_array[canvas_scaled == 1] = [30, 120, 220]  # Blue
    img_array[canvas_scaled == 0] = [245, 245, 250]  # Light gray
    
    img = Image.fromarray(img_array)
    
    output_dir = r'C:\Users\许耀仁\.openclaw\workspace\experiments'
    output_path = os.path.join(output_dir, output_name)
    img.save(output_path)
    print(f'Saved: {output_path}')

output_dir = r'C:\Users\许耀仁\.openclaw\workspace\experiments'
os.makedirs(output_dir, exist_ok=True)

# Class 1: Stable
visualize_rules([0, 4, 8, 16, 32, 64, 128, 255], 'wolfram_class1.png')

# Class 2: Periodic
visualize_rules([1, 3, 5, 10, 12, 14, 18, 22], 'wolfram_class2.png')

# Class 3: Chaotic
visualize_rules([30, 45, 90, 105, 150, 154, 170, 210], 'wolfram_class3.png')

# Class 4: Complex (Turing complete!)
visualize_rules([54, 110, 62, 94, 147, 193], 'wolfram_class4.png')

print('All Wolfram CA experiments completed.')