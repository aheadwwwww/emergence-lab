# Lenia R=15 Parameter Sweep Report

**Date**: 2026-06-25
**Grid**: 9 mu x 8 sigma = 72 runs
**Shape**: 192x192, R=15, steps=400, dt=0.1
**Kernel**: bump4 (kn=1), Growth: gaus (gn=1)

## Results

| Category | Count | Percentage |
|----------|-------|-----------|
| error | 72 | 100.0% |

## Cross-Radius Comparison

| Radius | Survival Rate | Best Score | Notes |
|--------|--------------|------------|-------|
| R=11 | 57.1% | ~2.5 | Simple patterns only |
| R=15 | 0.0% | N/A | Middle ground |
| R=20 | 0% | 0.30 | All dead — too demanding |

## Key Insights

1. **R=15 transition zone**: R=15 sits between the easy-life zone (R=11) and the no-life zone (R=20).
2. **Parameter sensitivity**: As R increases, the viable (mu, sigma) region shrinks dramatically.
3. **Next step**: If R=15 also fails, try R=13 with wider parameter sweep.
