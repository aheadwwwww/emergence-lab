"""
Work-Loop Cycle 2: Self-Organized Criticality in Lenia Systems
Tests whether Lenia dynamics exhibit SOC-like power-law distributions
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
    """Lenia growth function - creates attractor dynamics"""
    return 2 * np.exp(-((U - mu)**2) / (2 * sigma**2)) - 1

def measure_avalanche_sizes(grid, kernel, steps=50):
    """Measure 'avalanche' sizes - clusters of change above threshold"""
    avalanche_sizes = []
    prev_grid = grid.copy()
    
    for step in range(steps):
        # Lenia update
        U = ndimage.convolve(prev_grid, kernel, mode='wrap')
        G = growth_func(U)
        new_grid = np.clip(prev_grid + 0.1 * G, 0, 1)
        
        # Measure change clusters (avalanches)
        change = np.abs(new_grid - prev_grid)
        threshold = 0.02
        active = change > threshold
        
        if active.any():
            # Label connected components
            labeled, num_features = ndimage.label(active)
            for i in range(1, num_features + 1):
                size = (labeled == i).sum()
                if size > 1:
                    avalanche_sizes.append(size)
        
        prev_grid = new_grid
    
    return avalanche_sizes, prev_grid

def test_power_law(sizes):
    """Test if size distribution follows power law (signature of SOC)"""
    if len(sizes) < 10:
        return None, None
    
    # Log-bin the sizes
    sizes = np.array(sizes)
    log_sizes = np.log(sizes)
    
    # Simple power law fit: log(count) ~ -tau * log(size)
    size_counts = Counter(sizes)
    unique_sizes = np.array(sorted(size_counts.keys()))
    counts = np.array([size_counts[s] for s in unique_sizes])
    
    if len(unique_sizes) < 3:
        return None, None
    
    log_s = np.log(unique_sizes)
    log_c = np.log(counts)
    
    # Linear fit
    coeffs = np.polyfit(log_s, log_c, 1)
    tau = -coeffs[0]  # Power law exponent
    
    return tau, coeffs[1]

# Run experiment
np.random.seed(42)
grid = np.random.rand(64, 64)
kernel = create_gaussian_kernel(R=13, T=0.1, sigma=0.15)

print("Cycle 2: Self-Organized Criticality in Lenia")
print("=" * 50)

# Measure avalanches
avalanche_sizes, final_grid = measure_avalanche_sizes(grid, kernel, steps=50)
print(f"Detected {len(avalanche_sizes)} avalanches")
print(f"Size range: {min(avalanche_sizes) if avalanche_sizes else 0} - {max(avalanche_sizes) if avalanche_sizes else 0}")

# Test for power law
tau, intercept = test_power_law(avalanche_sizes)
if tau:
    print(f"Power law exponent tau: {tau:.3f}")
    print(f"SOC signature: {'YES' if 1.5 < tau < 3.0 else 'WEAK'}")
else:
    print("Insufficient data for power law fit")

# Analyze final state
mean_val = final_grid.mean()
std_val = final_grid.std()
print(f"\nFinal state: mean={mean_val:.3f}, std={std_val:.3f}")

# Cluster analysis
thresholded = final_grid > 0.5
labeled, num_clusters = ndimage.label(thresholded)
cluster_sizes = ndimage.sum(thresholded, labeled, range(1, num_clusters + 1))
print(f"Active clusters: {num_clusters}")
if len(cluster_sizes) > 0:
    print(f"Cluster size distribution: min={cluster_sizes.min():.0f}, max={cluster_sizes.max():.0f}, mean={cluster_sizes.mean():.1f}")

# Save results
results = {
    "experiment": "lenia_criticality",
    "topic": "self-organized criticality",
    "parameters": {
        "grid_size": 64,
        "kernel_R": 13,
        "kernel_T": 0.1,
        "kernel_sigma": 0.15,
        "steps": 50
    },
    "results": {
        "num_avalanches": len(avalanche_sizes),
        "avalanche_size_range": [int(min(avalanche_sizes)) if avalanche_sizes else 0, 
                                  int(max(avalanche_sizes)) if avalanche_sizes else 0],
        "power_law_tau": float(tau) if tau else None,
        "soc_detected": bool(1.5 < tau < 3.0) if tau else False,
        "final_mean": float(mean_val),
        "final_std": float(std_val),
        "num_clusters": int(num_clusters)
    }
}

os.makedirs("D:/openclaw_workspace/exploration", exist_ok=True)
with open("D:/openclaw_workspace/exploration/lenia_criticality_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nResults saved to lenia_criticality_results.json")
