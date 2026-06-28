"""Neural Lenia Evolution Experiment
Based on neuroparticles2 insight: gene → CA rule → behavior → fitness → evolution.
Applied to Lenia: neural network weights as genotype, run Lenia, score survival, evolve.

Concept:
- Genotype = NN weights (kernel function parameters)
- Phenotype = Lenia simulation result (survival, complexity, stability)
- Fitness = composite score
- Evolution = mutate best weights, cross-breed
"""

import jax
import jax.numpy as jnp
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json, time

from lenia_jax import make_kernel_fft, make_orbium

# ============================================================================
# Simple Neural Kernel
# ============================================================================

def create_random_genome(n_params=16):
    """Create a random genome (NN weights for kernel function)."""
    # Small 2-layer MLP: input (r, theta) -> hidden -> output (kernel value)
    # Layer 1: 2→8 = 16 weights + 8 biases = 24
    # Layer 2: 8→1 = 8 weights + 1 bias = 9
    # Total: 33 params
    genome = np.random.randn(n_params).astype(np.float32) * 0.5
    return genome

def genome_to_kernel(genome, R, size):
    """Convert genome to kernel via a small NN."""
    # Parse genome into layers
    # Layer 1: 2 inputs (r_norm, theta_norm) → 8 hidden
    w1 = genome[:16].reshape(8, 2)
    b1 = genome[16:24]
    # Layer 2: 8 hidden → 1 output
    w2 = genome[24:32].reshape(1, 8)
    b2 = genome[32:33]
    
    # Create coordinate grid
    y, x = np.ogrid[-R:R+1, -R:R+1]
    r = np.sqrt(x*x + y*y)
    theta = np.arctan2(y, x)
    
    # Normalize
    r_norm = r / (R + 1e-8)
    theta_norm = (theta + np.pi) / (2 * np.pi)
    
    # Apply NN to each pixel inside radius
    kernel = np.zeros((2*R+1, 2*R+1), dtype=np.float32)
    mask = r <= R
    
    for i in range(2*R+1):
        for j in range(2*R+1):
            if mask[i, j]:
                inp = np.array([r_norm[i,j], theta_norm[i,j]], dtype=np.float32)
                h = np.tanh(w1 @ inp + b1)
                out = np.tanh(w2 @ h + b2)
                kernel[i, j] = float(out[0])
    
    # Normalize kernel
    kernel = kernel / (np.abs(kernel).sum() + 1e-8)
    
    # FFT pad
    kernel_padded = np.zeros((size, size), dtype=np.float32)
    off = size // 2 - R
    kernel_padded[off:off+2*R+1, off:off+2*R+1] = kernel
    kernel_fft = jnp.fft.fft2(jnp.array(kernel_padded))
    
    return kernel_fft

def simulate_lenia(genome, R=15, size=128, steps=200, seed='orbium'):
    """Run Lenia with genome-based kernel and return history."""
    kernel_fft = genome_to_kernel(genome, R, size)
    
    if seed == 'orbium':
        grid = make_orbium((size, size), R)
    else:
        np.random.seed(42)
        grid = jnp.array(np.random.rand(size, size).astype(np.float32) * 0.5)
    
    mu = 0.2
    sigma = 0.03
    dt = 0.1
    
    history = [np.array(grid)]
    grid_jax = jnp.array(grid)
    
    for _ in range(steps):
        grid_fft = jnp.fft.fft2(grid_jax)
        conv = jnp.fft.ifft2(grid_fft * kernel_fft).real
        growth = jnp.exp(-((conv - mu) ** 2) / (2 * sigma ** 2)) * 2 - 1
        grid_jax = jnp.clip(grid_jax + dt * growth, 0, 1)
        
        if _ % 20 == 0:
            history.append(np.array(grid_jax))
    
    history.append(np.array(grid_jax))
    return history

def fitness(history):
    """Score a simulation result."""
    masses = np.array([h.sum() for h in history])
    final = history[-1]
    
    survival = np.mean(masses > 10)  # mass threshold
    if len(masses) > 5:
        stability = 1 - np.std(masses[-5:]) / (np.mean(masses[-5:]) + 1e-8)
    else:
        stability = 0
    
    final_norm = final / (final.sum() + 1e-8)
    entropy = -np.sum(final_norm * np.log(final_norm + 1e-8))
    entropy_norm = entropy / np.log(len(final.ravel()))
    
    return float(survival * max(0, stability) * (1 + entropy_norm))

# ============================================================================
# Evolution
# ============================================================================

def evolve(population_size=20, generations=10, n_params=33):
    """Evolve neural Lenia kernels."""
    # Initialize population
    pop = [create_random_genome(n_params) for _ in range(population_size)]
    
    results = []
    
    for gen in range(generations):
        print(f"\nGeneration {gen+1}/{generations}")
        
        # Evaluate fitness
        scores = []
        for i, genome in enumerate(pop):
            try:
                history = simulate_lenia(genome, R=15, steps=200, seed='orbium')
                score = fitness(history)
            except Exception as e:
                score = 0
            scores.append(score)
            if i % 5 == 0:
                print(f"  {i+1}/{population_size}: score={score:.4f}")
        
        # Sort by fitness
        ranked = sorted(zip(scores, pop), key=lambda x: x[0], reverse=True)
        best_score, best_genome = ranked[0]
        
        results.append({
            'generation': gen + 1,
            'best_score': float(best_score),
            'mean_score': float(np.mean(scores)),
            'max_score': float(np.max(scores)),
        })
        
        print(f"  Best: {best_score:.4f}, Mean: {np.mean(scores):.4f}")
        
        # Selection: keep top 50%
        n_keep = population_size // 2
        elite = [g for _, g in ranked[:n_keep]]
        
        # Cross-breed + mutate to fill population
        new_pop = elite.copy()
        while len(new_pop) < population_size:
            parent1 = elite[np.random.randint(len(elite))]
            parent2 = elite[np.random.randint(len(elite))]
            
            # Crossover
            mask = np.random.rand(n_params) < 0.5
            child = np.where(mask, parent1, parent2)
            
            # Mutation
            mutation_rate = 0.1
            mutation_mask = np.random.rand(n_params) < mutation_rate
            child[mutation_mask] += np.random.randn(np.sum(mutation_mask)) * 0.2
            
            new_pop.append(child.astype(np.float32))
        
        pop = new_pop
    
    return results, best_genome, best_score

# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Neural Lenia Evolution Experiment")
    print("=" * 60)
    
    output_dir = Path('output/neural_lenia_evo')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    t0 = time.time()
    results, best_genome, best_score = evolve(
        population_size=20, 
        generations=10,
        n_params=33
    )
    elapsed = time.time() - t0
    print(f"\nCompleted in {elapsed:.0f}s")
    print(f"Best score: {best_score:.4f}")
    
    # Save results
    with open(output_dir / 'evolution_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    np.save(output_dir / 'best_genome.npy', best_genome)
    
    # Plot evolution curve
    fig, ax = plt.subplots(figsize=(10, 6))
    gens = [r['generation'] for r in results]
    bests = [r['best_score'] for r in results]
    means = [r['mean_score'] for r in results]
    
    ax.plot(gens, bests, 'b-', label='Best Fitness', linewidth=2)
    ax.plot(gens, means, 'r--', label='Mean Fitness', linewidth=1)
    ax.fill_between(gens, means, bests, alpha=0.2)
    ax.set_xlabel('Generation')
    ax.set_ylabel('Fitness')
    ax.set_title('Neural Lenia Kernel Evolution')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'evolution_curve.png', dpi=150)
    print(f"Saved: {output_dir / 'evolution_curve.png'}")
    
    # Run best genome for visualization
    print("\nRunning best genome for 500 steps...")
    history = simulate_lenia(best_genome, R=15, steps=500, seed='orbium')
    
    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    axes = axes.flatten()
    step_indices = [0, 100, 200, 300, 400, 500]
    for i, si in enumerate(step_indices):
        if si < len(history):
            idx = min(si // 20, len(history) - 1)
            axes[i].imshow(history[idx], cmap='viridis')
            axes[i].set_title(f'Step {si}')
            axes[i].axis('off')
    
    plt.suptitle(f'Best Neural Lenia Kernel (score={best_score:.4f})', fontsize=14)
    plt.tight_layout()
    plt.savefig(output_dir / 'best_simulation.png', dpi=150)
    print(f"Saved: {output_dir / 'best_simulation.png'}")
    
    print("\nDone!")
