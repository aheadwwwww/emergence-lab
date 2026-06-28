"""
Gradient Depth Test for Differentiable Lenia
=============================================
Tests hypothesis: shorter simulation chains preserve gradients better.
Measures gradient magnitude through simulation at different depths.

Key questions:
1. Does gradient flow degrade with simulation length?
2. What's the optimal trade-off between simulation depth and gradient signal?
3. Can we use progressive simulation (short→long) as a curriculum?

Based on V10 findings: flat gradients on full 256-step simulation.
"""
import jax
import jax.numpy as jnp
import numpy as np
from jax import grad, vmap, jit
import time

# ============================================================
# Lenia Kernel (simplified, differentiable)
# ============================================================
def make_gaussian_kernel(R):
    """Factory: creates a gaussian kernel function for fixed R"""
    k = jnp.arange(-R, R + 1)
    xx, yy = jnp.meshgrid(k, k)
    R_float = float(R)
    
    def kernel(params):
        """params: [mu, sigma]"""
        mu, sigma = params
        dist = jnp.sqrt(xx**2 + yy**2) / R_float
        dist = jnp.minimum(dist, 1.0)
        return jnp.exp(-((dist - mu) ** 2) / (2 * sigma**2))
    return kernel

@jit
def compute_potential(field, kernel):
    """Convolution via FFT"""
    field_freq = jnp.fft.fft2(field)
    kernel_freq = jnp.fft.fft2(kernel, s=field.shape)
    return jnp.fft.ifft2(field_freq * kernel_freq).real

@jit
def growth_fn(U, mu_g=0.15, sigma_g=0.015):
    """Gaussian growth function"""
    return 2 * jnp.exp(-((U - mu_g) ** 2) / (2 * sigma_g**2)) - 1

def make_step_lenia(R):
    """Factory: creates step function for fixed R"""
    gk_fn = make_gaussian_kernel(R)
    
    @jit
    def step(state, kernel_params, dt=0.1):
        kernel = gk_fn(kernel_params)
        U = compute_potential(state, kernel)
        growth = growth_fn(U)
        new_state = jnp.clip(state + dt * growth, 0.0, 1.0)
        return new_state
    return step

@jit
def simulate_lenia(init_state, kernel_params, R, steps, dt=0.1):
    """Simulate Lenia for `steps` steps"""
    def body_fn(state, _):
        next_state = step_lenia(state, kernel_params, R, dt)
        return next_state, next_state
    final_state, _ = jax.lax.scan(body_fn, init_state, None, length=steps)
    return final_state

# Factory: creates a jitted function for specific R and steps
def make_simulate(R, steps):
    step_fn = make_step_lenia(R)
    dt = 0.1
    
    @jit
    def simulate(init_state, kernel_params):
        def body_fn(state, _):
            next_state = step_fn(state, kernel_params, dt)
            return next_state, next_state
        final_state, _ = jax.lax.scan(body_fn, init_state, None, length=steps)
        return final_state
    return simulate

# ============================================================
# Loss Functions
# ============================================================
def entropy_loss(state):
    """Pixel-wise entropy as emergence metric"""
    p = jnp.clip(state, 1e-8, 1 - 1e-8)
    return -jnp.mean(p * jnp.log(p) + (1 - p) * jnp.log(1 - p))

def complexity_loss(state):
    """Spatial complexity via gradient magnitude"""
    grad_y = state[1:, :] - state[:-1, :]
    grad_x = state[:, 1:] - state[:, :-1]
    # Align dimensions: both should be (H-1, W-1)
    gx = grad_x[:-1, :]  # Remove last row to match
    gy = grad_y[:, :-1]  # Remove last col to match
    return jnp.mean(jnp.sqrt(gx**2 + gy**2))

def emergence_loss(state):
    """Combined emergence metric"""
    return entropy_loss(state) + 0.5 * complexity_loss(state)

# ============================================================
# Gradient Analysis
# ============================================================
def compute_gradient_norm(kernel_params, init_state, R, steps):
    """Compute L2 norm of gradient w.r.t kernel_params"""
    simulate = make_simulate(R, steps)
    loss_fn = lambda p: emergence_loss(simulate(init_state, p))
    g = grad(loss_fn)(kernel_params)
    return jnp.sqrt(jnp.sum(g**2))

def run_depth_test():
    """Test gradient magnitude vs simulation depth"""
    # Setup
    SIZE = 64
    R = 10
    key = jax.random.PRNGKey(42)
    init_state = jax.random.uniform(key, (SIZE, SIZE)) * 0.3
    kernel_params = jnp.array([0.15, 0.03])  # mu, sigma
    
    depths = [4, 8, 16, 32, 64, 128, 256, 512]
    results = []
    
    print("=" * 60)
    print("Gradient Depth Test for Differentiable Lenia")
    print("=" * 60)
    print(f"{'Steps':>6} | {'Grad Norm':>12} | {'Time (s)':>10} | {'Survival':>10}")
    print("-" * 60)
    
    for steps in depths:
        t0 = time.time()
        grad_norm = float(compute_gradient_norm(kernel_params, init_state, R, steps))
        elapsed = time.time() - t0
        
        # Also check if alive
        simulate = make_simulate(R, steps)
        final_state = simulate(init_state, kernel_params)
        survival = float(jnp.mean(final_state > 0.01))
        
        results.append({
            'steps': steps,
            'grad_norm': grad_norm,
            'time': elapsed,
            'survival': survival
        })
        
        print(f"{steps:>6} | {grad_norm:>12.6e} | {elapsed:>10.3f} | {survival:>10.4f}")
    
    print("-" * 60)
    
    # Analysis
    norms = np.array([r['grad_norm'] for r in results])
    max_idx = np.argmax(norms)
    print(f"\nBest depth: {depths[max_idx]} steps (grad={norms[max_idx]:.6e})")
    print(f"Worst depth: {depths[np.argmin(norms)]} steps (grad={np.min(norms):.6e})")
    
    # Check for monotonic decay
    monotonic = all(norms[i] >= norms[i+1] for i in range(len(norms)-1))
    print(f"Monotonic decay: {monotonic}")
    
    return results

# ============================================================
# Progressive Training (Curriculum)
# ============================================================
def curriculum_loss(kernel_params, init_state, R, weight_short=0.3, weight_long=0.7, short_steps=16, long_steps=128):
    """Curriculum loss: short + long simulation"""
    sim_short = make_simulate(R, short_steps)
    sim_long = make_simulate(R, long_steps)
    final_short = sim_short(init_state, kernel_params)
    final_long = sim_long(init_state, kernel_params)
    return weight_short * emergence_loss(final_short) + weight_long * emergence_loss(final_long)

def compute_curriculum_gradient(kernel_params, init_state, R, stage1_steps, stage2_steps):
    """Gradient for 2-stage curriculum"""
    loss_fn = lambda p: curriculum_loss(p, init_state, R, 0.3, 0.7, stage1_steps, stage2_steps)
    g = grad(loss_fn)(kernel_params)
    return jnp.sqrt(jnp.sum(g**2))

def test_curriculum():
    """Compare single-depth vs curriculum gradients"""
    print("\n" + "=" * 60)
    print("Curriculum Gradient Test")
    print("=" * 60)
    
    SIZE = 64
    R = 10
    key = jax.random.PRNGKey(42)
    init_state = jax.random.uniform(key, (SIZE, SIZE)) * 0.3
    kernel_params = jnp.array([0.15, 0.03])
    
    # Single depth 256
    g_single = compute_gradient_norm(kernel_params, init_state, R, 256)
    
    # Curriculum: 64 + 256
    g_curriculum = compute_curriculum_gradient(kernel_params, init_state, R, 16, 128)
    
    print(f"Single depth (256): {float(g_single):.6e}")
    print(f"Curriculum (16+128): {float(g_curriculum):.6e}")
    
    if g_curriculum > g_single:
        print("✓ Curriculum preserves gradient better!")
    else:
        print("✗ Curriculum does not improve gradient")
    
    return {
        'single_256': float(g_single),
        'curriculum_16_128': float(g_curriculum)
    }

# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    t_total = time.time()
    
    # Run depth test
    depth_results = run_depth_test()
    
    # Run curriculum test
    curriculum_results = test_curriculum()
    
    print(f"\n{'='*60}")
    print(f"Total time: {time.time() - t_total:.2f}s")
    
    # Save results
    import json
    output = {
        'depth_results': depth_results,
        'curriculum_results': curriculum_results,
        'verdict': 'gradient_depth_analysis'
    }
    
    with open('results/gradient_depth_test.json', 'w') as f:
        json.dump(output, f, indent=2, default=float)
    
    print("Results saved to results/gradient_depth_test.json")
