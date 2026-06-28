"""
Evolutionary Lenia with Hybrid Fitness (V3)
Combines stability-focused (V1) and emergence-focused (V2) fitness approaches

Based on yuca library (https://github.com/riveSunder/yuca)
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from yuca.ca.continuous import CCA
from yuca.lenia import Lenia
from yuca.utils import query_kwargs, seed_all
from yuca.activations import Gaussian, DoubleGaussian
import time
import os

class HybridFitnessWrapper(nn.Module):
    """
    Hybrid fitness combining:
    - V1: Stability (survival + homeostasis)
    - V2: Emergence (temporal dynamics + spatial complexity)
    
    Uses Pareto front tracking for multi-objective optimization
    """
    
    def __init__(self, **kwargs):
        super(HybridFitnessWrapper, self).__init__()
        
        ca_fn = query_kwargs("ca_fn", Lenia, **kwargs)
        self.ca = ca_fn(**kwargs)
        
        self.ca_steps = query_kwargs("ca_steps", 512, **kwargs)
        self.batch_size = query_kwargs("batch_size", 4, **kwargs)
        self.dim = query_kwargs("dim", 64, **kwargs)
        
        # Fitness weights
        self.stability_weight = query_kwargs("stability_weight", 0.5, **kwargs)
        self.emergence_weight = query_kwargs("emergence_weight", 0.5, **kwargs)
        
        # V1 parameters
        self.alive_threshold = 0.0001
        
        # V2 parameters
        self.dynamics_threshold = 0.001
        
        self.my_device = query_kwargs("device", "cpu", **kwargs)
        self.action_space = self.ActionSpace(shape=self.ca.get_params().shape)
        
    class ActionSpace:
        def __init__(self, shape=(2,)):
            self.shape = shape
        def sample(self):
            return np.random.rand(*self.shape)
    
    def reset(self):
        pass
    
    def eval(self):
        self.ca.eval()
    
    def train(self):
        pass
    
    def compute_stability_fitness(self, grid, initial_mean):
        """V1: Stability-focused fitness"""
        # Survival component
        alive = (grid.mean(dim=(2,3)) > self.alive_threshold).float()
        survival = alive.mean()
        
        # Homeostasis component (penalize growth/decay)
        current_mean = grid.mean()
        homeostasis = 1.0 - torch.abs(1.0 - current_mean / (initial_mean + 1e-6))
        homeostasis = torch.clamp(homeostasis, 0, 1)
        
        # Stability entropy (reward structured patterns)
        grid_normalized = grid / (grid.max() + 1e-6)
        entropy = -torch.sum(grid_normalized * torch.log2(grid_normalized + 1e-6))
        entropy_bonus = torch.clamp(entropy / (self.dim * self.dim), 0, 1)
        
        stability = survival * (0.7 + 0.3 * homeostasis) * (1 + 0.1 * entropy_bonus)
        return stability.item()
    
    def compute_emergence_fitness(self, grid_history, dgrid):
        """V2: Emergence-focused fitness"""
        # Temporal dynamics (reward changing patterns)
        temporal_change = dgrid.mean()
        dynamics_score = torch.clamp(temporal_change * 10, 0, 1)
        
        # Spatial complexity (reward non-uniform patterns)
        spatial_std = grid_history[-1].std()
        complexity = torch.clamp(spatial_std * 5, 0, 1)
        
        # Novelty (distance from uniform)
        pattern_center = grid_history[-1].mean()
        novelty = torch.abs(grid_history[-1] - pattern_center).mean()
        novelty_score = torch.clamp(novelty * 2, 0, 1)
        
        emergence = dynamics_score * (0.5 + 0.3 * complexity + 0.2 * novelty_score)
        return emergence.item()
    
    def step(self, action):
        """Run simulation and compute hybrid fitness"""
        self.ca.set_params(action)
        self.ca.no_grad()
        
        # Initialize grid with random pattern in corner
        grid = torch.zeros(self.batch_size, self.ca.external_channels, 
                          self.dim, self.dim)
        quarter = self.dim // 4
        grid[:, :, :quarter*2, :quarter*2] = torch.rand(
            self.batch_size, self.ca.external_channels, quarter*2, quarter*2)
        
        initial_mean = grid.mean()
        grid_history = [grid.clone()]
        old_grid = grid.clone()
        
        # Run simulation
        for step in range(self.ca_steps):
            grid = self.ca(grid)
            
            if step % 32 == 0:
                grid_history.append(grid.clone())
            
            # Check for death
            if grid.mean() <= 0.0:
                break
        
        # Compute change at end
        dgrid = torch.abs(grid - self.ca(grid.clone()))
        
        # V1: Stability fitness
        stability = self.compute_stability_fitness(grid, initial_mean)
        
        # V2: Emergence fitness
        emergence = self.compute_emergence_fitness(grid_history, dgrid)
        
        # Hybrid fitness (weighted combination)
        hybrid = self.stability_weight * stability + self.emergence_weight * emergence
        
        # Pareto information for multi-objective tracking
        pareto_info = {
            "stability": stability,
            "emergence": emergence,
            "hybrid": hybrid,
            "survival": (grid.mean() > self.alive_threshold).item(),
            "dynamics": dgrid.mean().item(),
            "complexity": grid.std().item()
        }
        
        info = {
            "active_grid": grid.mean().item(),
            "pareto": pareto_info,
            "params": action,
            "ca_steps": self.ca_steps
        }
        
        done = False
        reward = hybrid
        
        return 0, reward, done, info
    
    def to_device(self, device):
        self.ca.to_device(device)
        self.my_device = device
    
    def get_params(self):
        return self.ca.get_params()
    
    def set_params(self, params):
        self.ca.set_params(params)


class SimpleCMAES:
    """Simplified CMA-ES for hybrid fitness optimization"""
    
    def __init__(self, **kwargs):
        self.population_size = query_kwargs("population_size", 16, **kwargs)
        self.elite_keep = self.population_size // 4
        self.generations = query_kwargs("generations", 10, **kwargs)
        self.replicates = query_kwargs("replicates", 2, **kwargs)
        
        env_fn = query_kwargs("env_fn", HybridFitnessWrapper, **kwargs)
        self.env = env_fn(**kwargs)
        
        # Initialize distribution
        ca_params = self.env.ca.get_params()
        self.dim = ca_params.shape[0]
        self.starting_means = ca_params
        self.starting_covar = np.abs(np.diag(np.ones(self.dim) * 0.1))
        
        self.pareto_front = []  # Track Pareto-optimal solutions
        
        print(f"CMA-ES initialized: {self.population_size} pop, {self.generations} gen, {self.dim} dims")
    
    def reset(self):
        self.means = 1.0 * self.starting_means
        self.covar = 1.0 * self.starting_covar
        self.pareto_front = []
    
    def sample_distribution(self):
        return np.random.multivariate_normal(self.means, self.covar)
    
    def get_fitness(self, params, seed=13):
        """Evaluate fitness with replicates"""
        seed_all(seed)
        fitness_list = []
        pareto_list = []
        
        for rep in range(self.replicates):
            self.env.reset()
            _, reward, _, info = self.env.step(params)
            fitness_list.append(reward)
            pareto_list.append(info["pareto"])
        
        # Return mean fitness and Pareto info
        return np.mean(fitness_list), pareto_list[0]
    
    def update_pareto_front(self, pareto_info, params):
        """Update Pareto front with new solution"""
        stability = pareto_info["stability"]
        emergence = pareto_info["emergence"]
        
        # Check if this solution dominates any existing ones
        is_dominated = False
        to_remove = []
        
        for i, (s, e, p) in enumerate(self.pareto_front):
            # Check dominance
            if s >= stability and e >= emergence:
                if s > stability or e > emergence:
                    is_dominated = True
                    break
            elif stability >= s and emergence >= e:
                if stability > s or emergence > e:
                    to_remove.append(i)
        
        # Remove dominated solutions
        for i in to_remove:
            self.pareto_front.pop(i)
        
        # Add if not dominated
        if not is_dominated:
            self.pareto_front.append((stability, emergence, params.copy()))
    
    def update_population(self, fitness_list, pareto_list, params_list):
        """Update distribution based on fitness"""
        # Sort by fitness
        sorted_indices = np.argsort(fitness_list)[::-1]
        
        # Get elite
        elite_params = np.array([params_list[i] for i in sorted_indices[:self.elite_keep]])
        elite_fitness = np.array([fitness_list[i] for i in sorted_indices[:self.elite_keep]])
        
        # Update Pareto front
        for i in sorted_indices[:self.elite_keep]:
            self.update_pareto_front(pareto_list[i], params_list[i])
        
        # Update distribution
        self.means = elite_params.mean(axis=0)
        centered = elite_params - self.means
        self.covar = (1 / self.elite_keep) * np.matmul(centered.T, centered)
        
        return elite_params, elite_fitness
    
    def search(self):
        """Run evolutionary search"""
        print("Starting hybrid fitness evolution...")
        
        results = {
            "fitness_history": [],
            "pareto_front": [],
            "best_params": None,
            "best_fitness": 0
        }
        
        self.reset()
        
        for gen in range(self.generations):
            # Sample population
            params_list = []
            for i in range(self.population_size):
                if i < self.elite_keep and gen > 0:
                    params_list.append(self.elite_params[i])
                else:
                    params_list.append(self.sample_distribution())
            
            # Evaluate fitness
            fitness_list = []
            pareto_list = []
            for params in params_list:
                fit, pareto = self.get_fitness(params, seed=gen)
                fitness_list.append(fit)
                pareto_list.append(pareto)
            
            # Update distribution
            self.elite_params, elite_fitness = self.update_population(
                fitness_list, pareto_list, params_list)
            
            # Log progress
            mean_fit = np.mean(fitness_list)
            max_fit = np.max(fitness_list)
            min_fit = np.min(fitness_list)
            
            results["fitness_history"].append({
                "gen": gen,
                "mean": mean_fit,
                "max": max_fit,
                "min": min_fit,
                "pareto_size": len(self.pareto_front)
            })
            
            print(f"Gen {gen}: fit mean={mean_fit:.4f}, max={max_fit:.4f}, "
                  f"Pareto front size={len(self.pareto_front)}")
            
            # Early stopping if converged
            if np.std(fitness_list) < 0.01 and gen > 4:
                print("Early stopping - fitness converged")
                break
        
        # Save Pareto front
        results["pareto_front"] = [(s, e) for s, e, _ in self.pareto_front]
        
        # Get best solution
        if self.pareto_front:
            # Select best hybrid solution
            best_idx = 0
            best_hybrid = 0
            for i, (s, e, p) in enumerate(self.pareto_front):
                hybrid = self.env.stability_weight * s + self.env.emergence_weight * e
                if hybrid > best_hybrid:
                    best_hybrid = hybrid
                    best_idx = i
            results["best_params"] = self.pareto_front[best_idx][2]
            results["best_fitness"] = best_hybrid
        
        return results


def run_experiment(**kwargs):
    """Run hybrid fitness evolution experiment"""
    
    # Default parameters
    kwargs.setdefault("dim", 64)
    kwargs.setdefault("ca_steps", 256)
    kwargs.setdefault("population_size", 12)
    kwargs.setdefault("generations", 8)
    kwargs.setdefault("batch_size", 4)
    kwargs.setdefault("replicates", 2)
    kwargs.setdefault("device", "cpu")
    
    # Hybrid weights
    kwargs.setdefault("stability_weight", 0.5)
    kwargs.setdefault("emergence_weight", 0.5)
    
    # Initialize and run
    cmaes = SimpleCMAES(**kwargs)
    results = cmaes.search()
    
    # Save results
    timestamp = int(time.time())
    output_path = f"D:/openclaw_workspace/exploration/hybrid_lenia_results_{timestamp}.npy"
    np.save(output_path, results)
    print(f"Results saved to {output_path}")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Evolutionary Lenia Hybrid Fitness")
    parser.add_argument("--dim", type=int, default=64)
    parser.add_argument("--ca_steps", type=int, default=256)
    parser.add_argument("--population_size", type=int, default=12)
    parser.add_argument("--generations", type=int, default=8)
    parser.add_argument("--stability_weight", type=float, default=0.5)
    parser.add_argument("--emergence_weight", type=float, default=0.5)
    parser.add_argument("--device", type=str, default="cpu")
    
    args = parser.parse_args()
    kwargs = dict(args._get_kwargs())
    
    results = run_experiment(**kwargs)
    
    print("\n=== Final Results ===")
    print(f"Best fitness: {results['best_fitness']:.4f}")
    print(f"Pareto front size: {len(results['pareto_front'])}")
    print(f"Pareto front (stability, emergence): {results['pareto_front']}")