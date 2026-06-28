"""
Evolutionary Lenia V5 - Joint Kernel + Growth Parameter Evolution
==================================================================

KEY INSIGHT from official Lenia reference (Chakazul/Lenia):
- Orbium:  m=0.15, s=0.015
- Gyrorbium: m=0.156, s=0.0224
- Scutium: m=0.29, s=0.045
- Hydrogeminium: m=0.26, s=0.036

The growth function parameters (m, s) vary SIGNIFICANTLY across species!
Previous experiments fixed mu=0.1622, sigma=0.0257 which limited discovery.

V5 Approach:
1. Evolve kernel shape (via NN weights)
2. Evolve growth parameters (mu, sigma) simultaneously
3. Use hybrid V1+V2 fitness function

Genome = [kernel_weights (33) | mu (1) | sigma (1)] = 35 parameters
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
from evolutionary_lenia_v3_hybrid import (
    compute_hybrid_fitness,
    HybridFitnessResult,
    get_seed,
    create_orbium_seed,
    create_perturbed_seed,
    create_multi_seed,
)


@dataclass
class GenomeV5:
    """
    Extended genome including growth parameters.
    
    Layout:
    - weights[0:32]: NN weights for kernel shape
    - weights[32]: mu (growth center) - mapped to [0.1, 0.35]
    - weights[33]: sigma (growth width) - mapped to [0.01, 0.05]
    """
    weights: np.ndarray  # Shape: (34,)
    
    @classmethod
    def random(cls, size: int = 34) -> 'GenomeV5':
        """Create random genome with reasonable defaults."""
        weights = np.random.randn(size).astype(np.float32) * 0.5
        # Initialize mu and sigma with good values
        weights[32] = 0.0  # Will map to mu=0.225 (middle of range)
        weights[33] = 0.0  # Will map to sigma=0.03 (middle of range)
        return cls(weights)
    
    @classmethod
    def from_params(cls, kernel_weights: np.ndarray, mu: float, sigma: float) -> 'GenomeV5':
        """Create genome from kernel weights and growth params."""
        weights = np.zeros(34, dtype=np.float32)
        weights[:32] = kernel_weights[:32]
        # Map mu [0.1, 0.35] -> [-1, 1]
        weights[32] = (mu - 0.225) / 0.125
        # Map sigma [0.01, 0.05] -> [-1, 1]
        weights[33] = (sigma - 0.03) / 0.02
        return cls(weights)
    
    def get_kernel_weights(self) -> np.ndarray:
        """Get NN weights for kernel."""
        return self.weights[:32]
    
    def get_mu(self) -> float:
        """Get growth center parameter."""
        # Map from genome value to [0.1, 0.35]
        return float(0.225 + 0.125 * np.clip(self.weights[32], -1, 1))
    
    def get_sigma(self) -> float:
        """Get growth width parameter."""
        # Map from genome value to [0.01, 0.05]
        return float(0.03 + 0.02 * np.clip(self.weights[33], -1, 1))
    
    def clone(self) -> 'GenomeV5':
        return GenomeV5(self.weights.copy())


class LeniaSimulatorV5:
    """Lenia simulator with evolvable growth parameters."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.kernel_radius = config['kernel_radius']
        self.grid_size = config['grid_size']
        self.dt = config.get('dt', 0.1)
        
    def simulate(self, genome: GenomeV5, seed: np.ndarray) -> List[np.ndarray]:
        """Run simulation with genome-specified parameters."""
        # Get parameters from genome
        mu = genome.get_mu()
        sigma = genome.get_sigma()
        kernel_weights = genome.get_kernel_weights()
        
        # Build kernel from NN weights
        kernel = self._build_kernel(kernel_weights)
        kernel_fft = jnp.fft.fft2(jnp.array(kernel))
        
        # Initialize grid
        grid = jnp.array(seed)
        history = [np.array(grid)]
        
        sim_steps = self.config.get('sim_steps', 200)
        
        for step in range(sim_steps):
            # FFT convolution
            grid_fft = jnp.fft.fft2(grid)
            conv = jnp.fft.ifft2(grid_fft * kernel_fft).real
            
            # Growth function with genome-specified mu and sigma
            growth = jnp.exp(-((conv - mu) ** 2) / (2 * sigma ** 2)) * 2 - 1
            
            # Update
            grid = jnp.clip(grid + self.dt * growth, 0, 1)
            
            if step % 20 == 0:
                history.append(np.array(grid))
        
        history.append(np.array(grid))
        return history
    
    def _build_kernel(self, weights: np.ndarray) -> np.ndarray:
        """Build kernel using simple parameterization."""
        R = self.kernel_radius
        size = self.grid_size
        mid = size // 2
        
        # Create coordinate grid
        y, x = np.ogrid[:size, :size]
        y = (y - mid) / R
        x = (x - mid) / R
        r = np.sqrt(x**2 + y**2)
        
        # Simple ring kernel with weights
        # weights[0]: center of ring (r0) in [0, 1]
        # weights[1]: width of ring in [0, 1]
        # weights[2]: amplitude
        
        r0 = 0.5 + 0.3 * np.clip(weights[0] if len(weights) > 0 else 0, -1, 1)
        width = 0.1 + 0.15 * np.clip(weights[1] if len(weights) > 1 else 0, -1, 1)
        amp = np.clip(weights[2] if len(weights) > 2 else 1, 0.5, 2.0)
        
        # Gaussian ring
        kernel = np.exp(-((r - r0) ** 2) / (2 * width ** 2)) * amp
        kernel = kernel / (kernel.sum() + 1e-8)
        
        return kernel.astype(np.float32)


@dataclass
class GenerationResultV5:
    """Results for one generation."""
    generation: int
    best_hybrid_fitness: float
    mean_hybrid_fitness: float
    best_mu: float
    best_sigma: float
    seed_results: Dict[str, HybridFitnessResult]


class EvolutionEngineV5:
    """
    Evolution engine with joint kernel + growth parameter optimization.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.simulator = LeniaSimulatorV5(config)
        self.history: List[GenerationResultV5] = []
        self.population: List[GenomeV5] = []
        
    def _evaluate(self, genome: GenomeV5) -> Tuple[float, Dict[str, HybridFitnessResult]]:
        """Evaluate genome on all seeds."""
        seed_results = {}
        total_fitness = 0.0
        
        for seed_name in self.config['seeds']:
            seed = get_seed(seed_name, self.config['grid_size'])
            history = self.simulator.simulate(genome, seed)
            
            result = compute_hybrid_fitness(history, alpha=0.5)
            seed_results[seed_name] = result
            total_fitness += result.hybrid_fitness
        
        return total_fitness, seed_results
    
    def _crossover(self, p1: GenomeV5, p2: GenomeV5) -> GenomeV5:
        """Uniform crossover."""
        mask = np.random.rand(34) < 0.5
        child_weights = np.where(mask, p1.weights, p2.weights)
        return GenomeV5(child_weights.astype(np.float32))
    
    def _mutate(self, genome: GenomeV5) -> GenomeV5:
        """Gaussian mutation."""
        mutated = genome.weights.copy()
        n_mutate = max(1, np.random.binomial(34, self.config['mutation_rate']))
        indices = np.random.choice(34, n_mutate, replace=False)
        mutated[indices] += np.random.randn(n_mutate) * self.config['mutation_scale']
        return GenomeV5(mutated.astype(np.float32))
    
    def evolve(self) -> List[GenerationResultV5]:
        """Run evolution."""
        pop_size = self.config['population_size']
        elite_n = max(1, int(pop_size * self.config['elite_fraction']))
        
        # Initialize population with diverse growth parameters
        self.population = []
        for i in range(pop_size):
            g = GenomeV5.random(34)
            # Spread initial mu and sigma values
            g.weights[32] = np.random.uniform(-1, 1)  # mu
            g.weights[33] = np.random.uniform(-1, 1)  # sigma
            self.population.append(g)
        
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
                    print(f"  [{i+1}/{pop_size}] hybrid={avg_hybrid:.4f} mu={genome.get_mu():.3f} sigma={genome.get_sigma():.4f}")
            
            # Record stats
            best_idx = int(np.argmax(scores))
            best_genome = self.population[best_idx]
            best_seeds = seed_details[best_idx]
            
            gen_result = GenerationResultV5(
                generation=gen + 1,
                best_hybrid_fitness=float(scores[best_idx]),
                mean_hybrid_fitness=float(np.mean(scores)),
                best_mu=best_genome.get_mu(),
                best_sigma=best_genome.get_sigma(),
                seed_results=best_seeds,
            )
            self.history.append(gen_result)
            
            if self.config['verbose']:
                print(f"\n  Best hybrid: {gen_result.best_hybrid_fitness:.4f}")
                print(f"  Best mu:     {gen_result.best_mu:.4f}")
                print(f"  Best sigma:  {gen_result.best_sigma:.4f}")
                print(f"  Mean:        {gen_result.mean_hybrid_fitness:.4f}")
            
            # Selection and variation
            if gen < self.config['generations'] - 1:
                ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
                elite = [self.population[i].clone() for i, _ in ranked[:elite_n]]
                
                new_pop = elite.copy()
                
                while len(new_pop) < pop_size:
                    # Tournament selection
                    idxs = np.random.choice(len(new_pop), min(3, len(new_pop)), replace=False)
                    parent1 = new_pop[idxs[0]]
                    
                    idxs2 = np.random.choice(len(new_pop), min(3, len(new_pop)), replace=False)
                    parent2 = new_pop[idxs2[0]]
                    
                    child = self._crossover(parent1, parent2)
                    child = self._mutate(child)
                    new_pop.append(child)
                
                self.population = new_pop
        
        return self.history
    
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
                'best_mu': r.best_mu,
                'best_sigma': r.best_sigma,
                'seed_results': {k: v.to_dict() for k, v in r.seed_results.items()},
            }
            history_data.append(d)
        
        with open(output_dir / 'evolution_history_v5.json', 'w') as f:
            json.dump(history_data, f, indent=2)
        
        # Save best genome
        best_idx = np.argmax([r.best_hybrid_fitness for r in self.history])
        best = self.population[0]  # Simplified
        np.save(output_dir / 'best_genome_v5.npy', best.weights)
        
        # Save config
        with open(output_dir / 'config_v5.json', 'w') as f:
            json.dump(self.config, f, indent=2)
        
        # Create plots
        self._plot_results(output_dir)
        
        print(f"\n[OK] Results saved to {output_dir}/")
    
    def _plot_results(self, output_dir: Path):
        """Create evolution plots."""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        gens = [r.generation for r in self.history]
        hybrid_best = [r.best_hybrid_fitness for r in self.history]
        hybrid_mean = [r.mean_hybrid_fitness for r in self.history]
        mu_vals = [r.best_mu for r in self.history]
        sigma_vals = [r.best_sigma for r in self.history]
        
        # Plot 1: Hybrid fitness
        ax = axes[0, 0]
        ax.plot(gens, hybrid_best, 'b-o', linewidth=2, markersize=6, label='Best')
        ax.plot(gens, hybrid_mean, 'g--', linewidth=1.5, label='Mean')
        ax.set_xlabel('Generation')
        ax.set_ylabel('Hybrid Fitness')
        ax.set_title('Fitness Evolution')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 2: Growth parameter mu
        ax = axes[0, 1]
        ax.plot(gens, mu_vals, 'r-o', linewidth=2, markersize=6)
        ax.axhline(y=0.15, color='gray', linestyle='--', alpha=0.5, label='Orbium (0.15)')
        ax.axhline(y=0.156, color='blue', linestyle='--', alpha=0.5, label='Gyrorbium (0.156)')
        ax.axhline(y=0.29, color='green', linestyle='--', alpha=0.5, label='Scutium (0.29)')
        ax.set_xlabel('Generation')
        ax.set_ylabel('mu (growth center)')
        ax.set_title('Evolved mu Parameter')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        
        # Plot 3: Growth parameter sigma
        ax = axes[1, 0]
        ax.plot(gens, sigma_vals, 'c-o', linewidth=2, markersize=6)
        ax.axhline(y=0.015, color='gray', linestyle='--', alpha=0.5, label='Orbium (0.015)')
        ax.axhline(y=0.0224, color='blue', linestyle='--', alpha=0.5, label='Gyrorbium (0.0224)')
        ax.axhline(y=0.045, color='green', linestyle='--', alpha=0.5, label='Scutium (0.045)')
        ax.set_xlabel('Generation')
        ax.set_ylabel('sigma (growth width)')
        ax.set_title('Evolved sigma Parameter')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        
        # Plot 4: Metrics comparison
        ax = axes[1, 1]
        if self.history:
            last = self.history[-1]
            seeds = list(last.seed_results.keys())
            
            v1_metrics = ['survival', 'stability', 'entropy']
            x = np.arange(len(v1_metrics))
            width = 0.25
            
            for i, seed in enumerate(seeds):
                result = last.seed_results[seed]
                values = [getattr(result, m) for m in v1_metrics]
                ax.bar(x + i*width, values, width, label=seed, alpha=0.8)
            
            ax.set_xticks(x + width)
            ax.set_xticklabels(v1_metrics)
            ax.set_ylabel('Score')
            ax.set_title('Final V1 Metrics by Seed')
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')
        
        plt.suptitle('Evolutionary Lenia V5 - Joint Kernel + Growth Optimization', 
                     fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        plt.savefig(output_dir / 'evolution_v5.png', dpi=150, bbox_inches='tight')
        plt.close()


def create_v5_config() -> Dict[str, Any]:
    """Create config for V5 experiment."""
    return {
        # Population
        'population_size': 20,
        'generations': 15,
        
        # Kernel
        'kernel_radius': 15,
        'grid_size': 128,
        
        # Simulation
        'dt': 0.1,
        'sim_steps': 200,
        
        # Seeds
        'seeds': ['orbium', 'perturbed', 'multi'],
        
        # Evolution
        'elite_fraction': 0.4,
        'mutation_rate': 0.15,
        'mutation_scale': 0.3,
        
        # Output
        'output_dir': 'output/evo_lenia_v5_joint',
        'verbose': True,
    }


def main():
    """Run V5 joint optimization experiment."""
    print("="*60)
    print("Evolutionary Lenia V5 - Joint Kernel + Growth Optimization")
    print("="*60)
    print("\nKEY INSIGHT from official Lenia reference:")
    print("  Growth parameters (mu, sigma) vary SIGNIFICANTLY across species:")
    print("    Orbium:     mu=0.15,  sigma=0.015")
    print("    Gyrorbium:  mu=0.156, sigma=0.0224")
    print("    Scutium:    mu=0.29,  sigma=0.045")
    print("\nPrevious experiments fixed mu=0.1622, sigma=0.0257!")
    print("V5 evolves BOTH kernel AND growth parameters.\n")
    
    config = create_v5_config()
    output_dir = Path(config['output_dir'])
    
    print(f"Configuration:")
    print(f"  Population: {config['population_size']}")
    print(f"  Generations: {config['generations']}")
    print(f"  Seeds: {config['seeds']}")
    print(f"  Genome: 34 params (32 kernel + mu + sigma)")
    print()
    
    # Run evolution
    engine = EvolutionEngineV5(config)
    
    t0 = time.time()
    history = engine.evolve()
    elapsed = time.time() - t0
    
    # Summary
    print(f"\n{'='*60}")
    print("EXPERIMENT COMPLETE")
    print(f"{'='*60}")
    print(f"Total time: {elapsed:.1f}s")
    print()
    
    first = history[0]
    final = history[-1]
    
    print("RESULTS SUMMARY:")
    print(f"  Initial best fitness: {first.best_hybrid_fitness:.6f}")
    print(f"  Final best fitness:   {final.best_hybrid_fitness:.6f}")
    print(f"  Improvement: {final.best_hybrid_fitness - first.best_hybrid_fitness:+.6f}")
    print()
    
    print("EVOLVED GROWTH PARAMETERS:")
    print(f"  Initial mu:    {first.best_mu:.4f}")
    print(f"  Final mu:      {final.best_mu:.4f}")
    print(f"  Initial sigma: {first.best_sigma:.4f}")
    print(f"  Final sigma:   {final.best_sigma:.4f}")
    print()
    
    # Compare to known species
    print("COMPARISON TO KNOWN LENIA SPECIES:")
    known_species = [
        ('Orbium', 0.15, 0.015),
        ('Gyrorbium', 0.156, 0.0224),
        ('Scutium', 0.29, 0.045),
        ('Hydrogeminium', 0.26, 0.036),
    ]
    
    for name, ref_mu, ref_sigma in known_species:
        mu_diff = abs(final.best_mu - ref_mu)
        sigma_diff = abs(final.best_sigma - ref_sigma)
        mu_match = "Y" if mu_diff < 0.02 else " "
        sigma_match = "Y" if sigma_diff < 0.005 else " "
        print(f"  {mu_match}{sigma_match} {name}: mu={ref_mu:.3f}, sigma={ref_sigma:.4f}")
    
    # Save results
    engine.save_results(output_dir)
    
    print(f"\n{'='*60}")
    print("Done!")
    
    return history


if __name__ == '__main__':
    main()
