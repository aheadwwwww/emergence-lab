"""
Lenia Stochastic Parameter Sweep

Hypothesis: Stochastic updates open up larger parameter regions for stable life.
Let's test multiple (μ, σ) combinations with both synchronous and stochastic updates.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import convolve
import jax
import jax.numpy as jnp
from jax import jit
import os

# Ensure output directory exists
os.makedirs("D:/emergence_experiments", exist_ok=True)


def create_kernel_jax(R, params):
    """Create Lenia kernel using JAX"""
    mu, sigma = params
    
    # Create coordinate grid
    x = jnp.linspace(-R, R, 2*R+1)
    y = jnp.linspace(-R, R, 2*R+1)
    X, Y = jnp.meshgrid(x, y)
    
    # Radial distance
    D = jnp.sqrt(X**2 + Y**2)
    
    # Gaussian-like kernel
    K = jnp.exp(-((D - mu*R)**2) / (2*(sigma*R)**2))
    
    # Normalize
    K = K / jnp.sum(K)
    
    return K


def growth_function_jax(U, mu_g, sigma_g):
    """Growth function for Lenia"""
    return jnp.exp(-((U - mu_g)**2) / (2*sigma_g**2)) * 2 - 1


def lenia_step_jax(A, K, mu_g, sigma_g, update_prob, key):
    """
    Single Lenia step with optional stochastic updates
    
    Args:
        A: Current state
        K: Convolution kernel
        mu_g, sigma_g: Growth function parameters
        update_prob: Probability of updating each cell (1.0 = synchronous)
        key: PRNG key for stochastic updates
    """
    # Convolution
    U = jax.scipy.signal.convolve(A, K, mode='same')
    
    # Growth
    G = growth_function_jax(U, mu_g, sigma_g)
    
    # Update with stochastic mask
    mask = jax.random.uniform(key, A.shape) < update_prob
    A_new = jnp.where(mask, jnp.clip(A + 0.1 * G, 0, 1), A)
    
    return A_new


def run_lenia_stochastic(R=13, mu=0.5, sigma=0.15, mu_g=0.15, sigma_g=0.015,
                         update_prob=0.5, n_steps=500, seed=None):
    """
    Run Lenia simulation with stochastic updates
    """
    if seed is None:
        seed = int(np.random.random() * 1e9)
    
    # Create kernel
    K = create_kernel_jax(R, (mu, sigma))
    
    # Initialize state - Orbium pattern
    size = 64
    A = np.zeros((size, size))
    
    # Orbium pattern
    cx, cy = size//2, size//2
    for i in range(size):
        for j in range(size):
            dx, dy = i - cx, j - cy
            r = np.sqrt(dx**2 + dy**2)
            if r < R * 0.8:
                A[i, j] = np.exp(-((r - R*0.3)**2) / (2*(R*0.15)**2))
    
    A = jnp.array(A)
    K = jnp.array(K)
    key = jax.random.PRNGKey(seed)
    
    # Run simulation
    alive_history = []
    for step in range(n_steps):
        key, subkey = jax.random.split(key)
        A = lenia_step_jax(A, K, mu_g, sigma_g, update_prob, subkey)
        alive_ratio = float(jnp.mean(A > 0.1))
        alive_history.append(alive_ratio)
        
        # Early termination if died
        if alive_ratio < 0.001 and step > 50:
            break
    
    return {
        'final_alive': alive_history[-1],
        'alive_history': alive_history,
        'survived': alive_history[-1] > 0.05
    }


def parameter_sweep():
    """
    Sweep parameter space comparing synchronous vs stochastic updates
    """
    print("=" * 70)
    print("Lenia Stochastic Parameter Sweep")
    print("=" * 70)
    
    # Parameter ranges
    mu_values = np.linspace(0.1, 0.9, 9)
    sigma_values = np.linspace(0.05, 0.3, 6)
    
    # Results storage
    results_sync = np.zeros((len(mu_values), len(sigma_values)))
    results_stoch = np.zeros((len(mu_values), len(sigma_values)))
    
    total = len(mu_values) * len(sigma_values) * 2
    count = 0
    
    print(f"\nSweeping {len(mu_values)} x {len(sigma_values)} = {len(mu_values)*len(sigma_values)} parameter pairs")
    print("Comparing synchronous (p=1.0) vs stochastic (p=0.5) updates\n")
    
    for i, mu in enumerate(mu_values):
        for j, sigma in enumerate(sigma_values):
            # Synchronous
            count += 1
            print(f"\r  Progress: {count}/{total} - μ={mu:.2f}, σ={sigma:.3f} (sync)", end='', flush=True)
            r_sync = run_lenia_stochastic(mu=mu, sigma=sigma, update_prob=1.0, n_steps=300)
            results_sync[i, j] = r_sync['final_alive']
            
            # Stochastic
            count += 1
            print(f"\r  Progress: {count}/{total} - μ={mu:.2f}, σ={sigma:.3f} (stoch)", end='', flush=True)
            r_stoch = run_lenia_stochastic(mu=mu, sigma=sigma, update_prob=0.5, n_steps=300)
            results_stoch[i, j] = r_stoch['final_alive']
    
    print("\n\nGenerating visualization...")
    
    # Visualize
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    
    # Synchronous results
    ax1 = axes[0]
    im1 = ax1.imshow(results_sync, aspect='auto', origin='lower', cmap='hot',
                     extent=[sigma_values[0], sigma_values[-1], mu_values[0], mu_values[-1]])
    ax1.set_xlabel('σ (kernel width)')
    ax1.set_ylabel('μ (kernel center)')
    ax1.set_title('Synchronous Updates (p=1.0)\nFinal Alive Ratio')
    plt.colorbar(im1, ax=ax1, label='Alive ratio')
    
    # Mark Orbium parameter
    ax1.scatter(0.15, 0.5, marker='*', s=200, c='cyan', edgecolor='white', linewidth=2)
    ax1.annotate('Orbium', (0.15, 0.5), xytext=(0.2, 0.55), fontsize=10, color='cyan',
                arrowprops=dict(arrowstyle='->', color='cyan'))
    
    # Stochastic results
    ax2 = axes[1]
    im2 = ax2.imshow(results_stoch, aspect='auto', origin='lower', cmap='hot',
                     extent=[sigma_values[0], sigma_values[-1], mu_values[0], mu_values[-1]])
    ax2.set_xlabel('σ (kernel width)')
    ax2.set_ylabel('μ (kernel center)')
    ax2.set_title('Stochastic Updates (p=0.5)\nFinal Alive Ratio')
    plt.colorbar(im2, ax=ax2, label='Alive ratio')
    
    ax2.scatter(0.15, 0.5, marker='*', s=200, c='cyan', edgecolor='white', linewidth=2)
    
    # Difference
    ax3 = axes[2]
    diff = results_stoch - results_sync
    im3 = ax3.imshow(diff, aspect='auto', origin='lower', cmap='RdBu_r',
                     extent=[sigma_values[0], sigma_values[-1], mu_values[0], mu_values[-1]],
                     vmin=-0.5, vmax=0.5)
    ax3.set_xlabel('σ (kernel width)')
    ax3.set_ylabel('μ (kernel center)')
    ax3.set_title('Stochastic Advantage\n(Stochastic - Synchronous)')
    plt.colorbar(im3, ax=ax3, label='Alive ratio difference')
    
    ax3.scatter(0.15, 0.5, marker='*', s=200, c='cyan', edgecolor='white', linewidth=2)
    
    # Count surviving regions
    sync_surviving = np.sum(results_sync > 0.05)
    stoch_surviving = np.sum(results_stoch > 0.05)
    
    plt.suptitle(f'Surviving parameter regions: Synchronous={sync_surviving}, Stochastic={stoch_surviving}\n'
                 f'Stochastic opens {stoch_surviving - sync_surviving} new stable regions',
                 fontsize=12, y=1.02)
    
    plt.tight_layout()
    save_path = "D:/emergence_experiments/lenia_stochastic_sweep.png"
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\nSaved: {save_path}")
    
    # Analysis
    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)
    print(f"Synchronous (p=1.0): {sync_surviving}/{len(mu_values)*len(sigma_values)} surviving regions")
    print(f"Stochastic (p=0.5): {stoch_surviving}/{len(mu_values)*len(sigma_values)} surviving regions")
    print(f"New regions opened by stochastic updates: {stoch_surviving - sync_surviving}")
    print(f"\nMax alive ratio (sync): {results_sync.max():.3f}")
    print(f"Max alive ratio (stoch): {results_stoch.max():.3f}")
    
    # Find best parameters
    best_sync_idx = np.unravel_index(results_sync.argmax(), results_sync.shape)
    best_stoch_idx = np.unravel_index(results_stoch.argmax(), results_stoch.shape)
    
    print(f"\nBest sync params: μ={mu_values[best_sync_idx[0]]:.2f}, σ={sigma_values[best_sync_idx[1]]:.3f}")
    print(f"Best stoch params: μ={mu_values[best_stoch_idx[0]]:.2f}, σ={sigma_values[best_stoch_idx[1]]:.3f}")
    
    return results_sync, results_stoch


if __name__ == "__main__":
    parameter_sweep()