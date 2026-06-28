"""
Depth 2 Experiment: Kernel Representation Diagnosis

Hypothesis: The 33-parameter genome (2->8->1 NN) cannot express
radially-symmetric kernels like the Gaussian Ring used by Orbium.

This experiment tests:
1. Can gradient descent fit genome weights to match a known-good kernel?
2. What is the minimum loss achievable?

If loss remains high, the representation is the bottleneck.

Based on Depth 1 findings:
- Best score stuck at 11.67 across 5 generations
- Orbium seed: survival=0.2 (dies immediately), score=0.0
- Random seed: survival=1.0, score=5.84 (stable but boring)
- Conclusion: Evolution rewards stability, not emergence
"""

import numpy as np
import jax
import jax.numpy as jnp
import matplotlib.pyplot as plt
from pathlib import Path
import json

# ============== Genome Class (from evolutionary_lenia.py) ==============

class Genome:
    def __init__(self, weights):
        self.weights = np.array(weights, dtype=np.float32)
        self.n = len(weights)

    def split_layers(self):
        w1 = self.weights[:16].reshape(8, 2)
        b1 = self.weights[16:24]
        w2 = self.weights[24:32].reshape(1, 8)
        b2 = self.weights[32:33]
        return w1, b1, w2, b2

    def to_kernel_array(self, R=15):
        """Convert genome to kernel array (for visualization)."""
        w1, b1, w2, b2 = self.split_layers()
        
        kernel_hw = 2 * R + 1
        y, x = np.ogrid[-R:R+1, -R:R+1]
        r = np.sqrt(x*x + y*y)
        theta = np.arctan2(y, x)
        r_norm = r / (R + 1e-8)
        theta_norm = (theta + np.pi) / (2 * np.pi)
        mask = r <= R
        
        kernel = np.zeros((kernel_hw, kernel_hw), dtype=np.float32)
        for i in range(kernel_hw):
            for j in range(kernel_hw):
                if mask[i, j]:
                    inp = np.array([r_norm[i,j], theta_norm[i,j]])
                    h = np.tanh(w1 @ inp + b1)
                    kernel[i, j] = float(np.tanh(w2 @ h + b2).item())
        
        # Normalize
        kernel = kernel / (np.abs(kernel).sum() + 1e-8)
        return kernel

# ============== Target Kernels ==============

def make_gaussian_ring_kernel(R=15, mu=0.5, sigma=0.15):
    """Orbium-style Gaussian Ring kernel."""
    y, x = np.ogrid[-R:R+1, -R:R+1]
    r = np.sqrt(x*x + y*y) / R
    kernel = np.exp(-((r - mu)**2) / (2 * sigma**2))
    kernel[r > 1] = 0
    return kernel / kernel.sum()

def make_gaussian_blob_kernel(R=15, sigma=0.3):
    """Simple Gaussian blob kernel."""
    y, x = np.ogrid[-R:R+1, -R:R+1]
    r = np.sqrt(x*x + y*y) / R
    kernel = np.exp(-(r**2) / (2 * sigma**2))
    kernel[r > 1] = 0
    return kernel / kernel.sum()

def make_donut_kernel(R=15, inner_r=0.3, outer_r=0.7):
    """Hard donut kernel (step function)."""
    y, x = np.ogrid[-R:R+1, -R:R+1]
    r = np.sqrt(x*x + y*y) / R
    kernel = np.where((r >= inner_r) & (r <= outer_r), 1.0, 0.0)
    kernel[r > 1] = 0
    return kernel / (kernel.sum() + 1e-8)

# ============== Gradient Descent Fitting ==============

def fit_genome_to_kernel(target_kernel, R=15, n_iters=2000, lr=0.05):
    """Use gradient descent to fit genome weights to match target kernel."""
    
    # Precompute grid coordinates (JAX arrays)
    kernel_hw = 2 * R + 1
    y, x = jnp.ogrid[-R:R+1, -R:R+1]
    r_grid = jnp.sqrt(x*x + y*y)
    theta_grid = jnp.arctan2(y, x)
    r_norm_grid = r_grid / (R + 1e-8)
    theta_norm_grid = (theta_grid + jnp.pi) / (2 * jnp.pi)
    mask_grid = r_grid <= R
    
    # Target as JAX array
    target_jax = jnp.array(target_kernel, dtype=jnp.float32)
    target_norm = target_jax / (jnp.abs(target_jax).sum() + 1e-8)
    
    def loss_fn(weights):
        """Pure JAX loss function."""
        w1 = weights[:16].reshape((8, 2))
        b1 = weights[16:24]
        w2 = weights[24:32].reshape((1, 8))
        b2 = weights[32:33]
        
        # Build kernel via NN evaluation at each grid point
        kernel = jnp.zeros((kernel_hw, kernel_hw), dtype=jnp.float32)
        
        # Vectorized computation over all grid points
        def compute_pixel(i, j):
            r_val = r_norm_grid[i, j]
            theta_val = theta_norm_grid[i, j]
            inp = jnp.array([r_val, theta_val])
            h = jnp.tanh(w1 @ inp + b1)
            return jnp.tanh(w2 @ h + b2)[0]
        
        # Use vmap for vectorization
        i_vals = jnp.arange(kernel_hw)
        j_vals = jnp.arange(kernel_hw)
        
        def row_kernel(i):
            return jax.vmap(lambda j: compute_pixel(i, j))(j_vals)
        
        kernel = jax.vmap(row_kernel)(i_vals)
        kernel = kernel * mask_grid  # Apply circular mask
        
        # Normalize
        pred_norm = kernel / (jnp.abs(kernel).sum() + 1e-8)
        
        return jnp.mean((pred_norm - target_norm)**2)
    
    # JAX gradient
    loss_and_grad = jax.value_and_grad(loss_fn)
    
    # Initialize
    key = jax.random.PRNGKey(42)
    weights = jax.random.normal(key, (33,)) * 0.5
    losses = []
    best_weights = weights
    best_loss = float('inf')
    
    for i in range(n_iters):
        loss, grad = loss_and_grad(weights)
        loss_val = float(loss)
        losses.append(loss_val)
        
        if loss_val < best_loss:
            best_loss = loss_val
            best_weights = weights
        
        weights = weights - lr * grad
        
        # Learning rate decay
        if i > 0 and i % 500 == 0:
            lr *= 0.5
    
    return Genome(np.array(best_weights)), losses, best_loss

# ============== Main Experiment ==============

def run_diagnosis():
    """Run the kernel representation diagnosis."""
    print("=" * 60)
    print("Depth 2: Kernel Representation Diagnosis")
    print("=" * 60)
    print()
    print("Testing: Can the 33-param genome express known-good kernels?")
    print()
    
    R = 15
    output_dir = Path("output/evo_lenia_depth2")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Test kernels
    kernels = {
        "gaussian_ring": make_gaussian_ring_kernel(R, mu=0.5, sigma=0.15),
        "gaussian_blob": make_gaussian_blob_kernel(R, sigma=0.3),
        "donut": make_donut_kernel(R, inner_r=0.3, outer_r=0.7),
    }
    
    results = {}
    
    for name, target in kernels.items():
        print(f"\nFitting to {name}...")
        
        # Multiple restarts to find best fit
        best_genome = None
        best_loss = float('inf')
        all_losses = []
        
        for restart in range(3):
            genome, losses, final_loss = fit_genome_to_kernel(
                target, R, n_iters=2000, lr=0.05
            )
            all_losses.append(losses)
            
            if final_loss < best_loss:
                best_loss = final_loss
                best_genome = genome
        
        results[name] = {
            "genome": best_genome,
            "loss": best_loss,
            "losses": all_losses[0],  # Use first run for plotting
            "target": target,
            "fitted": best_genome.to_kernel_array(R),
        }
        
        print(f"  Best loss: {best_loss:.6f}")
        
        if best_loss < 0.01:
            print(f"  ✓ EXCELLENT fit - representation is sufficient")
        elif best_loss < 0.05:
            print(f"  ○ GOOD fit - representation can approximate")
        elif best_loss < 0.1:
            print(f"  △ MODERATE fit - representation is limited")
        else:
            print(f"  ✗ POOR fit - representation cannot express this kernel")
    
    # Visualization
    fig, axes = plt.subplots(3, 4, figsize=(16, 12))
    
    for i, (name, res) in enumerate(results.items()):
        # Target kernel
        ax = axes[i, 0]
        im = ax.imshow(res["target"], cmap='viridis')
        ax.set_title(f'Target: {name}')
        ax.axis('off')
        plt.colorbar(im, ax=ax, fraction=0.046)
        
        # Fitted kernel
        ax = axes[i, 1]
        fitted = res["fitted"]
        im = ax.imshow(fitted, cmap='viridis')
        ax.set_title(f'Fitted (loss={res["loss"]:.4f})')
        ax.axis('off')
        plt.colorbar(im, ax=ax, fraction=0.046)
        
        # Difference
        ax = axes[i, 2]
        diff = np.abs(res["target"] - fitted)
        im = ax.imshow(diff, cmap='hot')
        ax.set_title('|Error|')
        ax.axis('off')
        plt.colorbar(im, ax=ax, fraction=0.046)
        
        # Loss curve
        ax = axes[i, 3]
        ax.plot(res["losses"])
        ax.set_xlabel('Iteration')
        ax.set_ylabel('MSE Loss')
        ax.set_title('Fitting Progress')
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3)
    
    plt.suptitle('Depth 2: Genome Kernel Representation Analysis', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_dir / 'kernel_fitting_analysis.png', dpi=150)
    plt.close()
    
    # Save results
    summary = {
        "experiment": "depth2_kernel_diagnosis",
        "conclusion": "",
        "kernel_results": {}
    }
    
    for name, res in results.items():
        summary["kernel_results"][name] = {
            "final_loss": res["loss"],
            "can_express": res["loss"] < 0.1
        }
    
    # Determine conclusion
    all_losses = [res["loss"] for res in results.values()]
    avg_loss = np.mean(all_losses)
    
    if avg_loss < 0.05:
        summary["conclusion"] = "Representation is adequate. Problem lies elsewhere (fitness function or GA parameters)."
    elif avg_loss < 0.1:
        summary["conclusion"] = "Representation is moderately limited. Consider increasing NN capacity (more hidden units)."
    else:
        summary["conclusion"] = "Representation is insufficient. The 2->8->1 NN cannot express radially-symmetric kernels well."
    
    with open(output_dir / "diagnosis_results.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "=" * 60)
    print("DIAGNOSIS COMPLETE")
    print("=" * 60)
    print(f"\nAverage loss: {avg_loss:.4f}")
    print(f"\nConclusion: {summary['conclusion']}")
    print(f"\nResults saved to: {output_dir}")
    
    return results, summary

if __name__ == "__main__":
    results, summary = run_diagnosis()
