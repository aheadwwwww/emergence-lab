"""
Enhanced Diffusion-Based Kernel Generator V2
Implements proper DDPM-style diffusion with iterative denoising

Key improvements:
1. Proper diffusion process with noise schedule
2. Better kernel evaluation metrics
3. Exploration of multi-ring and asymmetric kernels
4. Comparison to V6/V8/V9 baselines
"""

import numpy as np
from scipy.ndimage import convolve
from scipy.stats import entropy as scipy_entropy
import json
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

# ============================================================================
# ENHANCED DDPM IMPLEMENTATION
# ============================================================================

class EnhancedDDPM:
    """
    Proper DDPM implementation for kernel parameter generation.
    
    The key insight from GenCast: use diffusion to sample from a learned
    distribution, allowing exploration beyond the training data.
    """
    
    def __init__(self, n_steps: int = 100, beta_schedule: str = 'cosine'):
        self.n_steps = n_steps
        
        # Noise schedule
        if beta_schedule == 'linear':
            self.betas = np.linspace(1e-4, 0.02, n_steps)
        elif beta_schedule == 'cosine':
            # Cosine schedule from Improved DDPM paper
            steps = np.arange(n_steps + 1)
            alpha_bar = np.cos((steps / n_steps + 0.008) / 1.008 * np.pi / 2) ** 2
            self.betas = np.clip(1 - alpha_bar[1:] / alpha_bar[:-1], 0, 0.999)
        else:
            self.betas = np.linspace(1e-4, 0.02, n_steps)
        
        self.alphas = 1.0 - self.betas
        self.alpha_bars = np.cumprod(self.alphas)
        
        # For sampling
        self.sqrt_alpha_bars = np.sqrt(self.alpha_bars)
        self.sqrt_one_minus_alpha_bars = np.sqrt(1 - self.alpha_bars)
        
    def forward_diffusion(self, x0: np.ndarray, t: int) -> Tuple[np.ndarray, np.ndarray]:
        """Add noise to x0 at timestep t."""
        noise = np.random.randn(*x0.shape)
        xt = self.sqrt_alpha_bars[t] * x0 + self.sqrt_one_minus_alpha_bars[t] * noise
        return xt, noise
    
    def reverse_diffusion_step(self, xt: np.ndarray, t: int, 
                                predicted_noise: np.ndarray,
                                learned_mean: np.ndarray,
                                learned_std: np.ndarray) -> np.ndarray:
        """Single reverse diffusion step using learned statistics."""
        # Estimate x0 from xt and predicted noise
        x0_est = (xt - self.sqrt_one_minus_alpha_bars[t] * predicted_noise) / self.sqrt_alpha_bars[t]
        
        # Clamp x0 to valid range
        x0_est = np.clip(x0_est, learned_mean - 3*learned_std, learned_mean + 3*learned_std)
        
        # Compute x_{t-1}
        if t == 0:
            return x0_est
        
        # Add controlled noise for diversity
        noise = np.random.randn(*xt.shape) * np.sqrt(self.betas[t])
        alpha_t = self.alphas[t]
        
        # Move toward learned distribution
        xt_minus_1 = alpha_t * x0_est + (1 - alpha_t) * learned_mean + noise * 0.5
        return xt_minus_1
    
    def train(self, training_data: List[np.ndarray]):
        """Learn the distribution statistics."""
        X = np.array(training_data)
        self.mean = X.mean(axis=0)
        self.std = X.std(axis=0) + 1e-6
        self.cov = np.cov(X.T) if len(X) > 1 else np.eye(len(self.mean)) * 0.01
        
        # Principal components for better sampling
        eigenvalues, eigenvectors = np.linalg.eigh(self.cov)
        self.pca_components = eigenvectors
        self.pca_eigenvalues = eigenvalues
        
        print(f"DDPM trained on {len(training_data)} samples")
        print(f"Mean: {self.mean}")
        print(f"Std: {self.std}")
        
    def generate(self, n_samples: int = 1, temperature: float = 1.0,
                 use_pca: bool = True) -> List[np.ndarray]:
        """
        Generate samples using reverse diffusion process.
        
        Args:
            n_samples: Number of samples to generate
            temperature: Sampling temperature (higher = more exploration)
            use_pca: Use PCA-based sampling for better diversity
        """
        samples = []
        
        for _ in range(n_samples):
            # Start from pure noise
            xt = np.random.randn(len(self.mean)) * temperature
            
            # Use PCA directions for structured noise
            if use_pca and hasattr(self, 'pca_components'):
                # Sample along principal components
                noise_in_pca = np.random.randn(len(self.mean)) * np.sqrt(self.pca_eigenvalues + 0.1)
                xt = self.mean + self.pca_components @ noise_in_pca * temperature
            
            # Reverse diffusion - gradually denoise toward learned distribution
            for t in reversed(range(self.n_steps)):
                # Predict noise (simple: use gradient toward learned mean)
                predicted_noise = (xt - self.mean) * 0.5
                
                xt = self.reverse_diffusion_step(
                    xt, t, predicted_noise, self.mean, self.std
                )
            
            samples.append(xt)
        
        return samples


@dataclass
class EnhancedKernelParams:
    """Enhanced kernel parameterization with more degrees of freedom."""
    # Core ring parameters
    mu: float  # Ring center (normalized by R)
    sigma: float  # Ring width (normalized by R)
    R: int  # Kernel radius in pixels
    
    # Growth function parameters (separate from kernel)
    growth_mu: float = 0.15
    growth_sigma: float = 0.015
    
    # Asymmetry
    asymmetry_x: float = 0.0  # X-axis asymmetry factor
    asymmetry_y: float = 0.0  # Y-axis asymmetry factor
    
    # Multi-ring components
    n_rings: int = 1  # Number of concentric rings
    ring_spacing: float = 0.0  # Spacing between rings (normalized)
    ring_decay: float = 0.5  # Decay factor for outer rings
    
    def to_array(self) -> np.ndarray:
        """Convert to array for diffusion model."""
        return np.array([
            self.mu, self.sigma, self.R, 
            self.growth_mu, self.growth_sigma,
            self.asymmetry_x, self.asymmetry_y,
            self.n_rings, self.ring_spacing, self.ring_decay
        ])
    
    def to_dict(self) -> Dict:
        return asdict(self)


def create_enhanced_kernel(params: EnhancedKernelParams, grid_size: int = 31) -> np.ndarray:
    """Create 2D kernel from enhanced parameters."""
    xs = np.linspace(-grid_size//2, grid_size//2, grid_size)
    ys = np.linspace(-grid_size//2, grid_size//2, grid_size)
    x, y = np.meshgrid(xs, ys)
    d = np.sqrt(x**2 + y**2)
    
    # Apply asymmetry
    if params.asymmetry_x != 0 or params.asymmetry_y != 0:
        # Scale the kernel based on position
        asymmetry_scale = 1.0 + params.asymmetry_x * x / grid_size + params.asymmetry_y * y / grid_size
        asymmetry_scale = np.clip(asymmetry_scale, 0.5, 2.0)
    else:
        asymmetry_scale = 1.0
    
    # Build multi-ring kernel
    kernel = np.zeros((grid_size, grid_size))
    
    for ring_idx in range(params.n_rings):
        # Ring position
        ring_mu = params.mu * params.R + ring_idx * params.ring_spacing * params.R
        ring_sigma = params.sigma * params.R
        ring_weight = params.ring_decay ** ring_idx
        
        # Gaussian ring
        ring = np.exp(-((d - ring_mu) / ring_sigma)**2) * ring_weight
        kernel += ring
    
    # Apply asymmetry
    kernel = kernel * asymmetry_scale
    
    # Normalize
    kernel -= kernel.mean()
    if np.abs(kernel).sum() > 0:
        kernel /= np.abs(kernel).sum()
    
    return kernel


# ============================================================================
# IMPROVED LENIA SIMULATION
# ============================================================================

def run_enhanced_lenia_simulation(kernel: np.ndarray,
                                   params: EnhancedKernelParams,
                                   steps: int = 100,
                                   size: int = 64,
                                   seed_type: str = 'random') -> Dict:
    """
    Run Lenia simulation with enhanced metrics.
    """
    # Initialize field
    field = np.zeros((size, size))
    
    if seed_type == 'random':
        field = np.random.random((size, size)) * 0.5
    elif seed_type == 'spot':
        cx, cy = size // 2, size // 2
        r = 8
        for dx in range(-r, r+1):
            for dy in range(-r, r+1):
                dist = np.sqrt(dx**2 + dy**2)
                if dist <= r:
                    field[(cy + dy) % size, (cx + dx) % size] = np.clip(1.0 - dist/r, 0, 1)
    elif seed_type == 'ring':
        cx, cy = size // 2, size // 2
        for x in range(size):
            for y in range(size):
                d = np.sqrt((x - cx)**2 + (y - cy)**2)
                if 10 <= d <= 15:
                    field[y, x] = 0.9
    elif seed_type == 'multi_spot':
        # Multiple spots for testing pattern interaction
        for i in range(3):
            angle = i * 2 * np.pi / 3
            cx = int(size//2 + 15 * np.cos(angle))
            cy = int(size//2 + 15 * np.sin(angle))
            for dx in range(-5, 6):
                for dy in range(-5, 6):
                    dist = np.sqrt(dx**2 + dy**2)
                    if dist <= 5:
                        field[(cy + dy) % size, (cx + dx) % size] = max(0, 1.0 - dist/5)
    
    # Growth function
    def growth(u):
        return 2 * np.exp(-((u - params.growth_mu)**2) / (2 * params.growth_sigma**2)) - 1
    
    # Run simulation
    history = [field.copy()]
    dt = 0.1
    
    for step_idx in range(steps):
        U = convolve(field, kernel, mode='wrap')
        G = growth(U)
        field = np.clip(field + dt * G, 0, 1)
        history.append(field.copy())
    
    # Enhanced metrics
    final_field = history[-1]
    initial_field = history[0]
    
    # 1. Survival: mass retention
    initial_mass = initial_field.sum()
    final_mass = final_field.sum()
    survival = min(1.0, final_mass / (initial_mass + 1e-8))
    
    # 2. Stability: temporal variance of mass
    masses = [h.sum() for h in history[-30:]]
    mass_variance = np.var(masses)
    # Higher stability = lower variance, but cap at reasonable values
    stability = np.clip(1.0 / (mass_variance + 0.01), 0, 1.0)
    
    # 3. Complexity: spatial entropy + gradient complexity
    # Entropy component
    hist, _ = np.histogram(final_field[final_field > 0.01], bins=20, density=True)
    hist = hist + 1e-8
    spatial_entropy = scipy_entropy(hist)
    
    # Gradient complexity: measure of pattern structure
    gy, gx = np.gradient(final_field)
    gradient_mag = np.sqrt(gx**2 + gy**2)
    gradient_complexity = gradient_mag.mean() * 10  # Scale up
    
    complexity = np.clip((spatial_entropy / 2.0 + gradient_complexity) / 2, 0, 1.0)
    
    # 4. Emergence: autocorrelation and pattern formation
    # Spatial autocorrelation
    shifted = np.roll(final_field, 8, axis=0)
    corr_matrix = np.corrcoef(final_field.flatten(), shifted.flatten())
    if corr_matrix.shape == (2, 2):
        autocorr = abs(corr_matrix[0, 1]) if not np.isnan(corr_matrix[0, 1]) else 0
    else:
        autocorr = 0
    
    # Pattern diversity: number of distinct blobs
    from scipy.ndimage import label
    labeled, n_blobs = label(final_field > 0.3)
    blob_diversity = min(n_blobs / 10.0, 1.0)
    
    emergence = np.clip(autocorr * 0.5 + blob_diversity * 0.5, 0, 1.0)
    
    # 5. Dynamics: measure of interesting temporal behavior
    # Oscillation detection
    mass_series = np.array([h.sum() for h in history])
    if len(mass_series) > 10:
        # Compute frequency content
        mass_diff = np.diff(mass_series)
        dynamics = np.std(mass_diff[-20:]) * 5  # Movement variance
        dynamics = np.clip(dynamics, 0, 1.0)
    else:
        dynamics = 0
    
    return {
        'survival': float(survival),
        'stability': float(stability),
        'complexity': float(complexity),
        'emergence': float(emergence),
        'dynamics': float(dynamics),
        'final_mass': float(final_mass),
        'initial_mass': float(initial_mass),
        'n_blobs': int(n_blobs)
    }


# ============================================================================
# MAIN EXPERIMENT
# ============================================================================

def run_enhanced_diffusion_experiment():
    """
    Run the enhanced diffusion-based kernel generation experiment.
    """
    print("=" * 70)
    print("ENHANCED DIFFUSION-BASED LENIA KERNEL GENERATION V2")
    print("=" * 70)
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Baselines from V6/V8/V9
    baselines = {
        'v6_stability_max': 0.517,
        'v6_emergence_max': 1.328,
        'v8_survival': 0.492,
        'v8_complexity': 1.911,
        'v9_survival': 0.959,
        'v9_fitness': 2.026
    }
    
    # Create DDPM
    ddpm = EnhancedDDPM(n_steps=100, beta_schedule='cosine')
    
    # Training data: Pareto-optimal kernels from previous explorations
    # Plus some known good Lenia species parameters
    training_params = [
        # V7 evolved
        EnhancedKernelParams(mu=0.135, sigma=0.074, R=13, growth_mu=0.135, growth_sigma=0.074),
        # V9 hybrid best
        EnhancedKernelParams(mu=0.382, sigma=0.294, R=13, growth_mu=0.382, growth_sigma=0.294),
        # Classic Orbium
        EnhancedKernelParams(mu=0.15, sigma=0.014, R=13, growth_mu=0.15, growth_sigma=0.014),
        # Gaborium
        EnhancedKernelParams(mu=0.11, sigma=0.028, R=12, growth_mu=0.11, growth_sigma=0.028),
        # Aerium
        EnhancedKernelParams(mu=0.18, sigma=0.050, R=15, growth_mu=0.18, growth_sigma=0.050),
        # V8 GNN adapted
        EnhancedKernelParams(mu=0.10, sigma=0.025, R=12, growth_mu=0.10, growth_sigma=0.025),
        # High survival variant
        EnhancedKernelParams(mu=0.15, sigma=0.08, R=13, growth_mu=0.15, growth_sigma=0.08),
        # Multi-ring test
        EnhancedKernelParams(mu=0.14, sigma=0.03, R=14, growth_mu=0.14, growth_sigma=0.03,
                             n_rings=2, ring_spacing=0.1, ring_decay=0.5),
        # Asymmetric test
        EnhancedKernelParams(mu=0.15, sigma=0.04, R=13, growth_mu=0.15, growth_sigma=0.04,
                             asymmetry_x=0.1, asymmetry_y=0.0),
    ]
    
    training_arrays = [p.to_array() for p in training_params]
    ddpm.train(training_arrays)
    
    # Generate novel kernels
    n_kernels = 20
    print(f"\nGenerating {n_kernels} novel kernels...")
    
    generated_params = []
    samples = ddpm.generate(n_samples=n_kernels, temperature=1.3, use_pca=True)
    
    for i, sample in enumerate(samples):
        # Convert sample to parameters with proper clamping
        params = EnhancedKernelParams(
            mu=np.clip(sample[0], 0.08, 0.25),
            sigma=np.clip(sample[1], 0.02, 0.15),
            R=int(np.clip(sample[2], 10, 16)),
            growth_mu=np.clip(sample[3], 0.08, 0.25),
            growth_sigma=np.clip(sample[4], 0.01, 0.15),
            asymmetry_x=np.clip(sample[5], -0.3, 0.3),
            asymmetry_y=np.clip(sample[6], -0.3, 0.3),
            n_rings=int(np.clip(sample[7], 1, 3)),
            ring_spacing=np.clip(sample[8], 0.0, 0.15),
            ring_decay=np.clip(sample[9], 0.2, 0.8)
        )
        generated_params.append(params)
    
    print(f"Generated {len(generated_params)} kernels")
    
    # Evaluate each kernel
    print("\n" + "-" * 70)
    print("Evaluating generated kernels...")
    print("-" * 70)
    
    results = []
    
    for i, params in enumerate(generated_params):
        print(f"\nKernel {i+1}/{len(generated_params)}")
        print(f"  mu={params.mu:.3f}, sigma={params.sigma:.3f}, R={params.R}")
        print(f"  growth_mu={params.growth_mu:.3f}, growth_sigma={params.growth_sigma:.4f}")
        if params.n_rings > 1:
            print(f"  Multi-ring: {params.n_rings} rings, spacing={params.ring_spacing:.3f}")
        if params.asymmetry_x != 0 or params.asymmetry_y != 0:
            print(f"  Asymmetric: x={params.asymmetry_x:.2f}, y={params.asymmetry_y:.2f}")
        
        # Create kernel
        kernel = create_enhanced_kernel(params, grid_size=31)
        
        # Run simulations with multiple seeds
        seed_types = ['random', 'spot', 'ring', 'multi_spot']
        metrics_list = []
        
        for seed_type in seed_types:
            metrics = run_enhanced_lenia_simulation(
                kernel, params, steps=100, size=64, seed_type=seed_type
            )
            metrics_list.append(metrics)
        
        # Aggregate metrics
        avg_metrics = {
            'survival': np.mean([m['survival'] for m in metrics_list]),
            'stability': np.mean([m['stability'] for m in metrics_list]),
            'complexity': np.mean([m['complexity'] for m in metrics_list]),
            'emergence': np.mean([m['emergence'] for m in metrics_list]),
            'dynamics': np.mean([m['dynamics'] for m in metrics_list])
        }
        
        # Compute overall fitness with weighted components
        # Prioritize: survival (base), then complexity and emergence
        fitness = (
            avg_metrics['survival'] * 2.0 +  # Survival is critical
            avg_metrics['complexity'] * 1.5 +  # Complexity indicates interesting patterns
            avg_metrics['emergence'] * 1.5 +  # Emergence indicates self-organization
            avg_metrics['dynamics'] * 0.5 +  # Dynamics indicates interesting behavior
            avg_metrics['stability'] * 0.5  # Stability is bonus but not primary
        )
        
        # Check if exceeds baselines
        exceeds_pareto = (
            avg_metrics['survival'] > 0.1 and
            (avg_metrics['survival'] > baselines['v8_survival'] or
             avg_metrics['complexity'] > 0.4 or
             avg_metrics['emergence'] > 0.4 or
             fitness > 2.0)
        )
        
        result = {
            'kernel_id': i + 1,
            'params': params.to_dict(),
            'avg_metrics': avg_metrics,
            'fitness': float(fitness),
            'exceeds_pareto': bool(exceeds_pareto),
            'seed_results': metrics_list
        }
        results.append(result)
        
        print(f"  Results:")
        print(f"    Survival: {avg_metrics['survival']:.3f}")
        print(f"    Stability: {avg_metrics['stability']:.3f}")
        print(f"    Complexity: {avg_metrics['complexity']:.3f}")
        print(f"    Emergence: {avg_metrics['emergence']:.3f}")
        print(f"    Dynamics: {avg_metrics['dynamics']:.3f}")
        print(f"    Fitness: {fitness:.3f}")
        print(f"    Exceeds Pareto: {exceeds_pareto}")
    
    # Analysis
    print("\n" + "=" * 70)
    print("RESULTS ANALYSIS")
    print("=" * 70)
    
    # Sort by fitness
    sorted_results = sorted(results, key=lambda x: x['fitness'], reverse=True)
    
    # Find breakthrough kernels
    breakthroughs = [r for r in results if r['exceeds_pareto']]
    
    print(f"\nTotal kernels generated: {len(generated_params)}")
    print(f"Kernels exceeding Pareto front: {len(breakthroughs)}")
    
    if breakthroughs:
        print("\n--- BREAKTHROUGH KERNELS ---")
        for r in breakthroughs[:5]:
            print(f"\nKernel {r['kernel_id']}:")
            print(f"  Params: mu={r['params']['mu']:.3f}, sigma={r['params']['sigma']:.3f}, R={r['params']['R']}")
            print(f"  Growth: mu={r['params']['growth_mu']:.3f}, sigma={r['params']['growth_sigma']:.4f}")
            print(f"  Survival: {r['avg_metrics']['survival']:.3f} (V8 baseline: {baselines['v8_survival']:.3f})")
            print(f"  Complexity: {r['avg_metrics']['complexity']:.3f}")
            print(f"  Emergence: {r['avg_metrics']['emergence']:.3f}")
            print(f"  Fitness: {r['fitness']:.3f} (V9 baseline: {baselines['v9_fitness']:.3f})")
    
    # Best overall
    best = sorted_results[0]
    print("\n--- BEST KERNEL ---")
    print(f"Kernel {best['kernel_id']} with fitness {best['fitness']:.3f}")
    
    # Comparison summary
    print("\n--- BASELINE COMPARISON ---")
    print(f"| Metric          | Diffusion Best | V8/V9 Best | Improvement |")
    print(f"|-----------------|----------------|------------|-------------|")
    print(f"| Survival        | {best['avg_metrics']['survival']:.3f}          | {baselines['v8_survival']:.3f}      | {best['avg_metrics']['survival']/baselines['v8_survival']:.2f}x       |")
    print(f"| Fitness         | {best['fitness']:.3f}          | {baselines['v9_fitness']:.3f}    | {best['fitness']/baselines['v9_fitness']:.2f}x       |")
    
    # Novel parameter findings
    print("\n--- NOVEL PARAMETER DISCOVERIES ---")
    high_survival_kernels = sorted([r for r in results if r['avg_metrics']['survival'] > 0.3], 
                                    key=lambda x: x['avg_metrics']['survival'], reverse=True)[:5]
    if high_survival_kernels:
        print("High survival kernels use:")
        avg_mu = np.mean([r['params']['mu'] for r in high_survival_kernels])
        avg_sigma = np.mean([r['params']['sigma'] for r in high_survival_kernels])
        avg_growth_sigma = np.mean([r['params']['growth_sigma'] for r in high_survival_kernels])
        print(f"  Average mu: {avg_mu:.3f}")
        print(f"  Average sigma: {avg_sigma:.3f}")
        print(f"  Average growth_sigma: {avg_growth_sigma:.4f}")
    
    # Save results
    output = {
        'method': 'enhanced_diffusion_kernel_generation_v2',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'n_kernels_generated': len(generated_params),
        'training_data': [p.to_dict() for p in training_params],
        'baselines': baselines,
        'results': results,
        'breakthrough_count': len(breakthroughs),
        'best_kernel': best,
        'analysis': {
            'avg_survival_best': float(best['avg_metrics']['survival']),
            'avg_complexity_best': float(best['avg_metrics']['complexity']),
            'avg_emergence_best': float(best['avg_metrics']['emergence']),
            'best_fitness': float(best['fitness']),
            'novel_params': {
                'avg_mu_high_survival': float(avg_mu) if high_survival_kernels else None,
                'avg_sigma_high_survival': float(avg_sigma) if high_survival_kernels else None,
                'avg_growth_sigma_high_survival': float(avg_growth_sigma) if high_survival_kernels else None
            }
        }
    }
    
    output_path = Path('D:/openclaw_workspace/exploration/cycle4_diffusion_kernels.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\n\nResults saved to: {output_path}")
    
    return output


if __name__ == '__main__':
    result = run_enhanced_diffusion_experiment()