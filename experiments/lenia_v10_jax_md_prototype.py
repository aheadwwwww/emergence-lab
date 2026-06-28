"""
Lenia V10 Prototype - JAX-MD Inspired Differentiable Simulation
===============================================================

Inspiration from JAX-MD:
- Differentiable molecular dynamics
- Automatic differentiation through simulation steps
- Gradient-based parameter optimization

Key Innovation:
Apply JAX-MD's differentiable simulation approach to Lenia:
1. Treat Lenia kernel parameters as learnable
2. Use autodiff to compute gradients through simulation
3. Optimize for emergence metrics (survival, complexity, diversity)

This bridges:
- V7: Evolutionary parameter search (indirect gradient)
- V9: Learnable GNN attention (local gradients)
- V10: End-to-end differentiable Lenia (global gradients)

Reference:
https://github.com/jax-md/jax-md
Schoenholz & Cubuk, "JAX M.D. A Framework for Differentiable Physics"
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json
from datetime import datetime

try:
    import jax
    import jax.numpy as jnp
    from jax import jit, grad, vmap, lax
    from jax import random as jax_random
    from functools import partial
    import optax
    HAS_JAX = True
    print("[OK] JAX available for differentiable simulation")
except ImportError:
    HAS_JAX = False
    print("[FAIL] JAX not available")


# ============================================================================
# Differentiable Lenia Core (JAX)
# ============================================================================

def create_kernel_template(R: int) -> np.ndarray:
    """Pre-compute distance template for kernel."""
    coords = np.arange(-R, R + 1, dtype=np.float32)
    X, Y = np.meshgrid(coords, coords)
    dist = np.sqrt(X**2 + Y**2)
    r = dist / R  # Normalized distance [0, 1]
    return r


def gaussian_kernel_from_template(r_template: np.ndarray, mu: jnp.ndarray, sigma: jnp.ndarray) -> jnp.ndarray:
    """Create Gaussian kernel from pre-computed template using JAX ops."""
    # Use JAX operations for differentiable computation
    r = jax.device_put(r_template)
    kernel = jnp.exp(-((r - mu)**2) / (2 * sigma**2 + 1e-8))
    kernel = kernel / (jnp.sum(kernel) + 1e-8)
    return kernel


def growth_function_jax(U: jnp.ndarray, mu: float, sigma: float) -> jnp.ndarray:
    """Differentiable growth function."""
    return jnp.exp(-((U - mu)**2) / (2 * sigma**2 + 1e-8))


@jit
def lenia_step_jax(state: jnp.ndarray, kernel: jnp.ndarray, 
                   growth_mu: float, growth_sigma: float) -> jnp.ndarray:
    """Single differentiable Lenia step using convolution."""
    # 2D convolution with same padding
    R = kernel.shape[0] // 2
    padded = jnp.pad(state, ((R, R), (R, R)), mode='wrap')
    
    # Sliding window convolution
    def convolve_at(i, j):
        window = jax.lax.dynamic_slice(padded, (i, j), kernel.shape)
        return jnp.sum(window * kernel)
    
    U = jax.vmap(lambda i: jax.vmap(lambda j: convolve_at(i, j))(jnp.arange(state.shape[1])))(jnp.arange(state.shape[0]))
    
    # Growth function
    G = growth_function_jax(U, growth_mu, growth_sigma)
    
    # State update
    new_state = jnp.clip(state + 1.0 * (G - 0.5), 0.0, 1.0)
    
    return new_state


@jit
def simulate_lenia_jax_with_kernel(kernel: jnp.ndarray, growth_mu: float, growth_sigma: float, seed: jnp.ndarray, steps: int = 100) -> jnp.ndarray:
    """Run differentiable Lenia simulation with pre-computed kernel."""
    def step_fn(state, _):
        new_state = lenia_step_jax(state, kernel, growth_mu, growth_sigma)
        return new_state, None
    
    final_state, _ = lax.scan(step_fn, seed, None, length=steps)
    
    return final_state


# ============================================================================
# Emergence Metrics (Differentiable)
# ============================================================================

@jit
def compute_survival_metric(state: jnp.ndarray) -> float:
    """Differentiable survival metric."""
    return jnp.mean(state)


@jit
def compute_complexity_metric(state: jnp.ndarray) -> float:
    """Differentiable complexity metric using Sobel edges."""
    sobel_x = jnp.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    sobel_y = sobel_x.T
    
    # Pad for convolution
    padded = jnp.pad(state, ((1, 1), (1, 1)), mode='wrap')
    
    # Edge detection (simplified)
    edges_x = jnp.abs(state[1:, :] - state[:-1, :])
    edges_y = jnp.abs(state[:, 1:] - state[:, :-1])
    
    # Edge density
    edge_density = jnp.mean(edges_x) + jnp.mean(edges_y)
    
    return edge_density


@jit
def compute_diversity_metric(state: jnp.ndarray) -> float:
    """Differentiable diversity using entropy."""
    # Histogram approximation (soft binning)
    bins = jnp.linspace(0, 1, 20)
    
    def soft_count(bin_val):
        # Gaussian kernel density estimation
        weights = jnp.exp(-((state - bin_val)**2) / (2 * 0.05**2))
        return jnp.sum(weights)
    
    counts = jax.vmap(soft_count)(bins)
    probs = counts / (jnp.sum(counts) + 1e-8)
    
    # Entropy
    entropy = -jnp.sum(probs * jnp.log(probs + 1e-8))
    
    return entropy


@partial(jit, static_argnums=(2, 3))
def emergence_loss(params: dict, seed: jnp.ndarray, r_template: np.ndarray, steps: int = 100) -> float:
    """Loss function for gradient descent (negative emergence)."""
    kernel_mu = params['kernel_mu']
    kernel_sigma = params['kernel_sigma']
    growth_mu = params['growth_mu']
    growth_sigma = params['growth_sigma']
    
    # Create kernel using JAX ops (differentiable w.r.t. mu, sigma)
    kernel = gaussian_kernel_from_template(r_template, kernel_mu, kernel_sigma)
    
    final_state = simulate_lenia_jax_with_kernel(kernel, growth_mu, growth_sigma, seed, steps)
    
    survival = compute_survival_metric(final_state)
    complexity = compute_complexity_metric(final_state)
    diversity = compute_diversity_metric(final_state)
    
    # Combined emergence score (to maximize)
    emergence = 0.4 * survival + 0.3 * complexity + 0.3 * diversity
    
    # Return negative for minimization
    return -emergence


# ============================================================================
# Gradient-Based Optimization
# ============================================================================

def optimize_lenia_params(
    seed: jnp.ndarray,
    initial_params: dict,
    num_iterations: int = 50,
    learning_rate: float = 0.01,
    steps_per_sim: int = 50
) -> tuple:
    """
    Optimize Lenia parameters using gradient descent.
    
    This is the JAX-MD inspired approach:
    - Compute gradients through entire simulation
    - Use autodiff to optimize parameters
    - End-to-end differentiable pipeline
    """
    if not HAS_JAX:
        print("JAX required for optimization")
        return None, None
    
    print(f"\n{'='*60}")
    print(f"JAX-MD Style Differentiable Lenia Optimization")
    print(f"{'='*60}")
    print(f"Initial params: μ_k={initial_params['kernel_mu']:.4f}, "
          f"σ_k={initial_params['kernel_sigma']:.4f}")
    print(f"               μ_g={initial_params['growth_mu']:.4f}, "
          f"σ_g={initial_params['growth_sigma']:.4f}")
    print(f"Iterations: {num_iterations}, LR: {learning_rate}")
    print(f"Simulation steps: {steps_per_sim}")
    print(f"{'='*60}\n")
    
    # Initialize optimizer
    optimizer = optax.adam(learning_rate)
    
    # Convert params to JAX array for optimization
    param_array = jnp.array([
        initial_params['kernel_mu'],
        initial_params['kernel_sigma'],
        initial_params['growth_mu'],
        initial_params['growth_sigma']
    ])
    
    opt_state = optimizer.init(param_array)
    
    # Loss function with extracted params
    # Pre-compute kernel template
    R_const = initial_params.get('R', 10)
    r_template_np = create_kernel_template(R_const)
    r_template = jax.device_put(r_template_np)  # Convert to JAX array
    
    # Use closure to avoid static_argnums issue
    def loss_fn(param_vec):
        params = {
            'kernel_mu': param_vec[0],
            'kernel_sigma': param_vec[1],
            'growth_mu': param_vec[2],
            'growth_sigma': param_vec[3]
        }
        kernel_mu = params['kernel_mu']
        kernel_sigma = params['kernel_sigma']
        growth_mu = params['growth_mu']
        growth_sigma = params['growth_sigma']
        
        # Create kernel using JAX ops
        kernel = jnp.exp(-((r_template - kernel_mu)**2) / (2 * kernel_sigma**2 + 1e-8))
        kernel = kernel / (jnp.sum(kernel) + 1e-8)
        
        # Simulate
        def step_fn(state, _):
            R = kernel.shape[0] // 2
            padded = jnp.pad(state, ((R, R), (R, R)), mode='wrap')
            
            def convolve_row(i):
                def convolve_col(j):
                    window = jax.lax.dynamic_slice(padded, (i, j), kernel.shape)
                    return jnp.sum(window * kernel)
                return jax.vmap(convolve_col)(jnp.arange(state.shape[1]))
            
            U = jax.vmap(convolve_row)(jnp.arange(state.shape[0]))
            G = jnp.exp(-((U - growth_mu)**2) / (2 * growth_sigma**2 + 1e-8))
            new_state = jnp.clip(state + 1.0 * (G - 0.5), 0.0, 1.0)
            return new_state, None
        
        final_state, _ = lax.scan(step_fn, seed, None, length=steps_per_sim)
        
        # Metrics
        survival = jnp.mean(final_state)
        edges_x = jnp.abs(final_state[1:, :] - final_state[:-1, :])
        edges_y = jnp.abs(final_state[:, 1:] - final_state[:, :-1])
        complexity = jnp.mean(edges_x) + jnp.mean(edges_y)
        
        bins = jnp.linspace(0, 1, 20)
        def soft_count(bin_val):
            weights = jnp.exp(-((final_state - bin_val)**2) / (2 * 0.05**2))
            return jnp.sum(weights)
        counts = jax.vmap(soft_count)(bins)
        probs = counts / (jnp.sum(counts) + 1e-8)
        diversity = -jnp.sum(probs * jnp.log(probs + 1e-8))
        
        emergence = 0.4 * survival + 0.3 * complexity + 0.3 * diversity
        return -emergence
    
    # JIT compile gradient function
    grad_fn = jit(grad(loss_fn))
    
    # Optimization loop
    history = []
    best_loss = float('inf')
    best_params = None
    
    for i in range(num_iterations):
        # Compute gradients
        grads = grad_fn(param_array)
        
        # Update params
        updates, opt_state = optimizer.update(grads, opt_state)
        param_array = optax.apply_updates(param_array, updates)
        
        # Clip to valid ranges
        param_array = jnp.clip(param_array, 
                               jnp.array([0.0, 0.01, 0.0, 0.01]),
                               jnp.array([1.0, 0.5, 1.0, 0.5]))
        
        # Compute current loss
        current_loss = loss_fn(param_array)
        emergence_score = -current_loss
        
        # Track history
        history.append({
            'iteration': i,
            'loss': float(current_loss),
            'emergence': float(emergence_score),
            'params': param_array.tolist()
        })
        
        if current_loss < best_loss:
            best_loss = current_loss
            best_params = param_array.copy()
        
        if i % 10 == 0:
            print(f"Iter {i:3d}: Loss={current_loss:.6f}, "
                  f"Emergence={emergence_score:.4f}, "
                  f"Params=[μ_k={param_array[0]:.4f}, σ_k={param_array[1]:.4f}, "
                  f"μ_g={param_array[2]:.4f}, σ_g={param_array[3]:.4f}]")
    
    return best_params, history


# ============================================================================
# Visualization
# ============================================================================

def visualize_optimization(history: list, output_path: str):
    """Plot optimization progress."""
    iterations = [h['iteration'] for h in history]
    emergence = [h['emergence'] for h in history]
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    
    # Emergence over iterations
    axes[0].plot(iterations, emergence, 'b-', linewidth=2)
    axes[0].set_xlabel('Iteration', fontsize=12)
    axes[0].set_ylabel('Emergence Score', fontsize=12)
    axes[0].set_title('Gradient-Based Optimization Progress', fontsize=14)
    axes[0].grid(True, alpha=0.3)
    
    # Parameter evolution
    params_array = np.array([h['params'] for h in history])
    labels = ['Kernel μ', 'Kernel σ', 'Growth μ', 'Growth σ']
    
    for i, label in enumerate(labels):
        axes[1].plot(iterations, params_array[:, i], label=label, linewidth=2)
    
    axes[1].set_xlabel('Iteration', fontsize=12)
    axes[1].set_ylabel('Parameter Value', fontsize=12)
    axes[1].set_title('Parameter Evolution', fontsize=14)
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\n[OK] Visualization saved to {output_path}")


# ============================================================================
# Main Experiment
# ============================================================================

def main():
    """Run V10 differentiable Lenia prototype."""
    print("\n" + "="*70)
    print("LENIA V10 - JAX-MD INSPIRED DIFFERENTIABLE SIMULATION")
    print("="*70)
    print("\nKey Innovation: End-to-end gradients through simulation")
    print("Reference: JAX-MD (Schoenholz & Cubuk)")
    print("="*70 + "\n")
    
    if not HAS_JAX:
        print("✗ JAX not available. Install with: pip install jax jaxlib optax")
        return
    
    # Create seed pattern
    seed = np.zeros((64, 64), dtype=np.float32)
    center = 32
    for i in range(-5, 6):
        for j in range(-5, 6):
            if i*i + j*j <= 25:
                seed[center + i, center + j] = 1.0
    
    seed_jax = jax.device_put(seed)
    
    # Initial parameters (near Orbium)
    initial_params = {
        'kernel_mu': 0.15,
        'kernel_sigma': 0.015,
        'growth_mu': 0.15,
        'growth_sigma': 0.015,
        'R': 10
    }
    
    print("Initial parameters (Orbium-like):")
    print(f"  Kernel: μ={initial_params['kernel_mu']}, σ={initial_params['kernel_sigma']}")
    print(f"  Growth: μ={initial_params['growth_mu']}, σ={initial_params['growth_sigma']}")
    print(f"  Radius: R={initial_params['R']}\n")
    
    # Run optimization
    best_params, history = optimize_lenia_params(
        seed_jax,
        initial_params,
        num_iterations=100,
        learning_rate=0.005,
        steps_per_sim=50
    )
    
    if best_params is None:
        print("Optimization failed")
        return
    
    # Results
    print("\n" + "="*60)
    print("OPTIMIZATION COMPLETE")
    print("="*60)
    print(f"\nBest parameters found:")
    print(f"  Kernel: μ={best_params[0]:.4f}, σ={best_params[1]:.4f}")
    print(f"  Growth: μ={best_params[2]:.4f}, σ={best_params[3]:.4f}")
    print(f"\nBest emergence score: {-min(h['loss'] for h in history):.4f}")
    
    # Save results
    output_dir = Path("D:/emergence_experiments")
    output_dir.mkdir(exist_ok=True)
    
    results = {
        'method': 'jax_md_differentiable_optimization',
        'initial_params': initial_params,
        'best_params': {
            'kernel_mu': float(best_params[0]),
            'kernel_sigma': float(best_params[1]),
            'growth_mu': float(best_params[2]),
            'growth_sigma': float(best_params[3])
        },
        'best_emergence': float(-min(h['loss'] for h in history)),
        'history': history
    }
    
    results_path = output_dir / "v10_jax_md_results.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n[OK] Results saved to {results_path}")
    
    # Visualize
    viz_path = output_dir / "v10_optimization_progress.png"
    visualize_optimization(history, str(viz_path))
    
    # Comparison
    print("\n" + "="*60)
    print("COMPARISON WITH PRIOR METHODS")
    print("="*60)
    print("\nV7 (Evolutionary Search):")
    print("  - Population-based, gradient-free")
    print("  - Explores parameter space globally")
    print("  - Slower convergence")
    
    print("\nV9 (Learnable GNN):")
    print("  - Local gradients via attention")
    print("  - Hybrid evolutionary + gradient")
    print("  - 93.97% survival achieved")
    
    print("\nV10 (JAX-MD Style):")
    print("  - End-to-end differentiable")
    print("  - Direct gradient through simulation")
    print("  - Fast local optimization")
    print("  - Potential for combining with V7/V9")
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("\n1. Test on longer simulations (200-500 steps)")
    print("2. Try different seed patterns")
    print("3. Combine with evolutionary search (V7)")
    print("4. Apply to GNN Lenia (V9)")
    print("5. Explore JAX-MD's neighbor list optimization")


if __name__ == "__main__":
    main()
