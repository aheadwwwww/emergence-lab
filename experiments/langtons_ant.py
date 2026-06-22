"""
Langton's Ant 涌现演示
规则：
1. 在白色格子上，蚂蚁右转，格子变黑
2. 在黑色格子上，蚂蚁左转，格子变白
3. 向前移动一步

观察：约10000步后开始构建"高速公路"结构
"""

import numpy as np
from PIL import Image
import os

# Grid size
SIZE = 100
STEPS = 11000

# Grid: 0=white, 1=black
grid = np.zeros((SIZE, SIZE), dtype=np.uint8)

# Ant position and direction
x, y = SIZE // 2, SIZE // 2
# Direction: 0=up, 1=right, 2=down, 3=left
direction = 0

# Directions movement
dx = [0, 1, 0, -1]
dy = [-1, 0, 1, 0]

def turn_right(d):
    return (d + 1) % 4

def turn_left(d):
    return (d - 1) % 4

# Run simulation
for step in range(STEPS):
    # Get current cell color
    cell = grid[y, x]
    
    # Apply rules
    if cell == 0:  # White
        direction = turn_right(direction)
        grid[y, x] = 1  # Turn black
    else:  # Black
        direction = turn_left(direction)
        grid[y, x] = 0  # Turn white
    
    # Move forward
    x = (x + dx[direction]) % SIZE
    y = (y + dy[direction]) % SIZE

# Save image
output_path = r'C:\Users\许耀仁\.openclaw\workspace\experiments\langtons_ant.png'

# Create directory if needed
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Convert to image (black=1, white=0, invert for display)
img_array = (1 - grid) * 255  # White pixels = 255
img = Image.fromarray(img_array, mode='L')
img.save(output_path)

print(f'Langton\'s Ant simulation completed: {STEPS} steps')
print(f'Image saved to: {output_path}')
print(f'Grid coverage: {np.sum(grid)} black cells out of {SIZE*SIZE}')