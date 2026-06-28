"""
Lenia Parameter Space Search v2
Expanded search with stochastic updates and better scoring.

Changes from v1:
- Fixed imports (use lenia_jax.make_orbium, make_random_seed)
- Added stochastic update support (p_update parameter)
- Better scoring: survival × stability × (1+entropy) × diversity
- Larger search space with finer granularity
"""

import jax
import jax.numpy as jnp
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json, time
from lenia_jax import (
    make_kernel_fft, make_orbium, make_random_seed,
    run_lenia, _make_disk_kernel_np
)

# ============================================================================
# Scoring
# ============================================================================

def score_run(history, threshold=0.05):
    """Score a Lenia run by survival, stability, and diversity."""
    masses = np.array([h.sum() for h in history])
    
    # Survival rate
    survival = np.mean(masses > threshold)
    
    # Stability of final 20%
    n = len(masses)
    final_masses = masses[int(0.8*n):]
    if len(final_masses) > 0 and np.mean(final_masses) > 0:
        stability = 1 - np.var(final_masses) / (np.mean(final_masses)**2 + 1e-8)
        stability = max(0, min(1, stability))
    else:
        stability = 0
    
    # Entropy (structural complexity)
    final = history[-1]
    final_norm = final / (final.sum() + 1e-8)
    entropy = -np.sum(final_norm * np.log(final_norm + 1e-8))
    entropy_norm = entropy / np.log(len(final.ravel()))  # normalize
    
    # Diversity: variance across spatial regions
    h, w = final.shape
    regions = []
    for i in range(4):
        for j in range(4):
            region = final[i*h//4:(i+1)*h//4, j*w//4:(j+1)*w//4]
            regions.append(region.sum())
    diversity = np.std(regions) / (np.mean(regions) + 1e-8)
    
    score = survival * stability * (1 + entropy_norm) * (1 + diversity)
    
    return {
        'survival': float(survival),
        'stability': float(stability),
        'entropy': float(entropy_norm),
        'diversity': float(diversity),
        'final_mass': float(masses[-1]),
        'score': float(score)
    }


def run_single_param(R, mu, sigma, steps=300, size=128, seed_type='random', p_update=1.0):
    """Run Lenia with given parameters and return score."""
    np.random.seed(int(time.time() * 1000) % 2**31)
    
    if seed_type == 'orbium':
        grid = make_orbium((size, size), R)
    else:
        grid = make_random_seed((size, size), density=0.3)
    
    kernel_fft = make_kernel_fft((size, size), R)
    
    history = [np.array(grid)]
    grid_jax = jnp.array(grid)
    
    for step in range(steps):
        # Stochastic update mask
        if p_update < 1.0:
            mask = jnp.array(np.random.rand(size, size) < p_update, dtype=jnp.float32)
        else:
            mask = jnp.ones((size, size), dtype=jnp.float32)
        
        # Convolution
        grid_fft = jnp.fft.fft2(grid_jax)
        conv = jnp.fft.ifft2(grid_fft * kernel_fft).real
        
        # Growth function
        growth = jnp.exp(-((conv - mu) ** 2) / (2 * sigma ** 2)) * 2 - 1
        
        # Update with mask
        dt = 0.1
        new_grid = grid_jax + dt * growth
        new_grid = jnp.clip(new_grid, 0, 1)
        grid_jax = grid_jax * (1 - mask) + new_grid * mask
        
        if step % 50 == 0:
            history.append(np.array(grid_jax))
    
    history.append(np.array(grid_jax))
    return score_run(history)


# ============================================================================
# Parameter Sweep
# ============================================================================

def param_sweep(R_values, mu_values, sigma_values, steps=300, size=128, p_update=1.0):
    """Grid search over parameter space."""
    results = []
    total = len(R_values) * len(mu_values) * len(sigma_values)
    count = 0
    
    for R in R_values:
        for mu in mu_values:
            for sigma in sigma_values:
                count += 1
                if count % 20 == 0:
                    print(f"  [{count}/{total}] {100*count/total:.0f}%")
                
                score_random = run_single_param(R, mu, sigma, steps, size, 'random', p_update)
                score_orbium = run_single_param(R, mu, sigma, steps, size, 'orbium', p_update)
                
                results.append({
                    'R': int(R),
                    'mu': round(float(mu), 4),
                    'sigma': round(float(sigma), 4),
                    'p_update': p_update,
                    'random': score_random,
                    'orbium': score_orbium,
                    'combined_score': score_random['score'] + score_orbium['score']
                })
    
    results.sort(key=lambda x: x['combined_score'], reverse=True)
    return results


# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Lenia Parameter Space Search v2")
    print("=" * 60)
    
    output_dir = Path('output/lenia_search_v2')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    all_results = []
    
    # Search 1: Synchronous (p=1.0), fine grid
    print("\n[Search 1] Synchronous updates, fine grid")
    R_values = [10, 13, 15, 18, 20, 25]
    mu_values = np.linspace(0.08, 0.45, 10)
    sigma_values = np.linspace(0.01, 0.12, 8)
    
    print(f"  Grid: {len(R_values)}×{len(mu_values)}×{len(sigma_values)} = {len(R_values)*len(mu_values)*len(sigma_values)}")
    
    t0 = time.time()
    r1 = param_sweep(R_values, mu_values, sigma_values, steps=300, size=128, p_update=1.0)
    elapsed = time.time() - t0
    print(f"  Done in {elapsed:.0f}s, {len(r1)} results")
    all_results.extend(r1)
    
    # Search 2: Stochastic (p=0.5), key range
    print("\n[Search 2] Stochastic updates (p=0.5)")
    R_values = [13, 15, 18, 20]
    mu_values = np.linspace(0.1, 0.4, 7)
    sigma_values = np.linspace(0.02, 0.08, 5)
    
    print(f"  Grid: {len(R_values)}×{len(mu_values)}×{len(sigma_values)} = {len(R_values)*len(mu_values)*len(sigma_values)}")
    
    t0 = time.time()
    r2 = param_sweep(R_values, mu_values, sigma_values, steps=300, size=128, p_update=0.5)
    elapsed = time.time() - t0
    print(f"  Done in {elapsed:.0f}s, {len(r2)} results")
    all_results.extend(r2)
    
    # Sort all results
    all_results.sort(key=lambda x: x['combined_score'], reverse=True)
    
    # Save
    with open(output_dir / 'all_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Print top results
    print("\n" + "=" * 60)
    print("TOP 15 PARAMETER COMBINATIONS")
    print("=" * 60)
    for i, r in enumerate(all_results[:15], 1):
        print(f"{i:2d}. R={r['R']:2d} μ={r['mu']:.4f} σ={r['sigma']:.4f} p={r['p_update']:.1f} → {r['combined_score']:.4f}")
        print(f"    random: s={r['random']['survival']:.2f} st={r['random']['stability']:.2f} e={r['random']['entropy']:.2f} d={r['random']['diversity']:.2f}")
        print(f"    orbium: s={r['orbium']['survival']:.2f} st={r['orbium']['stability']:.2f} e={r['orbium']['entropy']:.2f} d={r['orbium']['diversity']:.2f}")
    
    # Summary stats
    sync = [r for r in all_results if r['p_update'] == 1.0]
    async_ = [r for r in all_results if r['p_update'] == 0.5]
    
    print(f"\n--- Summary ---")
    print(f"Synchronous:  {len(sync)} params, top score = {sync[0]['combined_score']:.4f}")
    print(f"Stochastic:   {len(async_)} params, top score = {async_[0]['combined_score']:.4f}")
    
    if async_[0]['combined_score'] > sync[0]['combined_score']:
        print("✓ Stochastic updates produce better results!")
    else:
        print("→ Synchronous updates still better for this range")
    
    print(f"\nResults saved to {output_dir}")
    print("Done!")
