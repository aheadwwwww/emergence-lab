"""
Evolutionary Lenia V4 - Warm Start from Orbium Parameters
===========================================================

Key insight from V3 failure: Random initialization leads to dead patterns.
Solution: Initialize population near known working Orbium parameters.

Orbium parameters (from Bert Chan's official Lenia):
  - R=13 (kernel radius)
  - mu=0.15 (growth function mean)
  - sigma=0.014 (growth function width)
  - Kernel: bump4 shape with ring at r~0.5

This version:
1. Initializes population as variations of the Orbium bump4 kernel
2. Uses smaller mutation scale (0.05 instead of 0.15)
3. Hybrid fitness with alpha=0.5
4. Tests primarily on orbium seed for faster iterations
"""

import jax
import jax.numpy as jnp
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Optional
import json
import time

from lenia_jax import make_orbium, _make_disk_kernel_np


# ═══════════════════════════════════════════════════════════════
# Orbium Kernel Generator (Warm Start)
# ═══════════════════════════════════════════════════════════════

def make_orbium_kernel_params(R: int = 10) -> Dict[str, Any]:
    """
    Orbium-like parameters optimized from parameter search v2.
    
    From lenia_parameter_analysis.md:
      Best: R=10, mu=0.1622, sigma=0.0257
      
    Also supporting Orbium standard: R=13, mu=0.15, sigma=0.014
    """
    return {
        'R': R,
        'mu': 0.1622,  # From best param search
        'sigma': 0.0257,  # From best param search
        'kn': 1,  # bump4 kernel
        'gn': 1,  # gaussian growth
    }


def make_bump4_kernel(R: int = 10) -> np.ndarray:
    """
    Create Orbium's bump4 kernel.
    
    bump4 kernel shape: exp(4 - 1/(r*(1-r))) for 0 < r < 1
    
    This creates a ring-shaped kernel with peak around r=0.5.
    """
    y, x = np.ogrid[-R:R+1, -R:R+1]
    r = np.sqrt(x*x + y*y) / R
    r = np.clip(r, 1e-8, 1 - 1e-8)
    
    # Bump4 kernel: exp(4 - 1/(r*(1-r)))
    # This peaks at r=0.5 and goes to 0 at r=0 and r=1
    kernel = np.exp(4.0 - 1.0 / (r * (1.0 - r)))
    
    # Zero beyond R
    mask = r <= 1.0
    kernel = kernel * mask
    
    # Normalize
    kernel = kernel / (kernel.sum() + 1e-8)
    
    return kernel.astype(np.float32)


def make_quad4_kernel(R: int = 10) -> np.ndarray:
    """
    Create quad4 kernel (alternative kernel shape).
    
    quad4 kernel: (4*r*(1-r))^4 for 0 < r < 1
    Also ring-shaped but with different profile.
    """
    y, x = np.ogrid[-R:R+1, -R:R+1]
    r = np.sqrt(x*x + y*y) / R
    r = np.clip(r, 1e-8, 1 - 1e-8)
    
    # quad4 kernel: (4*r*(1-r))^4
    kernel = (4 * r * (1.0 - r))**4
    
    # Zero beyond R
    mask = r <= 1.0
    kernel = kernel * mask
    
    # Normalize
    kernel = kernel / (kernel.sum() + 1e-8)
    
    return kernel.astype(np.float32)


def make_orbium_kernel_perturbed(R: int = 15, perturbation: float = 0.05) -> np.ndarray:
    """
    Create a perturbed Orbium-like kernel for warm start.
    
    The base is the bump4 kernel, with small perturbations added.
    Perturbation scale controls how far from Orbium we deviate.
    """
    # Start with bump4 kernel
    kernel = make_bump4_kernel(R)
    
    # Add small perturbation
    noise = np.random.randn(kernel.shape[0], kernel.shape[1]).astype(np.float32)
    # Smooth the noise slightly
    from scipy.ndimage import gaussian_filter
    noise = gaussian_filter(noise, sigma=1.0)
    
    # Add perturbation
    kernel_perturbed = kernel + perturbation * noise * kernel
    
    # Re-normalize
    kernel_perturbed = np.clip(kernel_perturbed, 0, None)
    kernel_perturbed = kernel_perturbed / (kernel_perturbed.sum() + 1e-8)
    
    return kernel_perturbed.astype(np.float32)


# ═══════════════════════════════════════════════════════════════
# Genome for Kernel Evolution
# ═══════════════════════════════════════════════════════════════

@dataclass
class Genome:
    """Genome = kernel array + mu/sigma parameters."""
    kernel: np.ndarray  # [2R+1, 2R+1] kernel
    mu: float
    sigma: float
    R: int
    
    @staticmethod
    def create_orbium_like(R: int = 10, perturbation: float = 0.05) -> 'Genome':
        """Create a genome near best search parameters (R=10, mu=0.1622, sigma=0.0257)."""
        kernel = make_orbium_kernel_perturbed(R, perturbation)
        # Best params from search with small random perturbation
        mu = 0.1622 + np.random.randn() * 0.02
        sigma = 0.0257 + np.random.randn() * 0.005
        # Clip to reasonable ranges
        mu = np.clip(mu, 0.12, 0.25)
        sigma = np.clip(sigma, 0.015, 0.05)
        return Genome(kernel=kernel, mu=float(mu), sigma=float(sigma), R=R)
    
    @staticmethod
    def create_population(size: int, R: int = 15, perturbation: float = 0.05) -> List['Genome']:
        """Create initial population near Orbium parameters."""
        return [Genome.create_orbium_like(R, perturbation) for _ in range(size)]
    
    def mutate(self, scale: float = 0.05) -> 'Genome':
        """Mutate genome with small perturbations."""
        from scipy.ndimage import gaussian_filter
        
        # Mutate kernel
        noise = np.random.randn(*self.kernel.shape).astype(np.float32)
        noise = gaussian_filter(noise, sigma=1.0)  # Smooth
        kernel_mutated = self.kernel + scale * noise * self.kernel
        kernel_mutated = np.clip(kernel_mutated, 0, None)
        kernel_mutated = kernel_mutated / (kernel_mutated.sum() + 1e-8)
        
        # Mutate mu and sigma
        mu_mutated = self.mu + np.random.randn() * scale * 0.02
        sigma_mutated = self.sigma + np.random.randn() * scale * 0.005
        
        # Clip
        mu_mutated = np.clip(mu_mutated, 0.08, 0.35)
        sigma_mutated = np.clip(sigma_mutated, 0.005, 0.08)
        
        return Genome(
            kernel=kernel_mutated.astype(np.float32),
            mu=float(mu_mutated),
            sigma=float(sigma_mutated),
            R=self.R
        )
    
    def crossover(self, other: 'Genome') -> 'Genome':
        """Crossover with another genome."""
        # Blend kernels
        alpha = np.random.rand()
        kernel_blended = alpha * self.kernel + (1 - alpha) * other.kernel
        kernel_blended = kernel_blended / (kernel_blended.sum() + 1e-8)
        
        # Blend parameters
        mu_blended = alpha * self.mu + (1 - alpha) * other.mu
        sigma_blended = alpha * self.sigma + (1 - alpha) * other.sigma
        
        return Genome(
            kernel=kernel_blended.astype(np.float32),
            mu=float(mu_blended),
            sigma=float(sigma_blended),
            R=self.R
        )
    
    def to_kernel_fft(self, size: int) -> jnp.ndarray:
        """Convert to FFT-ready kernel (properly padded and rolled for FFT)."""
        # Pad kernel to grid size
        kernel_hw = 2 * self.R + 1
        pad_h = (size - kernel_hw) // 2
        pad_w = (size - kernel_hw) // 2
        
        kernel_padded = np.pad(
            self.kernel,
            ((pad_h, size - kernel_hw - pad_h),
             (pad_w, size - kernel_hw - pad_w))
        )
        
        # Roll so kernel center is at (0, 0) for FFT
        cy = pad_h + self.R
        cx = pad_w + self.R
        kernel_padded = np.roll(kernel_padded, -cy, axis=0)
        kernel_padded = np.roll(kernel_padded, -cx, axis=1)
        
        return jnp.fft.fft2(jnp.array(kernel_padded))


# ═══════════════════════════════════════════════════════════════
# Lenia Simulation
# ═══════════════════════════════════════════════════════════════

def run_lenia(
    kernel_fft: jnp.ndarray,
    mu: float,
    sigma: float,
    seed_grid: jnp.ndarray,
    steps: int = 200,
    dt: float = 0.1,
    gn: int = 1
) -> List[np.ndarray]:
    """Run Lenia simulation and return history."""
    grid = jnp.array(seed_grid)
    history = [np.array(grid)]
    
    for step in range(steps):
        grid_fft = jnp.fft.fft2(grid)
        potential = jnp.fft.ifft2(grid_fft * kernel_fft).real
        potential = jnp.clip(potential, 0, 1)
        
        # Growth function (gn=1 is gaussian)
        if gn == 1:
            # Gaussian growth: exp(-(n-m)^2/(2*s^2)) * 2 - 1
            growth = jnp.exp(-((potential - mu) ** 2) / (2 * sigma ** 2)) * 2 - 1
        else:
            # quad4 growth: max(0, 1-(n-m)^2/(9*s^2))^4 * 2 - 1
            growth = jnp.maximum(0, 1 - ((potential - mu) / (9 * sigma))**2)**4 * 2 - 1
        
        grid = jnp.clip(grid + dt * growth, 0, 1)
        
        if step % 20 == 0:
            history.append(np.array(grid))
    
    history.append(np.array(grid))
    return history


# ═══════════════════════════════════════════════════════════════
# Hybrid Fitness (V3-style)
# ═══════════════════════════════════════════════════════════════

def compute_stability_fitness(history: List[np.ndarray], alpha: float = 0.5) -> float:
    """
    V1-style stability fitness.
    
    Rewards:
    - Survival (pattern doesn't die)
    - Homeostasis (mass stays near initial)
    - Structural complexity (entropy)
    """
    if len(history) < 2:
        return 0.0
    
    initial = history[0]
    final = history[-1]
    
    initial_mass = float(initial.sum())
    final_mass = float(final.sum())
    
    # Survival
    survival = 1.0 if final_mass > 0.1 * initial_mass else final_mass / (0.1 * initial_mass + 1e-8)
    survival = min(1.0, survival)
    
    # Homeostasis (penalize drift)
    mass_ratio = final_mass / (initial_mass + 1e-8)
    homeostasis = 1.0 - abs(1.0 - mass_ratio) * 0.5
    homeostasis = max(0.0, homeostasis)
    
    # Structural complexity (entropy-like)
    flat = final.flatten()
    hist, _ = np.histogram(flat[flat > 0.01], bins=20, range=(0, 1))
    hist = hist / (hist.sum() + 1e-8)
    entropy = -np.sum(hist * np.log2(hist + 1e-8))
    complexity = min(1.0, entropy / 4.0)  # Normalize
    
    stability = survival * (0.6 + 0.4 * homeostasis) * (1.0 + 0.2 * complexity)
    return float(stability)


def compute_emergence_fitness(history: List[np.ndarray]) -> float:
    """
    V2-style emergence fitness.
    
    Rewards:
    - Temporal dynamics (pattern changes over time)
    - Spatial complexity (edges, structure)
    - Novelty (non-uniform distribution)
    """
    if len(history) < 3:
        return 0.0
    
    T = len(history)
    
    # Temporal dynamics
    changes = []
    for i in range(1, min(T, 10)):
        idx = min(i * (T // 10), T - 1)
        prev_idx = max(0, idx - T // 10)
        diff = np.abs(history[idx] - history[prev_idx])
        changes.append(float(diff.mean()))
    dynamics = float(np.mean(changes)) if changes else 0.0
    
    # Spatial complexity (edge density)
    final = history[-1]
    grad_y = np.abs(np.diff(final, axis=0))
    grad_x = np.abs(np.diff(final, axis=1))
    grad_y = np.pad(grad_y, ((0, 1), (0, 0)))
    grad_x = np.pad(grad_x, ((0, 0), (0, 1)))
    edges = np.sqrt(grad_y**2 + grad_x**2)
    complexity = float(edges.mean())
    
    # Novelty (non-uniform distribution)
    mass_std = float(final.std())
    mass_mean = float(final.mean())
    novelty = mass_std / (mass_mean + 1e-8) if mass_mean > 0.01 else 0.0
    
    # Combined emergence score
    emergence = (dynamics * 10) * (0.3 + 0.4 * complexity) * (0.5 + 0.5 * min(1.0, novelty))
    return float(emergence)


def compute_hybrid_fitness(
    history: List[np.ndarray],
    alpha: float = 0.5
) -> Tuple[float, Dict[str, float]]:
    """
    Hybrid fitness combining stability and emergence.
    
    fitness = alpha * stability + (1 - alpha) * emergence
    """
    stability = compute_stability_fitness(history)
    emergence = compute_emergence_fitness(history)
    
    hybrid = alpha * stability + (1 - alpha) * emergence
    
    components = {
        'stability': stability,
        'emergence': emergence,
        'hybrid': hybrid,
        'survival': float(history[-1].sum() > 0.1 * history[0].sum()),
    }
    
    return hybrid, components


# ═══════════════════════════════════════════════════════════════
# Evolution Engine
# ═══════════════════════════════════════════════════════════════

class EvolutionEngine:
    """Evolution engine with warm start from Orbium parameters."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.R = config.get('kernel_radius', 15)
        self.grid_size = config.get('grid_size', 128)
        self.pop_size = config.get('population_size', 20)
        self.generations = config.get('generations', 10)
        self.mutation_scale = config.get('mutation_scale', 0.05)
        self.elite_fraction = config.get('elite_fraction', 0.3)
        self.sim_steps = config.get('sim_steps', 200)
        self.dt = config.get('dt', 0.1)
        self.alpha = config.get('hybrid_alpha', 0.5)
        self.output_dir = Path(config.get('output_dir', 'output/evo_lenia_v4_warmstart'))
        self.verbose = config.get('verbose', True)
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare seed grid (orbium only for faster iterations)
        self.seed_grid = self._make_orbium_seed()
        
        # Population
        self.population: List[Genome] = []
        self.fitness_history: List[Dict] = []
        self.best_genome: Optional[Genome] = None
        self.best_fitness: float = 0.0
    
    def _make_orbium_seed(self) -> jnp.ndarray:
        """Create Orbium seed pattern from actual Orbium seed file."""
        # Load the real Orbium O2u seed
        seed_path = Path('D:/openclaw_workspace/experiments/lenia_seed_O2u.npy')
        if seed_path.exists():
            seed = np.load(seed_path)
            # Place seed in center of grid
            h, w = self.grid_size, self.grid_size
            sh, sw = seed.shape
            grid = np.zeros((h, w), dtype=np.float32)
            y0 = (h - sh) // 2
            x0 = (w - sw) // 2
            grid[y0:y0+sh, x0:x0+sw] = seed
            return jnp.array(grid)
        else:
            # Fallback to synthetic orbium
            return make_orbium((self.grid_size, self.grid_size), self.R)
    
    def initialize_population(self):
        """Initialize population with Orbium-like genomes."""
        perturbation = self.config.get('init_perturbation', 0.05)
        self.population = Genome.create_population(
            self.pop_size, 
            self.R, 
            perturbation
        )
        if self.verbose:
            print(f"Initialized {len(self.population)} genomes near Orbium parameters")
            print(f"  mu range: {[g.mu for g in self.population[:3]]}")
            print(f"  sigma range: {[g.sigma for g in self.population[:3]]}")
    
    def evaluate_genome(self, genome: Genome) -> Tuple[float, Dict[str, float]]:
        """Evaluate a single genome."""
        kernel_fft = genome.to_kernel_fft(self.grid_size)
        history = run_lenia(
            kernel_fft, 
            genome.mu, 
            genome.sigma,
            self.seed_grid,
            self.sim_steps,
            self.dt
        )
        return compute_hybrid_fitness(history, self.alpha)
    
    def evaluate_population(self) -> List[Tuple[int, float, Dict]]:
        """Evaluate all genomes in population."""
        results = []
        for i, genome in enumerate(self.population):
            fitness, components = self.evaluate_genome(genome)
            results.append((i, fitness, components))
        return results
    
    def select_elite(self, results: List[Tuple[int, float, Dict]]) -> List[int]:
        """Select elite genomes."""
        sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
        n_elite = max(2, int(self.pop_size * self.elite_fraction))
        return [r[0] for r in sorted_results[:n_elite]]
    
    def evolve(self) -> Dict[str, Any]:
        """Run evolution."""
        if self.verbose:
            print("=" * 60)
            print("Evolutionary Lenia V4 - Warm Start from Orbium")
            print("=" * 60)
            print(f"Config:")
            print(f"  Population: {self.pop_size}")
            print(f"  Generations: {self.generations}")
            print(f"  Mutation scale: {self.mutation_scale}")
            print(f"  Hybrid alpha: {self.alpha}")
            print(f"  Kernel radius: {self.R}")
            print(f"  Grid size: {self.grid_size}")
            print(f"  Simulation steps: {self.sim_steps}")
            print("=" * 60)
        
        # Initialize
        self.initialize_population()
        
        results = {
            'fitness_history': [],
            'best_genome': None,
            'best_fitness': 0.0,
            'config': self.config,
        }
        
        for gen in range(self.generations):
            start_time = time.time()
            
            # Evaluate
            eval_results = self.evaluate_population()
            
            # Record stats
            fitnesses = [r[1] for r in eval_results]
            components_list = [r[2] for r in eval_results]
            
            stats = {
                'generation': gen,
                'mean_fitness': float(np.mean(fitnesses)),
                'max_fitness': float(np.max(fitnesses)),
                'min_fitness': float(np.min(fitnesses)),
                'std_fitness': float(np.std(fitnesses)),
                'mean_stability': float(np.mean([c['stability'] for c in components_list])),
                'mean_emergence': float(np.mean([c['emergence'] for c in components_list])),
                'survival_rate': float(np.mean([c['survival'] for c in components_list])),
            }
            self.fitness_history.append(stats)
            
            # Track best
            best_idx = int(np.argmax(fitnesses))
            if fitnesses[best_idx] > self.best_fitness:
                self.best_fitness = fitnesses[best_idx]
                self.best_genome = self.population[best_idx]
            
            elapsed = time.time() - start_time
            
            if self.verbose:
                print(f"Gen {gen:3d}: fit={stats['max_fitness']:.4f} "
                      f"(mean={stats['mean_fitness']:.4f}±{stats['std_fitness']:.4f}) "
                      f"stab={stats['mean_stability']:.3f} "
                      f"emrg={stats['mean_emergence']:.3f} "
                      f"surv={stats['survival_rate']:.2f} "
                      f"[{elapsed:.1f}s]")
            
            # Early stopping if converged
            if gen > 3 and stats['std_fitness'] < 0.001:
                if self.verbose:
                    print("Early stopping: population converged")
                break
            
            # Selection
            elite_indices = self.select_elite(eval_results)
            elite = [self.population[i] for i in elite_indices]
            
            # Create next generation
            new_population = []
            
            # Keep elite
            for genome in elite:
                new_population.append(Genome(
                    kernel=genome.kernel.copy(),
                    mu=genome.mu,
                    sigma=genome.sigma,
                    R=genome.R
                ))
            
            # Fill rest with mutated elite
            while len(new_population) < self.pop_size:
                # Select two random elite for crossover
                if len(elite) >= 2:
                    i1, i2 = np.random.choice(len(elite), 2, replace=False)
                    child = elite[i1].crossover(elite[i2])
                    child = child.mutate(self.mutation_scale)
                else:
                    child = elite[0].mutate(self.mutation_scale)
                new_population.append(child)
            
            self.population = new_population
        
        # Save results
        results['fitness_history'] = self.fitness_history
        results['best_fitness'] = self.best_fitness
        if self.best_genome:
            results['best_mu'] = self.best_genome.mu
            results['best_sigma'] = self.best_genome.sigma
            np.save(self.output_dir / 'best_kernel.npy', self.best_genome.kernel)
        
        # Save history
        with open(self.output_dir / 'history.json', 'w') as f:
            json.dump(self.fitness_history, f, indent=2)
        
        # Generate visualizations
        self._visualize_results(results)
        
        if self.verbose:
            print("=" * 60)
            print(f"Evolution complete!")
            print(f"Best fitness: {self.best_fitness:.4f}")
            if self.best_genome:
                print(f"Best mu: {self.best_genome.mu:.4f}")
                print(f"Best sigma: {self.best_genome.sigma:.4f}")
            print(f"Results saved to: {self.output_dir}")
            print("=" * 60)
        
        return results
    
    def _visualize_results(self, results: Dict):
        """Generate visualizations."""
        # Fitness over generations
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Fitness history
        ax = axes[0, 0]
        gens = [h['generation'] for h in self.fitness_history]
        max_fit = [h['max_fitness'] for h in self.fitness_history]
        mean_fit = [h['mean_fitness'] for h in self.fitness_history]
        std_fit = [h['std_fitness'] for h in self.fitness_history]
        
        ax.fill_between(gens, 
                        [m - s for m, s in zip(mean_fit, std_fit)],
                        [m + s for m, s in zip(mean_fit, std_fit)],
                        alpha=0.3, color='blue')
        ax.plot(gens, max_fit, 'g-', linewidth=2, label='Max')
        ax.plot(gens, mean_fit, 'b-', linewidth=2, label='Mean')
        ax.set_xlabel('Generation')
        ax.set_ylabel('Fitness')
        ax.set_title('Fitness Evolution')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Stability vs Emergence
        ax = axes[0, 1]
        stability = [h['mean_stability'] for h in self.fitness_history]
        emergence = [h['mean_emergence'] for h in self.fitness_history]
        ax.scatter(stability, emergence, c=gens, cmap='viridis', s=50)
        ax.set_xlabel('Stability')
        ax.set_ylabel('Emergence')
        ax.set_title('Stability vs Emergence (color = generation)')
        ax.grid(True, alpha=0.3)
        
        # Survival rate
        ax = axes[1, 0]
        survival = [h['survival_rate'] for h in self.fitness_history]
        ax.plot(gens, survival, 'r-', linewidth=2)
        ax.set_xlabel('Generation')
        ax.set_ylabel('Survival Rate')
        ax.set_title('Pattern Survival Rate')
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 1.1)
        
        # Best kernel visualization
        ax = axes[1, 1]
        if self.best_genome is not None:
            im = ax.imshow(self.best_genome.kernel, cmap='inferno')
            ax.set_title(f'Best Kernel (μ={self.best_genome.mu:.3f}, σ={self.best_genome.sigma:.4f})')
            plt.colorbar(im, ax=ax)
        else:
            ax.text(0.5, 0.5, 'No best genome', ha='center', va='center')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'evolution_summary.png', dpi=150)
        plt.close()
        
        # Visualize best pattern
        if self.best_genome:
            self._visualize_best_pattern()
    
    def _visualize_best_pattern(self):
        """Visualize the best pattern evolution."""
        if self.best_genome is None:
            return
        
        kernel_fft = self.best_genome.to_kernel_fft(self.grid_size)
        history = run_lenia(
            kernel_fft, 
            self.best_genome.mu, 
            self.best_genome.sigma,
            self.seed_grid,
            self.sim_steps,
            self.dt
        )
        
        # Create timeline visualization
        n_frames = min(8, len(history))
        indices = [int(i * (len(history) - 1) / (n_frames - 1)) for i in range(n_frames)]
        
        fig, axes = plt.subplots(2, 4, figsize=(16, 8))
        axes = axes.flatten()
        
        for i, idx in enumerate(indices):
            axes[i].imshow(history[idx], cmap='inferno', vmin=0, vmax=1)
            axes[i].set_title(f'Step {idx * 20}')
            axes[i].axis('off')
        
        plt.suptitle(f'Best Pattern Evolution (fitness={self.best_fitness:.4f})', fontsize=14)
        plt.tight_layout()
        plt.savefig(self.output_dir / 'best_pattern_timeline.png', dpi=150)
        plt.close()


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def create_v4_config() -> Dict[str, Any]:
    """Create V4 warmstart configuration."""
    return {
        'population_size': 20,
        'generations': 10,
        'kernel_radius': 10,  # Best from param search
        'grid_size': 128,
        'sim_steps': 200,
        'dt': 0.1,
        'mutation_scale': 0.05,  # Smaller than V3's 0.15
        'elite_fraction': 0.3,
        'hybrid_alpha': 0.5,  # Equal weight stability/emergence
        'init_perturbation': 0.05,  # Small perturbation from Orbium
        'output_dir': 'D:/openclaw_workspace/output/evo_lenia_v4_warmstart',
        'verbose': True,
    }


def main():
    """Run V4 warmstart experiment."""
    print("\n" + "=" * 60)
    print("LENIA V4 WARMSTART EXPERIMENT")
    print("=" * 60)
    print("\nKey features:")
    print("  1. Initialize near Orbium parameters (mu~0.15, sigma~0.014)")
    print("  2. Bump4 ring kernel initialization")
    print("  3. Small mutation scale (0.05)")
    print("  4. Hybrid fitness (alpha=0.5)")
    print("  5. Orbium seed for faster iterations")
    print("=" * 60 + "\n")
    
    config = create_v4_config()
    engine = EvolutionEngine(config)
    results = engine.evolve()
    
    # Save final summary
    summary = {
        'experiment': 'V4 Warmstart',
        'config': config,
        'best_fitness': results.get('best_fitness', 0),
        'best_mu': results.get('best_mu', 0),
        'best_sigma': results.get('best_sigma', 0),
        'generations_run': len(results.get('fitness_history', [])),
        'final_stats': results.get('fitness_history', [{}])[-1] if results.get('fitness_history') else {},
    }
    
    with open(Path(config['output_dir']) / 'summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nFinal summary saved to: {config['output_dir']}/summary.json")
    
    return results


if __name__ == '__main__':
    results = main()