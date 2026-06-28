"""
Test: Can the Genome class express known-good Lenia kernels?

Hypothesis: If gradient descent cannot find genome weights that produce
a Gaussian Ring kernel, then the representation is too limited.

This tests whether the 33-parameter genome (2→8→1 neural network) 
can approximate a known-good Orbium kernel.
"""

import sys
sys.path.insert(0, 'D:/openclaw_workspace/experiments')

import numpy as np
import jax
import jax.numpy as jnp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

from evolutionary_lenia import Genome

# ═══════════════════════════════════════════════════════════════
# Target Kernel: Gaussian Ring (Orbium-style)
# ═══════════════════════════════════════════════════════════════

def make_gaussian_ring_kernel(R: int, mu: float = 0.5, sigma: float = 0.15) -> np.ndarray:
    """Create a Gaussian Ring kernel (Orbium-style)."""
    y, x = np.ogrid[-R:R+1, -R:R+1]
    r = np.sqrt(x*x + y*y) / R
    kernel = np.exp(-((r - mu)**2) / (2 * sigma**2))
    kernel[r > 1] = 0
    return kernel / kernel.sum()


# ═══════════════════════════════════════════════════════════════
# Genome → Kernel Conversion
# ═══════════════════════════════════════════════════════════════

def genome_to_kernel_jax(weights: jnp.ndarray, R: int) -> jnp.ndarray:
    """Convert genome weights to kernel using JAX (differentiable)."""
    # Parse weights
    w1 = weights[:16].reshape(8, 2)
    b1 = weights[16:24]
    w2 = weights[24:32].reshape(1, 8)
    b2 = weights[32:33]
    
    # Create coordinate grid
    kernel_hw = 2 * R + 1
    y, x = jnp.ogrid[-R:R+1, -R:R+1]
    r = jnp.sqrt(x*x + y*y)
    theta = jnp.arctan2(y, x)
    r_norm = r / (R + 1e-8)
    theta_norm = (theta + jnp.pi) / (2 * jnp.pi)
    mask = r <= R
    
    # Build kernel using vectorized operations
    # Flatten for batch processing
    r_flat = r_norm.flatten()
    theta_flat = theta_norm.flatten()
    mask_flat = mask.flatten()
    
    # Batch input: [N, 2]
    inp = jnp.stack([r_flat, theta_flat], axis=1)
    
    # Forward pass through NN: [N, 2] @ [2, 8] + [8] -> [N, 8]
    h = jnp.tanh(inp @ w1.T + b1)
    # [N, 8] @ [8, 1] + [1] -> [N, 1]
    out = jnp.tanh(h @ w2.T + b2)
    
    # Reshape and apply mask
    kernel = (out.squeeze() * mask_flat).reshape(kernel_hw, kernel_hw)
    
    return kernel

def genome_to_kernel_array(genome: Genome, R: int) -> np.ndarray:
    """Extract the kernel array from a genome (for visualization)."""
    return np.array(genome_to_kernel_jax(jnp.array(genome.weights), R))


# ═══════════════════════════════════════════════════════════════
# Gradient Descent Fitting
# ═══════════════════════════════════════════════════════════════

def fit_genome_to_kernel(target_kernel: np.ndarray, R: int, n_iters: int = 1000, lr: float = 0.1):
    """Use gradient descent to fit genome weights to match target kernel."""
    
    # Convert target to JAX array
    target_jax = jnp.array(target_kernel, dtype=jnp.float32)
    target_sum = jnp.abs(target_jax).sum()
    
    def loss_fn(weights):
        """MSE loss between predicted kernel and target kernel."""
        pred_kernel = genome_to_kernel_jax(weights, R)
        
        # Normalize both for fair comparison
        pred_norm = pred_kernel / (jnp.abs(pred_kernel).sum() + 1e-8)
        target_norm = target_jax / (target_sum + 1e-8)
        
        # MSE loss
        return jnp.mean((pred_norm - target_norm)**2)
    
    # JAX gradient
    loss_and_grad = jax.value_and_grad(loss_fn)
    
    # Initialize weights (JAX array)
    key = jax.random.PRNGKey(42)
    weights = jax.random.normal(key, shape=(33,)) * 0.5
    weights = weights.astype(jnp.float32)
    losses = []
    
    print(f"Starting kernel fitting optimization...")
    print(f"Target: Gaussian Ring (R={R}, mu=0.5, sigma=0.15)")
    print(f"Genome: 33 parameters (2→8→1 NN)")
    print(f"Optimizer: Gradient Descent (lr={lr}, iters={n_iters})")
    print()
    
    for i in range(n_iters):
        loss_val, grad = loss_and_grad(weights)
        loss_float = float(loss_val)
        losses.append(loss_float)
        weights = weights - lr * grad
        
        if i % 100 == 0 or i == n_iters - 1:
            print(f"Iter {i:4d}: loss = {loss_float:.6f}")
    
    return Genome(np.array(weights)), losses


# ═══════════════════════════════════════════════════════════════
# Main Test
# ═══════════════════════════════════════════════════════════════

def main():
    print("="*60)
    print("KERNEL FITTING TEST")
    print("Can a 33-param genome express a Gaussian Ring kernel?")
    print("="*60)
    print()
    
    # Parameters
    R = 15
    
    # Create target kernel
    target = make_gaussian_ring_kernel(R, mu=0.5, sigma=0.15)
    print(f"Target kernel shape: {target.shape}")
    print(f"Target kernel sum: {target.sum():.6f}")
    print()
    
    # Fit genome to target
    fitted_genome, losses = fit_genome_to_kernel(target, R, n_iters=500, lr=0.05)
    
    # Extract fitted kernel
    fitted_kernel = genome_to_kernel_array(fitted_genome, R)
    
    # Normalize for comparison
    fitted_norm = fitted_kernel / (np.abs(fitted_kernel).sum() + 1e-8)
    target_norm = target / (np.abs(target).sum() + 1e-8)
    
    # Compute final error
    final_mse = np.mean((fitted_norm - target_norm)**2)
    max_error = np.max(np.abs(fitted_norm - target_norm))
    
    print()
    print("="*60)
    print("RESULTS")
    print("="*60)
    print(f"Final MSE Loss:      {final_mse:.6f}")
    print(f"Max Absolute Error:  {max_error:.6f}")
    print(f"Initial Loss:        {losses[0]:.6f}")
    print(f"Loss Reduction:      {losses[0] - losses[-1]:.6f}")
    print()
    
    # Visual assessment
    if final_mse < 0.001:
        assessment = "EXCELLENT - Genome can closely approximate Gaussian Ring"
    elif final_mse < 0.01:
        assessment = "GOOD - Genome captures the main structure"
    elif final_mse < 0.1:
        assessment = "MODERATE - Genome captures some structure but not precise"
    else:
        assessment = "POOR - Genome cannot approximate Gaussian Ring well"
    
    print(f"Visual Assessment: {assessment}")
    print()
    
    # Conclusion
    print("="*60)
    print("CONCLUSION")
    print("="*60)
    if final_mse < 0.01:
        print("[PASS] The 33-parameter genome CAN express known-good kernels.")
        print("  Representation capacity is SUFFICIENT.")
        print("  The evolution bottleneck is likely elsewhere:")
        print("    - Fitness function design")
        print("    - Evolutionary operators (mutation/crossover)")
        print("    - Selection pressure")
    else:
        print("[FAIL] The 33-parameter genome CANNOT express Gaussian Ring well.")
        print("  Representation capacity is INSUFFICIENT.")
        print("  Recommendations:")
        print("    - Increase hidden layer size (2->16->1 or 2->32->1)")
        print("    - Add more hidden layers (2->8->8->1)")
        print("    - Use different activation functions")
        print("    - Consider direct kernel parameterization")
    print()
    
    # Visualization
    print("Saving visualization...")
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Target kernel
    ax = axes[0, 0]
    im = ax.imshow(target, cmap='viridis', interpolation='bilinear')
    ax.set_title('Target: Gaussian Ring\n(Orbium-style kernel)', fontsize=12, fontweight='bold')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    plt.colorbar(im, ax=ax, fraction=0.046)
    
    # Fitted kernel
    ax = axes[0, 1]
    im = ax.imshow(fitted_norm, cmap='viridis', interpolation='bilinear')
    ax.set_title(f'Fitted Genome Kernel\n(MSE={final_mse:.6f})', fontsize=12, fontweight='bold')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    plt.colorbar(im, ax=ax, fraction=0.046)
    
    # Difference map
    ax = axes[1, 0]
    diff = fitted_norm - target_norm
    im = ax.imshow(diff, cmap='RdBu_r', interpolation='bilinear', 
                   vmin=-max_error, vmax=max_error)
    ax.set_title('Difference Map\n(Fitted - Target)', fontsize=12, fontweight='bold')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    plt.colorbar(im, ax=ax, fraction=0.046)
    
    # Loss curve
    ax = axes[1, 1]
    ax.plot(losses, linewidth=2)
    ax.set_xlabel('Iteration', fontsize=11)
    ax.set_ylabel('MSE Loss', fontsize=11)
    ax.set_title('Optimization Progress', fontsize=12, fontweight='bold')
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0.01, color='r', linestyle='--', alpha=0.5, label='Good threshold')
    ax.axhline(y=0.1, color='orange', linestyle='--', alpha=0.5, label='Moderate threshold')
    ax.legend()
    
    plt.suptitle('Kernel Fitting Test: Genome vs Gaussian Ring', 
                 fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    output_path = Path('D:/openclaw_workspace/output/evo_lenia_demo/kernel_fitting_test.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"[OK] Saved to: {output_path}")
    print()
    print("Done!")
    
    return final_mse, assessment


if __name__ == '__main__':
    main()
