"""
Scale-Free Networks in Lenia

Exploring how scale-free network topology emerges in Lenia dynamics.
Scale-free networks follow a power-law degree distribution: P(k) ~ k^(-γ)

Key questions:
1. Can we extract a network from Lenia patterns where nodes = coherent structures?
2. Does the connectivity follow a power law?
3. How does network topology relate to pattern stability?

Approach:
- Run Lenia and identify coherent structures (local maxima above threshold)
- Build adjacency network based on spatial proximity
- Analyze degree distribution for power-law signature
- Compare across different Lenia parameters
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import convolve, maximum_filter, label
from scipy.spatial.distance import cdist
from collections import Counter
import json
import os

# ============ Lenia Core ============

def create_kernel(R: int, peaks: list) -> np.ndarray:
    """Create multi-peak Lenia kernel"""
    size = 2 * R + 1
    y, x = np.ogrid[-R:R+1, -R:R+1]
    d = np.sqrt(x**2 + y**2) / R
    
    kernel = np.zeros_like(d)
    for center, width, weight in peaks:
        kernel += weight * np.exp(-((d - center) / width) ** 2)
    
    return kernel / kernel.sum() if kernel.sum() > 0 else kernel

def lenia_step(field: np.ndarray, kernel: np.ndarray, mu: float, sigma: float) -> np.ndarray:
    """Single Lenia update step"""
    U = convolve(field, kernel, mode='wrap')
    G = np.exp(-((U - mu) / sigma) ** 2) - 0.5
    return np.clip(field + 0.1 * G, 0, 1)

# ============ Network Extraction ============

def extract_structures(field: np.ndarray, threshold: float = 0.5, min_size: int = 5) -> list:
    """
    Extract coherent structures from Lenia field.
    Returns list of (x, y, mass) tuples representing nodes.
    """
    # Find local maxima
    max_filtered = maximum_filter(field, size=5)
    local_max = (field == max_filtered) & (field > threshold)
    
    # Label connected components
    labeled, num_features = label(local_max)
    
    structures = []
    for i in range(1, num_features + 1):
        mask = labeled == i
        if mask.sum() >= min_size:
            # Find centroid and total mass
            y_coords, x_coords = np.where(mask)
            masses = field[mask]
            total_mass = masses.sum()
            
            cx = (x_coords * masses).sum() / total_mass
            cy = (y_coords * masses).sum() / total_mass
            
            structures.append((cx, cy, total_mass))
    
    return structures

def build_network(structures: list, connection_radius: float) -> tuple:
    """
    Build network from structures.
    Returns adjacency list and degree distribution.
    """
    n = len(structures)
    if n < 2:
        return {}, []
    
    # Compute pairwise distances
    positions = np.array([(s[0], s[1]) for s in structures])
    distances = cdist(positions, positions)
    
    # Build adjacency
    adjacency = {i: [] for i in range(n)}
    for i in range(n):
        for j in range(i+1, n):
            if distances[i, j] < connection_radius:
                adjacency[i].append(j)
                adjacency[j].append(i)
    
    # Degree distribution
    degrees = [len(adjacency[i]) for i in range(n)]
    
    return adjacency, degrees

def fit_power_law(degrees: list) -> tuple:
    """
    Fit power law to degree distribution.
    Returns (gamma, r_squared) where P(k) ~ k^(-gamma)
    """
    if len(degrees) < 10:
        return 0, 0
    
    # Count degree frequencies
    degree_counts = Counter(degrees)
    ks = np.array(sorted(degree_counts.keys()))
    counts = np.array([degree_counts[k] for k in ks])
    
    # Filter out zeros and take logs
    valid = counts > 0
    log_k = np.log(ks[valid])
    log_p = np.log(counts[valid] / sum(counts))
    
    if len(log_k) < 3:
        return 0, 0
    
    # Linear regression: log(P) = -gamma * log(k) + c
    A = np.vstack([log_k, np.ones(len(log_k))]).T
    slope, intercept = np.linalg.lstsq(A, log_p, rcond=None)[0]
    
    # R-squared
    predictions = slope * log_k + intercept
    ss_res = np.sum((log_p - predictions) ** 2)
    ss_tot = np.sum((log_p - log_p.mean()) ** 2)
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    
    return -slope, r_squared

# ============ Experiment ============

def run_scale_free_experiment():
    """Test scale-free network emergence in Lenia"""
    
    print("=" * 60)
    print("SCALE-FREE NETWORK EMERGENCE IN LENIA")
    print("=" * 60)
    
    results = {
        'experiment': 'scale_free_networks',
        'parameters': [],
        'network_stats': [],
        'power_law_fits': []
    }
    
    # Test different Lenia configurations
    configs = [
        {'R': 13, 'peaks': [(0.5, 0.15, 1.0)], 'mu': 0.15, 'sigma': 0.015, 'name': 'standard'},
        {'R': 15, 'peaks': [(0.3, 0.12, 1.0), (0.7, 0.12, 0.5)], 'mu': 0.12, 'sigma': 0.02, 'name': 'dual_ring'},
        {'R': 20, 'peaks': [(0.4, 0.1, 1.0)], 'mu': 0.2, 'sigma': 0.025, 'name': 'wide_kernel'},
    ]
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    for idx, config in enumerate(configs):
        print(f"\n[Config: {config['name']}]")
        
        # Create kernel
        kernel = create_kernel(config['R'], config['peaks'])
        
        # Initialize field
        size = 128
        field = np.random.rand(size, size)
        
        # Run Lenia
        n_steps = 150
        for _ in range(n_steps):
            field = lenia_step(field, kernel, config['mu'], config['sigma'])
        
        # Extract structures
        structures = extract_structures(field, threshold=0.4, min_size=3)
        print(f"  Structures found: {len(structures)}")
        
        # Build network
        connection_radius = size / 10
        adjacency, degrees = build_network(structures, connection_radius)
        
        # Analyze degree distribution
        if degrees:
            mean_deg = np.mean(degrees)
            max_deg = max(degrees)
            gamma, r2 = fit_power_law(degrees)
            
            print(f"  Network: {len(structures)} nodes, mean degree={mean_deg:.2f}, max={max_deg}")
            print(f"  Power law: γ={gamma:.3f}, R²={r2:.3f}")
            
            results['network_stats'].append({
                'config': config['name'],
                'nodes': len(structures),
                'mean_degree': float(mean_deg),
                'max_degree': int(max_deg),
                'gamma': float(gamma),
                'r_squared': float(r2)
            })
            
            # Scale-free signature: γ typically between 2 and 3
            is_scale_free = 2.0 < gamma < 3.0 and r2 > 0.7
            print(f"  Scale-free? {'YES' if is_scale_free else 'WEAK/NO'}")
        
        # Plot field
        axes[0, idx].imshow(field, cmap='viridis')
        axes[0, idx].set_title(f"{config['name']}\n{len(structures)} structures")
        axes[0, idx].axis('off')
        
        # Plot degree distribution
        if degrees:
            degree_counts = Counter(degrees)
            ks = sorted(degree_counts.keys())
            counts = [degree_counts[k] for k in ks]
            
            axes[1, idx].loglog(ks, counts, 'bo-', markersize=8)
            axes[1, idx].set_xlabel('Degree k')
            axes[1, idx].set_ylabel('Count P(k)')
            axes[1, idx].set_title(f'Degree dist: γ={gamma:.2f}')
            axes[1, idx].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('scale_free_lenia_results.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    # Find most scale-free configuration
    best = max(results['network_stats'], key=lambda x: x['r_squared']) if results['network_stats'] else None
    if best:
        print(f"Best power-law fit: {best['config']} with γ={best['gamma']:.3f}, R²={best['r_squared']:.3f}")
        
        if 2.0 < best['gamma'] < 3.0:
            print("✓ Scale-free network topology detected!")
            print("  This suggests self-organized criticality in Lenia dynamics.")
        else:
            print("✗ No clear scale-free signature found.")
            print("  Network topology may be random or exponential.")
    
    # Save results
    with open('scale_free_lenia_data.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    results = run_scale_free_experiment()
