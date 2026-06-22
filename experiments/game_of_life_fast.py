"""
Conway's Game of Life - NumPy optimized
"""

import numpy as np
from PIL import Image
import os

SIZE = 150
STEPS = 300

# Initialize
grid = np.zeros((SIZE, SIZE), dtype=np.uint8)

# Random cells
np.random.seed(42)
grid[np.random.rand(SIZE, SIZE) < 0.12] = 1

# Gosper Glider Gun
gun = [(0,4),(0,5),(1,4),(1,5),(10,4),(10,5),(10,6),(11,3),(11,7),(12,2),(12,8),
       (13,2),(13,8),(14,5),(15,3),(15,7),(16,4),(16,5),(16,6),(17,5),
       (20,2),(20,3),(20,4),(21,2),(21,3),(21,4),(22,1),(22,5),
       (24,0),(24,1),(24,5),(24,6),(34,2),(34,3),(35,2),(35,3)]
for dy, dx in gun:
    y, x = 5 + dy, 5 + dx
    if 0 <= y < SIZE and 0 <= x < SIZE:
        grid[y, x] = 1

def step_life(grid):
    # Count neighbors using rolled arrays
    neighbors = sum(np.roll(np.roll(grid, dy, axis=0), dx, axis=1) 
                    for dy in [-1, 0, 1] for dx in [-1, 0, 1]
                    if not (dy == 0 and dx == 0))
    # Apply rules
    new_grid = ((grid == 1) & ((neighbors == 2) | (neighbors == 3))) | \
               ((grid == 0) & (neighbors == 3))
    return new_grid.astype(np.uint8)

# Run simulation and save frames
SCALE = 4
frames = []
for step in range(STEPS):
    # Create image
    img_array = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)
    img_array[grid == 1] = [30, 120, 220]  # Blue alive cells
    img_array[grid == 0] = [245, 245, 250]  # Light gray background
    
    # Scale up
    img_array = np.repeat(np.repeat(img_array, SCALE, axis=0), SCALE, axis=1)
    img = Image.fromarray(img_array)
    frames.append(img)
    
    grid = step_life(grid)

output_path = r'C:\Users\许耀仁\.openclaw\workspace\experiments\game_of_life.gif'
frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=50, loop=0)
print(f'Game of Life completed: {STEPS} steps, final alive: {np.sum(grid)}')
print(f'GIF saved to: {output_path}')
