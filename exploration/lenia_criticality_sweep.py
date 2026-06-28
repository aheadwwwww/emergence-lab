"""
Work-Loop Cycle 3: Critical Regime Discovery in Lenia
Sweep parameters to find SOC regime, then test evolutionary optimization
"""
import numpy as np
from scipy import ndimage
import json
import os
from collections import Counter

def create_gaussian_kernel(R=13, T=0.1, sigma=0.15):
    """Create Lenia's Gaussian ring kernel"""
    size = 2 * R + 1
    y, x = np.ogrid[-R:R+1, -R:R+1]
    dist = np.sqrt(x**2 + y**2) / R
    kernel = np.exp(-((dist - T)**2) / (2 * sigma**2))
    kernel[dist > 1] = 0
    kernel /= kernel.sum()
    return kernel

def growth_func(U, mu=0.15, sigma=0.015):
    """Lenia growth function"""
    return 2 * np.exp(-((U - mu)**2) / (2 * sigma**2)) - 1

def measure_avalanche_sizes(grid, kernel, steps=50, change_threshold=0.02):
    """Measure avalanche sizes with configurable threshold"""
    avalanche_sizes = []
    prev_grid = grid.copy()
    
    for step in range(steps):
        U = ndimage.convolve(prev_grid, kernel, mode='wrap')
        G = growth_func(U)
        new_grid = np.clip(prev_grid + 0.1 * G, 0, 1)
        
        change = np.abs(new_grid - prev_grid)
        active = change > change_threshold
        
        if active.any():
            labeled, num_features = ndimage.label(active)
            for i in range(1, num_features + 1):
                size = (labeled == i).sum()
                if size > 1:
                    avalanche_sizes.append(size)
        
        prev_grid = new_grid
    
    return avalanche_sizes, prev_grid

def test_power_law(sizes):
    """Test if size distribution follows power law"""
    if len(sizes) < 10:
        return None, None
    
    sizes = np.array(sizes)
    size_counts = Counter(sizes)
    unique_sizes = np.array(sorted(size_counts.keys()))
    counts = np.array([size_counts[s] for s in unique_sizes])
    
    if len(unique_sizes) < 3:
        return None, None
    
    log_s = np.log(unique_sizes)
    log_c = np.log(counts)
    
    coeffs = np.polyfit(log_s, log_c, 1)
    tau = -coeffs[0]
    
    return tau, coeffs[1]

def analyze_state(grid):
    """Analyze final state properties"""
    mean_val = grid.mean()
    std_val = grid.std()
    
    # Active clusters
    thresholded = grid > 0.5
    labeled, num_clusters = ndimage.label(thresholded)
    cluster_sizes = ndimage.sum(thresholded, labeled, range(1, num_clusters + 1))
    
    # Entropy measure
    hist, _ = np.histogram(grid, bins=20, range=(0, 1))
    hist = hist / hist.sum()
    entropy = -np.sum(hist * np.log2(hist + 1e-10))
    
    return {
        'mean': float(mean_val),
        'std': float(std_val),
        'num_clusters': int(num_clusters),
        'entropy': float(entropy)
    }

def parameter_sweep():
    """Sweep T and sigma to find critical regime"""
    print("=" * 60)
    print("CYCLE 3: Critical Regime Discovery in Lenia")
    print("=" * 60)
    
    # Parameter ranges
    T_values = np.linspace(0.05, 0.5, 10)  # Ring center
    sigma_values = np.linspace(0.05, 0.3, 6)  # Ring width
    
    results = []
    best_tau = 0
    best_params = None
    
    np.random.seed(42)
    initial_grid = np.random.rand(64, 64)
    
    total = len(T_values) * len(sigma_values)
    count = 0
    
    print(f"\nSweeping {total} parameter combinations...")
    print("-" * 60)
    
    for T in T_values:
        for sigma in sigma_values:
            count += 1
            kernel = create_gaussian_kernel(R=13, T=T, sigma=sigma)
            avalanche_sizes, final_grid = measure_avalanche_sizes(
                initial_grid.copy(), kernel, steps=50
            )
            
            tau, _ = test_power_law(avalanche_sizes)
            state_info = analyze_state(final_grid)
            
            # Criticality score: how close to ideal tau range
            if tau:
                # Distance to middle of critical range (2.25)
                critical_distance = abs(tau - 2.25)
                in_critical = 1.5 < tau < 3.0
            else:
                critical_distance = 10
                in_critical = False
            
            result = {
                'T': float(T),
                'sigma': float(sigma),
                'tau': float(tau) if tau else None,
                'in_critical': in_critical,
                'critical_distance': float(critical_distance),
                'num_avalanches': len(avalanche_sizes),
                **state_info
            }
            results.append(result)
            
            if tau and tau > best_tau:
                best_tau = tau
                best_params = (T, sigma)
            
            if count % 10 == 0:
                print(f"  Progress: {count}/{total} | Best τ so far: {best_tau:.3f}")
    
    return results, best_params, best_tau

def evolutionary_criticality_search(initial_params, generations=20, population_size=12):
    """Use evolution to find parameters that maximize criticality"""
    print("\n" + "=" * 60)
    print("EVOLUTIONARY SEARCH FOR CRITICALITY")
    print("=" * 60)
    
    np.random.seed(123)
    initial_grid = np.random.rand(64, 64)
    
    # Initialize population around best sweep result
    population = []
    for _ in range(population_size):
        T = initial_params[0] + np.random.uniform(-0.05, 0.05)
        sigma = initial_params[1] + np.random.uniform(-0.02, 0.02)
        T = np.clip(T, 0.05, 0.5)
        sigma = np.clip(sigma, 0.05, 0.3)
        population.append({'T': T, 'sigma': sigma})
    
    evolution_log = []
    
    for gen in range(generations):
        # Evaluate fitness (criticality)
        fitness_scores = []
        for individual in population:
            kernel = create_gaussian_kernel(R=13, T=individual['T'], sigma=individual['sigma'])
            avalanche_sizes, _ = measure_avalanche_sizes(initial_grid.copy(), kernel, steps=50)
            tau, _ = test_power_law(avalanche_sizes)
            
            if tau:
                # Fitness: maximize proximity to critical range center
                # Also penalize being outside [1.5, 3.0]
                if 1.5 < tau < 3.0:
                    fitness = 1.0 / (1.0 + abs(tau - 2.25))
                else:
                    fitness = 0.1 / (1.0 + abs(tau - 2.25))
            else:
                fitness = 0.01
            
            individual['tau'] = tau
            individual['fitness'] = fitness
            fitness_scores.append(fitness)
        
        # Sort by fitness
        population.sort(key=lambda x: x['fitness'], reverse=True)
        
        best = population[0]
        avg_fitness = np.mean(fitness_scores)
        
        evolution_log.append({
            'generation': gen,
            'best_T': best['T'],
            'best_sigma': best['sigma'],
            'best_tau': best['tau'],
            'best_fitness': best['fitness'],
            'avg_fitness': float(avg_fitness)
        })
        
        if gen % 5 == 0:
            tau_str = f"{best['tau']:.3f}" if best['tau'] else "N/A"
            print(f"  Gen {gen}: τ={tau_str:>6} | "
                  f"T={best['T']:.3f}, σ={best['sigma']:.3f} | fitness={best['fitness']:.4f}")
        
        # Selection + reproduction
        survivors = population[:population_size // 2]
        new_population = survivors.copy()
        
        while len(new_population) < population_size:
            parent = survivors[np.random.randint(len(survivors))]
            child = {
                'T': parent['T'] + np.random.uniform(-0.02, 0.02),
                'sigma': parent['sigma'] + np.random.uniform(-0.01, 0.01)
            }
            child['T'] = np.clip(child['T'], 0.05, 0.5)
            child['sigma'] = np.clip(child['sigma'], 0.05, 0.3)
            new_population.append(child)
        
        population = new_population
    
    return evolution_log, population[0]

# Run experiments
sweep_results, best_sweep_params, best_sweep_tau = parameter_sweep()

print("\n" + "-" * 60)
print("SWEEP RESULTS SUMMARY")
print("-" * 60)

# Find critical regime entries
critical_entries = [r for r in sweep_results if r['in_critical']]
print(f"Parameters in critical regime (1.5 < τ < 3.0): {len(critical_entries)}")

if critical_entries:
    print("\nCritical regime found at:")
    for entry in critical_entries[:5]:
        print(f"  T={entry['T']:.3f}, σ={entry['sigma']:.3f} → τ={entry['tau']:.3f}")
else:
    print("\nNo parameters reached critical regime.")
    print(f"Best τ from sweep: {best_sweep_tau:.3f} at T={best_sweep_params[0]:.3f}, σ={best_sweep_params[1]:.3f}")

# Evolutionary refinement
if best_sweep_params:
    evo_log, best_evo = evolutionary_criticality_search(best_sweep_params)
    print("\n" + "-" * 60)
    print("EVOLUTIONARY RESULTS")
    print("-" * 60)
    print(f"Best evolved: T={best_evo['T']:.4f}, σ={best_evo['sigma']:.4f}")
    tau_str = f"{best_evo['tau']:.3f}" if best_evo['tau'] else "N/A"
    print(f"Final τ: {tau_str}")
    print(f"Fitness: {best_evo['fitness']:.4f}")

# Save comprehensive results
output = {
    "experiment": "lenia_criticality_sweep",
    "cycle": 3,
    "topic": "critical_regime_discovery",
    "sweep_summary": {
        "total_combinations": len(sweep_results),
        "critical_regime_count": len(critical_entries),
        "best_tau": float(best_sweep_tau),
        "best_params": [float(best_sweep_params[0]), float(best_sweep_params[1])] if best_sweep_params else None
    },
    "sweep_results": sweep_results,
    "evolution_log": evo_log if 'evo_log' in dir() else [],
    "best_evolved": {
        "T": float(best_evo['T']),
        "sigma": float(best_evo['sigma']),
        "tau": float(best_evo['tau']) if best_evo['tau'] else None,
        "fitness": float(best_evo['fitness'])
    } if 'best_evo' in dir() else None
}

os.makedirs("D:/openclaw_workspace/exploration", exist_ok=True)
with open("D:/openclaw_workspace/exploration/lenia_criticality_sweep_results.json", "w") as f:
    json.dump(output, f, indent=2)

print("\nResults saved to lenia_criticality_sweep_results.json")
