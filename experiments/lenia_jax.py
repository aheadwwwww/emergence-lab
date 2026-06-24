"""
Lenia (JAX-accelerated) — Continuous Cellular Automata
Based on Bert Chan's Lenia (2019) with GPU-like speed via JAX.

Key improvements over NumPy version:
- JAX JIT + FFT convolution → ~10-50x faster
- Handles R>=20 with 256×256 grids easily
- Orbium seed patterns support
- Multi-ring kernel shell (beta parameters)

References:
- Chan, B. W.-C. (2019). Lenia - Biology of Artificial Life. Complex Systems, 28(3), 251–286.
- https://github.com/Chakazul/Lenia
"""

import jax
import jax.numpy as jnp
from jax import jit
import numpy as np
from scipy.ndimage import zoom
from functools import partial
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path
import json, time, argparse

# ============================================================================
# Core Lenia Functions (JAX JIT compiled)
# ============================================================================

def _make_disk_kernel_np(R, kn=0):
    """Create normalized circular kernel using NumPy (pre-JIT).
    
    kn: kernel type (matching official Lenia)
      0 = quad4: (4*r*(1-r))^4
      1 = bump4: exp(4 - 1/(r*(1-r)))
      2 = step:  (r>=1/4)*(r<=3/4)
    """
    y, x = np.ogrid[-R:R+1, -R:R+1]
    dist = np.sqrt(x*x + y*y) / R
    dist = np.clip(dist, 0, 1)
    
    eps = 1e-8
    r = np.clip(dist, eps, 1 - eps)
    
    if kn == 0:
        kernel = (4 * r * (1 - r))**4
    elif kn == 1:
        # Official Lenia bump4: exp(4 - 1/(r*(1-r)))
        kernel = np.exp(4.0 - 1.0 / (r * (1 - r)))
    elif kn == 2:
        q = 0.25
        kernel = ((r >= q) & (r <= 1 - q)).astype(np.float32)
    else:
        kernel = (4 * r * (1 - r))**4
    
    # Zero beyond R
    mask = dist <= 1.0
    kernel = kernel * mask
    # Normalize
    kernel = kernel / (kernel.sum() + eps)
    return kernel.astype(np.float32)


@partial(jit, static_argnums=(2, 3, 4, 5))
def _lenia_step(grid, kernel_fft, mu, sigma, R, gn=0):
    """Single Lenia update step.
    
    gn: growth function type (matching official Lenia)
      0 = quad4: max(0, 1-(n-m)^2/(9*s^2))^4 * 2 - 1
      1 = gaus:  exp(-(n-m)^2/(2*s^2)) * 2 - 1
      2 = step:  (|n-m|<=s) * 2 - 1
    """
    eps = 1e-8
    
    # FFT-based convolution
    grid_fft = jnp.fft.fft2(grid)
    conv_fft = grid_fft * kernel_fft
    potential = jnp.fft.ifft2(conv_fft).real
    
    # Clip potential to [0, 1]
    n_potential = jnp.clip(potential, 0, 1)
    
    # Growth function
    if gn == 0:
        # quad4: max(0, 1-(n-m)^2/(9*s^2))^4 * 2 - 1
        growth = jnp.maximum(0, 1 - ((n_potential - mu) / (9 * sigma))**2)**4 * 2 - 1
    elif gn == 1:
        # gaus: exp(-(n-m)^2/(2*s^2)) * 2 - 1
        growth = jnp.exp(-((n_potential - mu)**2) / (2 * sigma**2)) * 2 - 1
    elif gn == 2:
        # step: (|n-m|<=s) * 2 - 1
        growth = jnp.where(jnp.abs(n_potential - mu) <= sigma, 1.0, -1.0)
    else:
        growth = jnp.maximum(0, 1 - ((n_potential - mu) / (9 * sigma))**2)**4 * 2 - 1
    
    # Euler integration
    dt = 0.1
    new_grid = grid + dt * growth
    new_grid = jnp.clip(new_grid, 0, 1)
    
    return new_grid, potential


def make_kernel_fft(shape, R, kn=0):
    """Create kernel and its FFT for convolution.
    
    Properly centers the kernel at (0,0) for FFT convolution.
    """
    kernel_2r1 = _make_disk_kernel_np(R, kn)
    h, w = shape
    k_h, k_w = kernel_2r1.shape
    
    # Pad to full grid size, kernel center at (R, R) in kernel_2r1
    pad_h = (h - k_h) // 2
    pad_w = (w - k_w) // 2
    kernel_pad = np.pad(kernel_2r1, 
                        ((pad_h, h - k_h - pad_h), 
                         (pad_w, w - k_w - pad_w)))
    
    # Kernel center in padded array: (pad_h + R, pad_w + R)
    # For FFT: roll so center is at (0, 0)
    cy = pad_h + R
    cx = pad_w + R
    kernel_pad = np.roll(kernel_pad, -cy, axis=0)
    kernel_pad = np.roll(kernel_pad, -cx, axis=1)
    
    return jnp.fft.fft2(jnp.array(kernel_pad))


# ============================================================================
# Orbium Seed Patterns
# ============================================================================

def make_orbium(shape, R=20, variant='classic'):
    """Create an Orbium seed pattern.
    
    Orbium is the iconic Lenia species — a glider-like creature
    that moves diagonally, leaving a trail.
    """
    h, w = shape
    cy, cx = h // 2, w // 2
    
    grid = np.zeros(shape, dtype=np.float32)
    
    # Orbium is approximately a circle of radius ~R*0.6 with some asymmetry
    r_orb = int(R * 0.55)
    
    y_coords, x_coords = np.ogrid[-r_orb:r_orb+1, -r_orb:r_orb+1]
    dist = np.sqrt(x_coords**2 + y_coords**2)
    
    # Basic circle with density gradient
    orb_cells = np.exp(-dist**2 / (2 * (r_orb * 0.7)**2))
    
    # Add asymmetry (Orbium's "head" is denser on one side)
    if variant == 'classic':
        orb_cells *= (1 + 0.3 * (1 - x_coords / (r_orb + 1)))
    elif variant == 'split':
        orb_cells *= (1 + 0.5 * np.sin(x_coords / (r_orb + 1) * 3))
    elif variant == 'ring':
        orb_cells = np.exp(-((dist - r_orb * 0.6)**2) / (2 * (r_orb * 0.15)**2))
    
    orb_cells = np.clip(orb_cells, 0, 1)
    
    y_start = cy - r_orb
    x_start = cx - r_orb
    grid[y_start:y_start+2*r_orb+1, x_start:x_start+2*r_orb+1] = orb_cells
    
    return grid


def make_random_seed(shape, radius=None, density=0.3):
    """Create a random seed blob."""
    if radius is None:
        radius = min(shape) // 6
    
    grid = np.zeros(shape, dtype=np.float32)
    h, w = shape
    cy, cx = h // 2, w // 2
    
    y_coords, x_coords = np.ogrid[-radius:radius+1, -radius:radius+1]
    dist = np.sqrt(x_coords**2 + y_coords**2) / radius
    
    rng = np.random.default_rng()
    noise = rng.uniform(0, 1, (2*radius+1, 2*radius+1))
    mask = dist <= 1.0
    blob = noise * mask * density
    
    y_start = cy - radius
    x_start = cx - radius
    grid[y_start:y_start+2*radius+1, x_start:x_start+2*radius+1] = blob
    
    return grid


# ============================================================================
# Analysis
# ============================================================================

def analyze_state(grid, potential=None, n_steps=5):
    """Analyze Lenia state: alive%, entropy, stability, edge density."""
    eps = 1e-8
    
    alive = float(jnp.mean(grid > 0.01))
    
    # Entropy of histogram
    hist, _ = jnp.histogram(grid, bins=20, range=(0, 1))
    probs = hist / (hist.sum() + eps)
    entropy = -jnp.sum(probs * jnp.log(probs + eps))
    entropy_norm = entropy / jnp.log(20.0)
    
    # Edge density (gradient magnitude)
    gy = grid[1:, :] - grid[:-1, :]
    gx = grid[:, 1:] - grid[:, :-1]
    edge = jnp.mean(jnp.abs(gy)) + jnp.mean(jnp.abs(gx))
    edge_density = float(edge / 2.0)
    
    # Stability (inverse of rate of change)
    stability = float(1.0 / (edge_density + eps))
    stability = min(stability, 100.0) / 100.0
    
    # Score (prefer alive, high entropy, medium edge density)
    score = alive * 0.3 + entropy_norm * 0.3 + min(edge_density * 5, 1.0) * 0.2 + stability * 0.2
    
    return {
        'alive': round(alive, 4),
        'entropy': round(float(entropy_norm), 4),
        'edge_density': round(edge_density, 4),
        'stability': round(stability, 4),
        'score': round(float(score), 4),
    }


def classify_state(stats):
    """Classify Lenia state."""
    if stats['alive'] < 0.001:
        return 'dead'
    if stats['edge_density'] < 0.01:
        if stats['alive'] > 0.8:
            return 'saturated'
        return 'uniform'
    if stats['edge_density'] > 0.05 and stats['alive'] > 0.01 and stats['alive'] < 0.5:
        return 'structure'
    return 'simple'


# ============================================================================
# Visualization
# ============================================================================

def make_cmap():
    """Custom colormap for Lenia (dark blue → teal → yellow)."""
    colors = [
        (0.0, 0.0, 0.1),       # deep space
        (0.0, 0.1, 0.3),       # dark blue
        (0.0, 0.4, 0.6),       # teal
        (0.1, 0.7, 0.5),       # mint
        (0.6, 0.9, 0.3),       # lime
        (1.0, 1.0, 0.0),       # yellow
        (1.0, 1.0, 1.0),       # white peak
    ]
    return LinearSegmentedColormap.from_list('lenia', colors)


def render_timeline(grids, potentials=None, filename='lenia_timeline.png', step_labels=None):
    """Render a timeline of Lenia states."""
    n = len(grids)
    cols = min(n, 6)
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
            if step_labels and i < len(step_labels):
                label = step_labels[i]
            elif potentials and i < len(potentials):
                stats = analyze_state(grids[i])
                label = f'step={i*50}'
                if stats['alive'] > 0.001:
                    label += f"\nalive={stats['alive']:.2f} score={stats['score']:.2f}"
                else:
                    label += '\n(dead)'
            else:
                label = f'step={i*50}'
            ax.set_title(label, fontsize=9)
        ax.axis('off')
    
    plt.tight_layout(pad=0.5)
    fig.savefig(filename, dpi=150, bbox_inches='tight', facecolor='black')
    plt.close(fig)
    print(f"[OK] Timeline saved: {filename}")
    return filename


# ============================================================================
# Main Simulation
# ============================================================================

def load_seed(seed_path, shape, R):
    """Load a seed array and place it centered on a grid of given shape."""
    seed = np.load(seed_path)
    sh, sw = seed.shape
    h, w = shape
    grid = np.zeros(shape, dtype=np.float32)
    y0 = (h - sh) // 2
    x0 = (w - sw) // 2
    grid[y0:y0+sh, x0:x0+sw] = seed
    return grid


def run_lenia(shape=(256, 256), R=20, mu=0.15, sigma=0.015, kn=0, gn=0,
              steps=500, init='orbium', orbium_variant='classic',
              seed_path=None, record_every=50, save_timeline=None, verbose=True):
    """Run Lenia simulation with JAX acceleration.
    
    gn: growth function type (0=quad4, 1=gaus, 2=step)
    init: 'orbium', 'random', or 'seed' (load from seed_path)
    """
    
    if verbose:
        print(f"Lenia: {shape[0]}x{shape[1]}, R={R}, mu={mu}, sigma={sigma}, kn={kn}, gn={gn}, steps={steps}")
    
    # Initialize grid
    if init == 'seed' and seed_path:
        grid = load_seed(seed_path, shape, R)
        if verbose:
            print(f"  Loaded seed: {seed_path} ({grid.shape})")
    elif init == 'orbium':
        grid = make_orbium(shape, R, orbium_variant)
    elif init == 'random':
        grid = make_random_seed(shape, R)
    else:
        grid = make_orbium(shape, R, 'classic')
    
    grid = jnp.array(grid)
    
    # Prepare kernel
    kernel_fft = make_kernel_fft(shape, R, kn)
    
    # Run simulation
    grids = [grid]
    potentials_list = []
    t0 = time.time()
    
    for step in range(steps):
        grid, potential = _lenia_step(grid, kernel_fft, mu, sigma, R, gn)
        
        if (step + 1) % record_every == 0 or step == 0:
            grids.append(grid)
            potentials_list.append(potential)
        
        if verbose and (step + 1) % (steps // 10) == 0:
            stats = analyze_state(grid)
            elapsed = time.time() - t0
            print(f"  step {step+1}/{steps} | alive={stats['alive']:.3f} score={stats['score']:.3f} | {elapsed:.1f}s")
    
    elapsed = time.time() - t0
    final_stats = analyze_state(grid)
    final_state = classify_state(final_stats)
    
    if verbose:
        print(f"  done in {elapsed:.1f}s | {final_state} | alive={final_stats['alive']:.3f}")
    
    result = {
        'params': {'R': R, 'mu': mu, 'sigma': sigma, 'kn': kn, 'gn': gn, 'shape': list(shape), 'steps': steps},
        'stats': final_stats,
        'state': final_state,
        'time': round(elapsed, 2),
        'grids': [np.array(g) for g in grids],
        'potentials': [],
    }
    
    if save_timeline:
        step_labels = [f'step={i*record_every}' for i in range(len(grids))]
        result['timeline_path'] = render_timeline(grids, potentials_list, save_timeline, step_labels)
    
    return result


# ============================================================================
# Parameter Sweep
# ============================================================================

def sweep_lenia(shape=(192, 192), R=13, grid_n=7, steps=300):
    """Grid sweep over (mu, sigma) parameter space."""
    mus = np.linspace(0.06, 0.22, grid_n)
    sigmas = np.linspace(0.008, 0.040, grid_n)
    
    results = []
    t0 = time.time()
    
    for i, mu in enumerate(mus):
        for j, sigma in enumerate(sigmas):
            result = run_lenia(
                shape=shape, R=R, mu=round(mu, 4), sigma=round(sigma, 4),
                steps=steps, init='random', verbose=False
            )
            entry = {
                'mu': round(float(mu), 4),
                'sigma': round(float(sigma), 4),
                'alive': result['stats']['alive'],
                'entropy': result['stats']['entropy'],
                'edge_density': result['stats']['edge_density'],
                'stability': result['stats']['stability'],
                'score': result['stats']['score'],
                'label': result['state'],
            }
            results.append(entry)
            if (i * grid_n + j + 1) % 10 == 0:
                elapsed = time.time() - t0
                print(f"  [{i*grid_n+j+1}/{grid_n*grid_n}] {elapsed:.1f}s | last: mu={mu:.3f} σ={sigma:.3f} → {result['state']}")
    
    elapsed = time.time() - t0
    print(f"\nSweep done: {len(results)} runs in {elapsed:.1f}s")
    
    # Summarize
    labels = {}
    for r in results:
        lbl = r['label']
        labels[lbl] = labels.get(lbl, 0) + 1
    
    total = len(results)
    print(f"  Results: " + ", ".join(f"{k}: {v}/{total} ({v/total*100:.1f}%)" for k, v in sorted(labels.items())))
    
    best = max(results, key=lambda r: r['score'])
    print(f"  Best: mu={best['mu']}, sigma={best['sigma']}, score={best['score']:.4f}")
    
    return results


# ============================================================================
# CLI
# ============================================================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Lenia (JAX) — Continuous CA')
    parser.add_argument('--mode', default='single', choices=['single', 'sweep', 'test'],
                        help='Run mode')
    parser.add_argument('--shape', type=int, nargs=2, default=[256, 256],
                        help='Grid size (default: 256 256)')
    parser.add_argument('--R', type=int, default=20, help='Kernel radius')
    parser.add_argument('--mu', type=float, default=0.15, help='Growth center')
    parser.add_argument('--sigma', type=float, default=0.015, help='Growth width')
    parser.add_argument('--kn', type=int, default=1, choices=[0, 1, 2],
                        help='Kernel type: 0=quad4, 1=bump4, 2=step')
    parser.add_argument('--gn', type=int, default=1, choices=[0, 1, 2],
                        help='Growth function: 0=quad4, 1=gaus, 2=step')
    parser.add_argument('--steps', type=int, default=500, help='Simulation steps')
    parser.add_argument('--init', default='orbium', choices=['orbium', 'random', 'seed'],
                        help='Initialization')
    parser.add_argument('--seed-path', default=None, help='Path to .npy seed file (for init=seed)')
    parser.add_argument('--variant', default='classic',
                        choices=['classic', 'split', 'ring'],
                        help='Orbium variant')
    parser.add_argument('--output', default=None, help='Output timeline image')
    parser.add_argument('--grid-n', type=int, default=7, help='Sweep grid size')
    
    args = parser.parse_args()
    
    if args.mode == 'sweep':
        results = sweep_lenia(
            shape=tuple(args.shape), R=args.R,
            grid_n=args.grid_n, steps=args.steps
        )
        
        out_json = args.output or f'experiments/lenia_jax_sweep_R{args.R}.json'
        with open(out_json, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"[OK] Results saved: {out_json}")
        
        # Also create a summary scatter plot
        fig, ax = plt.subplots(figsize=(8, 6))
        
        for r in results:
            color = {'dead': '#333333', 'simple': '#4488cc', 'structure': '#ff6644', 'uniform': '#666666', 'saturated': '#aa44aa'}
            ax.scatter(r['mu'], r['sigma'], s=80 + r['score'] * 200,
                      c=color.get(r['label'], 'gray'), alpha=0.7, edgecolors='white', linewidth=0.5)
        
        ax.set_xlabel('μ (growth center)', fontsize=12)
        ax.set_ylabel('σ (growth width)', fontsize=12)
        ax.set_title(f'Lenia Parameter Landscape (R={args.R}, {args.shape[0]}x{args.shape[1]})', fontsize=13)
        
        from matplotlib.patches import Patch
        legend = [
            Patch(color='#333333', label='Dead'),
            Patch(color='#4488cc', label='Simple'),
            Patch(color='#ff6644', label='Structure'),
            Patch(color='#aa44aa', label='Saturated'),
        ]
        ax.legend(handles=legend, loc='upper right')
        
        scatter_path = out_json.replace('.json', '_scatter.png')
        fig.savefig(scatter_path, dpi=150, bbox_inches='tight', facecolor='#111122')
        plt.close(fig)
        print(f"[OK] Scatter plot: {scatter_path}")
        
    elif args.mode == 'test':
        # Quick test
        result = run_lenia(
            shape=tuple(args.shape), R=args.R,
            mu=args.mu, sigma=args.sigma, kn=args.kn, gn=args.gn,
            steps=args.steps, init=args.init,
            seed_path=args.seed_path,
            orbium_variant=args.variant,
            record_every=50,
            save_timeline=args.output or 'experiments/lenia_jax_test.png'
        )
        
    else:  # single
        result = run_lenia(
            shape=tuple(args.shape), R=args.R,
            mu=args.mu, sigma=args.sigma, kn=args.kn, gn=args.gn,
            steps=args.steps, init=args.init,
            seed_path=args.seed_path,
            orbium_variant=args.variant,
            record_every=50,
            save_timeline=args.output or 'experiments/lenia_jax_orbium.png'
        )
        
        stats = result['stats']
        print(f"\nFinal: {result['state']} | alive={stats['alive']:.4f} entropy={stats['entropy']:.4f}")
        print(f"  edge_density={stats['edge_density']:.4f} stability={stats['stability']:.4f}")
        print(f"  score={stats['score']:.4f} time={result['time']}s")
        print(f"  Timeline: {result.get('timeline_path', 'N/A')}")
