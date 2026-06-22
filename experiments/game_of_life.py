"""
Conway's Game of Life - 经典元胞自动机
规则：
1. 活细胞有2或3个活邻居 → 存活
2. 活细胞有<2或>3个活邻居 → 死亡
3. 死细胞恰好有3个活邻居 → 复活

观察经典模式：滑翔机、滑翔机枪、脉冲星
"""

import numpy as np
from PIL import Image, ImageDraw
import os

SIZE = 100
STEPS = 200

# Initialize with random pattern + some classic structures
grid = np.zeros((SIZE, SIZE), dtype=np.uint8)

# Add random cells
np.random.seed(42)
random_cells = np.random.rand(SIZE, SIZE) < 0.15
grid[random_cells] = 1

# Add a Gosper Glider Gun at position (10, 10)
gun_pattern = [
    (0,4),(0,5),(1,4),(1,5),
    (10,4),(10,5),(10,6),(11,3),(11,7),(12,2),(12,8),(13,2),(13,8),
    (14,5),(15,3),(15,7),(16,4),(16,5),(16,6),(17,5),
    (20,2),(20,3),(20,4),(21,2),(21,3),(21,4),(22,1),(22,5),
    (24,0),(24,1),(24,5),(24,6),
    (34,2),(34,3),(35,2),(35,3)
]

offset_x, offset_y = 5, 5
for dy, dx in gun_pattern:
    y, x = offset_y + dy, offset_x + dx
    if 0 <= y < SIZE and 0 <= x < SIZE:
        grid[y, x] = 1

# Add a Pulsar (period 3 oscillator) at (60, 60)
pulsar_offsets = [
    (0,2),(0,3),(0,4),(0,8),(0,9),(0,10),
    (2,0),(3,0),(4,0),(2,5),(3,5),(4,5),(2,7),(3,7),(4,7),(2,12),(3,12),(4,12),
    (5,2),(5,3),(5,4),(5,8),(5,9),(5,10),
    (7,2),(7,3),(7,4),(7,8),(7,9),(7,10),
    (8,0),(9,0),(10,0),(8,5),(9,5),(10,5),(8,7),(9,7),(10,7),(8,12),(9,12),(10,12),
    (12,2),(12,3),(12,4),(12,8),(12,9),(12,10),
]

offset_x, offset_y = 60, 60
for dy, dx in pulsar_offsets:
    y, x = offset_y + dy, offset_x + dx
    if 0 <= y < SIZE and 0 <= x < SIZE:
        grid[y, x] = 1

def step_life(grid):
    new_grid = np.zeros_like(grid)
    for y in range(SIZE):
        for x in range(SIZE):
            # Count neighbors
            neighbors = 0
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dy == 0 and dx == 0:
                        continue
                    ny, nx = (y + dy) % SIZE, (x + dx) % SIZE
                    neighbors += grid[ny, nx]
            
            if grid[y, x] == 1:  # Alive
                if neighbors == 2 or neighbors == 3:
                    new_grid[y, x] = 1
            else:  # Dead
                if neighbors == 3:
                    new_grid[y, x] = 1
    return new_grid

# Run and save frames
frames = []
for step in range(STEPS):
    # Create image
    img = Image.new('RGB', (SIZE*4, SIZE*4), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    for y in range(SIZE):
        for x in range(SIZE):
            if grid[y, x] == 1:
                draw.rectangle([x*4, y*4, x*4+3, y*4+3], fill=(30, 120, 220))
    
    frames.append(img)
    grid = step_life(grid)
    
    if step % 50 == 0:
        alive = np.sum(grid)
        print(f'Step {step}: {alive} alive cells', flush=True)

# Save GIF
output_path = r'C:\Users\许耀仁\.openclaw\workspace\experiments\game_of_life.gif'
frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=50, loop=0)
print(f'Game of Life completed: {STEPS} steps')
print(f'GIF saved to: {output_path}')
