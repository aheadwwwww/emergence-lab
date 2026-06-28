"""
Lenia Kernel-Growth Parameter Co-evolution (V7)
Learns optimal kernel shape + growth parameter combinations based on official species data

Key insight from official Lenia: Growth parameters (mu, sigma) vary systematically:
- Orbium: μ=0.15, σ=0.015
- Gyrorbium: μ=0.156, σ=0.0224
- Scutium: μ=0.29, σ=0.045
- Hydrogeminium: μ=0.26, σ=0.036

This suggests kernel shape and growth params are coupled.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy.ndimage import gaussian_filter
import time
import os
import json
from typing import Dict, List, Tuple, Optional

# Try to import yuca, fall back to simple implementation
try:
    from yuca.ca.continuous import CCA
    from yuca.lenia import Lenia
    from yuca.utils import query_kwargs, seed_all
    YUCA_AVAILABLE = True
except ImportError:
    YUCA_AVAILABLE = False
    print("yuca not available, using simple implementation")


# Official Lenia species growth parameters for reference
SPECIES_PARAMS = {
    "orbium": {"mu": 0.15, "sigma": 0.015, "R": 13, "kernel": "bump4"},
    "gyrorbium": {"mu": 0.156, "sigma": 0.0224, "R": 13, "kernel": "bump4"},
    "scutium": {"mu": 0.29, "sigma": 0.045, "R": 13, "kernel": "bump4"},
    "hydrogeminium": {"mu": 0.26, "sigma": 0.036, "R": 13, "kernel": "bump4"},
    "parorbium": {"mu": 0.184, "sigma": 0.025, "R": 13, "kernel": "bump4"},
    "discutium": {"mu": 0.356, "sigma": 0.063, "R": 13, "kernel": "bump4"},
}


def kernel_core_bump4(r: np.ndarray) -> np.ndarray:
    """Exponential/gaussian bump kernel (most common in official Lenia)"""
    result = np.zeros_like(r)
    mask = (r > 0) & (r < 1)
    result[mask] = np.exp(4 - 1 / (r[mask] * (1 - r[mask])))
    return result


def kernel_core_polynomial(r: np.ndarray) -> np.ndarray:
    """Polynomial kernel (quad4)"""
    return (4 * r * (1 - r)) ** 4


def growth_gaussian(n: np.ndarray, mu: float, sigma: float) -> np.ndarray:
    """Gaussian growth function"""
    return np.exp(-((n - mu) ** 2) / (2 * sigma ** 2)) * 2 - 1


def growth_polynomial(n: np.ndarray, mu: float, sigma: float) -> np.ndarray:
    """Polynomial growth function"""
    return np.maximum(0, 1 - (n - mu) ** 2 / (9 * sigma ** 2)) ** 4 * 2 - 1


class SimpleLenia:
    """Simple Lenia implementation for when yuca is not available"""
    
    def __init__(self, R: int = 13, mu: float = 0.15, sigma: float = 0.015,
                 dim: int = 64, kernel_type: str = "bump4"):
        self.R = R
        self.mu = mu
        self.sigma = sigma
        self.dim = dim
        self.kernel_type = kernel_type
        
        # Pre-compute kernel
        self.kernel = self._create_kernel()
        self.kernel_fft = np.fft.fft2(self.kernel)
        
    def _create_kernel(self) -> np.ndarray:
        """Create ring-shaped kernel"""
        x = np.linspace(-self.R, self.R, self.dim)
        y = np.linspace(-self.R, self.R, self.dim)
        X, Y = np.meshgrid(x, y)
        D = np.sqrt(X**2 + Y**2) / self.R
        
        # Use bump4 kernel
        if self.kernel_type == "bump4":
            core = kernel_core_bump4(D)
        else:
            core = kernel_core_polynomial(D)
        
        # Normalize
        kernel_sum = core.sum()
        if kernel_sum > 0:
            core = core / kernel_sum
            
        return core
    
    def step(self, grid: np.ndarray) -> np.ndarray:
        """Single Lenia step"""
        # Convolve with kernel (FFT)
        grid_fft = np.fft.fft2(grid)
        potential = np.real(np.fft.ifft2(self.kernel_fft * grid_fft))
        
        # Apply growth function
        growth = growth_gaussian(potential, self.mu, self.sigma)
        
        # Update
        new_grid = np.clip(grid + 1/10 * growth, 0, 1)
        
        return new_grid


class KernelGrowthEvolver:
    """
    Co-evolves kernel shape parameters and growth parameters (mu, sigma)
    
    Genome structure:
    - kernel_params: [k1, k2, k3, k4] - multi-ring kernel coefficients
    - growth_params: [mu, sigma] - growth function parameters
    
    Total: 6 parameters
    """
    
    def __init__(self, dim: int = 64, steps: int = 256, population_size: int = 20,
                 generations: int = 15, device: str = "cpu"):
        self.dim = dim
        self.steps = steps
        self.population_size = population_size
        self.generations = generations
        self.device = device
        
        # Parameter bounds
        self.bounds = {
            "mu": (0.1, 0.4),        # Growth center
            "sigma": (0.01, 0.08),   # Growth width
            "k": (0.0, 1.0),         # Kernel ring coefficients
        }
        
        # Species-inspired starting points
        self.starting_points = list(SPECIES_PARAMS.values())
        
        # Pareto front for multi-objective
        self.pareto_front: List[Dict] = []
        
        print(f"KernelGrowthEvolver initialized: {population_size} pop, {generations} gen")
        
    def create_kernel(self, params: Dict) -> np.ndarray:
        """Create multi-ring kernel from parameters"""
        x = np.linspace(-1, 1, self.dim)
        y = np.linspace(-1, 1, self.dim)
        X, Y = np.meshgrid(x, y)
        D = np.sqrt(X**2 + Y**2)
        
        kernel = np.zeros((self.dim, self.dim))
        
        # Multi-ring kernel: 4 concentric rings
        k_params = params.get("kernel_coeffs", [0.5, 0.5, 0.5, 0.5])
        
        for i, k in enumerate(k_params):
            r_inner = i / 4
            r_outer = (i + 1) / 4
            ring_mask = (D >= r_inner) & (D < r_outer)
            kernel[ring_mask] = kernel_core_bump4((D[ring_mask] - r_inner) / (r_outer - r_inner)) * k
        
        # Normalize
        kernel_sum = kernel.sum()
        if kernel_sum > 0:
            kernel = kernel / kernel_sum
            
        return kernel
    
    def run_simulation(self, kernel: np.ndarray, mu: float, sigma: float,
                       seed: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """Run Lenia simulation with given parameters"""
        grid = seed.copy()
        kernel_fft = np.fft.fft2(kernel)
        
        history = [grid.copy()]
        alive_steps = 0
        
        for step in range(self.steps):
            # FFT convolution
            grid_fft = np.fft.fft2(grid)
            potential = np.real(np.fft.ifft2(kernel_fft * grid_fft))
            
            # Growth function
            growth = growth_gaussian(potential, mu, sigma)
            
            # Update with dt = 1/10
            grid = np.clip(grid + 0.1 * growth, 0, 1)
            
            # Track alive
            if grid.mean() > 0.001:
                alive_steps += 1
                
            if step % 32 == 0:
                history.append(grid.copy())
                
            # Early termination if dead
            if grid.mean() < 0.0001:
                break
                
        return grid, {
            "history": history,
            "alive_steps": alive_steps,
            "final_mass": grid.mean(),
            "final_std": grid.std(),
        }
    
    def compute_fitness(self, params: Dict, seeds: List[np.ndarray]) -> Dict:
        """Compute multi-objective fitness over multiple seeds"""
        kernel = self.create_kernel(params)
        mu = params["mu"]
        sigma = params["sigma"]
        
        results = []
        for seed in seeds:
            final_grid, info = self.run_simulation(kernel, mu, sigma, seed)
            results.append(info)
        
        # Aggregate metrics
        survival_rate = np.mean([r["alive_steps"] for r in results]) / self.steps
        mean_mass = np.mean([r["final_mass"] for r in results])
        mean_std = np.mean([r["final_std"] for r in results])
        
        # Objective 1: Stability (survival + mass retention)
        stability = survival_rate * (mean_mass + 0.1)
        
        # Objective 2: Complexity (pattern structure)
        complexity = mean_std * 5  # Scale up
        
        # Combined fitness (weighted)
        fitness = stability * 0.6 + complexity * 0.4
        
        return {
            "fitness": fitness,
            "stability": stability,
            "complexity": complexity,
            "survival_rate": survival_rate,
            "mean_mass": mean_mass,
            "mean_std": mean_std,
        }
    
    def create_seed(self, seed_type: str = "orbium") -> np.ndarray:
        """Create initial pattern seed"""
        np.random.seed(hash(seed_type) % (2**31))
        
        grid = np.zeros((self.dim, self.dim))
        
        if seed_type == "orbium":
            # Circular blob in corner
            quarter = self.dim // 4
            cx, cy = quarter, quarter
            for i in range(self.dim):
                for j in range(self.dim):
                    d = np.sqrt((i - cx*2)**2 + (j - cy*2)**2)
                    if d < quarter:
                        grid[i, j] = np.exp(-d**2 / (quarter/2)**2)
                        
        elif seed_type == "random":
            # Random noise in corner
            quarter = self.dim // 4
            grid[:quarter*2, :quarter*2] = np.random.rand(quarter*2, quarter*2)
            
        elif seed_type == "perturbed":
            # Orbium with noise
            quarter = self.dim // 4
            cx, cy = quarter, quarter
            for i in range(self.dim):
                for j in range(self.dim):
                    d = np.sqrt((i - cx*2)**2 + (j - cy*2)**2)
                    if d < quarter:
                        grid[i, j] = np.exp(-d**2 / (quarter/2)**2) + np.random.rand() * 0.2
                        
        return np.clip(grid, 0, 1)
    
    def sample_params(self) -> Dict:
        """Sample random parameters"""
        params = {
            "mu": np.random.uniform(*self.bounds["mu"]),
            "sigma": np.random.uniform(*self.bounds["sigma"]),
            "kernel_coeffs": [np.random.uniform(*self.bounds["k"]) for _ in range(4)],
        }
        return params
    
    def mutate_params(self, params: Dict, mutation_rate: float = 0.2) -> Dict:
        """Mutate parameters"""
        new_params = params.copy()
        new_params["kernel_coeffs"] = params["kernel_coeffs"].copy()
        
        if np.random.rand() < mutation_rate:
            new_params["mu"] = np.clip(
                params["mu"] + np.random.randn() * 0.02,
                *self.bounds["mu"]
            )
        
        if np.random.rand() < mutation_rate:
            new_params["sigma"] = np.clip(
                params["sigma"] + np.random.randn() * 0.005,
                *self.bounds["sigma"]
            )
        
        for i in range(4):
            if np.random.rand() < mutation_rate:
                new_params["kernel_coeffs"][i] = np.clip(
                    params["kernel_coeffs"][i] + np.random.randn() * 0.1,
                    *self.bounds["k"]
                )
        
        return new_params
    
    def crossover(self, p1: Dict, p2: Dict) -> Dict:
        """Crossover two parameter sets"""
        child = {
            "mu": (p1["mu"] + p2["mu"]) / 2,
            "sigma": (p1["sigma"] + p2["sigma"]) / 2,
            "kernel_coeffs": [
                (p1["kernel_coeffs"][i] + p2["kernel_coeffs"][i]) / 2
                for i in range(4)
            ],
        }
        return child
    
    def update_pareto_front(self, params: Dict, scores: Dict):
        """Update Pareto front with new solution"""
        stability = scores["stability"]
        complexity = scores["complexity"]
        
        # Check if dominated by existing solutions
        is_dominated = False
        to_remove = []
        
        for i, solution in enumerate(self.pareto_front):
            s, c = solution["stability"], solution["complexity"]
            
            # Dominated by existing?
            if s >= stability and c >= complexity and (s > stability or c > complexity):
                is_dominated = True
                break
            
            # Dominates existing?
            if stability >= s and complexity >= c and (stability > s or complexity > c):
                to_remove.append(i)
        
        # Remove dominated solutions
        for i in reversed(to_remove):
            self.pareto_front.pop(i)
        
        # Add if not dominated
        if not is_dominated:
            self.pareto_front.append({
                "params": params.copy(),
                "stability": stability,
                "complexity": complexity,
                "fitness": scores["fitness"],
            })
    
    def evolve(self, seeds: List[np.ndarray] = None, verbose: bool = True) -> Dict:
        """Run evolutionary optimization"""
        if seeds is None:
            seeds = [
                self.create_seed("orbium"),
                self.create_seed("random"),
                self.create_seed("perturbed"),
            ]
        
        # Initialize population with species-inspired params
        population = []
        for i in range(self.population_size):
            if i < len(self.starting_points):
                # Start from known species
                sp = self.starting_points[i % len(self.starting_points)]
                params = {
                    "mu": sp["mu"],
                    "sigma": sp["sigma"],
                    "kernel_coeffs": [0.5, 0.7, 0.5, 0.3],  # Default rings
                }
                # Add small noise
                params = self.mutate_params(params, mutation_rate=0.5)
            else:
                params = self.sample_params()
            population.append(params)
        
        # Evolution history
        history = []
        best_fitness = 0
        best_params = None
        
        for gen in range(self.generations):
            # Evaluate population
            fitness_scores = []
            all_scores = []
            
            for params in population:
                scores = self.compute_fitness(params, seeds)
                fitness_scores.append(scores["fitness"])
                all_scores.append(scores)
                self.update_pareto_front(params, scores)
            
            # Track best
            gen_best_idx = np.argmax(fitness_scores)
            if fitness_scores[gen_best_idx] > best_fitness:
                best_fitness = fitness_scores[gen_best_idx]
                best_params = population[gen_best_idx].copy()
            
            # Selection and reproduction
            elite_idx = np.argsort(fitness_scores)[::-1][:self.population_size // 4]
            new_population = [population[i] for i in elite_idx]
            
            # Create offspring
            while len(new_population) < self.population_size:
                # Tournament selection
                idx1, idx2 = np.random.choice(len(population), 2, replace=False)
                parent1 = population[idx1 if fitness_scores[idx1] > fitness_scores[idx2] else idx2]
                
                idx3, idx4 = np.random.choice(len(population), 2, replace=False)
                parent2 = population[idx3 if fitness_scores[idx3] > fitness_scores[idx4] else idx4]
                
                # Crossover and mutation
                child = self.crossover(parent1, parent2)
                child = self.mutate_params(child)
                new_population.append(child)
            
            population = new_population
            
            # Log
            if verbose:
                mean_fit = np.mean(fitness_scores)
                max_fit = np.max(fitness_scores)
                pareto_size = len(self.pareto_front)
                print(f"Gen {gen}: fit mean={mean_fit:.4f}, max={max_fit:.4f}, "
                      f"Pareto={pareto_size}, best_μ={best_params['mu']:.3f}, "
                      f"best_σ={best_params['sigma']:.4f}")
            
            history.append({
                "generation": gen,
                "mean_fitness": np.mean(fitness_scores),
                "max_fitness": np.max(fitness_scores),
                "pareto_size": len(self.pareto_front),
            })
        
        return {
            "best_fitness": best_fitness,
            "best_params": best_params,
            "pareto_front": self.pareto_front,
            "history": history,
        }


def run_experiment(**kwargs):
    """Run kernel-growth co-evolution experiment"""
    defaults = {
        "dim": 64,
        "steps": 256,
        "population_size": 16,
        "generations": 12,
    }
    defaults.update(kwargs)
    
    evolver = KernelGrowthEvolver(**defaults)
    results = evolver.evolve()
    
    # Save results
    timestamp = int(time.time())
    output_dir = "D:/openclaw_workspace/output/evo_lenia_v7_kernel_growth"
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert to serializable format
    save_results = {
        "best_fitness": results["best_fitness"],
        "best_params": results["best_params"],
        "pareto_front": results["pareto_front"],
        "history": results["history"],
    }
    
    with open(f"{output_dir}/results_{timestamp}.json", "w") as f:
        json.dump(save_results, f, indent=2, default=str)
    
    print(f"\nResults saved to {output_dir}/results_{timestamp}.json")
    print(f"Best fitness: {results['best_fitness']:.4f}")
    print(f"Best params: μ={results['best_params']['mu']:.3f}, σ={results['best_params']['sigma']:.4f}")
    print(f"Pareto front size: {len(results['pareto_front'])}")
    
    return results


if __name__ == "__main__":
    results = run_experiment()
