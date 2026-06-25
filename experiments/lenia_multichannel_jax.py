"""
Lenia Multi-Channel (RGB) — JAX-accelerated

Extends single-channel Lenia to 3-channel (R, G, B) with cross-channel interaction.

Key differences from single-channel:
- 3 parallel grids (channels) with independent parameters
- Cross-channel convolution: each channel receives input from all channels
- Channel mixing matrix controls interactions
- Richer dynamics: patterns emerge from inter-channel feedback

References:
- Chan, B. W.-C. (2019). Lenia - Biology of Artificial Life. Complex Systems, 28(3), 251-286.
- https://github.com/Chakazul/Lenia (official implementation)
- https://chakazul.github.io/lenia.html

Author: Agent (OpenClaw)
Date: 2026-06-25
"""

import jax
import jax.numpy as jnp
from jax import jit, vmap
import numpy as np
from functools import partial
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path
import json, time, argparse, itertools

# ============================================================================
# Core Multi-Channel Lenia Functions
# ============================================================================

def _make_disk_kernel_np(R, kn=0):
    """Create normalized circular kernel using NumPy (pre-JIT).
    
    kn: kernel type
      0 = quad4: (4*r*(1-r))^4
      1 = bump4: exp(4 - 1/(r*(1-r))) (official Lenia default)
      2 = step
    """
    y, x = np.ogrid[-R:R+1, -R:R+1]
    dist = np.sqrt(x*x + y*y) / R
    dist = np.clip(dist, 0, 1)
    
    eps = 1e-8
    r = np.clip(dist, eps, 1 - eps)
    
    if kn == 0:
        kernel = (4 * r * (1 - r))**4
    elif kn == 1:
        kernel = np.exp(4.0 - 1.0 / (r * (1 - r)))
    elif kn == 2:
        q = 0.25
        kernel = ((r >= q) & (r <= 1 - q)).astype(np.float32)
    else:
        kernel = (4 * r * (1 - r))**4
    
    mask = dist <= 1.0
    kernel = kernel * mask
    kernel = kernel / (kernel.sum() + eps)
    return kernel.astype(np.float32)


def make_multi_kernel_fft(shape, Rvals, kn_vals=None):
    """Create multiple kernels (one per channel) with separate FFTs.
    
    Args:
        shape: (H, W) grid shape
        Rvals: list of 3 radii for R, G, B channels
        kn_vals: list of 3 kernel types, default [1, 1, 1]
    
    Returns:
        kernel_ffts: list of 3 FFT kernels
    """
    if kn_vals is None:
        kn_vals = [1, 1, 1]
    
    kernel_ffts = []
    for R, kn in zip(Rvals, kn_vals):
        kernel_2r1 = _make_disk_kernel_np(R, kn)
        h, w = shape
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
        
        kernel_ffts.append(jnp.fft.fft2(jnp.array(kernel_pad)))
    
    return kernel_ffts


@jit
def _multichannel_lenia_step(grids, kernel_ffts, mu_arr, sigma_arr, gn_arr, mixing_matrix, dt=0.1):
    """Single multi-channel Lenia update step with mixing.
    
    Args:
        grids: list of 3 grids [R, G, B], each (H, W)
        kernel_ffts: list of 3 FFT kernels
        mu_arr: [3] growth centers
        sigma_arr: [3] growth widths
        gn_arr: [3] growth function types (0=quad4, 1=gaus, 2=step)
        mixing_matrix: 3x3 weight matrix for cross-channel interaction
            mixing_matrix[i,j] = weight of channel j contributing to channel i
        dt: time step
    
    Returns:
        new_grids: list of 3 updated grids
        potentials: list of 3 potential fields
    """
    eps = 1e-8
    N_CHANNELS = 3
    
    # Compute convolution for each channel
    convs = []
    for ch in range(N_CHANNELS):
        grid_fft = jnp.fft.fft2(grids[ch])
        conv_fft = grid_fft * kernel_ffts[ch]
        conv = jnp.fft.ifft2(conv_fft).real
        convs.append(jnp.clip(conv, 0, 1))
    
    # Mixing: each channel's "effective potential" = weighted sum of all convolutions
    potentials = []
    for ch in range(N_CHANNELS):
        mixed = 0.0
        for j in range(N_CHANNELS):
            mixed += mixing_matrix[ch, j] * convs[j]
        potentials.append(jnp.clip(mixed, 0, 1))
    
    # Apply growth function to each channel
    new_grids = []
    for ch in range(N_CHANNELS):
        n_potential = potentials[ch]
        mu = mu_arr[ch]
        sigma = sigma_arr[ch]
        gn = gn_arr[ch]
        
        # Use lax.switch to dispatch growth function (avoids Python-level branching)
        def growth_quad4(n, m, s):
            return jnp.maximum(0, 1 - ((n - m) / (9 * s + 1e-8))**2)**4 * 2 - 1
        def growth_gaus(n, m, s):
            return jnp.exp(-((n - m)**2) / (2 * s**2 + 1e-8)) * 2 - 1
        def growth_step(n, m, s):
            return jnp.where(jnp.abs(n - m) <= s, 1.0, -1.0)
        
        growth = jax.lax.switch(
            gn,
            [
                lambda n, m, s: growth_quad4(n, m, s),
                lambda n, m, s: growth_gaus(n, m, s),
                lambda n, m, s: growth_step(n, m, s),
            ],
            n_potential, mu, sigma
        )
        
        new_grid = grids[ch] + dt * growth
        new_grid = jnp.clip(new_grid, 0, 1)
        new_grids.append(new_grid)
    
    return new_grids, potentials


# ============================================================================
# Seed Patterns
# ============================================================================

def make_multichannel_seed(shape, mode='orbium', R=20, density=0.3):
    """Create multi-channel seed pattern.
    
    Modes:
      'orbium': single blob in one channel, others empty
      'overlap': overlapping blobs in all channels
      'spread': blobs in different locations per channel
      'gradient': gradient patterns per channel
      'random': independent random noise per channel
    """
    h, w = shape
    grids = []
    
    if mode == 'orbium':
        # Classical orbium in R channel, empty G and B
        grid_r = make_channel_blob(shape, R, cx=w//2, cy=h//2, variant='classic')
        grid_g = make_channel_blob(shape, int(R*0.7), cx=w//3, cy=h//3, variant='ring')
        grid_b = make_channel_blob(shape, int(R*0.5), cx=2*w//3, cy=2*h//3, variant='split')
        
    elif mode == 'overlap':
        rng = np.random.default_rng(42)
        # All three blobs at center with different sizes
        grid_r = make_channel_blob(shape, int(R*0.6), variant='classic')
        grid_g = make_channel_blob(shape, int(R*0.5), variant='ring')
        grid_b = make_channel_blob(shape, int(R*0.7), variant='split')
        
    elif mode == 'spread':
        grid_r = make_channel_blob(shape, int(R*0.5), cx=w//4, cy=h//2, variant='classic')
        grid_g = make_channel_blob(shape, int(R*0.5), cx=w//2, cy=h//4, variant='ring')
        grid_b = make_channel_blob(shape, int(R*0.5), cx=3*w//4, cy=3*h//4, variant='split')
        
    elif mode == 'random':
        rng = np.random.default_rng(42)
        radius = int(min(shape) // 6)
        grid_r = make_random_blob(shape, radius, density * rng.uniform(0.5, 1.0), rng)
        grid_g = make_random_blob(shape, int(radius*0.8), density * rng.uniform(0.5, 1.0), rng)
        grid_b = make_random_blob(shape, int(radius*1.2), density * rng.uniform(0.5, 1.0), rng)
        
    elif mode == 'gradient':
        yy, xx = np.mgrid[0:h, 0:w]
        # RGB phase-shifted gradients
        grid_r = np.sin(xx * 0.1 + yy * 0.05) * 0.3 + 0.5
        grid_g = np.sin(xx * 0.05 + yy * 0.1 + 1.0) * 0.3 + 0.5
        grid_b = np.sin(xx * 0.08 - yy * 0.08 + 2.0) * 0.3 + 0.5
        grid_r = np.clip(grid_r, 0, 1).astype(np.float32)
        grid_g = np.clip(grid_g, 0, 1).astype(np.float32)
        grid_b = np.clip(grid_b, 0, 1).astype(np.float32)
        
    else:
        grid_r = make_channel_blob(shape, R)
        grid_g = make_channel_blob(shape, int(R*0.7))
        grid_b = make_channel_blob(shape, int(R*0.5))
    
    return [grid_r, grid_g, grid_b]


def make_channel_blob(shape, radius, cx=None, cy=None, variant='classic'):
    """Create a single-channel blob pattern."""
    h, w = shape
    if cx is None: cx = w // 2
    if cy is None: cy = h // 2
    
    grid = np.zeros(shape, dtype=np.float32)
    r_orb = radius
    
    y_coords, x_coords = np.ogrid[-r_orb:r_orb+1, -r_orb:r_orb+1]
    dist = np.sqrt(x_coords**2 + y_coords**2)
    
    if variant == 'classic':
        cells = np.exp(-dist**2 / (2 * (r_orb * 0.7)**2))
        cells *= (1 + 0.3 * (1 - x_coords / (r_orb + 1)))
    elif variant == 'ring':
        cells = np.exp(-((dist - r_orb * 0.6)**2) / (2 * (r_orb * 0.15)**2))
    elif variant == 'split':
        cells = np.exp(-dist**2 / (2 * (r_orb * 0.6)**2))
        cells *= (1 + 0.5 * np.sin(x_coords / (r_orb + 1) * 3))
    elif variant == 'gaussian':
        cells = np.exp(-dist**2 / (2 * (r_orb * 0.4)**2))
    else:
        cells = np.exp(-dist**2 / (2 * (r_orb * 0.7)**2))
    
    cells = np.clip(cells, 0, 1)
    
    y_start = max(0, cy - r_orb)
    x_start = max(0, cx - r_orb)
    y_end = min(h, cy + r_orb + 1)
    x_end = min(w, cx + r_orb + 1)
    
    k_y_start = y_start - (cy - r_orb)
    k_x_start = x_start - (cx - r_orb)
    k_y_end = k_y_start + (y_end - y_start)
    k_x_end = k_x_start + (x_end - x_start)
    
    grid[y_start:y_end, x_start:x_end] = cells[k_y_start:k_y_end, k_x_start:k_x_end]
    return grid


def make_random_blob(shape, radius, density=0.3, rng=None):
    """Create a random noise blob in one channel."""
    if rng is None:
        rng = np.random.default_rng()
    
    grid = np.zeros(shape, dtype=np.float32)
    h, w = shape
    cy, cx = h // 2, w // 2
    
    y_coords, x_coords = np.ogrid[-radius:radius+1, -radius:radius+1]
    dist = np.sqrt(x_coords**2 + y_coords**2) / radius
    
    noise = rng.uniform(0, 1, (2*radius+1, 2*radius+1))
    mask = dist <= 1.0
    blob = noise * mask * density
    
    y_start = max(0, cy - radius)
    x_start = max(0, cx - radius)
    y_end = min(h, cy + radius + 1)
    x_end = min(w, cx + radius + 1)
    
    k_y_start = y_start - (cy - radius)
    k_x_start = x_start - (cx - radius)
    k_y_end = k_y_start + (y_end - y_start)
    k_x_end = k_x_start + (x_end - x_start)
    
    grid[y_start:y_end, x_start:x_end] = blob[k_y_start:k_y_end, k_x_start:k_x_end]
    return grid


# ============================================================================
# Analysis
# ============================================================================

def analyze_multichannel_state(grids):
    """Analyze multi-channel state: alive%, entropy, edge density per channel + composite."""
    eps = 1e-8
    N_CHANNELS = len(grids)
    
    channel_stats = []
    for ch in range(N_CHANNELS):
        grid = grids[ch]
        
        alive = float(jnp.mean(grid > 0.01))
        
        hist, _ = jnp.histogram(grid, bins=20, range=(0, 1))
        probs = hist / (hist.sum() + eps)
        entropy = -jnp.sum(probs * jnp.log(probs + eps))
        entropy_norm = float(entropy / jnp.log(20.0))
        
        gy = grid[1:, :] - grid[:-1, :]
        gx = grid[:, 1:] - grid[:, :-1]
        edge = float(jnp.mean(jnp.abs(gy)) + jnp.mean(jnp.abs(gx)))
        edge_density = edge / 2.0
        
        channel_stats.append({
            'alive': round(alive, 4),
            'entropy': round(entropy_norm, 4),
            'edge_density': round(edge_density, 4),
        })
    
    # Composite stats
    composite = jnp.stack(grids, axis=-1)
    composite_flat = composite.reshape(-1, N_CHANNELS)
    
    # Channel correlation (mean pairwise abs correlation)
    corr_sum = 0.0
    count = 0
    for i in range(N_CHANNELS):
        for j in range(i+1, N_CHANNELS):
            gi = composite_flat[:, i]
            gj = composite_flat[:, j]
            gi_centered = gi - jnp.mean(gi)
            gj_centered = gj - jnp.mean(gj)
            cov = jnp.mean(gi_centered * gj_centered)
            std_i = jnp.std(gi)
            std_j = jnp.std(gj)
            corr = float(cov / (std_i * std_j + eps))
            corr_sum += abs(corr)
            count += 1
    mean_corr = corr_sum / max(count, 1)
    
    # RGB diversity (how different are the channels)
    rgb_values = jnp.array([float(jnp.mean(g)) for g in grids])
    diversity = float(jnp.std(rgb_values))
    
    # Score: prefer alive, high entropy, good edge, low correlation (diverse channels)
    mean_alive = np.mean([s['alive'] for s in channel_stats])
    mean_entropy = np.mean([s['entropy'] for s in channel_stats])
    mean_edge = np.mean([s['edge_density'] for s in channel_stats])
    
    score = mean_alive * 0.25 + mean_entropy * 0.25 + min(mean_edge * 3, 1.0) * 0.15 + \
            (1 - mean_corr) * 0.2 + diversity * 0.15
    
    return {
        'channels': channel_stats,
        'composite': {
            'mean_alive': round(mean_alive, 4),
            'mean_entropy': round(mean_entropy, 4),
            'mean_edge': round(mean_edge, 4),
            'channel_correlation': round(mean_corr, 4),
            'rgb_diversity': round(diversity, 4),
            'score': round(float(score), 4),
        }
    }


# ============================================================================
# Visualization
# ============================================================================

def render_multichannel_timeline(grids_list, filename='lenia_multi_timeline.png', step_labels=None):
    """Render timeline of multi-channel states (composite RGB + individual channels)."""
    n = len(grids_list)
    cols = min(n, 5)
    rows = (n + cols - 1) // cols
    
    # 4 rows: composite RGB + R + G + B
    fig, axes = plt.subplots(4, cols, figsize=(cols * 3, 4 * 3.2))
    if cols == 1:
        axes = axes.reshape(4, 1)
    
    for i in range(cols):
        if i < n:
            grids = grids_list[i]
            # Composite RGB
            rgb = np.stack([np.array(g) for g in grids], axis=-1)
            axes[0, i].imshow(rgb, interpolation='bilinear')
            
            # Individual channels
            cmaps = ['Reds', 'Greens', 'Blues']
            for ch in range(3):
                axes[ch + 1, i].imshow(np.array(grids[ch]), cmap=cmaps[ch], vmin=0, vmax=1, interpolation='bilinear')
            
            label = step_labels[i] if step_labels and i < len(step_labels) else f'step={i * 50}'
            axes[0, i].set_title(label, fontsize=9, color='white')
        
        for row in range(4):
            axes[row, i].axis('off')
    
    # Row labels
    row_labels = ['RGB', 'R', 'G', 'B']
    for row in range(4):
        col = 0
        axes[row, col].set_ylabel(row_labels[row], fontsize=10, color='white', weight='bold')
    
    plt.tight_layout(pad=0.5)
    fig.savefig(filename, dpi=150, bbox_inches='tight', facecolor='black')
    plt.close(fig)
    print(f"[OK] Multi-channel timeline saved: {filename}")
    return filename


def render_composite(grids, filename='lenia_multi_composite.png'):
    """Render a single composite RGB image from multi-channel state."""
    grids_np = [np.array(g) for g in grids]
    rgb = np.stack(grids_np, axis=-1)
    
    fig, axes = plt.subplots(2, 2, figsize=(10, 10))
    
    axes[0, 0].imshow(rgb, interpolation='bilinear')
    axes[0, 0].set_title('RGB Composite', fontsize=12)
    
    for ch, (ax, cmap, label) in enumerate(zip(
        [axes[0, 1], axes[1, 0], axes[1, 1]],
        ['Reds', 'Greens', 'Blues'],
        ['R Channel', 'G Channel', 'B Channel']
    )):
        ax.imshow(grids_np[ch], cmap=cmap, vmin=0, vmax=1, interpolation='bilinear')
        ax.set_title(label, fontsize=12)
    
    for ax in axes.flat:
        ax.axis('off')
    
    plt.tight_layout()
    fig.savefig(filename, dpi=150, bbox_inches='tight', facecolor='black')
    plt.close(fig)
    print(f"[OK] Composite saved: {filename}")
    return filename


# ============================================================================
# Main Simulation
# ============================================================================

def run_multichannel_lenia(
    shape=(256, 256),
    Rvals=None,
    mu_vals=None,
    sigma_vals=None,
    kn_vals=None,
    gn_vals=None,
    mixing_matrix=None,
    steps=500,
    dt=0.1,
    init='orbium',
    seed_density=0.3,
    record_every=50,
    save_timeline=None,
    save_composite=None,
    verbose=True,
):
    """Run multi-channel Lenia simulation.
    
    Args:
        shape: (H, W) grid shape
        Rvals: list of 3 radii (default [20, 17, 14])
        mu_vals: list of 3 growth centers (default [0.15, 0.14, 0.13])
        sigma_vals: list of 3 growth widths (default [0.015, 0.012, 0.010])
        kn_vals: list of 3 kernel types (default [1, 1, 1])
        gn_vals: list of 3 growth functions (default [1, 1, 1])
        mixing_matrix: 3x3 cross-channel weights (default identity + weak off-diagonal)
        steps: number of simulation steps
        dt: time step size
        init: seed pattern mode
        record_every: record state every N steps
        save_timeline: output path for timeline image
        save_composite: output path for final composite image
    
    Returns:
        dict with simulation results
    """
    N_CHANNELS = 3
    
    if Rvals is None:
        Rvals = [20, 17, 14]
    if mu_vals is None:
        mu_vals = [0.15, 0.14, 0.13]
    if sigma_vals is None:
        sigma_vals = [0.015, 0.012, 0.010]
    if kn_vals is None:
        kn_vals = [1, 1, 1]
    if gn_vals is None:
        gn_vals = [1, 1, 1]
    if mixing_matrix is None:
        # Default: strong self (identity) + weak cross (0.3)
        mixing_matrix = jnp.array([
            [1.0, 0.3, 0.3],
            [0.3, 1.0, 0.3],
            [0.3, 0.3, 1.0],
        ], dtype=jnp.float32)
    
    params_mu = jnp.array(mu_vals, dtype=jnp.float32)
    params_sigma = jnp.array(sigma_vals, dtype=jnp.float32)
    params_gn = jnp.array(gn_vals, dtype=jnp.int32)
    
    if verbose:
        print(f"Multi-channel Lenia: {shape[0]}x{shape[1]}")
        print(f"  R={Rvals}, mu={mu_vals}, sigma={sigma_vals}")
        print(f"  kn={kn_vals}, gn={gn_vals}")
        print(f"  Mixing matrix:\n{np.array(mixing_matrix)}")
        print(f"  Init: {init}, Steps: {steps}, dt={dt}")
    
    # Initialize grids
    grids_np = make_multichannel_seed(shape, mode=init, R=max(Rvals), density=seed_density)
    grids = [jnp.array(g) for g in grids_np]
    
    # Prepare kernels
    kernel_ffts = make_multi_kernel_fft(shape, Rvals, kn_vals)
    
    # Run simulation
    recorded_grids = [[g.copy() for g in grids]]
    t0 = time.time()
    
    for step in range(steps):
        grids, potentials = _multichannel_lenia_step(
            grids, kernel_ffts, params_mu, params_sigma, params_gn, mixing_matrix, dt
        )
        
        if (step + 1) % record_every == 0:
            recorded_grids.append([g.copy() for g in grids])
        
        if verbose and (step + 1) % (steps // 10) == 0:
            stats = analyze_multichannel_state(grids)
            c = stats['composite']
            elapsed = time.time() - t0
            print(f"  step {step+1}/{steps} | alive={c['mean_alive']:.3f} score={c['score']:.3f} corr={c['channel_correlation']:.3f} | {elapsed:.1f}s")
    
    elapsed = time.time() - t0
    final_stats = analyze_multichannel_state(grids)
    c = final_stats['composite']
    
    if verbose:
        print(f"  done in {elapsed:.1f}s | score={c['score']:.3f} alive={c['mean_alive']:.3f}")
    
    result = {
        'params': {
            'shape': list(shape),
            'Rvals': Rvals,
            'mu_vals': mu_vals,
            'sigma_vals': sigma_vals,
            'kn_vals': kn_vals,
            'gn_vals': gn_vals,
            'mixing_matrix': np.array(mixing_matrix).tolist(),
            'steps': steps,
            'dt': dt,
            'init': init,
        },
        'stats': final_stats,
        'time': round(elapsed, 2),
        'recorded_grids': recorded_grids,
    }
    
    if save_timeline:
        step_labels = [f'step={i*record_every}' for i in range(len(recorded_grids))]
        result['timeline_path'] = render_multichannel_timeline(
            recorded_grids, save_timeline, step_labels
        )
    
    if save_composite:
        result['composite_path'] = render_composite(grids, save_composite)
    
    return result


# ============================================================================
# Parameter Sweep (Multi-Channel)
# ============================================================================

def sweep_multi_lenia(shape=(192, 192), steps=300, n_samples=16, seed_mode='spread'):
    """Sweep over mixing matrix strengths to find interesting dynamics.
    
    Explores the effects of cross-channel coupling.
    """
    # Sweep over mixing strength alpha (cross-channel weight)
    alphas = np.linspace(0.0, 1.0, n_samples)
    
    results = []
    t0 = time.time()
    
    for i, alpha in enumerate(alphas):
        mixing = np.array([
            [1.0, alpha, alpha],
            [alpha, 1.0, alpha],
            [alpha, alpha, 1.0],
        ], dtype=np.float32)
        
        result = run_multichannel_lenia(
            shape=shape,
            steps=steps,
            mixing_matrix=jnp.array(mixing),
            init=seed_mode,
            record_every=100,
            verbose=False,
        )
        
        entry = {
            'alpha': round(float(alpha), 4),
            'mean_alive': result['stats']['composite']['mean_alive'],
            'mean_entropy': result['stats']['composite']['mean_entropy'],
            'mean_edge': result['stats']['composite']['mean_edge'],
            'channel_correlation': result['stats']['composite']['channel_correlation'],
            'rgb_diversity': result['stats']['composite']['rgb_diversity'],
            'score': result['stats']['composite']['score'],
        }
        results.append(entry)
        
        elapsed = time.time() - t0
        print(f"  [{i+1}/{n_samples}] alpha={alpha:.2f} → score={entry['score']:.3f} alive={entry['mean_alive']:.3f} | {elapsed:.1f}s")
    
    elapsed = time.time() - t0
    print(f"\nSweep done: {len(results)} runs in {elapsed:.1f}s")
    
    # Best result
    best = max(results, key=lambda r: r['score'])
    print(f"  Best: alpha={best['alpha']:.2f}, score={best['score']:.4f}, alive={best['mean_alive']:.4f}")
    
    return results


# ============================================================================
# CLI
# ============================================================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Multi-channel Lenia (RGB) — JAX')
    parser.add_argument('--mode', default='single', choices=['single', 'sweep', 'explore'],
                        help='Run mode')
    parser.add_argument('--shape', type=int, nargs=2, default=[256, 256],
                        help='Grid size (default: 256 256)')
    parser.add_argument('--R', type=int, nargs=3, default=[20, 17, 14],
                        help='Kernel radii for R G B (default: 20 17 14)')
    parser.add_argument('--mu', type=float, nargs=3, default=[0.15, 0.14, 0.13],
                        help='Growth centers for R G B')
    parser.add_argument('--sigma', type=float, nargs=3, default=[0.015, 0.012, 0.010],
                        help='Growth widths for R G B')
    parser.add_argument('--init', default='spread',
                        choices=['orbium', 'overlap', 'spread', 'random', 'gradient'],
                        help='Seed pattern mode')
    parser.add_argument('--alpha', type=float, default=0.3,
                        help='Cross-channel mixing strength (default: 0.3)')
    parser.add_argument('--steps', type=int, default=500, help='Simulation steps')
    parser.add_argument('--dt', type=float, default=0.1, help='Time step')
    parser.add_argument('--output', default=None, help='Output prefix for images')
    parser.add_argument('--samples', type=int, default=16, help='Sweep samples')
    
    args = parser.parse_args()
    
    output_prefix = args.output or f'experiments/lenia_multi_{args.init}'
    
    if args.mode == 'sweep':
        # Sweep over mixing alpha
        results = sweep_multi_lenia(
            shape=tuple(args.shape),
            steps=args.steps,
            n_samples=args.samples,
            seed_mode=args.init,
        )
        
        out_json = f'{output_prefix}_sweep.json'
        with open(out_json, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"[OK] Results saved: {out_json}")
        
        # Plot sweep results
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        alphas = [r['alpha'] for r in results]
        
        axes[0, 0].plot(alphas, [r['mean_alive'] for r in results], '-o', color='cyan')
        axes[0, 0].set_xlabel('Alpha (cross-channel weight)')
        axes[0, 0].set_ylabel('Mean Alive')
        axes[0, 0].grid(True, alpha=0.3)
        
        axes[0, 1].plot(alphas, [r['score'] for r in results], '-o', color='lime')
        axes[0, 1].set_xlabel('Alpha (cross-channel weight)')
        axes[0, 1].set_ylabel('Score')
        axes[0, 1].grid(True, alpha=0.3)
        
        axes[1, 0].plot(alphas, [r['channel_correlation'] for r in results], '-o', color='orange')
        axes[1, 0].set_xlabel('Alpha (cross-channel weight)')
        axes[1, 0].set_ylabel('Channel Correlation')
        axes[1, 0].grid(True, alpha=0.3)
        
        axes[1, 1].plot(alphas, [r['rgb_diversity'] for r in results], '-o', color='magenta')
        axes[1, 1].set_xlabel('Alpha (cross-channel weight)')
        axes[1, 1].set_ylabel('RGB Diversity')
        axes[1, 1].grid(True, alpha=0.3)
        
        fig.suptitle(f'Multi-Channel Lenia: Mixing Strength Sweep\n{args.shape[0]}x{args.shape[1]}', fontsize=14)
        plt.tight_layout()
        fig.savefig(f'{output_prefix}_sweep.png', dpi=150, bbox_inches='tight', facecolor='#111122')
        plt.close(fig)
        print(f"[OK] Sweep plot: {output_prefix}_sweep.png")
        
    elif args.mode == 'explore':
        # Multiple preset runs to explore dynamics
        presets = [
            {'name': 'identity', 'mix': [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]},
            {'name': 'mild_cross', 'mix': [[1.0, 0.3, 0.3], [0.3, 1.0, 0.3], [0.3, 0.3, 1.0]]},
            {'name': 'strong_cross', 'mix': [[1.0, 0.7, 0.7], [0.7, 1.0, 0.7], [0.7, 0.7, 1.0]]},
            {'name': 'cyclic', 'mix': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]]},
            {'name': 'inhibitory', 'mix': [[1.0, -0.3, -0.3], [-0.3, 1.0, -0.3], [-0.3, -0.3, 1.0]]},
        ]
        
        for preset in presets:
            print(f"\n{'='*60}")
            print(f"Preset: {preset['name']}")
            print(f"Mix: {preset['mix']}")
            
            result = run_multichannel_lenia(
                shape=tuple(args.shape),
                Rvals=list(args.R),
                mu_vals=list(args.mu),
                sigma_vals=list(args.sigma),
                steps=args.steps,
                dt=args.dt,
                init=args.init,
                mixing_matrix=jnp.array(preset['mix'], dtype=jnp.float32),
                record_every=100,
                save_timeline=f'{output_prefix}_{preset["name"]}_timeline.png',
                save_composite=f'{output_prefix}_{preset["name"]}_final.png',
                verbose=True,
            )
            
            c = result['stats']['composite']
            print(f"  Final: score={c['score']:.4f} alive={c['mean_alive']:.4f} corr={c['channel_correlation']:.4f}")
    
    else:  # single
        mixing = np.array([
            [1.0, args.alpha, args.alpha],
            [args.alpha, 1.0, args.alpha],
            [args.alpha, args.alpha, 1.0],
        ], dtype=np.float32)
        
        print(f"Single run — mixing matrix:\n{mixing}")
        
        result = run_multichannel_lenia(
            shape=tuple(args.shape),
            Rvals=list(args.R),
            mu_vals=list(args.mu),
            sigma_vals=list(args.sigma),
            steps=args.steps,
            dt=args.dt,
            init=args.init,
            mixing_matrix=jnp.array(mixing, dtype=jnp.float32),
            record_every=50,
            save_timeline=f'{output_prefix}_timeline.png',
            save_composite=f'{output_prefix}_final.png',
            verbose=True,
        )
        
        c = result['stats']['composite']
        print(f"\nFinal: score={c['score']:.4f} alive={c['mean_alive']:.4f}")
        print(f"  channel_corr={c['channel_correlation']:.4f} diversity={c['rgb_diversity']:.4f}")
        print(f"  time={result['time']}s")
