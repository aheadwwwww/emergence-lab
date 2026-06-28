"""
Evolutionary Lenia V10 - Hybrid Conv+GNN System
================================================
Combines FFT-based convolution with GNN pathway for enhanced pattern formation.

Architecture:
- Conv pathway: 64x64 FFT-based Lenia
- GNN pathway: 16x16 coarse mesh with message passing
- Fusion: learnable w_conv * conv_update + w_gnn * gnn_update
"""

import numpy as np
from scipy.ndimage import convolve, zoom
from scipy.fft import fft2, ifft2, fftfreq
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG = {
    'grid_size': 64,
    'coarse_size': 16,
    'generations': 10,
    'population_size': 6,
    'steps_per_eval': 150,
    'dt': 0.1,
    
    # V9 warm-start params
    'init_mu': 0.20,
    'init_sigma': 0.10,
    
    # Evolution params
    'mutation_rate': 0.15,
    'mutation_strength': 0.05,
    
    # Output
    'output_path': r'D:\openclaw_workspace\experiments\v10_hybrid_results.json'
}

# ============================================================================
# KERNEL GENERATION
# ============================================================================

def create_gaussian_kernel(size: int, radius: float = 13.0, sigma_k: float = 4.0) -> np.ndarray:
    """Create Gaussian ring kernel for Lenia."""
    kernel = np.zeros((size, size))
    center = size // 2
    
    for i in range(size):
        for j in range(size):
            d = np.sqrt((i - center)**2 + (j - center)**2)
            # Ring-shaped kernel
            kernel[i, j] = np.exp(-((d - radius)**2) / (2 * sigma_k**2))
    
    # Normalize
    kernel /= kernel.sum() if kernel.sum() > 0 else 1
    return kernel

def create_kernel_fft(kernel: np.ndarray) -> np.ndarray:
    """Precompute FFT of kernel for fast convolution."""
    return fft2(kernel)

# ============================================================================
# CONVOLUTION PATHWAY (FFT-based)
# ============================================================================

class ConvPathway:
    """FFT-based Lenia convolution pathway."""
    
    def __init__(self, size: int = 64):
        self.size = size
        self.kernel = create_gaussian_kernel(size)
        self.kernel_fft = create_kernel_fft(self.kernel)
    
    def compute_update(self, grid: np.ndarray) -> np.ndarray:
        """Compute convolution update using FFT."""
        grid_fft = fft2(grid)
        convolved = np.real(ifft2(grid_fft * self.kernel_fft))
        return convolved
    
    def apply_growth(self, convolved: np.ndarray, mu: float, sigma: float) -> np.ndarray:
        """Apply Gaussian growth function."""
        # Growth function: G(u) = exp(-(u-mu)^2 / (2*sigma^2))
        growth = np.exp(-((convolved - mu)**2) / (2 * sigma**2))
        return growth

# ============================================================================
# GNN PATHWAY
# ============================================================================

class GNNPathway:
    """Graph Neural Network pathway operating on coarse mesh."""
    
    def __init__(self, fine_size: int = 64, coarse_size: int = 16):
        self.fine_size = fine_size
        self.coarse_size = coarse_size
        self.scale = fine_size // coarse_size
        
        # Build adjacency for coarse grid
        self.adjacency, self.edge_weights = self._build_adjacency()
        
        # GNN weights
        self.node_weight = 0.5
        self.neighbor_weight = 0.3
        self.self_weight = 0.2
    
    def _build_adjacency(self) -> Tuple[np.ndarray, np.ndarray]:
        """Build adjacency matrix for coarse grid (8-connectivity)."""
        n = self.coarse_size ** 2
        adj = np.zeros((n, n))
        
        def idx(i, j):
            return i * self.coarse_size + j
        
        for i in range(self.coarse_size):
            for j in range(self.coarse_size):
                node = idx(i, j)
                # 8-connectivity
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue
                        ni, nj = (i + di) % self.coarse_size, (j + dj) % self.coarse_size
                        neighbor = idx(ni, nj)
                        adj[node, neighbor] = 1
        
        # Initialize edge weights
        edge_weights = np.ones_like(adj) * 0.5
        return adj, edge_weights
    
    def downsample(self, grid: np.ndarray) -> np.ndarray:
        """Downsample fine grid to coarse grid."""
        # Average pooling
        coarse = np.zeros((self.coarse_size, self.coarse_size))
        for i in range(self.coarse_size):
            for j in range(self.coarse_size):
                region = grid[i*self.scale:(i+1)*self.scale, j*self.scale:(j+1)*self.scale]
                coarse[i, j] = np.mean(region)
        return coarse
    
    def upsample(self, coarse: np.ndarray) -> np.ndarray:
        """Upsample coarse grid to fine grid."""
        # Nearest neighbor upsampling
        return zoom(coarse, self.scale, order=1)
    
    def message_passing(self, nodes: np.ndarray) -> np.ndarray:
        """Perform one round of message passing."""
        n = len(nodes)
        new_nodes = np.zeros_like(nodes)
        
        for i in range(n):
            # Self contribution
            new_nodes[i] = self.self_weight * nodes[i]
            
            # Neighbor contributions
            neighbors = np.where(self.adjacency[i] > 0)[0]
            if len(neighbors) > 0:
                neighbor_sum = 0
                for j in neighbors:
                    weight = self.edge_weights[i, j]
                    neighbor_sum += weight * nodes[j]
                new_nodes[i] += self.neighbor_weight * neighbor_sum / len(neighbors)
        
        return new_nodes
    
    def compute_update(self, grid: np.ndarray) -> np.ndarray:
        """Compute GNN update for the fine grid."""
        # Downsample
        coarse = self.downsample(grid)
        
        # Flatten to node features
        nodes = coarse.flatten()
        
        # Message passing (2 rounds)
        nodes = self.message_passing(nodes)
        nodes = self.message_passing(nodes)
        
        # Reshape back
        coarse_update = nodes.reshape(self.coarse_size, self.coarse_size)
        
        # Upsample
        fine_update = self.upsample(coarse_update)
        
        # Resize to match fine grid if needed
        if fine_update.shape != (self.fine_size, self.fine_size):
            fine_update = zoom(fine_update, self.fine_size / fine_update.shape[0], order=1)
        
        return fine_update

# ============================================================================
# HYBRID LENIA SYSTEM
# ============================================================================

class HybridLenia:
    """Hybrid Conv+GNN Lenia system."""
    
    def __init__(self, params: Dict):
        self.params = params
        self.size = CONFIG['grid_size']
        
        # Initialize pathways
        self.conv = ConvPathway(self.size)
        self.gnn = GNNPathway(self.size, CONFIG['coarse_size'])
        
        # Extract parameters
        self.mu = params['mu']
        self.sigma = params['sigma']
        self.w_conv = params['w_conv']
        self.w_gnn = params['w_gnn']
        
        # GNN edge weight (single scalar for simplicity)
        self.gnn_edge_weight = params.get('gnn_edge_weight', 0.5)
        self.gnn.edge_weights = np.ones_like(self.gnn.edge_weights) * self.gnn_edge_weight
    
    def step(self, grid: np.ndarray) -> np.ndarray:
        """Perform one simulation step."""
        # Conv pathway
        conv_update = self.conv.compute_update(grid)
        growth = self.conv.apply_growth(conv_update, self.mu, self.sigma)
        conv_result = growth - 0.5  # Center around 0
        
        # GNN pathway
        gnn_result = self.gnn.compute_update(grid)
        
        # Normalize GNN result
        if gnn_result.max() > gnn_result.min():
            gnn_result = (gnn_result - gnn_result.min()) / (gnn_result.max() - gnn_result.min())
        gnn_result = gnn_result - 0.5  # Center around 0
        
        # Fusion
        combined = self.w_conv * conv_result + self.w_gnn * gnn_result
        
        # Update
        new_grid = grid + CONFIG['dt'] * combined
        
        # Clamp to [0, 1]
        new_grid = np.clip(new_grid, 0, 1)
        
        return new_grid
    
    def simulate(self, steps: int, init_grid: np.ndarray = None) -> Tuple[np.ndarray, List[np.ndarray]]:
        """Run simulation for given steps."""
        if init_grid is None:
            # Initialize with random pattern
            grid = np.random.rand(self.size, self.size) * 0.3
            # Add a central blob
            center = self.size // 2
            y, x = np.ogrid[:self.size, :self.size]
            mask = ((x - center)**2 + (y - center)**2) < 100
            grid[mask] += 0.4
            grid = np.clip(grid, 0, 1)
        else:
            grid = init_grid.copy()
        
        history = [grid.copy()]
        
        for _ in range(steps):
            grid = self.step(grid)
            history.append(grid.copy())
        
        return grid, history

# ============================================================================
# EVOLUTION
# ============================================================================

def create_individual(mu: float = None, sigma: float = None, 
                      w_conv: float = None, w_gnn: float = None,
                      gnn_edge_weight: float = None) -> Dict:
    """Create an individual with given or random parameters."""
    if mu is None:
        mu = CONFIG['init_mu'] + np.random.uniform(-0.05, 0.05)
    if sigma is None:
        sigma = CONFIG['init_sigma'] + np.random.uniform(-0.02, 0.02)
    if w_conv is None:
        w_conv = np.random.uniform(0.3, 0.8)
    if w_gnn is None:
        w_gnn = 1.0 - w_conv + np.random.uniform(-0.1, 0.1)
    if gnn_edge_weight is None:
        gnn_edge_weight = np.random.uniform(0.3, 0.7)
    
    # Normalize weights
    total = w_conv + w_gnn
    w_conv /= total
    w_gnn /= total
    
    return {
        'mu': np.clip(mu, 0.1, 0.35),
        'sigma': np.clip(sigma, 0.05, 0.2),
        'w_conv': np.clip(w_conv, 0.2, 0.8),
        'w_gnn': np.clip(w_gnn, 0.2, 0.8),
        'gnn_edge_weight': np.clip(gnn_edge_weight, 0.2, 0.8),
        'fitness': 0.0,
        'metrics': {}
    }

def evaluate_individual(individual: Dict) -> Dict:
    """Evaluate an individual and return metrics."""
    system = HybridLenia(individual)
    final_grid, history = system.simulate(CONFIG['steps_per_eval'])
    
    # Metrics
    final_mean = np.mean(final_grid)
    final_std = np.std(final_grid)
    
    # Survival: pattern persists above threshold
    survival = 1.0 if final_mean > 0.05 else 0.0
    
    # Complexity: spatial variance (how varied the pattern is)
    # Use variance of local means
    regions = []
    for i in range(4):
        for j in range(4):
            region = final_grid[i*16:(i+1)*16, j*16:(j+1)*16]
            regions.append(np.mean(region))
    complexity = np.std(regions) * 4  # Scale up
    
    # Stability: temporal correlation (how much pattern persists)
    if len(history) > 10:
        early = history[-10]
        late = history[-1]
        # Correlation coefficient
        early_flat = early.flatten()
        late_flat = late.flatten()
        if np.std(early_flat) > 0 and np.std(late_flat) > 0:
            stability = np.corrcoef(early_flat, late_flat)[0, 1]
            stability = max(0, stability)  # Clamp negative
        else:
            stability = 0
    else:
        stability = 0
    
    # Combined fitness
    # Weight survival heavily, then complexity and stability
    fitness = survival * 0.5 + complexity * 0.25 + stability * 0.25
    
    metrics = {
        'final_mean': float(final_mean),
        'final_std': float(final_std),
        'survival': float(survival),
        'complexity': float(complexity),
        'stability': float(stability),
        'fitness': float(fitness)
    }
    
    individual['fitness'] = fitness
    individual['metrics'] = metrics
    
    return individual

def mutate(individual: Dict) -> Dict:
    """Mutate an individual."""
    new_ind = individual.copy()
    
    if np.random.random() < CONFIG['mutation_rate']:
        new_ind['mu'] += np.random.uniform(-1, 1) * CONFIG['mutation_strength']
        new_ind['mu'] = np.clip(new_ind['mu'], 0.1, 0.35)
    
    if np.random.random() < CONFIG['mutation_rate']:
        new_ind['sigma'] += np.random.uniform(-1, 1) * CONFIG['mutation_strength'] * 0.5
        new_ind['sigma'] = np.clip(new_ind['sigma'], 0.05, 0.2)
    
    if np.random.random() < CONFIG['mutation_rate']:
        new_ind['w_conv'] += np.random.uniform(-1, 1) * CONFIG['mutation_strength']
        new_ind['w_conv'] = np.clip(new_ind['w_conv'], 0.2, 0.8)
        new_ind['w_gnn'] = 1.0 - new_ind['w_conv']
    
    if np.random.random() < CONFIG['mutation_rate']:
        new_ind['gnn_edge_weight'] += np.random.uniform(-1, 1) * CONFIG['mutation_strength']
        new_ind['gnn_edge_weight'] = np.clip(new_ind['gnn_edge_weight'], 0.2, 0.8)
    
    return new_ind

def crossover(parent1: Dict, parent2: Dict) -> Dict:
    """Create child from two parents."""
    child = {}
    
    # Blend parameters
    alpha = np.random.random()
    child['mu'] = alpha * parent1['mu'] + (1 - alpha) * parent2['mu']
    child['sigma'] = alpha * parent1['sigma'] + (1 - alpha) * parent2['sigma']
    child['w_conv'] = alpha * parent1['w_conv'] + (1 - alpha) * parent2['w_conv']
    child['w_gnn'] = alpha * parent1['w_gnn'] + (1 - alpha) * parent2['w_gnn']
    child['gnn_edge_weight'] = alpha * parent1['gnn_edge_weight'] + (1 - alpha) * parent2['gnn_edge_weight']
    
    # Normalize fusion weights
    total = child['w_conv'] + child['w_gnn']
    child['w_conv'] /= total
    child['w_gnn'] /= total
    
    child['fitness'] = 0.0
    child['metrics'] = {}
    
    return child

def run_evolution():
    """Run evolutionary algorithm."""
    print("=" * 60)
    print("EVOLUTIONARY LENIA V10 - HYBRID CONV+GNN")
    print("=" * 60)
    print(f"\nConfig: {CONFIG['generations']} generations, {CONFIG['population_size']} individuals")
    print(f"Warm-start: mu={CONFIG['init_mu']}, sigma={CONFIG['init_sigma']}")
    print(f"Grid: {CONFIG['grid_size']}x{CONFIG['grid_size']} fine, {CONFIG['coarse_size']}x{CONFIG['coarse_size']} coarse")
    print()
    
    # Initialize population
    population = []
    
    # First individual is warm-start from V9
    population.append(create_individual(
        mu=CONFIG['init_mu'],
        sigma=CONFIG['init_sigma'],
        w_conv=0.6,
        w_gnn=0.4
    ))
    
    # Random individuals
    for _ in range(CONFIG['population_size'] - 1):
        population.append(create_individual())
    
    results = {
        'config': CONFIG,
        'generations': [],
        'best_individual': None,
        'final_stats': {}
    }
    
    best_fitness = 0
    best_individual = None
    
    for gen in range(CONFIG['generations']):
        print(f"Generation {gen + 1}/{CONFIG['generations']}")
        
        # Evaluate all individuals
        for i, ind in enumerate(population):
            population[i] = evaluate_individual(ind)
        
        # Sort by fitness
        population.sort(key=lambda x: x['fitness'], reverse=True)
        
        # Track best
        if population[0]['fitness'] > best_fitness:
            best_fitness = population[0]['fitness']
            best_individual = population[0].copy()
        
        # Calculate generation stats
        fitnesses = [ind['fitness'] for ind in population]
        survivals = [ind['metrics']['survival'] for ind in population]
        complexities = [ind['metrics']['complexity'] for ind in population]
        stabilities = [ind['metrics']['stability'] for ind in population]
        
        gen_stats = {
            'generation': gen + 1,
            'best_fitness': float(max(fitnesses)),
            'mean_fitness': float(np.mean(fitnesses)),
            'survival_rate': float(np.mean(survivals)),
            'mean_complexity': float(np.mean(complexities)),
            'mean_stability': float(np.mean(stabilities)),
            'best_params': population[0].copy()
        }
        gen_stats['best_params'].pop('metrics', None)
        results['generations'].append(gen_stats)
        
        print(f"  Best fitness: {gen_stats['best_fitness']:.4f}")
        print(f"  Survival rate: {gen_stats['survival_rate']*100:.1f}%")
        print(f"  Mean complexity: {gen_stats['mean_complexity']:.4f}")
        print(f"  Mean stability: {gen_stats['mean_stability']:.4f}")
        print(f"  Best params: mu={population[0]['mu']:.3f}, sigma={population[0]['sigma']:.3f}, "
              f"w_conv={population[0]['w_conv']:.3f}, w_gnn={population[0]['w_gnn']:.3f}")
        
        # Selection and reproduction
        if gen < CONFIG['generations'] - 1:
            # Keep top 2
            new_population = [population[0], population[1]]
            
            # Create children
            while len(new_population) < CONFIG['population_size']:
                # Tournament selection
                idx1 = np.random.randint(0, 3)
                idx2 = np.random.randint(0, 3)
                parent1 = population[min(idx1, idx2)]
                
                idx1 = np.random.randint(0, 3)
                idx2 = np.random.randint(0, 3)
                parent2 = population[min(idx1, idx2)]
                
                child = crossover(parent1, parent2)
                child = mutate(child)
                new_population.append(child)
            
            population = new_population
    
    # Final results
    results['best_individual'] = best_individual
    results['final_stats'] = {
        'best_fitness': float(best_fitness),
        'best_mu': float(best_individual['mu']),
        'best_sigma': float(best_individual['sigma']),
        'best_w_conv': float(best_individual['w_conv']),
        'best_w_gnn': float(best_individual['w_gnn']),
        'best_gnn_edge_weight': float(best_individual['gnn_edge_weight']),
        'final_survival_rate': results['generations'][-1]['survival_rate'],
        'final_complexity': results['generations'][-1]['mean_complexity'],
        'target_met': results['generations'][-1]['survival_rate'] >= 0.9
    }
    
    # Save results
    os.makedirs(os.path.dirname(CONFIG['output_path']), exist_ok=True)
    with open(CONFIG['output_path'], 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"\nBest fitness: {results['final_stats']['best_fitness']:.4f}")
    print(f"Best parameters:")
    print(f"  mu: {results['final_stats']['best_mu']:.4f}")
    print(f"  sigma: {results['final_stats']['best_sigma']:.4f}")
    print(f"  w_conv: {results['final_stats']['best_w_conv']:.4f}")
    print(f"  w_gnn: {results['final_stats']['best_w_gnn']:.4f}")
    print(f"  gnn_edge_weight: {results['final_stats']['best_gnn_edge_weight']:.4f}")
    print(f"\nFinal survival rate: {results['final_stats']['final_survival_rate']*100:.1f}%")
    print(f"Final complexity: {results['final_stats']['final_complexity']:.4f}")
    target_status = "ACHIEVED" if results['final_stats']['target_met'] else "NOT MET"
    print(f"\nTarget (>90% survival): {target_status}")
    print(f"\nResults saved to: {CONFIG['output_path']}")
    
    return results

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    results = run_evolution()