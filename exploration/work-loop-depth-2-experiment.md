# Lenia V4 Warmstart Experiment Results

**Date**: 2026-06-28  
**Status**: ✅ SUCCESS

## Overview

Following the V3 failure (random initialization led to dead patterns), V4 uses **warm-start initialization** from known working Orbium parameters. This approach succeeded where V3 failed.

## Key Results

| Metric | Value |
|--------|-------|
| Best Fitness | 0.4827 |
| Best μ (mu) | 0.1726 |
| Best σ (sigma) | 0.0317 |
| Survival Rate | 100% |
| Generations Run | 10/10 |
| Kernel Radius | R=10 |

## Evolution Progress

| Gen | Mean Fitness | Max Fitness | Stability | Emergence | Survival |
|-----|--------------|-------------|-----------|-----------|----------|
| 0 | 0.3851 | 0.4765 | 0.552 | 0.218 | 85% |
| 1 | 0.4633 | 0.4765 | 0.653 | 0.273 | 100% |
| 5 | 0.4769 | 0.4802 | 0.645 | 0.309 | 100% |
| 9 | 0.4789 | 0.4827 | 0.645 | 0.313 | 100% |

## Key Findings

### 1. Warm-Start Critical for Success

- **V3 (random init)**: All patterns died, fitness ~0.001
- **V4 (warm start)**: 100% survival, fitness ~0.48

**Lesson**: Random kernel initialization in Lenia almost always produces dead patterns. Starting near known working parameters (Orbium) is essential for evolutionary search.

### 2. Evolved Parameters vs Initial

| Parameter | Initial (Orbium-like) | Evolved Best |
|-----------|----------------------|--------------|
| μ (mu) | 0.1622 ± 0.02 | 0.1726 |
| σ (sigma) | 0.0257 ± 0.005 | 0.0317 |

The evolution slightly increased both μ and σ from the initial "best search" parameters:
- **Higher μ** (0.1726 vs 0.1622): Slightly higher activation threshold
- **Higher σ** (0.0317 vs 0.0257): Wider growth window, more tolerant

### 3. Stability vs Emergence Trade-off

Final population showed:
- **Stability**: 0.645 (good pattern persistence)
- **Emergence**: 0.313 (moderate dynamics)
- **Balance**: α=0.5 weighting gave ~2:1 stability:emergence ratio

This suggests the Orbium-like kernels naturally favor stability over emergence.

### 4. Kernel Radius Sweet Spot

R=10 confirmed as optimal from previous parameter search. Smaller kernels (R=10) produced more viable patterns than larger ones (R=13, 15, 20).

## Technical Implementation

### Warm-Start Strategy

1. **Kernel Initialization**: Bump4 ring kernel (Orbium's kernel type)
2. **Parameter Initialization**: 
   - μ ~ 0.1622 (from param search v2 best)
   - σ ~ 0.0257 (from param search v2 best)
3. **Perturbation**: Small random noise (0.05 scale)
4. **Seed**: Real Orbium O2u seed (20x20 pattern)

### Mutation Strategy

- **Mutation scale**: 0.05 (smaller than V3's 0.15)
- **Elite fraction**: 30%
- **Crossover**: Blended crossover between elite parents

### Critical Fix: Kernel FFT Padding

The key technical fix was using proper FFT padding for the kernel:
```python
# Pad kernel to grid size
kernel_padded = np.pad(kernel, ((pad_h, ...), (pad_w, ...)))
# Roll so center is at (0, 0) for FFT convolution
kernel_padded = np.roll(kernel_padded, -cy, axis=0)
kernel_padded = np.roll(kernel_padded, -cx, axis=1)
```

## Output Files

- `best_kernel.npy`: Best evolved kernel (21x21 array)
- `best_pattern_timeline.png`: Evolution of best pattern over simulation
- `evolution_summary.png`: Fitness curves and kernel visualization
- `history.json`: Per-generation statistics
- `summary.json`: Final results summary

## Comparison with Previous Experiments

| Version | Init Strategy | Survival Rate | Best Fitness |
|---------|--------------|---------------|--------------|
| V1 | Random | ~10% | 0.15 |
| V2 | Random | ~15% | 0.20 |
| V3 | Random | 0% | 0.001 |
| **V4** | **Warm-start** | **100%** | **0.48** |

## Next Steps

1. **Run longer evolution**: 50-100 generations to see if fitness continues improving
2. **Multi-seed evaluation**: Test on random seeds too, not just Orbium
3. **Kernel shape evolution**: Allow evolution of kernel type (bump4 vs quad4 vs custom)
4. **Larger population**: 50-100 individuals for better diversity
5. **Novelty search**: Add explicit diversity preservation mechanism

## Conclusion

**V4 warmstart experiment succeeded!** The key insight is that Lenia's parameter space is highly sparse—random initialization almost never finds viable parameters, but starting near known working parameters enables effective evolutionary search.

The evolved parameters (μ=0.1726, σ=0.0317, R=10) with bump4 kernel provide a solid baseline for further exploration of Lenia's rich dynamics.

---

**Files**:  
- Experiment code: `experiments/evolutionary_lenia_v4_warmstart.py`  
- Output: `output/evo_lenia_v4_warmstart/`
