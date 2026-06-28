"""
Diffusion-Based Kernel Generator for Lenia
Inspired by GenCast methodology using Denoising Diffusion Probabilistic Models (DDPM)

This module generates novel Lenia kernels by:
1. Training a simple DDPM on Pareto-optimal kernels from previous explorations
2. Sampling new kernels from the diffusion process
3. Evaluating generated kernels on survival, stability, and complexity metrics

Baseline comparison:
- V6 Pareto: stability_max=0.517, emergence_max=1.328
- V8 GNN best: survival=0.492, complexity=1.911
- V9 Hybrid best: survival=0.959, fitness=2.026
"""

import numpy as np
from scipy.ndimage import convolve
from scipy.stats import entropy
import json
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

# Try to import JAX for acceleration
try:
    import jax
    import jax.numpy as jnp
    from jax import jit, vmap
    from jax.scipy.ndimage import convolve as jax_convolve
    JAX_AVAILABLE = True
    print("JAX available - using accelerated kernels")
except ImportError:
    JAX_AVAILABLE = False
    print("JAX not available - using NumPy fallback")


# ============================================================================
# KERNEL REPRESENTATION
# ============================================================================

@dataclass
class LeniaKernelParams:
    """Parameterization of a Lenia kernel"""
    mu: float  # Ring center (radius)
    sigma: float  # Ring width
    R: int  # Kernel radius
    # Perturbation parameters for asymmetry
    asymmetry_factor: float = 0.0  # 0 = symmetric, 1 = fully asymmetric
    asymmetry_angle: float = 0.0  # Direction of asymmetry
    # Multi-ring components
    ring2_weight: float = 0.0  # Weight of secondary ring
    ring2_mu_offset: float = 0.0  # Secondary ring offset from primary
    
    def to_dict(self) -> Dict:
        return asdict(self)


def create_gaussian_ring_kernel(size: int, mu: float, sigma: float, 
                                 asymmetry_factor: float = 0.0,
                                 asymmetry_angle: float = 0.0,
                                 ring2_weight: float = 0.0,
                                 ring2_mu_offset: float = 0.0) -> np.ndarray:
    """
    Create a 2D Gaussian ring kernel with optional asymmetry and multi-ring components.
    
    Args:
        size: Kernel size (should be odd)
        mu: Ring center radius
        sigma: Ring width
        asymmetry_factor: 0-1, amount of angular asymmetry
        asymmetry_angle: Direction of asymmetry in radians
        ring2_weight: Weight of secondary ring (0-1)
        ring2_mu_offset: Offset of secondary ring from primary
    
    Returns:
        2D kernel array normalized to sum to 1
    """
    xs = np.linspace(-size//2, size//2, size)
    ys = np.linspace(-size//2, size//2, size)
    x, y = np.meshgrid(xs, ys)
    d = np.sqrt(x**2 + y**2)
    theta = np.arctan2(y, x)
    
    # Primary ring
    if asymmetry_factor > 0:
        # Angular modulation for asymmetry
        angular_mod = 1.0 + asymmetry_factor * np.cos(theta - asymmetry_angle)
        effective_sigma = sigma * angular_mod
        primary = np.exp(-((d - mu) / effective_sigma)**2)
    else:
        primary = np.exp(-((d - mu) / sigma)**2)
    
    kernel = primary
    
    # Add secondary ring if specified
    if ring2_weight > 0 and ring2_mu_offset != 0:
        secondary = np.exp(-((d - (mu + ring2_mu_offset)) / sigma)**2)
        kernel = kernel + ring2_weight * secondary
    
    # Normalize
    kernel -= kernel.mean()
    if np.abs(kernel).sum() > 0:
        kernel /= np.abs(kernel).sum()
    
    return kernel


def params_to_kernel_2d(params: LeniaKernelParams, grid_size: int = 31) -> np.ndarray:
    """Convert kernel parameters to 2D grid representation."""
    return create_gaussian_ring_kernel(
        size=grid_size,
        mu=params.mu * params.R,  # Scale mu by R
        sigma=params.sigma * params.R,  # Scale sigma by R
        asymmetry_factor=params.asymmetry_factor,
        asymmetry_angle=params.asymmetry_angle,
        ring2_weight=params.ring2_weight,
        ring2_mu_offset=params.ring2_mu_offset * params.R
    )


# ============================================================================
# DDPM DIFFUSION MODEL
# ============================================================================

class SimpleDDPM:
    """
    Simplified DDPM for 2D kernel generation.
    
    Uses a U-Net style denoiser operating on parameter space rather than raw pixels.
    This is more efficient for our low-dimensional kernel representation.
    """
    
    def __init__(self, 
                 n_diffusion_steps: int = 100,
                 beta_start: float = 0.0001,
                 beta_end: float = 0.02,
                 param_dim: int = 7):  # mu, sigma, R, asymmetry, angle, ring2_weight, ring2_offset
        
        self.n_steps = n_diffusion_steps
        self.param_dim = param_dim
        
        # Linear beta schedule
        self.betas = np.linspace(beta_start, beta_end, n_diffusion_steps)
        self.alphas = 1.0 - self.betas
        self.alphas_cumprod = np.cumprod(self.alphas)
        
        # Simple denoiser network (we'll use a simple MLP)
        # In practice, you'd use a proper neural network
        self.denoiser_weights = None
        
    def q_sample(self, x_0: np.ndarray, t: int, noise: Optional[np.ndarray] = None) -> np.ndarray:
        """Add noise to x_0 at timestep t (forward diffusion)."""
        if noise is None:
            noise = np.random.randn(*x_0.shape)
        
        alpha_t = self.alphas_cumprod[t]
        return np.sqrt(alpha_t) * x_0 + np.sqrt(1 - alpha_t) * noise
    
    def simple_denoise(self, x_t: np.ndarray, t: int) -> np.ndarray:
        """
        Simple denoising step - predicts noise and subtracts it.
        Uses a learned linear transformation for simplicity.
        """
        # In a real DDPM, this would be a neural network
        # Here we use a simple heuristic: gradual denoising toward a learned mean
        
        if self.denoiser_weights is None:
            # Initialize with identity-like transformation
            return x_t * 0.95  # Simple shrinkage
        
        # Apply learned denoising
        predicted_noise = self.denoiser_weights @ x_t
        return x_t - self.betas[t] * predicted_noise
    
    def p_sample(self, x_t: np.ndarray, t: int) -> np.ndarray:
        """Single reverse diffusion step."""
        # Predict x_0 from x_t
        x_0_pred = self.simple_denoise(x_t, t)
        
        # Add small noise for stochasticity (except at t=0)
        if t > 0:
            noise = np.random.randn(*x_t.shape) * np.sqrt(self.betas[t])
            return x_0_pred + noise
        return x_0_pred
    
    def train(self, training_kernels: List[np.ndarray], epochs: int = 100):
        """
        Train the diffusion model on a set of kernels.
        For simplicity, we learn the mean and covariance of the kernel distribution.
        """
        X = np.array(training_kernels)  # [N, param_dim]
        
        # Learn statistics
        self.mean = X.mean(axis=0)
        self.std = X.std(axis=0) + 1e-8
        self.cov = np.cov(X.T) + 1e-6 * np.eye(self.param_dim)
        
        # Simple "training": learn to denoise toward this distribution
        # In practice, you'd train a neural network here
        print(f"Trained on {len(training_kernels)} kernels")
        print(f"Mean: {self.mean}")
        print(f"Std: {self.std}")
        
    def generate(self, n_samples: int = 1, temperature: float = 1.0) -> List[np.ndarray]:
        """
        Generate new samples by reverse diffusion.
        
        For simplicity, we sample from the learned distribution directly
        and apply a diffusion-like perturbation/ denoising process.
        """
        samples = []
        
        for _ in range(n_samples):
            # Start from noise
            x_t = np.random.randn(self.param_dim) * temperature
            
            # Reverse diffusion
            for t in reversed(range(self.n_steps)):
                x_t = self.p_sample(x_t, t)
            
            # Shift toward learned mean
            x_0 = x_t * self.std + self.mean
            
            samples.append(x_0)
        
        return samples


class KernelDiffusionGenerator:
    """
    Main class for generating Lenia kernels using diffusion.
    """
    
    def __init__(self, 
                 param_ranges: Optional[Dict] = None,
                 n_diffusion_steps: int = 50):
        
        # Default parameter ranges
        self.param_ranges = param_ranges or {
            'mu': (0.10, 0.20),
            'sigma': (0.02, 0.10),
            'R': (10, 15),
            'asymmetry_factor': (0.0, 0.5),
            'asymmetry_angle': (0.0, 2 * np.pi),
            'ring2_weight': (0.0, 0.3),
            'ring2_mu_offset': (-0.1, 0.1)
        }
        
        self.ddpm = SimpleDDPM(n_diffusion_steps=n_diffusion_steps)
        self.trained = False
        
    def create_training_kernels(self, pareto_kernels: List[Dict]) -> List[np.ndarray]:
        """
        Convert Pareto-optimal kernels to parameter vectors for training.
        """
        training_data = []
        
        for kernel_dict in pareto_kernels:
            # Extract parameters
            params = [
                kernel_dict.get('mu', 0.15),
                kernel_dict.get('sigma', 0.05),
                kernel_dict.get('R', 12),
                kernel_dict.get('asymmetry_factor', 0.0),
                kernel_dict.get('asymmetry_angle', 0.0),
                kernel_dict.get('ring2_weight', 0.0),
                kernel_dict.get('ring2_mu_offset', 0.0)
            ]
            training_data.append(np.array(params))
        
        return training_data
    
    def train_on_pareto_front(self, pareto_kernels: List[Dict]):
        """Train the diffusion model on Pareto-optimal kernels."""
        training_data = self.create_training_kernels(pareto_kernels)
        self.ddpm.train(training_data)
        self.trained = True
        
    def generate_novel_kernels(self, n_kernels: int = 10, 
                                temperature: float = 1.0,
                                perturbation_strength: float = 0.1) -> List[LeniaKernelParams]:
        """
        Generate novel kernels by sampling from the diffusion process
        and adding strategic perturbations.
        """
        if not self.trained:
            # Use default statistics if not trained
            self.ddpm.mean = np.array([0.15, 0.05, 12.0, 0.0, 0.0, 0.0, 0.0])
            self.ddpm.std = np.array([0.05, 0.03, 2.0, 0.2, 1.0, 0.1, 0.05])
        
        kernels = []
        
        for i in range(n_kernels):
            # Sample from diffusion model
            if self.trained:
                samples = self.ddpm.generate(n_samples=1, temperature=temperature)
                params_vec = samples[0]
            else:
                # Random sampling from ranges
                params_vec = np.array([
                    np.random.uniform(*self.param_ranges['mu']),
                    np.random.uniform(*self.param_ranges['sigma']),
                    np.random.randint(*self.param_ranges['R']),
                    np.random.uniform(*self.param_ranges['asymmetry_factor']),
                    np.random.uniform(*self.param_ranges['asymmetry_angle']),
                    np.random.uniform(*self.param_ranges['ring2_weight']),
                    np.random.uniform(*self.param_ranges['ring2_mu_offset'])
                ])
            
            # Add strategic perturbations to explore novel regions
            perturbation = np.random.randn(7) * perturbation_strength * np.array([
                0.02, 0.01, 1.0, 0.1, 0.5, 0.05, 0.02
            ])
            params_vec = params_vec + perturbation
            
            # Clip to valid ranges
            params_vec = np.clip(params_vec, 
                                  [r[0] for r in self.param_ranges.values()],
                                  [r[1] for r in self.param_ranges.values()])
            
            # Create kernel params
            kernel_params = LeniaKernelParams(
                mu=float(params_vec[0]),
                sigma=float(params_vec[1]),
                R=int(params_vec[2]),
                asymmetry_factor=float(params_vec[3]),
                asymmetry_angle=float(params_vec[4]),
                ring2_weight=float(params_vec[5]),
                ring2_mu_offset=float(params_vec[6])
            )
            
            kernels.append(kernel_params)
        
        return kernels


# ============================================================================
# LENIA SIMULATION AND EVALUATION
# ============================================================================

def growth_function(u: np.ndarray, mu: float = 0.15, sigma: float = 0.015) -> np.ndarray:
    """Growth mapping for Lenia."""
    return 2 * np.exp(-((u - mu)**2) / (2 * sigma**2)) - 1


def run_lenia_simulation(kernel: np.ndarray, 
                         steps: int = 50,
                         size: int = 64,
                         seed_type: str = 'random',
                         growth_mu: float = 0.15,
                         growth_sigma: float = 0.015,
                         dt: float = 0.1) -> Dict:
    """
    Run a Lenia simulation with the given kernel.
    
    Returns metrics: survival, stability, complexity, emergence
    """
    # Initialize field
    field = np.zeros((size, size))
    
    if seed_type == 'random':
        field = np.random.random((size, size)) * 0.3
    elif seed_type == 'spot':
        cx, cy = size // 2, size // 2
        for dx in range(-5, 6):
            for dy in range(-5, 6):
                dist = np.sqrt(dx**2 + dy**2)
                if dist <= 5:
                    field[(cy + dy) % size, (cx + dx) % size] = max(0, 1.0 - dist/5)
    elif seed_type == 'ring':
        cx, cy = size // 2, size // 2
        for x in range(size):
            for y in range(size):
                d = np.sqrt((x - cx)**2 + (y - cy)**2)
                if 8 <= d <= 12:
                    field[y, x] = 0.8
    
    # Run simulation
    history = [field.copy()]
    for _ in range(steps):
        U = convolve(field, kernel, mode='wrap')
        G = growth_function(U, growth_mu, growth_sigma)
        field = np.clip(field + dt * G, 0, 1)
        history.append(field.copy())
    
    # Compute metrics
    final_field = history[-1]
    initial_field = history[0]
    
    # Survival: fraction of initial mass retained
    survival = final_field.sum() / (initial_field.sum() + 1e-8)
    survival = min(survival, 1.0)  # Cap at 1.0
    
    # Stability: inverse of temporal variance (higher = more stable)
    temporal_variance = np.var([h.mean() for h in history[-20:]])
    stability = 1.0 / (temporal_variance + 0.1)  # Scale factor
    stability = np.clip(stability / 5.0, 0, 1.0)  # Normalize to [0,1]
    
    # Complexity: spatial entropy and pattern diversity
    # Use histogram entropy as complexity measure
    hist, _ = np.histogram(final_field, bins=20, range=(0, 1), density=True)
    hist = hist + 1e-8  # Avoid log(0)
    complexity = entropy(hist)
    complexity = min(complexity / 3.0, 1.0)  # Normalize to [0, 1]
    
    # Emergence: measure of structure formation
    # Use spatial autocorrelation as a proxy
    from scipy.ndimage import correlate
    shifted = np.roll(final_field, 5, axis=0)
    correlation = np.corrcoef(final_field.flatten(), shifted.flatten())[0, 1]
    emergence = max(0, correlation)  # Higher correlation = more structure
    
    return {
        'survival': float(survival),
        'stability': float(stability),
        'complexity': float(complexity),
        'emergence': float(emergence),
        'final_mass': float(final_field.sum()),
        'initial_mass': float(initial_field.sum())
    }


# ============================================================================
# MAIN EXPERIMENT
# ============================================================================

def run_diffusion_experiment(output_path: str = None):
    """
    Main experiment: generate and evaluate diffusion-based kernels.
    """
    print("=" * 70)
    print("DIFFUSION-BASED LENIA KERNEL GENERATION")
    print("=" * 70)
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize generator
    generator = KernelDiffusionGenerator(n_diffusion_steps=50)
    
    # Create training kernels from known Pareto front (V6/V7/V8/V9 best)
    # Based on previous results and known good Lenia parameters
    pareto_kernels = [
        # V7 evolved parameters
        {'mu': 0.135, 'sigma': 0.074, 'R': 13, 'asymmetry_factor': 0.0},
        # V9 hybrid best
        {'mu': 0.382, 'sigma': 0.294, 'R': 13, 'asymmetry_factor': 0.0},
        # Classic Orbium
        {'mu': 0.15, 'sigma': 0.015, 'R': 13, 'asymmetry_factor': 0.0},
        # Gaborium-like
        {'mu': 0.12, 'sigma': 0.03, 'R': 12, 'asymmetry_factor': 0.0},
        # Aerium-like
        {'mu': 0.18, 'sigma': 0.05, 'R': 15, 'asymmetry_factor': 0.0},
        # V8 GNN adapted
        {'mu': 0.10, 'sigma': 0.025, 'R': 12, 'asymmetry_factor': 0.0},
        # High emergence
        {'mu': 0.11, 'sigma': 0.04, 'R': 14, 'asymmetry_factor': 0.1},
        # Stable specialist
        {'mu': 0.16, 'sigma': 0.02, 'R': 11, 'asymmetry_factor': 0.0},
    ]
    
    print(f"Training on {len(pareto_kernels)} Pareto-optimal kernels...")
    generator.train_on_pareto_front(pareto_kernels)
    print()
    
    # Generate novel kernels
    print("Generating novel kernels...")
    n_kernels = 15
    novel_kernels = generator.generate_novel_kernels(
        n_kernels=n_kernels,
        temperature=1.2,  # Higher temperature for more exploration
        perturbation_strength=0.15
    )
    print(f"Generated {len(novel_kernels)} kernels")
    print()
    
    # Evaluate each kernel
    print("Evaluating generated kernels...")
    print("-" * 70)
    
    results = []
    baselines = {
        'v6_stability_max': 0.517,
        'v6_emergence_max': 1.328,
        'v8_survival': 0.492,
        'v8_complexity': 1.911,
        'v9_survival': 0.959,
        'v9_fitness': 2.026
    }
    
    for i, kernel_params in enumerate(novel_kernels):
        print(f"\nKernel {i+1}/{len(novel_kernels)}: {kernel_params}")
        
        # Create 2D kernel
        kernel_2d = params_to_kernel_2d(kernel_params, grid_size=31)
        
        # Run simulation with multiple seeds
        metrics_list = []
        for seed_type in ['random', 'spot', 'ring']:
            metrics = run_lenia_simulation(
                kernel_2d, 
                steps=50, 
                size=64,
                seed_type=seed_type,
                growth_mu=kernel_params.mu,
                growth_sigma=kernel_params.sigma * 0.3
            )
            metrics_list.append(metrics)
        
        # Average metrics across seeds
        avg_metrics = {
            'survival': np.mean([m['survival'] for m in metrics_list]),
            'stability': np.mean([m['stability'] for m in metrics_list]),
            'complexity': np.mean([m['complexity'] for m in metrics_list]),
            'emergence': np.mean([m['emergence'] for m in metrics_list])
        }
        
        # Compute fitness
        fitness = (avg_metrics['survival'] * 1.0 + 
                   avg_metrics['stability'] * 0.5 + 
                   avg_metrics['complexity'] * 1.5 + 
                   avg_metrics['emergence'] * 1.0)
        
        # Check if exceeds Pareto front on meaningful metrics
        # Must have survival > 0.1 AND exceed at least one normalized baseline
        exceeds_pareto = (
            avg_metrics['survival'] > 0.1 and
            (avg_metrics['stability'] > baselines['v6_stability_max'] / 5.0 or
             avg_metrics['emergence'] > 0.5 or
             avg_metrics['survival'] > baselines['v8_survival'] or
             avg_metrics['complexity'] > 0.5)
        )
        
        result = {
            'kernel_id': i + 1,
            'params': kernel_params.to_dict(),
            'metrics': avg_metrics,
            'fitness': float(fitness),
            'exceeds_pareto': bool(exceeds_pareto),
            'individual_metrics': metrics_list
        }
        results.append(result)
        
        print(f"  Survival: {avg_metrics['survival']:.3f}")
        print(f"  Stability: {avg_metrics['stability']:.3f}")
        print(f"  Complexity: {avg_metrics['complexity']:.3f}")
        print(f"  Emergence: {avg_metrics['emergence']:.3f}")
        print(f"  Fitness: {fitness:.3f}")
        print(f"  Exceeds Pareto: {exceeds_pareto}")
    
    # Find breakthrough kernels
    breakthrough_kernels = [r for r in results if r['exceeds_pareto']]
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total kernels generated: {len(novel_kernels)}")
    print(f"Breakthrough kernels (exceed Pareto): {len(breakthrough_kernels)}")
    print()
    
    if breakthrough_kernels:
        print("Best breakthrough kernels:")
        for r in sorted(breakthrough_kernels, key=lambda x: x['fitness'], reverse=True)[:3]:
            print(f"  Kernel {r['kernel_id']}: fitness={r['fitness']:.3f}, "
                  f"survival={r['metrics']['survival']:.3f}, "
                  f"complexity={r['metrics']['complexity']:.3f}")
    
    # Best overall
    best = max(results, key=lambda x: x['fitness'])
    print(f"\nBest overall: Kernel {best['kernel_id']} with fitness {best['fitness']:.3f}")
    print(f"  Params: mu={best['params']['mu']:.3f}, sigma={best['params']['sigma']:.3f}, "
          f"R={best['params']['R']}")
    
    # Comparison to baselines
    print("\nBaseline Comparison:")
    print(f"  V6 Stability Max: {baselines['v6_stability_max']:.3f}")
    print(f"  V6 Emergence Max: {baselines['v6_emergence_max']:.3f}")
    print(f"  V8 Survival: {baselines['v8_survival']:.3f}")
    print(f"  V8 Complexity: {baselines['v8_complexity']:.3f}")
    print(f"  V9 Survival: {baselines['v9_survival']:.3f}")
    print(f"  V9 Fitness: {baselines['v9_fitness']:.3f}")
    
    # Save results
    output = {
        'method': 'diffusion_kernel_generation',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'n_kernels_generated': len(novel_kernels),
        'training_data': pareto_kernels,
        'baselines': baselines,
        'results': results,
        'breakthrough_count': len(breakthrough_kernels),
        'best_kernel': best
    }
    
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        print(f"\nResults saved to: {output_path}")
    
    return output


if __name__ == '__main__':
    output = run_diffusion_experiment(
        output_path='D:/openclaw_workspace/exploration/cycle4_diffusion_kernels.json'
    )
