"""
Lenia with Stochastic Updates (JAX-accelerated)

Key insight from experiments: Synchronous updates kill patterns,
but stochastic (asynchronous) updates allow survival.

This JAX version enables fast parameter sweeps to find optimal
update probabilities and test multiple seeds.

Inspired by Isotropic NCA's 50% stochastic update rate.
"""

import jax
import jax.numpy as jnp
from jax import jit
import numpy as np
from functools import partial
import matplotlib.pyplot as plt
from pathlib import Path
import time

# Import from lenia_jax
from lenia_jax import (
    _make_disk_kernel_np,
    _lenia_step,
    make_orbium,
    make_random_seed,
    make_kernel_fft,
    analyze_state
)


@partial(jit, static_argnums=(3, 4, 5, 6))
def _lenia_step_stochastic(grid, kernel_fft, key, mu, sigma, R, gn=0, update_prob=0.5):
    """Single Lenia step with stochastic updates.
    
    Instead of updating all cells, each cell updates with probability update_prob.
    This prevents oscillation and allows patterns to survive.
    """
    eps = 1e-8
    
    # Standard Lenia step
    grid_fft = jnp.fft.fft2(grid)
    conv_fft = grid_fft * kernel_fft
    potential = jnp.fft.ifft2(conv_fft).real
    
    # Growth function
    if gn == 0:
        growth = jnp.maximum(0, 1 - (potential - mu)**2 / (9 * sigma**2))**4 * 2 - 1
    elif gn == 1:
        growth = jnp.exp(-(potential - mu)**2 / (2 * sigma**2)) * 2 - 1
    else:
        growth = (jnp.abs(potential - mu) <= sigma) * 2 - 1
    
    new_grid = jnp.clip(grid + growth * 0.1, 0, 1)
    
    # Stochastic mask: each cell updates with probability update_prob
    update_mask = jax.random.uniform(key, grid.shape) < update_prob
    
    # Apply update only where mask is True
    result = jnp.where(update_mask, new_grid, grid)
    
    return result


def run_lenia_stochastic(grid, kernel_fft, key, steps, R, mu, sigma, gn=0, update_prob=0.5):
    """Run Lenia with stochastic updates for multiple steps."""
    
    @jit
    def step_fn(grid, key):
        new_grid = _lenia_step_stochastic(grid, kernel_fft, key, mu, sigma, R, gn, update_prob)
        return new_grid
    
    trajectory = []
    for i in range(steps):
        key, subkey = jax.random.split(key)
        grid = step_fn(grid, subkey)
        if i % 50 == 0:
            trajectory.append(np.array(grid))
    
    trajectory.append(np.array(grid))
    return grid, trajectory


def run_comparison_experiment(seed_type='orbium', R=13, mu=0.15, sigma=0.015, 
                               steps=200, update_probs=[1.0, 0.75, 0.5, 0.25]):
    """Compare synchronous vs stochastic Lenia."""
    
    print(f"Running stochastic Lenia comparison: {seed_type}, R={R}, steps={steps}")
    
    # Create seed
    grid_size = max(128, R * 8)
    if seed_type == 'orbium':
        seed = make_orbium((grid_size, grid_size), R)
    else:
        seed = make_random_seed((grid_size, grid_size), R)
    
    # Create kernel
    kernel_fft = make_kernel_fft(seed.shape, R)
    
    results = {}
    
    for p in update_probs:
        print(f"  update_prob={p:.2f}...", end='', flush=True)
        start = time.time()
        
        key = jax.random.PRNGKey(42)
        final, trajectory = run_lenia_stochastic(
            jnp.array(seed), kernel_fft, key, steps, R, mu, sigma, 
            update_prob=p
        )
        
        elapsed = time.time() - start
        
        # Compute alive ratio
        alive_ratio = float((final > 0.1).mean())
        results[p] = {
            'final': np.array(final),
            'trajectory': np.array(trajectory),
            'alive_ratio': alive_ratio,
            'time': elapsed
        }
        print(f" alive={alive_ratio:.3f}, time={elapsed:.2f}s")
    
    return results, seed


def visualize_comparison(results, seed, save_path=None):
    """Visualize comparison of different update probabilities."""
    n = len(results)
    fig, axes = plt.subplots(2, n, figsize=(3*n, 6))
    
    # Custom colormap
    colors = ['#000020', '#1a0a4a', '#4a1a8a', '#8a3aba', '#ba6aeb', '#ebabff']
    cmap = plt.cm.colors.LinearSegmentedColormap.from_list('lenia', colors)
    
    probs = sorted(results.keys())
    
    # Row 1: initial seed
    for i, p in enumerate(probs):
        ax = axes[0, i]
        ax.imshow(seed, cmap=cmap, vmin=0, vmax=1)
        ax.set_title(f'p={p:.2f}\nInitial', fontsize=10)
        ax.axis('off')
    
    # Row 2: final state
    for i, p in enumerate(probs):
        ax = axes[1, i]
        data = results[p]['final']
        alive = results[p]['alive_ratio']
        ax.imshow(data, cmap=cmap, vmin=0, vmax=1)
        status = 'ALIVE' if alive > 0.1 else 'DEAD'
        ax.set_title(f'Final (step 200)\nAlive: {alive:.1%} {status}', fontsize=10)
        ax.axis('off')
    
    plt.suptitle('Stochastic Lenia: Update Probability Comparison', fontsize=14)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    plt.close()
    return fig


def parameter_sweep(seed_type='orbium', R_values=[13, 15, 20], 
                    update_probs=np.linspace(0.1, 1.0, 10),
                    steps=200, mu=0.15, sigma=0.015):
    """Sweep R and update_prob to find optimal combinations."""
    
    print(f"Parameter sweep: R={R_values}, update_prob=[0.1, 1.0], steps={steps}")
    print()
    
    results = {}
    
    for R in R_values:
        print(f"=== R={R} ===")
        results[R] = {}
        
        # Create seed and kernel for this R
        grid_size = max(128, R * 8)
        if seed_type == 'orbium':
            seed = make_orbium((grid_size, grid_size), R)
        else:
            seed = make_random_seed((grid_size, grid_size), R)
        
        kernel_fft = make_kernel_fft(seed.shape, R)
        
        for p in update_probs:
            key = jax.random.PRNGKey(42)
            final, _ = run_lenia_stochastic(
                jnp.array(seed), kernel_fft, key, steps, R, mu, sigma,
                update_prob=p
            )
            alive = float((final > 0.1).mean())
            results[R][p] = alive
            print(f"  p={p:.2f}: alive={alive:.3f}")
    
    return results


def visualize_sweep(results, save_path=None):
    """Heatmap of survival vs R and update_prob."""
    R_values = sorted(results.keys())
    p_values = sorted(results[R_values[0]].keys())
    
    data = np.array([[results[R][p] for p in p_values] for R in R_values])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(data, aspect='auto', cmap='RdYlGn', vmin=0, vmax=0.5)
    
    ax.set_xlabel('Update Probability')
    ax.set_ylabel('R (kernel radius)')
    ax.set_xticks(range(len(p_values)))
    ax.set_xticklabels([f'{p:.2f}' for p in p_values])
    ax.set_yticks(range(len(R_values)))
    ax.set_yticklabels([str(R) for R in R_values])
    
    plt.colorbar(im, label='Alive Ratio')
    ax.set_title('Stochastic Lenia: Survival Heatmap\n(Green = Alive, Red = Dead)')
    
    # Add text annotations
    for i, R in enumerate(R_values):
        for j, p in enumerate(p_values):
            val = results[R][p]
            color = 'white' if val < 0.25 else 'black'
            ax.text(j, i, f'{val:.2f}', ha='center', va='center', 
                   color=color, fontsize=8)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    plt.close()
    return fig


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Stochastic Lenia (JAX)')
    parser.add_argument('--mode', choices=['compare', 'sweep'], default='compare')
    parser.add_argument('--seed', choices=['orbium', 'geminium', 'random'], default='orbium')
    parser.add_argument('--R', type=int, default=13)
    parser.add_argument('--steps', type=int, default=200)
    args = parser.parse_args()
    
    print("="*60)
    print("Stochastic Lenia (JAX-accelerated)")
    print("="*60)
    print()
    
    if args.mode == 'compare':
        results, seed = run_comparison_experiment(
            seed_type=args.seed, R=args.R, steps=args.steps
        )
        
        # Save visualization
        save_path = Path('experiments') / f'stochastic_lenia_R{args.R}.png'
        visualize_comparison(results, seed, save_path)
        
        # Summary
        print("\n=== Summary ===")
        for p, r in sorted(results.items()):
            status = 'ALIVE' if r['alive_ratio'] > 0.1 else 'DEAD'
            print(f"  p={p:.2f}: {r['alive_ratio']:.1%} {status}")
    
    elif args.mode == 'sweep':
        results = parameter_sweep(
            seed_type=args.seed,
            R_values=[13, 15, 17, 20],
            steps=args.steps
        )
        
        save_path = Path('experiments') / 'stochastic_lenia_sweep.png'
        visualize_sweep(results, save_path)


if __name__ == '__main__':
    main()
