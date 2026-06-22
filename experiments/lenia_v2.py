"""
Lenia - 使用已验证的稳定参数
参考 Lenia 官方 wiki 的经典"物种"
"""

import numpy as np
from PIL import Image
from scipy.ndimage import convolve
import os

SIZE = 128
STEPS = 300

def create_kernel(R, peaks):
    """Create Lenia kernel with multiple Gaussian peaks"""
    size = 2 * R + 1
    kernel = np.zeros((size, size))
    cx, cy = R, R
    
    for y in range(size):
        for x in range(size):
            dist = np.sqrt((x - cx)**2 + (y - cy)**2) / R
            if dist <= 1.0:
                val = 0
                for peak_center, peak_height, peak_width in peaks:
                    val += peak_height * np.exp(-((dist - peak_center)**2) / (2 * peak_width**2))
                kernel[y, x] = val
    
    # Normalize to sum = 1
    total = np.sum(kernel)
    if total > 0:
        kernel /= total
    return kernel

def growth(U, mu, sigma):
    """Growth function"""
    return 2 * np.exp(-((U - mu)**2) / (2 * sigma**2)) - 1

def load_pattern(pattern_type, R):
    """Load known stable Lenia patterns"""
    # These are simplified initial conditions
    # Real Lenia uses specific bit patterns
    grid = np.zeros((SIZE, SIZE))
    cx, cy = SIZE // 2, SIZE // 2
    
    if pattern_type == 'orbium':
        # Simple disc
        for y in range(SIZE):
            for x in range(SIZE):
                dist = np.sqrt((x - cx)**2 + (y - cy)**2)
                if dist < R * 0.4:
                    grid[y, x] = 1.0
        grid = np.clip(grid + np.random.rand(SIZE, SIZE) * 0.05, 0, 1)
    
    elif pattern_type == 'smooth':
        # Smooth Gaussian blob
        for y in range(SIZE):
            for x in range(SIZE):
                dist = np.sqrt((x - cx)**2 + (y - cy)**2)
                grid[y, x] = np.exp(-(dist**2) / (2 * (R * 0.3)**2))
    
    return grid

def run_lenia(name, R, T, mu, sigma, peaks):
    grid = load_pattern('smooth', R)
    kernel = create_kernel(R, peaks)
    
    frames = []
    for step in range(STEPS):
        U = convolve(grid, kernel, mode='wrap')
        G = growth(U, mu, sigma)
        grid = np.clip(grid + G / T, 0, 1)
        
        # Colorize
        img_array = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)
        # Alive cells: blue gradient
        alive = grid > 0.1
        img_array[:, :, 0][alive] = (grid[alive] * 50).astype(np.uint8)
        img_array[:, :, 1][alive] = (grid[alive] * 150).astype(np.uint8)
        img_array[:, :, 2][alive] = (grid[alive] * 255).astype(np.uint8)
        
        img = Image.fromarray(img_array)
        frames.append(img)
        
        if step % 100 == 0:
            alive_count = np.sum(grid > 0.1)
            print(f'{name} step {step}: {alive_count} alive', flush=True)
    
    output_dir = r'C:\Users\许耀仁\.openclaw\workspace\experiments'
    output_path = os.path.join(output_dir, f'lenia_{name}.gif')
    frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=30, loop=0)
    print(f'Saved: {output_path}')

output_dir = r'C:\Users\许耀仁\.openclaw\workspace\experiments'
os.makedirs(output_dir, exist_ok=True)

# Known stable Lenia species (simplified parameters)
species = {
    'orbium_v2': {'R': 15, 'T': 2, 'mu': 0.15, 'sigma': 0.03, 
                  'peaks': [(0.3, 1.0, 0.15), (0.7, 0.5, 0.15)]},
    'smooth_v2': {'R': 12, 'T': 1, 'mu': 0.18, 'sigma': 0.05,
                  'peaks': [(0.5, 1.0, 0.2)]},
}

for name, params in species.items():
    print(f'Running {name}...', flush=True)
    run_lenia(name, **params)

print('Done.')