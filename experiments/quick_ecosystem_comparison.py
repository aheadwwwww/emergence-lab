"""
Quick experiment: Compare ecosystem types
Chain vs Cycle vs Web vs Competition

Goal: Validate that mutualistic web has highest diversity
"""

import numpy as np
import sys
sys.path.append('D:/openclaw_workspace/experiments')

# Import the mutualistic_lenia module
from mutualistic_lenia import MutualisticEcosystem

def run_comparison():
    """Run all 4 ecosystem types and compare diversity"""
    
    types = ['chain', 'cycle', 'web', 'competition']
    type_names = {
        'chain': '链式共生',
        'cycle': '环式共生',
        'web': '共生网络',
        'competition': '竞争关系'
    }
    results = {}
    
    for eco_type in types:
        print(f"\nTesting {type_names[eco_type]} ({eco_type})...", end="", flush=True)
        
        eco = MutualisticEcosystem(size=64, ecosystem_type=eco_type)
        
        # Run 200 steps
        diversities = []
        for step in range(200):
            eco.step()
            if step % 50 == 0:
                diversity = eco.get_diversity()
                diversities.append(diversity)
        
        # Final diversity
        final_diversity = np.mean(diversities[-3:])
        alive_count = eco.get_survival_count(threshold=50)
        
        results[eco_type] = {
            'final_diversity': final_diversity,
            'alive_species': alive_count,
            'total_species': len(eco.species)
        }
        
        print(f" OK
  Final diversity: {final_diversity:.2f}")
        print(f"  Alive species: {alive_count}/{len(eco.species)}")
    
    # Print comparison
    print("\n" + "="*50)
    print("COMPARISON RESULTS")
    print("="*50)
    for eco_type, data in results.items():
        print(f"{type_names[eco_type]:12s}: diversity={data['final_diversity']:.2f}, alive={data['alive_species']}/{data['total_species']}")
    
    # Find winner
    winner = max(results.keys(), key=lambda k: results[k]['final_diversity'])
    print(f"\nWinner: {winner}")
    
    return results

if __name__ == "__main__":
    results = run_comparison()
