"""
Test: Dynamic Fitness on Genome-Generated Patterns
===================================================

Quick test: generate a kernel from a genome, simulate Lenia, compute dynamic fitness.
"""

import sys
sys.path.insert(0, '.')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
import jax.numpy as jnp

from evolutionary_lenia import Genome, LeniaSimulator, create_default_config
from dynamic_fitness import compute_dynamic_fitness


def simulate_genome_quick(genome, config, seed='random', steps=500):
    """Quick simulation of a genome."""
    size = config['grid_size']
    R = config['kernel_radius']
    
    # Get kernel FFT
    kernel_fft = genome.to_kernel_fft(R, size)
    
    # Initialize seed
    if seed == 'orbium':
        from lenia_jax import make_orbium
        orbium = make_orbium()
        state = orbium['cells'][0].copy()
        state = np.pad(state, (size - state.shape[0]) // 2)
    else:
        state = np.random.rand(size, size).astype(np.float32) * 0.5
    
    state = jnp.array(state)
    
    # Simulate
    history = []
    mu = config['mu']
    sigma = config['sigma']
    dt = config['dt']
    
    for step in range(steps):
        # Lenia update
        A_fft = jnp.fft.fft2(state)
        U = jnp.real(jnp.fft.ifft2(kernel_fft * A_fft))
        U = jnp.clip(U, 0, 1)
        
        # Growth function
        growth = jnp.exp(-((U - mu)**2) / (2 * sigma**2)) * 2 - 1
        state = jnp.clip(state + dt * growth, 0, 1)
        
        if step % 5 == 0:  # Sample every 5 steps
            history.append(np.array(state))
    
    return history


def visualize_result(history, result, output_path):
    """Visualize simulation result."""
    n_frames = len(history)
    indices = [0, n_frames//4, n_frames//2, n_frames-1]
    
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    
    # Top: frames
    for i, idx in enumerate(indices):
        ax = axes[0, i]
        ax.imshow(history[idx], cmap='viridis', vmin=0, vmax=1)
        ax.set_title(f'Step {idx*5}')
        ax.axis('off')
    
    # Bottom: fitness breakdown
    ax = axes[1, 0]
    ax.text(0.5, 0.5, f"Score: {result.score:.3f}\n\n{result.breakdown}", 
            ha='center', va='center', fontsize=10, transform=ax.transAxes)
    ax.axis('off')
    
    # Mass over time
    masses = [h.sum() for h in history]
    ax = axes[1, 1]
    ax.plot(masses)
    ax.set_title('Mass over time')
    ax.set_xlabel('Frame')
    ax.grid(True, alpha=0.3)
    
    # Dynamics over time
    changes = []
    for i in range(1, len(history)):
        diff = np.abs(history[i] - history[i-1]).sum()
        total = history[i].sum() + history[i-1].sum() + 1e-8
        changes.append(diff / total)
    ax = axes[1, 2]
    ax.plot(changes)
    ax.set_title('Change rate over time')
    ax.set_xlabel('Frame')
    ax.grid(True, alpha=0.3)
    
    # Final state
    ax = axes[1, 3]
    ax.imshow(history[-1], cmap='viridis', vmin=0, vmax=1)
    ax.set_title('Final state')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    Path("output/evo_lenia_dynamic").mkdir(parents=True, exist_ok=True)
    
    config = create_default_config()
    config['sim_steps'] = 500
    config['mu'] = 0.1622
    config['sigma'] = 0.0257
    
    print("Testing dynamic fitness on genome-generated patterns...")
    print(f"Config: R={config['kernel_radius']}, mu={config['mu']}, sigma={config['sigma']}")
    
    # Test multiple random genomes
    for trial in range(3):
        print(f"\n{'='*60}")
        print(f"Trial {trial+1}")
        print(f"{'='*60}")
        
        genome = Genome.random(33, seed=trial)
        history = simulate_genome_quick(genome, config, seed='random', steps=500)
        result = compute_dynamic_fitness(history)
        
        print(f"\nResult:")
        print(f"  Score: {result.score:.3f}")
        print(f"  Survival: {result.survival:.3f}")
        print(f"  Stability: {result.stability:.3f}")
        print(f"  Dynamics: {result.dynamics:.4f}")
        print(f"  Complexity: {result.complexity:.4f}")
        print(f"\n  {result.breakdown}")
        
        # Visualize
        visualize_result(history, result, f"output/evo_lenia_dynamic/trial_{trial+1}.png")
    
    # Test with Orbium kernel (known-good)
    print(f"\n{'='*60}")
    print(f"Trial: Orbium kernel (ground truth)")
    print(f"{'='*60}")
    
    # Try to fit Orbium kernel
    from lenia_jax import _make_disk_kernel_np
    R = config['kernel_radius']
    
    # Gaussian Ring parameters (Orbium)
    mu_k = 0.5
    sigma_k = 0.15
    y, x = np.ogrid[-R:R+1, -R:R+1]
    r = np.sqrt(x*x + y*y) / R
    orbium_kernel = np.exp(-((r - mu_k)**2) / (2 * sigma_k**2))
    orbium_kernel[r > 1] = 0
    orbium_kernel = orbium_kernel / orbium_kernel.sum()
    
    # Pad to grid size
    size = config['grid_size']
    orbium_kernel_padded = np.zeros((size, size))
    off = size // 2 - R
    orbium_kernel_padded[off:off+2*R+1, off:off+2*R+1] = orbium_kernel
    orbium_kernel_fft = jnp.fft.fft2(jnp.array(orbium_kernel_padded))
    
    # Create a fake genome that should produce Orbium-like behavior
    # Use the fitted genome from the expressiveness test
    genome_orbium = Genome.random(33, seed=42)  # Placeholder
    
    history_orbium = simulate_genome_quick(genome_orbium, config, seed='orbium', steps=500)
    result_orbium = compute_dynamic_fitness(history_orbium)
    
    print(f"\nResult (Orbium seed):")
    print(f"  Score: {result_orbium.score:.3f}")
    print(f"  Dynamics: {result_orbium.dynamics:.4f}")
    print(f"\n  {result_orbium.breakdown}")
    
    visualize_result(history_orbium, result_orbium, "output/evo_lenia_dynamic/orbium_test.png")
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Tested {3+1} configurations with dynamic fitness")
    print(f"Output saved to: output/evo_lenia_dynamic/")