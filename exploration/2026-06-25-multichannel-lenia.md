# Multi-Channel Lenia (RGB): First Run Results

**Date**: 2026-06-25
**File**: `experiments/lenia_multichannel_jax.py`

## Implementation

Extended single-channel Lenia to 3-channel (RGB) with:
- 3 parallel grids with independent parameters per channel
- Mixing matrix for cross-channel interaction (3×3 weights)
- `jax.lax.switch` for growth function dispatch
- RGB composite visualization + per-channel breakdown
- 5 mixing presets + sweep mode

## Key Findings

### 256×256 grid, R=20, mu=0.22, sigma=0.04 (all channels same)

| Preset | Score | Alive | Channel Corr | Notes |
|--------|-------|-------|-------------|-------|
| Identity (α=0) | 0.34 | 0.218 | 0.03 ✅ | Best! Independent evolution, diverse RGB |
| Mild cross (α=0.3) | 0.14 | 0.197 | 1.0 ❌ | Channels synchronize immediately |
| Strong cross (α=0.7) | 0.12 | 0.146 | 1.0 ❌ | Even worse sync, less alive |
| Cyclic (R→G→B→R) | 0.20 | 0.000 | — | Dies instantly, no self-feedback |
| Inhibitory (α=-0.3) | 0.30 | 0.137 | 0.02 ✅ | Diverse but less alive |

### Insights

1. **Positive cross-talk kills diversity**: Even weak coupling (0.3) causes channel synchronization within ~80 steps. Three channels with identical params behave identically when coupled.

2. **Identity is optimal for same params**: When channels share parameters, keeping them independent (no mixing) yields the best score.

3. **Inhibition preserves diversity**: Negative cross-talk keeps channels different (like competitive species), but reduces overall aliveness.

4. **No self-feedback = death**: The cyclic preset (R←G←B←R) with 0.0 on diagonal dies immediately. Each channel needs its own convolution to survive.

### Next Steps

- **Channel-specific params** (different mu/sigma/R per channel) to create asymmetric dynamics even with cross-talk
- **Asymmetric mixing** (e.g., R→G strong, G→R weak) for directional interaction
- **GIF animation** of evolution
- **Larger grid** (384+) for more spatial room
- **Compare with official Lenia** RGB implementation for validation

## Current Limitations

- All channels use same kernel shape (bump4)
- No channel-specific dt or normalization
- Mixing matrix is constant — no spatial or temporal variation
