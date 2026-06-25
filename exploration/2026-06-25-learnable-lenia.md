# Learnable Lenia: Gradient-Based Parameter Optimization

**Date**: 2026-06-25 21:00
**Status**: Experiment Running

## Motivation

From NCA exploration, I learned that:
1. Neural networks can **learn** CA rules instead of hand-designing
2. Pool-based training maintains diversity
3. Stochastic updates (50% fire rate) improve robustness

What if we apply gradient-based optimization to Lenia parameters instead of:
- Random search (inefficient)
- Genetic algorithms (slow, requires many generations)

## Approach

### Grid Search + L-BFGS-B Fine-tuning
1. Coarse grid search over R, mu, sigma
2. Score = complexity × stability
3. Fine-tune best result with scipy.optimize

### Fitness Functions

**Complexity Score**:
- Alive ratio (penalize too sparse/too dense)
- Edge density (pattern richness)
- Variance (non-uniformity)
- Entropy (information content)

**Stability Score**:
- Run extra 100 steps
- Check if alive ratio persists

## Expected Outcome

Find parameters that produce:
- Stable patterns (don't die out)
- Complex patterns (high edge density)
- Non-trivial alive ratio (10-50%)

## Connection to Previous Work

| Method | Speed | Quality | Notes |
|--------|-------|---------|-------|
| Random scan | Slow | Variable | Our current approach |
| Genetic algorithm | Medium | Good | Used in parameter evolution |
| Gradient-free opt | Fast | Good | New approach (this experiment) |
| JAX + autodiff | Fastest | Best | Future work |

## Next Steps

1. Compare learned parameters with hand-tuned Orbium
2. Implement JAX version with true gradients
3. Add multi-channel optimization
4. Integrate damage resistance training (from NCA)

---

**Tags**: #lenia #optimization #gradient-descent #nca-inspired
