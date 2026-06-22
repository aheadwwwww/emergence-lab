"""
Turing Patterns / Reaction-Diffusion
Gray-Scott model

两个化学物质 U 和 V 的反应扩散：
dU/dt = Du * laplacian(U) - U*V^2 + F*(1-U)
dV/dt = Dv * laplacian(V) + U*V^2 - (F+K)*V

参数 F（feed rate）和 K（kill rate）决定产生的图案类型
"""

import numpy as np
from PIL import Image
import os

SIZE = 200
STEPS = 5000
Du = 0.16    # Diffusion rate of U
Dv = 0.08    # Diffusion rate of V

# Different parameter sets produce different patterns
configs = {
    'spots': (0.035, 0.065),      # F, K - spots
    'stripes': (0.04, 0.06),      # stripes
    'coral': (0.055, 0.062),      # coral/maze
    'mitosis': (0.0367, 0.0649),  # mitosis (dividing spots)
}

def laplacian(grid):
    return (np.roll(grid, 1, axis=0) + np.roll(grid, -1, axis=0) +
            np.roll(grid, 1, axis=1) + np.roll(grid, -1, axis=1) - 4 * grid)

def run_gray_scott(F, K, name):
    # Initialize: U=1 everywhere, V=0 everywhere, seed V in center
    U = np.ones((SIZE, SIZE))
    V = np.zeros((SIZE, SIZE))
    
    # Seed: add V in several random spots
    np.random.seed(42)
    for _ in range(20):
        cx, cy = np.random.randint(20, SIZE-20, 2)
        r = 3
        U[cx-r:cx+r, cy-r:cy+r] = 0.50
        V[cx-r:cx+r, cy-r:cy+r] = 0.25
    
    # Add some noise
    U += 0.02 * np.random.rand(SIZE, SIZE)
    V += 0.02 * np.random.rand(SIZE, SIZE)
    
    dt = 1.0
    for step in range(STEPS):
        lu = laplacian(U)
        lv = laplacian(V)
        
        uvv = U * V * V
        U += dt * (Du * lu - uvv + F * (1 - U))
        V += dt * (Dv * lv + uvv - (F + K) * V)
        
        # Clamp
        U = np.clip(U, 0, 1)
        V = np.clip(V, 0, 1)
    
    # Create image from V concentration
    img_array = (V * 255).astype(np.uint8)
    img = Image.fromarray(img_array, mode='L')
    
    output_dir = r'C:\Users\许耀仁\.openclaw\workspace\experiments'
    output_path = os.path.join(output_dir, f'turing_{name}.png')
    img.save(output_path)
    print(f'{name} (F={F}, K={K}): saved to {output_path}')
    return output_path

output_dir = r'C:\Users\许耀仁\.openclaw\workspace\experiments'
os.makedirs(output_dir, exist_ok=True)

for name, (F, K) in configs.items():
    print(f'Running {name}...', flush=True)
    run_gray_scott(F, K, name)

print('All Turing pattern experiments completed.')
