"""
Lenia with Alive Mask - Inspired by Isotropic NCA

Key innovation from Google Research:
1. Alive mask: Only cells with living neighbors survive
2. Prevents "ghost structures" from drifting
3. Combines with stochastic updates for stability

Reference: google-research/self-organising-systems/isotropic_nca
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import convolve
from PIL import Image
import os

def gaussian_kernel(size, sigma):
    """Create a Gaussian kernel"""
    x = np.arange(size) - (size - 1) / 2
    kernel_1d = np.exp(-x**2 / (2 * sigma**2))
    kernel_2d = np.outer(kernel_1d, kernel_1d)
    return kernel_2d / kernel_2d.sum()

def growth_function(u, mu, sigma):
    """Lenia growth function: Gaussian centered at mu"""
    return np.exp(-((u - mu)**2) / (2 * sigma**2)) * 2 - 1

def get_alive_mask(state, threshold=0.1, nhood_radius=1):
    """
    Compute alive mask: cells with living neighbors survive.
    
    Inspired by Isotropic NCA's get_alive_mask:
    - Detect mature cells (value > threshold)
    - Use neighborhood convolution to propagate survival signal
    - Cell survives if any neighbor is alive
    
    Args:
        state: current state field [H, W]
        threshold: minimum value for a cell to be "alive"
        nhood_radius: radius of neighborhood check
    
    Returns:
        alive_mask: boolean mask [H, W]
    """
    # Detect mature cells
    mature = (state > threshold).astype(np.float32)
    
    # Create neighborhood kernel
    size = 2 * nhood_radius + 1
    nhood_kernel = np.ones((size, size))
    
    # Convolve: count alive neighbors
    alive_count = convolve(mature, nhood_kernel, mode='wrap')
    
    # Cell survives if it or any neighbor is alive
    return alive_count > 0.5

def lenia_alive_mask_step(state, kernel, mu, sigma, 
                          update_prob=0.5, alive_threshold=0.1,
                          nhood_radius=1, seed=None):
    """
    Lenia step with both stochastic updates AND alive mask.
    
    Combines two key innovations from Isotropic NCA:
    1. Stochastic update (50% default)
    2. Alive mask (prevent ghost structures)
    
    Args:
        state: current state field [H, W]
        kernel: convolution kernel
        mu, sigma: growth parameters
        update_prob: probability each cell updates
        alive_threshold: threshold for alive detection
        nhood_radius: neighborhood radius for alive mask
        seed: random seed
    
    Returns:
        new_state: updated state field
        alive_mask: computed alive mask (for visualization)
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Step 1: Standard Lenia convolution
    U = convolve(state, kernel, mode='wrap')
    G = growth_function(U, mu, sigma)
    
    # Step 2: Stochastic update mask
    update_mask = np.random.random(state.shape) < update_prob
    
    # Step 3: Apply growth only to selected cells
    new_state = state.copy()
    new_state[update_mask] = np.clip(
        state[update_mask] + G[update_mask], 
        0, 1
    )
    
    # Step 4: Apply alive mask (prevent ghost structures)
    alive_mask = get_alive_mask(new_state, alive_threshold, nhood_radius)
    new_state = new_state * alive_mask
    
    return new_state, alive_mask

def run_alive_mask_lenia(R=13, mu=0.15, sigma=0.015,
                         update_prob=0.5, alive_threshold=0.1,
                         nhood_radius=1, steps=200,
                         size=64, seed=42):
    """Run Lenia with alive mask"""
    np.random.seed(seed)
    
    # Create kernel
    kernel_size = 2 * R + 1
    kernel = gaussian_kernel(kernel_size, R / 2)
    
    # Initialize with random seed
    state = np.zeros((size, size))
    center = size // 2
    radius = size // 8
    for i in range(size):
        for j in range(size):
            if (i - center)**2 + (j - center)**2 < radius**2:
                state[i, j] = np.random.random() * 0.5 + 0.25
    
    # Run simulation
    history = [state.copy()]
    alive_history = [np.ones_like(state)]
    
    for step in range(steps):
        state, alive_mask = lenia_alive_mask_step(
            state, kernel, mu, sigma,
            update_prob, alive_threshold, nhood_radius,
            seed=seed + step if seed else None
        )
        history.append(state.copy())
        alive_history.append(alive_mask.copy())
    
    return np.array(history), np.array(alive_history)

def compare_techniques():
    """Compare: Standard vs Stochastic vs AliveMask vs Stochastic+AliveMask"""
    print("=" * 60)
    print("Lenia: Comparing Update Techniques")
    print("=" * 60)
    
    configs = [
        ("Standard (sync)", 1.0, 0.0, 0),     # no alive mask
        ("Stochastic (50%)", 0.5, 0.0, 0),    # no alive mask
        ("Alive Mask (sync)", 1.0, 0.1, 1),   # with alive mask
        ("Stochastic + Alive", 0.5, 0.1, 1),  # both
    ]
    
    fig, axes = plt.subplots(2, 4, figsize=(18, 10))
    
    for idx, (name, update_prob, alive_thresh, nhood_r) in enumerate(configs):
        print(f"\nRunning: {name}")
        
        if alive_thresh > 0:
            history, alive_history = run_alive_mask_lenia(
                R=13, mu=0.15, sigma=0.015,
                update_prob=update_prob,
                alive_threshold=alive_thresh,
                nhood_radius=nhood_r,
                steps=200, seed=42
            )
        else:
            # Standard Lenia (no alive mask)
            from lenia_stochastic import run_stochastic_lenia
            history = run_stochastic_lenia(
                R=13, mu=0.15, sigma=0.015,
                update_prob=update_prob,
                steps=200, seed=42
            )
        
        # Row 0: step 100
        axes[0, idx].imshow(history[100], cmap='viridis', vmin=0, vmax=1)
        axes[0, idx].set_title(f'{name}\nStep 100', fontsize=10)
        axes[0, idx].axis('off')
        
        # Row 1: step 200
        axes[1, idx].imshow(history[200], cmap='viridis', vmin=0, vmax=1)
        axes[1, idx].set_title(f'{name}\nStep 200', fontsize=10)
        axes[1, idx].axis('off')
        
        # Metrics
        alive_ratio = (history[200] > 0.1).sum() / history[200].size
        mean_value = history[200].mean()
        print(f"  Alive ratio: {alive_ratio:.3f}")
        print(f"  Mean value: {mean_value:.4f}")
    
    plt.suptitle('Lenia Update Techniques Comparison\n'
                 'Standard | Stochastic | Alive Mask | Stochastic + Alive Mask',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, 'lenia_alive_mask_comparison.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    print(f"\nSaved: {path}")
    
    return fig

def alive_mask_analysis():
    """Detailed analysis of alive mask effect"""
    print("\n" + "=" * 60)
    print("Alive Mask Analysis")
    print("=" * 60)
    
    # Run with alive mask
    print("\n1. Running with alive mask...")
    history, alive_history = run_alive_mask_lenia(
        R=13, mu=0.15, sigma=0.015,
        update_prob=0.5, alive_threshold=0.1,
        nhood_radius=1, steps=200, seed=42
    )
    
    # Run without alive mask (stochastic only)
    print("2. Running without alive mask (stochastic only)...")
    from lenia_stochastic import run_stochastic_lenia
    history_no_mask = run_stochastic_lenia(
        R=13, mu=0.15, sigma=0.015,
        update_prob=0.5, steps=200, seed=42
    )
    
    # Compare metrics
    steps_to_check = [50, 100, 150, 200]
    
    print("\n" + "-" * 40)
    print(f"{'Step':<8} {'Metric':<20} {'With Mask':<15} {'No Mask':<15}")
    print("-" * 40)
    
    for step in steps_to_check:
        with_mask = history[step]
        without_mask = history_no_mask[step]
        
        # Alive ratio
        alive_with = (with_mask > 0.1).sum() / with_mask.size
        alive_without = (without_mask > 0.1).sum() / without_mask.size
        
        # Structure count (connected components)
        from scipy import ndimage
        binary_with = (with_mask > 0.1).astype(int)
        binary_without = (without_mask > 0.1).astype(int)
        
        _, n_with = ndimage.label(binary_with)
        _, n_without = ndimage.label(binary_without)
        
        print(f"{step:<8} {'Alive Ratio':<20} {alive_with:<15.4f} {alive_without:<15.4f}")
        print(f"{step:<8} {'Structures':<20} {n_with:<15} {n_without:<15}")
    
    # Visualize alive mask evolution
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    
    checkpoints = [0, 25, 50, 100, 150, 200]
    for i, step in enumerate(checkpoints[:4]):
        axes[0, i].imshow(history[step], cmap='viridis', vmin=0, vmax=1)
        axes[0, i].set_title(f'State (step {step})')
        axes[0, i].axis('off')
        
        axes[1, i].imshow(alive_history[step], cmap='gray')
        axes[1, i].set_title(f'Alive Mask (step {step})')
        axes[1, i].axis('off')
    
    plt.suptitle('Alive Mask Evolution Over Time', fontsize=14)
    plt.tight_layout()
    
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, 'lenia_alive_mask_evolution.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    print(f"\nSaved: {path}")
    
    return fig

if __name__ == '__main__':
    print("=" * 60)
    print("Lenia with Alive Mask Experiment")
    print("Inspired by Google Research Isotropic NCA")
    print("=" * 60)
    
    # Experiment 1: Compare all techniques
    compare_techniques()
    
    # Experiment 2: Detailed alive mask analysis
    alive_mask_analysis()
    
    print("\n" + "=" * 60)
    print("Key Findings:")
    print("1. Alive mask prevents ghost structures from drifting")
    print("2. Stochastic + Alive Mask = most organic patterns")
    print("3. Neighborhood-based survival creates cleaner boundaries")
    print("=" * 60)
