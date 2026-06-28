"""
Test: Can the Genome class express known-good Lenia kernels?

Hypothesis: If gradient descent cannot find genome weights that produce
a Gaussian Ring kernel, then the representation is too limited.
"""

import numpy as np
import jax
import jax.numpy as jnp
from evolutionary_lenia import Genome, create_default_config
from lenia_jax import _make_disk_kernel_np
import matplotlib.pyplot as plt
from pathlib import Path

def make_gaussian_ring_kernel(R: int, mu: float = 0.5, sigma: float = 0.15) -> np.ndarray:
    """Create a Gaussian Ring kernel (Orbium-style)."""
    y, x = np.ogrid[-R:R+1, -R:R+1]
    r = np.sqrt(x*x + y*y) / R
    kernel = np.exp(-((r - mu)**2) / (2 * sigma**2))
    kernel[r > 1] = 0
    return kernel / kernel.sum()

def genome_to_kernel_array_jax(weights: jnp.ndarray, R: int) -> jnp.ndarray:
    """Extract the kernel array from genome weights using pure JAX ops."""
    w1 = weights[:16].reshape(8, 2)
    b1 = weights[16:24]
    w2 = weights[24:32].reshape(1, 8)
    b2 = weights[32:33]
    
    kernel_hw = 2 * R + 1
    y, x = jnp.mgrid[-R:R+1, -R:R+1]
    r = jnp.sqrt(x*x + y*y)
    theta = jnp.arctan2(y, x)
    r_norm = r / (R + 1e-8)
    theta_norm = (theta + jnp.pi) / (2 * jnp.pi)
    
    # Vectorized computation
    inp = jnp.stack([r_norm, theta_norm], axis=-1)  # (H, W, 2)
    h = jnp.tanh(jnp.einsum('ij,hwj->hwi', w1, inp) + b1)  # (H, W, 8)
    kernel = jnp.tanh(jnp.einsum('ij,hwj->hwi', w2, h) + b2).squeeze(-1)  # (H, W)
    
    # Mask outside disk
    mask = r <= R
    kernel = jnp.where(mask, kernel, 0.0)
    
    return kernel

def fit_genome_to_kernel(target_kernel: np.ndarray, R: int, n_iters: int = 1000, lr: float = 0.1):
    """Use gradient descent to fit genome weights to match target kernel."""
    
    target_jax = jnp.array(target_kernel)
    
    def loss_fn(weights):
        pred_kernel = genome_to_kernel_array_jax(weights, R)
        
        # Normalize both for fair comparison
        pred_norm = pred_kernel / (jnp.abs(pred_kernel).sum() + 1e-8)
        target_norm = target_jax / (jnp.abs(target_jax).sum() + 1e-8)
        
        return jnp.mean((pred_norm - target_norm)**2)
    
    # JAX gradient
    loss_and_grad = jax.value_and_grad(loss_fn)
    
    weights = np.random.randn(33).astype(np.float32) * 0.5
    losses = []
    
    for i in range(n_iters):
        loss, grad = loss_and_grad(weights)
        losses.append(float(loss))
        weights = weights - lr * np.array(grad)
        
        if i % 100 == 0:
            print(f"Iter {i}: loss = {loss:.6f}")
    
    return Genome(weights), losses

# Run test
if __name__ == "__main__":
    Path("output/evo_lenia_demo").mkdir(parents=True, exist_ok=True)
    
    print("Testing genome representation expressiveness...")
    print("Target: Gaussian Ring kernel (Orbium-style)")
    
    R = 15
    target = make_gaussian_ring_kernel(R)
    fitted_genome, losses = fit_genome_to_kernel(target, R, n_iters=500, lr=0.05)
    
    # Visualize
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    # Target
    ax = axes[0]
    im = ax.imshow(target, cmap='viridis')
    ax.set_title('Target: Gaussian Ring')
    plt.colorbar(im, ax=ax)
    
    # Fitted (using JAX version)
    fitted_kernel = np.array(genome_to_kernel_array_jax(fitted_genome.weights, R))
    ax = axes[1]
    im = ax.imshow(fitted_kernel, cmap='viridis')
    ax.set_title(f'Fitted Genome (loss={losses[-1]:.4f})')
    plt.colorbar(im, ax=ax)
    
    # Loss curve
    ax = axes[2]
    ax.plot(losses)
    ax.set_xlabel('Iteration')
    ax.set_ylabel('MSE Loss')
    ax.set_title('Fitting Progress')
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_path = 'output/evo_lenia_demo/kernel_fitting_test.png'
    plt.savefig(output_path, dpi=150)
    print(f"\nSaved: {output_path}")
    
    print(f"\n{'='*60}")
    print(f"FINAL RESULT: loss = {losses[-1]:.6f}")
    print(f"{'='*60}")
    if losses[-1] > 0.1:
        print("FAIL: Genome representation is TOO LIMITED")
        print("   The 33-parameter NN cannot express a Gaussian Ring kernel.")
        print("   Recommendation: Increase genome size or change architecture.")
    elif losses[-1] > 0.01:
        print("PARTIAL: Genome can approximate but not perfectly match.")
        print("   Consider increasing hidden layer size (8 -> 16).")
    else:
        print("SUCCESS: Genome can express known-good kernels.")
        print("   The bottleneck is elsewhere (fitness function, evolution params).")
    print(f"{'='*60}")
