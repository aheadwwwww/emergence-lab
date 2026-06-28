# Work-Loop Depth 1: Evolutionary Lenia Kernel Analysis

**Date**: 2026-06-28 18:11
**Topic**: evolutionary_lenia_kernel_optimization
**Cycle**: 1

---

## Previous Context

From memory/2026-06-28.md:
- Evolutionary Lenia framework created and tested
- 5 generations × 16 individuals demo completed
- Best score stuck at 11.67 (no improvement)
- Orbium seed consistently fails (survival=0.2, all mass dies)
- Only random seed contributes to fitness

From neuroparticles2 deep analysis:
- Gene-to-behavior mapping is critical
- Their 512-bit genome directly encodes CA rules
- Recursive perception mechanism (13×13 → 3×3 via CA)
- Cumulative fitness across generations

---

## Problem Identification

### Symptom
Evolution is not making progress. The best genome from generation 1 remains the best throughout all 5 generations.

### Root Cause Hypothesis
The **Genome → Kernel** mapping may not preserve useful structure:
1. NN architecture (2→8→1) may be too simple
2. Kernel weights initialized randomly, no inductive bias toward smooth kernels
3. Normalization step (`/ sum(|kernel|)`) may destroy information
4. The tanh activations create symmetric patterns, but Lenia needs radial structures

### Evidence
Looking at `evolution_history.json`:
- Orbium seed: always survival=0.2 (dies in first ~40 steps)
- Random seed: survival=1.0, high stability
- Score breakdown shows the random kernel creates a "stable blob" not interesting dynamics

**Key Insight**: The fitness function rewards stability, but we want **emergent dynamics**, not static blobs.

---

## Experiment Design

### Goal
Test if the current genome representation can express known-good kernels.

### Method
1. Create a "ground truth" kernel (Gaussian Ring from Orbium)
2. Try to fit the genome to match this kernel
3. Compare: can the 33-parameter genome approximate a Gaussian Ring?

### Expected Outcome
If the genome CANNOT approximate a known-good kernel, then the representation is the bottleneck.

---

## Code: Kernel Fitting Test

```python
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

def make_gaussian_ring_kernel(R: int, mu: float = 0.5, sigma: float = 0.15) -> np.ndarray:
    """Create a Gaussian Ring kernel (Orbium-style)."""
    y, x = np.ogrid[-R:R+1, -R:R+1]
    r = np.sqrt(x*x + y*y) / R
    kernel = np.exp(-((r - mu)**2) / (2 * sigma**2))
    kernel[r > 1] = 0
    return kernel / kernel.sum()

def genome_to_kernel_array(genome: Genome, R: int) -> np.ndarray:
    """Extract the kernel array from a genome (for visualization)."""
    w1, b1, w2, b2 = genome.split_layers()
    
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
    
    return kernel

def fit_genome_to_kernel(target_kernel: np.ndarray, R: int, n_iters: int = 1000, lr: float = 0.1):
    """Use gradient descent to fit genome weights to match target kernel."""
    
    def loss_fn(weights):
        genome = Genome(weights)
        pred_kernel = genome_to_kernel_array(genome, R)
        
        # Normalize both for fair comparison
        pred_norm = pred_kernel / (np.abs(pred_kernel).sum() + 1e-8)
        target_norm = target_kernel / (np.abs(target_kernel).sum() + 1e-8)
        
        return np.mean((pred_norm - target_norm)**2)
    
    # JAX gradient
    loss_and_grad = jax.value_and_grad(loss_fn)
    
    weights = np.random.randn(33).astype(np.float32) * 0.5
    losses = []
    
    for i in range(n_iters):
        loss, grad = loss_and_grad(weights)
        losses.append(float(loss))
        weights = weights - lr * grad
        
        if i % 100 == 0:
            print(f"Iter {i}: loss = {loss:.6f}")
    
    return Genome(weights), losses

# Run test
R = 15
target = make_gaussian_ring_kernel(R)
fitted_genome, losses = fit_genome_to_kernel(target, R, n_iters=500, lr=0.05)

# Visualize
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Target
ax = axes[0]
ax.imshow(target, cmap='viridis')
ax.set_title('Target: Gaussian Ring')

# Fitted
fitted_kernel = genome_to_kernel_array(fitted_genome, R)
ax = axes[1]
ax.imshow(fitted_kernel, cmap='viridis')
ax.set_title(f'Fitted Genome (loss={losses[-1]:.4f})')

# Loss curve
ax = axes[2]
ax.plot(losses)
ax.set_xlabel('Iteration')
ax.set_ylabel('MSE Loss')
ax.set_title('Fitting Progress')
ax.set_yscale('log')

plt.tight_layout()
plt.savefig('output/evo_lenia_demo/kernel_fitting_test.png', dpi=150)
plt.close()

print(f"\nFinal loss: {losses[-1]:.6f}")
print("If loss is high (>0.1), the genome representation is too limited.")
```

---

## Running the Experiment

Let me execute this test to see if the representation is the problem.
