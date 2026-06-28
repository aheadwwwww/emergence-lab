"""
Evolutionary Lenia V2 - Emergence-Focused Fitness

Key Changes from V1:
1. Fitness rewards DYNAMICS, not stability
2. Multiple seed types including perturbation seeds
3. Longer simulation (500 steps)
4. Novelty-based component in fitness

The goal is to evolve kernels that produce interesting emergent patterns,
not static blobs.
"""

import numpy as np
import jax
import jax.numpy as jnp
from jax import jit, vmap
from typing import NamedTuple, Tuple, List, Dict
import json
from pathlib import Path
from dataclasses import dataclass
import matplotlib.pyplot as plt

# ============== Genome (Same as V1) ==============

class Genome(NamedTuple):
    """33-parameter genome encoding a kernel via small NN."""
    weights: jnp.ndarray  # 33 params: 2->8->1 MLP
    
    def split_layers(self):
        w1 = self.weights[:16].reshape(8, 2)
        b1 = self.weights[16:24]
        w2 = self.weights[24:32].reshape(1, 8)
        b2 = self.weights[32:33]
        return w1, b1, w2, b2
    
    def to_kernel(self, R: int = 15) -> jnp.ndarray:
        """Convert genome to R-radius kernel."""
        w1, b1, w2, b2 = self.split_layers()
        
        # Create coordinate grid
        y, x = jnp.ogrid[-R:R+1, -R:R+1]
        r = jnp.sqrt(x*x + y*y)
        theta = jnp.arctan2(y, x)
        
        # Normalize coordinates
        r_norm = r / (R + 1e-8)
        theta_norm = (theta + jnp.pi) / (2 * jnp.pi)
        
        # Create mask for circular kernel
        mask = r <= R
        
        # Apply MLP to each pixel
        def compute_pixel(r_n, th_n, m):
            inp = jnp.array([r_n, th_n])
            h = jnp.tanh(w1 @ inp + b1)
            out = jnp.tanh(w2 @ h + b2)
            return out * m
        
        # Vectorize over grid
        compute_grid = jax.vmap(lambda r_n, th_n, m: compute_pixel(r_n, th_n, m))
        
        r_flat = r_norm.flatten()
        th_flat = theta_norm.flatten()
        m_flat = mask.flatten().astype(jnp.float32)
        
        kernel_flat = compute_grid(r_flat, th_flat, m_flat)
        kernel = kernel_flat.reshape(2*R+1, 2*R+1)
        
        # Normalize
        kernel = kernel / (jnp.abs(kernel).sum() + 1e-8)
        
        return kernel

# ============== Lenia Simulation ==============

@jit
def lenia_step(world: jnp.ndarray, kernel: jnp.ndarray, dt: float = 0.1) -> jnp.ndarray:
    """Single Lenia simulation step."""
    R = kernel.shape[0] // 2
    
    # Pad world for convolution
    padded = jnp.pad(world, R, mode='wrap')
    
    # Convolution via sliding window
    def convolve_at(i, j):
        window = jax.lax.dynamic_slice(padded, (i, j), (2*R+1, 2*R+1))
        return (window * kernel).sum()
    
    i_vals = jnp.arange(world.shape[0])
    j_vals = jnp.arange(world.shape[1])
    
    U = jax.vmap(lambda i: jax.vmap(lambda j: convolve_at(i, j))(j_vals))(i_vals)
    
    # Growth function
    growth = 2 * jnp.exp(-((U - 0.5) ** 2) / 0.1) - 1
    
    # Update
    new_world = jnp.clip(world + dt * growth, 0, 1)
    return new_world

@jit
def simulate_lenia(world: jnp.ndarray, kernel: jnp.ndarray, steps: int = 500) -> jnp.ndarray:
    """Run Lenia simulation for given steps."""
    def step_fn(w, _):
        return lenia_step(w, kernel), None
    
    final_world, _ = jax.lax.scan(step_fn, world, None, length=steps)
    return final_world

# ============== V2 Fitness: Emergence-Focused ==============

@dataclass
class EmergenceMetrics:
    """Metrics for emergent pattern quality."""
    temporal_entropy: float      # Diversity of states over time
    spatial_complexity: float    # Edge density
    pattern_change_rate: float   # How much the pattern changes
    survival: float              # Did anything survive?
    novelty: float               # Distance from simple patterns

def compute_emergence_metrics(world_history: List[jnp.ndarray]) -> EmergenceMetrics:
    """
    Compute metrics that reward EMERGENT DYNAMICS, not static stability.
    
    Key insight: We want patterns that:
    1. Change over time (not static)
    2. Have spatial structure (not uniform)
    3. Maintain complexity (not collapse or explode)
    """
    if len(world_history) < 2:
        return EmergenceMetrics(0, 0, 0, 0, 0)
    
    # Stack history
    history = jnp.stack(world_history)  # [T, H, W]
    
    # 1. Temporal Entropy: Diversity of states over time
    # Sample frames at different times and measure their uniqueness
    T, H, W = history.shape
    sample_frames = history[::max(1, T//10)]  # Sample 10 frames
    frame_hashes = []
    for f in sample_frames:
        # Simple hash: binned mass distribution
        flat = f.flatten()
        hist, _ = jnp.histogram(flat, bins=10, range=(0, 1))
        hist = hist / (hist.sum() + 1e-8)
        frame_hashes.append(hist)
    
    frame_hashes = jnp.stack(frame_hashes)
    # Entropy of frame distribution
    mean_hash = frame_hashes.mean(axis=0)
    temporal_entropy = float(-(mean_hash * jnp.log(mean_hash + 1e-8)).sum())
    
    # 2. Spatial Complexity: Edge density using Sobel-like filter
    final = world_history[-1]
    # Simple gradient magnitude
    grad_y = jnp.abs(jnp.diff(final, axis=0))
    grad_x = jnp.abs(jnp.diff(final, axis=1))
    # Pad to same size
    grad_y = jnp.pad(grad_y, ((0, 1), (0, 0)))
    grad_x = jnp.pad(grad_x, ((0, 0), (0, 1)))
    edge_magnitude = jnp.sqrt(grad_y**2 + grad_x**2)
    spatial_complexity = float(edge_magnitude.mean())
    
    # 3. Pattern Change Rate: How much does the pattern change?
    changes = []
    for i in range(1, len(world_history)):
        diff = jnp.abs(world_history[i] - world_history[i-1])
        changes.append(float(diff.mean()))
    pattern_change_rate = float(jnp.mean(jnp.array(changes))) if changes else 0.0
    
    # 4. Survival: Did anything survive?
    final_mass = float(world_history[-1].sum())
    initial_mass = float(world_history[0].sum())
    survival = min(1.0, final_mass / (initial_mass + 1e-8))
    
    # 5. Novelty: Distance from "boring" patterns
    # A boring pattern is uniform or has very low entropy
    mass_std = float(history[-1].std())
    mass_mean = float(history[-1].mean())
    # High novelty = non-uniform distribution
    novelty = mass_std / (mass_mean + 1e-8)
    
    return EmergenceMetrics(
        temporal_entropy=temporal_entropy,
        spatial_complexity=spatial_complexity,
        pattern_change_rate=pattern_change_rate,
        survival=survival,
        novelty=novelty
    )

def compute_v2_fitness(metrics: EmergenceMetrics) -> float:
    """
    V2 Fitness Function: Rewards emergent dynamics.
    
    Formula:
    fitness = (temporal_entropy × pattern_change) × 
              (spatial_complexity + novelty) × 
              survival_weighted
    
    This rewards patterns that:
    - Change over time (pattern_change_rate)
    - Have diverse states (temporal_entropy)
    - Have spatial structure (spatial_complexity)
    - Are non-uniform (novelty)
    - Survive long enough to be interesting (survival, but weighted)
    """
    # Weight survival: too much survival (static blob) is penalized
    # Ideal survival is around 0.5-0.8
    survival_weight = metrics.survival * (1.0 - metrics.survival) * 4  # Peaks at 0.5
    
    # Combine metrics
    dynamics = metrics.temporal_entropy * metrics.pattern_change_rate
    structure = metrics.spatial_complexity + metrics.novelty
    
    fitness = dynamics * structure * (0.3 + 0.7 * survival_weight)
    
    return float(fitness)

# ============== Seed Strategies ==============

def create_orbium_seed(size: int = 128) -> jnp.ndarray:
    """Create Orbium-style initial pattern."""
    world = jnp.zeros((size, size), dtype=jnp.float32)
    
    # Create asymmetric shape (Orbium is not perfectly round)
    cy, cx = size // 2, size // 2
    y, x = jnp.ogrid[:size, :size]
    
    # Main body (ellipse)
    r = jnp.sqrt(((x - cx) / 12) ** 2 + ((y - cy) / 10) ** 2)
    world = jnp.where(r < 1, 1.0, 0.0)
    
    # Add asymmetry
    theta = jnp.arctan2(y - cy, x - cx)
    r2 = jnp.sqrt(((x - cx) / 8) ** 2 + ((y - cy) / 14) ** 2)
    world = world + jnp.where((r2 < 0.6) & (theta > 0), 0.3, 0.0)
    
    return jnp.clip(world, 0, 1)

def create_random_seed(size: int = 128, sparsity: float = 0.3) -> jnp.ndarray:
    """Create random sparse pattern."""
    key = jax.random.PRNGKey(42)
    key, subkey = jax.random.split(key)
    world = jax.random.uniform(subkey, (size, size))
    world = jnp.where(world > (1 - sparsity), world, 0.0)
    return world

def create_perturbed_orbium_seed(size: int = 128, noise_level: float = 0.2) -> jnp.ndarray:
    """Create Orbium with noise perturbation."""
    base = create_orbium_seed(size)
    key = jax.random.PRNGKey(123)
    noise = jax.random.uniform(key, (size, size)) * noise_level
    # Add noise only where there's mass
    perturbed = jnp.where(base > 0.5, base + noise * 0.3, noise * 0.1)
    return jnp.clip(perturbed, 0, 1)

def create_multi_seed(size: int = 128, n_orbs: int = 3) -> jnp.ndarray:
    """Create multiple Orbium-like patterns."""
    world = jnp.zeros((size, size), dtype=jnp.float32)
    
    positions = [(size//4, size//4), (size//2, 3*size//4), (3*size//4, size//3)]
    
    for i, (px, py) in enumerate(positions[:n_orbs]):
        y, x = jnp.ogrid[:size, :size]
        r = jnp.sqrt((x - px) ** 2 + (y - py) ** 2)
        orb = jnp.where(r < 8, 1.0, 0.0)
        world = world + orb
    
    return jnp.clip(world, 0, 1)

# ============== Evolution ==============

def evaluate_genome_v2(genome: Genome, seed_type: str = "orbium", 
                       sim_steps: int = 500) -> Tuple[float, EmergenceMetrics]:
    """Evaluate genome with V2 emergence-focused fitness."""
    kernel = genome.to_kernel(R=15)
    
    # Create seed
    if seed_type == "orbium":
        seed = create_orbium_seed()
    elif seed_type == "random":
        seed = create_random_seed()
    elif seed_type == "perturbed":
        seed = create_perturbed_orbium_seed()
    elif seed_type == "multi":
        seed = create_multi_seed()
    else:
        seed = create_random_seed()
    
    # Simulate with history
    world = seed
    history = [world]
    
    for step in range(sim_steps):
        world = lenia_step(world, kernel)
        if step % 20 == 0:  # Sample every 20 steps
            history.append(world)
    
    # Compute emergence metrics
    metrics = compute_emergence_metrics(history)
    fitness = compute_v2_fitness(metrics)
    
    return fitness, metrics

def evolve_v2(n_generations: int = 10, pop_size: int = 20, 
               seed_types: List[str] = ["orbium", "perturbed", "multi"],
               sim_steps: int = 500) -> Dict:
    """Evolve with V2 emergence-focused fitness."""
    
    # Initialize population
    key = jax.random.PRNGKey(42)
    
    population = []
    for i in range(pop_size):
        key, subkey = jax.random.split(key)
        weights = jax.random.normal(subkey, (33,)) * 0.5
        population.append(Genome(weights))
    
    history = {
        "generations": [],
        "best_genomes": [],
        "config": {
            "n_generations": n_generations,
            "pop_size": pop_size,
            "seed_types": seed_types,
            "sim_steps": sim_steps,
            "fitness_version": "v2_emergence"
        }
    }
    
    for gen in range(n_generations):
        print(f"Generation {gen+1}/{n_generations}")
        
        # Evaluate population on all seed types
        fitness_scores = []
        all_metrics = []
        
        for genome in population:
            # Evaluate on multiple seeds and take average
            seed_scores = []
            seed_metrics = []
            
            for seed_type in seed_types:
                score, metrics = evaluate_genome_v2(genome, seed_type, sim_steps)
                seed_scores.append(score)
                seed_metrics.append(metrics)
            
            avg_score = float(jnp.mean(jnp.array(seed_scores)))
            fitness_scores.append(avg_score)
            all_metrics.append(seed_metrics)
        
        # Find best
        best_idx = int(jnp.argmax(jnp.array(fitness_scores)))
        best_genome = population[best_idx]
        best_score = fitness_scores[best_idx]
        
        print(f"  Best score: {best_score:.6f}")
        print(f"  Mean score: {jnp.mean(jnp.array(fitness_scores)):.6f}")
        
        # Record history
        gen_record = {
            "generation": gen + 1,
            "best_score": best_score,
            "mean_score": float(jnp.mean(jnp.array(fitness_scores))),
            "median_score": float(jnp.median(jnp.array(fitness_scores))),
            "best_metrics": {
                seed_types[i]: {
                    "temporal_entropy": all_metrics[best_idx][i].temporal_entropy,
                    "spatial_complexity": all_metrics[best_idx][i].spatial_complexity,
                    "pattern_change_rate": all_metrics[best_idx][i].pattern_change_rate,
                    "survival": all_metrics[best_idx][i].survival,
                    "novelty": all_metrics[best_idx][i].novelty,
                    "fitness": seed_scores[i]
                }
                for i in range(len(seed_types))
            }
        }
        history["generations"].append(gen_record)
        history["best_genomes"].append([float(w) for w in best_genome.weights])
        
        # Selection + Variation
        if gen < n_generations - 1:
            # Tournament selection
            new_population = [best_genome]  # Elitism
            
            while len(new_population) < pop_size:
                # Select parent (tournament)
                idxs = jax.random.randint(key, (3,), 0, pop_size)
                parent_idx = int(idxs[jnp.argmax(jnp.array([fitness_scores[i] for i in idxs]))])
                parent = population[parent_idx]
                
                # Mutate
                key, subkey = jax.random.split(key)
                mutation = jax.random.normal(subkey, (33,)) * 0.1
                child = Genome(parent.weights + mutation)
                new_population.append(child)
            
            population = new_population
    
    return history

# ============== Main ==============

if __name__ == "__main__":
    print("=" * 60)
    print("Evolutionary Lenia V2: Emergence-Focused Fitness")
    print("=" * 60)
    print("\nKey changes from V1:")
    print("- Fitness rewards DYNAMICS, not stability")
    print("- Multiple seed types (orbium, perturbed, multi)")
    print("- Longer simulation (500 steps)")
    print("- Novelty-based component")
    print()
    
    # Run evolution
    history = evolve_v2(
        n_generations=10,
        pop_size=20,
        seed_types=["orbium", "perturbed", "multi"],
        sim_steps=500
    )
    
    # Save results
    output_dir = Path("output/evo_lenia_v2")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "evolution_history_v2.json", "w") as f:
        json.dump(history, f, indent=2)
    
    # Plot evolution curves
    generations = [g["generation"] for g in history["generations"]]
    best_scores = [g["best_score"] for g in history["generations"]]
    mean_scores = [g["mean_score"] for g in history["generations"]]
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Fitness over generations
    ax = axes[0]
    ax.plot(generations, best_scores, 'b-o', label='Best')
    ax.plot(generations, mean_scores, 'g--', label='Mean')
    ax.set_xlabel('Generation')
    ax.set_ylabel('Fitness')
    ax.set_title('V2 Fitness Evolution')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Metrics breakdown for best genome
    ax = axes[1]
    last_gen = history["generations"][-1]
    seed_types = list(last_gen["best_metrics"].keys())
    metrics_names = ["temporal_entropy", "spatial_complexity", "pattern_change_rate", "survival", "novelty"]
    
    x = range(len(metrics_names))
    width = 0.25
    for i, seed in enumerate(seed_types):
        values = [last_gen["best_metrics"][seed][m] for m in metrics_names]
        ax.bar([j + i*width for j in x], values, width, label=seed)
    
    ax.set_xlabel('Metric')
    ax.set_ylabel('Value')
    ax.set_title('Best Genome Metrics by Seed Type')
    ax.set_xticks([j + width for j in x])
    ax.set_xticklabels(metrics_names, rotation=45, ha='right')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(output_dir / "evolution_v2_curves.png", dpi=150)
    plt.close()
    
    print(f"\nResults saved to {output_dir}")
    print(f"Best fitness: {best_scores[-1]:.6f}")
    
    # Check for improvement
    if len(best_scores) > 1:
        improvement = best_scores[-1] - best_scores[0]
        if improvement > 0:
            print(f"✓ Fitness IMPROVED by {improvement:.6f}")
        else:
            print(f"✗ Fitness did not improve")
