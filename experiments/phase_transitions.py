"""
Phase Transitions - Ising Model
"""

import numpy as np
from PIL import Image, ImageDraw
import random

def ising_step(grid, beta):
    SIZE = len(grid)
    x, y = random.randint(0, SIZE-1), random.randint(0, SIZE-1)
    neighbors = grid[(x-1)%SIZE][y] + grid[(x+1)%SIZE][y] + grid[x][(y-1)%SIZE] + grid[x][(y+1)%SIZE]
    delta_E = 2 * grid[x][y] * neighbors
    if delta_E < 0 or random.random() < np.exp(-beta * delta_E):
        grid[x][y] *= -1
    return grid

def run_ising(size=50, beta=0.44, steps=50000):
    grid = np.random.choice([-1, 1], size=(size, size))
    for _ in range(steps):
        ising_step(grid, beta)
    return grid

def visualize_ising(grid, path, label):
    SIZE = len(grid) * 4
    img = Image.new('RGB', (SIZE, SIZE), (15, 15, 25))
    scale = SIZE // len(grid)
    pixels = img.load()
    for i in range(len(grid)):
        for j in range(len(grid)):
            color = (255, 100, 100) if grid[i][j] > 0 else (50, 50, 150)
            for di in range(scale):
                for dj in range(scale):
                    pixels[i*scale+di, j*scale+dj] = color
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), label, fill=(255, 255, 255))
    img.save(path)
    print(f'Saved: {path}')

def visualize_phase_curve(path):
    SIZE = 800
    MARGIN = 80
    img = Image.new('RGB', (SIZE, SIZE), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    draw.line([MARGIN, MARGIN, MARGIN, SIZE-MARGIN], fill=(80,80,80), width=2)
    draw.line([MARGIN, SIZE-MARGIN, SIZE-MARGIN, SIZE-MARGIN], fill=(80,80,80), width=2)
    
    Tc = 2.269
    temps = np.linspace(0.1, 4.0, 100)
    mags = [(1 - (t/Tc)**2)**0.125 if t < Tc else 0 for t in temps]
    
    WIDTH = SIZE - 2*MARGIN
    HEIGHT = SIZE - 2*MARGIN
    
    for i in range(len(temps)-1):
        x1 = MARGIN + (temps[i]-0.1)/3.9*WIDTH
        y1 = SIZE-MARGIN - mags[i]*HEIGHT
        x2 = MARGIN + (temps[i+1]-0.1)/3.9*WIDTH
        y2 = SIZE-MARGIN - mags[i+1]*HEIGHT
        draw.line([x1,y1,x2,y2], fill=(100,255,150), width=3)
    
    x_tc = MARGIN + (Tc-0.1)/3.9*WIDTH
    draw.line([x_tc, MARGIN, x_tc, SIZE-MARGIN], fill=(255,100,100), width=1)
    draw.text((x_tc-10, SIZE-35), "Tc", fill=(255,100,100))
    
    draw.text((SIZE//2-30, 20), "Phase Transition", fill=(255,255,255))
    draw.text((MARGIN+20, MARGIN+40), "Ordered", fill=(100,255,150))
    draw.text((SIZE-MARGIN-80, MARGIN+40), "Disordered", fill=(150,150,150))
    
    img.save(path)
    print(f'Saved: {path}')

from pathlib import Path; output = str(Path(r'D:\emergence_experiments').resolve())
print('=== Phase Transitions ===')

for label, beta in [('T0.5', 2.0), ('T2.27', 0.44), ('T4.0', 0.25)]:
    grid = run_ising(size=50, beta=beta, steps=50000)
    visualize_ising(grid, f'{output}/ising_{label}.png', label)

visualize_phase_curve(f'{output}/phase_transition_curve.png')
print('Done')