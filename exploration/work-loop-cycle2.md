# Work-Loop Cycle 2: Self-Organized Criticality in Lenia Systems

**Date**: 2026-06-28 17:36 (Asia/Shanghai)  
**Topic**: Self-Organized Criticality, Complex Systems, Power Laws

## Exploration Summary

Self-Organized Criticality (SOC) is a phenomenon where systems naturally evolve to a critical state without external tuning. Classic examples include sandpile models, earthquakes, and forest fires. This experiment tested whether Lenia - a continuous cellular automaton - exhibits SOC-like dynamics through avalanche analysis.

## Experiment: Lenia Avalanche Dynamics

### Hypothesis
If Lenia exhibits SOC, the distribution of "avalanche" sizes (clusters of significant change between time steps) should follow a power law: P(size) ∝ size^(-τ) where τ typically ranges from 1.5 to 3.0.

### Setup
- **Type**: Lenia continuous cellular automaton with avalanche tracking
- **Grid Size**: 64x64 cells
- **Parameters**: R=13, T=0.1, sigma=0.15 (standard Lenia parameters)
- **Initialization**: Random noise (seed=42)
- **Steps**: 50 iterations
- **Avalanche Definition**: Connected clusters where |Δstate| > 0.02

### Key Findings

| Metric | Value |
|--------|-------|
| Total Avalanches | 683 |
| Size Range | 2 - 4013 cells |
| Power Law Exponent (τ) | 0.313 |
| SOC Signature | **WEAK** |
| Final Mean | 0.155 |
| Final Std | 0.173 |
| Active Clusters | 126 |

### Criticality Analysis

**Result: Weak SOC signature**

The power law exponent τ = 0.313 is significantly lower than the typical SOC range (1.5 < τ < 3.0). This suggests:

1. **Sub-critical dynamics**: The Lenia parameters used may be below the critical threshold
2. **Different criticality class**: Lenia may exhibit a different type of criticality than classical SOC models
3. **Parameter sensitivity**: Small changes in T or sigma might shift the system toward criticality

### Cluster Structure

The final state shows:
- 126 distinct active clusters (cells > 0.5)
- Small cluster sizes (mean = 1.8 cells)
- Fragmented rather than consolidated patterns

This fragmentation differs from classical SOC systems which tend toward large, connected structures at criticality.

## Theoretical Insights

### Why Weak SOC?

1. **Continuous vs Discrete**: Lenia's continuous state space may smooth out the sharp transitions that create SOC avalanches
2. **Growth Function Shape**: The Gaussian growth function creates soft attractors rather than threshold dynamics
3. **Conservation**: Unlike sandpile models, Lenia doesn't conserve "mass" - this changes the critical dynamics

### Alternative Hypothesis

Lenia may exhibit **self-organized bistability** rather than criticality:
- Multiple stable attractor states
- Transitions between attractors rather than critical fluctuations
- Pattern formation without scale-free statistics

## Next Steps

- Vary parameters (T, sigma) to search for critical regime
- Compare with discrete Lenia variants
- Measure temporal correlations (1/f noise)
- Test multi-kernel Lenia for enhanced criticality

## Technical Notes

- Avalanche detection via connected component labeling on thresholded change map
- Power law fit via log-log linear regression
- scipy.ndimage.label for cluster identification
- Threshold 0.02 chosen to capture meaningful changes while filtering noise

## Files Generated

- `lenia_criticality.py` - Experiment script
- `lenia_criticality_results.json` - Numerical results
