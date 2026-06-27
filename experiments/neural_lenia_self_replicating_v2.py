"""
Self-Replicating Neural Lenia (Simplified)
==========================================

Simplified version based on working neural_lenia.py prototype.
Tests whether neural kernels can produce self-sustaining patterns.
"""

import jax
import jax.numpy as jnp
import numpy as np
from PIL import Image
import json
from pathlib import Path
from functools import partial
from typing import NamedTuple


class NeuralKernelParams(NamedTuple):
    """Neural kernel parameters"""
    w1: jnp.ndarray
    b1: jnp.ndarray
    w2: jnp.ndarray
    b2: jnp.ndarray


def init_neural_kernel(key, hidden_dim=16):
    """Initialize neural kernel"""
    input_dim = 3  # r, sin(theta), cos(theta)
    k1, k2 = jax.random.split(key)
    
    w1 = jax.random.normal(k1, (hidden_dim, input_dim)) * 0.3
    b1 = jnp.zeros(hidden_dim)
    w2 = jax.random.normal(k2, (1, hidden_dim)) * 0.3
    b2 = jnp.zeros(1)
    
    return NeuralKernelParams(w1, b1, w2, b2)


def neural_kernel_forward(params: NeuralKernelParams, r, theta):
    """Forward: (r, theta) -> kernel value [0, 1]"""
    # Input encoding
    x = jnp.array([
        jnp.sin(r * 2 * jnp.pi),
        jnp.sin(theta),
        jnp.cos(theta)
    ])
    
    # Hidden layer with ReLU
    h = jnp.maximum(0, params.w1 @ x + params.b1)
    
    # Output with sigmoid
    out = jax.nn.sigmoid(params.w2 @ h + params.b2)
    
    return out.squeeze()


def make_neural_kernel(R=13):
    """Create a function that generates kernel from params"""
    
    @jax.jit
    def generate_kernel(params):
        """Generate 2D kernel from neural parameters"""
        size = 2 * R + 1
        kernel = jnp.zeros((size, size))
        
        # Generate kernel values
        for y in range(size):
            for x in range(size):
                dy = y - R
                dx = x - R
                r = jnp.sqrt(dx**2 + dy**2) / R
                theta = jnp.arctan2(dy, dx)
                
                # Only set values in ring [0.1, 1.0]
                val = jnp.where(
                    (r > 0.1) & (r <= 1.0),
                    neural_kernel_forward(params, r, theta),
                    0.0
                )
                kernel = kernel.at[y, x].set(val)
        
        # Normalize
        kernel = kernel / (jnp.sum(kernel) + 1e-8)
        return kernel
    
    return generate_kernel


def lenia_step(grid, kernel, growth_fn, dt=0.1):
    """Single Lenia step"""
    # Convolution (simplified, without scipy)
    pad_size = kernel.shape[0] // 2
    padded = jnp.pad(grid, pad_size, mode='wrap')
    
    # Manual convolution (slow but correct)
    def convolve_at(y, x):
        region = jax.lax.dynamic_slice(padded, (y, x), kernel.shape)
        return jnp.sum(region * kernel)
    
    h, w = grid.shape
    kh, kw = kernel.shape
    
    # Use jax.vmap for efficiency
    y_idx = jnp.arange(h)
    x_idx = jnp.arange(w)
    
    def conv_row(y):
        def conv_col(x):
            region = jax.lax.dynamic_slice(padded, (y, x), (kh, kw))
            return jnp.sum(region * kernel)
        return jax.vmap(conv_col)(x_idx)
    
    conv = jax.vmap(conv_row)(y_idx)
    
    # Growth
    growth = growth_fn(conv)
    
    # Update
    new_grid = jnp.clip(grid + dt * (growth * 2 - 1), 0, 1)
    
    return new_grid


def make_growth_fn(mu=0.15, sigma=0.014):
    """Create growth function"""
    @jax.jit
    def growth(x):
        return jnp.exp(-((x - mu)**2) / (2 * sigma**2))
    return growth


def run_lenia(params, generate_kernel, R=13, steps=200, grid_size=64, seed=0):
    """Run Lenia simulation with neural kernel"""
    key = jax.random.PRNGKey(seed)
    
    # Generate kernel
    kernel = generate_kernel(params)
    
    # Initialize grid
    grid = jax.random.uniform(key, (grid_size, grid_size)) * 0.3
    
    # Add seed pattern in center
    center = grid_size // 2
    seed_size = 10
    k1, k2 = jax.random.split(key)
    seed_pattern = jax.random.uniform(k1, (seed_size*2, seed_size*2), minval=0.5, maxval=1.0)
    grid = jax.lax.dynamic_update_slice(grid, seed_pattern, (center-seed_size, center-seed_size))
    
    # Growth function
    growth_fn = make_growth_fn(mu=0.15, sigma=0.014)
    
    # Run simulation
    alive_history = []
    
    def step_fn(grid, _):
        new_grid = lenia_step(grid, kernel, growth_fn, dt=0.1)
        alive = jnp.mean((new_grid > 0.1).astype(float))
        return new_grid, alive
    
    # Scan over steps
    final_grid, alive_array = jax.lax.scan(step_fn, grid, None, length=steps)
    
    return {
        'final_grid': np.array(final_grid),
        'kernel': np.array(kernel),
        'alive_final': float(alive_array[-1]),
        'alive_mean': float(jnp.mean(alive_array[-50:])),
        'alive_history': [float(x) for x in alive_array]
    }


def evaluate_self_replication(params, generate_kernel, R=13, steps=200):
    """
    Evaluate self-replication capability.
    
    Criteria:
    1. Survival: alive > 0.2
    2. Stability: variance < 0.05
    """
    result = run_lenia(params, generate_kernel, R=R, steps=steps)
    
    alive_mean = result['alive_mean']
    alive_history = result['alive_history']
    variance = float(np.var(alive_history[-50:]))
    
    # Score: survival + stability
    survival_score = alive_mean * 5 if alive_mean > 0.1 else 0
    stability_score = max(0, 1 - variance * 20)
    
    score = survival_score + stability_score
    
    return {
        'score': score,
        'alive_mean': alive_mean,
        'variance': variance,
        'survival_score': survival_score,
        'stability_score': stability_score
    }


def random_search(n_iterations=30, R=13, steps=200, hidden_dim=16):
    """Random search for self-replicating kernels"""
    print(f"\n[SEARCH] {n_iterations} iterations, R={R}, steps={steps}")
    
    generate_kernel = make_neural_kernel(R=R)
    
    best_score = -float('inf')
    best_params = None
    results = []
    
    for i in range(n_iterations):
        # Random init
        key = jax.random.PRNGKey(i * 42)
        params = init_neural_kernel(key, hidden_dim=hidden_dim)
        
        # Evaluate
        eval_result = evaluate_self_replication(params, generate_kernel, R=R, steps=steps)
        
        results.append({
            'iteration': i,
            **eval_result
        })
        
        if eval_result['score'] > best_score:
            best_score = eval_result['score']
            best_params = params
        
        if (i + 1) % 10 == 0:
            print(f"  [{i+1}/{n_iterations}] Best: {best_score:.3f}, Last alive: {eval_result['alive_mean']:.3f}")
    
    return {
        'best_params': best_params,
        'best_score': best_score,
        'results': results
    }


def test_self_replicating_lenia():
    """Main test"""
    print("=" * 60)
    print("Self-Replicating Neural Lenia (Simplified)")
    print("=" * 60)
    
    # Run search
    search_result = random_search(n_iterations=30, R=13, steps=200, hidden_dim=16)
    
    print(f"\n[BEST] Score: {search_result['best_score']:.3f}")
    
    # Generate outputs
    if search_result['best_params'] is not None:
        generate_kernel = make_neural_kernel(R=13)
        
        # Run with best params
        result = run_lenia(search_result['best_params'], generate_kernel, R=13, steps=300)
        
        # Save outputs
        output_dir = Path("D:/openclaw_workspace/experiments/output")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = int(jax.random.PRNGKey(0)[0])
        
        # Kernel image
        kernel_img = Image.fromarray((result['kernel'] * 255).astype(np.uint8))
        kernel_img = kernel_img.resize((256, 256), Image.NEAREST)
        kernel_path = output_dir / f"self_repl_kernel_{timestamp}.png"
        kernel_img.save(kernel_path)
        print(f"[SAVED] Kernel: {kernel_path}")
        
        # Grid image
        grid_img = Image.fromarray((result['final_grid'] * 255).astype(np.uint8))
        grid_img = grid_img.resize((256, 256), Image.NEAREST)
        grid_path = output_dir / f"self_repl_grid_{timestamp}.png"
        grid_img.save(grid_path)
        print(f"[SAVED] Grid: {grid_path}")
        
        # Results JSON
        results_json = {
            'best_score': search_result['best_score'],
            'alive_final': result['alive_final'],
            'alive_mean': result['alive_mean'],
            'top_5': sorted(search_result['results'], key=lambda x: -x['score'])[:5]
        }
        json_path = output_dir / f"self_repl_results_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(results_json, f, indent=2)
        print(f"[SAVED] Results: {json_path}")
        
        # Summary
        print(f"\n[SUMMARY]")
        print(f"  Final alive: {result['alive_final']:.3f}")
        print(f"  Mean alive (last 50): {result['alive_mean']:.3f}")
        
        if result['alive_mean'] > 0.2:
            print("  [OK] Pattern survives!")
        else:
            print("  [X] Pattern died")
    
    print("\n[DONE]")


if __name__ == '__main__':
    test_self_replicating_lenia()
