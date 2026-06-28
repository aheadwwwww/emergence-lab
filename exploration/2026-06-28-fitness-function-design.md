# Fitness Function Design for Emergent Dynamics

**Date**: 2026-06-28 19:50
**Context**: Kernel fitting test showed representation is NOT the bottleneck. The fitness function is.

---

## The Problem

**Observation**: Evolutionary Lenia fails to find interesting patterns despite having sufficient representation capacity.

**Root Cause Analysis**:
1. ✅ Genome representation (33 params) can express good kernels (verified by gradient descent fitting)
2. ❌ Fitness function rewards static stability, not emergent dynamics
3. ❓ Evolutionary operators may need tuning
4. ❓ Selection pressure may be misconfigured

**Primary Suspect**: Fitness function design

---

## Current vs Desired Behavior

### Current Fitness Function
```
fitness = survival × stability × (1 + entropy) × (1 + diversity)
```

**What it rewards**:
- Survival: Not dying (good)
- Stability: Staying the same (BAD for emergence!)
- Entropy: Information content (neutral)
- Diversity: Spatial variation (good but static)

**What emerges**: Static blobs that survive but don't do anything interesting.

### Desired Behavior
We want patterns that:
1. **Persist** (survival)
2. **Change** (dynamics, NOT static stability)
3. **Self-organize** (complexity)
4. **Exhibit temporal patterns** (oscillators, gliders, self-replication)

---

## Fitness Function Redesign Strategies

### Strategy 1: Temporal Dynamics Metrics

**Key Insight**: Measure CHANGE over time, not just final state.

```python
def dynamic_fitness(history):
    """
    history: List of frames [A_0, A_1, ..., A_T]
    """
    # Frame-to-frame change rate
    change_rates = [
        np.abs(history[t+1] - history[t]).mean() 
        for t in range(len(history)-1)
    ]
    dynamics = np.mean(change_rates)
    
    # Complexity: fractal edge density
    complexity = fractal_dimension(history[-1])
    
    # Moderate stability: don't collapse, don't explode
    mass = history[-1].sum()
    stability = 1.0 / (1.0 + abs(mass - target_mass))
    
    return dynamics * complexity * stability
```

**Why this works**:
- Rewards continuous change (dynamics)
- Rewards complex structure (fractal edges)
- Penalizes collapse/explosion (moderate stability)

### Strategy 2: Pattern Recognition Metrics

**Key Insight**: Detect specific emergent behaviors.

```python
def pattern_fitness(history):
    score = 0.0
    
    # Oscillation detection
    if has_oscillation(history):
        score += 1.0
    
    # Glider detection
    if has_gliders(history):
        score += 2.0
    
    # Self-replication detection
    if has_replication(history):
        score += 3.0
    
    # Spatial complexity
    score += fractal_dimension(history[-1])
    
    return score
```

**Why this works**:
- Directly rewards the behaviors we want
- Can use computer vision techniques (contour detection, template matching)
- Inspired by Game of Life pattern classification

### Strategy 3: Multi-Objective Optimization

**Key Insight**: Don't collapse to single scalar too early.

```python
def multi_objective_fitness(history):
    return {
        'survival': survival_score(history),
        'dynamics': dynamics_score(history),
        'complexity': complexity_score(history),
        'novelty': novelty_score(history, archive),
    }
```

**Use Pareto dominance** for selection:
- Individual A dominates B if A is better in all objectives and strictly better in at least one
- Maintains diversity in the population
- Avoids premature convergence to static blobs

### Strategy 4: Open-Endedness

**Key Insight**: Don't optimize for a fixed target. Let complexity increase indefinitely.

**Inspired by**: 
- Picbreeder (evolutionary art with no target)
- neuroplexparticles2 (no preset behaviors)
- xagent (no reward function)

```python
def open_ended_fitness(history, previous_best):
    # Novelty: different from previous champions
    novelty = distance(history, previous_best)
    
    # Complexity: always try to increase
    complexity = fractal_dimension(history[-1])
    
    # Persistence: must survive long enough
    survival = survival_score(history)
    
    return novelty * complexity * survival
```

**Why this works**:
- No fixed target → continuous exploration
- Novelty pressure → diversity maintenance
- Complexity pressure → open-ended growth

---

## Implementation Plan

### Phase 1: Dynamic Fitness (Immediate)

1. **Implement `compute_dynamic_fitness()`** ✅ (already done in `dynamic_fitness.py`)
   - Frame change rate
   - Fractal edge density
   - Moderate stability

2. **Test on known patterns**
   - Orbium: should score high on stability + moderate dynamics
   - Aerum: should score high on dynamics
   - Random: should score low

3. **Run evolution** with new fitness
   - Compare with old fitness
   - Track dynamics/complexity metrics over generations

### Phase 2: Pattern Detection (Next)

1. **Implement pattern detectors**
   - Oscillator: periodic autocorrelation
   - Glider: template matching
   - Self-replication: object counting over time

2. **Add to fitness function**
   - Weight patterns by interest level
   - Self-replication > gliders > oscillators

### Phase 3: Multi-Objective (Future)

1. **Implement NSGA-II or MOEA/D**
   - Use existing JAX-MD or DEAP implementations
   - Pareto front visualization

2. **Explore trade-offs**
   - Dynamics vs stability
   - Complexity vs survival
   - Novelty vs exploitation

---

## Lessons from Related Work

### From neuroparticles2
- **Three-layer architecture**: Particles + CA + GA
- **Emergent strategies**: No preset behaviors, let evolution discover
- **Visualization**: Real-time feedback helps spot interesting patterns

### From xagent
- **No reward function**: Behavior emerges from homeostasis
- **Free energy principle**: Minimize surprise = maximize prediction
- **Inspiration**: Could use "predictive fitness" - reward patterns that are predictable yet non-trivial

### From Picbreeder
- **Human-in-the-loop**: Interactive selection
- **No target**: Open-ended evolution
- **Inspiration**: Could use "aesthetic fitness" - neural network trained on interesting patterns

---

## Key Metrics to Track

| Metric | Formula | What it measures |
|--------|---------|------------------|
| **Dynamics** | `mean(|A_{t+1} - A_t|)` | Temporal change rate |
| **Complexity** | Fractal dimension | Spatial structure |
| **Stability** | `1 / (1 + |mass - target|)` | Moderate survival |
| **Novelty** | Distance to archive | Diversity |
| **Oscillation** | Autocorrelation peak | Periodic behavior |
| **Gliders** | Template match count | Moving patterns |
| **Replication** | Object count change | Self-copying |

---

## Hypothesis

**H1**: The dynamic fitness function will drive evolution toward patterns with:
- Higher temporal dynamics (frame-to-frame change)
- Higher spatial complexity (fractal edges)
- Moderate stability (not collapse, not explosion)

**H2**: Multi-objective optimization will find a Pareto front of trade-offs between:
- Dynamics vs stability
- Complexity vs survival
- Novelty vs exploitation

**H3**: Open-ended evolution will continuously discover new patterns without converging to a fixed optimum.

---

## Next Steps

1. ✅ Verify representation capacity (kernel fitting test)
2. ✅ Implement dynamic fitness function
3. ⏳ Run evolution with dynamic fitness
4. ⏳ Compare with old fitness
5. ⏳ Implement pattern detectors
6. ⏳ Implement multi-objective optimization
7. ⏳ Explore open-ended evolution

---

## References

- **neuroparticles2**: https://github.com/xcontcom/neuroparticles2
- **xagent**: https://github.com/koraytaylan/xagent
- **Picbreeder**: Secret et al., "Reconciling explanations in the space of possible solutions"
- **NSGA-II**: Deb et al., "A fast and elitist multiobjective genetic algorithm"
- **Free Energy Principle**: Friston, "The free energy principle: a unified brain theory?"
