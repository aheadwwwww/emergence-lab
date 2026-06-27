# Turmites Experiment - 2026-06-27

## What are Turmites?

Turmites are 2D Turing machines - a generalization of Langton's Ant where both the grid cells and the "ant" (turmite) can have multiple states. This creates much richer emergent behavior than the binary Langton's Ant.

## Implementation

Created `experiments/core/turmites.py` with:

### Core Classes
- `Turmite`: 2D Turing machine with configurable states and transition rules
- Supports arbitrary number of cell states and internal turmite states
- Random rule generation for exploration
- Famous configurations (Langton's Ant, Turmita, Spiral)

### Features
- **Pattern Classification**: Automatically classifies results as 'highway', 'symmetric', 'chaotic', 'sparse', or 'dense'
- **Visualization**: Color-coded output based on cell states
- **Batch Exploration**: `explore_turmites()` for parameter sweeps

## Results (First Run)

```
Langton's Ant (binary, single state): sparse pattern
Random Turmites (5 experiments):
  - sparse: 4
  - symmetric: 1
```

## Key Insight

Most random turmite configurations result in sparse patterns, suggesting that highway-creating or symmetric patterns require specific rule structures. This aligns with the idea that complex emergent behavior is rare in rule space.

## Relation to Other Experiments

- **Langton's Ant**: Special case of turmite (binary cells, single internal state)
- **Wolfram CA**: 1D equivalent of state transition rules
- **Turing Machines**: Turmites are essentially Turing machines on a 2D tape

## Next Steps

1. Implement rule-space search for "interesting" patterns
2. Add multi-turmite interactions (multiple agents on same grid)
3. Evolve transition rules using genetic algorithms
4. Compare pattern complexity with Langton's Ant

## Files

- `experiments/core/turmites.py` - Main implementation
- `D:/emergence_experiments/langton_ant_*.png` - Output images
- `D:/emergence_experiments/turmite_*.png` - Random turmite outputs

## Reference

Turmites were first described by Greg Turk in 1987 as a way to study emergent behavior in multi-state cellular automata.
