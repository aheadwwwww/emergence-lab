"""
Evolutionary Lenia V6 - Pareto Front Optimization
==================================================

Multi-objective optimization to discover Pareto-optimal kernels.

Objectives:
  1. Stability: survival × persistence (pattern maintenance)
  2. Emergence: diversity × complexity (novel behavior)

Why Pareto?
  - Reveals trade-offs between stability and emergence
  - Identifies specialist kernels (high in one objective)
  - Finds generalist kernels (balanced performance)
  - Enables kernel selection for different applications

Algorithm: NSGA-II (Non-dominated Sorting Genetic Algorithm)
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
from evolutionary_lenia_v4_adaptive import (
    MultiRingGenome,
    RingParams,
    polynomial_bump,
    gaussian_bump,
    LeniaSimulatorV4,
)


@dataclass
class ObjectiveScores:
    """Multi-objective fitness scores."""
    stability: float    # Objective 1: pattern maintenance
    emergence: float    # Objective 2: novel behavior
    survival: float     # Raw survival rate
    diversity: float    # Pattern diversity
    complexity: float   # Pattern complexity
    persistence: float  # Pattern stability over time
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'stability': float(self.stability),
            'emergence': float(self.emergence),
            'survival': float(self.survival),
            'diversity': float(self.diversity),
            'complexity': float(self.complexity),
            'persistence': float(self.persistence),
        }


def compute_objectives(history: List[np.ndarray]) -> ObjectiveScores:
    """
    Compute multi-objective fitness from simulation history.
    
    Objective 1 (Stability) = survival × persistence
    Objective 2 (Emergence) = diversity × complexity
    """
    final = history[-1]
    
    # Survival: fraction of alive cells
    survival = float(np.mean(final > 0.1))
    
    # Persistence: how much pattern retained over time
    if len(history) > 1:
        initial = history[0]
        persistence = 1.0 - np.mean(np.abs(final - initial))
    else:
        persistence = 0.5
    
    # Diversity: entropy of cell values
    hist, _ = np.histogram(final, bins=20, range=(0, 1))
    hist = hist / hist.sum()
    diversity = float(-np.sum(hist * np.log2(hist + 1e-10)))
    
    # Complexity: spatial variance
    complexity = float(np.std(final))
    
    # Combine into objectives
    stability = survival * persistence
    emergence = diversity * complexity
    
    return ObjectiveScores(
        stability=stability,
        emergence=emergence,
        survival=survival,
        diversity=diversity,
        complexity=complexity,
        persistence=persistence,
    )


def dominates(scores1: ObjectiveScores, scores2: ObjectiveScores) -> bool:
    """Check if scores1 dominates scores2 (Pareto dominance)."""
    better_or_equal = (
        scores1.stability >= scores2.stability and
        scores1.emergence >= scores2.emergence
    )
    strictly_better = (
        scores1.stability > scores2.stability or
        scores1.emergence > scores2.emergence
    )
    return better_or_equal and strictly_better


def fast_non_dominated_sort(population: List[ObjectiveScores]) -> List[List[int]]:
    """
    NSGA-II fast non-dominated sort.
    Returns list of fronts, where front[0] is Pareto-optimal.
    """
    n = len(population)
    domination_count = np.zeros(n, dtype=int)
    dominated_set = [[] for _ in range(n)]
    
    for i in range(n):
        for j in range(i + 1, n):
            if dominates(population[i], population[j]):
                domination_count[j] += 1
                dominated_set[i].append(j)
            elif dominates(population[j], population[i]):
                domination_count[i] += 1
                dominated_set[j].append(i)
    
    fronts = []
    current_front = list(np.where(domination_count == 0)[0])
    
    while current_front:
        fronts.append(current_front)
        next_front = []
        
        for i in current_front:
            for j in dominated_set[i]:
                domination_count[j] -= 1
                if domination_count[j] == 0:
                    next_front.append(j)
        
        current_front = next_front
    
    return fronts


def crowding_distance(front_scores: List[ObjectiveScores]) -> np.ndarray:
    """Compute crowding distance for diversity preservation."""
    n = len(front_scores)
    if n <= 2:
        return np.full(n, np.inf)
    
    distances = np.zeros(n)
    
    for obj_name in ['stability', 'emergence']:
        values = np.array([getattr(s, obj_name) for s in front_scores])
        sorted_idx = np.argsort(values)
        
        distances[sorted_idx[0]] = np.inf
        distances[sorted_idx[-1]] = np.inf
        
        val_range = values[sorted_idx[-1]] - values[sorted_idx[0]]
        if val_range > 1e-10:
            for i in range(1, n - 1):
                distances[sorted_idx[i]] += (
                    values[sorted_idx[i + 1]] - values[sorted_idx[i - 1]]
                ) / val_range
    
    return distances


@dataclass
class Individual:
    """Individual in the population."""
    genome: MultiRingGenome
    scores: Optional[ObjectiveScores] = None
    rank: int = -1
    crowding_dist: float = 0.0


class EvolutionEngineV6:
    """NSGA-II multi-objective optimization."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.simulator = LeniaSimulatorV4(config)
        self.population: List[Individual] = []
        self.history: List[Dict] = []
        
    def _evaluate(self, individual: Individual) -> ObjectiveScores:
        """Evaluate genome on seeds and aggregate objectives."""
        all_scores = []
        
        for seed_name in self.config['seeds']:
            # Simulate
            history = self.simulator.run(individual.genome, seed_name)
            
            # Compute objectives
            scores = compute_objectives(history)
            all_scores.append(scores)
        
        # Aggregate: average across seeds
        return ObjectiveScores(
            stability=np.mean([s.stability for s in all_scores]),
            emergence=np.mean([s.emergence for s in all_scores]),
            survival=np.mean([s.survival for s in all_scores]),
            diversity=np.mean([s.diversity for s in all_scores]),
            complexity=np.mean([s.complexity for s in all_scores]),
            persistence=np.mean([s.persistence for s in all_scores]),
        )
    
    def _create_orbium_seed(self) -> np.ndarray:
        """Create Orbium-like seed pattern."""
        size = self.config['grid_size']
        grid = np.zeros((size, size), dtype=np.float32)
        mid = size // 2
        
        # Create simple disk pattern
        y, x = np.ogrid[:size, :size]
        r = np.sqrt((x - mid)**2 + (y - mid)**2)
        
        disk_radius = size // 8
        grid[r < disk_radius] = 1.0
        
        # Smooth edges
        transition = 2
        mask = (r >= disk_radius) & (r < disk_radius + transition)
        grid[mask] = 1.0 - (r[mask] - disk_radius) / transition
        
        return grid
    
    def _create_random_seed(self) -> np.ndarray:
        """Create random seed pattern."""
        size = self.config['grid_size']
        grid = np.random.rand(size, size).astype(np.float32)
        
        # Center the pattern
        mid = size // 2
        radius = size // 4
        y, x = np.ogrid[:size, :size]
        r = np.sqrt((x - mid)**2 + (y - mid)**2)
        grid[r > radius] = 0.0
        
        return grid
    
    def _crossover(self, p1: Individual, p2: Individual) -> Individual:
        """Simulated binary crossover."""
        child_params = np.zeros(6, dtype=np.float32)
        parent1_params = p1.genome.to_param_vector()
        parent2_params = p2.genome.to_param_vector()
        
        for i in range(6):
            if np.random.rand() < 0.5:
                child_params[i] = parent1_params[i]
            else:
                child_params[i] = parent2_params[i]
        
        child_genome = MultiRingGenome.from_param_vector(child_params)
        return Individual(genome=child_genome)
    
    def _mutate(self, individual: Individual) -> Individual:
        """Polynomial mutation."""
        params = individual.genome.to_param_vector()
        mutated = params.copy()
        
        for i in range(6):
            if np.random.rand() < self.config['mutation_rate']:
                eta = 20.0  # Mutation distribution index
                delta = np.random.randn() * 0.15
                mutated[i] = np.clip(params[i] + delta, -1, 1)
        
        child_genome = MultiRingGenome.from_param_vector(mutated)
        return Individual(genome=child_genome)
    
    def evolve(self) -> List[Dict]:
        """Run NSGA-II evolution."""
        pop_size = self.config['population_size']
        generations = self.config['generations']
        
        # Initialize population
        self.population = [
            Individual(genome=MultiRingGenome.random())
            for _ in range(pop_size)
        ]
        
        # Evaluate initial population
        for ind in self.population:
            ind.scores = self._evaluate(ind)
        
        for gen in range(generations):
            print(f"\n{'='*60}")
            print(f"Generation {gen+1}/{generations}")
            print(f"{'='*60}")
            
            # Create offspring
            offspring = []
            
            # Non-dominated sort
            scores = [ind.scores for ind in self.population]
            fronts = fast_non_dominated_sort(scores)
            
            # Assign ranks
            for rank, front in enumerate(fronts):
                for idx in front:
                    self.population[idx].rank = rank
            
            # Crowding distance
            for front in fronts:
                front_scores = [self.population[i].scores for i in front]
                distances = crowding_distance(front_scores)
                for i, idx in enumerate(front):
                    self.population[idx].crowding_dist = distances[i]
            
            # Generate offspring
            while len(offspring) < pop_size:
                # Tournament selection
                candidates = np.random.choice(pop_size, 2, replace=False)
                p1 = self.population[candidates[0]]
                p2 = self.population[candidates[1]]
                
                # Select based on rank and crowding distance
                if p1.rank < p2.rank:
                    parent1 = p1
                elif p2.rank < p1.rank:
                    parent1 = p2
                elif p1.crowding_dist > p2.crowding_dist:
                    parent1 = p1
                else:
                    parent1 = p2
                
                # Second parent
                candidates = np.random.choice(pop_size, 2, replace=False)
                p1 = self.population[candidates[0]]
                p2 = self.population[candidates[1]]
                
                if p1.rank < p2.rank:
                    parent2 = p1
                elif p2.rank < p1.rank:
                    parent2 = p2
                elif p1.crowding_dist > p2.crowding_dist:
                    parent2 = p1
                else:
                    parent2 = p2
                
                # Crossover and mutation
                child = self._crossover(parent1, parent2)
                child = self._mutate(child)
                offspring.append(child)
            
            # Evaluate offspring
            for ind in offspring:
                ind.scores = self._evaluate(ind)
            
            # Combine and select
            combined = self.population + offspring
            combined_scores = [ind.scores for ind in combined]
            combined_fronts = fast_non_dominated_sort(combined_scores)
            
            new_population = []
            for front in combined_fronts:
                if len(new_population) + len(front) <= pop_size:
                    for idx in front:
                        new_population.append(combined[idx])
                else:
                    # Partial front selection
                    remaining = pop_size - len(new_population)
                    front_scores = [combined[i].scores for i in front]
                    distances = crowding_distance(front_scores)
                    sorted_front = sorted(
                        zip(front, distances),
                        key=lambda x: x[1],
                        reverse=True
                    )
                    for idx, _ in sorted_front[:remaining]:
                        new_population.append(combined[idx])
                    break
            
            self.population = new_population[:pop_size]
            
            # Record history
            pareto_front = [
                self.population[i].scores
                for i in combined_fronts[0]
                if i < pop_size
            ]
            
            self.history.append({
                'generation': gen + 1,
                'pareto_size': len(pareto_front),
                'pareto_stability': [float(s.stability) for s in pareto_front],
                'pareto_emergence': [float(s.emergence) for s in pareto_front],
            })
            
            # Print stats
            if pareto_front:
                print(f"Pareto front size: {len(pareto_front)}")
                print(f"Stability range: [{min(s.stability for s in pareto_front):.4f}, "
                      f"{max(s.stability for s in pareto_front):.4f}]")
                print(f"Emergence range: [{min(s.emergence for s in pareto_front):.4f}, "
                      f"{max(s.emergence for s in pareto_front):.4f}]")
        
        return self.history
    
    def save_results(self, output_dir: Path):
        """Save Pareto front results."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get final Pareto front
        scores = [ind.scores for ind in self.population]
        fronts = fast_non_dominated_sort(scores)
        pareto_individuals = [self.population[i] for i in fronts[0]]
        
        # Save Pareto front
        pareto_data = []
        for ind in pareto_individuals:
            pareto_data.append({
                'params': ind.genome.to_param_vector().tolist(),
                'scores': ind.scores.to_dict(),
            })
        
        with open(output_dir / 'pareto_front.json', 'w') as f:
            json.dump(pareto_data, f, indent=2)
        
        # Save history
        with open(output_dir / 'evolution_history.json', 'w') as f:
            json.dump(self.history, f, indent=2)
        
        # Create plots
        self._plot_pareto_front(pareto_individuals, output_dir)
        
        print(f"\n[OK] Results saved to {output_dir}/")
    
    def _plot_pareto_front(self, pareto: List[Individual], output_dir: Path):
        """Plot Pareto front."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Plot 1: Pareto front
        ax = axes[0]
        stability = [ind.scores.stability for ind in pareto]
        emergence = [ind.scores.emergence for ind in pareto]
        
        ax.scatter(stability, emergence, s=100, alpha=0.7, c='blue', edgecolors='black')
        ax.set_xlabel('Stability (survival × persistence)', fontsize=12)
        ax.set_ylabel('Emergence (diversity × complexity)', fontsize=12)
        ax.set_title('Pareto Front: Stability vs Emergence', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Annotate extremes
        max_stab_idx = np.argmax(stability)
        max_emer_idx = np.argmax(emergence)
        
        ax.annotate(
            'Stability\nSpecialist',
            xy=(stability[max_stab_idx], emergence[max_stab_idx]),
            xytext=(10, 10),
            textcoords='offset points',
            fontsize=9,
            alpha=0.7
        )
        ax.annotate(
            'Emergence\nSpecialist',
            xy=(stability[max_emer_idx], emergence[max_emer_idx]),
            xytext=(10, -15),
            textcoords='offset points',
            fontsize=9,
            alpha=0.7
        )
        
        # Plot 2: Evolution progress
        ax = axes[1]
        if self.history:
            gens = [h['generation'] for h in self.history]
            pareto_sizes = [h['pareto_size'] for h in self.history]
            
            ax.plot(gens, pareto_sizes, 'o-', linewidth=2, markersize=8)
            ax.set_xlabel('Generation', fontsize=12)
            ax.set_ylabel('Pareto Front Size', fontsize=12)
            ax.set_title('Pareto Front Size Evolution', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
        
        plt.suptitle('Evolutionary Lenia V6 - Pareto Optimization', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_dir / 'pareto_front.png', dpi=150, bbox_inches='tight')
        plt.close()


def create_v6_config() -> Dict[str, Any]:
    """Create config for V6 Pareto experiment."""
    return {
        'population_size': 30,
        'generations': 15,
        'kernel_radius': 15,
        'grid_size': 128,
        'dt': 0.1,
        'sim_steps': 200,
        'mu': 0.12,  # Based on V5 findings
        'sigma': 0.05,  # Based on V5 findings (close to Scutium)
        'seeds': ['orbium', 'random'],
        'mutation_rate': 0.2,
        'output_dir': 'output/evo_lenia_v6_pareto',
        'verbose': True,
    }


def main():
    """Run V6 Pareto optimization experiment."""
    print("="*60)
    print("Evolutionary Lenia V6 - Pareto Front Optimization")
    print("="*60)
    print("\nMulti-objective optimization:")
    print("  Objective 1: Stability (survival × persistence)")
    print("  Objective 2: Emergence (diversity × complexity)")
    print("\nAlgorithm: NSGA-II (Non-dominated Sorting GA)")
    print()
    
    config = create_v6_config()
    output_dir = Path(config['output_dir'])
    
    print(f"Configuration:")
    print(f"  Population: {config['population_size']}")
    print(f"  Generations: {config['generations']}")
    print(f"  Seeds: {config['seeds']}")
    print()
    
    # Run evolution
    engine = EvolutionEngineV6(config)
    
    t0 = time.time()
    history = engine.evolve()
    elapsed = time.time() - t0
    
    # Summary
    print(f"\n{'='*60}")
    print("EXPERIMENT COMPLETE")
    print(f"{'='*60}")
    print(f"Total time: {elapsed:.1f}s")
    
    # Save results
    engine.save_results(output_dir)
    
    print(f"\n{'='*60}")
    print("Done!")


if __name__ == '__main__':
    main()
