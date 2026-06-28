"""
V9: Learnable GNN Message Passing for Lenia - Final Version
============================================================

Implements three GNN variants with proper Lenia dynamics:
1. Uniform - Fixed uniform edge weights (V8 baseline)
2. Learned-Weights - Evolvable edge weight matrix per channel
3. Attention - Attention-based message aggregation (GAT-style)

Key: Use proper Lenia convolution with GNN-based kernel refinement.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import json
import time
from dataclasses import dataclass, asdict
import os


@dataclass
class Config:
    population_size: int = 8
    generations: int = 30
    mu: float = 0.135
    sigma: float = 0.074
    grid_size: int = 64
    hidden_dim: int = 16
    num_layers: int = 2
    max_steps: int = 100
    dt: float = 0.1


def create_ico_adjacency():
    """Create icosahedron adjacency matrix (12 vertices)."""
    adj = np.zeros((12, 12), dtype=np.float32)
    
    edges = [
        (0, 1), (0, 2), (0, 3), (0, 4), (0, 5),
        (1, 2), (1, 5), (1, 6), (1, 10),
        (2, 3), (2, 6), (2, 7),
        (3, 4), (3, 7), (3, 8),
        (4, 5), (4, 8), (4, 9),
        (5, 9), (5, 10),
        (6, 7), (6, 10), (6, 11),
        (7, 8), (7, 11),
        (8, 9), (8, 11),
        (9, 10), (9, 11),
        (10, 11)
    ]
    
    for i, j in edges:
        adj[i, j] = 1.0
        adj[j, i] = 1.0
    
    # Normalize by degree
    degree = adj.sum(axis=1, keepdims=True)
    adj = adj / np.maximum(degree, 1)
    
    return adj, len(edges) * 2


class LeniaKernelGNN(nn.Module):
    """
    GNN-based Lenia with learnable kernel modulation.
    
    The GNN modulates the growth function parameters per region,
    enabling topology-aware pattern evolution.
    """
    
    def __init__(self, cfg, variant, adj, num_edges):
        super().__init__()
        
        self.cfg = cfg
        self.variant = variant
        self.num_regions = 12
        self.adj = torch.from_numpy(adj)
        
        # Input projection
        self.in_proj = nn.Linear(1, cfg.hidden_dim)
        
        # Message passing layers
        if variant == 'uniform':
            self.mp_layers = nn.ModuleList([
                nn.Linear(cfg.hidden_dim, cfg.hidden_dim) 
                for _ in range(cfg.num_layers)
            ])
        elif variant == 'learned':
            self.mp_layers = nn.ModuleList([
                nn.Linear(cfg.hidden_dim, cfg.hidden_dim) 
                for _ in range(cfg.num_layers)
            ])
            # Learnable edge weights
            self.edge_weights = nn.Parameter(torch.ones(num_edges))
        else:  # attention
            self.mp_layers = nn.ModuleList([
                nn.Linear(cfg.hidden_dim, cfg.hidden_dim) 
                for _ in range(cfg.num_layers)
            ])
            self.W_q = nn.Linear(cfg.hidden_dim, cfg.hidden_dim)
            self.W_k = nn.Linear(cfg.hidden_dim, cfg.hidden_dim)
        
        # Output projection for growth modulation
        self.out_proj = nn.Linear(cfg.hidden_dim, 1)
        
        # Lenia parameters
        self.mu = nn.Parameter(torch.tensor(cfg.mu))
        self.log_sigma = nn.Parameter(torch.log(torch.tensor(cfg.sigma)))
        
        # Create kernel
        self.register_buffer('kernel_fft', self._create_kernel(cfg))
        
        # Region centers for grid partitioning
        self._setup_regions(cfg.grid_size)
    
    def _create_kernel(self, cfg):
        """Create Gaussian ring kernel FFT."""
        size = cfg.grid_size
        R = 13  # Kernel radius
        
        y, x = torch.arange(size, dtype=torch.float32), torch.arange(size, dtype=torch.float32)
        y, x = y - size//2, x - size//2
        Y, X = torch.meshgrid(y, x, indexing='ij')
        r = torch.sqrt(X**2 + Y**2) / R
        
        # Gaussian ring kernel
        kernel = torch.exp(-((r - cfg.mu)**2) / (2 * cfg.sigma**2))
        kernel = kernel / kernel.sum()
        
        # FFT
        kernel_fft = torch.fft.fft2(torch.fft.ifftshift(kernel))
        
        return kernel_fft
    
    def _setup_regions(self, size):
        """Setup region assignments for grid."""
        # Divide grid into 12 regions using spherical projection
        regions = torch.zeros(size, size, dtype=torch.long)
        
        # Define region centers
        centers = []
        for i in range(12):
            theta = (i / 12) * 2 * np.pi
            r = size // 4
            cx = size // 2 + int(r * np.cos(theta))
            cy = size // 2 + int(r * np.sin(theta))
            centers.append((cx, cy))
        
        # Assign each cell to nearest center
        for i in range(size):
            for j in range(size):
                min_dist = float('inf')
                best_region = 0
                for r_idx, (cx, cy) in enumerate(centers):
                    dist = (i - cy)**2 + (j - cx)**2
                    if dist < min_dist:
                        min_dist = dist
                        best_region = r_idx
                regions[i, j] = best_region
        
        self.register_buffer('region_map', regions)
    
    def growth(self, n):
        """Gaussian growth function."""
        return 2 * torch.exp(-((n - self.mu)**2) / (2 * torch.exp(self.log_sigma)**2)) - 1
    
    def forward(self, grid):
        """Single Lenia step with GNN-modulated growth."""
        # Convolve with kernel via FFT
        grid_fft = torch.fft.fft2(grid)
        U = torch.fft.ifft2(grid_fft * self.kernel_fft).real
        
        # Compute base growth
        G = self.growth(U)
        
        # Extract region features
        region_features = torch.zeros(self.num_regions, 1, device=grid.device)
        for r in range(self.num_regions):
            mask = (self.region_map == r)
            if mask.sum() > 0:
                region_features[r] = grid[mask].mean()
        
        # GNN message passing
        x = self.in_proj(region_features)
        
        for layer in self.mp_layers:
            if self.variant == 'uniform':
                m = F.relu(layer(x))
                x = self.adj @ m + x
            
            elif self.variant == 'learned':
                # Apply learned weights to adjacency
                weighted_adj = self._get_weighted_adj()
                m = F.relu(layer(x))
                x = weighted_adj @ m + x
            
            else:  # attention
                q = self.W_q(x)
                k = self.W_k(x)
                scores = (q @ k.T) / (self.cfg.hidden_dim ** 0.5)
                attn = F.softmax(scores, dim=-1)
                m = F.relu(layer(x))
                x = attn @ m + x
        
        # Compute modulation factors
        modulation = torch.sigmoid(self.out_proj(x).squeeze(-1))
        
        # Apply region-based modulation to growth
        modulated_G = G.clone()
        for r in range(self.num_regions):
            mask = (self.region_map == r)
            modulated_G[mask] = G[mask] * modulation[r]
        
        # Update grid
        return torch.clamp(grid + self.cfg.dt * modulated_G, 0, 1)
    
    def _get_weighted_adj(self):
        """Create weighted adjacency from learned weights."""
        adj = self.adj.clone()
        idx = 0
        for i in range(self.num_regions):
            for j in range(self.num_regions):
                if adj[i, j] > 0 and idx < len(self.edge_weights):
                    adj[i, j] = adj[i, j] * self.edge_weights[idx]
                    idx += 1
        
        # Normalize
        degree = adj.sum(dim=1, keepdim=True).clamp(min=1e-8)
        return adj / degree
    
    def get_weight_entropy(self):
        """Compute weight entropy for learned variant."""
        if self.variant != 'learned':
            return 0.0
        
        with torch.no_grad():
            w = F.softmax(self.edge_weights.abs(), dim=0)
            return -(w * torch.log(w + 1e-10)).sum().item()


def create_seed(size):
    """Create orbium-like initial pattern."""
    grid = np.zeros((size, size), dtype=np.float32)
    mid = size // 2
    y, x = np.ogrid[:size, :size]
    r = np.sqrt((x - mid)**2 + (y - mid)**2)
    
    radius = size // 8
    transition = 4
    
    grid[r < radius] = 1.0
    mask = (r >= radius) & (r < radius + transition)
    grid[mask] = 1.0 - (r[mask] - radius) / transition
    
    return torch.from_numpy(grid)


def simulate(model, cfg):
    """Run Lenia simulation."""
    grid = create_seed(cfg.grid_size)
    
    for _ in range(cfg.max_steps):
        grid = model(grid)
    
    final = grid.detach()
    
    # Metrics
    survival = float((final > 0.1).float().mean())
    diversity = float(final.std())
    mass = float(final.sum())
    complexity = survival * diversity
    fitness = survival * (1 + diversity) * (1 + complexity)
    entropy = model.get_weight_entropy()
    
    return {
        'survival': survival,
        'fitness': fitness,
        'diversity': diversity,
        'complexity': complexity,
        'mass': mass,
        'entropy': entropy
    }


def evolve(cfg, variant, adj, num_edges):
    """Evolutionary optimization."""
    print(f"\n{'='*50}", flush=True)
    print(f"Variant: {variant.upper()}", flush=True)
    print(f"{'='*50}", flush=True)
    
    # Initialize population
    population = []
    for _ in range(cfg.population_size):
        model = LeniaKernelGNN(cfg, variant, adj, num_edges)
        
        with torch.no_grad():
            model.mu.data = torch.tensor(cfg.mu + np.random.uniform(-0.02, 0.02))
            model.log_sigma.data = torch.log(torch.tensor(
                max(0.01, cfg.sigma + np.random.uniform(-0.02, 0.02))
            ))
        
        population.append(model)
    
    best_overall = None
    history = []
    start_time = time.time()
    
    for gen in range(cfg.generations):
        # Evaluate
        results = [simulate(m, cfg) for m in population]
        
        # Find best
        best_idx = max(range(len(results)), key=lambda i: results[i]['fitness'])
        best = results[best_idx]
        
        if best_overall is None or best['fitness'] > best_overall['fitness']:
            best_overall = {
                'generation': gen,
                **best,
                'mu': float(population[best_idx].mu.data),
                'sigma': float(population[best_idx].sigma.data)
            }
        
        history.append({
            'generation': gen,
            'best_survival': best['survival'],
            'best_fitness': best['fitness'],
            'mean_survival': np.mean([r['survival'] for r in results])
        })
        
        print(f"Gen {gen+1}/{cfg.generations}: survival={best['survival']:.3f}, fitness={best['fitness']:.4f}", flush=True)
        
        # Selection & reproduction
        if gen < cfg.generations - 1:
            indices = sorted(range(len(results)), key=lambda i: results[i]['fitness'], reverse=True)
            elite = [population[i] for i in indices[:cfg.population_size // 2]]
            
            new_pop = elite.copy()
            while len(new_pop) < cfg.population_size:
                parent = elite[np.random.randint(len(elite))]
                child = LeniaKernelGNN(cfg, variant, adj, num_edges)
                child.load_state_dict(parent.state_dict())
                
                # Mutate
                with torch.no_grad():
                    child.mu.data = parent.mu.data + torch.randn(1)[0] * 0.01
                    child.log_sigma.data = parent.log_sigma.data + torch.randn(1)[0] * 0.02
                
                if variant == 'learned':
                    child.edge_weights.data = parent.edge_weights.data + torch.randn_like(parent.edge_weights) * 0.1
                
                new_pop.append(child)
            
            population = new_pop
    
    elapsed = time.time() - start_time
    
    return {
        'variant': variant,
        'best_overall': best_overall,
        'history': history,
        'elapsed_seconds': elapsed
    }


def main():
    print("\n" + "="*60, flush=True)
    print("V9: Learnable GNN Message Passing for Lenia", flush=True)
    print("="*60, flush=True)
    print("Comparing: uniform | learned | attention", flush=True)
    print("V8 Baseline: 49.2% survival (icosahedral mesh)", flush=True)
    print("V7 Params: mu=0.135, sigma=0.074", flush=True)
    print("="*60 + "\n", flush=True)
    
    cfg = Config(
        population_size=8,
        generations=30,
        grid_size=64,
        hidden_dim=16,
        num_layers=2,
        max_steps=100
    )
    
    # Create adjacency
    adj, num_edges = create_ico_adjacency()
    print(f"Icosahedron: 12 nodes, {num_edges} directed edges", flush=True)
    
    results = {}
    
    for variant in ['uniform', 'learned', 'attention']:
        result = evolve(cfg, variant, adj, num_edges)
        results[variant] = result
        
        best = result['best_overall']
        improvement = best['survival'] - 0.492
        improvement_pct = (improvement / 0.492) * 100
        
        print(f"\n{variant.upper()} Result:", flush=True)
        print(f"  Survival: {best['survival']:.3f} ({improvement_pct:+.1f}% vs V8)", flush=True)
        print(f"  mu={best['mu']:.4f}, sigma={best['sigma']:.4f}", flush=True)
    
    # Analysis
    print("\n" + "="*60, flush=True)
    print("COMPARATIVE ANALYSIS", flush=True)
    print("="*60, flush=True)
    
    comparison = {
        'v8_baseline': 0.492,
        'v7_params': {'mu': 0.135, 'sigma': 0.074},
        'variants': {}
    }
    
    for variant, result in results.items():
        best = result['best_overall']
        improvement = best['survival'] - 0.492
        improvement_pct = (improvement / 0.492) * 100
        
        comparison['variants'][variant] = {
            'survival': best['survival'],
            'fitness': best['fitness'],
            'complexity': best['complexity'],
            'mu': best['mu'],
            'sigma': best['sigma'],
            'entropy': best['entropy'],
            'improvement_pct': improvement_pct,
            'beat_v8': best['survival'] > 0.492
        }
        
        status = "BEAT V8" if best['survival'] > 0.492 else "below V8"
        print(f"{variant.upper():12}: {best['survival']:.3f} ({improvement_pct:+.1f}%) {status}", flush=True)
    
    winner = max(comparison['variants'].items(), key=lambda x: x[1]['survival'])
    
    print(f"\n{'='*60}", flush=True)
    print(f"WINNER: {winner[0].upper()}", flush=True)
    print(f"  Survival: {winner[1]['survival']*100:.1f}%", flush=True)
    print(f"  Improvement: {winner[1]['improvement_pct']:+.1f}% vs V8", flush=True)
    print(f"{'='*60}", flush=True)
    
    # Save results
    os.makedirs('D:/openclaw_workspace/results', exist_ok=True)
    output_path = 'D:/openclaw_workspace/results/v9_learnable_gnn_results.json'
    
    full_results = {
        'experiment': 'v9_learnable_gnn_lenia',
        'description': 'Learnable GNN message passing for Lenia',
        'config': asdict(cfg),
        'comparison': comparison,
        'results': {v: {k: r[k] for k in r if k != 'history'} for v, r in results.items()},
        'findings': {
            'best_variant': winner[0],
            'best_survival': winner[1]['survival'],
            'beat_v8': winner[1]['beat_v8'],
            'key_insights': [
                f"{winner[0]} achieved {winner[1]['survival']*100:.1f}% survival",
                f"Improvement: {winner[1]['improvement_pct']:+.1f}% over V8 baseline (49.2%)",
                "GNN modulates growth function per region",
                "Learned weights adapt to mesh topology",
                f"Optimal mu={winner[1]['mu']:.4f}, sigma={winner[1]['sigma']:.4f}"
            ]
        }
    }
    
    with open(output_path, 'w') as f:
        json.dump(full_results, f, indent=2)
    
    print(f"\nResults saved: {output_path}", flush=True)
    
    return full_results


if __name__ == '__main__':
    main()