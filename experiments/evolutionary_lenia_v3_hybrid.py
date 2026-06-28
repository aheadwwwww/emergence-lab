"""
Evolutionary Lenia V3 - Hybrid Fitness Function
=================================================

Combines V1 stability-focused fitness with V2 emergence dynamics.

Hybrid Fitness = alpha * V1_fitness + (1 - alpha) * V2_fitness

Where:
- V1_fitness: rewards survival, stability, structural complexity
- V2_fitness: rewards temporal dynamics, pattern change, novelty
- alpha = 0.5 (equal weight to both objectives)

Goal: Evolve kernels that produce patterns that are BOTH stable AND dynamic.
"""

import jax
import jax.numpy as jnp
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any
import json
import time

# Import from existing modules
from evolutionary_lenia import (
    Genome,
    LeniaSimulator,
    compute_fitness,
    FitnessResult,
)

# ============================================================================
# V2 Emergence Metrics (from evolutionary_lenia_v2.py)
# ============================================================================

@dataclass
class EmergenceMetrics:
    """Metrics for emergent pattern quality."""
    temporal_entropy: float      # Diversity of states over time
    spatial_complexity: float    # Edge density
    pattern_change_rate: float   # How much the pattern changes
    survival: float              # Did anything survive?
    novelty: float               # Distance from simple patterns


def compute_emergence_metrics(history: List[np.ndarray]) -> EmergenceMetrics:
    """
    Compute metrics that reward EMERGENT DYNAMICS.
    
    Key insight: We want patterns that:
    1. Change over time (not static)
    2. Have spatial structure (not uniform)
    3. Maintain complexity (not collapse or explode)
    """
    if len(history) < 2:
        return EmergenceMetrics(0, 0, 0, 0, 0)
    
    # Stack history
    history_arr = np.array(history)  # [T, H, W]
    T, H, W = history_arr.shape
    
    # 1. Temporal Entropy: Diversity of states over time
    # Sample frames at different times and measure their uniqueness
    sample_frames = history_arr[::max(1, T//10)]  # Sample up to 10 frames
    frame_hashes = []
    for f in sample_frames:
        # Simple hash: binned mass distribution
        flat = f.flatten()
        hist, _ = np.histogram(flat, bins=10, range=(0, 1))
        hist = hist / (hist.sum() + 1e-8)
        frame_hashes.append(hist)
    
    frame_hashes = np.array(frame_hashes)
    # Entropy of frame distribution
    mean_hash = frame_hashes.mean(axis=0)
    temporal_entropy = float(-(mean_hash * np.log(mean_hash + 1e-8)).sum())
    
    # 2. Spatial Complexity: Edge density using gradient
    final = history[-1]
    # Simple gradient magnitude
    grad_y = np.abs(np.diff(final, axis=0))
    grad_x = np.abs(np.diff(final, axis=1))
    # Pad to same size
    grad_y = np.pad(grad_y, ((0, 1), (0, 0)))
    grad_x = np.pad(grad_x, ((0, 0), (0, 1)))
    edge_magnitude = np.sqrt(grad_y**2 + grad_x**2)
    spatial_complexity = float(edge_magnitude.mean())
    
    # 3. Pattern Change Rate: How much does the pattern change?
    changes = []
    for i in range(1, len(history)):
        diff = np.abs(history[i] - history[i-1])
        changes.append(float(diff.mean()))
    pattern_change_rate = float(np.mean(changes)) if changes else 0.0
    
    # 4. Survival: Did anything survive?
    final_mass = float(history[-1].sum())
    initial_mass = float(history[0].sum())
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
    """
    # Weight survival: too much survival (static blob) is penalized
    # Ideal survival is around 0.5-0.8
    survival_weight = metrics.survival * (1.0 - metrics.survival) * 4  # Peaks at 0.5
    
    # Combine metrics
    dynamics = metrics.temporal_entropy * metrics.pattern_change_rate
    structure = metrics.spatial_complexity + metrics.novelty
    
    fitness = dynamics * structure * (0.3 + 0.7 * survival_weight)
    
    return float(fitness)


# ============================================================================
# Hybrid Fitness
# ============================================================================

@dataclass
class HybridFitnessResult:
    """Combined fitness from V1 and V2."""
    v1_fitness: float
    v2_fitness: float
    hybrid_fitness: float
    
    # V1 metrics
    survival: float
    stability: float
    entropy: float
    diversity: float
    final_mass: float
    
    # V2 metrics
    temporal_entropy: float
    spatial_complexity: float
    pattern_change_rate: float
    novelty: float
    
    def to_dict(self):
        return {
            'v1_fitness': self.v1_fitness,
            'v2_fitness': self.v2_fitness,
            'hybrid_fitness': self.hybrid_fitness,
            'survival': self.survival,
            'stability': self.stability,
            'entropy': self.entropy,
            'diversity': self.diversity,
            'final_mass': self.final_mass,
            'temporal_entropy': self.temporal_entropy,
            'spatial_complexity': self.spatial_complexity,
            'pattern_change_rate': self.pattern_change_rate,
            'novelty': self.novelty,
        }


def compute_hybrid_fitness(history: List[np.ndarray], alpha: float = 0.5) -> HybridFitnessResult:
    """
    Compute hybrid fitness combining V1 and V2.
    
    Args:
        history: List of simulation frames
        alpha: Weight for V1 fitness (1-alpha for V2), default 0.5
    
    Returns:
        HybridFitnessResult with all metrics
    """
    # V1 fitness (from evolutionary_lenia.py)
    v1_result = compute_fitness(history)
    v1_fitness = v1_result.score
    
    # V2 fitness (from evolutionary_lenia_v2.py)
    emergence_metrics = compute_emergence_metrics(history)
    v2_fitness = compute_v2_fitness(emergence_metrics)
    
    # Hybrid fitness
    hybrid_fitness = alpha * v1_fitness + (1 - alpha) * v2_fitness
    
    return HybridFitnessResult(
        v1_fitness=v1_fitness,
        v2_fitness=v2_fitness,
        hybrid_fitness=hybrid_fitness,
        # V1 metrics
        survival=v1_result.survival,
        stability=v1_result.stability,
        entropy=v1_result.entropy,
        diversity=v1_result.diversity,
        final_mass=v1_result.final_mass,
        # V2 metrics
        temporal_entropy=emergence_metrics.temporal_entropy,
        spatial_complexity=emergence_metrics.spatial_complexity,
        pattern_change_rate=emergence_metrics.pattern_change_rate,
        novelty=emergence_metrics.novelty,
    )


# ============================================================================
# Seed Types
# ============================================================================

def create_orbium_seed(size: int = 128) -> np.ndarray:
    """Create Orbium-style initial pattern."""
    world = np.zeros((size, size), dtype=np.float32)
    
    # Create asymmetric shape
    cy, cx = size // 2, size // 2
    y, x = np.ogrid[:size, :size]
    
    # Main body (ellipse)
    r = np.sqrt(((x - cx) / 12) ** 2 + ((y - cy) / 10) ** 2)
    world = np.where(r < 1, 1.0, 0.0)
    
    # Add asymmetry
    theta = np.arctan2(y - cy, x - cx)
    r2 = np.sqrt(((x - cx) / 8) ** 2 + ((y - cy) / 14) ** 2)
    world = world + np.where((r2 < 0.6) & (theta > 0), 0.3, 0.0)
    
    return np.clip(world, 0, 1).astype(np.float32)


def create_perturbed_seed(size: int = 128, noise_level: float = 0.2) -> np.ndarray:
    """Create Orbium with noise perturbation."""
    base = create_orbium_seed(size)
    np.random.seed(123)
    noise = np.random.rand(size, size).astype(np.float32) * noise_level
    # Add noise only where there's mass
    perturbed = np.where(base > 0.5, base + noise * 0.3, noise * 0.1)
    return np.clip(perturbed, 0, 1).astype(np.float32)


def create_multi_seed(size: int = 128) -> np.ndarray:
    """Create multiple Orbium-like patterns."""
    world = np.zeros((size, size), dtype=np.float32)
    
    positions = [(size//4, size//4), (size//2, 3*size//4), (3*size//4, size//3)]
    
    for px, py in positions:
        y, x = np.ogrid[:size, :size]
        r = np.sqrt((x - px) ** 2 + (y - py) ** 2)
        orb = np.where(r < 8, 1.0, 0.0).astype(np.float32)
        world = world + orb
    
    return np.clip(world, 0, 1).astype(np.float32)


def get_seed(seed_name: str, size: int = 128) -> np.ndarray:
    """Get seed by name."""
    if seed_name == 'orbium':
        return create_orbium_seed(size)
    elif seed_name == 'perturbed':
        return create_perturbed_seed(size)
    elif seed_name == 'multi':
        return create_multi_seed(size)
    else:
        # Random fallback
        np.random.seed(42)
        return (np.random.rand(size, size) * 0.5).astype(np.float32)


# ============================================================================
# Evolution Engine V3
# ============================================================================

@dataclass
class GenerationResultV3:
    """Results for one generation."""
    generation: int
    best_hybrid_fitness: float
    mean_hybrid_fitness: float
    best_v1_fitness: float
    best_v2_fitness: float
    best_genome_idx: int
    seed_results: Dict[str, HybridFitnessResult]


class EvolutionEngineV3:
    """
    Evolution engine with hybrid V1+V2 fitness.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.simulator = LeniaSimulator(config)
        self.history: List[GenerationResultV3] = []
        self.population: List[Genome] = []
        self.alpha = config.get('alpha', 0.5)
        
    def _evaluate(self, genome: Genome) -> Tuple[float, Dict[str, HybridFitnessResult]]:
        """Evaluate genome on all seeds with hybrid fitness."""
        kernel_fft = genome.to_kernel_fft(
            self.config['kernel_radius'],
            self.config['grid_size']
        )
        
        seed_results = {}
        total_hybrid = 0.0
        
        for seed_name in self.config['seeds']:
            # Get seed and run simulation
            seed = get_seed(seed_name, self.config['grid_size'])
            # Use simulator with custom seed
            history = []
            grid = jnp.array(seed)
            history.append(np.array(grid))
            
            for step in range(self.config['sim_steps']):
                grid_fft = jnp.fft.fft2(grid)
                conv = jnp.fft.ifft2(grid_fft * kernel_fft).real
                growth = jnp.exp(-((conv - self.simulator.mu) ** 2) / 
                                (2 * self.simulator.sigma ** 2)) * 2 - 1
                grid = jnp.clip(grid + self.simulator.dt * growth, 0, 1)
                if step % 20 == 0:
                    history.append(np.array(grid))
            history.append(np.array(grid))
            
            # Compute hybrid fitness
            result = compute_hybrid_fitness(history, self.alpha)
            seed_results[seed_name] = result
            total_hybrid += result.hybrid_fitness
        
        return total_hybrid, seed_results
    
    def _crossover(self, p1: Genome, p2: Genome) -> Genome:
        """Uniform crossover."""
        mask = np.random.rand(self.config['genome_size']) < 0.5
        child_weights = np.where(mask, p1.weights, p2.weights)
        return Genome(child_weights.astype(np.float32))
    
    def _mutate(self, genome: Genome) -> Genome:
        """Gaussian mutation."""
        mutated = genome.weights.copy()
        n_mutate = max(1, np.random.binomial(
            self.config['genome_size'],
            self.config['mutation_rate']
        ))
        indices = np.random.choice(
            self.config['genome_size'],
            n_mutate,
            replace=False
        )
        mutated[indices] += np.random.randn(n_mutate) * self.config['mutation_scale']
        return Genome(mutated.astype(np.float32))
    
    def evolve(self) -> List[GenerationResultV3]:
        """Run evolution."""
        pop_size = self.config['population_size']
        elite_n = max(1, int(pop_size * self.config['elite_fraction']))
        
        # Initialize population
        self.population = [
            Genome.random(self.config['genome_size'])
            for _ in range(pop_size)
        ]
        self.history = []
        
        for gen in range(self.config['generations']):
            if self.config['verbose']:
                print(f"\n{'='*60}")
                print(f"Generation {gen+1}/{self.config['generations']}")
                print(f"{'='*60}")
            
            # Evaluate all genomes
            scores = []
            seed_details = []
            
            for i, genome in enumerate(self.population):
                total_score, seed_results = self._evaluate(genome)
                scores.append(total_score)
                seed_details.append(seed_results)
                
                if self.config['verbose'] and i % 4 == 0:
                    avg_hybrid = np.mean([r.hybrid_fitness for r in seed_results.values()])
                    print(f"  [{i+1}/{pop_size}] hybrid={avg_hybrid:.4f}")
            
            # Record stats
            best_idx = int(np.argmax(scores))
            best_seeds = seed_details[best_idx]
            
            gen_result = GenerationResultV3(
                generation=gen + 1,
                best_hybrid_fitness=float(scores[best_idx]),
                mean_hybrid_fitness=float(np.mean(scores)),
                best_v1_fitness=float(np.mean([r.v1_fitness for r in best_seeds.values()])),
                best_v2_fitness=float(np.mean([r.v2_fitness for r in best_seeds.values()])),
                best_genome_idx=best_idx,
                seed_results=best_seeds,
            )
            self.history.append(gen_result)
            
            if self.config['verbose']:
                print(f"\n  Best hybrid: {gen_result.best_hybrid_fitness:.4f}")
                print(f"  Best V1:     {gen_result.best_v1_fitness:.4f}")
                print(f"  Best V2:     {gen_result.best_v2_fitness:.4f}")
                print(f"  Mean:        {gen_result.mean_hybrid_fitness:.4f}")
            
            # Selection and variation
            if gen < self.config['generations'] - 1:
                ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
                elite = [self.population[i] for i, _ in ranked[:elite_n]]
                
                new_pop = [g.clone() for g in elite]
                
                while len(new_pop) < pop_size:
                    # Tournament selection
                    idxs = np.random.choice(len(new_pop), min(3, len(new_pop)), replace=False)
                    parent1 = new_pop[idxs[0]] if scores[idxs[0]] > scores[idxs[-1]] else new_pop[idxs[-1]]
                    
                    idxs2 = np.random.choice(len(new_pop), min(3, len(new_pop)), replace=False)
                    parent2 = new_pop[idxs2[0]] if np.random.random() < 0.7 else new_pop[idxs2[-1]]
                    
                    child = self._crossover(parent1, parent2)
                    child = self._mutate(child)
                    new_pop.append(child)
                
                self.population = new_pop
        
        return self.history
    
    def get_best(self) -> Genome:
        """Get best genome from current population."""
        scores = []
        for genome in self.population:
            total, _ = self._evaluate(genome)
            scores.append(total)
        return self.population[int(np.argmax(scores))]
    
    def plot_results(self, output_dir: Path):
        """Create evolution plots."""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        gens = [r.generation for r in self.history]
        hybrid_best = [r.best_hybrid_fitness for r in self.history]
        hybrid_mean = [r.mean_hybrid_fitness for r in self.history]
        v1_best = [r.best_v1_fitness for r in self.history]
        v2_best = [r.best_v2_fitness for r in self.history]
        
        # Plot 1: Hybrid fitness over generations
        ax = axes[0, 0]
        ax.plot(gens, hybrid_best, 'b-o', linewidth=2, markersize=6, label='Best')
        ax.plot(gens, hybrid_mean, 'g--', linewidth=1.5, label='Mean')
        ax.fill_between(gens, hybrid_mean, hybrid_best, alpha=0.15)
        ax.set_xlabel('Generation', fontsize=11)
        ax.set_ylabel('Hybrid Fitness', fontsize=11)
        ax.set_title('Hybrid Fitness Evolution', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 2: V1 vs V2 fitness
        ax = axes[0, 1]
        ax.plot(gens, v1_best, 'r-o', linewidth=2, markersize=6, label='V1 (Stability)')
        ax.plot(gens, v2_best, 'c-o', linewidth=2, markersize=6, label='V2 (Emergence)')
        ax.set_xlabel('Generation', fontsize=11)
        ax.set_ylabel('Fitness', fontsize=11)
        ax.set_title('V1 vs V2 Fitness Components', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 3: Metrics breakdown (last generation)
        ax = axes[1, 0]
        last = self.history[-1]
        seeds = list(last.seed_results.keys())
        
        v1_metrics = ['survival', 'stability', 'entropy', 'diversity']
        v2_metrics = ['temporal_entropy', 'spatial_complexity', 'pattern_change_rate', 'novelty']
        
        x = np.arange(len(v1_metrics))
        width = 0.25
        
        for i, seed in enumerate(seeds):
            result = last.seed_results[seed]
            values = [getattr(result, m) for m in v1_metrics]
            ax.bar(x + i*width, values, width, label=seed, alpha=0.8)
        
        ax.set_xticks(x + width)
        ax.set_xticklabels(v1_metrics, rotation=45, ha='right')
        ax.set_ylabel('Score', fontsize=11)
        ax.set_title('V1 Metrics (Stability) by Seed', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        # Plot 4: V2 metrics breakdown
        ax = axes[1, 1]
        x = np.arange(len(v2_metrics))
        
        for i, seed in enumerate(seeds):
            result = last.seed_results[seed]
            values = [getattr(result, m) for m in v2_metrics]
            ax.bar(x + i*width, values, width, label=seed, alpha=0.8)
        
        ax.set_xticks(x + width)
        ax.set_xticklabels(v2_metrics, rotation=45, ha='right')
        ax.set_ylabel('Score', fontsize=11)
        ax.set_title('V2 Metrics (Emergence) by Seed', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.suptitle(
            f'Evolutionary Lenia V3 - Hybrid Fitness (α={self.alpha})',
            fontsize=14, fontweight='bold', y=1.02
        )
        plt.tight_layout()
        
        plot_path = output_dir / 'evolution_v3_hybrid.png'
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return plot_path
    
    def save_results(self, output_dir: Path):
        """Save all results."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save history
        history_data = []
        for r in self.history:
            d = {
                'generation': r.generation,
                'best_hybrid_fitness': r.best_hybrid_fitness,
                'mean_hybrid_fitness': r.mean_hybrid_fitness,
                'best_v1_fitness': r.best_v1_fitness,
                'best_v2_fitness': r.best_v2_fitness,
                'seed_results': {k: v.to_dict() for k, v in r.seed_results.items()},
            }
            history_data.append(d)
        
        with open(output_dir / 'evolution_history_v3.json', 'w') as f:
            json.dump(history_data, f, indent=2)
        
        # Save best genome
        best = self.get_best()
        np.save(output_dir / 'best_genome_v3.npy', best.weights)
        
        # Save config
        with open(output_dir / 'config_v3.json', 'w') as f:
            json.dump(self.config, f, indent=2)
        
        # Plot
        self.plot_results(output_dir)
        
        print(f"\n[OK] Results saved to {output_dir}/")


# ============================================================================
# Main Experiment
# ============================================================================

def create_hybrid_config() -> Dict[str, Any]:
    """Create config for hybrid experiment."""
    return {
        # Population
        'population_size': 16,
        'generations': 8,
        'genome_size': 33,
        
        # Kernel
        'kernel_radius': 15,
        'grid_size': 128,
        
        # Lenia dynamics
        'mu': 0.1622,
        'sigma': 0.0257,
        'dt': 0.1,
        'sim_steps': 200,
        
        # Seeds
        'seeds': ['orbium', 'perturbed', 'multi'],
        
        # Evolution
        'elite_fraction': 0.5,
        'mutation_rate': 0.1,
        'mutation_scale': 0.2,
        
        # Hybrid fitness
        'alpha': 0.5,  # Equal weight to V1 and V2
        
        # Output
        'output_dir': 'output/evo_lenia_v3_hybrid',
        'verbose': True,
    }


def main():
    """Run hybrid evolution experiment."""
    print("="*60)
    print("Evolutionary Lenia V3 - Hybrid Fitness Function")
    print("="*60)
    print("\nCombines:")
    print("  V1: Stability-focused (survival × stability × complexity)")
    print("  V2: Emergence-focused (dynamics × structure × novelty)")
    print("  Hybrid: α × V1 + (1-α) × V2")
    print()
    
    config = create_hybrid_config()
    output_dir = Path(config['output_dir'])
    
    print(f"Configuration:")
    print(f"  Population: {config['population_size']}")
    print(f"  Generations: {config['generations']}")
    print(f"  Simulation steps: {config['sim_steps']}")
    print(f"  Seeds: {config['seeds']}")
    print(f"  Alpha (V1 weight): {config['alpha']}")
    print()
    
    # Create engine and run evolution
    engine = EvolutionEngineV3(config)
    
    t0 = time.time()
    history = engine.evolve()
    elapsed = time.time() - t0
    
    # Summary
    print(f"\n{'='*60}")
    print("EXPERIMENT COMPLETE")
    print(f"{'='*60}")
    print(f"Total time: {elapsed:.1f}s")
    print()
    
    # Best results
    first = history[0]
    final = history[-1]
    
    print("RESULTS SUMMARY:")
    print(f"  Initial best hybrid fitness: {first.best_hybrid_fitness:.6f}")
    print(f"  Final best hybrid fitness:   {final.best_hybrid_fitness:.6f}")
    print(f"  Improvement: {final.best_hybrid_fitness - first.best_hybrid_fitness:+.6f}")
    print()
    
    print("FITNESS COMPONENTS:")
    print(f"  V1 (stability):  {first.best_v1_fitness:.6f} → {final.best_v1_fitness:.6f}")
    print(f"  V2 (emergence):  {first.best_v2_fitness:.6f} → {final.best_v2_fitness:.6f}")
    print()
    
    print("KEY METRICS (Best Genome, averaged over seeds):")
    for seed_name, result in final.seed_results.items():
        print(f"\n  [{seed_name}]")
        print(f"    V1 Metrics:")
        print(f"      survival:  {result.survival:.4f}")
        print(f"      stability: {result.stability:.4f}")
        print(f"      entropy:   {result.entropy:.4f}")
        print(f"      diversity: {result.diversity:.4f}")
        print(f"    V2 Metrics:")
        print(f"      temporal_entropy:    {result.temporal_entropy:.4f}")
        print(f"      spatial_complexity:  {result.spatial_complexity:.4f}")
        print(f"      pattern_change_rate: {result.pattern_change_rate:.4f}")
        print(f"      novelty:             {result.novelty:.4f}")
    print()
    
    # Save results
    engine.save_results(output_dir)
    
    # Pattern observations
    print("\nPATTERN OBSERVATIONS:")
    
    # Check for improvement
    improvement = final.best_hybrid_fitness - first.best_hybrid_fitness
    if improvement > 0:
        print(f"  ✓ Fitness improved by {improvement:.6f}")
    else:
        print(f"  ✗ Fitness did not improve (Δ = {improvement:.6f})")
    
    # Check V1 vs V2 balance
    v1_improvement = final.best_v1_fitness - first.best_v1_fitness
    v2_improvement = final.best_v2_fitness - first.best_v2_fitness
    
    if v1_improvement > 0 and v2_improvement > 0:
        print(f"  ✓ Both V1 and V2 improved (balanced evolution)")
    elif v1_improvement > v2_improvement:
        print(f"  → V1 improved more ({v1_improvement:+.6f} vs {v2_improvement:+.6f})")
    elif v2_improvement > v1_improvement:
        print(f"  → V2 improved more ({v2_improvement:+.6f} vs {v1_improvement:+.6f})")
    
    # Check survival patterns
    avg_survival = np.mean([r.survival for r in final.seed_results.values()])
    if avg_survival > 0.8:
        print(f"  → High survival rate ({avg_survival:.2%}) - patterns are stable")
    elif avg_survival > 0.4:
        print(f"  → Moderate survival ({avg_survival:.2%}) - balance of stability and dynamics")
    else:
        print(f"  → Low survival ({avg_survival:.2%}) - patterns may be too unstable")
    
    # Check dynamics
    avg_change = np.mean([r.pattern_change_rate for r in final.seed_results.values()])
    if avg_change > 0.01:
        print(f"  → Active dynamics (change rate: {avg_change:.4f}) - patterns evolving")
    else:
        print(f"  → Low dynamics (change rate: {avg_change:.4f}) - static patterns")
    
    print(f"\n{'='*60}")
    print("Done!")
    
    return history


if __name__ == '__main__':
    main()
