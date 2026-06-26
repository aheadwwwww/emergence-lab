# Lenia Alive Mask Parameter Sweep

## Experiment

**Goal**: Find optimal `alive_threshold` for Stochastic + Alive Mask Lenia

**Date**: 2026-06-26 21:05

## Results

| Threshold | Final Alive | Max Alive | Status |
|-----------|-------------|-----------|--------|
| 0.05      | 0.3%        | 0.7%      | FAIL   |
| 0.10      | 0.6%        | 0.6%      | FAIL   |
| 0.15      | 0.6%        | 0.6%      | FAIL   |
| 0.20      | 0.6%        | 0.7%      | FAIL   |
| 0.25      | 0.7%        | 0.7%      | FAIL   |
| 0.30      | 0.8%        | 0.8%      | FAIL   |

## Analysis

All configurations showed very low survival (< 1%). This contradicts the earlier successful experiment that showed 25.9% survival with stochastic + alive mask.

### Possible Issues

1. **Alive Mask Logic Difference**
   - Successful version: `alive_count > 0.5` (at least one alive neighbor)
   - Sweep version: `alive_neighbors > 0.5` on normalized convolution
   - The normalization divides by neighborhood size, making threshold harder to reach

2. **Update Mask Application**
   - Successful version: `new_grid = np.where(update_mask & alive, G, grid)`
   - This combines two conditions with AND, which is very restrictive
   - Might need to relax one or both conditions

3. **Seed Initialization**
   - Random seed each run might create unfavorable initial conditions

## Next Steps

1. Fix alive mask logic to match successful experiment
2. Test different update rates (0.3, 0.5, 0.7)
3. Try OR instead of AND for combining stochastic + alive
4. Use deterministic seeds for reproducibility

## Key Insight

The alive mask is a **survival constraint**, not an update constraint. It should prevent ghost structures from drifting, not kill healthy cells. The threshold needs careful tuning.

---

*Experiment time: 2026-06-26 21:05 GMT+8*
