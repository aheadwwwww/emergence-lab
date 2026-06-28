"""
Homeostatic Lenia - inspired by xagent's predictive processing paradigm.

Core idea: Instead of optimizing for external reward (survival score),
let Lenia patterns self-organize to maintain internal homeostasis.

Based on:
- xagent: free energy principle, minimize surprise
- Lenia: continuous CA with smooth kernels
- Isotropic NCA: stochastic updates enable survival

Implementation:
1. Track "expected state" (rolling average of past states)
2. Compute "surprise" = distance from expected state
3. Homeostatic pressure = surprise gradient
4. Pattern behavior emerges from minimizing surprise
"""

import jax
import jax.numpy as jnp
import numpy as np
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from lenia_jax import make_kernel_fft, make_orbium

OUTPUT_DIR = Path('D:/openclaw_workspace/experiments/output/homeostatic_lenia')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# Homeostatic Pressure
# ============================================================================

def compute_surprise(state, expected_state):
    """Surprise = KL divergence (simplified to L2 distance)."""
    return jnp.sum((state - expected_state) ** 2)

def update_expected_state(expected_state, new_state, alpha=0.01):
    """Rolling average with decay."""
    return alpha * new_state + (1 - alpha) * expected_state

# ============================================================================
# Homeostatic Lenia Step
# ============================================================================

@jax.jit
def homeostatic_lenia_step(state, kernel_fft, expected_state, mu, sigma, alpha=0.01):
    """
    Single step of homeostatic Lenia.
    
    State update influenced by:
    1. Standard Lenia dynamics (kernel + growth)
    2. Homeostatic pressure (move toward expected state)
    """
    # Standard Lenia step
    A = jnp.fft.fft2(state)
    U = jnp.real(jnp.fft.ifft2(kernel_fft * A))
    n_potential = jnp.clip(U, 0, 1)
    growth = jnp.exp(-((n_potential - mu)**2) / (2 * sigma**2)) * 2 - 1
    new_state = jnp.clip(state + 0.1 * growth, 0, 1)
    
    # Homeostatic pressure
    surprise = compute_surprise(new_state, expected_state)
    homeostatic_correction = 0.01 * (expected_state - new_state)
    
    # Blend
    corrected_state = jnp.clip(new_state + homeostatic_correction, 0, 1)
    
    # Update expected state
    new_expected = update_expected_state(expected_state, corrected_state, alpha)
    
    return corrected_state, new_expected, surprise

# ============================================================================
# Simulation
# ============================================================================

def run_homeostatic_lenia(R=15, mu=0.15, sigma=0.015, size=128, steps=500, seed='orbium', alpha=0.01):
    """Run homeostatic Lenia simulation."""
    # Initialize
    kernel_fft = make_kernel_fft((size, size), R)
    state = make_orbium((size, size))
    
    # Expected state starts as initial state
    expected_state = state.copy()
    
    # Track metrics
    surprises = []
    entropies = []
    alive_ratios = []
    
    print(f"Running homeostatic Lenia: R={R}, mu={mu}, sigma={sigma}, alpha={alpha}")
    
    for step in range(steps):
        state, expected_state, surprise = homeostatic_lenia_step(
            state, kernel_fft, expected_state, mu, sigma, alpha
        )
        
        # Metrics
        surprises.append(float(surprise))
        ent = -jnp.sum(state * jnp.log(state + 1e-10))
        entropies.append(float(ent))
        alive_ratios.append(float(jnp.mean(state > 0.1)))
        
        if step % 100 == 0:
            print(f"  Step {step}: surprise={surprise:.2f}, entropy={ent:.2f}, alive={alive_ratios[-1]:.2%}")
    
    return {
        'final_state': np.array(state),
        'surprises': surprises,
        'entropies': entropies,
        'alive_ratios': alive_ratios
    }

# ============================================================================
# Visualization
# ============================================================================

def make_cmap():
    colors = [
        (0.0, 0.0, 0.1), (0.0, 0.1, 0.3), (0.0, 0.4, 0.6),
        (0.1, 0.7, 0.5), (0.6, 0.9, 0.3), (1.0, 1.0, 0.0), (1.0, 1.0, 1.0),
    ]
    return LinearSegmentedColormap.from_list('lenia', colors)

def visualize_results(results, output_path):
    """Create a summary visualization."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Final state
    ax = axes[0, 0]
    ax.imshow(results['final_state'], cmap=make_cmap(), vmin=0, vmax=1)
    ax.set_title('Final State')
    ax.axis('off')
    
    # Surprise over time
    ax = axes[0, 1]
    ax.plot(results['surprises'])
    ax.set_xlabel('Step')
    ax.set_ylabel('Surprise')
    ax.set_title('Homeostatic Pressure Over Time')
    ax.grid(True, alpha=0.3)
    
    # Entropy over time
    ax = axes[1, 0]
    ax.plot(results['entropies'])
    ax.set_xlabel('Step')
    ax.set_ylabel('Entropy')
    ax.set_title('Pattern Complexity')
    ax.grid(True, alpha=0.3)
    
    # Alive ratio
    ax = axes[1, 1]
    ax.plot(results['alive_ratios'])
    ax.set_xlabel('Step')
    ax.set_ylabel('Alive Ratio')
    ax.set_title('Activity Level')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved: {output_path}")

# ============================================================================
# Experiments
# ============================================================================

def experiment_homeostatic_vs_standard():
    """Compare homeostatic Lenia with standard Lenia."""
    print("\n" + "="*60)
    print("Experiment: Homeostatic vs Standard Lenia")
    print("="*60)
    
    # Parameters known to be unstable in standard Lenia
    params = [
        (15, 0.15, 0.015, "low_mu"),
        (15, 0.22, 0.04, "orbium_like"),
        (15, 0.30, 0.06, "high_mu"),
    ]
    
    for R, mu, sigma, name in params:
        print(f"\n--- Testing {name} ---")
        
        # Homeostatic version
        results = run_homeostatic_lenia(R=R, mu=mu, sigma=sigma, steps=500, alpha=0.01)
        output_path = OUTPUT_DIR / f"homeostatic_{name}.png"
        visualize_results(results, output_path)
        
        # Print summary
        final_surprise = results['surprises'][-1]
        final_alive = results['alive_ratios'][-1]
        print(f"  Final surprise: {final_surprise:.2f}")
        print(f"  Final alive ratio: {final_alive:.2%}")

if __name__ == '__main__':
    experiment_homeostatic_vs_standard()
    print("\n[DONE] Homeostatic Lenia experiments complete")
