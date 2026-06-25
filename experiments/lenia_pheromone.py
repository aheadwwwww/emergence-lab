"""
Lenia + Pheromone Coupling — 信息素耦合多通道 Lenia

灵感来自 gkirgizov/die 的信息素机制：
- 每个通道释放信息素（正比于活性）
- 信息素扩散+衰减
- 通道根据信息素梯度微调 growth 参数

假设：信息素耦合可能产生更稳定的多物种共存
"""

import jax
import jax.numpy as jnp
from jax import jit
import numpy as np
from functools import partial
import matplotlib.pyplot as plt
from pathlib import Path
import time

from lenia_jax import _make_disk_kernel_np, analyze_state, classify_state, make_cmap


def make_multichannel_kernel(shape, R_list, kn_list=None):
    """Create multi-channel kernels for RGB Lenia."""
    if kn_list is None:
        kn_list = [1, 1, 1]
    
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


def gaussian_kernel_fft(shape, sigma):
    """Create FFT of a Gaussian kernel for pheromone diffusion."""
    h, w = shape
    y = jnp.fft.fftfreq(h) * h
    x = jnp.fft.fftfreq(w) * w
    yy, xx = jnp.meshgrid(y, x, indexing='ij')
    dist_sq = xx**2 + yy**2
    gauss = jnp.exp(-2 * jnp.pi**2 * sigma**2 * dist_sq / (h * w))
    return gauss


def _lenia_pheromone_step(grids, kernels_fft, mu_list, sigma_list, R_list, gn_list,
                           coupling, pheromone_grids, gauss_fft, decay_rate, deposit_rate,
                           pheromone_influence, dt=0.1):
    """Single step with pheromone coupling.
    
    Args:
        grids: (C, H, W) Lenia channels
        pheromone_grids: (C, H, W) pheromone channels
        pheromone_influence: how much pheromone gradient shifts mu
    """
    C = grids.shape[0]
    new_grids = []
    new_pheromones = []
    
    for c in range(C):
        # === Lenia update ===
        grid_fft = jnp.fft.fft2(grids[c])
        conv_fft = grid_fft * kernels_fft[c]
        potential = jnp.fft.ifft2(conv_fft).real
        n_potential = jnp.clip(potential, 0, 1)
        
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
        
        # Pheromone influence: shift mu based on other channels' pheromone gradient
        pheromone_effect = 0.0
        for other_c in range(C):
            if other_c != c:
                # Mean pheromone from other channel → shifts mu
                mean_phero = jnp.mean(pheromone_grids[other_c])
                pheromone_effect += coupling[c, other_c] * mean_phero
        
        # Adjust mu by pheromone influence
        mu_adj = mu + pheromone_influence * pheromone_effect
        
        # Recompute growth with adjusted mu
        if gn == 0:
            growth_adj = jnp.maximum(0, 1 - ((n_potential - mu_adj) / (9 * sigma))**2)**4 * 2 - 1
        elif gn == 1:
            growth_adj = jnp.exp(-((n_potential - mu_adj)**2) / (2 * sigma**2)) * 2 - 1
        elif gn == 2:
            growth_adj = jnp.where(jnp.abs(n_potential - mu_adj) <= sigma, 1.0, -1.0)
        else:
            growth_adj = jnp.exp(-((n_potential - mu_adj)**2) / (2 * sigma**2)) * 2 - 1
        
        # Direct coupling from other channels
        coupling_effect = jnp.zeros_like(grids[c])
        for other_c in range(C):
            if other_c != c:
                coupling_effect = coupling_effect + coupling[c, other_c] * grids[other_c]
        
        update = growth_adj + 0.1 * coupling_effect
        new_grid = grids[c] + dt * update
        new_grid = jnp.clip(new_grid, 0, 1)
        new_grids.append(new_grid)
        
        # === Pheromone update ===
        # Deposit: proportional to channel activity
        deposit = deposit_rate * grids[c]
        
        # Diffuse pheromone in Fourier space
        phero_fft = jnp.fft.fft2(pheromone_grids[c] + deposit)
        diffused_fft = phero_fft * gauss_fft
        diffused = jnp.fft.ifft2(diffused_fft).real
        
        # Decay
        new_phero = diffused * (1 - decay_rate)
        new_phero = jnp.clip(new_phero, 0, 10)  # cap to prevent blowup
        new_pheromones.append(new_phero)
    
    return jnp.stack(new_grids), jnp.stack(new_pheromones)


def run_lenia_pheromone(
    shape=(256, 256),
    R_list=[12, 15, 18],
    mu_list=[0.15, 0.15, 0.15],
    sigma_list=[0.025, 0.015, 0.008],
    kn_list=[1, 1, 1],
    gn_list=[1, 1, 1],
    coupling=None,
    deposit_rate=0.1,
    decay_rate=0.05,
    diffusion_sigma=2.0,
    pheromone_influence=0.01,
    steps=300,
    init='random',
    record_every=20,
    save_timeline=None,
):
    """Run Lenia with pheromone coupling."""
    h, w = shape
    C = 3
    
    # Initialize grids
    rng = np.random.default_rng(42)
    if init == 'random':
        grids = rng.uniform(0, 0.3, (C, h, w)).astype(np.float32)
    else:
        grids = rng.uniform(0, 0.3, (C, h, w)).astype(np.float32)
    
    # Initialize pheromones to zero
    pheromone_grids = np.zeros((C, h, w), dtype=np.float32)
    
    # Create kernels
    kernels_fft = make_multichannel_kernel(shape, R_list, kn_list)
    
    # Gaussian diffusion kernel for pheromones
    gauss_fft = gaussian_kernel_fft(shape, diffusion_sigma)
    
    # Coupling matrix
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
    phero_frames = [pheromone_grids.copy()]
    t0 = time.time()
    
    grids = jnp.array(grids)
    pheromone_grids = jnp.array(pheromone_grids)
    
    _step_jit = jit(_lenia_pheromone_step, static_argnums=(4, 5))
    
    for step in range(steps):
        grids, pheromone_grids = _step_jit(
            grids, kernels_fft, tuple(mu_list), tuple(sigma_list),
            tuple(R_list), tuple(gn_list), coupling,
            pheromone_grids, gauss_fft, decay_rate, deposit_rate,
            pheromone_influence
        )
        
        if (step + 1) % record_every == 0:
            frames.append(np.array(grids))
            phero_frames.append(np.array(pheromone_grids))
    
    elapsed = time.time() - t0
    
    # Analyze final state
    final_grid = np.mean(grids, axis=0)
    stats = analyze_state(jnp.array(final_grid))
    label = classify_state(stats)
    
    # Channel-wise stats
    channel_stats = {}
    for c in range(C):
        ch_stats = analyze_state(jnp.array(grids[c]))
        channel_stats[f'ch{"RGB"[c]}'] = ch_stats
    
    # Save timeline
    if save_timeline:
        n_frames = len(frames)
        fig, axes = plt.subplots(6, n_frames, figsize=(4 * n_frames, 24))
        if n_frames == 1:
            axes = axes.reshape(6, 1)
        
        cmaps = ['Reds', 'Greens', 'Blues']
        phero_cmaps = ['OrRd', 'YlGn', 'PuBu']
        
        for i, (frame, phero_frame) in enumerate(zip(frames, phero_frames)):
            for c in range(C):
                # Lenia channels
                ax = axes[c, i]
                ax.imshow(frame[c], cmap=cmaps[c], vmin=0, vmax=1)
                ax.set_title(f'Ch{"RGB"[c]} Step {i * record_every}')
                ax.axis('off')
                
                # Pheromone channels
                ax_p = axes[c + 3, i]
                ax_p.imshow(phero_frame[c], cmap=phero_cmaps[c], vmin=0, vmax=phero_frame[c].max() * 0.8)
                ax_p.set_title(f'Phero{"RGB"[c]} Step {i * record_every}')
                ax_p.axis('off')
        
        plt.tight_layout()
        fig.savefig(save_timeline, dpi=100, bbox_inches='tight', facecolor='#111122')
        plt.close(fig)
    
    return {
        'final': np.array(grids),
        'final_pheromone': np.array(pheromone_grids),
        'stats': stats,
        'channel_stats': channel_stats,
        'state': label,
        'time': round(elapsed, 2),
        'frames': frames,
        'phero_frames': phero_frames,
        'timeline_path': save_timeline,
    }


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Lenia + Pheromone Coupling')
    parser.add_argument('--shape', type=int, nargs=2, default=[256, 256])
    parser.add_argument('--R', type=int, nargs=3, default=[12, 15, 18])
    parser.add_argument('--mu', type=float, nargs=3, default=[0.15, 0.15, 0.15])
    parser.add_argument('--sigma', type=float, nargs=3, default=[0.025, 0.015, 0.008])
    parser.add_argument('--deposit', type=float, default=0.1)
    parser.add_argument('--decay', type=float, default=0.05)
    parser.add_argument('--diffusion', type=float, default=2.0)
    parser.add_argument('--influence', type=float, default=0.01)
    parser.add_argument('--steps', type=int, default=300)
    parser.add_argument('--output', type=str, default='experiments/lenia_pheromone.png')
    
    args = parser.parse_args()
    
    print(f"Lenia + Pheromone: R={args.R}, mu={args.mu}, sigma={args.sigma}")
    print(f"Pheromone: deposit={args.deposit}, decay={args.decay}, diffusion={args.diffusion}, influence={args.influence}")
    
    result = run_lenia_pheromone(
        shape=tuple(args.shape),
        R_list=args.R,
        mu_list=args.mu,
        sigma_list=args.sigma,
        deposit_rate=args.deposit,
        decay_rate=args.decay,
        diffusion_sigma=args.diffusion,
        pheromone_influence=args.influence,
        steps=args.steps,
        save_timeline=args.output,
    )
    
    print(f"Done: {result['state']} | alive={result['stats']['alive']:.4f} | score={result['stats']['score']:.4f} | {result['time']}s")
    for c in range(3):
        cs = result['channel_stats'][f'ch{"RGB"[c]}']
        print(f"  Ch{'RGB'[c]}: alive={cs['alive']:.4f}, score={cs['score']:.4f}")
    print(f"Timeline: {result['timeline_path']}")
