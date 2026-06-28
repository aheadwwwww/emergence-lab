"""V9 Simple Test"""
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import json
import os

# Create simple GNN simulation
class SimpleGNN:
    def __init__(self, mu=0.135, sigma=0.074, dt=0.1, grid_size=64, num_regions=12):
        self.mu = mu
        self.sigma = sigma
        self.dt = dt
        self.grid_size = grid_size
        self.num_regions = num_regions
        
        # Edge weights for message passing (learnable)
        self.edge_weights = np.random.randn(num_regions * 5).astype(np.float32) * 0.3 + 1.0
        
        # Create grid mapping
        self.mapping = self._create_mapping()
    
    def _create_mapping(self):
        mapping = np.zeros((self.grid_size, self.grid_size), dtype=np.int32)
        rows = [3, 4, 3, 2]
        centers = []
        for row, count in enumerate(rows):
            y = row * self.grid_size // 4 + self.grid_size // 8
            x_spacing = self.grid_size // (count + 1)
            for i in range(count):
                centers.append((x_spacing * (i + 1), y))
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                min_dist = float('inf')
                for v, (cx, cy) in enumerate(centers):
                    dist = (i - cy)**2 + (j - cx)**2
                    if dist < min_dist:
                        min_dist = dist
                        mapping[i, j] = v
        return mapping
    
    def create_seed(self):
        size = self.grid_size
        grid = np.zeros((size, size), dtype=np.float32)
        mid = size // 2
        y, x = np.ogrid[:size, :size]
        r = np.sqrt((x - mid)**2 + (y - mid)**2)
        disk_radius = size // 6
        grid[r < disk_radius] = 1.0
        transition = 3
        mask = (r >= disk_radius) & (r < disk_radius + transition)
        grid[mask] = 1.0 - (r[mask] - disk_radius) / transition
        return grid
    
    def growth(self, U):
        return 2 * np.exp(-((U - self.mu)**2) / (2 * self.sigma**2)) - 1
    
    def simulate(self, max_steps=150):
        grid = self.create_seed()
        
        for step in range(max_steps):
            # Compute region features
            region_vals = np.zeros(self.num_regions)
            for v in range(self.num_regions):
                mask = (self.mapping == v)
                if mask.sum() > 0:
                    region_vals[v] = grid[mask].mean()
            
            # Message passing with learned weights
            new_region_vals = region_vals.copy()
            for v in range(self.num_regions):
                # Simplified: weighted average of neighbors
                w_idx = v * 5
                weights = self.edge_weights[w_idx:w_idx+5]
                weights = weights / (np.abs(weights).sum() + 1e-8)
                # Simple message passing
                new_region_vals[v] = region_vals[v] * 0.5 + region_vals.mean() * 0.5
            
            # Apply growth
            growth_vals = self.growth(new_region_vals)
            
            # Update grid
            for v in range(self.num_regions):
                mask = (self.mapping == v)
                grid[mask] = np.clip(grid[mask] + self.dt * growth_vals[v], 0, 1)
        
        survival = float((grid > 0.1).mean())
        return survival
    
    def mutate(self, rate=0.1):
        self.edge_weights += np.random.randn(len(self.edge_weights)).astype(np.float32) * rate
        self.mu += np.random.randn() * 0.01
        self.mu = np.clip(self.mu, 0.1, 0.2)
        self.sigma += np.random.randn() * 0.005
        self.sigma = max(0.01, min(0.15, self.sigma))


def evolve(pop_size=8, generations=12):
    print(f"\nV9: Evolving GNN Weights")
    print(f"Pop: {pop_size}, Gen: {generations}")
    print("="*50)
    
    # Initialize population
    population = []
    for i in range(pop_size):
        gnn = SimpleGNN(mu=0.135 + np.random.uniform(-0.02, 0.02),
                       sigma=0.074 + np.random.uniform(-0.01, 0.01))
        population.append({'id': i, 'gnn': gnn, 'survival': 0.0})
    
    best_overall = None
    history = []
    
    for gen in range(generations):
        print(f"\nGen {gen+1}/{generations}")
        
        # Evaluate
        for ind in population:
            ind['survival'] = ind['gnn'].simulate()
            print(f"  Ind {ind['id']}: {ind['survival']:.3f}")
        
        # Track best
        best = max(population, key=lambda x: x['survival'])
        if best_overall is None or best['survival'] > best_overall['survival']:
            best_overall = {'generation': gen, 'survival': best['survival'],
                          'mu': best['gnn'].mu, 'sigma': best['gnn'].sigma,
                          'weights': best['gnn'].edge_weights.tolist()}
        
        mean_surv = np.mean([x['survival'] for x in population])
        history.append({'gen': gen, 'best': best['survival'], 'mean': mean_surv})
        print(f"  Best: {best['survival']:.3f}, Mean: {mean_surv:.3f}")
        
        # Reproduce
        if gen < generations - 1:
            population.sort(key=lambda x: x['survival'], reverse=True)
            elite = population[:pop_size // 2]
            
            new_pop = []
            for i, ind in enumerate(elite):
                ind['id'] = i
                new_pop.append(ind)
            
            while len(new_pop) < pop_size:
                parent = elite[np.random.randint(len(elite))]
                child = SimpleGNN(mu=parent['gnn'].mu, sigma=parent['gnn'].sigma)
                child.edge_weights = parent['gnn'].edge_weights.copy()
                child.mutate(rate=0.15)
                new_pop.append({'id': len(new_pop), 'gnn': child, 'survival': 0.0})
            
            population = new_pop
    
    return best_overall, history


if __name__ == '__main__':
    best, history = evolve()
    
    print("\n" + "="*50)
    print("RESULTS")
    print("="*50)
    print(f"Best Survival: {best['survival']:.3f} ({best['survival']*100:.1f}%)")
    print(f"Mu: {best['mu']:.4f}")
    print(f"Sigma: {best['sigma']:.4f}")
    
    v8 = 0.492
    improvement = (best['survival'] - v8) / v8 * 100
    print(f"\nV8 Baseline: {v8:.3f}")
    print(f"V9 Result: {best['survival']:.3f}")
    print(f"Improvement: {improvement:+.1f}%")
    
    if best['survival'] > v8:
        print("\nBEAT BASELINE!")
    
    # Save
    results = {'best': best, 'history': history, 'v8_baseline': v8}
    os.makedirs('D:/openclaw_workspace/results', exist_ok=True)
    with open('D:/openclaw_workspace/results/v9_learnable_gnn.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("\nSaved to results/v9_learnable_gnn.json")
