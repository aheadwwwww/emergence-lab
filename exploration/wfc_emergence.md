# Wave Function Collapse: Local Constraints → Global Emergence

**Date**: 2026-06-24
**Experiment**: `experiments/wfc_demo.py`
**Source**: [mxgmn/WaveFunctionCollapse](https://github.com/mxgmn/WaveFunctionCollapse) (cloned)

## What It Does
WFC generates output images that are **locally similar** to an input bitmap:
- (C1) Output should contain only NxN patterns that exist in the input
- (Weak C2) Distribution of NxN patterns should match input

## Algorithm
1. **Count patterns** from input
2. **Initialize wave** — every output cell in superposition of all patterns
3. **Observation-Propagation cycle**:
   - Observe: pick cell with lowest Shannon entropy, collapse to definite state
   - Propagate: constrain neighbors based on adjacency compatibility
4. Repeat until all cells observed or contradiction detected

## Key Insight
WFC is fundamentally an **emergence algorithm**:
- **Local rules** (pattern adjacency constraints) → **global structure**
- **Superposition** before collapse models the space of possibilities
- **Contradictions** happen when constraints over-constrain the system (NP-hard in general)
- **Entropy minimization** chooses the most constrained cell → emergent order

## Connection to Emergence Nodes
| Node | Connection |
|------|-----------|
| #001 Emergence | Pure case: local constraints → global pattern without top-down design |
| #003 Edge of Chaos | Contradiction rate vs output quality: too much constraint = boring, too little = random |
| #022 Open-Endedness | Simple tiled model variant can generate infinite tilemaps |
| #019 Strange Loops | Superposition to collapse mirrors quantum weirdness |
| #013 Attention | Entropy minimization as an attention mechanism |

## Result
- Simple 5x5 pattern → consistent 30x30 output preserving local features
- Smaller N = more variety (less constraint)
- Larger N = more faithful to input but more contradictions

## Relevance
WFC models how **local constraints spontaneously organize** into global order — the same mechanism behind crystal growth, cellular automata, and constraint satisfaction in neural networks.
