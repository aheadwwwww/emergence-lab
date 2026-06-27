"""
Rigorous experiment: Run each ecosystem type 10 times

Goal: Get stable average results
"""

import numpy as np
import sys
sys.path.append('D:/openclaw_workspace/experiments')

from mutualistic_lenia import MutualisticEcosystem

def run_comparison(n_runs=10):
    """Run each ecosystem type multiple times"""
    
    types = ['chain', 'cycle', 'web', 'competition']
    type_names = {
        'chain': '链式共生',
        'cycle': '环式共生',
        'web': '共生网络',
        'competition': '竞争关系'
    }
    
    all_results = {t: {'diversity': [], 'alive': []} for t in types}
    
    for run in range(n_runs):
        print(f"\nRun {run+1}/{n_runs}")
        for eco_type in types:
            eco = MutualisticEcosystem(size=64, ecosystem_type=eco_type)
            eco.seed_random(n_seeds=3)
            
            for step in range(200):
                eco.step()
            
            diversity = eco.get_diversity()
            alive = eco.get_survival_count(threshold=50)
            
            all_results[eco_type]['diversity'].append(diversity)
            all_results[eco_type]['alive'].append(alive)
    
    # Print statistics
    print("\n" + "="*60)
    print(f"RESULTS (averaged over {n_runs} runs)")
    print("="*60)
    
    summary = {}
    for eco_type in types:
        mean_div = np.mean(all_results[eco_type]['diversity'])
        std_div = np.std(all_results[eco_type]['diversity'])
        mean_alive = np.mean(all_results[eco_type]['alive'])
        
        summary[eco_type] = {
            'mean_diversity': mean_div,
            'std_diversity': std_div,
            'mean_alive': mean_alive
        }
        
        print(f"{type_names[eco_type]:8s}: diversity={mean_div:.2f}±{std_div:.2f}, alive={mean_alive:.1f}/3")
    
    # Winner
    winner = max(summary.keys(), key=lambda k: summary[k]['mean_diversity'])
    print(f"\nWinner: {type_names[winner]}")
    
    return summary

if __name__ == "__main__":
    results = run_comparison(n_runs=10)
