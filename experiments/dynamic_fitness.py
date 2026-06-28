"""
Improved Fitness Functions for Evolutionary Lenia
==================================================

Problem: Current fitness rewards stability, not emergent dynamics.
Solution: New metrics that reward pattern change, temporal diversity, and novelty.
"""

import numpy as np
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class DynamicFitnessResult:
    """Fitness result with temporal dynamics metrics."""
    survival: float
    stability: float
    entropy: float
    diversity: float
    dynamics: float  # NEW: temporal change rate
    complexity: float  # NEW: fractal-like complexity
    score: float
    breakdown: str


def compute_dynamic_fitness(history: List[np.ndarray], threshold: float = 0.05) -> DynamicFitnessResult:
    """
    Improved fitness that rewards emergent dynamics.
    
    Key insight: We want patterns that are:
    1. Stable enough to survive (not die out)
    2. Dynamic enough to be interesting (not static)
    3. Complex enough to be novel (not simple)
    
    New metrics:
    - dynamics: average frame-to-frame change rate
    - complexity: fractal-like edge density
    
    Score = survival × (moderate_stability) × (1+entropy) × (1+diversity) × (1+dynamics) × (1+complexity)
    """
    masses = np.array([h.sum() for h in history])
    
    # Survival: fraction of frames with mass > threshold
    survival = float(np.mean(masses > threshold))
    
    # Stability: but MODERATE, not too stable
    # Goldilocks zone: variance should be in [0.05, 0.3]
    n = len(masses)
    final_slice = masses[int(0.8*n):]
    if len(final_slice) > 0 and np.mean(final_slice) > 0:
        variance = np.var(final_slice) / (np.mean(final_slice)**2 + 1e-8)
        # Moderate stability: penalize both too stable (variance < 0.05) and too unstable (variance > 0.3)
        if variance < 0.05:
            stability = variance / 0.05  # Linear ramp from 0 to 1
        elif variance > 0.3:
            stability = max(0, 1 - (variance - 0.3) / 0.7)  # Linear decay from 1 to 0
        else:
            stability = 1.0  # Goldilocks zone
    else:
        stability = 0.0
    
    # Entropy: structural complexity
    final = history[-1]
    final_norm = final / (final.sum() + 1e-8)
    raw_entropy = -np.sum(final_norm * np.log(final_norm + 1e-8))
    entropy_norm = float(raw_entropy / np.log(len(final.ravel())))
    
    # Diversity: multi-structure patterns
    h, w = final.shape
    regions = []
    for i in range(4):
        for j in range(4):
            region = final[i*h//4:(i+1)*h//4, j*w//4:(j+1)*w//4]
            regions.append(region.sum())
    diversity = float(np.std(regions) / (np.mean(regions) + 1e-8))
    
    # NEW: Dynamics - average frame-to-frame change
    changes = []
    for i in range(1, len(history)):
        diff = np.abs(history[i] - history[i-1]).sum()
        total = history[i].sum() + history[i-1].sum() + 1e-8
        changes.append(diff / total)
    dynamics = float(np.mean(changes)) if changes else 0.0
    
    # NEW: Complexity - fractal-like edge density
    # Use Laplacian to detect edges
    from scipy import ndimage
    laplacian = ndimage.laplace(final)
    edge_density = float((np.abs(laplacian) > 0.01).sum() / laplacian.size)
    
    # Multi-scale complexity
    h, w = final.shape
    scales = []
    for scale in [1, 2, 4]:
        small = final[::scale, ::scale]
        if small.size > 0:
            small_norm = small / (small.sum() + 1e-8)
            small_entropy = -np.sum(small_norm * np.log(small_norm + 1e-8))
            scales.append(small_entropy)
    complexity = float(np.std(scales)) if len(scales) > 1 else 0.0
    
    # Combine: survival is gate, others are bonuses
    score = survival * stability * (1 + entropy_norm) * (1 + diversity) * (1 + dynamics) * (1 + complexity)
    
    breakdown = (
        f"survival={survival:.3f} × "
        f"stability={stability:.3f} × "
        f"(1+entropy)={1+entropy_norm:.3f} × "
        f"(1+diversity)={1+diversity:.3f} × "
        f"(1+dynamics)={1+dynamics:.3f} × "
        f"(1+complexity)={1+complexity:.3f}"
    )
    
    return DynamicFitnessResult(
        survival=survival,
        stability=stability,
        entropy=entropy_norm,
        diversity=diversity,
        dynamics=dynamics,
        complexity=complexity,
        score=score,
        breakdown=breakdown
    )


def compute_novelty_fitness(history: List[np.ndarray], archive: List[np.ndarray], k: int = 15) -> Tuple[float, str]:
    """
    Novelty search: reward patterns that are different from archive.
    
    Based on Lehman & Stanley's novelty search.
    
    Args:
        history: simulation frames
        archive: archive of previous behaviors (final states)
        k: number of nearest neighbors to consider
    
    Returns:
        (novelty_score, breakdown)
    """
    if len(archive) == 0:
        return 1.0, "archive empty"
    
    # Compare final state to archive
    final = history[-1].flatten()
    final_norm = final / (np.linalg.norm(final) + 1e-8)
    
    # Compute distances to archive
    distances = []
    for archived in archive:
        archived_flat = archived.flatten()
        archived_norm = archived_flat / (np.linalg.norm(archived_flat) + 1e-8)
        dist = np.linalg.norm(final_norm - archived_norm)
        distances.append(dist)
    
    # Novelty = mean distance to k nearest neighbors
    distances = sorted(distances)
    k_nearest = distances[:min(k, len(distances))]
    novelty = float(np.mean(k_nearest))
    
    breakdown = f"novelty={novelty:.3f} (dist to {len(k_nearest)} nearest)"
    
    return novelty, breakdown


# ═══════════════════════════════════════════════════════════════
# Testing
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Test with synthetic data
    print("Testing dynamic fitness...")
    
    # Static blob
    static = [np.ones((128, 128)) * 0.5 for _ in range(200)]
    result_static = compute_dynamic_fitness(static)
    print(f"Static blob: score={result_static.score:.3f}, dynamics={result_static.dynamics:.4f}")
    
    # Dynamic pattern (oscillating)
    dynamic = []
    for t in range(200):
        pattern = np.sin(t * 0.1) * np.ones((128, 128)) * 0.5 + 0.5
        dynamic.append(pattern)
    result_dynamic = compute_dynamic_fitness(dynamic)
    print(f"Dynamic pattern: score={result_dynamic.score:.3f}, dynamics={result_dynamic.dynamics:.4f}")
    
    # Random noise
    noise = [np.random.rand(128, 128) for _ in range(200)]
    result_noise = compute_dynamic_fitness(noise)
    print(f"Random noise: score={result_noise.score:.3f}, dynamics={result_noise.dynamics:.4f}")
    
    print("\nBreakdown (dynamic pattern):")
    print(result_dynamic.breakdown)