"""
Ecosystem Parameter Sweep: Find optimal settings for species coexistence

Explore:
- Different population sizes (2, 3, 4, 5 species)
- Different ecosystem types
- Different grid sizes
"""

import numpy as np
import sys
sys.path.append('D:/openclaw_workspace/experiments')

from mutualistic_lenia import MutualisticEcosystem
import json
from pathlib import Path

def run_sweep():
    """Sweep parameters and collect results"""
    
    results = []
    
    # Parameters to test
    n_species_list = [2, 3, 4, 5]
    eco_types = ['web', 'chain', 'cycle', 'competition']
    sizes = [64, 128, 256]
    n_runs = 5  # per configuration
    
    total_configs = len(n_species_list) * len(eco_types) * len(sizes)
    config_count = 0
    
    for n_species in n_species_list:
        for eco_type in eco_types:
            for size in sizes:
                config_count += 1
                print(f"\nConfig {config_count}/{total_configs}: {n_species} species, {eco_type}, size={size}")
                
                diversities = []
                alive_counts = []
                
                for run in range(n_runs):
                    eco = MutualisticEcosystem(size=size, ecosystem_type=eco_type)
                    eco.seed_random(n_seeds=n_species)
                    
                    for step in range(150):
                        eco.step()
                    
                    diversity = eco.get_diversity()
                    alive = eco.get_survival_count(threshold=30)
                    
                    diversities.append(diversity)
                    alive_counts.append(alive)
                
                result = {
                    'n_species': n_species,
                    'eco_type': eco_type,
                    'grid_size': size,
                    'mean_diversity': np.mean(diversities),
                    'std_diversity': np.std(diversities),
                    'mean_alive': np.mean(alive_counts),
                    'survival_rate': np.mean(alive_counts) / n_species
                }
                
                results.append(result)
                
                # Early log
                print(f"  Diversity: {result['mean_diversity']:.2f}±{result['std_diversity']:.2f}")
                print(f"  Survival: {result['mean_alive']:.1f}/{n_species} ({result['survival_rate']*100:.1f}%)")
    
    # Save results
    output_path = Path('experiments/data/ecosystem_sweep_results.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*70}")
    print("SWEEP COMPLETE")
    print(f"{'='*70}")
    
    # Find best configurations
    best_by_diversity = max(results, key=lambda x: x['mean_diversity'])
    best_by_survival = max(results, key=lambda x: x['survival_rate'])
    
    print(f"\nBest by Diversity:")
    print(f"  {best_by_diversity['n_species']} species, {best_by_diversity['eco_type']}, size {best_by_diversity['grid_size']}")
    print(f"  Diversity: {best_by_diversity['mean_diversity']:.2f}")
    
    print(f"\nBest by Survival Rate:")
    print(f"  {best_by_survival['n_species']} species, {best_by_survival['eco_type']}, size {best_by_survival['grid_size']}")
    print(f"  Survival: {best_by_survival['survival_rate']*100:.1f}%")
    
    return results

if __name__ == "__main__":
    results = run_sweep()
