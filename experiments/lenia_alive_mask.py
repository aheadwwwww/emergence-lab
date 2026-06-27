"""
Lenia with Alive Mask - Integration of Google Isotropic NCA techniques

Key innovations from Google Research:
1. Stochastic updates (50% update rate) - already implemented
2. Alive mask: mature cells (>threshold) with live neighbors survive
3. This creates more robust, self-sustaining patterns

References:
- https://github.com/google-research/self-organizing-systems
- isotropic_nca/blogpost_isonca_single_seed_pytorch.ipynb
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import convolve
from pathlib import Path

def gaussian_kernel(size, sigma):
    """Create a Gaussian kernel"""
    x = np.arange(size) - (size - 1) / 2
    kernel_1d = np.exp(-x**2 / (2 * sigma**2))
    kernel_2d = np.outer(kernel_1d, kernel_1d)
    return kernel_2d / kernel_2d.sum()

def growth_function(u, mu, sigma):
    """Lenia growth function: Gaussian centered at mu"""
    return np.exp(-((u - mu)**2) / (2 * sigma**2)) * 2 - 1

def get_alive_mask(state, maturity_threshold=0.1, neighbor_kernel_size=3):
    """
    Compute alive mask similar to Google Isotropic NCA
    
    A cell is "alive" if:
    1. It's mature (value > threshold), OR
    2. It has mature neighbors
    
    Args:
        state: current state field
        maturity_threshold: minimum value to be considered mature
        neighbor_kernel_size: size of neighborhood to check
    
    Returns:
        boolean mask of alive cells
    """
    # Mature cells
    mature = (state > maturity_threshold).astype(float)
    
    # Count mature neighbors (using simple box kernel)
    neighbor_kernel = np.ones((neighbor_kernel_size, neighbor_kernel_size))
    neighbor_kernel /= neighbor_kernel_size**2  # Normalize
    
    # Average mature neighbors
    neighbor_mature = convolve(mature, neighbor_kernel, mode='wrap')
    
    # Alive if mature neighbors > 0.5 (majority of neighbors are mature)
    alive = neighbor_mature > 0.5 / neighbor_kernel_size**2
    
    return alive

def lenia_with_alive_mask_step(state, kernel, mu, sigma, 
                                update_prob=0.5, 
                                maturity_threshold=0.1,
                                use_alive_mask=True,
                                seed=None):
    """
    Lenia step with stochastic updates and alive mask
    
    Args:
        state: current state field
        kernel: convolution kernel
        mu, sigma: growth parameters
        update_prob: probability each cell updates (default 0.5)
        maturity_threshold: minimum value to be considered mature
        use_alive_mask: whether to apply alive mask
        seed: random seed for reproducibility
    
    Returns:
        new state field, alive_count, mature_count
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Compute alive mask
    if use_alive_mask:
        alive = get_alive_mask(state, maturity_threshold)
    else:
        alive = np.ones_like(state, dtype=bool)
    
    # Convolve with kernel (periodic boundary)
    U = convolve(state, kernel, mode='wrap')
    
    # Growth function
    G = growth_function(U, mu, sigma)
    
    # Stochastic update mask
    update_mask = np.random.random(state.shape) < update_prob
    
    # Combine: only update cells that are both alive and selected
    effective_mask = alive & update_mask
    
    # Apply update
    new_state = state.copy()
    new_state[effective_mask] = np.clip(
        state[effective_mask] + G[effective_mask], 
        0, 1
    )
    
    # Clean up dead cells (set to 0 if not alive)
    if use_alive_mask:
        new_state[~alive] = 0
    
    # Statistics
    alive_count = np.sum(alive)
    mature_count = np.sum(state > maturity_threshold)
    
    return new_state, alive_count, mature_count

def run_lenia_alive_mask_experiment(R=13, mu=0.15, sigma=0.015,
                                     update_probs=[0.3, 0.5, 0.7, 1.0],
                                     maturity_thresholds=[0.05, 0.1, 0.2],
                                     steps=500, size=64, seed=42,
                                     output_dir="output/lenia_alive_mask"):
    """
    Compare Lenia with different update rates and alive mask settings
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    np.random.seed(seed)
    
    # Create kernel
    kernel_size = 2 * R + 1
    kernel = gaussian_kernel(kernel_size, R / 2)
    
    # Initialize with Orbium-like seed
    state_init = np.zeros((size, size))
    center = size // 2
    radius = size // 8
    for i in range(size):
        for j in range(size):
            if (i - center)**2 + (j - center)**2 < radius**2:
                state_init[i, j] = np.random.random() * 0.5 + 0.25
    
    results = {}
    
    fig, axes = plt.subplots(len(update_probs), len(maturity_thresholds), 
                              figsize=(4*len(maturity_thresholds), 4*len(update_probs)))
    
    for i, update_prob in enumerate(update_probs):
        for j, maturity_thresh in enumerate(maturity_thresholds):
            state = state_init.copy()
            alive_history = []
            mature_history = []
            
            for step in range(steps):
                state, alive_count, mature_count = lenia_with_alive_mask_step(
                    state, kernel, mu, sigma, 
                    update_prob=update_prob,
                    maturity_threshold=maturity_thresh,
                    use_alive_mask=True
                )
                alive_history.append(alive_count)
                mature_history.append(mature_count)
            
            # Final state
            ax = axes[i, j] if len(update_probs) > 1 else axes[j]
            ax.imshow(state, cmap='viridis', vmin=0, vmax=1)
            ax.set_title(f'p={update_prob}, thresh={maturity_thresh}\nalive={alive_count:.0f}')
            ax.axis('off')
            
            key = f"p{update_prob}_thresh{maturity_thresh}"
            results[key] = {
                'final_alive': alive_count,
                'final_mature': mature_count,
                'alive_history': alive_history,
                'mature_history': mature_history,
                'final_state': state
            }
    
    plt.suptitle(f'Lenia with Alive Mask (R={R}, μ={mu}, σ={sigma}, steps={steps})', 
                 fontsize=14)
    plt.tight_layout()
    plt.savefig(output_path / 'alive_mask_comparison.png', dpi=150, 
                bbox_inches='tight')
    plt.close()
    
    # Save results
    import json
    summary = {k: {'final_alive': int(v['final_alive']), 
                   'final_mature': int(v['final_mature'])} 
               for k, v in results.items()}
    with open(output_path / 'results.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Results saved to {output_path}")
    return results

def compare_with_without_alive_mask(R=13, mu=0.15, sigma=0.015,
                                     update_prob=0.5,
                                     steps=500, size=64, seed=42):
    """
    Direct comparison: with vs without alive mask
    """
    np.random.seed(seed)
    
    # Create kernel
    kernel_size = 2 * R + 1
    kernel = gaussian_kernel(kernel_size, R / 2)
    
    # Initialize
    state_init = np.zeros((size, size))
    center = size // 2
    radius = size // 8
    for i in range(size):
        for j in range(size):
            if (i - center)**2 + (j - center)**2 < radius**2:
                state_init[i, j] = np.random.random() * 0.5 + 0.25
    
    # Without alive mask
    state_no_mask = state_init.copy()
    alive_no_mask = []
    
    for step in range(steps):
        state_no_mask, ac, mc = lenia_with_alive_mask_step(
            state_no_mask, kernel, mu, sigma,
            update_prob=update_prob,
            use_alive_mask=False
        )
        alive_no_mask.append(ac)
    
    # With alive mask
    state_with_mask = state_init.copy()
    alive_with_mask = []
    
    for step in range(steps):
        state_with_mask, ac, mc = lenia_with_alive_mask_step(
            state_with_mask, kernel, mu, sigma,
            update_prob=update_prob,
            maturity_threshold=0.1,
            use_alive_mask=True
        )
        alive_with_mask.append(ac)
    
    # Plot comparison
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    axes[0].imshow(state_no_mask, cmap='viridis', vmin=0, vmax=1)
    axes[0].set_title(f'Without Alive Mask\nFinal: {alive_no_mask[-1]:.0f} alive')
    axes[0].axis('off')
    
    axes[1].imshow(state_with_mask, cmap='viridis', vmin=0, vmax=1)
    axes[1].set_title(f'With Alive Mask\nFinal: {alive_with_mask[-1]:.0f} alive')
    axes[1].axis('off')
    
    axes[2].plot(alive_no_mask, label='Without Alive Mask', alpha=0.7)
    axes[2].plot(alive_with_mask, label='With Alive Mask', alpha=0.7)
    axes[2].set_xlabel('Step')
    axes[2].set_ylabel('Alive Cells')
    axes[2].set_title('Alive Cells Over Time')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    plt.suptitle(f'Lenia Alive Mask Comparison (p={update_prob}, R={R})', fontsize=14)
    plt.tight_layout()
    plt.savefig('output/lenia_alive_mask/with_vs_without.png', dpi=150, 
                bbox_inches='tight')
    plt.close()
    
    print(f"Without mask: {alive_no_mask[-1]:.0f} alive cells")
    print(f"With mask: {alive_with_mask[-1]:.0f} alive cells")
    
    return state_no_mask, state_with_mask, alive_no_mask, alive_with_mask

if __name__ == '__main__':
    print("="*60)
    print("Lenia with Alive Mask Experiment")
    print("="*60)
    print("\nInspired by Google Isotropic NCA techniques:")
    print("- 50% stochastic update rate")
    print("- Alive mask: mature cells with live neighbors survive")
    print("="*60)
    
    # Run comparison experiment
    print("\n[1] Comparing with vs without alive mask...")
    state_no_mask, state_with_mask, alive_no_mask, alive_with_mask = \
        compare_with_without_alive_mask(steps=300)
    
    # Run parameter sweep
    print("\n[2] Running parameter sweep...")
    results = run_lenia_alive_mask_experiment(
        update_probs=[0.3, 0.5, 0.7, 1.0],
        maturity_thresholds=[0.05, 0.1, 0.2],
        steps=300
    )
    
    print("\nExperiment complete! Check output/lenia_alive_mask/")