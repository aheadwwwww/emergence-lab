"""
Quick follow-up with better parameters found in sweep:
R=9, mu=0.1822, sigma=0.0307 (top scoring)
"""

import sys
import os
sys.path.insert(0, 'D:/openclaw_workspace/experiments')

import jax
import jax.numpy as jnp
import numpy as np
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from lenia_jax import (
    make_kernel_fft, make_orbium,
    _lenia_step, analyze_state, classify_state
)

OUTPUT_DIR = Path('D:/openclaw_workspace/experiments/output/lenia_fine_search')

def make_cmap():
    colors = [
        (0.0, 0.0, 0.1), (0.0, 0.1, 0.3), (0.0, 0.4, 0.6),
        (0.1, 0.7, 0.5), (0.6, 0.9, 0.3), (1.0, 1.0, 0.0), (1.0, 1.0, 1.0),
    ]
    return LinearSegmentedColormap.from_list('lenia', colors)

def grid_to_image(grid, cmap=None):
    if cmap is None:
        cmap = make_cmap()
    normalized = np.clip(grid, 0, 1)
    rgba = cmap(normalized)
    rgb = (rgba[:, :, :3] * 255).astype(np.uint8)
    return Image.fromarray(rgb)

def create_gif(grids, output_path, fps=30):
    frames = [grid_to_image(g) for g in grids]
    size = frames[0].size
    if size[0] < 256:
        new_size = (256, 256)
        frames = [f.resize(new_size, Image.LANCZOS) for f in frames]
    frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=1000//fps, loop=0)
    print(f"[OK] GIF saved: {output_path}")

# Top parameters from sweep
TOP_PARAMS = [
    {'R': 8, 'mu': 0.1822, 'sigma': 0.0307},
    {'R': 9, 'mu': 0.1822, 'sigma': 0.0307},
    {'R': 10, 'mu': 0.1822, 'sigma': 0.0307},
]

print("=" * 60)
print("Follow-up: Long simulation with better parameters")
print("=" * 60)

size = 128
steps = 1000
record_every = 10

for idx, params in enumerate(TOP_PARAMS, 1):
    R = params['R']
    mu = params['mu']
    sigma = params['sigma']
    
    print(f"\n[Run {idx}] R={R}, mu={mu}, sigma={sigma}")
    
    grid = make_orbium((size, size), R, 'classic')
    grid = jnp.array(grid)
    kernel_fft = make_kernel_fft((size, size), R, kn=1)
    
    grids = [np.array(grid)]
    
    for step in range(steps):
        grid, _ = _lenia_step(grid, kernel_fft, mu, sigma, R, 1)
        if (step + 1) % record_every == 0:
            grids.append(np.array(grid))
    
    final_stats = analyze_state(grid)
    final_state = classify_state(final_stats)
    
    print(f"  Final: {final_state}, score={final_stats['score']:.4f}, alive={final_stats['alive']:.4f}")
    
    # Save GIF
    gif_path = OUTPUT_DIR / f'followup_R{R}_mu{mu:.4f}_sig{sigma:.4f}.gif'
    create_gif(grids, str(gif_path), fps=30)

# Also try with random seed for R=10, mu=0.1622, sigma=0.0257
print("\n[Random seed test] R=10, mu=0.1622, sigma=0.0257")
from lenia_jax import make_random_seed

R, mu, sigma = 10, 0.1622, 0.0257
grid = make_random_seed((size, size), density=0.3)
grid = jnp.array(grid)
kernel_fft = make_kernel_fft((size, size), R, kn=1)

grids = [np.array(grid)]
for step in range(steps):
    grid, _ = _lenia_step(grid, kernel_fft, mu, sigma, R, 1)
    if (step + 1) % record_every == 0:
        grids.append(np.array(grid))

final_stats = analyze_state(grid)
final_state = classify_state(final_stats)
print(f"  Final: {final_state}, score={final_stats['score']:.4f}, alive={final_stats['alive']:.4f}")

gif_path = OUTPUT_DIR / 'followup_R10_mu0.1622_random_seed.gif'
create_gif(grids, str(gif_path), fps=30)

print("\nDone!")
