"""
异步 Lenia — 引入 NCA 的随机异步更新机制

核心改动：
- 每步只有 fire_rate% 的细胞更新
- 随机掩码决定哪些细胞参与更新
- 目标：提升鲁棒性，容忍局部错误
"""

import jax
import jax.numpy as jnp
from jax import jit
import numpy as np
from functools import partial
import matplotlib.pyplot as plt
from pathlib import Path
import json, time

from lenia_jax import _make_disk_kernel_np, analyze_state, classify_state


# ============================================================================
# Async Lenia Step
# ============================================================================

@partial(jit, static_argnums=(2, 3, 4))
def _lenia_async_step(grid, kernel_fft, params, fire_rate=0.5, gn=1, dt=0.1):
    """Single async Lenia step with stochastic update mask.
    
    Args:
        grid: (H, W) state array
        kernel_fft: FFT'd kernel
        params: (mu, sigma) tuple
        fire_rate: probability of each cell updating (static)
        gn: growth function type (static)
        dt: time step
    
    Returns:
        new_grid: updated grid
    """
    mu, sigma = params
    h, w = grid.shape
    
    # Generate random mask for async update
    rng = jax.random.PRNGKey(int(time.time() * 1000) % 2**31)
    update_mask = jax.random.uniform(rng, (h, w)) < fire_rate
    
    # Convolution (all cells perceive, but only some update)
    grid_fft = jnp.fft.fft2(grid)
    conv_fft = grid_fft * kernel_fft
    potential = jnp.fft.ifft2(conv_fft).real
    n_potential = jnp.clip(potential, 0, 1)
    
    # Growth function
    growth = jnp.exp(-((n_potential - mu)**2) / (2 * sigma**2)) * 2 - 1
    
    # Apply update only to selected cells
    update = growth * update_mask
    new_grid = grid + dt * update
    new_grid = jnp.clip(new_grid, 0, 1)
    
    return new_grid


# ============================================================================
# Run Async Lenia
# ============================================================================

def run_async_lenia(
    shape=(256, 256),
    R=20,
    mu=0.15,
    sigma=0.03,
    kn=1,
    gn=1,
    fire_rate=0.5,
    steps=300,
    init='random',
    record_every=50,
    save_timeline=None,
):
    """Run async Lenia simulation."""
    h, w = shape
    
    # Initialize grid
    if init == 'random':
        rng = np.random.default_rng()
        grid = rng.uniform(0, 0.2, (h, w)).astype(np.float32)
        cy, cx = h // 2, w // 2
        r = min(shape) // 6
        blob = rng.uniform(0.2, 0.6, (2*r+1, 2*r+1))
        grid[cy-r:cy+r+1, cx-r:cx+r+1] = blob
    else:
        from lenia_jax import make_orbium
        grid = make_orbium(shape, R=R)
    
    # Create kernel
    kernel_2r1 = _make_disk_kernel_np(R, kn)
    k_h, k_w = kernel_2r1.shape
    pad_h = (h - k_h) // 2
    pad_w = (w - k_w) // 2
    kernel_pad = np.pad(kernel_2r1,
                        ((pad_h, h - k_h - pad_h),
                         (pad_w, w - k_w - pad_w)))
    cy = pad_h + R
    cx = pad_w + R
    kernel_pad = np.roll(kernel_pad, -cy, axis=0)
    kernel_pad = np.roll(kernel_pad, -cx, axis=1)
    kernel_fft = jnp.fft.fft2(jnp.array(kernel_pad))
    
    # Run simulation
    frames = [grid.copy()]
    t0 = time.time()
    
    grid = jnp.array(grid)
    
    for step in range(steps):
        # Use fixed fire_rate and gn, pass as static tuple
        grid = _lenia_async_step(grid, kernel_fft, (mu, sigma), fire_rate, gn)
        
        if (step + 1) % record_every == 0:
            frames.append(np.array(grid))
    
    elapsed = time.time() - t0
    
    # Analyze final state
    stats = analyze_state(grid)
    label = classify_state(stats)
    
    # Save timeline
    if save_timeline:
        n_frames = len(frames)
        fig, axes = plt.subplots(1, n_frames, figsize=(4 * n_frames, 4))
        if n_frames == 1:
            axes = [axes]
        
        cmap = plt.cm.coolwarm
        cmap.set_bad(color='#111122')
        
        for i, frame in enumerate(frames):
            ax = axes[i]
            ax.imshow(frame, cmap=cmap, vmin=0, vmax=1)
            ax.set_title(f'Step {i * record_every}')
            ax.axis('off')
        
        plt.tight_layout()
        fig.savefig(save_timeline, dpi=100, bbox_inches='tight', facecolor='#111122')
        plt.close(fig)
    
    return {
        'final': np.array(grid),
        'stats': stats,
        'state': label,
        'time': round(elapsed, 2),
        'frames': frames,
        'timeline_path': save_timeline,
    }


# ============================================================================
# Compare Sync vs Async
# ============================================================================

def compare_sync_async(R=20, mu=0.14, sigma=0.024, steps=300, shape=(256, 256)):
    """Compare synchronous vs asynchronous Lenia."""
    
    # Sync Lenia
    from lenia_jax import run_lenia
    sync_result = run_lenia(
        shape=shape, R=R, mu=mu, sigma=sigma, 
        steps=steps, init='orbium',
        save_timeline='experiments/lenia_sync_comparison.png'
    )
    
    # Async Lenia (50% fire rate)
    async_result = run_async_lenia(
        shape=shape, R=R, mu=mu, sigma=sigma,
        fire_rate=0.5, steps=steps, init='orbium',
        save_timeline='experiments/lenia_async_comparison.png'
    )
    
    print(f"Sync: {sync_result['state']} | alive={sync_result['stats']['alive']:.3f} | time={sync_result['time']}s")
    print(f"Async (50%): {async_result['state']} | alive={async_result['stats']['alive']:.3f} | time={async_result['time']}s")
    
    return {
        'sync': sync_result,
        'async': async_result,
    }


# ============================================================================
# CLI
# ============================================================================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Async Lenia')
    parser.add_argument('--R', type=int, default=20)
    parser.add_argument('--mu', type=float, default=0.14)
    parser.add_argument('--sigma', type=float, default=0.024)
    parser.add_argument('--fire-rate', type=float, default=0.5)
    parser.add_argument('--steps', type=int, default=300)
    parser.add_argument('--shape', type=int, nargs=2, default=[256, 256])
    parser.add_argument('--output', type=str, default='experiments/lenia_async.png')
    parser.add_argument('--compare', action='store_true', help='Compare sync vs async')
    
    args = parser.parse_args()
    
    if args.compare:
        result = compare_sync_async(
            R=args.R, mu=args.mu, sigma=args.sigma,
            steps=args.steps, shape=tuple(args.shape)
        )
    else:
        result = run_async_lenia(
            shape=tuple(args.shape),
            R=args.R,
            mu=args.mu,
            sigma=args.sigma,
            fire_rate=args.fire_rate,
            steps=args.steps,
            save_timeline=args.output,
        )
        print(f"Result: {result['state']} | {result['stats']} | {result['time']}s")