"""
Self-Organized Criticality - Abelian Sandpile
Bak-Tang-Wiesenfeld 沙堆模型

规则：
1. 随机向网格添加沙粒
2. 任何位置沙粒>=4时"崩塌"，向4个邻居各分1粒
3. 崩塌可能引发连锁反应（雪崩）

观察：雪崩大小的幂律分布——系统自组织到临界态
"""

import numpy as np
from PIL import Image, ImageDraw
import os

SIZE = 100
TOTAL_GRAINS = 50000
SAMPLE_EVERY = 500

grid = np.zeros((SIZE, SIZE), dtype=np.int32)
avalanche_sizes = []

def topple(grid):
    """Topple until stable, return avalanche size"""
    avalanche = 0
    while True:
        unstable = grid >= 4
        if not np.any(unstable):
            break
        n_topple = np.sum(unstable)
        avalanche += n_topple
        
        # Subtract 4 from unstable cells
        grid[unstable] -= 4
        
        # Add 1 to each neighbor
        grid[np.roll(unstable, 1, axis=0)] += 1  # up
        grid[np.roll(unstable, -1, axis=0)] += 1  # down
        grid[np.roll(unstable, 1, axis=1)] += 1   # left
        grid[np.roll(unstable, -1, axis=1)] += 1   # right
        
        # Open boundaries: remove sand at edges
        grid[0, :] = 0
        grid[-1, :] = 0
        grid[:, 0] = 0
        grid[:, -1] = 0
    
    return avalanche

# Run simulation
frames = []
for grain in range(TOTAL_GRAINS):
    # Drop grain at center
    cx, cy = SIZE // 2, SIZE // 2
    grid[cy, cx] += 1
    
    # Topple
    avalanche = topple(grid)
    avalanche_sizes.append(avalanche)
    
    # Save frame periodically
    if grain % SAMPLE_EVERY == 0 and grain > 0:
        # Create colored image
        img_array = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)
        colors = [
            (245, 245, 250),  # 0: light gray
            (100, 180, 255),  # 1: light blue
            (30, 120, 220),   # 2: blue
            (220, 50, 50),    # 3: red (unstable)
        ]
        for c in range(4):
            mask = grid == c
            for ch in range(3):
                img_array[:, :, ch][mask] = colors[c][ch]
        
        # Scale up
        img_array = np.repeat(np.repeat(img_array, 4, axis=0), 4, axis=1)
        img = Image.fromarray(img_array)
        frames.append(img)
        
        if grain % 5000 == 0:
            avg_av = np.mean(avalanche_sizes[-1000:]) if len(avalanche_sizes) > 1000 else 0
            print(f'Grain {grain}: avg avalanche={avg_av:.1f}, max={np.max(grid)}', flush=True)

# Save GIF
output_path = r'C:\Users\许耀仁\.openclaw\workspace\experiments\sandpile.gif'
frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=100, loop=0)
print(f'Sandpile completed: {TOTAL_GRAINS} grains, {len(frames)} frames')

# Also save final state
img_array = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)
colors = [(245,245,250), (100,180,255), (30,120,220), (220,50,50)]
for c in range(4):
    mask = grid == c
    for ch in range(3):
        img_array[:,:,ch][mask] = colors[c][ch]
img_array = np.repeat(np.repeat(img_array, 4, axis=0), 4, axis=1)
img = Image.fromarray(img_array)
final_path = r'C:\Users\许耀仁\.openclaw\workspace\experiments\sandpile_final.png'
img.save(final_path)

# Analyze avalanche size distribution
sizes = np.array(avalanche_sizes)
print(f'Avalanche stats: mean={np.mean(sizes):.1f}, median={np.median(sizes):.1f}, max={np.max(sizes)}')
print(f'Large avalanches (>100): {np.sum(sizes > 100)}')
print(f'Small avalanches (0): {np.sum(sizes == 0)}')
