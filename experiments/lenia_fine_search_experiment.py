"""
Lenia Fine Parameter Search Experiment
Based on best params from v2 search: R=10, mu=0.1622, sigma=0.0257

Experiments:
1. Long simulation (1000 steps) with best params → GIF
2. Fine-grained parameter sweep around R=10
3. Orbium seed comparison across R values
4. Results saved to experiments/output/lenia_fine_search/
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import jax
import jax.numpy as jnp
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path
import json, time
from PIL import Image

from lenia_jax import (
    make_kernel_fft, make_orbium, make_random_seed,
    run_lenia, _make_disk_kernel_np, _lenia_step, analyze_state, classify_state
)

# ============================================================================
# Configuration
# ============================================================================

OUTPUT_DIR = Path('D:/openclaw_workspace/experiments/output/lenia_fine_search')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Best params from v2 search
BEST_R = 10
BEST_MU = 0.1622
BEST_SIGMA = 0.0257

# ============================================================================
# Visualization
# ============================================================================

def make_cmap():
    """Custom colormap for Lenia."""
    colors = [
        (0.0, 0.0, 0.1),
        (0.0, 0.1, 0.3),
        (0.0, 0.4, 0.6),
        (0.1, 0.7, 0.5),
        (0.6, 0.9, 0.3),
        (1.0, 1.0, 0.0),
        (1.0, 1.0, 1.0),
    ]
    return LinearSegmentedColormap.from_list('lenia', colors)


def grid_to_image(grid, cmap=None):
    """Convert grid to PIL Image."""
    if cmap is None:
        cmap = make_cmap()
    
    # Normalize and apply colormap
    normalized = np.clip(grid, 0, 1)
    rgba = cmap(normalized)
    rgb = (rgba[:, :, :3] * 255).astype(np.uint8)
    return Image.fromarray(rgb)


def create_gif(grids, output_path, fps=20):
    """Create GIF from grid sequence."""
    frames = [grid_to_image(g) for g in grids]
    
    # Resize for better visibility
    size = frames[0].size
    if size[0] < 256:
        new_size = (256, 256)
        frames = [f.resize(new_size, Image.LANCZOS) for f in frames]
    
    # Save as GIF
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=1000 // fps,
        loop=0
    )
    print(f"[OK] GIF saved: {output_path}")
    return output_path


def create_timeline_image(grids, output_path, title=""):
    """Create timeline image from grid sequence."""
    n = len(grids)
    cols = min(n, 5)
    rows = (n + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 3, rows * 3.2))
    if rows == 1 and cols == 1:
        axes = [[axes]]
    elif rows == 1:
        axes = [axes]
    elif cols == 1:
        axes = [[ax] for ax in axes]
    
    cmap = make_cmap()
    
    for i in range(rows * cols):
        r, c = i // cols, i % cols
        ax = axes[r][c]
        
        if i < n:
            im = ax.imshow(np.array(grids[i]), cmap=cmap, vmin=0, vmax=1, interpolation='bilinear')
            ax.set_title(f'step={i * (1000 // (n-1)) if i > 0 else 0}', fontsize=9)
        ax.axis('off')
    
    if title:
        fig.suptitle(title, fontsize=11, color='white')
    
    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='black')
    plt.close(fig)
    print(f"[OK] Timeline saved: {output_path}")
    return output_path


# ============================================================================
# Experiment 1: Long Simulation with Best Params
# ============================================================================

def experiment_1_long_simulation():
    """Run 1000-step simulation with best parameters."""
    print("\n" + "=" * 60)
    print("Experiment 1: Long Simulation (1000 steps)")
    print(f"Best params: R={BEST_R}, mu={BEST_MU}, sigma={BEST_SIGMA}")
    print("=" * 60)
    
    size = 128
    shape = (size, size)
    steps = 1000
    record_every = 10  # Record every 10 steps for smooth GIF
    
    # Initialize with Orbium seed
    grid = make_orbium(shape, BEST_R, 'classic')
    grid = jnp.array(grid)
    
    # Prepare kernel
    kernel_fft = make_kernel_fft(shape, BEST_R, kn=1)  # kn=1 = bump4
    
    # Run simulation
    grids = [np.array(grid)]
    t0 = time.time()
    
    for step in range(steps):
        grid, potential = _lenia_step(grid, kernel_fft, BEST_MU, BEST_SIGMA, BEST_R, 1)
        
        if (step + 1) % record_every == 0:
            grids.append(np.array(grid))
        
        if (step + 1) % 200 == 0:
            stats = analyze_state(grid)
            elapsed = time.time() - t0
            print(f"  step {step+1}/{steps} | alive={stats['alive']:.3f} score={stats['score']:.3f} | {elapsed:.1f}s")
    
    elapsed = time.time() - t0
    final_stats = analyze_state(grid)
    final_state = classify_state(final_stats)
    
    print(f"\n  Done in {elapsed:.1f}s")
    print(f"  Final state: {final_state}")
    print(f"  Stats: alive={final_stats['alive']:.4f}, entropy={final_stats['entropy']:.4f}, score={final_stats['score']:.4f}")
    
    # Create GIF
    gif_path = OUTPUT_DIR / 'exp1_long_simulation.gif'
    create_gif(grids, str(gif_path), fps=30)
    
    # Create timeline
    timeline_path = OUTPUT_DIR / 'exp1_long_timeline.png'
    sampled = grids[::10]  # Sample every 10th recorded frame
    create_timeline_image(sampled[:10], str(timeline_path), 
                          f"Best params: R={BEST_R}, μ={BEST_MU}, σ={BEST_SIGMA}")
    
    # Save final state
    final_path = OUTPUT_DIR / 'exp1_final_state.png'
    grid_to_image(grids[-1]).save(final_path)
    
    # Save results
    result = {
        'experiment': 'long_simulation',
        'params': {'R': BEST_R, 'mu': BEST_MU, 'sigma': BEST_SIGMA},
        'steps': steps,
        'final_stats': final_stats,
        'final_state': final_state,
        'time': round(elapsed, 2),
        'frames_recorded': len(grids),
    }
    
    with open(OUTPUT_DIR / 'exp1_results.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    return result


# ============================================================================
# Experiment 2: Fine-grained Parameter Sweep
# ============================================================================

def experiment_2_fine_sweep():
    """Sweep around best params: R in [8,9,10,11,12], mu±0.02, sigma±0.01."""
    print("\n" + "=" * 60)
    print("Experiment 2: Fine-grained Parameter Sweep")
    print("R ∈ [8, 9, 10, 11, 12]")
    print(f"mu ∈ [{BEST_MU-0.02:.4f}, {BEST_MU+0.02:.4f}]")
    print(f"sigma ∈ [{BEST_SIGMA-0.01:.4f}, {BEST_SIGMA+0.01:.4f}]")
    print("=" * 60)
    
    R_values = [8, 9, 10, 11, 12]
    mu_values = np.linspace(BEST_MU - 0.02, BEST_MU + 0.02, 5)
    sigma_values = np.linspace(max(0.01, BEST_SIGMA - 0.01), BEST_SIGMA + 0.01, 5)
    
    size = 128
    shape = (size, size)
    steps = 300
    
    results = []
    all_grids = {}
    
    total = len(R_values) * len(mu_values) * len(sigma_values)
    count = 0
    t0 = time.time()
    
    for R in R_values:
        for mu in mu_values:
            for sigma in sigma_values:
                count += 1
                mu_r = round(float(mu), 4)
                sigma_r = round(float(sigma), 4)
                
                # Run with Orbium seed
                grid = make_orbium(shape, R, 'classic')
                grid = jnp.array(grid)
                kernel_fft = make_kernel_fft(shape, R, kn=1)
                
                history = [np.array(grid)]
                for step in range(steps):
                    grid, _ = _lenia_step(grid, kernel_fft, mu_r, sigma_r, R, 1)
                    if step % 100 == 0:
                        history.append(np.array(grid))
                history.append(np.array(grid))
                
                # Analyze
                stats = analyze_state(grid)
                state = classify_state(stats)
                
                result = {
                    'R': R,
                    'mu': mu_r,
                    'sigma': sigma_r,
                    'stats': stats,
                    'state': state,
                }
                results.append(result)
                
                # Store final state for visualization
                key = f"R{R}_mu{mu_r:.4f}_sig{sigma_r:.4f}"
                all_grids[key] = {
                    'final': np.array(grid),
                    'history': history,
                    'params': {'R': R, 'mu': mu_r, 'sigma': sigma_r},
                }
                
                if count % 25 == 0:
                    elapsed = time.time() - t0
                    print(f"  [{count}/{total}] {100*count/total:.0f}% | {elapsed:.0f}s")
    
    elapsed = time.time() - t0
    print(f"\n  Done in {elapsed:.1f}s")
    
    # Sort by score
    results.sort(key=lambda x: x['stats']['score'], reverse=True)
    
    # Print top 10
    print("\n  Top 10 parameter combinations:")
    for i, r in enumerate(results[:10], 1):
        print(f"    {i:2d}. R={r['R']:2d} μ={r['mu']:.4f} σ={r['sigma']:.4f} "
              f"→ score={r['stats']['score']:.4f} [{r['state']}]")
    
    # Create parameter landscape visualization
    create_sweep_visualization(results, R_values, mu_values, sigma_values)
    
    # Save results
    with open(OUTPUT_DIR / 'exp2_sweep_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results, all_grids


def create_sweep_visualization(results, R_values, mu_values, sigma_values):
    """Create visualization of parameter sweep results."""
    
    # Create per-R summary plots
    fig, axes = plt.subplots(1, len(R_values), figsize=(4 * len(R_values), 4))
    if len(R_values) == 1:
        axes = [axes]
    
    cmap = make_cmap()
    
    for idx, R in enumerate(R_values):
        ax = axes[idx]
        
        # Get results for this R
        r_results = [r for r in results if r['R'] == R]
        if not r_results:
            continue
        
        # Create 2D grid for mu x sigma
        mu_list = sorted(set(r['mu'] for r in r_results))
        sigma_list = sorted(set(r['sigma'] for r in r_results))
        
        score_grid = np.zeros((len(sigma_list), len(mu_list)))
        state_grid = np.zeros((len(sigma_list), len(mu_list)), dtype=int)
        
        for r in r_results:
            i = sigma_list.index(r['sigma'])
            j = mu_list.index(r['mu'])
            score_grid[i, j] = r['stats']['score']
            state_grid[i, j] = {'dead': 0, 'simple': 1, 'structure': 2, 'saturated': 3}.get(r['state'], 0)
        
        # Plot
        im = ax.imshow(score_grid, cmap='viridis', aspect='auto',
                       extent=[mu_list[0], mu_list[-1], sigma_list[-1], sigma_list[0]])
        ax.set_xlabel('μ', fontsize=10)
        ax.set_ylabel('σ', fontsize=10)
        ax.set_title(f'R={R}', fontsize=11)
        
        # Add contour for state boundaries
        ax.contour(score_grid, levels=[0.3, 0.5, 0.7], colors='white', 
                   linewidths=0.5, extent=[mu_list[0], mu_list[-1], sigma_list[0], sigma_list[-1]])
        
        plt.colorbar(im, ax=ax, label='Score', shrink=0.8)
    
    fig.suptitle('Fine-grained Parameter Sweep: Score Landscape', fontsize=12)
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / 'exp2_parameter_landscape.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"[OK] Parameter landscape saved")
    
    # Create grid of final states
    best_per_R = {}
    for r in results:
        if r['R'] not in best_per_R or r['stats']['score'] > best_per_R[r['R']]['stats']['score']:
            best_per_R[r['R']] = r
    
    # Load final states for best params
    fig, axes = plt.subplots(1, len(R_values), figsize=(3 * len(R_values), 3.5))
    if len(R_values) == 1:
        axes = [axes]
    
    for idx, R in enumerate(R_values):
        ax = axes[idx]
        # Find best result for this R
        best = best_per_R.get(R)
        if best:
            # Re-run to get final state
            grid = make_orbium((128, 128), R, 'classic')
            grid = jnp.array(grid)
            kernel_fft = make_kernel_fft((128, 128), R, kn=1)
            for _ in range(300):
                grid, _ = _lenia_step(grid, kernel_fft, best['mu'], best['sigma'], R, 1)
            
            ax.imshow(np.array(grid), cmap=cmap, vmin=0, vmax=1)
            ax.set_title(f"R={R}\nμ={best['mu']:.3f} σ={best['sigma']:.3f}\nscore={best['stats']['score']:.3f}", 
                        fontsize=9)
        ax.axis('off')
    
    fig.suptitle('Best Pattern per R Value', fontsize=12)
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / 'exp2_best_per_R.png', dpi=150, bbox_inches='tight', facecolor='black')
    plt.close(fig)
    print(f"[OK] Best per R saved")


# ============================================================================
# Experiment 3: Orbium Seed Comparison Across R Values
# ============================================================================

def experiment_3_orbium_comparison():
    """Compare Orbium seed behavior across different R values."""
    print("\n" + "=" * 60)
    print("Experiment 3: Orbium Seed Comparison Across R Values")
    print("R ∈ [8, 9, 10, 11, 12] with best (mu, sigma) params")
    print("=" * 60)
    
    R_values = [8, 9, 10, 11, 12]
    size = 128
    shape = (size, size)
    steps = 500
    record_every = 50
    
    results = {}
    all_timelines = {}
    
    t0 = time.time()
    
    for R in R_values:
        print(f"\n  Running R={R}...")
        
        # Use best params, scaled appropriately for R
        # Scale mu and sigma slightly based on R
        mu = BEST_MU
        sigma = BEST_SIGMA
        
        grid = make_orbium(shape, R, 'classic')
        grid = jnp.array(grid)
        kernel_fft = make_kernel_fft(shape, R, kn=1)
        
        timeline = [np.array(grid)]
        stats_history = []
        
        for step in range(steps):
            grid, _ = _lenia_step(grid, kernel_fft, mu, sigma, R, 1)
            
            if (step + 1) % record_every == 0:
                timeline.append(np.array(grid))
                stats = analyze_state(grid)
                stats_history.append(stats)
        
        final_stats = analyze_state(grid)
        final_state = classify_state(final_stats)
        
        results[R] = {
            'params': {'R': R, 'mu': mu, 'sigma': sigma},
            'final_stats': final_stats,
            'final_state': final_state,
            'stats_history': stats_history,
        }
        all_timelines[R] = timeline
        
        print(f"    → {final_state}, score={final_stats['score']:.4f}, alive={final_stats['alive']:.4f}")
    
    elapsed = time.time() - t0
    print(f"\n  Done in {elapsed:.1f}s")
    
    # Create comparison visualization
    create_orbium_comparison_viz(results, all_timelines, R_values)
    
    # Save results
    serializable = {}
    for R, r in results.items():
        serializable[str(R)] = {
            'params': r['params'],
            'final_stats': r['final_stats'],
            'final_state': r['final_state'],
        }
    
    with open(OUTPUT_DIR / 'exp3_orbium_comparison.json', 'w') as f:
        json.dump(serializable, f, indent=2)
    
    return results, all_timelines


def create_orbium_comparison_viz(results, all_timelines, R_values):
    """Create visualization comparing Orbium across R values."""
    cmap = make_cmap()
    
    # Create timeline comparison
    n_steps = len(next(iter(all_timelines.values())))
    n_R = len(R_values)
    
    fig, axes = plt.subplots(n_R, n_steps, figsize=(n_steps * 2.5, n_R * 2.5))
    
    for i, R in enumerate(R_values):
        timeline = all_timelines[R]
        for j in range(n_steps):
            ax = axes[i, j] if n_R > 1 else axes[j]
            
            if j < len(timeline):
                ax.imshow(timeline[j], cmap=cmap, vmin=0, vmax=1)
            
            if j == 0:
                ax.set_ylabel(f'R={R}', fontsize=10)
            if i == 0:
                ax.set_title(f't={j * 50}', fontsize=9)
            ax.axis('off')
    
    fig.suptitle('Orbium Seed Evolution Across R Values', fontsize=12)
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / 'exp3_orbium_timeline_comparison.png', dpi=150, bbox_inches='tight', facecolor='black')
    plt.close(fig)
    print(f"[OK] Timeline comparison saved")
    
    # Create score comparison plot
    fig, ax = plt.subplots(figsize=(10, 5))
    
    x_labels = [f'R={R}' for R in R_values]
    scores = [results[R]['final_stats']['score'] for R in R_values]
    alives = [results[R]['final_stats']['alive'] for R in R_values]
    entropies = [results[R]['final_stats']['entropy'] for R in R_values]
    
    x = np.arange(len(R_values))
    width = 0.25
    
    ax.bar(x - width, scores, width, label='Score', color='#4488cc')
    ax.bar(x, alives, width, label='Alive %', color='#44cc88')
    ax.bar(x + width, entropies, width, label='Entropy', color='#cc8844')
    
    ax.set_xlabel('Kernel Radius (R)', fontsize=11)
    ax.set_ylabel('Value', fontsize=11)
    ax.set_title('Orbium Seed Performance Across R Values', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / 'exp3_orbium_score_comparison.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"[OK] Score comparison saved")
    
    # Create final state comparison
    fig, axes = plt.subplots(1, n_R, figsize=(3 * n_R, 3.5))
    if n_R == 1:
        axes = [axes]
    
    for i, R in enumerate(R_values):
        ax = axes[i]
        timeline = all_timelines[R]
        final = timeline[-1]
        
        ax.imshow(final, cmap=cmap, vmin=0, vmax=1)
        stats = results[R]['final_stats']
        ax.set_title(f"R={R}\nscore={stats['score']:.3f}\n{results[R]['final_state']}", fontsize=9)
        ax.axis('off')
    
    fig.suptitle(f'Final States: Orbium Seed (μ={BEST_MU}, σ={BEST_SIGMA})', fontsize=11)
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / 'exp3_orbium_final_states.png', dpi=150, bbox_inches='tight', facecolor='black')
    plt.close(fig)
    print(f"[OK] Final states saved")


# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 60)
    print("Lenia Fine Parameter Search Experiment")
    print(f"Best params from v2: R={BEST_R}, mu={BEST_MU}, sigma={BEST_SIGMA}")
    print(f"Output: {OUTPUT_DIR}")
    print("=" * 60)
    
    t0 = time.time()
    
    # Experiment 1: Long simulation
    exp1 = experiment_1_long_simulation()
    
    # Experiment 2: Fine sweep
    exp2_results, exp2_grids = experiment_2_fine_sweep()
    
    # Experiment 3: Orbium comparison
    exp3_results, exp3_timelines = experiment_3_orbium_comparison()
    
    # Create summary report
    total_time = time.time() - t0
    
    report = f"""# Lenia Fine Parameter Search Report

**Date**: {time.strftime('%Y-%m-%d %H:%M')}
**Base Parameters**: R={BEST_R}, μ={BEST_MU}, σ={BEST_SIGMA}

## Summary

Total experiment time: {total_time:.1f}s

---

## Experiment 1: Long Simulation (1000 steps)

- **Parameters**: R={BEST_R}, μ={BEST_MU}, σ={BEST_SIGMA}
- **Final State**: {exp1['final_state']}
- **Score**: {exp1['final_stats']['score']:.4f}
- **Alive**: {exp1['final_stats']['alive']:.4f}
- **Entropy**: {exp1['final_stats']['entropy']:.4f}
- **Output**: `exp1_long_simulation.gif`

---

## Experiment 2: Fine-grained Parameter Sweep

- **R values**: [8, 9, 10, 11, 12]
- **μ range**: [{BEST_MU-0.02:.4f}, {BEST_MU+0.02:.4f}]
- **σ range**: [{max(0.01, BEST_SIGMA-0.01):.4f}, {BEST_SIGMA+0.01:.4f}]
- **Total runs**: {len(exp2_results)}

### Top 5 Parameter Combinations

"""
    
    for i, r in enumerate(exp2_results[:5], 1):
        report += f"{i}. R={r['R']}, μ={r['mu']:.4f}, σ={r['sigma']:.4f} → score={r['stats']['score']:.4f} [{r['state']}]\n"
    
    report += f"""
- **Output**: `exp2_parameter_landscape.png`, `exp2_best_per_R.png`

---

## Experiment 3: Orbium Seed Comparison

Comparison of Orbium seed behavior across R values with constant (μ, σ).

| R | State | Score | Alive | Entropy |
|---|-------|-------|-------|---------|
"""
    
    for R in [8, 9, 10, 11, 12]:
        r = exp3_results[R]
        report += f"| {R} | {r['final_state']} | {r['final_stats']['score']:.4f} | {r['final_stats']['alive']:.4f} | {r['final_stats']['entropy']:.4f} |\n"
    
    report += f"""
- **Output**: `exp3_orbium_timeline_comparison.png`, `exp3_orbium_score_comparison.png`, `exp3_orbium_final_states.png`

---

## Files Generated

- `exp1_long_simulation.gif` - 1000-step animation
- `exp1_long_timeline.png` - Timeline snapshot
- `exp2_parameter_landscape.png` - Score landscape
- `exp2_best_per_R.png` - Best pattern per R
- `exp3_orbium_timeline_comparison.png` - Orbium evolution comparison
- `exp3_orbium_score_comparison.png` - Score comparison chart
- `exp3_orbium_final_states.png` - Final state comparison
- `exp*_results.json` - Detailed results
"""
    
    with open(OUTPUT_DIR / 'experiment_report.md', 'w') as f:
        f.write(report)
    
    print("\n" + "=" * 60)
    print(f"All experiments complete! Total time: {total_time:.1f}s")
    print(f"Results saved to: {OUTPUT_DIR}")
    print("=" * 60)
    
    return {
        'exp1': exp1,
        'exp2': exp2_results[:10],
        'exp3': {k: {'state': v['final_state'], 'score': v['final_stats']['score']} for k, v in exp3_results.items()},
    }


if __name__ == '__main__':
    main()
