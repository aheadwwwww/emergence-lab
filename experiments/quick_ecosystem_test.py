"""
Quick ecosystem test - smaller sweep for fast results
"""

import numpy as np
import sys
sys.path.append('D:/openclaw_workspace/experiments')

from mutualistic_lenia import MutualisticEcosystem
import json
from pathlib import Path

def quick_test():
    """Quick test of different configurations"""
    
    results = []
    
    # Test: 3 species, different types, size 64
    n_species = 3
    eco_types = ['web', 'chain', 'cycle', 'competition']
    n_runs = 3
    size = 64
    steps = 100
    
    print(f"Quick test: {n_species} species, size {size}, {steps} steps, {n_runs} runs each\n")
    
    for eco_type in eco_types:
        type_names = {
            'chain': '链式共生',
            'cycle': '环式共生', 
            'web': '共生网络',
            'competition': '竞争关系'
        }
        
        diversities = []
        alive_counts = []
        
        for run in range(n_runs):
            eco = MutualisticEcosystem(size=size, ecosystem_type=eco_type)
            eco.seed_random(n_seeds=n_species)
            
            for step in range(steps):
                eco.step()
            
            diversity = eco.get_diversity()
            alive = eco.get_survival_count(threshold=30)
            
            diversities.append(diversity)
            alive_counts.append(alive)
            
            print(f"{type_names[eco_type]:8s} run {run+1}: div={diversity:.2f}, alive={alive}/{n_species}")
        
        result = {
            'eco_type': eco_type,
            'mean_diversity': np.mean(diversities),
            'std_diversity': np.std(diversities),
            'mean_alive': np.mean(alive_counts),
            'survival_rate': np.mean(alive_counts) / n_species
        }
        
        results.append(result)
        
        print(f"  Average: diversity={result['mean_diversity']:.2f}±{result['std_diversity']:.2f}, survival={result['survival_rate']*100:.0f}%\n")
    
    # Summary
    print("="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    
    best = max(results, key=lambda x: x['mean_diversity'])
    print(f"\nBest ecosystem type: {type_names[best['eco_type']]}")
    print(f"  Diversity: {best['mean_diversity']:.2f}")
    print(f"  Survival rate: {best['survival_rate']*100:.0f}%")
    
    return results

if __name__ == "__main__":
    results = quick_test()