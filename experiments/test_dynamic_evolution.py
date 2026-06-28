"""
Test: Evolution with Dynamic Fitness
=====================================

Compare evolution results:
1. Old fitness (rewards stability)
2. New fitness (rewards dynamics)
"""

import sys
sys.path.insert(0, '.')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
import json

from evolutionary_lenia import Genome, create_default_config, LeniaSimulator
from dynamic_fitness import compute_dynamic_fitness

def test_fitness_on_known_patterns():
    """Test fitness function on known Lenia patterns."""
    from lenia_jax import make_orbium, lenia_step, _make_kernel_fft
    
    print("Testing fitness on known Lenia patterns...")
    
    # Orbium (known-good)
    orbium = make_orbium()
    R = orbium['R']
    grid_size = 128
    
    # Simulate Orbium with its native kernel
    state = orbium['cells'][0].copy()
    state = np.pad(state, (grid_size - state.shape[0]) // 2)
    
    # Get Orbium kernel
    from lenia_jax import _make_disk_kernel_np
    kernel = _make_disk_kernel_np(R, orbium['k_params'])
    kernel_fft = np.fft.fft2(kernel, s=(grid_size, grid_size))
    
    history = [state.copy()]
    for _ in range(200):
        state = lenia_step(state, kernel_fft, orbium['params'])
        history.append(state.copy())
    
    result = compute_dynamic_fitness(history)
    print(f"\nOrbium (known-good):")
    print(f"  Score: {result.score:.3f}")
    print(f"  Dynamics: {result.dynamics:.4f}")
    print(f"  Breakdown: {result.breakdown}")
    
    return result


def evolve_with_dynamic_fitness(generations=5, pop_size=10):
    """Quick evolution test with dynamic fitness."""
    print(f"\n{'='*60}")
    print(f"Evolution test: {generations} generations, {pop_size} individuals")
    print(f"{'='*60}")
    
    config = create_default_config()
    config['generations'] = generations
    config['population_size'] = pop_size
    config['sim_steps'] = 500  # Longer simulation for dynamics
    config['verbose'] = True
    
    simulator = LeniaSimulator(config)
    
    # Initialize population
    population = [Genome.random(config['genome_size']) for _ in range(pop_size)]
    
    best_scores = []
    best_genomes = []
    
    for gen in range(generations):
        print(f"\n--- Generation {gen+1}/{generations} ---")
        
        # Evaluate
        results = []
        for i, genome in enumerate(population):
            try:
                kernel_fft = genome.to_kernel_fft(config['kernel_radius'], config['grid_size'])
                history = simulator.run(kernel_fft, 'random')  # Use random seed
                result = compute_dynamic_fitness(history)
                results.append((genome, result))
                print(f"  Genome {i+1}: score={result.score:.3f}, dynamics={result.dynamics:.4f}")
            except Exception as e:
                print(f"  Genome {i+1}: ERROR - {e}")
                results.append((genome, None))
        
        # Select best
        valid = [(g, r) for g, r in results if r is not None]
        if not valid:
            print("  No valid genomes, reinitializing...")
            population = [Genome.random(config['genome_size']) for _ in range(pop_size)]
            continue
        
        valid.sort(key=lambda x: x[1].score, reverse=True)
        best_genome, best_result = valid[0]
        best_scores.append(best_result.score)
        best_genomes.append(best_genome)
        
        print(f"\n  Best: score={best_result.score:.3f}")
        print(f"  {best_result.breakdown}")
        
        # Evolve
        if gen < generations - 1:
            # Tournament selection + mutation
            new_pop = []
            for _ in range(pop_size):
                # Tournament
                candidates = np.random.choice(len(valid), size=3, replace=False)
                winner = max(candidates, key=lambda i: valid[i][1].score)
                parent = valid[winner][0]
                
                # Mutate
                child = parent.clone()
                child.mutate(rate=0.1, scale=0.2)
                new_pop.append(child)
            
            population = new_pop
    
    return best_scores, best_genomes


def visualize_evolution(best_scores, output_path):
    """Plot evolution progress."""
    plt.figure(figsize=(10, 5))
    plt.plot(best_scores, marker='o')
    plt.xlabel('Generation')
    plt.ylabel('Best Score')
    plt.title('Evolution Progress (Dynamic Fitness)')
    plt.grid(True, alpha=0.3)
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    Path("output/evo_lenia_dynamic").mkdir(parents=True, exist_ok=True)
    
    # Test 1: Known patterns
    try:
        test_fitness_on_known_patterns()
    except Exception as e:
        print(f"Test 1 failed: {e}")
    
    # Test 2: Quick evolution
    print("\n" + "="*60)
    print("Starting evolution with dynamic fitness...")
    print("="*60)
    
    best_scores, best_genomes = evolve_with_dynamic_fitness(generations=5, pop_size=10)
    
    # Visualize
    visualize_evolution(best_scores, "output/evo_lenia_dynamic/evolution_progress.png")
    
    # Save results
    results = {
        'best_scores': best_scores,
        'final_score': best_scores[-1] if best_scores else 0,
    }
    
    with open("output/evo_lenia_dynamic/results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Generations: 5")
    print(f"Best score: {best_scores[-1]:.3f}")
    print(f"Progress: {best_scores}")
    print(f"\nSaved to: output/evo_lenia_dynamic/")