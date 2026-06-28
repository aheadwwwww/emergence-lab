"""
Evolutionary Lenia Framework
=============================
Reusable framework for evolving Lenia kernels via genetic algorithms.

Design inspired by neuroparticles2's three-layer fusion:
  Genome → Kernel function → Lenia simulation → Fitness → Evolution

Architecture:
  - Genome: neural network weights (parameterized kernel function)
  - Phenotype: Lenia simulation result
  - Fitness: composite score (survival × stability × complexity)
  - Evolution: tournament selection + crossover + mutation

Usage:
  from evolutionary_lenia import EvolutionEngine, create_default_config
  engine = EvolutionEngine(create_default_config())
  results = engine.evolve()

Key design decisions:
  1. Kernel as genotype: NN weights determine kernel shape, not hardcoded
  2. Multi-seed fitness: evaluate on both orbium and random seeds
  3. Cumulative fitness: cross-generation accumulation (from neuroparticles2)
  4. Tournament selection: better diversity than top-N truncation
  5. Config-driven: all hyperparams in one dict, easy to sweep
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
import json, time, copy

from lenia_jax import make_orbium, _make_disk_kernel_np


# ═══════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════

def create_default_config() -> Dict[str, Any]:
    """Default evolution config. Override fields as needed."""
    return {
        # Population
        'population_size': 20,
        'generations': 10,
        'genome_size': 33,  # NN params: 2x8 + 8x1 weights/biases

        # Kernel
        'kernel_radius': 15,
        'grid_size': 128,

        # Lenia dynamics
        'mu': 0.1622,    # growth mean (from param search v2 best)
        'sigma': 0.0257, # growth width
        'dt': 0.1,
        'sim_steps': 200,

        # Seeds (evaluated simultaneously)
        'seeds': ['orbium', 'random'],

        # Evolution
        'elite_fraction': 0.5,
        'mutation_rate': 0.1,
        'mutation_scale': 0.2,  # std of mutation noise

        # Output
        'output_dir': 'output/evo_lenia',
        'save_gif': False,
        'verbose': True,
    }


# ═══════════════════════════════════════════════════════════════
# Genome ↔ Kernel NN
# ═══════════════════════════════════════════════════════════════

class Genome:
    """
    A genome encodes a small neural network that maps (r, theta) → kernel value.
    
    Architecture:
      Input:  normalized radius + normalized angle  (2)
      Hidden: tanh( W1@[r,theta] + b1 )            (8)
      Output: tanh( W2@hidden + b2 )                (1)
    
    Genome vector layout: [W1_flat(16), b1(8), W2_flat(8), b2(1)] = 33 params
    """

    def __init__(self, weights: np.ndarray):
        self.weights = weights.astype(np.float32)
        self.n = len(weights)
        self._cache = {}

    @staticmethod
    def random(n_params: int = 33, seed: Optional[int] = None) -> 'Genome':
        if seed is not None:
            np.random.seed(seed)
        return Genome(np.random.randn(n_params).astype(np.float32) * 0.5)

    def split_layers(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Parse genome into network layers."""
        w1 = self.weights[:16].reshape(8, 2)
        b1 = self.weights[16:24]
        w2 = self.weights[24:32].reshape(1, 8)
        b2 = self.weights[32:33]
        return w1, b1, w2, b2

    def to_kernel_fft(self, R: int, size: int) -> jnp.ndarray:
        """Convert genome to a padded FFT-ready kernel."""
        cache_key = (R, size)
        if cache_key in self._cache:
            return self._cache[cache_key]

        w1, b1, w2, b2 = self.split_layers()

        # Build kernel in radius-R disk
        kernel_hw = 2 * R + 1
        y, x = np.ogrid[-R:R+1, -R:R+1]
        r = np.sqrt(x*x + y*y)
        theta = np.arctan2(y, x)
        r_norm = r / (R + 1e-8)
        theta_norm = (theta + np.pi) / (2 * np.pi)
        mask = r <= R

        kernel = np.zeros((kernel_hw, kernel_hw), dtype=np.float32)
        for i in range(kernel_hw):
            for j in range(kernel_hw):
                if mask[i, j]:
                    inp = np.array([r_norm[i,j], theta_norm[i,j]])
                    h = np.tanh(w1 @ inp + b1)
                    kernel[i, j] = float(np.tanh(w2 @ h + b2).item())

        # Normalize and pad
        kernel = kernel / (np.abs(kernel).sum() + 1e-8)
        kernel_padded = np.zeros((size, size), dtype=np.float32)
        off = size // 2 - R
        kernel_padded[off:off+kernel_hw, off:off+kernel_hw] = kernel

        kernel_fft = jnp.fft.fft2(jnp.array(kernel_padded))
        self._cache[cache_key] = kernel_fft
        return kernel_fft

    def clone(self) -> 'Genome':
        return Genome(self.weights.copy())

    def __repr__(self):
        return f"Genome(n={self.n}, std={float(np.std(self.weights)):.3f})"


# ═══════════════════════════════════════════════════════════════
# Lenia Simulation
# ═══════════════════════════════════════════════════════════════

class LeniaSimulator:
    """Runs Lenia with a given kernel on multiple seeds."""

    def __init__(self, config: Dict[str, Any]):
        self.size = config['grid_size']
        self.R = config['kernel_radius']
        self.mu = config['mu']
        self.sigma = config['sigma']
        self.dt = config['dt']
        self.steps = config['sim_steps']
        self._seed_grids = {}

    def get_seed(self, seed_name: str) -> jnp.ndarray:
        if seed_name not in self._seed_grids:
            if seed_name == 'orbium':
                grid = make_orbium((self.size, self.size), self.R)
            else:  # random
                grid = jnp.array(np.random.rand(self.size, self.size).astype(np.float32) * 0.5)
            self._seed_grids[seed_name] = grid
        return self._seed_grids[seed_name]

    def run(self, kernel_fft: jnp.ndarray, seed_name: str) -> List[np.ndarray]:
        """Run Lenia and return history (snapshots every 20 steps)."""
        grid = jnp.array(self.get_seed(seed_name))
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


# ═══════════════════════════════════════════════════════════════
# Fitness
# ═══════════════════════════════════════════════════════════════

@dataclass
class FitnessResult:
    survival: float
    stability: float
    entropy: float   # structural complexity (normalized)
    diversity: float # spatial variance
    final_mass: float
    score: float      # composite

    def to_dict(self):
        return {
            'survival': self.survival,
            'stability': self.stability,
            'entropy': self.entropy,
            'diversity': self.diversity,
            'final_mass': self.final_mass,
            'score': self.score,
        }


def compute_fitness(history: List[np.ndarray], threshold: float = 0.05) -> FitnessResult:
    """
    Composite fitness: survival × stability × (1+entropy) × (1+diversity).
    
    - survival: fraction of frames with mass > threshold
    - stability: final 20% frames' variance (1 - normalized variance)
    - entropy: normalized Shannon entropy of final state → structural complexity
    - diversity: std across 4x4 spatial regions → multi-structure patterns
    """
    masses = np.array([h.sum() for h in history])

    survival = float(np.mean(masses > threshold))

    n = len(masses)
    final_slice = masses[int(0.8*n):]
    if len(final_slice) > 0 and np.mean(final_slice) > 0:
        stability = 1 - np.var(final_slice) / (np.mean(final_slice)**2 + 1e-8)
        stability = max(0, min(1, float(stability)))
    else:
        stability = 0.0

    final = history[-1]
    final_norm = final / (final.sum() + 1e-8)
    raw_entropy = -np.sum(final_norm * np.log(final_norm + 1e-8))
    entropy_norm = float(raw_entropy / np.log(len(final.ravel())))

    h, w = final.shape
    regions = []
    for i in range(4):
        for j in range(4):
            region = final[i*h//4:(i+1)*h//4, j*w//4:(j+1)*w//4]
            regions.append(region.sum())
    diversity = float(np.std(regions) / (np.mean(regions) + 1e-8))

    score = float(survival * stability * (1 + entropy_norm) * (1 + diversity))

    return FitnessResult(
        survival=survival,
        stability=stability,
        entropy=entropy_norm,
        diversity=diversity,
        final_mass=float(masses[-1]),
        score=score,
    )


# ═══════════════════════════════════════════════════════════════
# Evolution Engine
# ═══════════════════════════════════════════════════════════════

@dataclass
class GenerationResult:
    generation: int
    best_score: float
    mean_score: float
    median_score: float
    best_genome_idx: int
    seed_scores: Dict[str, FitnessResult]


class EvolutionEngine:
    """
    Main evolution loop.
    
    Each generation:
      1. Evaluate all genomes on all seeds → fitness
      2. Sort by composite fitness
      3. Elite selection (top elite_fraction)
      4. Crossover + mutation to refill population
      5. Record stats
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.simulator = LeniaSimulator(config)
        self.history: List[GenerationResult] = []
        self.population: List[Genome] = []
        self.cumulative_fitness: Dict[int, float] = {}  # genome id → cumulative score

    def _evaluate(self, genome: Genome) -> Tuple[float, Dict[str, FitnessResult]]:
        """Evaluate one genome on all seeds. Returns (combined_score, per_seed_results)."""
        kernel_fft = genome.to_kernel_fft(self.config['kernel_radius'], self.config['grid_size'])

        seed_results = {}
        total_score = 0.0

        for seed_name in self.config['seeds']:
            history = self.simulator.run(kernel_fft, seed_name)
            result = compute_fitness(history)
            seed_results[seed_name] = result
            total_score += result.score

        return total_score, seed_results

    def _crossover(self, parent1: Genome, parent2: Genome) -> Genome:
        """Uniform crossover."""
        mask = np.random.rand(self.config['genome_size']) < 0.5
        child_weights = np.where(mask, parent1.weights, parent2.weights)
        return Genome(child_weights.astype(np.float32))

    def _mutate(self, genome: Genome) -> Genome:
        """Gaussian mutation on random positions."""
        mutated = genome.weights.copy()
        n_mutate = max(1, np.random.binomial(self.config['genome_size'], self.config['mutation_rate']))
        indices = np.random.choice(self.config['genome_size'], n_mutate, replace=False)
        mutated[indices] += np.random.randn(n_mutate) * self.config['mutation_scale']
        return Genome(mutated.astype(np.float32))

    def evolve(self) -> List[GenerationResult]:
        """Run full evolution. Returns generation history."""
        config = self.config
        pop_size = config['population_size']
        elite_n = int(pop_size * config['elite_fraction'])

        # Initialize population
        self.population = [Genome.random(config['genome_size']) for _ in range(pop_size)]
        self.history = []

        for gen in range(config['generations']):
            if config['verbose']:
                print(f"\n{'='*50}")
                print(f"Generation {gen+1}/{config['generations']}")
                print(f"{'='*50}")

            # Evaluate
            scores = []
            seed_details = []
            for i, genome in enumerate(self.population):
                total_score, seed_results = self._evaluate(genome)

                # Cumulative fitness (from neuroparticles2 inspiration)
                genome_id = id(genome)
                if genome_id in self.cumulative_fitness:
                    self.cumulative_fitness[genome_id] += total_score * 0.1
                else:
                    self.cumulative_fitness[genome_id] = total_score

                adjusted_score = total_score + self.cumulative_fitness.get(genome_id, 0)
                scores.append(adjusted_score)
                seed_details.append(seed_results)

                if config['verbose'] and i % 5 == 0:
                    surv = seed_results.get('orbium', seed_results[config['seeds'][0]]).survival
                    print(f"  [{i+1}/{pop_size}] score={total_score:.4f} surv={surv:.2f}")

            # Record stats
            best_idx = int(np.argmax(scores))
            gen_result = GenerationResult(
                generation=gen + 1,
                best_score=float(scores[best_idx]),
                mean_score=float(np.mean(scores)),
                median_score=float(np.median(scores)),
                best_genome_idx=best_idx,
                seed_scores=seed_details[best_idx],
            )
            self.history.append(gen_result)

            if config['verbose']:
                print(f"  Best: {gen_result.best_score:.4f}  Mean: {gen_result.mean_score:.4f}")

            # Selection: elite + tournament to fill
            ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
            elite = [self.population[i] for i, _ in ranked[:elite_n]]

            new_pop = [g.clone() for g in elite]
            while len(new_pop) < pop_size:
                # Tournament selection (2-way)
                t1, t2 = np.random.choice(len(new_pop), 2, replace=False)
                if np.random.random() < 0.7:
                    parent1 = new_pop[t1] if scores[t1] > scores[t2] else new_pop[t2]
                else:
                    parent1 = new_pop[t1]  # sometimes pick weaker for diversity

                t3, t4 = np.random.choice(len(new_pop), 2, replace=False)
                parent2 = new_pop[t3] if np.random.random() < 0.7 else new_pop[t4]

                child = self._crossover(parent1, parent2)
                child = self._mutate(child)
                new_pop.append(child)

            self.population = new_pop

        return self.history

    def get_best(self) -> Genome:
        """Return best genome from last generation."""
        scores = []
        for genome in self.population:
            total, _ = self._evaluate(genome)
            scores.append(total)
        return self.population[int(np.argmax(scores))]

    def plot_evolution(self, output_dir: Path):
        """Plot evolution curves."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        gens = [r.generation for r in self.history]
        bests = [r.best_score for r in self.history]
        means = [r.mean_score for r in self.history]
        medians = [r.median_score for r in self.history]

        # Fitness curve
        ax = axes[0]
        ax.plot(gens, bests, 'b-', linewidth=2, label='Best')
        ax.plot(gens, means, 'r--', linewidth=1.5, label='Mean')
        ax.plot(gens, medians, 'g:', linewidth=1, label='Median')
        ax.fill_between(gens, means, bests, alpha=0.15)
        ax.set_xlabel('Generation')
        ax.set_ylabel('Fitness')
        ax.set_title('Evolution Progress')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Score composition (last gen best)
        ax = axes[1]
        last = self.history[-1]
        seeds = last.seed_scores
        metrics = ['survival', 'stability', 'entropy', 'diversity']
        x = np.arange(len(metrics))
        width = 0.35

        for si, (seed_name, result) in enumerate(seeds.items()):
            values = [getattr(result, m) for m in metrics]
            ax.bar(x + si*width, values, width, label=seed_name, alpha=0.8)

        ax.set_xticks(x + width/2)
        ax.set_xticklabels(metrics)
        ax.set_ylabel('Score')
        ax.set_title('Best Genome Score Breakdown')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        plt.suptitle('Evolutionary Lenia', fontsize=14, fontweight='bold')
        plt.tight_layout()
        path = output_dir / 'evolution_curves.png'
        plt.savefig(path, dpi=150)
        plt.close()
        return path

    def save_results(self, output_dir: Path):
        """Save full results to disk."""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save history
        history_data = []
        for r in self.history:
            d = {
                'generation': r.generation,
                'best_score': r.best_score,
                'mean_score': r.mean_score,
                'median_score': r.median_score,
                'seed_scores': {k: v.to_dict() for k, v in r.seed_scores.items()},
            }
            history_data.append(d)

        with open(output_dir / 'evolution_history.json', 'w') as f:
            json.dump(history_data, f, indent=2)

        # Save best genome
        best = self.get_best()
        np.save(output_dir / 'best_genome.npy', best.weights)

        # Save config
        with open(output_dir / 'config.json', 'w') as f:
            json.dump(self.config, f, indent=2)

        # Plot
        self.plot_evolution(output_dir)


# ═══════════════════════════════════════════════════════════════
# Quick demo
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("Evolutionary Lenia Framework Demo")
    print("=" * 50)

    config = create_default_config()
    config['population_size'] = 16   # small for demo
    config['generations'] = 5
    config['sim_steps'] = 150
    config['output_dir'] = 'output/evo_lenia_demo'

    engine = EvolutionEngine(config)

    t0 = time.time()
    history = engine.evolve()
    elapsed = time.time() - t0

    print(f"\n{'='*50}")
    print(f"Evolution complete in {elapsed:.0f}s")
    print(f"Initial best: {history[0].best_score:.4f}")
    print(f"Final best:   {history[-1].best_score:.4f}")
    print(f"Improvement:  {history[-1].best_score - history[0].best_score:+.4f}")

    engine.save_results(Path(config['output_dir']))
    print(f"\nResults saved to {config['output_dir']}/")
    print("Done!")
