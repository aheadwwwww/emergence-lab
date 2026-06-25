"""
RDL: Reaction-Diffusion-Lenia Hybrid
Combines Gray-Scott reaction-diffusion with Lenia's growth function.

Key insight: Lenia's bell-shaped growth function creates a "life zone"
that Gray-Scott's cubic growth cannot express.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import convolve

# ============================================================
# Kernels
# ============================================================

def gaussian_kernel(R, sigma=None):
    """Gaussian kernel for smooth diffusion."""
    if sigma is None:
        sigma = R / 3.0
    size = 2 * R + 1
    x = np.arange(size) - R
    k1 = np.exp(-x**2 / (2 * sigma**2))
    k2d = np.outer(k1, k1)
    return k2d / k2d.sum()

def lenia_kernel(R, kn=0):
    """Lenia kernel: disk with smooth edge."""
    y, x = np.ogrid[-R:R+1, -R:R+1]
    dist = np.sqrt(x*x + y*y) / R
    dist = np.clip(dist, 0, 1)
    
    eps = 1e-8
    r = np.clip(dist, eps, 1 - eps)
    
    if kn == 0:
        kernel = (4 * r * (1 - r))**4
    else:
        kernel = np.exp(4.0 - 1.0 / (r * (1 - r)))
    
    mask = dist <= 1.0
    kernel = kernel * mask
    return kernel / (kernel.sum() + eps)

# ============================================================
# Lenia Growth Function
# ============================================================

def lenia_growth(U, mu, sigma):
    """Gaussian bell growth: 2*exp(-(U-mu)^2/(2*sigma^2)) - 1"""
    return np.exp(-((U - mu)**2) / (2 * sigma**2)) * 2 - 1

# ============================================================
# Laplacian
# ============================================================

def laplacian(field):
    """Discrete Laplacian using 5-point stencil."""
    lap = np.zeros_like(field)
    lap[1:-1, 1:-1] = (
        field[:-2, 1:-1] + field[2:, 1:-1] +
        field[1:-1, :-2] + field[1:-1, 2:] -
        4 * field[1:-1, 1:-1]
    )
    return lap

# ============================================================
# Classic Gray-Scott (for comparison)
# ============================================================

def gray_scott_step(U, V, Du=0.16, Dv=0.08, F=0.035, k=0.065):
    """Classic Gray-Scott step."""
    Lu = laplacian(U)
    Lv = laplacian(V)
    uvv = U * V * V
    U_new = U + (Du * Lu - uvv + F * (1 - U))
    V_new = V + (Dv * Lv + uvv - (F + k) * V)
    return np.clip(U_new, 0, 1), np.clip(V_new, 0, 1)

# ============================================================
# RDL: Reaction-Diffusion-Lenia
# ============================================================

def rdl_step(A, B, kernel_A, kernel_B, params, dt=0.1):
    """
    Reaction-Diffusion-Lenia step.
    
    A: "activator" - autocatalytic, produces pattern
    B: "inhibitor" - counterbalances A, creates Turing instability
    
    params: dict with
        mu_A, sigma_A: Lenia growth params for A
        mu_B, sigma_B: Lenia growth params for B
        D_A, D_B: diffusion rates
        feed, kill: Gray-Scott rates
        alpha_AB: A influence on B growth (-1 to 1)
        alpha_BA: B influence on A growth (-1 to 1)
    """
    D_A, D_B = params['D_A'], params['D_B']
    mu_A, sigma_A = params['mu_A'], params['sigma_A']
    mu_B, sigma_B = params['mu_B'], params['sigma_B']
    feed, kill_rate = params['feed'], params['kill']
    alpha_AB = params.get('alpha_AB', 0.0)
    alpha_BA = params.get('alpha_BA', 0.0)
    
    # Convolve with Lenia kernels to get "potential"
    U_A = convolve(A, kernel_A, mode='wrap')
    U_B = convolve(B, kernel_B, mode='wrap')
    
    # Lenia growth with cross-coupling
    G_A = lenia_growth(U_A + alpha_BA * U_B, mu_A, sigma_A)
    G_B = lenia_growth(U_B + alpha_AB * U_A, mu_B, sigma_B)
    
    # Reaction-Diffusion
    dA = D_A * laplacian(A) + G_A * dt
    dB = D_B * laplacian(B) + G_B * dt
    
    # Gray-Scott terms (A autocatalyzes, B inhibits A)
    A_new = A + dA - feed * A * B * dt
    B_new = B + dB + feed * A * B * dt - kill_rate * B * dt
    
    return np.clip(A_new, 0, 1), np.clip(B_new, 0, 1)

# ============================================================
# Run experiments
# ============================================================

def run_rdl(size=128, steps=2000, params=None):
    """Run RDL simulation."""
    if params is None:
        params = {
            'R_A': 13, 'R_B': 13,
            'mu_A': 0.15, 'sigma_A': 0.015,
            'mu_B': 0.10, 'sigma_B': 0.020,
            'D_A': 0.12, 'D_B': 0.06,
            'feed': 0.04, 'kill': 0.06,
            'alpha_AB': 0.02, 'alpha_BA': -0.02,
        }
    
    R_A, R_B = params['R_A'], params['R_B']
    kernel_A = lenia_kernel(R_A)
    kernel_B = lenia_kernel(R_B)
    
    # Initialize: random A, uniform B
    np.random.seed(42)
    A = np.random.random((size, size)) * 0.1
    B = np.zeros((size, size))
    # Add a central perturbation
    center = size // 2
    rng = size // 10
    y, x = np.ogrid[-rng:rng+1, -rng:rng+1]
    mask = (x**2 + y**2) <= rng**2
    A[center-rng:center+rng+1, center-rng:center+rng+1][mask] = 0.5 + np.random.random(mask.sum()) * 0.3
    B[center-rng:center+rng+1, center-rng:center+rng+1][mask] = 0.25
    
    history = {'A': [], 'B': []}
    record_every = steps // 10 
    
    for step in range(steps):
        A, B = rdl_step(A, B, kernel_A, kernel_B, params)
        
        if step % record_every == 0:
            history['A'].append(A.copy())
            history['B'].append(B.copy())
    
    history['A'].append(A.copy())
    history['B'].append(B.copy())
    
    return A, B, history

def compare_rd_vs_rdl():
    """Compare classic Gray-Scott with RDL."""
    size = 128
    steps = 1000
    
    print("=" * 60)
    print("Comparing Gray-Scott vs RDL Hybrid")
    print("=" * 60)
    
    # Classic Gray-Scott
    print("\nRunning classic Gray-Scott...")
    np.random.seed(42)
    U = np.ones((size, size)) * 1.0
    V = np.zeros((size, size))
    center = size // 2
    rng = 10
    V[center-rng:center+rng, center-rng:center+rng] = 0.25
    U[center-rng:center+rng, center-rng:center+rng] = 0.5
    
    for _ in range(steps):
        U, V = gray_scott_step(U, V)
    
    gs_alive = (V > 0.01).mean()
    print(f"  V alive ratio: {gs_alive:.3f}")
    
    # RDL
    print("\nRunning RDL hybrid...")
    params = {
        'R_A': 13, 'R_B': 13,
        'mu_A': 0.15, 'sigma_A': 0.015,
        'mu_B': 0.10, 'sigma_B': 0.020,
        'D_A': 0.12, 'D_B': 0.06,
        'feed': 0.04, 'kill': 0.06,
        'alpha_AB': 0.02, 'alpha_BA': -0.02,
    }
    A, B, history = run_rdl(size, steps, params)
    
    a_alive = (A > 0.01).mean()
    b_alive = (B > 0.01).mean()
    print(f"  A alive ratio: {a_alive:.3f}")
    print(f"  B alive ratio: {b_alive:.3f}")
    
    # Edge density (complexity measure)
    edge_A = np.mean(np.abs(A[1:, :] - A[:-1, :])) + np.mean(np.abs(A[:, 1:] - A[:, :-1]))
    edge_GS = np.mean(np.abs(V[1:, :] - V[:-1, :])) + np.mean(np.abs(V[:, 1:] - V[:, :-1]))
    print(f"\n  Edge density: GS={edge_GS:.4f}, RDL-A={edge_A:.4f}")
    
    # Visualize
    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    
    axes[0, 0].imshow(U, cmap='inferno')
    axes[0, 0].set_title('Gray-Scott U (feed)')
    axes[0, 0].axis('off')
    
    axes[0, 1].imshow(V, cmap='viridis')
    axes[0, 1].set_title(f'Gray-Scott V (chem)\nalive={gs_alive:.2f}')
    axes[0, 1].axis('off')
    
    axes[0, 2].text(0.5, 0.5, 'Gray-Scott\nParameters:\nDu=0.16, Dv=0.08\nF=0.035, k=0.065', 
                     ha='center', va='center', fontsize=10, transform=axes[0, 2].transAxes)
    axes[0, 2].axis('off')
    
    axes[1, 0].imshow(A, cmap='inferno')
    axes[1, 0].set_title(f'RDL A (activator)\nalive={a_alive:.2f}')
    axes[1, 0].axis('off')
    
    axes[1, 1].imshow(B, cmap='viridis')
    axes[1, 1].set_title(f'RDL B (inhibitor)\nalive={b_alive:.2f}')
    axes[1, 1].axis('off')
    
    axes[1, 2].text(0.5, 0.5, 'RDL Parameters:\nmu_A=0.15, sigma_A=0.015\nmu_B=0.10, sigma_B=0.020\nD_A=0.12, D_B=0.06\nfeed=0.04, kill=0.06\nα_AB=0.02, α_BA=-0.02', 
                     ha='center', va='center', fontsize=9, transform=axes[1, 2].transAxes)
    axes[1, 2].axis('off')
    
    plt.suptitle('Gray-Scott vs RDL (Reaction-Diffusion-Lenia)', fontsize=14)
    plt.tight_layout()
    plt.savefig('experiments/rdl_comparison.png', dpi=150, bbox_inches='tight')
    print(f"\nSaved: experiments/rdl_comparison.png")
    plt.close()
    
    return A, B, V, history

if __name__ == '__main__':
    print("Reaction-Diffusion-Lenia Hybrid")
    print("=" * 60)
    print("Combining Gray-Scott RD with Lenia's growth function\n")
    
    A, B, V, history = compare_rd_vs_rdl()
    
    print("\n" + "=" * 60)
    print("Done! Check experiments/rdl_comparison.png")
    print("=" * 60)
