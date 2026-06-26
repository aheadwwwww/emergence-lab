# Lenia Ecosystem Experiment - 2026-06-26

## Overview
Multi-species Lenia ecosystem combining:
- **Multi-channel Lenia**: Different parameters = different "species"
- **Stochastic updates**: 40-60% update probability per species
- **Weak inter-species coupling**: 5% cross-influence
- **Ecological memory**: Track emergence events

## Species Parameters

| Species | R | μ | σ | Update Prob |
|---------|---|---|---|-------------|
| Orbium | 13 | 0.15 | 0.015 | 50% |
| Geminium | 10 | 0.20 | 0.025 | 60% |
| Asterium | 15 | 0.12 | 0.020 | 40% |

## Results (500 steps)

### Initial State (t=0)
- Total: 5026 cells
- Diversity: 0.949 (high)
- Orbium: 2019, Geminium: 2085, Asterium: 922

### Final State (t=500)
- Total: 2058 cells
- Diversity: 0.320 (low)
- Orbium: 3 [EXTINCT]
- Geminium: 1834 [DOMINANT]
- Asterium: 221 [COEXIST]

### Emergence Events
- 21 emergence events detected
- High variance in Orbium population before extinction

## Key Findings

1. **Competitive Exclusion**: One species (Geminium) dominated
2. **Extinction Cascade**: Orbium went extinct rapidly (t=50)
3. **Stable Coexistence**: Geminium + Asterium stabilized
4. **Stochastic Updates Help**: Prevented total oscillation death

## Ecological Interpretation

- Geminium (μ=0.20, σ=0.025, 60% update) found optimal niche
- Asterium (μ=0.12, large R=15, 40% update) survived as secondary
- Orbium (μ=0.15, R=13, 50% update) lost competition

## Next Steps

1. Add more species (4-6)
2. Implement resource competition (limited food)
3. Add predator-prey dynamics
4. Evolve parameters with genetic algorithm
5. Test different coupling strengths

## Files
- `lenia_ecosystem.py` - Main experiment
- `output/lenia_ecosystem/` - Visualization frames
