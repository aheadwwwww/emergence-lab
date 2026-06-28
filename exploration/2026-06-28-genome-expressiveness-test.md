# Genome Expressiveness Test Results

**Date**: 2026-06-28 18:30
**Test**: Can the 33-parameter genome express known-good Lenia kernels?

---

## Result: SUCCESS

**Final Loss**: 0.000004 (essentially zero)

The genome CAN perfectly express a Gaussian Ring kernel (Orbium-style).

---

## Implications

### What This Means
1. **Representation is NOT the bottleneck** - The 33-parameter NN (2→8→1) is sufficient.
2. **The problem lies elsewhere**:
   - Fitness function design
   - Evolution hyperparameters
   - Seed strategy
   - Simulation duration

### Why Evolution Wasn't Improving

From the exploration note (work-loop-depth-1.md):
> Best score stuck at 11.67 (no improvement across 5 generations)

Now we know the genome CAN express good kernels, so the issue must be:

1. **Fitness Function**: 
   - Current: `survival × stability × complexity`
   - Problem: Rewards stable blobs, not emergent dynamics
   - The random seed creates a "static blob" that scores high but isn't interesting

2. **Seed Strategy**:
   - Orbium seed consistently dies (survival=0.2)
   - Random seed creates stable but boring patterns
   - Need seeds that challenge the kernel to produce dynamics

3. **Simulation Duration**:
   - 200 steps may be too short to see emergence
   - Need longer runs (1000+) to distinguish "stable blob" from "dynamic pattern"

---

## Next Steps

### 1. Redesign Fitness Function
Instead of rewarding stability, reward:
- **Pattern diversity** (entropy over time)
- **Spatial complexity** (edge density, fractal dimension)
- **Temporal dynamics** (change rate, oscillation)
- **Novelty** (distance from known patterns)

### 2. Better Seed Strategy
- Use multiple challenging seeds
- Include "perturbation seeds" (orbium + noise)
- Include "competitive seeds" (multiple orbiums)

### 3. Longer Simulations
- Increase `sim_steps` to 1000+
- Add "burn-in" period before scoring

### 4. Alternative Evolution Strategy
- Instead of maximizing fitness, minimize "boringness"
- Use novelty search (Lehman & Stanley)
- Maintain diversity in population

---

## Code Artifact

Test script: `experiments/test_genome_expressiveness.py`

Output: `experiments/output/evo_lenia_demo/kernel_fitting_test.png`

---

## Key Insight

**The bottleneck is NOT the representation.**

This is a common pattern in ML:
- We blame the model architecture
- But the real issue is the objective function

The genome is a hammer. The fitness function is what we're hitting. We've been hitting the wrong thing.
