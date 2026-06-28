# Depth Report 1: Evolutionary Lenia Kernel Optimization

**Date**: 2026-06-28 20:04 (Asia/Shanghai)
**Cycle**: 1
**Focus**: Analysis of existing evolutionary Lenia framework

## Current State

The workspace contains extensive Lenia research including:
- `evolutionary_lenia.py` - Full GA framework with NN-parameterized kernels
- `evolutionary_lenia_v2.py` - Emergence-focused fitness (rewards dynamics, not stability)
- `neural_lenia_evo.py` - Simplified neural kernel evolution
- Multiple multichannel, stochastic, and agent-based variants

## Key Findings

### 1. Existing Framework Architecture

**Genome → Kernel → Simulation → Fitness → Evolution**

- **Genome**: 33-parameter MLP (2→8→1) mapping (r, θ) → kernel value
- **Kernel**: FFT-ready convolution kernel
- **Fitness V1**: `survival × stability × (1+entropy) × (1+diversity)`
- **Fitness V2**: `(temporal_entropy × pattern_change) × (spatial_complexity + novelty) × survival_weighted`

### 2. V1 vs V2 Fitness Philosophy

| Aspect | V1 | V2 |
|--------|-----|-----|
| Goal | Stability | Emergence |
| Rewards | Static patterns | Dynamic patterns |
| Survival | Raw survival | Weighted (peaks at 0.5) |
| Novelty | Not included | Distance from uniform |

### 3. Official Lenia Reference (Chakazul/Lenia)

- Multi-channel via `-c -k -x` parameters
- GPU acceleration via reikna
- No stochastic update mechanism (our innovation)
- No ecological relationship modeling (our innovation)

### 4. Research Gaps Identified

1. **Kernel Shape Space**: Current NN parameterization may be too constrained
2. **Fitness Landscape**: V2 emergence focus may miss stable-but-interesting patterns
3. **Multi-objective**: No Pareto optimization for survival vs dynamics trade-off
4. **Transfer Learning**: No mechanism to transfer learned kernels between tasks

## Proposed Experiment for Cycle 2

**Hypothesis**: A hybrid fitness combining V1 stability with V2 dynamics will find kernels that produce both long-lived AND dynamic patterns.

**Approach**:
1. Create `evolutionary_lenia_v3.py` with hybrid fitness
2. Add multi-objective Pareto front tracking
3. Test on diverse seed types (orbium, random, perturbed, multi)
4. Compare with V1 and V2 baselines

## Technical Notes

- CDP proxy available but connection issues (Chrome on port 9222, proxy on 3456)
- Web search/fetch disabled - relying on local knowledge
- JAX-based simulation with FFT convolution
- Population sizes typically 16-20, generations 5-10 for quick experiments

## Next Steps

1. Spawn subagent to implement v3 hybrid fitness
2. Run comparative experiment: V1 vs V2 vs V3
3. Analyze Pareto front for trade-off insights
4. Document findings in depth-2.md
