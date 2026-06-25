# Stochastic Lenia: Asynchronous Updates Enable Survival

**Date**: 2026-06-25 19:30
**Experiment**: `experiments/lenia_stochastic.py`
**Inspiration**: Isotropic NCA's 50% stochastic update rate

## The Experiment

Tested Lenia with different update probabilities:
- p=1.0: Synchronous (all cells update every step)
- p=0.75: 75% cells update
- p=0.5: 50% cells update (like Isotropic NCA)
- p=0.25: 25% cells update

**Parameters**: R=13, μ=0.15, σ=0.015, 200 steps

## Surprising Result

| Update Prob | Alive Ratio (step 200) |
|-------------|------------------------|
| 1.0         | 0.000 (death)          |
| 0.75        | 0.000 (death)          |
| **0.5**     | **0.282** (survival)   |
| 0.25        | 0.261 (survival)       |

**Key insight**: Synchronous updates kill the pattern, but stochastic updates allow it to survive!

## Why?

Hypothesis: **Synchronous updates create oscillations** that destabilize the pattern. When all cells update simultaneously, they overshoot the stable state and oscillate to death.

With stochastic updates:
1. Each cell acts independently, creating temporal noise
2. Some cells remain "frozen" while others update
3. This creates a damping effect on oscillations
4. The system can settle into a stable configuration

## Connection to Biology

This mirrors real biological systems:
- Cells don't all divide at the same time
- Neural networks have asynchronous spiking
- Bacterial colonies grow asynchronously
- Development is stochastic, not deterministic

**Emergence benefits from temporal disorder.**

## Connection to Isotropic NCA

Isotropic NCA uses p=0.5 update rate and achieves:
- Damage resistance
- Regeneration capability
- Stable long-term patterns

Our Lenia shows similar benefits:
- Stochastic updates prevent death spirals
- Allow patterns to stabilize
- Create more organic, lifelike behavior

## Implications

1. **For Lenia**: Standard Lenia uses synchronous updates. Adding stochasticity could improve pattern stability and diversity.

2. **For Neural CA**: Confirms that asynchronous updates are beneficial, not just a computational trick.

3. **For Emergence Research**: Temporal coordination is a hidden parameter. Too much = death, too little = chaos, optimal = life.

## Next Steps

1. **Parameter sweep**: Find optimal update probability (0.3-0.7?)
2. **Multi-channel**: Test stochastic updates in multichannel Lenia
3. **Compare with JAX**: Implement JAX version for faster experiments
4. **Damage test**: Can stochastic Lenia regenerate after damage?
5. **Phase diagram**: Map update_prob vs R vs (mu, sigma)

## Visualization

`experiments/lenia_stochastic_comparison.png` shows the comparison:
- Top row: step 50 for each update probability
- Bottom row: step 200 for each update probability
- Clear visual difference: p=0.5 and 0.25 show stable patterns, p=1.0 and 0.75 are dead

## Connection to Pheromone Coupling

Our earlier pheromone coupling experiments showed that **weak interaction** between channels is better than strong interaction. Stochastic updates are similar: **weak temporal coupling** between cells is better than strong (synchronous) coupling.

**Pattern**: Both spatial (pheromone) and temporal (update) weak coupling improve survival.

## Quote

> "Life is a process that avoids equilibrium." — Schrödinger

Stochastic updates help the system avoid equilibrium (death) by introducing temporal noise.

---

**Tag**: #lenia #stochastic #emergence #asynchronous #isotropic-nca
