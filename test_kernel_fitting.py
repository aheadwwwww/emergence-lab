#!/usr/bin/env python3
"""
Test script for evolutionary Lenia kernel fitting.
Tests whether the Genome representation can express known-good kernels.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import os

# =============================================================================
# Genome-based Kernel Generation
# =============================================================================

def chebyshev_pairs(n_pairs):
    """Generate Chebyshev node pairs for radii and amplitudes."""
    if n_pairs == 0:
        return np.array([]), np.array([])
    
    # Chebyshev nodes of second kind on [0, 1], excluding endpoints
    k = np.arange(1, n_pairs + 1)
    nodes = 0.5 * (1 - np.cos(np.pi * k / (n_pairs + 1)))
    return nodes

def genome_to_kernel(genome, size=64):
    """
    Convert a Genome to a 2D kernel.
    
    Genome format (33 params):
    - [0]: n_rings (0-8, discretized)
    - [1-8]: ring_radii (normalized to [0.1, 0.9])
    - [9-16]: ring_amplitudes (normalized to [-1, 1])
    - [17-24]: ring_widths (normalized to [0.02, 0.2])
    - [25-32]: reserved (set to 0 for now)
    """
    # Parse genome
    n_rings = int(np.clip(genome[0] * 8, 1, 8))
    
    # Radii: map from [0,1] to [0.1, 0.9]
    radii = genome[1:9][:n_rings] * 0.8 + 0.1
    
    # Amplitudes: map from [0,1] to [-1, 1]
    amplitudes = genome[9:17][:n_rings] * 2 - 1
    
    # Widths: map from [0,1] to [0.02, 0.2]
    widths = genome[17:25][:n_rings] * 0.18 + 0.02
    
    # Generate kernel
    center = size // 2
    y, x = np.ogrid[:size, :size]
    dist = np.sqrt((x - center)**2 + (y - center)**2) / center
    
    kernel = np.zeros((size, size))
    for r, a, w in zip(radii, amplitudes, widths):
        # Gaussian ring
        ring = np.exp(-((dist - r)**2) / (2 * w**2))
        kernel += a * ring
    
    # Normalize to sum to 1
    if np.abs(kernel.sum()) > 1e-8:
        kernel = kernel / np.abs(kernel.sum())
    
    return kernel

# =============================================================================
# Target Kernel: Gaussian Ring (Orbium-style)
# =============================================================================

def create_gaussian_ring_kernel(size=64, radius=0.5, width=0.15, amplitude=1.0):
    """Create a simple Gaussian ring kernel (Orbium-style)."""
    center = size // 2
    y, x = np.ogrid[:size, :size]
    dist = np.sqrt((x - center)**2 + (y - center)**2) / center
    
    kernel = amplitude * np.exp(-((dist - radius)**2) / (2 * width**2))
    
    # Normalize
    kernel = kernel / kernel.sum()
    
    return kernel

# =============================================================================
# Gradient Descent Fitting
# =============================================================================

def fit_genome_to_kernel(target_kernel, n_iterations=500, lr=0.05, seed=None):
    """
    Fit a Genome to a target kernel using gradient descent.
    
    Returns:
        genome: Optimized genome
        losses: Loss history
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Initialize random genome
    genome = np.random.rand(33)
    genome[0] = 0.5  # Start with ~4 rings
    
    losses = []
    
    for i in range(n_iterations):
        # Forward pass
        kernel = genome_to_kernel(genome)
        
        # Compute loss (MSE)
        loss = np.mean((kernel - target_kernel)**2)
        losses.append(loss)
        
        # Numerical gradient (finite differences)
        grad = np.zeros_like(genome)
        epsilon = 1e-5
        
        for j in range(33):
            genome_plus = genome.copy()
            genome_plus[j] += epsilon
            kernel_plus = genome_to_kernel(genome_plus)
            loss_plus = np.mean((kernel_plus - target_kernel)**2)
            
            grad[j] = (loss_plus - loss) / epsilon
        
        # Update genome
        genome = genome - lr * grad
        
        # Clip genome to valid range
        genome = np.clip(genome, 0, 1)
        
        if (i + 1) % 100 == 0:
            print(f"Iteration {i+1}/{n_iterations}, Loss: {loss:.6f}")
    
    return genome, losses

# =============================================================================
# Main Test
# =============================================================================

def main():
    print("=" * 60)
    print("Kernel Fitting Test for Evolutionary Lenia")
    print("=" * 60)
    
    # Create output directory
    output_dir = "output/evo_lenia_demo"
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 1: Create target kernel (Gaussian Ring - Orbium-style)
    print("\n[1] Creating target Gaussian Ring kernel...")
    target_kernel = create_gaussian_ring_kernel(
        size=64, 
        radius=0.5,    # Ring at center
        width=0.15,    # Ring width
        amplitude=1.0
    )
    print(f"    Target kernel shape: {target_kernel.shape}")
    print(f"    Target kernel sum: {target_kernel.sum():.4f}")
    
    # Step 2: Initialize and fit genome
    print("\n[2] Fitting Genome to target kernel...")
    print("    Using gradient descent: 500 iterations, lr=0.05")
    
    genome, losses = fit_genome_to_kernel(
        target_kernel,
        n_iterations=500,
        lr=0.05,
        seed=42
    )
    
    # Step 3: Generate fitted kernel
    print("\n[3] Generating fitted kernel from optimized genome...")
    fitted_kernel = genome_to_kernel(genome)
    
    # Step 4: Compute final metrics
    final_loss = np.mean((fitted_kernel - target_kernel)**2)
    max_diff = np.max(np.abs(fitted_kernel - target_kernel))
    
    print(f"\n[4] Final Results:")
    print(f"    Final MSE Loss: {final_loss:.6f}")
    print(f"    Max Absolute Difference: {max_diff:.6f}")
    
    # Parse optimized genome
    n_rings = int(np.clip(genome[0] * 8, 1, 8))
    print(f"    Optimized n_rings: {n_rings}")
    
    # Step 5: Visualization
    print("\n[5] Creating visualization...")
    
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    
    # Target kernel
    ax1 = axes[0]
    im1 = ax1.imshow(target_kernel, cmap='viridis', interpolation='nearest')
    ax1.set_title('Target Kernel\n(Gaussian Ring)', fontsize=11)
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    plt.colorbar(im1, ax=ax1, fraction=0.046)
    
    # Fitted kernel
    ax2 = axes[1]
    im2 = ax2.imshow(fitted_kernel, cmap='viridis', interpolation='nearest')
    ax2.set_title(f'Fitted Kernel\n(Genome, {n_rings} rings)', fontsize=11)
    ax2.set_xlabel('X')
    ax2.set_ylabel('Y')
    plt.colorbar(im2, ax=ax2, fraction=0.046)
    
    # Difference
    ax3 = axes[2]
    diff = fitted_kernel - target_kernel
    im3 = ax3.imshow(diff, cmap='RdBu', interpolation='nearest', 
                     vmin=-abs(diff).max(), vmax=abs(diff).max())
    ax3.set_title('Difference\n(Fitted - Target)', fontsize=11)
    ax3.set_xlabel('X')
    ax3.set_ylabel('Y')
    plt.colorbar(im3, ax=ax3, fraction=0.046)
    
    # Loss curve
    ax4 = axes[3]
    ax4.plot(losses, 'b-', linewidth=1.5)
    ax4.set_xlabel('Iteration', fontsize=11)
    ax4.set_ylabel('MSE Loss', fontsize=11)
    ax4.set_title(f'Loss Curve\n(Final: {final_loss:.6f})', fontsize=11)
    ax4.grid(True, alpha=0.3)
    ax4.set_yscale('log')
    
    plt.tight_layout()
    
    # Save
    output_path = os.path.join(output_dir, "kernel_fitting_test.png")
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"    Saved to: {output_path}")
    
    plt.close()
    
    # =============================================================================
    # Conclusion
    # =============================================================================
    print("\n" + "=" * 60)
    print("CONCLUSION")
    print("=" * 60)
    
    if final_loss < 1e-4:
        conclusion = "EXCELLENT: Genome representation is highly adequate."
        adequacy = "The representation can accurately express Gaussian Ring kernels."
    elif final_loss < 1e-3:
        conclusion = "GOOD: Genome representation is adequate."
        adequacy = "The representation can express Gaussian Ring kernels with minor deviation."
    elif final_loss < 1e-2:
        conclusion = "ACCEPTABLE: Genome representation has moderate limitation."
        adequacy = "The representation captures the structure but with noticeable error."
    else:
        conclusion = "POOR: Genome representation needs improvement."
        adequacy = "The representation cannot adequately express Gaussian Ring kernels."
    
    print(f"\nFinal Loss: {final_loss:.6f}")
    print(f"Verdict: {conclusion}")
    print(f"Assessment: {adequacy}")
    
    return final_loss, conclusion

if __name__ == "__main__":
    final_loss, conclusion = main()