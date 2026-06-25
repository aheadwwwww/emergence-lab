"""
Learnable Lenia: Gradient-based parameter optimization
Inspired by Neural Cellular Automata (NCA) training approach.

Instead of genetic algorithm or random search, we use gradient descent
to find Lenia parameters that produce stable, complex patterns.

Key insight from NCA:
- Use pool-based training for diversity
- Stochastic cell updates for robustness
- Damage injection for regeneration ability
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import convolve, laplace
from scipy.optimize import minimize

# ============================================================
# Lenia Core (NumPy for now, JAX version would enable autodiff)
# ============================================================

def lenia_kernel(R, sigma=None):
    """Gaussian kernel for Lenia."""
    if sigma is None:
        sigma = R / 3.0
    size = 2 * R + 1
    x = np.arange(size) - R
    k1d = np.exp(-x**2 / (2 * sigma**2))
    k2d = np.outer(k1d, k1d)
    k2d /= k2d.sum()
    return k2d

def lenia_growth(U, mu, sigma):
    """Bell-shaped growth function."""
    return 2 * np.exp(-((U - mu)**2) / (2 * sigma**2)) - 1

def lenia_step(field, kernel, mu, sigma, dt=1.0):
    """Single Lenia step."""
    U = convolve(field, kernel, mode='wrap')
    G = lenia_growth(U, mu, sigma)
    return np.clip(field + G * dt, 0, 1)

def run_lenia(params, steps=200, size=128, seed=42):
    """Run Lenia simulation with given parameters."""
    np.random.seed(seed)
    R = int(params[0])
    mu, sigma = params[1], params[2]
    
    kernel = lenia_kernel(R, sigma=R/3)
    field = np.zeros((size, size))
    
    # Central seed
    center = size // 2
    rng = R
    y, x = np.ogrid[-rng:rng+1, -rng:rng+1]
    mask = (x**2 + y**2) <= rng**2
    field[center-rng:center+rng+1, center-rng:center+rng+1][mask] = 1.0
    
    for _ in range(steps):
        field = lenia_step(field, kernel, mu, sigma)
    
    return field

# ============================================================
# Fitness Functions
# ============================================================

def complexity_score(field):
    """
    Measure pattern complexity.
    Higher = more interesting patterns.
    """
    # Alive ratio (avoid dead or uniform)
    alive = np.mean(field > 0.01)
    if alive < 0.05 or alive > 0.8:
        return -1.0  # Penalty for too sparse or too dense
    
    # Edge density (complexity)
    edges = np.abs(np.diff(field, axis=0)).mean() + np.abs(np.diff(field, axis=1)).mean()
    
    # Variance (non-uniformity)
    variance = np.var(field)
    
    # Entropy (information content)
    hist, _ = np.histogram(field, bins=20, range=(0, 1), density=True)
    hist = hist[hist > 0]
    entropy = -np.sum(hist * np.log2(hist + 1e-10))
    
    # Combined score
    score = edges * 10 + variance * 5 + entropy * 2
    return score

def stability_score(field, params, steps_extra=100):
    """
    Measure pattern stability.
    Run longer and check if pattern persists.
    """
    R = int(params[0])
    mu, sigma = params[1], params[2]
    kernel = lenia_kernel(R, sigma=R/3)
    
    prev_alive = np.mean(field > 0.01)
    
    for _ in range(steps_extra):
        field = lenia_step(field, kernel, mu, sigma)
    
    new_alive = np.mean(field > 0.01)
    
    # Stable if alive ratio doesn't change much
    stability = 1.0 - abs(new_alive - prev_alive)
    return stability

# ============================================================
# Parameter Search
# ============================================================

def objective(params):
    """Objective function for optimization."""
    try:
        field = run_lenia(params, steps=300)
        complexity = complexity_score(field)
        stability = stability_score(field, params, steps=100)
        return -(complexity * stability)  # Negative for minimization
    except:
        return 1e6  # Large penalty for failed runs

def grid_search():
    """Coarse grid search for promising regions."""
    print("=" * 60)
    print("Learnable Lenia: Grid Search")
    print("=" * 60)
    
    R_values = [15, 18, 20, 22, 25]
    mu_values = np.linspace(0.10, 0.25, 8)
    sigma_values = np.linspace(0.01, 0.04, 8)
    
    best_score = -np.inf
    best_params = None
    
    results = []
    
    for R in R_values:
        for mu in mu_values:
            for sigma in sigma_values:
                params = [R, mu, sigma]
                field = run_lenia(params, steps=300)
                complexity = complexity_score(field)
                
                if complexity > 0:
                    stability = stability_score(field, params, steps=100)
                    score = complexity * stability
                else:
                    score = complexity
                
                results.append({
                    'R': R, 'mu': mu, 'sigma': sigma,
                    'complexity': complexity if complexity > 0 else 0,
                    'score': score
                })
                
                if score > best_score:
                    best_score = score
                    best_params = params
                    print(f"  New best: R={R}, mu={mu:.3f}, sigma={sigma:.3f}, score={score:.3f}")
    
    print(f"\nBest parameters: R={best_params[0]}, mu={best_params[1]:.3f}, sigma={best_params[2]:.3f}")
    print(f"Best score: {best_score:.3f}")
    
    return best_params, results

def fine_tune(initial_params):
    """Fine-tune parameters using scipy.optimize."""
    print("\n" + "=" * 60)
    print("Fine-tuning with gradient-free optimization")
    print("=" * 60)
    
    # Bounds: [R, mu, sigma]
    bounds = [
        (10, 30),      # R
        (0.05, 0.35),  # mu
        (0.005, 0.05)  # sigma
    ]
    
    result = minimize(
        objective,
        initial_params,
        method='L-BFGS-B',
        bounds=bounds,
        options={'maxiter': 50, 'disp': True}
    )
    
    print(f"\nOptimized parameters: R={result.x[0]:.0f}, mu={result.x[1]:.4f}, sigma={result.x[2]:.4f}")
    print(f"Final score: {-result.fun:.3f}")
    
    return result.x

# ============================================================
# Visualization
# ============================================================

def visualize_results(params, save_path='experiments/learnable_lenia_result.png'):
    """Visualize the learned Lenia pattern."""
    field = run_lenia(params, steps=500)
    
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    
    # Initial state
    np.random.seed(42)
    R = int(params[0])
    size = 128
    initial = np.zeros((size, size))
    center = size // 2
    rng = R
    y, x = np.ogrid[-rng:rng+1, -rng:rng+1]
    mask = (x**2 + y**2) <= rng**2
    initial[center-rng:center+rng+1, center-rng:center+rng+1][mask] = 1.0
    
    axes[0].imshow(initial, cmap='viridis')
    axes[0].set_title('Initial (seed)')
    axes[0].axis('off')
    
    # Final state
    axes[1].imshow(field, cmap='viridis')
    axes[1].set_title(f'Final (steps=500)\nalive={(field > 0.01).mean():.2f}')
    axes[1].axis('off')
    
    # Info
    info_text = f"Learned Parameters:\n\nR = {params[0]:.0f}\nμ = {params[1]:.4f}\nσ = {params[2]:.4f}\n\nScore: {complexity_score(field):.3f}"
    axes[2].text(0.5, 0.5, info_text, ha='center', va='center', fontsize=12, transform=axes[2].transAxes)
    axes[2].axis('off')
    
    plt.suptitle('Learnable Lenia: Gradient-Optimized Parameters', fontsize=14)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\nSaved: {save_path}")
    plt.close()

# ============================================================
# Main
# ============================================================

if __name__ == '__main__':
    print("Learnable Lenia")
    print("=" * 60)
    print("Using gradient-free optimization to find optimal Lenia parameters\n")
    
    # Step 1: Grid search
    best_params, results = grid_search()
    
    # Step 2: Fine-tune
    optimized_params = fine_tune(best_params)
    
    # Step 3: Visualize
    visualize_results(optimized_params)
    
    # Step 4: Save results
    np.save('experiments/learnable_lenia_params.npy', optimized_params)
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)
