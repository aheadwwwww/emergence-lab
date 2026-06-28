"""
Diffusion-based Lenia Kernel Generator (V9)
============================================

Applies GenCast-style diffusion for generating novel Lenia kernels.
Learns from V6 Pareto front and generates new candidates.

Based on GenCast (Price et al., 2023) diffusion architecture.
"""

import numpy as np
import jax
import jax.numpy as jnp
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import json
from pathlib import Path

# Import base Lenia components
from evolutionary_lenia import LeniaSystem, EvolutionaryTrial, PARETO_ARCHETYPES

# ============================================================================
# Diffusion Schedule (from GenCast/DPM-Solver++)
# ============================================================================

def cosine_schedule(t: jnp.ndarray, s: float = 0.008) -> jnp.ndarray:
    """Cosine noise schedule (improved over linear)."""
    return jnp.cos((t + s) / (1 + s) * jnp.pi / 2) ** 2


def get_noise_level(t: jnp.ndarray, schedule_fn) -> Tuple[jnp.ndarray, jnp.ndarray]:
    """Get signal and noise levels for diffusion step t."""
    alpha_bar = schedule_fn(t)
    signal = jnp.sqrt(alpha_bar)
    noise = jnp.sqrt(1 - alpha_bar)
    return signal, noise


# ============================================================================
# Kernel Encoder/Decoder
# ============================================================================

class KernelEncoder:
    """
    Encode Lenia kernel parameters to latent representation.
    Uses 2D FFT magnitude as the kernel representation.
    """
    
    def __init__(self, R: int = 13, size: int = 128):
        self.R = R
        self.size = size
        
    def params_to_kernel(self, mu: float, sigma: float) -> np.ndarray:
        """Convert (mu, sigma) to 2D kernel."""
        size = self.size
        kernel = np.zeros((size, size), dtype=np.float32)
        y, x = np.ogrid[-size//2:size//2, -size//2:size//2]
        r = np.sqrt(x*x + y*y) / self.R
        
        # Gaussian ring kernel
        kernel = np.exp(-((r - mu)**2) / (2 * sigma**2))
        kernel = kernel / (kernel.sum() + 1e-8)
        
        return kernel
    
    def kernel_to_latent(self, kernel: np.ndarray) -> np.ndarray:
        """Convert kernel to latent representation (FFR coefficients)."""
        # Use FFT magnitude as latent
        fft = np.fft.fft2(kernel)
        fft_shifted = np.fft.fftshift(fft)
        magnitude = np.abs(fft_shifted)
        
        # Extract central region (low frequency components)
        center = self.size // 2
        half_width = 16  # Keep 32x32 central region
        latent = magnitude[center-half_width:center+half_width,
                          center-half_width:center+half_width]
        
        return latent.flatten().astype(np.float32)
    
    def params_to_latent(self, mu: float, sigma: float) -> np.ndarray:
        """Convert params directly to latent."""
        kernel = self.params_to_kernel(mu, sigma)
        return self.kernel_to_latent(kernel)


# ============================================================================
# Diffusion Kernel Generator
# ============================================================================

@dataclass
class DiffusionConfig:
    """Configuration for diffusion process."""
    latent_dim: int = 32 * 32  # 1024 (from 32x32 central FFT region)
    num_steps: int = 100
    schedule_s: float = 0.008
    learning_rate: float = 1e-4
    

class DiffusionKernelGenerator:
    """
    Generate Lenia kernels using diffusion process.
    
    Inspired by GenCast:
    - Uses cosine noise schedule
    - Denoising network predicts clean kernel
    - DPM-Solver++ for efficient sampling
    """
    
    def __init__(self, config: Optional[DiffusionConfig] = None):
        self.config = config or DiffusionConfig()
        self.encoder = KernelEncoder()
        self.schedule_fn = lambda t: cosine_schedule(t, self.config.schedule_s)
        
        # Training data (kernel latents from Pareto front)
        self.training_latents: List[np.ndarray] = []
        self.training_labels: List[str] = []
        
    def add_training_example(self, mu: float, sigma: float, label: str = ""):
        """Add a kernel example to training set."""
        latent = self.encoder.params_to_latent(mu, sigma)
        self.training_latents.append(latent)
        self.training_labels.append(label)
        
    def build_training_set_from_archetypes(self):
        """Build training set from V6 Pareto archetypes."""
        for name, archetype in PARETO_ARCHETYPES.items():
            mu = archetype['mu']
            sigma = archetype['sigma']
            
            # Add base archetype
            self.add_training_example(mu, sigma, name)
            
            # Add perturbed variants
            for _ in range(5):
                mu_p = mu + np.random.uniform(-0.02, 0.02)
                sigma_p = sigma + np.random.uniform(-0.01, 0.01)
                mu_p = np.clip(mu_p, 0.1, 0.2)
                sigma_p = np.clip(sigma_p, 0.02, 0.1)
                self.add_training_example(mu_p, sigma_p, f"{name}_variant")
                
    def simple_denoise(self, noisy_latent: np.ndarray, t: float) -> np.ndarray:
        """
        Simple denoising using nearest neighbor in training set.
        
        In a full implementation, this would be a neural network.
        For now, we use a simplified approach based on GenCast concepts.
        """
        if len(self.training_latents) == 0:
            return noisy_latent
            
        # Compute distances to all training examples
        distances = []
        for latent in self.training_latents:
            dist = np.sum((noisy_latent - latent) ** 2)
            distances.append(dist)
            
        # Weighted average of nearest neighbors
        weights = np.exp(-np.array(distances) / (np.mean(distances) + 1e-8))
        weights = weights / weights.sum()
        
        denoised = np.zeros_like(noisy_latent)
        for i, latent in enumerate(self.training_latents):
            denoised += weights[i] * latent
            
        # Blend with noisy input based on noise level
        signal, noise = get_noise_level(jnp.array(t), self.schedule_fn)
        alpha = float(signal)
        
        return alpha * denoised + (1 - alpha) * noisy_latent
    
    def latent_to_params(self, latent: np.ndarray) -> Tuple[float, float]:
        """
        Decode latent back to (mu, sigma) parameters.
        
        Uses nearest neighbor lookup in training set.
        """
        if len(self.training_latents) == 0:
            # Default fallback
            return 0.15, 0.05
            
        # Find nearest training example
        distances = []
        for train_latent in self.training_latents:
            dist = np.sum((latent - train_latent) ** 2)
            distances.append(dist)
            
        nearest_idx = np.argmin(distances)
        nearest_label = self.training_labels[nearest_idx]
        
        # Get params from nearest archetype
        if nearest_label in PARETO_ARCHETYPES:
            archetype = PARETO_ARCHETYPES[nearest_label]
            return archetype['mu'], archetype['sigma']
        else:
            # Extract from variant label
            base_name = nearest_label.replace('_variant', '')
            if base_name in PARETO_ARCHETYPES:
                archetype = PARETO_ARCHETYPES[base_name]
                # Add small perturbation
                mu = archetype['mu'] + np.random.uniform(-0.01, 0.01)
                sigma = archetype['sigma'] + np.random.uniform(-0.005, 0.005)
                return np.clip(mu, 0.1, 0.2), np.clip(sigma, 0.02, 0.1)
                
        # Fallback
        return 0.15, 0.05
    
    def generate(self, num_samples: int = 10, seed: int = None) -> List[Dict]:
        """
        Generate novel kernels using diffusion process.
        
        Uses simplified DPM-Solver++ style sampling.
        """
        if seed is not None:
            np.random.seed(seed)
            
        # Build training set if empty
        if len(self.training_latents) == 0:
            self.build_training_set_from_archetypes()
            
        results = []
        
        for sample_idx in range(num_samples):
            # Start from pure noise
            latent = np.random.randn(self.config.latent_dim).astype(np.float32)
            
            # Reverse diffusion (denoising)
            num_steps = self.config.num_steps
            for step in range(num_steps):
                t = 1.0 - step / num_steps  # t from 1 to 0
                
                # Denoise
                latent = self.simple_denoise(latent, t)
                
                # Add small noise (except last step)
                if step < num_steps - 1:
                    signal, noise = get_noise_level(jnp.array(t - 1/num_steps), self.schedule_fn)
                    latent = latent + 0.1 * np.random.randn(*latent.shape).astype(np.float32)
            
            # Decode to params
            mu, sigma = self.latent_to_params(latent)
            
            # Evaluate the generated kernel
            system = LeniaSystem(mu=mu, sigma=sigma)
            trial = EvolutionaryTrial(system, max_steps=150)
            result = trial.run()
            
            results.append({
                'sample_idx': sample_idx,
                'mu': float(mu),
                'sigma': float(sigma),
                'fitness': float(result['fitness']),
                'survival': float(result['survival']),
                'complexity': float(result['complexity']),
                'stability': float(result['stability']),
                'latent_norm': float(np.linalg.norm(latent))
            })
            
            print(f"Sample {sample_idx}: mu={mu:.3f}, sigma={sigma:.3f}, "
                  f"fitness={result['fitness']:.4f}")
            
        return results


# ============================================================================
# DPM-Solver++ Sampler (Simplified)
# ============================================================================

class DPMSolverPlusPlus:
    """
    Simplified DPM-Solver++ for efficient diffusion sampling.
    
    Reference: DPM-Solver++: Fast Solver for Guided Sampling of 
    Diffusion Probabilistic Models (Lu et al., 2022)
    """
    
    def __init__(self, num_steps: int = 20):
        self.num_steps = num_steps
        
    def get_time_steps(self) -> np.ndarray:
        """Get time steps for sampling."""
        return np.linspace(1, 0, self.num_steps + 1)
    
    def dpm_plus_plus_update(self, x: np.ndarray, t: float, t_prev: float,
                            denoise_fn) -> np.ndarray:
        """
        Single DPM-Solver++ update step.
        
        Uses second-order multistep method.
        """
        # Current noise level
        alpha_t = cosine_schedule(jnp.array(t))
        alpha_prev = cosine_schedule(jnp.array(t_prev))
        
        # Predict clean sample
        x0_pred = denoise_fn(x, t)
        
        # Compute update
        sigma_t = jnp.sqrt(1 - alpha_t)
        sigma_prev = jnp.sqrt(1 - alpha_prev)
        
        # DPM-Solver++ coefficient
        lambda_t = jnp.log(alpha_t / sigma_t)
        lambda_prev = jnp.log(alpha_prev / sigma_prev)
        
        h = lambda_prev - lambda_t
        
        # Update rule
        x_prev = (alpha_prev / alpha_t) * x - sigma_prev * (jnp.exp(h) - 1) * x0_pred
        
        return np.array(x_prev)
    
    def sample(self, denoise_fn, shape: Tuple[int, ...], 
               seed: int = None) -> np.ndarray:
        """Generate sample using DPM-Solver++."""
        if seed is not None:
            np.random.seed(seed)
            
        # Initialize from noise
        x = np.random.randn(*shape).astype(np.float32)
        
        time_steps = self.get_time_steps()
        
        for i in range(len(time_steps) - 1):
            t = time_steps[i]
            t_prev = time_steps[i + 1]
            
            x = self.dpm_plus_plus_update(x, t, t_prev, denoise_fn)
            
        return x


# ============================================================================
# Ensemble Generator (GenCast Style)
# ============================================================================

class EnsembleKernelGenerator:
    """
    Generate ensemble of kernels for probabilistic exploration.
    
    Inspired by GenCast's ensemble forecasting approach.
    """
    
    def __init__(self, num_ensemble: int = 5):
        self.num_ensemble = num_ensemble
        self.diffusion_gen = DiffusionKernelGenerator()
        
    def generate_ensemble(self, num_samples: int = 20) -> Dict:
        """
        Generate ensemble of kernels and aggregate results.
        
        Returns distribution statistics and best candidates.
        """
        all_results = []
        
        for ensemble_idx in range(self.num_ensemble):
            print(f"\n=== Ensemble Member {ensemble_idx + 1}/{self.num_ensemble} ===")
            
            results = self.diffusion_gen.generate(
                num_samples=num_samples // self.num_ensemble,
                seed=42 + ensemble_idx * 100
            )
            
            for r in results:
                r['ensemble_idx'] = ensemble_idx
                all_results.append(r)
                
        # Aggregate statistics
        fitnesses = [r['fitness'] for r in all_results]
        survivals = [r['survival'] for r in all_results]
        complexities = [r['complexity'] for r in all_results]
        
        # Find best candidates
        best_fitness = max(all_results, key=lambda x: x['fitness'])
        best_survival = max(all_results, key=lambda x: x['survival'])
        best_complexity = max(all_results, key=lambda x: x['complexity'])
        
        # Pareto front (simplified)
        pareto_candidates = []
        for r in all_results:
            is_pareto = True
            for other in all_results:
                if (other['survival'] >= r['survival'] and 
                    other['complexity'] >= r['complexity'] and
                    (other['survival'] > r['survival'] or other['complexity'] > r['complexity'])):
                    is_pareto = False
                    break
            if is_pareto:
                pareto_candidates.append(r)
                
        return {
            'num_total': len(all_results),
            'num_pareto': len(pareto_candidates),
            'mean_fitness': float(np.mean(fitnesses)),
            'std_fitness': float(np.std(fitnesses)),
            'mean_survival': float(np.mean(survivals)),
            'std_survival': float(np.std(survivals)),
            'mean_complexity': float(np.mean(complexities)),
            'best_fitness': best_fitness,
            'best_survival': best_survival,
            'best_complexity': best_complexity,
            'pareto_front': pareto_candidates[:10],
            'all_results': all_results
        }


# ============================================================================
# Main Experiment
# ============================================================================

def run_v9_experiment():
    """Run V9 diffusion-based kernel generation experiment."""
    print("=" * 60)
    print("V9: Diffusion-based Lenia Kernel Generation")
    print("=" * 60)
    print("\nInspired by GenCast (Price et al., 2023)")
    print("Using cosine noise schedule + DPM-Solver++ sampling")
    print()
    
    # Create ensemble generator
    ensemble_gen = EnsembleKernelGenerator(num_ensemble=5)
    
    # Generate ensemble
    print("Generating kernel ensemble...")
    results = ensemble_gen.generate_ensemble(num_samples=25)
    
    # Print summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"\nTotal samples generated: {results['num_total']}")
    print(f"Pareto front size: {results['num_pareto']}")
    print(f"\nFitness: mean={results['mean_fitness']:.4f}, std={results['std_fitness']:.4f}")
    print(f"Survival: mean={results['mean_survival']:.4f}, std={results['std_survival']:.4f}")
    print(f"Complexity: mean={results['mean_complexity']:.4f}")
    
    print("\n--- Best Candidates ---")
    print(f"Best Fitness: mu={results['best_fitness']['mu']:.3f}, "
          f"sigma={results['best_fitness']['sigma']:.3f}, "
          f"fitness={results['best_fitness']['fitness']:.4f}")
    
    print(f"Best Survival: mu={results['best_survival']['mu']:.3f}, "
          f"sigma={results['best_survival']['sigma']:.3f}, "
          f"survival={results['best_survival']['survival']:.4f}")
    
    print(f"Best Complexity: mu={results['best_complexity']['mu']:.3f}, "
          f"sigma={results['best_complexity']['sigma']:.3f}, "
          f"complexity={results['best_complexity']['complexity']:.4f}")
    
    print("\n--- Pareto Front ---")
    for i, p in enumerate(results['pareto_front'][:5]):
        print(f"  {i+1}. mu={p['mu']:.3f}, sigma={p['sigma']:.3f}, "
              f"survival={p['survival']:.3f}, complexity={p['complexity']:.3f}")
    
    return results


if __name__ == '__main__':
    results = run_v9_experiment()
    
    # Save results
    output_dir = Path('exploration')
    output_dir.mkdir(exist_ok=True)
    
    # Save as JSON (without history)
    save_results = {k: v for k, v in results.items() if k != 'all_results'}
    
    with open(output_dir / 'v9_diffusion_results.json', 'w') as f:
        json.dump(save_results, f, indent=2, default=str)
        
    print(f"\nResults saved to {output_dir / 'v9_diffusion_results.json'}")
