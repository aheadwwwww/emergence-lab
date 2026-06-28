"""
Evolutionary Lenia V4 - Adaptive for Orbium Seed Survival
===========================================================

Modified V4 experiment targeting single-organism stability.

Key modifications from V4 multiring:
  1. Uses ONLY orbium seed for evaluation (not multi-seed)
  2. Increased mutation_scale (0.15) to escape local optima
  3. Extended generations (15 instead of 10)
  4. Stronger inhibitory outer ring bounds (b2 from -1.0 to 0.5)

Hypothesis: Focusing on orbium seed will force evolution toward
single-organism stability rather than multi-seed patterns.
"""

import jax
import jax.numpy as jnp
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any, Callable
import json
import time

# Import hybrid fitness from V3
from evolutionary_lenia_v3_hybrid import (
    compute_hybrid_fitness,
    HybridFitnessResult,
    get_seed,
)


# ============================================================================
# Multi-Ring Kernel (same as V4)
# ============================================================================

def polynomial_bump(r: np.ndarray) -> np.ndarray:
    """
    Polynomial bump function: (4*r*(1-r))^4
    Maximum at r=0.5, zero at r=0 and r=1.
    """
    r_clipped = np.clip(r, 0, 1)
    return np.where(
        (r_clipped > 0) & (r_clipped < 1),
        (4 * r_clipped * (1 - r_clipped)) ** 4,
        0.0
    )


def gaussian_bump(r: np.ndarray) -> np.ndarray:
    """
    Gaussian-like bump: exp(4 - 1/(r*(1-r)))
    Sharper than polynomial, also max at r=0.5.
    """
    r_clipped = np.clip(r, 1e-6, 1 - 1e-6)
    inner = r_clipped * (1 - r_clipped)
    return np.where(
        (r_clipped > 0) & (r_clipped < 1),
        np.exp(4 - 1 / inner),
        0.0
    )


@dataclass
class RingParams:
    """Parameters for a single ring."""
    radius: float    # r: center of ring (normalized 0-1)
    width: float     # w: width of ring
    weight: float    # b: weight/amplitude (can be negative for inhibitory)
    
    def to_dict(self) -> Dict[str, float]:
        return {'r': float(self.radius), 'w': float(self.width), 'b': float(self.weight)}
    
    @staticmethod
    def from_dict(d: Dict[str, float]) -> 'RingParams':
        return RingParams(d['r'], d['w'], d['b'])


@dataclass
class MultiRingGenome:
    """
    Genome with explicit ring parameters.
    
    Two rings:
      Ring 1: Excitatory (r1, w1, b1)
      Ring 2: Can be inhibitory (r2, w2, b2)
    
    Bump function: 'polynomial' or 'gaussian'
    """
    ring1: RingParams
    ring2: RingParams
    bump_type: str = 'polynomial'
    _cache: Dict = field(default_factory=dict, repr=False)
    
    def to_kernel_fft(self, R: int, size: int) -> jnp.ndarray:
        """Convert ring parameters to FFT-ready kernel."""
        cache_key = (R, size, id(self))
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Select bump function
        if self.bump_type == 'polynomial':
            bump = polynomial_bump
        else:
            bump = gaussian_bump
        
        # Build kernel grid
        kernel_hw = 2 * R + 1
        y, x = np.ogrid[-R:R+1, -R:R+1]
        r_norm = np.sqrt(x*x + y*y) / R  # Normalized radius [0, 1+]
        mask = r_norm <= 1.0
        
        # Compute kernel value from two rings
        kernel = np.zeros((kernel_hw, kernel_hw), dtype=np.float32)
        
        # Ring 1 contribution
        r1_scaled = (r_norm - self.ring1.radius) / (self.ring1.width + 1e-8)
        kernel += self.ring1.weight * bump(r1_scaled) * mask
        
        # Ring 2 contribution
        r2_scaled = (r_norm - self.ring2.radius) / (self.ring2.width + 1e-8)
        kernel += self.ring2.weight * bump(r2_scaled) * mask
        
        # Normalize (sum to 1 for conservation)
        kernel_sum = np.abs(kernel).sum()
        if kernel_sum > 1e-8:
            kernel = kernel / kernel_sum
        
        # Pad to full grid size
        kernel_padded = np.zeros((size, size), dtype=np.float32)
        off = size // 2 - R
        kernel_padded[off:off+kernel_hw, off:off+kernel_hw] = kernel
        
        # FFT
        kernel_fft = jnp.fft.fft2(jnp.array(kernel_padded))
        self._cache[cache_key] = kernel_fft
        return kernel_fft
    
    def to_param_vector(self) -> np.ndarray:
        """Flatten to vector for GA operations."""
        return np.array([
            self.ring1.radius,
            self.ring1.width,
            self.ring1.weight,
            self.ring2.radius,
            self.ring2.width,
            self.ring2.weight,
        ], dtype=np.float32)
    
    @staticmethod
    def from_param_vector(params: np.ndarray, bump_type: str = 'polynomial') -> 'MultiRingGenome':
        """Create genome from parameter vector."""
        return MultiRingGenome(
            ring1=RingParams(
                radius=params[0],
                width=params[1],
                weight=params[2],
            ),
            ring2=RingParams(
                radius=params[3],
                width=params[4],
                weight=params[5],
            ),
            bump_type=bump_type,
        )
    
    @staticmethod
    def random(bump_type: str = 'polynomial', seed: Optional[int] = None) -> 'MultiRingGenome':
        """Create random genome within valid parameter ranges."""
        if seed is not None:
            np.random.seed(seed)
        
        # Ring 1: Excitatory (positive weight)
        r1 = np.random.uniform(0.3, 0.7)
        w1 = np.random.uniform(0.05, 0.2)
        b1 = np.random.uniform(0.5, 1.5)
        
        # Ring 2: Can be inhibitory (allow negative weight)
        # ADAPTIVE: Increased negative range for stronger inhibition
        r2 = np.random.uniform(0.5, 0.9)
        w2 = np.random.uniform(0.05, 0.2)
        b2 = np.random.uniform(-1.0, 0.5)  # MODIFIED: was [-0.5, 0.5]
        
        return MultiRingGenome(
            ring1=RingParams(r1, w1, b1),
            ring2=RingParams(r2, w2, b2),
            bump_type=bump_type,
        )
    
    def clone(self) -> 'MultiRingGenome':
        return MultiRingGenome(
            ring1=RingParams(self.ring1.radius, self.ring1.width, self.ring1.weight),
            ring2=RingParams(self.ring2.radius, self.ring2.width, self.ring2.weight),
            bump_type=self.bump_type,
        )


# ============================================================================
# Lenia Simulation
# ============================================================================

class LeniaSimulatorV4:
    """Lenia simulator for multi-ring kernels."""
    
    def __init__(self, config: Dict[str, Any]):
        self.size = config['grid_size']
        self.R = config['kernel_radius']
        self.mu = config['mu']
        self.sigma = config['sigma']
        self.dt = config['dt']
        self.steps = config['sim_steps']
    
    def run(self, genome: MultiRingGenome, seed_name: str) -> List[np.ndarray]:
        """Run simulation and return history."""
        kernel_fft = genome.to_kernel_fft(self.R, self.size)
        seed = get_seed(seed_name, self.size)
        
        grid = jnp.array(seed)
        history = [np.array(grid)]
        
        for step in range(self.steps):
            grid_fft = jnp.fft.fft2(grid)
            conv = jnp.fft.ifft2(grid_fft * kernel_fft).real
            growth = jnp.exp(-((conv - self.mu) ** 2) / (2 * self.sigma ** 2)) * 2 - 1
            grid = jnp.clip(grid + self.dt * growth, 0, 1)
            if step % 20 == 0:
                history.append(np.array(grid))
        
        history.append(np.array(grid))
        return history


# ============================================================================
# Evolution Engine V4 Adaptive
# ============================================================================

# ADAPTIVE: Modified parameter bounds for stronger inhibition
PARAM_BOUNDS_ADAPTIVE = {
    'r1': (0.3, 0.7),
    'w1': (0.05, 0.2),
    'b1': (0.5, 1.5),
    'r2': (0.5, 0.9),
    'w2': (0.05, 0.2),
    'b2': (-1.0, 0.5),  # MODIFIED: was [-0.5, 0.5]
}


def clip_params_adaptive(params: np.ndarray) -> np.ndarray:
    """Clip parameters to valid ranges (adaptive version)."""
    clipped = params.copy()
    clipped[0] = np.clip(clipped[0], *PARAM_BOUNDS_ADAPTIVE['r1'])
    clipped[1] = np.clip(clipped[1], *PARAM_BOUNDS_ADAPTIVE['w1'])
    clipped[2] = np.clip(clipped[2], *PARAM_BOUNDS_ADAPTIVE['b1'])
    clipped[3] = np.clip(clipped[3], *PARAM_BOUNDS_ADAPTIVE['r2'])
    clipped[4] = np.clip(clipped[4], *PARAM_BOUNDS_ADAPTIVE['w2'])
    clipped[5] = np.clip(clipped[5], *PARAM_BOUNDS_ADAPTIVE['b2'])
    return clipped


@dataclass
class GenerationResultV4:
    """Results for one generation."""
    generation: int
    best_hybrid_fitness: float
    mean_hybrid_fitness: float
    best_v1_fitness: float
    best_v2_fitness: float
    best_genome: MultiRingGenome
    seed_results: Dict[str, HybridFitnessResult]


class EvolutionEngineV4Adaptive:
    """
    Evolution engine for multi-ring kernels (adaptive version).
    
    Key differences from V4:
      - Uses only orbium seed
      - Increased mutation_scale (0.15)
      - Extended generations (15)
      - Stronger inhibitory bounds
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.simulator = LeniaSimulatorV4(config)
        self.history: List[GenerationResultV4] = []
        self.population: List[MultiRingGenome] = []
        self.alpha = config.get('alpha', 0.5)
        self.bump_type = config.get('bump_type', 'polynomial')
    
    def _evaluate(self, genome: MultiRingGenome) -> Tuple[float, Dict[str, HybridFitnessResult]]:
        """Evaluate genome on all seeds."""
        seed_results = {}
        total_hybrid = 0.0
        
        for seed_name in self.config['seeds']:
            history = self.simulator.run(genome, seed_name)
            result = compute_hybrid_fitness(history, self.alpha)
            seed_results[seed_name] = result
            total_hybrid += result.hybrid_fitness
        
        return total_hybrid, seed_results
    
    def _crossover(self, p1: MultiRingGenome, p2: MultiRingGenome) -> MultiRingGenome:
        """Blend crossover for real-valued parameters."""
        v1 = p1.to_param_vector()
        v2 = p2.to_param_vector()
        
        # Blend alpha crossover
        alpha_blend = 0.5
        child_v = alpha_blend * v1 + (1 - alpha_blend) * v2
        
        # Add small noise for diversity
        child_v += np.random.randn(6) * 0.02
        
        child_v = clip_params_adaptive(child_v)
        return MultiRingGenome.from_param_vector(child_v, self.bump_type)
    
    def _mutate(self, genome: MultiRingGenome) -> MultiRingGenome:
        """Gaussian mutation on parameters."""
        params = genome.to_param_vector()
        
        # Mutate each parameter with some probability
        for i in range(6):
            if np.random.random() < self.config['mutation_rate']:
                params[i] += np.random.randn() * self.config['mutation_scale']
        
        params = clip_params_adaptive(params)
        return MultiRingGenome.from_param_vector(params, self.bump_type)
    
    def evolve(self) -> List[GenerationResultV4]:
        """Run evolution."""
        pop_size = self.config['population_size']
        elite_n = max(1, int(pop_size * self.config['elite_fraction']))
        
        # Initialize population
        self.population = [
            MultiRingGenome.random(self.bump_type, seed=i)
            for i in range(pop_size)
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
                    print(f"  [{i+1}/{pop_size}] hybrid={avg_hybrid:.4f} "
                          f"r1={genome.ring1.radius:.3f} b1={genome.ring1.weight:.3f}")
            
            # Record stats
            best_idx = int(np.argmax(scores))
            best_genome = self.population[best_idx]
            best_seeds = seed_details[best_idx]
            
            gen_result = GenerationResultV4(
                generation=gen + 1,
                best_hybrid_fitness=float(scores[best_idx]),
                mean_hybrid_fitness=float(np.mean(scores)),
                best_v1_fitness=float(np.mean([r.v1_fitness for r in best_seeds.values()])),
                best_v2_fitness=float(np.mean([r.v2_fitness for r in best_seeds.values()])),
                best_genome=best_genome.clone(),
                seed_results=best_seeds,
            )
            self.history.append(gen_result)
            
            if self.config['verbose']:
                print(f"\n  Best hybrid: {gen_result.best_hybrid_fitness:.4f}")
                print(f"  Best V1:     {gen_result.best_v1_fitness:.4f}")
                print(f"  Best V2:     {gen_result.best_v2_fitness:.4f}")
                print(f"  Mean:        {gen_result.mean_hybrid_fitness:.4f}")
                print(f"  Best params: r1={best_genome.ring1.radius:.3f} "
                      f"w1={best_genome.ring1.width:.3f} b1={best_genome.ring1.weight:.3f}")
                print(f"               r2={best_genome.ring2.radius:.3f} "
                      f"w2={best_genome.ring2.width:.3f} b2={best_genome.ring2.weight:.3f}")
            
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
    
    def plot_results(self, output_dir: Path):
        """Create evolution plots."""
        fig, axes = plt.subplots(2, 3, figsize=(16, 10))
        
        gens = [r.generation for r in self.history]
        hybrid_best = [r.best_hybrid_fitness for r in self.history]
        hybrid_mean = [r.mean_hybrid_fitness for r in self.history]
        v1_best = [r.best_v1_fitness for r in self.history]
        v2_best = [r.best_v2_fitness for r in self.history]
        
        # Plot 1: Hybrid fitness
        ax = axes[0, 0]
        ax.plot(gens, hybrid_best, 'b-o', linewidth=2, markersize=6, label='Best')
        ax.plot(gens, hybrid_mean, 'g--', linewidth=1.5, label='Mean')
        ax.fill_between(gens, hybrid_mean, hybrid_best, alpha=0.15)
        ax.set_xlabel('Generation', fontsize=11)
        ax.set_ylabel('Hybrid Fitness', fontsize=11)
        ax.set_title('Hybrid Fitness Evolution', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 2: V1 vs V2
        ax = axes[0, 1]
        ax.plot(gens, v1_best, 'r-o', linewidth=2, markersize=6, label='V1 (Stability)')
        ax.plot(gens, v2_best, 'c-o', linewidth=2, markersize=6, label='V2 (Emergence)')
        ax.set_xlabel('Generation', fontsize=11)
        ax.set_ylabel('Fitness', fontsize=11)
        ax.set_title('V1 vs V2 Components', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 3: Ring parameters over time
        ax = axes[0, 2]
        r1_vals = [r.best_genome.ring1.radius for r in self.history]
        r2_vals = [r.best_genome.ring2.radius for r in self.history]
        ax.plot(gens, r1_vals, 'b-o', linewidth=2, markersize=6, label='Ring 1 radius')
        ax.plot(gens, r2_vals, 'r-o', linewidth=2, markersize=6, label='Ring 2 radius')
        ax.set_xlabel('Generation', fontsize=11)
        ax.set_ylabel('Radius', fontsize=11)
        ax.set_title('Ring Radii Evolution', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 4: Ring weights
        ax = axes[1, 0]
        b1_vals = [r.best_genome.ring1.weight for r in self.history]
        b2_vals = [r.best_genome.ring2.weight for r in self.history]
        ax.plot(gens, b1_vals, 'b-o', linewidth=2, markersize=6, label='Ring 1 weight (excitatory)')
        ax.plot(gens, b2_vals, 'r-o', linewidth=2, markersize=6, label='Ring 2 weight (inhibitory)')
        ax.axhline(y=0, color='k', linestyle='--', alpha=0.3)
        ax.set_xlabel('Generation', fontsize=11)
        ax.set_ylabel('Weight', fontsize=11)
        ax.set_title('Ring Weights Evolution', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 5: Kernel visualization
        ax = axes[1, 1]
        best_genome = self.history[-1].best_genome
        # Compute kernel for visualization
        R = self.config['kernel_radius']
        y, x = np.ogrid[-R:R+1, -R:R+1]
        r_norm = np.sqrt(x*x + y*y) / R
        
        if self.bump_type == 'polynomial':
            bump = polynomial_bump
        else:
            bump = gaussian_bump
        
        r1_scaled = (r_norm - best_genome.ring1.radius) / (best_genome.ring1.width + 1e-8)
        r2_scaled = (r_norm - best_genome.ring2.radius) / (best_genome.ring2.width + 1e-8)
        
        kernel_2d = (best_genome.ring1.weight * bump(r1_scaled) +
                     best_genome.ring2.weight * bump(r2_scaled))
        kernel_2d = kernel_2d * (r_norm <= 1.0)
        
        im = ax.imshow(kernel_2d, cmap='RdBu_r', aspect='equal')
        ax.set_title('Best Kernel (2D)', fontsize=12, fontweight='bold')
        ax.axis('off')
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        
        # Plot 6: 1D kernel profile
        ax = axes[1, 2]
        r_1d = np.linspace(0, 1, 100)
        k1_1d = best_genome.ring1.weight * bump((r_1d - best_genome.ring1.radius) / best_genome.ring1.width)
        k2_1d = best_genome.ring2.weight * bump((r_1d - best_genome.ring2.radius) / best_genome.ring2.width)
        
        ax.plot(r_1d, k1_1d, 'b-', linewidth=2, label='Ring 1 (excitatory)')
        ax.plot(r_1d, k2_1d, 'r-', linewidth=2, label='Ring 2 (inhibitory)')
        ax.plot(r_1d, k1_1d + k2_1d, 'k--', linewidth=2, label='Combined')
        ax.axhline(y=0, color='gray', linestyle=':', alpha=0.5)
        ax.set_xlabel('Normalized radius', fontsize=11)
        ax.set_ylabel('Kernel value', fontsize=11)
        ax.set_title('1D Kernel Profile', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.suptitle(
            f'Evolutionary Lenia V4 Adaptive - Orbium Seed Focus ({self.bump_type.title()} Bump)',
            fontsize=14, fontweight='bold', y=1.02
        )
        plt.tight_layout()
        
        plot_path = output_dir / 'evolution_v4_adaptive.png'
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
                'best_genome': {
                    'ring1': r.best_genome.ring1.to_dict(),
                    'ring2': r.best_genome.ring2.to_dict(),
                    'bump_type': r.best_genome.bump_type,
                },
                'seed_results': {k: v.to_dict() for k, v in r.seed_results.items()},
            }
            history_data.append(d)
        
        with open(output_dir / 'evolution_history_v4_adaptive.json', 'w') as f:
            json.dump(history_data, f, indent=2)
        
        # Save best genome parameters
        best_params = self.history[-1].best_genome.to_param_vector()
        np.save(output_dir / 'best_genome_v4_adaptive_params.npy', best_params)
        
        # Save config
        with open(output_dir / 'config_v4_adaptive.json', 'w') as f:
            json.dump(self.config, f, indent=2)
        
        # Plot
        self.plot_results(output_dir)
        
        print(f"\n[OK] Results saved to {output_dir}/")


# ============================================================================
# Main Experiment
# ============================================================================

def create_adaptive_config() -> Dict[str, Any]:
    """Create config for adaptive orbium-focused experiment."""
    return {
        # Population
        'population_size': 20,
        'generations': 15,  # MODIFIED: was 10
        
        # Kernel
        'kernel_radius': 15,
        'grid_size': 128,
        
        # Lenia dynamics
        'mu': 0.1622,
        'sigma': 0.0257,
        'dt': 0.1,
        'sim_steps': 200,
        
        # Seeds - MODIFIED: only orbium
        'seeds': ['orbium'],
        
        # Evolution
        'elite_fraction': 0.5,
        'mutation_rate': 0.15,
        'mutation_scale': 0.15,  # MODIFIED: was 0.1
        
        # Hybrid fitness
        'alpha': 0.5,
        
        # Bump function
        'bump_type': 'polynomial',  # or 'gaussian'
        
        # Output
        'output_dir': 'output/evo_lenia_v4_adaptive',
        'verbose': True,
    }


def main():
    """Run adaptive evolution experiment targeting orbium seed survival."""
    print("="*60)
    print("Evolutionary Lenia V4 Adaptive - Orbium Seed Focus")
    print("="*60)
    print("\nKey Modifications from V4 Multiring:")
    print("  1. Seeds: ONLY orbium (was ['orbium', 'perturbed', 'multi'])")
    print("  2. Mutation scale: 0.15 (was 0.1)")
    print("  3. Generations: 15 (was 10)")
    print("  4. Ring2 weight bounds: [-1.0, 0.5] (was [-0.5, 0.5])")
    print()
    print("Hypothesis:")
    print("  Focusing on orbium seed will force evolution toward")
    print("  single-organism stability rather than multi-seed patterns.")
    print()
    
    config = create_adaptive_config()
    output_dir = Path(config['output_dir'])
    
    print(f"Configuration:")
    print(f"  Population: {config['population_size']}")
    print(f"  Generations: {config['generations']}")
    print(f"  Simulation steps: {config['sim_steps']}")
    print(f"  Seeds: {config['seeds']}")
    print(f"  Bump function: {config['bump_type']}")
    print(f"  Alpha (V1 weight): {config['alpha']}")
    print(f"  Mutation scale: {config['mutation_scale']}")
    print()
    
    # Run polynomial bump experiment
    print("\n" + "="*60)
    print("Running with POLYNOMIAL bump function")
    print("="*60)
    
    config['bump_type'] = 'polynomial'
    engine_poly = EvolutionEngineV4Adaptive(config)
    
    t0 = time.time()
    history_poly = engine_poly.evolve()
    elapsed_poly = time.time() - t0
    
    # Summary
    print(f"\n{'='*60}")
    print("POLYNOMIAL BUMP EXPERIMENT COMPLETE")
    print(f"{'='*60}")
    print(f"Total time: {elapsed_poly:.1f}s")
    
    first_poly = history_poly[0]
    final_poly = history_poly[-1]
    
    print(f"\nRESULTS (Polynomial):")
    print(f"  Initial best: {first_poly.best_hybrid_fitness:.6f}")
    print(f"  Final best:   {final_poly.best_hybrid_fitness:.6f}")
    print(f"  Improvement:  {final_poly.best_hybrid_fitness - first_poly.best_hybrid_fitness:+.6f}")
    
    print(f"\nBEST KERNEL PARAMETERS:")
    best_genome = final_poly.best_genome
    print(f"  Ring 1: r={best_genome.ring1.radius:.4f}, "
          f"w={best_genome.ring1.width:.4f}, b={best_genome.ring1.weight:.4f}")
    print(f"  Ring 2: r={best_genome.ring2.radius:.4f}, "
          f"w={best_genome.ring2.width:.4f}, b={best_genome.ring2.weight:.4f}")
    
    # Check orbium seed survival
    orbium_result = final_poly.seed_results.get('orbium')
    if orbium_result:
        print(f"\nORBIUM SEED PERFORMANCE:")
        print(f"  Hybrid fitness: {orbium_result.hybrid_fitness:.6f}")
        print(f"  V1 (stability): {orbium_result.v1_fitness:.6f}")
        print(f"  V2 (emergence): {orbium_result.v2_fitness:.6f}")
    
    # Save results
    engine_poly.save_results(output_dir)
    
    # Run Gaussian bump experiment
    print("\n" + "="*60)
    print("Running with GAUSSIAN bump function")
    print("="*60)
    
    config['bump_type'] = 'gaussian'
    output_dir_gauss = Path(str(output_dir).replace('adaptive', 'adaptive_gaussian'))
    config['output_dir'] = str(output_dir_gauss)
    
    engine_gauss = EvolutionEngineV4Adaptive(config)
    
    t0 = time.time()
    history_gauss = engine_gauss.evolve()
    elapsed_gauss = time.time() - t0
    
    # Summary
    print(f"\n{'='*60}")
    print("GAUSSIAN BUMP EXPERIMENT COMPLETE")
    print(f"{'='*60}")
    print(f"Total time: {elapsed_gauss:.1f}s")
    
    first_gauss = history_gauss[0]
    final_gauss = history_gauss[-1]
    
    print(f"\nRESULTS (Gaussian):")
    print(f"  Initial best: {first_gauss.best_hybrid_fitness:.6f}")
    print(f"  Final best:   {final_gauss.best_hybrid_fitness:.6f}")
    print(f"  Improvement:  {final_gauss.best_hybrid_fitness - first_gauss.best_hybrid_fitness:+.6f}")
    
    print(f"\nBEST KERNEL PARAMETERS:")
    best_genome_gauss = final_gauss.best_genome
    print(f"  Ring 1: r={best_genome_gauss.ring1.radius:.4f}, "
          f"w={best_genome_gauss.ring1.width:.4f}, b={best_genome_gauss.ring1.weight:.4f}")
    print(f"  Ring 2: r={best_genome_gauss.ring2.radius:.4f}, "
          f"w={best_genome_gauss.ring2.width:.4f}, b={best_genome_gauss.ring2.weight:.4f}")
    
    # Check orbium seed survival
    orbium_result_gauss = final_gauss.seed_results.get('orbium')
    if orbium_result_gauss:
        print(f"\nORBIUM SEED PERFORMANCE:")
        print(f"  Hybrid fitness: {orbium_result_gauss.hybrid_fitness:.6f}")
        print(f"  V1 (stability): {orbium_result_gauss.v1_fitness:.6f}")
        print(f"  V2 (emergence): {orbium_result_gauss.v2_fitness:.6f}")
    
    # Save Gaussian results
    engine_gauss.save_results(output_dir_gauss)
    
    # Compare bump functions
    print(f"\n{'='*60}")
    print("FINAL COMPARISON")
    print(f"{'='*60}")
    
    print(f"\nBUMP FUNCTION COMPARISON:")
    print(f"  Polynomial final: {final_poly.best_hybrid_fitness:.6f}")
    print(f"  Gaussian final:   {final_gauss.best_hybrid_fitness:.6f}")
    
    if final_poly.best_hybrid_fitness > final_gauss.best_hybrid_fitness:
        print(f"  → Polynomial bump performed better for orbium seed")
        best_overall = final_poly
        best_bump = 'polynomial'
    else:
        print(f"  → Gaussian bump performed better for orbium seed")
        best_overall = final_gauss
        best_bump = 'gaussian'
    
    print(f"\nORBIUM SEED SURVIVAL ANALYSIS:")
    print(f"  Best approach: {best_bump} bump")
    print(f"  Best hybrid fitness: {best_overall.best_hybrid_fitness:.6f}")
    print(f"  Best V1 (stability): {best_overall.best_v1_fitness:.6f}")
    print(f"  Best V2 (emergence): {best_overall.best_v2_fitness:.6f}")
    
    # Compare with V4 multiring results if available
    v4_multiring_output = Path('output/evo_lenia_v4_multiring/evolution_history_v4.json')
    if v4_multiring_output.exists():
        with open(v4_multiring_output, 'r') as f:
            v4_history = json.load(f)
        
        print(f"\nCOMPARISON WITH V4 MULTIRING:")
        print(f"  V4 multiring final: {v4_history[-1]['best_hybrid_fitness']:.6f}")
        print(f"  V4 adaptive final:  {best_overall.best_hybrid_fitness:.6f}")
        
        if best_overall.best_hybrid_fitness > v4_history[-1]['best_hybrid_fitness']:
            print(f"  → Adaptive approach improved orbium seed survival!")
        else:
            print(f"  → V4 multiring still performs better")
    
    print(f"\n{'='*60}")
    print("Done!")
    
    return history_poly, history_gauss


if __name__ == '__main__':
    main()
