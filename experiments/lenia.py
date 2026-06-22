"""
Lenia - Continuous Cellular Automata
Conway's Game of Life 的连续版本

使用模糊核（Gaussian kernel）代替离散规则，
产生类似生物的连续形态：脉动、分裂、游动

参考：https://github.com/Chakazul/Lenia
"""

import numpy as np
from PIL import Image
from scipy.ndimage import convolve
import os

SIZE = 128
STEPS = 200

# Lenia parameters
R = 13  # Kernel radius
MU = 0.15  # Growth function center
SIGMA = 0.015  # Growth function width

# Different parameter sets produce different "creatures"
configs = {
    'orbium': {'R': 13, 'T': 10, 'mu': 0.15, 'sigma': 0.015, 'b': 1.0, 'm': 0.5, 's': 0.014},
    'geminium': {'R': 12, 'T': 10, 'mu': 0.14, 'sigma': 0.014, 'b': 0.5, 'm': 0.39, 's': 0.025},
}

def gaussian_kernel(R, b=1.0, m=0.5, s=0.014):
    """Generate Lenia kernel with Gaussian rings"""
    size = 2 * R + 1
    kernel = np.zeros((size, size))
    cx, cy = R, R
    
    for y in range(size):
        for x in range(size):
            dist = np.sqrt((x - cx)**2 + (y - cy)**2) / R
            if dist <= 1.0:
                # Multiple Gaussian rings
                kernel[y, x] = np.exp(-((dist - m)**2) / (2 * s**2)) * b
    
    # Normalize
    kernel = kernel / np.sum(kernel)
    return kernel

def growth_function(U, mu, sigma):
    """Smooth growth function instead of discrete rules"""
    return 2 * np.exp(-((U - mu)**2) / (2 * sigma**2)) - 1

def run_lenia(config, name):
    R = config['R']
    T = config['T']
    mu = config['mu']
    sigma = config['sigma']
    b = config['b']
    m = config['m']
    s = config['s']
    
    # Initialize with a simple shape
    grid = np.zeros((SIZE, SIZE))
    
    # Create initial "creature" shape
    cx, cy = SIZE // 2, SIZE // 2
    for y in range(SIZE):
        for x in range(SIZE):
            dist = np.sqrt((x - cx)**2 + (y - cy)**2)
            if dist < R * 0.5:
                grid[y, x] = np.exp(-((dist / R - 0.3)**2) / 0.05)
    
    grid = np.clip(grid, 0, 1)
    
    # Generate kernel
    kernel = gaussian_kernel(R, b, m, s)
    
    frames = []
    for step in range(STEPS):
        # Convolve with kernel
        U = convolve(grid, kernel, mode='wrap')
        
        # Apply growth function
        G = growth_function(U, mu, sigma)
        
        # Update grid
        dt = 1.0 / T
        grid = np.clip(grid + dt * G, 0, 1)
        
        # Create frame
        img_array = (grid * 255).astype(np.uint8)
        img = Image.fromarray(img_array, mode='L')
        frames.append(img)
        
        if step % 50 == 0:
            alive = np.sum(grid > 0.1)
            print(f'{name} step {step}: alive cells ~ {alive}', flush=True)
    
    # Save GIF
        output_dir = r'D:\emergence_experiments'
    output_path = os.path.join(output_dir, f'lenia_{name}.gif')
    frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=30, loop=0)
    print(f'{name} saved to: {output_path}')
    
    # Save final frame as PNG
    final_path = os.path.join(output_dir, f'lenia_{name}_final.png')
    frames[-1].save(final_path)

output_dir = r'D:\emergence_experiments'
os.makedirs(output_dir, exist_ok=True)

for name, config in configs.items():
    print(f'Running Lenia {name}...', flush=True)
    run_lenia(config, name)

print('Lenia experiments completed.')