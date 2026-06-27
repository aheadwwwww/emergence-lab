# Self-Replicating Neural Lenia Experiment

**Date**: 2026-06-27 19:15
**Experiment**: `neural_lenia_self_replicating_v2.py`

## Goal

Combine Neural Lenia with self-replication concepts from Google's self-organising systems.

Can a neural network learn a kernel that produces self-sustaining patterns?

## Method

1. **Neural Kernel**: MLP (16 hidden units) generates kernel from (r, θ) coordinates
2. **Training**: Random search (30 iterations, 200 steps each)
3. **Evaluation**: 
   - Survival score: alive_mean × 5 (if alive > 0.1)
   - Stability score: 1 - variance × 20
   - Total = survival + stability

## Results

| Iteration | Score | Alive Mean | Variance | Status |
|-----------|-------|------------|----------|--------|
| 29 | **2.15** | 0.231 | 2.9e-06 | ✓ Survives |
| 12 | 2.15 | 0.229 | 2.9e-05 | ✓ Survives |
| 13 | 1.96 | 0.206 | 3.4e-03 | ✓ Survives |
| 0-11, 14-28 | < 1.0 | 0.0 | 0.0 | ✗ Died |

**Success rate**: 3/30 (10%)

## Key Findings

1. **Neural kernels CAN produce stable patterns** - 10% of random kernels work
2. **Very high stability** - variance ~10^-6 means patterns don't oscillate
3. **Alive fraction ~23%** - similar to classic Lenia Orbium

## Output Files

- `experiments/output/self_repl_kernel_0.png` - Learned kernel visualization
- `experiments/output/self_repl_grid_0.png` - Final pattern state
- `experiments/output/self_repl_results_0.json` - Full results

## Next Steps

1. **Gradient optimization**: Use JAX autodiff to optimize kernel parameters
2. **Target replication**: Train patterns to "spawn" copies in empty regions
3. **Multi-channel**: Extend to multi-channel Neural Lenia with interaction matrices

## References

- Google Self-Replicating NN: `exploration/2026-06-27-self-replicating-nn-google.md`
- Neural Lenia prototype: `experiments/neural_lenia.py`
- Lenia project: `memory/projects.md`
