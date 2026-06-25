"""
Lenia + Pheromone Parameter Scan

Runs 16 combinations:
- pheromone_influence: 0.01, 0.03, 0.05, 0.10
- deposit_rate: 0.05, 0.10, 0.20, 0.40

Fixed: steps=300, R=[12,15,18], mu=[0.15,0.15,0.15], sigma=[0.025,0.015,0.008]
"""

import sys
from pathlib import Path

# Add experiments to path
sys.path.insert(0, str(Path(__file__).parent))

from lenia_pheromone import run_lenia_pheromone


def run_parameter_scan():
    """Run parameter scan and print summary table."""
    
    # Parameter ranges
    pheromone_influences = [0.01, 0.03, 0.05, 0.10]
    deposit_rates = [0.05, 0.10, 0.20, 0.40]
    
    # Fixed parameters
    steps = 300
    R_list = [12, 15, 18]
    mu_list = [0.15, 0.15, 0.15]
    sigma_list = [0.025, 0.015, 0.008]
    
    # Results storage
    results = []
    
    # Output directory
    output_dir = Path(__file__).parent
    
    print("=" * 100)
    print("Lenia + Pheromone Parameter Scan")
    print("=" * 100)
    print(f"Combinations: {len(pheromone_influences)} x {len(deposit_rates)} = {len(pheromone_influences) * len(deposit_rates)}")
    print(f"Fixed: steps={steps}, R={R_list}, mu={mu_list}, sigma={sigma_list}")
    print()
    
    total = len(pheromone_influences) * len(deposit_rates)
    count = 0
    
    for influence in pheromone_influences:
        for deposit in deposit_rates:
            count += 1
            print(f"[{count}/{total}] Running: influence={influence}, deposit={deposit}")
            
            # Output file
            output_file = output_dir / f"lenia_pheromone_inf{influence}_dep{deposit}.png"
            
            # Run simulation
            result = run_lenia_pheromone(
                shape=(256, 256),
                R_list=R_list,
                mu_list=mu_list,
                sigma_list=sigma_list,
                kn_list=[1, 1, 1],
                gn_list=[1, 1, 1],
                coupling=None,  # Use default coupling
                deposit_rate=deposit,
                decay_rate=0.05,
                diffusion_sigma=2.0,
                pheromone_influence=influence,
                steps=steps,
                init='random',
                record_every=20,
                save_timeline=str(output_file),
            )
            
            # Store results
            results.append({
                'influence': influence,
                'deposit': deposit,
                'alive': result['stats']['alive'],
                'score': result['stats']['score'],
                'chR_alive': result['channel_stats']['chR']['alive'],
                'chG_alive': result['channel_stats']['chG']['alive'],
                'chB_alive': result['channel_stats']['chB']['alive'],
                'time': result['time'],
                'state': result['state'],
            })
            
            print(f"    -> {result['state']} | alive={result['stats']['alive']:.4f} | time={result['time']}s")
            print(f"    -> Saved: {output_file.name}")
            print()
    
    # Print summary table
    print()
    print("=" * 100)
    print("RESULTS SUMMARY")
    print("=" * 100)
    print()
    
    # Header
    print(f"{'Influence':<12} {'Deposit':<10} {'Alive':<10} {'Score':<10} {'chR':<10} {'chG':<10} {'chB':<10} {'Time':<8}")
    print("-" * 88)
    
    # Rows
    for r in results:
        print(f"{r['influence']:<12} {r['deposit']:<10} {r['alive']:<10.4f} {r['score']:<10.4f} "
              f"{r['chR_alive']:<10.4f} {r['chG_alive']:<10.4f} {r['chB_alive']:<10.4f} {r['time']:<8.2f}")
    
    print()
    print("=" * 100)
    print(f"Total runs: {len(results)}")
    print(f"Output files: {output_dir / 'lenia_pheromone_inf*_dep*.png'}")
    print("=" * 100)
    
    return results


if __name__ == '__main__':
    run_parameter_scan()