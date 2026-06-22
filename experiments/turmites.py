"""
Turmites（图米特）- 朗顿蚂蚁的推广
多色状态蚂蚁，规则表可以自定义

观察不同规则表产生的不同涌现模式
"""

import numpy as np
from PIL import Image
import os

# Grid size
SIZE = 200
STEPS = 50000

# Rule table: {(state, color): (new_color, turn, new_state)}
# This is the classic Langton's Ant extended to multi-color
# Try the "RL" rule (classic), then "RLR", "LLRR", "LRRRRRLLR"

RULES = {
    # Classic 2-color Langton's Ant
    'RL': {(0, 0): (1, 'R', 0), (0, 1): (0, 'L', 0)},
    # Tri-color: creates a triangle pattern
    'RLR': {(0, 0): (1, 'R', 0), (0, 1): (2, 'L', 0), (0, 2): (0, 'R', 0)},
    # Four-color: creates a filling pattern
    'LLRR': {(0, 0): (1, 'L', 0), (0, 1): (2, 'L', 0), (0, 2): (3, 'R', 0), (0, 3): (0, 'R', 0)},
    # Nine-color: creates complex highway
    'LRRRRRLLR': {(0, 0): (1, 'L', 0), (0, 1): (2, 'R', 0), (0, 2): (3, 'R', 0), 
                  (0, 3): (4, 'R', 0), (0, 4): (5, 'R', 0), (0, 5): (6, 'R', 0),
                  (0, 6): (7, 'L', 0), (0, 7): (8, 'L', 0), (0, 8): (0, 'R', 0)},
}

def run_turmite(rule_name, rule_table, num_colors):
    grid = np.zeros((SIZE, SIZE), dtype=np.uint8)
    x, y = SIZE // 2, SIZE // 2
    direction = 0
    state = 0
    dx = [0, 1, 0, -1]
    dy = [-1, 0, 1, 0]
    
    for step in range(STEPS):
        color = grid[y, x]
        key = (state, color)
        if key in rule_table:
            new_color, turn, new_state = rule_table[key]
            grid[y, x] = new_color
            state = new_state
            
            if turn == 'R':
                direction = (direction + 1) % 4
            elif turn == 'L':
                direction = (direction - 1) % 4
            
            x = (x + dx[direction]) % SIZE
            y = (y + dy[direction]) % SIZE
    
    # Create colored image
    img_array = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)
    
    # Color palette
    colors = [
        (255, 255, 255),  # 0: white
        (0, 0, 0),        # 1: black
        (220, 50, 50),    # 2: red
        (50, 120, 220),   # 3: blue
        (50, 180, 50),    # 4: green
        (220, 180, 50),   # 5: yellow
        (180, 50, 220),   # 6: purple
        (50, 220, 200),   # 7: teal
        (220, 130, 50),   # 8: orange
    ]
    
    for c in range(num_colors):
        mask = grid == c
        for ch in range(3):
            img_array[:, :, ch][mask] = colors[c][ch]
    
    img = Image.fromarray(img_array)
    return img

# Run all rules
output_dir = r'C:\Users\许耀仁\.openclaw\workspace\experiments'
os.makedirs(output_dir, exist_ok=True)

rule_configs = [
    ('RL', 2, 50000),
    ('RLR', 3, 50000),
    ('LLRR', 4, 50000),
    ('LRRRRRLLR', 9, 50000),
]

for rule_name, num_colors, steps in rule_configs:
    print(f'Running rule {rule_name} ({num_colors} colors, {steps} steps)...', flush=True)
    img = run_turmite(rule_name, RULES[rule_name], num_colors)
    output_path = os.path.join(output_dir, f'turmite_{rule_name}.png')
    img.save(output_path)
    print(f'  Saved: {output_path}')

print('All turmite experiments completed.')
