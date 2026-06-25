"""
Stochastic Lenia - Asynchronous Updates
Inspired by Isotropic NCA's 50% stochastic update rate

Key idea: Instead of all cells updating synchronously, 
each cell has a probability p of updating each step.
This creates more organic, lifelike patterns.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import convolve
from PIL import Image

def gaussian_kernel(size, sigma):
    """Create a Gaussian kernel"""
    x = np.arange(size) - (size - 1) / 2
    kernel_1d = np.exp(-x**2 / (2 * sigma**2))
    kernel_2d = np.outer(kernel_1d, kernel_1d)
    return kernel_2d / kernel_2d.sum()

def growth_function(u, mu, sigma):
    """Lenia growth function: Gaussian centered at mu"""
    return np.exp(-((u - mu)**2) / (2 * sigma**2)) * 2 - 1

def stochastic_lenia_step(state, kernel, mu, sigma, update_prob=0.5, seed=None):
    """
    Lenia step with stochastic updates
    
    Args:
        state: current state field
        kernel: convolution kernel
        mu, sigma: growth parameters
        update_prob: probability each cell updates (default 0.5)
        seed: random seed for reproducibility
    
    Returns:
        new state field
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Convolve with kernel (periodic boundary)
    U = convolve(state, kernel, mode='wrap')
    
    # Growth function
    G = growth_function(U, mu, sigma)
    
    # Stochastic update mask
    update_mask = np.random.random(state.shape) < update_prob
    
    # Only update selected cells
    new_state = state.copy()
    new_state[update_mask] = np.clip(
        state[update_mask] + G[update_mask], 
        0, 1
    )
    
    return new_state

def run_stochastic_lenia(R=13, mu=0.15, sigma=0.015, 
                         update_prob=0.5, steps=200, 
                         size=64, seed=42):
    """Run stochastic Lenia simulation"""
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
    for step in range(steps):
        state = stochastic_lenia_step(
            state, kernel, mu, sigma, 
            update_prob, 
            seed=seed + step if seed else None
        )
        history.append(state.copy())
    
    return np.array(history)

def compare_update_rates():
    """Compare synchronous vs stochastic updates"""
    print("Running Lenia with different update rates...")
    
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    
    update_probs = [1.0, 0.75, 0.5, 0.25]
    
    for idx, update_prob in enumerate(update_probs):
        print(f"  Update prob: {update_prob}")
        
        history = run_stochastic_lenia(
            R=13, mu=0.15, sigma=0.015,
            update_prob=update_prob,
            steps=200, seed=42
        )
        
        # First row: step 50
        axes[0, idx].imshow(history[50], cmap='viridis', vmin=0, vmax=1)
        axes[0, idx].set_title(f'p={update_prob}, step 50')
        axes[0, idx].axis('off')
        
        # Second row: step 200
        axes[1, idx].imshow(history[200], cmap='viridis', vmin=0, vmax=1)
        axes[1, idx].set_title(f'p={update_prob}, step 200')
        axes[1, idx].axis('off')
        
        # Calculate alive ratio
        alive_ratio = (history[200] > 0.1).sum() / history[200].size
        print(f"    Final alive ratio: {alive_ratio:.3f}")
    
    plt.suptitle('Stochastic Lenia: Impact of Update Probability', fontsize=14)
    plt.tight_layout()
    plt.savefig('lenia_stochastic_comparison.png', dpi=150)
    print(f"\nSaved: lenia_stochastic_comparison.png")
    
    return fig

if __name__ == '__main__':
    print("=" * 60)
    print("Stochastic Lenia Experiment")
    print("=" * 60)
    print("\nInspired by Isotropic NCA's stochastic update mechanism")
    print("Testing if asynchronous updates create more organic patterns\n")
    
    compare_update_rates()
    
    print("\n" + "=" * 60)
    print("Key Question:")
    print("Does stochastic updating help or hurt pattern stability?")
    print("=" * 60)
