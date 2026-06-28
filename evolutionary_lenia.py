"""
Evolutionary Lenia - Core Components for Hybrid Learning
==========================================================

Provides the base classes and components needed for hybrid evolutionary learning.
"""

import numpy as np
import jax
import jax.numpy as jnp
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import time

# ============================================================================
# Pareto Archetypes (from V6 discoveries)
# ============================================================================

PARETO_ARCHETYPES = {
    'stability_specialist': {
        'mu': 0.12,
        'sigma': 0.05,
        'k': 1,
        'description': 'High stability, lower emergence'
    },
    'emergence_specialist': {
        'mu': 0.18,
        'sigma': 0.04,
        'k': 1,
        'description': 'Higher emergence, moderate stability'
    },
    'balanced_generalist': {
        'mu': 0.15,
        'sigma': 0.045,
        'k': 1,
        'description': 'Balanced stability and emergence'
    },
    'wide_growth': {
        'mu': 0.14,
        'sigma': 0.08,
        'k': 1,
        'description': 'Wide growth function for robustness'
    },
    'narrow_growth': {
        'mu': 0.13,
        'sigma': 0.03,
        'k': 1,
        'description': 'Narrow growth for precision patterns'
    }
}


# ============================================================================
# Lenia System
# ============================================================================

class LeniaSystem:
    """
    Core Lenia simulation system.
    
    Implements continuous cellular automaton with Gaussian ring kernel.
    """
    
    def __init__(self, mu: float = 0.15, sigma: float = 0.05, R: int = 13, 
                 T: int = 10, k: int = 1, dt: float = 0.1):
        self.mu = mu
        self.sigma = sigma
        self.R = R
        self.T = T
        self.k = k
        self.dt = dt
        
        # Grid size derived from R
        self.size = 128
        
        # Pre-compute kernel FFT
        self.kernel_fft = self._make_kernel_fft()
        
    def _make_kernel_fft(self) -> jnp.ndarray:
        """Create Gaussian ring kernel and compute FFT."""
        size = self.size
        R = self.R
        mu = self.mu
        sigma = self.sigma
        
        # Create kernel grid
        kernel = np.zeros((size, size), dtype=np.float32)
        y, x = np.ogrid[-size//2:size//2, -size//2:size//2]
        r = np.sqrt(x*x + y*y) / R
        
        # Gaussian ring kernel
        kernel = np.exp(-((r - mu)**2) / (2 * sigma**2))
        
        # Normalize
        kernel = kernel / kernel.sum()
        
        # Shift for FFT
        kernel = np.fft.ifftshift(kernel)
        
        # Compute FFT
        kernel_fft = jnp.fft.fft2(jnp.array(kernel))
        
        return kernel_fft
    
    def growth(self, U: jnp.ndarray) -> jnp.ndarray:
        """Growth function: Gaussian centered at mu with width sigma."""
        return 2 * jnp.exp(-((U - self.mu)**2) / (2 * self.sigma**2)) - 1
    
    def step(self, grid: jnp.ndarray) -> jnp.ndarray:
        """Single simulation step."""
        # Convolve with kernel via FFT
        grid_fft = jnp.fft.fft2(grid)
        U = jnp.fft.ifft2(grid_fft * self.kernel_fft).real
        
        # Apply growth function
        G = self.growth(U)
        
        # Update grid
        new_grid = jnp.clip(grid + self.dt * G, 0, 1)
        
        return new_grid
    
    def create_seed(self, seed_type: str = 'orbium') -> jnp.ndarray:
        """Create initial pattern seed."""
        size = self.size
        
        if seed_type == 'orbium':
            # Create Orbium-like pattern
            grid = np.zeros((size, size), dtype=np.float32)
            mid = size // 2
            
            # Simple smooth disk pattern
            y, x = np.ogrid[:size, :size]
            r = np.sqrt((x - mid)**2 + (y - mid)**2)
            
            # Smooth disk with gradient
            disk_radius = size // 8
            grid[r < disk_radius] = 1.0
            
            # Smooth edges
            transition = 3
            mask = (r >= disk_radius) & (r < disk_radius + transition)
            grid[mask] = 1.0 - (r[mask] - disk_radius) / transition
            
        elif seed_type == 'random':
            # Random pattern
            grid = np.random.rand(size, size).astype(np.float32) * 0.3
            
        elif seed_type == 'spot':
            # Single spot
            grid = np.zeros((size, size), dtype=np.float32)
            mid = size // 2
            grid[mid-2:mid+2, mid-2:mid+2] = 1.0
            
        else:
            grid = np.random.rand(size, size).astype(np.float32) * 0.5
            
        return jnp.array(grid)


# ============================================================================
# Evolutionary Trial
# ============================================================================

@dataclass
class TrialResult:
    """Results from a single evolutionary trial."""
    fitness: float
    survival: float
    complexity: float
    stability: float
    diversity: float
    final_mass: float
    history: List[np.ndarray]


class EvolutionaryTrial:
    """
    Run a Lenia simulation and compute fitness metrics.
    """
    
    def __init__(self, system: LeniaSystem, max_steps: int = 200):
        self.system = system
        self.max_steps = max_steps
        
    def run(self, seed_type: str = 'orbium') -> TrialResult:
        """Run simulation and return fitness metrics."""
        grid = self.system.create_seed(seed_type)
        history = [np.array(grid)]
        
        # Run simulation
        for step in range(self.max_steps):
            grid = self.system.step(grid)
            if step % 20 == 0:
                history.append(np.array(grid))
        
        history.append(np.array(grid))
        
        # Compute metrics
        final = np.array(grid)
        
        # Survival: fraction of alive cells
        survival = float(np.mean(final > 0.1))
        
        # Diversity: standard deviation of cell values
        diversity = float(np.std(final))
        
        # Stability: temporal variance in final portion
        masses = [h.sum() for h in history[-5:]]
        if len(masses) > 1 and np.mean(masses) > 0:
            stability = 1.0 - min(1.0, np.var(masses) / (np.mean(masses)**2 + 1e-8))
            stability = max(0, float(stability))
        else:
            stability = 0.0
        
        # Complexity: combination of survival and diversity
        complexity = survival * diversity * (1 + stability)
        
        # Fitness: composite score
        fitness = survival * stability * (1 + diversity) * (1 + complexity)
        
        result = TrialResult(
            fitness=fitness,
            survival=survival,
            complexity=complexity,
            stability=stability,
            diversity=diversity,
            final_mass=float(final.sum()),
            history=history
        )
        
        # Return as dict for compatibility
        return {
            'fitness': result.fitness,
            'survival': result.survival,
            'complexity': result.complexity,
            'stability': result.stability,
            'diversity': result.diversity,
            'final_mass': result.final_mass,
            'history': result.history
        }


# ============================================================================
# Lenia Evolver
# ============================================================================

class LeniaEvolver:
    """
    Evolve Lenia parameters using genetic algorithm.
    """
    
    def __init__(self, population_size: int = 20, generations: int = 10):
        self.population_size = population_size
        self.generations = generations
        self.population: List[Dict] = []
        self.history: List[Dict] = []
        
    def initialize_population(self):
        """Initialize random population."""
        self.population = []
        
        for _ in range(self.population_size):
            params = {
                'mu': np.random.uniform(0.1, 0.2),
                'sigma': np.random.uniform(0.02, 0.1),
                'R': 13,
                'T': 10,
                'k': 1
            }
            self.population.append({
                'params': params,
                'fitness': 0.0
            })
            
    def evaluate_population(self):
        """Evaluate all individuals."""
        for ind in self.population:
            params = ind['params']
            system = LeniaSystem(
                mu=params['mu'],
                sigma=params['sigma'],
                R=params['R'],
                T=params['T'],
                k=params['k']
            )
            trial = EvolutionaryTrial(system)
            result = trial.run()
            
            ind['fitness'] = result.fitness
            ind['survival'] = result.survival
            ind['complexity'] = result.complexity
            ind['stability'] = result.stability
            
    def select_and_reproduce(self):
        """Selection and reproduction."""
        # Sort by fitness
        self.population.sort(key=lambda x: x['fitness'], reverse=True)
        
        # Keep top half
        elite = self.population[:self.population_size // 2]
        
        # Create offspring
        new_population = elite.copy()
        
        while len(new_population) < self.population_size:
            # Select parent
            parent = elite[np.random.randint(len(elite))]
            
            # Mutate
            child_params = parent['params'].copy()
            child_params['mu'] += np.random.uniform(-0.02, 0.02)
            child_params['sigma'] += np.random.uniform(-0.01, 0.01)
            
            # Clamp
            child_params['mu'] = np.clip(child_params['mu'], 0.1, 0.2)
            child_params['sigma'] = np.clip(child_params['sigma'], 0.02, 0.1)
            
            new_population.append({
                'params': child_params,
                'fitness': 0.0
            })
            
        self.population = new_population
        
    def evolve(self) -> List[Dict]:
        """Run evolution."""
        self.initialize_population()
        
        for gen in range(self.generations):
            self.evaluate_population()
            
            best = max(self.population, key=lambda x: x['fitness'])
            
            self.history.append({
                'generation': gen,
                'best_fitness': best['fitness'],
                'best_params': best['params'].copy(),
                'mean_fitness': np.mean([x['fitness'] for x in self.population])
            })
            
            print(f"Gen {gen}: best_fitness={best['fitness']:.4f}, "
                  f"mu={best['params']['mu']:.3f}, sigma={best['params']['sigma']:.3f}")
            
            if gen < self.generations - 1:
                self.select_and_reproduce()
                
        return self.history


# ============================================================================
# Helper Functions
# ============================================================================

def create_population_from_archetype(archetype_name: str, size: int = 10) -> List[Dict]:
    """
    Create a population from a Pareto archetype with small variations.
    """
    if archetype_name not in PARETO_ARCHETYPES:
        archetype_name = 'balanced_generalist'
        
    archetype = PARETO_ARCHETYPES[archetype_name]
    
    population = []
    for i in range(size):
        # Add small perturbation for diversity
        params = {
            'mu': archetype['mu'] + np.random.uniform(-0.01, 0.01),
            'sigma': archetype['sigma'] + np.random.uniform(-0.005, 0.005),
            'k': archetype.get('k', 1)
        }
        
        # Clamp to valid range
        params['mu'] = np.clip(params['mu'], 0.1, 0.2)
        params['sigma'] = np.clip(params['sigma'], 0.02, 0.1)
        
        population.append({
            'type': f'{archetype_name}_variant_{i}',
            'params': params,
            'fitness': 0.0
        })
        
    return population


# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    print("Evolutionary Lenia Core Components")
    print("=" * 50)
    
    # Test basic functionality
    print("\nTesting LeniaSystem...")
    system = LeniaSystem(mu=0.15, sigma=0.05)
    
    print("\nTesting EvolutionaryTrial...")
    trial = EvolutionaryTrial(system, max_steps=100)
    result = trial.run()
    
    print(f"  Survival: {result.survival:.3f}")
    print(f"  Complexity: {result.complexity:.3f}")
    print(f"  Fitness: {result.fitness:.3f}")
    
    print("\nTesting LeniaEvolver...")
    evolver = LeniaEvolver(population_size=10, generations=3)
    history = evolver.evolve()
    
    print("\nDone!")
