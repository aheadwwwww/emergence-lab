# Multi-Channel Lenia Breakthrough: Asymmetric Parameters

**Date**: 2026-06-25
**Session**: Heartbeat exploration

## Key Discovery

**Different parameters per channel prevent synchronization even with cross-channel mixing.**

## Experimental Results

### Test 1: Asymmetric Params + Mild Cross-talk (α=0.15)
```
R=[20, 17, 14], mu=[0.22, 0.20, 0.18], sigma=[0.04, 0.035, 0.03]
Score: 0.317, Alive: 17.9%, Correlation: 0.10
```

### Test 2: Asymmetric Params + No Cross-talk (α=0)
```
R=[20, 17, 14], mu=[0.22, 0.20, 0.18], sigma=[0.04, 0.035, 0.03]
Score: 0.286, Alive: 10.9%, Correlation: 0.00
```

## Analysis

1. **Cross-talk HELPS when channels have different parameters**
   - The α=0.15 case has higher score AND alive fraction
   - Channels interact constructively, creating richer patterns
   - Different R, μ, σ values create different "species" that can coexist

2. **Mechanism**
   - Each channel develops its own pattern due to different parameters
   - Cross-talk allows channels to influence each other
   - But because their "rules" differ, they can't fully synchronize
   - Result: emergent multi-scale, multi-species dynamics

3. **Implications for Artificial Life**
   - Multi-channel Lenia can support "ecosystems" of different species
   - Parameter diversity creates niches
   - Cross-talk creates interaction without collapse into uniformity
   - This is analogous to biological ecosystems with multiple species

## Comparison with Earlier Findings

| Config | Score | Alive | Corr |
|--------|-------|-------|------|
| Same params, α=0 (identity) | 0.34 | 0.22 | 0.03 |
| Same params, α=0.3 | 0.14 | 0.20 | 1.0 (sync!) |
| Diff params, α=0.15 | 0.32 | 0.18 | 0.10 |
| Diff params, α=0 | 0.29 | 0.11 | 0.00 |

**Key insight**: Same parameters + cross-talk = death by synchronization. Different parameters + cross-talk = richer life!

## Next Steps

1. **Parameter search**: Find optimal R, μ, σ combinations for multi-species Lenia
2. **Asymmetric mixing**: Try directional mixing (R→G strong, G→R weak)
3. **Larger grids**: 384×384 or 512×512 for more spatial room
4. **Species tracking**: Identify and track distinct pattern types across channels
5. **GIF animation**: Visualize the evolutionary dynamics

## Biological Analogy

This mirrors real ecosystems:
- Same species compete directly → one dominates
- Different species with niches → coexistence
- Inter-species interaction → richer ecosystems

The "parameters" are like biological niches - different enough to coexist, similar enough to interact.