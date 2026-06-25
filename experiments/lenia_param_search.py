"""
Lenia Parameter Space Search
Systematic exploration of (R, μ, σ) to find stable life forms.

Strategy:
1. Grid search over R × μ × σ
2. For each parameter, run from random seed + Orbium seed
3. Score by survival rate, structure count, and stability
4. Output top candidates for further study
"""

import jax
import jax.numpy as jnp
from jax import jit
import numpy as np
from functools import partial
import matplotlib.pyplot as plt
from pathlib import Path
import json, time
from concurrent.futures import ThreadPoolExecutor

# Import from lenia_jax
from lenia_jax import _make_disk_kernel_np, _lenia_step, create_orbium_seed

# ============================================================================
# Parameter Search
# ============================================================================

def score_run(history, threshold=0.1):
    """Score a Lenia run by survival and stability.
    
    Metrics:
    - survival_rate: fraction of steps with mass > threshold
    - stability: 1 - variance(final_mass) / mean(final_mass)
    - structure: entropy of final state (higher = more structures)
    """
    masses = [h.sum() for h in history]
    
    # Survival rate
    survival = sum(m > threshold for m in masses) / len(masses)
    
    # Stability (last 20%)
    n = len(masses)
    final_masses = masses[int(0.8*n):]
    if len(final_masses) > 0 and np.mean(final_masses) > 0:
        stability = 1 - np.var(final_masses) / (np.mean(final_masses)**2 + 1e-8)
        stability = max(0, stability)
    else:
        stability = 0
    
    # Structure (entropy of final state)
    final = history[-1]
    final_norm = final / (final.sum() + 1e-8)
    entropy = -np.sum(final_norm * np.log(final_norm + 1e-8))
    
    return {
        'survival': float(survival),
        'stability': float(stability),
        'entropy': float(entropy),
        'final_mass': float(masses[-1]),
        'score': float(survival * stability * (1 + entropy))
    }


def run_single_param(R, mu, sigma, steps=500, size=128, seed_type='random'):
    """Run Lenia with given parameters and return score."""
    # Initialize grid
    if seed_type == 'orbium':
        grid = create_orbium_seed(size, R)
    else:
        np.random.seed(int(time.time() * 1000) % 2**31)
        grid = np.random.rand(size, size).astype(np.float32) * 0.5
    
    # Create kernel
    kernel = _make_disk_kernel_np(R)
    kernel_fft = jnp.fft.fft2(kernel, s=(size, size))
    
    # Run simulation
    history = [grid.copy()]
    grid_jax = jnp.array(grid)
    
    for _ in range(steps):
        grid_jax = _lenia_step(grid_jax, kernel_fft, mu, sigma, R)
        grid = np.array(grid_jax)
        history.append(grid.copy())
    
    return score_run(history)


def param_sweep(R_values, mu_values, sigma_values, steps=300, size=128):
    """Grid search over parameter space."""
    results = []
    total = len(R_values) * len(mu_values) * len(sigma_values)
    count = 0
    
    for R in R_values:
        for mu in mu_values:
            for sigma in sigma_values:
                count += 1
                if count % 10 == 0:
                    print(f"Progress: {count}/{total} ({100*count/total:.1f}%)")
                
                # Run both random and orbium seeds
                score_random = run_single_param(R, mu, sigma, steps, size, 'random')
                score_orbium = run_single_param(R, mu, sigma, steps, size, 'orbium')
                
                results.append({
                    'R': int(R),
                    'mu': float(mu),
                    'sigma': float(sigma),
                    'random': score_random,
                    'orbium': score_orbium,
                    'combined_score': score_random['score'] + score_orbium['score']
                })
    
    # Sort by combined score
    results.sort(key=lambda x: x['combined_score'], reverse=True)
    return results


# ============================================================================
# Visualization
# ============================================================================

def plot_top_results(results, top_n=9, save_path='lenia_param_search.png'):
    """Visualize top parameter combinations."""
    top = results[:top_n]
    
    fig, axes = plt.subplots(3, 3, figsize=(15, 15))
    axes = axes.flatten()
    
    for i, ax in enumerate(axes):
        if i >= len(top):
            ax.axis('off')
            continue
        
        r = top[i]
        ax.text(0.5, 0.7, f"R={r['R']}, μ={r['mu']:.3f}, σ={r['sigma']:.3f}",
                ha='center', fontsize=12, transform=ax.transAxes)
        ax.text(0.5, 0.5, f"Score: {r['combined_score']:.3f}",
                ha='center', fontsize=10, transform=ax.transAxes)
        ax.text(0.5, 0.3, f"Survival: {r['random']['survival']:.2f} / {r['orbium']['survival']:.2f}",
                ha='center', fontsize=10, transform=ax.transAxes)
        ax.axis('off')
    
    plt.suptitle('Top Lenia Parameter Combinations', fontsize=16)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")


# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Lenia Parameter Space Search")
    print("=" * 60)
    
    # Parameter ranges
    R_values = [10, 13, 15, 18, 20]
    mu_values = np.linspace(0.1, 0.4, 7)  # 0.1, 0.15, ..., 0.4
    sigma_values = np.linspace(0.01, 0.1, 5)  # 0.01, 0.03, ..., 0.1
    
    print(f"\nSearch space: {len(R_values)} × {len(mu_values)} × {len(sigma_values)} = {len(R_values)*len(mu_values)*len(sigma_values)} combinations")
    print(f"R: {R_values}")
    print(f"μ: {list(mu_values)}")
    print(f"σ: {list(sigma_values)}")
    
    start_time = time.time()
    results = param_sweep(R_values, mu_values, sigma_values, steps=300, size=128)
    elapsed = time.time() - start_time
    
    print(f"\nCompleted in {elapsed:.1f}s")
    
    # Save results
    output_dir = Path('output/lenia_search')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / 'param_search_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nTop 10 results:")
    for i, r in enumerate(results[:10], 1):
        print(f"{i}. R={r['R']}, μ={r['mu']:.3f}, σ={r['sigma']:.3f} → score={r['combined_score']:.3f}")
    
    # Visualize
    plot_top_results(results, top_n=9, save_path=output_dir / 'top_params.png')
    
    print("\n✓ Parameter search complete!")
