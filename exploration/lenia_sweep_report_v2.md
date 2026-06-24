# Lenia Sweep V2 Report

**Date**: 2026-06-24
**Settings**: Grid 7x7=49 runs, 192x192, R=13, steps=300

## Results

| Category | Count | % |
|----------|-------|---|
| Structure (complex edges) | 0 | 0.0% |
| Alive (stable but simple) | 29 | 59.2% |
| Dead | 20 | 40.8% |
| Saturated | 0 | 0.0% |

## Best Param
- mu=0.180, sigma=0.026, score=0.48

## Combined Insights (V1 + V2)

1. **R scales everything**: At R=11, Lenia struggles to form structure. R=13+ is necessary for interesting patterns.
2. **Grid size matters**: 128x128 is too small; 192x192 shows more structure.
3. **The "life zone"**: Alive patterns appear at (mu ~ 0.10-0.18, sigma >= 0.018). Dead below sigma ~ 0.015.
4. **No true Orbium found**: Even at R=13, I don't see the classic Lenia species. Likely need:
   - R >= 20 for "creatures" (Orbium uses R=20+)
   - Specific initial conditions (Orbium seed pattern, not random)
   - Multi-channel Lenia (2+ channel interaction)

## Next Phase
- Try R=20 with 256^2 grid (needs JAX for speed ¡ª current 49 runs took ~2 min)
- Use Orbium-specific initialization pattern
- Add multi-channel support (different growth per channel)
- Genetic algorithm search over (R, mu, sigma, kernel_shape)
