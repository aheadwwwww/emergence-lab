"""
Lenia Multi-Channel (RGB) — 扩展单通道到三通道

官方 Lenia 用 RGB 三通道产生更丰富的物种形态。
每个通道有自己的核参数 (R, mu, sigma)，通道间通过交互规则耦合。

简化实现：
- 3 个独立通道，每个通道有自己的 kernel 和 growth 参数
- 通道间通过"交互矩阵"耦合（暂时用简单的权重）
- JAX 加速，支持大网格和长时演化

参考：
- Bert Chan's Lenia with multiple channels
- https://github.com/Chakazul/Lenia
"""

import jax
import jax.numpy as jnp
from jax import jit
import numpy as np
from functools import partial
import matplotlib.pyplot as plt
from pathlib import Path
import json, time

from lenia_jax import _make_disk_kernel_np, analyze_state, classify_state, make_cmap


# ============================================================================
# Multi-Channel Kernel
# ============================================================================

def make_multichannel_kernel(shape, R_list, kn_list=None):
    """Create multi-channel kernels for RGB Lenia.
    
    Args:
        shape: grid shape (H, W)
        R_list: list of kernel radii for each channel [R_r, R_g, R_b]
        kn_list: list of kernel types for each channel
    
    Returns:
        kernels_fft: list of FFT'd kernels for each channel
    """
    if kn_list is None:
        kn_list = [1, 1, 1]  # all bump4
    
    h, w = shape
    kernels_fft = []
    
    for R, kn in zip(R_list, kn_list):
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
        
        kernels_fft.append(jnp.fft.fft2(jnp.array(kernel_pad)))
    
    return kernels_fft


# ============================================================================
# Multi-Channel Lenia Step
# ============================================================================

def _lenia_multichannel_step(grids, kernels_fft, mu_list, sigma_list, R_list, gn_list, coupling, dt=0.1):
    """Single multi-channel Lenia step.
    
    Args:
        grids: (C, H, W) array of C channels
        kernels_fft: list of FFT'd kernels
        mu_list: growth center for each channel (tuple)
        sigma_list: growth width for each channel (tuple)
        R_list: kernel radii (tuple, static)
        gn_list: growth function types (tuple)
        coupling: (C, C) interaction matrix
        dt: time step
    
    Returns:
        new_grids: updated grids
    """
    eps = 1e-8
    C = grids.shape[0]
    new_grids = []
    
    for c in range(C):
        # Compute potential for this channel
        grid_fft = jnp.fft.fft2(grids[c])
        conv_fft = grid_fft * kernels_fft[c]
        potential = jnp.fft.ifft2(conv_fft).real
        n_potential = jnp.clip(potential, 0, 1)
        
        # Growth function
        mu = mu_list[c]
        sigma = sigma_list[c]
        gn = gn_list[c]
        
        if gn == 0:
            growth = jnp.maximum(0, 1 - ((n_potential - mu) / (9 * sigma))**2)**4 * 2 - 1
        elif gn == 1:
            growth = jnp.exp(-((n_potential - mu)**2) / (2 * sigma**2)) * 2 - 1
        elif gn == 2:
            growth = jnp.where(jnp.abs(n_potential - mu) <= sigma, 1.0, -1.0)
        else:
            growth = jnp.exp(-((n_potential - mu)**2) / (2 * sigma**2)) * 2 - 1
        
        # Apply coupling from other channels (simplified: weighted sum of other channels' grids)
        coupling_effect = jnp.zeros_like(grids[c])
        for other_c in range(C):
            if other_c != c:
                coupling_effect = coupling_effect + coupling[c, other_c] * grids[other_c]
        
        # Combined update
        update = growth + 0.1 * coupling_effect  # small coupling influence
        new_grid = grids[c] + dt * update
        new_grid = jnp.clip(new_grid, 0, 1)
        new_grids.append(new_grid)
    
    return jnp.stack(new_grids)


# ============================================================================
# Run Multi-Channel Lenia
# ============================================================================

def run_lenia_multichannel(
    shape=(256, 256),
    R_list=[20, 20, 20],
    mu_list=[0.15, 0.15, 0.15],
    sigma_list=[0.03, 0.03, 0.03],
    kn_list=[1, 1, 1],
    gn_list=[1, 1, 1],
    coupling=None,
    steps=200,
    init='random',
    seed_path=None,
    record_every=20,
    save_timeline=None,
):
    """Run multi-channel Lenia simulation."""
    h, w = shape
    C = 3
    
    # Initialize grids
    if init == 'random':
        rng = np.random.default_rng()
        grids = rng.uniform(0, 0.3, (C, h, w)).astype(np.float32)
    elif init == 'orbium':
        # Use single-channel orbium as base, add small noise to other channels
        from lenia_jax import make_orbium
        base = make_orbium(shape, R=R_list[0])
        grids = np.stack([base, base * 0.5, base * 0.3], axis=0).astype(np.float32)
    else:
        grids = np.zeros((C, h, w), dtype=np.float32)
        cy, cx = h // 2, w // 2
        r = min(shape) // 6
        for c in range(C):
            rng = np.random.default_rng(42 + c)
            blob = rng.uniform(0, 0.5, (2*r+1, 2*r+1))
            grids[c, cy-r:cy+r+1, cx-r:cx+r+1] = blob
    
    # Create kernels
    kernels_fft = make_multichannel_kernel(shape, R_list, kn_list)
    
    # Coupling matrix (default: weak positive coupling)
    if coupling is None:
        coupling = jnp.array([
            [1.0, 0.1, 0.05],
            [0.1, 1.0, 0.1],
            [0.05, 0.1, 1.0],
        ])
    else:
        coupling = jnp.array(coupling)
    
    # Run simulation
    frames = [grids.copy()]
    t0 = time.time()
    
    grids = jnp.array(grids)
    
    # Create JIT-compiled step function with fixed static args
    _step_jit = jit(_lenia_multichannel_step, static_argnums=(4, 5))
    
    for step in range(steps):
        grids = _step_jit(
            grids, kernels_fft, tuple(mu_list), tuple(sigma_list),
            tuple(R_list), tuple(gn_list), coupling
        )
        
        if (step + 1) % record_every == 0:
            frames.append(np.array(grids))
    
    elapsed = time.time() - t0
    
    # Analyze final state (average across channels)
    final_grid = np.mean(grids, axis=0)
    stats = analyze_state(jnp.array(final_grid))
    label = classify_state(stats)
    
    # Save timeline
    if save_timeline:
        fig, axes = plt.subplots(3, len(frames), figsize=(4 * len(frames), 12))
        if len(frames) == 1:
            axes = axes.reshape(3, 1)
        
        cmaps = ['Reds', 'Greens', 'Blues']
        
        for i, frame in enumerate(frames):
            for c in range(C):
                ax = axes[c, i]
                ax.imshow(frame[c], cmap=cmaps[c], vmin=0, vmax=1)
                ax.set_title(f'Ch{"RGB"[c]} Step {i * record_every}')
                ax.axis('off')
        
        plt.tight_layout()
        fig.savefig(save_timeline, dpi=100, bbox_inches='tight', facecolor='#111122')
        plt.close(fig)
    
    return {
        'final': np.array(grids),
        'stats': stats,
        'state': label,
        'time': round(elapsed, 2),
        'frames': frames,
        'timeline_path': save_timeline,
    }


# ============================================================================
# CLI
# ============================================================================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Multi-Channel Lenia')
    parser.add_argument('--shape', type=int, nargs=2, default=[256, 256])
    parser.add_argument('--R', type=int, nargs=3, default=[20, 20, 20], help='Kernel radii for RGB')
    parser.add_argument('--mu', type=float, nargs=3, default=[0.15, 0.15, 0.15], help='Growth centers')
    parser.add_argument('--sigma', type=float, nargs=3, default=[0.03, 0.03, 0.03], help='Growth widths')
    parser.add_argument('--steps', type=int, default=300)
    parser.add_argument('--output', type=str, default='experiments/lenia_multichannel.png')
    
    args = parser.parse_args()
    
    print(f"Multi-Channel Lenia: {args.shape}, R={args.R}, mu={args.mu}, sigma={args.sigma}")
    
    result = run_lenia_multichannel(
        shape=tuple(args.shape),
        R_list=args.R,
        mu_list=args.mu,
        sigma_list=args.sigma,
        steps=args.steps,
        save_timeline=args.output,
    )
    
    print(f"Done: {result['state']} | {result['stats']} | {result['time']}s")
    print(f"Timeline: {result['timeline_path']}")
