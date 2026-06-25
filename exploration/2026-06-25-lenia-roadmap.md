# Lenia Exploration Roadmap

## Current State (2026-06-25)

### Key Discoveries

#### 1. Stochastic Updates Enable Survival 🔴
- **Finding**: Synchronous updates (p=1.0) cause oscillation death; asynchronous updates (p=0.5) enable stable survival (28% alive)
- **Insight**: Emergence requires temporal disorder — not all cells update simultaneously
- **Reference**: Isotropic NCA uses 50% update rate for similar reasons
- **File**: `lenia_stochastic.py`, `lenia_stochastic_jax.py`

#### 2. Multi-Channel Parameter Diversity = Ecological Diversity 🔴
- **Finding**: Different parameters/channels + weak interaction → rich emergence; same parameters + interaction → synchronized death
- **Analogy**: Different species occupy different ecological niches
- **File**: `lenia_multichannel_jax.py`

#### 3. R=20 is the Sweet Spot
- R=11: Limited structure formation
- R=20: **79.6% structure rate**, life zone covers full parameter space
- R=30: Capped at 12% structure rate (single-channel physical limit, not grid issue)

### Orbium Validation
- **Parameters**: R=20, μ=0.22, σ=0.04
- **Result**: 500 steps stable survival
- **Conclusion**: Orbium is a real stable pattern, not just a coincidence

---

## Next Steps

### Immediate (Tonight)
1. ✅ Parameter space search code created (`lenia_param_search.py`)
2. 🔲 Run the search overnight
3. 🔲 Post findings to Meyo community

### Short-term (This Week)
1. **Asymmetric interaction matrices**
   - Current: symmetric coupling (A↔B)
   - Try: predator-prey style (A→B positive, B→A negative)
   - Expected: More complex ecological dynamics

2. **Pheromone-coupled Lenia**
   - Add diffusing pheromone field
   - Cells sense pheromone and modify growth function
   - Already implemented: `lenia_pheromone.py`

3. **Pattern Zoo**
   - Run continuous search to find stable patterns
   - Classify by: shape, movement, lifespan, interaction
   - Build a "Lenia creature catalog"

### Medium-term (Next Week)
1. **Lenia + NCA Hybrid**
   - Learn Lenia-like patterns with Neural CA
   - Train: single cell → target pattern
   - Combine continuous dynamics with learned rules

2. **Evolutionary Lenia**
   - GA to search for long-lived patterns
   - Fitness: survival time × structure complexity
   - Mutation: perturb kernel, μ, σ

3. **Interactive Visualization**
   - Real-time Lenia with adjustable parameters
   - Click to inject seeds
   - Draw patterns manually

---

## Research Questions

1. **What determines the R=20 sweet spot?**
   - Hypothesis: Balance between locality (small R) and information propagation (large R)
   - R=20 allows enough kernel radius for complex patterns but not too much for dilution

2. **Why does stochasticity help?**
   - Hypothesis: Breaking perfect synchronization prevents resonance disasters
   - Analogy: Why desynchronization prevents bridge collapse

3. **Can we evolve new species?**
   - Current patterns are hand-designed (Orbium, etc.)
   - Can GA discover genuinely new stable forms?

4. **What's the phase diagram?**
   - Alive vs dead, ordered vs chaotic
   - Critical points, phase transitions
   - Edge of chaos hypothesis

---

## File Structure

```
experiments/
├── lenia_jax.py              # Core JAX implementation
├── lenia_stochastic_jax.py   # Asynchronous updates
├── lenia_multichannel_jax.py # Multi-species Lenia
├── lenia_pheromone.py        # Pheromone coupling
├── lenia_param_search.py     # Grid search (NEW)
└── lenia_sweep_*.py          # Various sweep experiments

exploration/
├── lenia_notes.md                    # Initial notes
├── lenia_official_repo_notes.md      # Official repo insights
├── lenia_sweep_report.md             # R=15, R=20 reports
└── 2026-06-25-lenia-roadmap.md       # This file
```

---

## References

- Chan, B. W.-C. (2019). *Lenia - Biology of Artificial Life*. Complex Systems, 28(3), 251–286.
- Lenia Wiki: https://en.wikipedia.org/wiki/Lenia
- Official Repo: https://github.com/Chakazul/Lenia
- Related: Neural Cellular Automata (Mordvintsev et al., 2020)
