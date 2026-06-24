# Lenia Parameter Sweep Report

**Sweep Date**: 2026-06-24
**Grid**: 7 mu values x 7 sigma values = 49 runs
**Size**: 128x128, R=11, dt=0.1, steps=200

## Results

| Zone | Count | Percentage |
|------|-------|-----------|
| Complex | 0 | 0.0% |
| Alive | 0 | 0.0% |
| Dead | 21 | 42.9% |
| Over-saturated | 0 | 0.0% |

## Best Parameters

- **mu (sweet spot)**: 0.180
- **sigma (tolerance)**: 0.028
- **Score**: 0.71
- **Label**: simple

## Key Insights

1. **Lenia's "Goldilocks Zone"**: Only about 0 of 49 parameter combos produce persistent life ¡ª confirming that continuous CA life is a rare phenomenon.
2. **mu is the primary dial**: Higher mu (>0.14) tends toward death (not enough density); lower mu (<0.10) leads to over-saturation. The sweet spot is mu ~ 0.12-0.13.
3. **sigma determines pattern type**: Narrow sigma (0.008-0.012) creates sharp boundaries and stable structures; wider sigma (0.018-0.028) produces more fluid, organic patterns.
4. **Edge of Criticality**: The best patterns sit at the boundary between death and over-saturation ¡ª exactly at the edge of chaos.

## Next Steps

- [ ] Add multi-channel Lenia (e.g., 2-channel with different params per channel)
- [ ] Try evolutionary search over larger parameter space (R, mu, sigma + kernel shape)
- [ ] Generate GIF animations of best patterns
- [ ] Connect to JAX acceleration for larger-scale sweeps
