"""
Self-Replicating Lenia Experiment

Combining insights from Self-Replicating Neural Networks with Lenia:
- Can a Lenia pattern "remember" its kernel parameters?
- Can we create a pattern that encodes its own shape?

Idea: Train a pattern to output its own kernel parameters through
the dynamics of the field itself (without neural networks).

Approach:
1. Create a Lenia pattern with learnable kernel parameters
2. Add a "memory region" that encodes kernel parameters
3. The pattern evolves, and the memory region updates to reflect
   the kernel parameters that would sustain the pattern

This is simpler than Self-Rep NN but tests the same concept:
can a dynamical system encode its own parameters?
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import convolve
from pathlib import Path
import json


def make_gaussian_kernel(R, mu, sigma):
    """Create a Gaussian ring kernel for Lenia."""
    size = 2 * R + 1
    y, x = np.ogrid[-R:R+1, -R:R+1]
    r = np.sqrt(x**2 + y**2)
    
    # Gaussian ring
    kernel = np.exp(-((r - R * mu)**2) / (2 * (R * sigma)**2))
    kernel[r > R] = 0
    kernel /= kernel.sum()
    
    return kernel


def lenia_step(grid, kernel, mu=0.15, sigma=0.015, dt=0.1):
    """Single Lenia update step."""
    # Convolution
    U = convolve(grid, kernel, mode='wrap')
    
    # Growth function
    growth = np.exp(-((U - mu)**2) / (2 * sigma**2)) * 2 - 1
    
    # Update
    new_grid = np.clip(grid + dt * growth, 0, 1)
    
    return new_grid, U


def make_orbium(shape, R=13):
    """Create the classic Orbium pattern."""
    h, w = shape
    grid = np.zeros(shape)
    
    # Orbium is a smooth, rounded creature
    cy, cx = h // 2, w // 2
    
    # Create smooth disk-like shape
    y, x = np.ogrid[:h, :w]
    r = np.sqrt((x - cx)**2 + (y - cy)**2)
    
    # Orbium shape: smooth gradient
    inner_r = R * 0.3
    outer_r = R * 0.7
    
    # Smooth falloff
    dist = (r - inner_r) / (outer_r - inner_r)
    dist = np.clip(dist, 0, 1)
    
    # Main body
    mask = r <= outer_r
    grid[mask] = np.cos(dist[mask] * np.pi / 2) ** 2
    
    # Add some internal structure
    angle = np.arctan2(y - cy, x - cx)
    internal_structure = 0.1 * np.sin(3 * angle) * (1 - dist)
    grid[mask] += internal_structure[mask]
    
    grid = np.clip(grid, 0, 1)
    
    return grid


def add_memory_region(grid, kernel_params, memory_size=8):
    """
    Add a 'memory region' to the grid that encodes kernel parameters.
    The memory is a small region where the pattern stores its parameters.
    
    Memory encoding:
    - Each cell encodes a parameter value as its intensity
    - Position encodes which parameter
    """
    h, w = grid.shape
    memory = np.zeros((memory_size, memory_size))
    
    # Encode parameters
    R, mu, sigma = kernel_params
    
    # Normalize to [0, 1] range
    memory[0, 0] = min(R / 30, 1)      # R normalized
    memory[0, 1] = mu                    # mu is already [0, 1]
    memory[0, 2] = sigma * 10            # sigma scaled up
    memory[0, 3] = 1.0                   # marker bit
    
    # Place memory in top-left corner
    grid[:memory_size, :memory_size] = memory
    
    return grid


def extract_memory_region(grid, memory_size=8):
    """
    Extract kernel parameters from memory region.
    """
    memory = grid[:memory_size, :memory_size]
    
    # Decode parameters
    R = memory[0, 0] * 30
    mu = memory[0, 1]
    sigma = memory[0, 2] / 10
    
    return R, mu, sigma


def self_replicating_lenia_experiment(
    initial_params=(13, 0.15, 0.015),
    grid_size=64,
    steps=300,
    memory_size=8,
    replication_interval=50,
    noise_level=0.01
):
    """
    Run a self-replicating Lenia experiment.
    
    The pattern tries to maintain its kernel parameters in the memory region
    while evolving. If successful, the memory region should remain stable
    while the pattern continues to exist.
    """
    print("=" * 60)
    print("Self-Replicating Lenia Experiment")
    print("=" * 60)
    
    R, mu, sigma = initial_params
    print(f"\nInitial parameters: R={R}, μ={mu}, σ={sigma}")
    
    # Create initial pattern with memory
    grid = make_orbium((grid_size, grid_size), R)
    grid = add_memory_region(grid, initial_params, memory_size)
    
    # Make kernel from parameters
    kernel = make_gaussian_kernel(R, mu, sigma)
    
    # Track metrics
    memory_history = []
    energy_history = []
    snapshots = [grid.copy()]
    
    for step in range(steps):
        # Normal Lenia step
        grid, U = lenia_step(grid, kernel, mu, sigma)
        
        # Add small noise to memory region (mutation)
        grid[:memory_size, :memory_size] += np.random.randn(memory_size, memory_size) * noise_level
        grid[:memory_size, :memory_size] = np.clip(grid[:memory_size, :memory_size], 0, 1)
        
        # Every replication_interval steps, "read" the memory and update parameters
        if step > 0 and step % replication_interval == 0:
            # Extract parameters from memory
            new_R, new_mu, new_sigma = extract_memory_region(grid, memory_size)
            
            # Only update if parameters are valid
            if new_R > 5 and new_R < 30 and 0.05 < new_mu < 0.5 and 0.001 < new_sigma < 0.1:
                R, mu, sigma = new_R, new_mu, new_sigma
                kernel = make_gaussian_kernel(int(R), mu, sigma)
                print(f"  Step {step}: Updated kernel to R={R:.1f}, μ={mu:.3f}, σ={sigma:.4f}")
        
        # Track memory
        if step % 10 == 0:
            memory_history.append(grid[:memory_size, :memory_size].copy())
            energy = np.sum(grid)
            energy_history.append(energy)
        
        if step % 100 == 0:
            snapshots.append(grid.copy())
            print(f"  Step {step}: energy={energy:.2f}")
    
    return grid, memory_history, energy_history, snapshots


def parameter_sweep_experiment():
    """
    Sweep through different parameter combinations to find stable
    self-replicating configurations.
    """
    print("\n" + "=" * 60)
    print("Parameter Sweep: Finding Self-Replicating Configurations")
    print("=" * 60)
    
    results = []
    
    # Parameter ranges
    R_values = [10, 13, 15, 18]
    mu_values = [0.12, 0.15, 0.18, 0.20]
    sigma_values = [0.01, 0.015, 0.02, 0.03]
    
    total = len(R_values) * len(mu_values) * len(sigma_values)
    count = 0
    
    for R in R_values:
        for mu in mu_values:
            for sigma in sigma_values:
                count += 1
                print(f"\n[{count}/{total}] Testing R={R}, μ={mu}, σ={sigma}")
                
                # Run short simulation
                final_grid, mem_hist, energy_hist, _ = self_replicating_lenia_experiment(
                    initial_params=(R, mu, sigma),
                    grid_size=64,
                    steps=200,
                    replication_interval=50,
                    noise_level=0.005
                )
                
                # Metrics
                initial_energy = energy_hist[0]
                final_energy = energy_hist[-1]
                survival_rate = final_energy / (initial_energy + 1e-8)
                
                # Memory stability (how much did memory change?)
                mem_change = np.mean(np.abs(mem_hist[-1] - mem_hist[0]))
                
                result = {
                    'R': R,
                    'mu': mu,
                    'sigma': sigma,
                    'initial_energy': float(initial_energy),
                    'final_energy': float(final_energy),
                    'survival_rate': float(survival_rate),
                    'memory_change': float(mem_change),
                    'stable': 'yes' if survival_rate > 0.5 and mem_change < 0.2 else 'no'
                }
                results.append(result)
                
                status = "[OK] STABLE" if result['stable'] else "[X] UNSTABLE"
                print(f"  {status}: survival={survival_rate:.2f}, mem_change={mem_change:.3f}")
    
    # Save results
    output_path = Path("D:/openclaw_workspace/experiments/self_replicating_lenia_sweep.json")
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved sweep results to {output_path}")
    
    # Summary
    stable_count = sum(1 for r in results if r['stable'] == 'yes')
    print(f"\nFound {stable_count}/{total} stable configurations")
    
    return results


def visualize_self_replication(grid, memory_history, energy_history, snapshots):
    """Create visualization of self-replicating experiment."""
    
    fig = plt.figure(figsize=(14, 10))
    
    # 1. Evolution snapshots
    n_snaps = min(len(snapshots), 6)
    for i, snap in enumerate(snapshots[:n_snaps]):
        ax = fig.add_subplot(3, 4, i + 1)
        ax.imshow(snap, cmap='inferno', vmin=0, vmax=1)
        ax.set_title(f"Step {i * 100}")
        ax.axis('off')
    
    # 2. Memory evolution - show last 4 memory states
    n_mem = min(len(memory_history), 4)
    for i in range(n_mem):
        idx = len(memory_history) - n_mem + i  # Show last 4
        ax = fig.add_subplot(3, 4, 9 + i)
        ax.imshow(memory_history[idx], cmap='viridis', vmin=0, vmax=1)
        ax.set_title(f"Mem {idx * 10}")
        ax.axis('off')
    
    # 3. Energy plot
    ax = fig.add_subplot(3, 1, 3)
    ax.plot(energy_history, 'b-', linewidth=2)
    ax.set_xlabel('Time (x10 steps)')
    ax.set_ylabel('Total Energy')
    ax.set_title('Pattern Energy Over Time')
    ax.grid(True, alpha=0.3)
    
    plt.suptitle("Self-Replicating Lenia: Pattern + Memory Evolution", fontsize=14)
    plt.tight_layout()
    
    output_path = Path("D:/openclaw_workspace/experiments/self_replicating_lenia.png")
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Saved visualization to {output_path}")
    
    return fig


def visualize_sweep(results):
    """Visualize parameter sweep results."""
    
    # Extract data
    R_vals = [r['R'] for r in results]
    mu_vals = [r['mu'] for r in results]
    sigma_vals = [r['sigma'] for r in results]
    survival = [r['survival_rate'] for r in results]
    mem_change = [r['memory_change'] for r in results]
    stable = [r['stable'] == 'yes' for r in results]
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # 1. Survival rate scatter
    ax = axes[0, 0]
    colors = ['green' if s else 'red' for s in stable]
    ax.scatter(range(len(results)), survival, c=colors, alpha=0.7)
    ax.axhline(y=0.5, color='gray', linestyle='--', label='Stability threshold')
    ax.set_xlabel('Configuration')
    ax.set_ylabel('Survival Rate')
    ax.set_title('Survival Rate by Configuration')
    ax.legend()
    
    # 2. Memory change scatter
    ax = axes[0, 1]
    ax.scatter(range(len(results)), mem_change, c=colors, alpha=0.7)
    ax.axhline(y=0.2, color='gray', linestyle='--', label='Memory threshold')
    ax.set_xlabel('Configuration')
    ax.set_ylabel('Memory Change')
    ax.set_title('Memory Stability by Configuration')
    ax.legend()
    
    # 3. R vs survival
    ax = axes[1, 0]
    R_unique = sorted(set(R_vals))
    for R in R_unique:
        idx = [i for i, r in enumerate(results) if r['R'] == R]
        ax.scatter([R] * len(idx), [survival[i] for i in idx], 
                   c=['green' if stable[i] else 'red' for i in idx],
                   alpha=0.7)
    ax.set_xlabel('Kernel Radius (R)')
    ax.set_ylabel('Survival Rate')
    ax.set_title('Survival Rate by Kernel Radius')
    
    # 4. Summary
    ax = axes[1, 1]
    ax.axis('off')
    stable_count = sum(stable)
    best_idx = survival.index(max(survival))
    best = results[best_idx]
    
    summary_text = f"""
    Self-Replicating Lenia Sweep Results
    {'=' * 35}
    
    Total configurations: {len(results)}
    Stable configurations: {stable_count}
    
    Best configuration:
      R = {best['R']}
      μ = {best['mu']}
      σ = {best['sigma']}
      Survival rate: {best['survival_rate']:.3f}
      Memory change: {best['memory_change']:.3f}
    
    Stability criteria:
      - Survival rate > 0.5
      - Memory change < 0.2
    """
    ax.text(0.1, 0.5, summary_text, fontsize=11, fontfamily='monospace',
            verticalalignment='center', transform=ax.transAxes)
    
    plt.suptitle("Self-Replicating Lenia Parameter Sweep", fontsize=14)
    plt.tight_layout()
    
    output_path = Path("D:/openclaw_workspace/experiments/self_replicating_lenia_sweep.png")
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Saved sweep visualization to {output_path}")


if __name__ == "__main__":
    print("=" * 60)
    print("SELF-REPLICATING LENIA EXPERIMENT")
    print("=" * 60)
    print("\nHypothesis: A Lenia pattern can encode its own kernel")
    print("parameters in a 'memory region' and maintain them through")
    print("self-referential dynamics.")
    print()
    
    # Run main experiment
    print("\n--- Main Experiment ---")
    grid, mem_hist, energy_hist, snapshots = self_replicating_lenia_experiment(
        initial_params=(13, 0.15, 0.015),
        grid_size=64,
        steps=300,
        replication_interval=50,
        noise_level=0.01
    )
    
    visualize_self_replication(grid, mem_hist, energy_hist, snapshots)
    
    # Run parameter sweep
    print("\n--- Parameter Sweep ---")
    results = parameter_sweep_experiment()
    visualize_sweep(results)
    
    print("\n" + "=" * 60)
    print("Experiment complete!")
    print("=" * 60)
    print("\nKey questions for analysis:")
    print("1. Does the memory region remain stable?")
    print("2. Can parameters be extracted and used to regenerate the pattern?")
    print("3. What parameter combinations enable self-replication?")
    print("4. Is there a correlation between pattern stability and memory stability?")