"""
Evolutionary Lenia with Dynamic Fitness
========================================

Test whether the NEW dynamic fitness function drives evolution better than the old one.

Key differences:
  OLD: rewards stability (static blobs score high)
  NEW: rewards dynamics (frame change rate), complexity (fractal edge density), moderate_stability

Expected outcome: best_score should IMPROVE across generations with new fitness.
"""

import sys
sys.path.insert(0, 'D:/openclaw_workspace/experiments')
sys.path.insert(0, 'D:/openclaw_workspace/experiments/orchestrator')

import numpy as np
import jax
import jax.numpy as jnp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
import json
import time

# Import existing Lenia infrastructure
from evolutionary_lenia import (
    Genome, LeniaSimulator, create_default_config
)
# Import NEW dynamic fitness
from dynamic_fitness import compute_dynamic_fitness, DynamicFitnessResult


# ═══════════════════════════════════════════════════════════════
# Dynamic Fitness Wrapper
# ═══════════════════════════════════════════════════════════════

@dataclass
class DynamicFitnessWrapper:
    """Wraps the new dynamic fitness result."""
    survival: float
    stability: float
    entropy: float
    diversity: float
    dynamics: float      # NEW
    complexity: float    # NEW
    final_mass: float
    score: float

    def to_dict(self):
        return {
            'survival': float(self.survival),
            'stability': float(self.stability),
            'entropy': float(self.entropy),
            'diversity': float(self.diversity),
            'dynamics': float(self.dynamics),
            'complexity': float(self.complexity),
            'final_mass': float(self.final_mass),
            'score': float(self.score),
        }


def compute_dynamic_fitness_wrapper(history: List[np.ndarray], threshold: float = 0.05) -> DynamicFitnessWrapper:
    """Use the NEW dynamic fitness function."""
    result = compute_dynamic_fitness(history, threshold)
    masses = np.array([h.sum() for h in history])
    
    return DynamicFitnessWrapper(
        survival=result.survival,
        stability=result.stability,
        entropy=result.entropy,
        diversity=result.diversity,
        dynamics=result.dynamics,
        complexity=result.complexity,
        final_mass=float(masses[-1]),
        score=result.score,
    )


# ═══════════════════════════════════════════════════════════════
# Evolution Engine with Dynamic Fitness
# ═══════════════════════════════════════════════════════════════

@dataclass
class GenerationResult:
    generation: int
    best_score: float
    mean_score: float
    median_score: float
    best_genome_idx: int
    seed_scores: Dict[str, DynamicFitnessWrapper]


class DynamicEvolutionEngine:
    """Evolution engine using the NEW dynamic fitness function."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.simulator = LeniaSimulator(config)
        self.history: List[GenerationResult] = []
        self.population: List[Genome] = []

    def _evaluate(self, genome: Genome) -> Tuple[float, Dict[str, DynamicFitnessWrapper]]:
        """Evaluate one genome on all seeds using DYNAMIC fitness."""
        kernel_fft = genome.to_kernel_fft(self.config['kernel_radius'], self.config['grid_size'])

        seed_results = {}
        total_score = 0.0

        for seed_name in self.config['seeds']:
            history = self.simulator.run(kernel_fft, seed_name)
            # USE NEW DYNAMIC FITNESS
            result = compute_dynamic_fitness_wrapper(history)
            seed_results[seed_name] = result
            total_score += result.score

        return total_score, seed_results

    def _crossover(self, parent1: Genome, parent2: Genome) -> Genome:
        """Uniform crossover."""
        mask = np.random.rand(self.config['genome_size']) < 0.5
        child_weights = np.where(mask, parent1.weights, parent2.weights)
        return Genome(child_weights.astype(np.float32))

    def _mutate(self, genome: Genome) -> Genome:
        """Gaussian mutation."""
        mutated = genome.weights.copy()
        n_mutate = max(1, np.random.binomial(self.config['genome_size'], self.config['mutation_rate']))
        indices = np.random.choice(self.config['genome_size'], n_mutate, replace=False)
        mutated[indices] += np.random.randn(n_mutate) * self.config['mutation_scale']
        return Genome(mutated.astype(np.float32))

    def evolve(self) -> List[GenerationResult]:
        """Run evolution with DYNAMIC fitness."""
        config = self.config
        pop_size = config['population_size']
        elite_n = max(2, int(pop_size * config['elite_fraction']))

        # Initialize population
        self.population = [Genome.random(config['genome_size']) for _ in range(pop_size)]
        self.history = []

        for gen in range(config['generations']):
            if config['verbose']:
                print(f"\n{'='*50}")
                print(f"Generation {gen+1}/{config['generations']}")
                print(f"{'='*50}")

            # Evaluate all genomes
            scores = []
            seed_details = []
            for i, genome in enumerate(self.population):
                total_score, seed_results = self._evaluate(genome)
                scores.append(total_score)
                seed_details.append(seed_results)

                if config['verbose']:
                    # Show key metrics for first genome
                    if i == 0:
                        for seed_name, res in seed_results.items():
                            print(f"  [{seed_name}] score={res.score:.3f} dyn={res.dynamics:.4f} cmp={res.complexity:.4f}")

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
                best_res = seed_details[best_idx]
                best_dyn = list(best_res.values())[0].dynamics
                best_cmp = list(best_res.values())[0].complexity
                print(f"  Best: {gen_result.best_score:.4f}  Mean: {gen_result.mean_score:.4f}")
                print(f"        dynamics={best_dyn:.4f}  complexity={best_cmp:.4f}")

            # Selection + reproduction
            ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
            elite = [self.population[i] for i, _ in ranked[:elite_n]]

            new_pop = [g.clone() for g in elite]
            while len(new_pop) < pop_size:
                # Tournament selection
                idx1, idx2 = np.random.choice(len(elite), 2, replace=False)
                parent1 = elite[idx1] if scores[ranked[idx1][0]] > scores[ranked[idx2][0]] else elite[idx2]
                idx3, idx4 = np.random.choice(len(elite), 2, replace=False)
                parent2 = elite[idx3] if scores[ranked[idx3][0]] > scores[ranked[idx4][0]] else elite[idx4]

                child = self._crossover(parent1, parent2)
                child = self._mutate(child)
                new_pop.append(child)

            self.population = new_pop

        return self.history

    def get_best(self) -> Genome:
        """Return best genome."""
        scores = []
        for genome in self.population:
            total, _ = self._evaluate(genome)
            scores.append(total)
        return self.population[int(np.argmax(scores))]

    def save_results(self, output_dir: Path):
        """Save results to disk."""
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

        # Plot evolution curves
        self._plot_evolution(output_dir)

    def _plot_evolution(self, output_dir: Path):
        """Plot evolution curves."""
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))

        gens = [r.generation for r in self.history]
        bests = [r.best_score for r in self.history]
        means = [r.mean_score for r in self.history]

        # Fitness curve
        ax = axes[0]
        ax.plot(gens, bests, 'b-o', linewidth=2, label='Best')
        ax.plot(gens, means, 'r--s', linewidth=1.5, label='Mean')
        ax.set_xlabel('Generation')
        ax.set_ylabel('Fitness')
        ax.set_title('Evolution Progress (Dynamic Fitness)')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Dynamics metric over generations
        ax = axes[1]
        dynamics_vals = []
        complexity_vals = []
        for r in self.history:
            seed_res = list(r.seed_scores.values())[0]
            dynamics_vals.append(seed_res.dynamics)
            complexity_vals.append(seed_res.complexity)
        ax.plot(gens, dynamics_vals, 'g-o', linewidth=2, label='Dynamics')
        ax.plot(gens, complexity_vals, 'm-s', linewidth=2, label='Complexity')
        ax.set_xlabel('Generation')
        ax.set_ylabel('Metric Value')
        ax.set_title('Key Dynamic Metrics')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Score breakdown (last gen)
        ax = axes[2]
        last = self.history[-1]
        seed_res = list(last.seed_scores.values())[0]
        metrics = ['survival', 'stability', 'entropy', 'diversity', 'dynamics', 'complexity']
        values = [getattr(seed_res, m) for m in metrics]
        bars = ax.bar(metrics, values, color=['#3498db', '#2ecc71', '#e74c3c', '#9b59b6', '#f39c12', '#1abc9c'])
        ax.set_ylabel('Score')
        ax.set_title('Best Genome Score Breakdown')
        ax.grid(True, alpha=0.3, axis='y')
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                   f'{val:.3f}', ha='center', va='bottom', fontsize=9)

        plt.suptitle('Evolutionary Lenia with Dynamic Fitness', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_dir / 'evolution_curves.png', dpi=150)
        plt.close()


# ═══════════════════════════════════════════════════════════════
# Main Experiment
# ═══════════════════════════════════════════════════════════════

def run_experiment():
    """Run evolutionary Lenia with dynamic fitness."""
    print("=" * 60)
    print("EVOLUTIONARY LENIA WITH DYNAMIC FITNESS")
    print("=" * 60)
    print("\nHypothesis: Dynamic fitness should drive evolution better")
    print("  - Old fitness: rewards static blobs (stuck at ~11.67)")
    print("  - New fitness: rewards dynamics + complexity")
    print()

    # Config
    config = create_default_config()
    config['population_size'] = 12
    config['generations'] = 8
    config['sim_steps'] = 150
    config['output_dir'] = 'D:/openclaw_workspace/output/evo_lenia_dynamic'
    config['verbose'] = True

    print(f"Config: {config['population_size']} individuals × {config['generations']} generations")
    print(f"Output: {config['output_dir']}")
    print()

    # Run evolution
    engine = DynamicEvolutionEngine(config)
    t0 = time.time()
    history = engine.evolve()
    elapsed = time.time() - t0

    # Analysis
    print(f"\n{'='*60}")
    print("RESULTS")
    print(f"{'='*60}")

    initial_best = history[0].best_score
    final_best = history[-1].best_score
    improvement = final_best - initial_best

    print(f"\nGeneration-by-generation best scores:")
    for r in history:
        seed_res = list(r.seed_scores.values())[0]
        print(f"  Gen {r.generation}: best={r.best_score:.4f}  dynamics={seed_res.dynamics:.4f}  complexity={seed_res.complexity:.4f}")

    print(f"\nSummary:")
    print(f"  Initial best:  {initial_best:.4f}")
    print(f"  Final best:    {final_best:.4f}")
    print(f"  Improvement:   {improvement:+.4f}")
    print(f"  Time:          {elapsed:.0f}s")

    # Key metrics for best individual
    best_res = list(history[-1].seed_scores.values())[0]
    print(f"\nBest individual metrics:")
    print(f"  survival:   {best_res.survival:.4f}")
    print(f"  stability:  {best_res.stability:.4f}")
    print(f"  entropy:    {best_res.entropy:.4f}")
    print(f"  diversity:  {best_res.diversity:.4f}")
    print(f"  dynamics:   {best_res.dynamics:.4f}  ← NEW")
    print(f"  complexity: {best_res.complexity:.4f}  ← NEW")

    # Conclusion
    print(f"\n{'='*60}")
    print("CONCLUSION")
    print(f"{'='*60}")

    if improvement > 0.5:
        print(f"[SUCCESS] Evolution improved by {improvement:.2f}")
        print("   The dynamic fitness function drives evolution!")
    elif improvement > 0:
        print(f"[MARGINAL] Evolution improved by {improvement:.2f}")
        print("   Some improvement, may need more generations or tuning")
    else:
        print(f"[FAILURE] No improvement ({improvement:.2f})")
        print("   Dynamic fitness may need adjustment")

    # Check if dynamics metric is non-zero
    if best_res.dynamics > 0.01:
        print(f"\n[OK] Dynamics metric is active: {best_res.dynamics:.4f}")
    else:
        print(f"\n[WARN] Dynamics metric is low: {best_res.dynamics:.4f}")

    # Save results
    output_dir = Path(config['output_dir'])
    engine.save_results(output_dir)

    # Write summary JSON
    summary = {
        'experiment': 'evolutionary_lenia_dynamic_fitness',
        'config': config,
        'results': {
            'initial_best': initial_best,
            'final_best': final_best,
            'improvement': improvement,
            'elapsed_seconds': elapsed,
        },
        'best_metrics': best_res.to_dict(),
        'generation_scores': [
            {
                'generation': r.generation,
                'best_score': r.best_score,
                'mean_score': r.mean_score,
                'dynamics': list(r.seed_scores.values())[0].dynamics,
                'complexity': list(r.seed_scores.values())[0].complexity,
            }
            for r in history
        ],
        'conclusion': {
            'success': improvement > 0.5,
            'message': 'Dynamic fitness drives evolution' if improvement > 0.5 else 'Needs tuning',
        }
    }

    with open(output_dir / 'summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\nResults saved to {output_dir}/")
    print("Done!")

    return summary


if __name__ == '__main__':
    run_experiment()
