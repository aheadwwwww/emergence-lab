# Reaction-Diffusion-Lenia Hybrid: Combining RD Systems with Lenia

**Date**: 2026-06-25 20:05
**Status**: Exploration

## Motivation

We've explored three major classes of emergent systems:
1. **Reaction-Diffusion** (Turing Patterns): Two chemicals U and V, U autocatalyzes, V inhibits
2. **Lenia**: Continuous CA with smooth kernel and growth function
3. **Stochastic Updates**: Asynchronous cell updates for stability

What if we combine them?

## The Hybrid Idea

**RDL (Reaction-Diffusion-Lenia)** = Lenia's growth function + Gray-Scott's two-component dynamics

```
dA/dt = D_A ∇²A + G_A(A, B, U_A, mu_A, sigma_A)
dB/dt = D_B ∇²B + G_B(A, B, U_B, mu_B, sigma_B)
```

Where:
- G_A, G_B are **Lenia growth functions** (instead of standard polynomial)
- U_A = K_A * A (kernel convolution of A with A's kernel)
- U_B = K_B * B (kernel convolution of B with B's kernel)
- Cross-channel coupling via U terms

### Key Questions

1. **Does Lenia's growth function (bell curve) produce richer patterns than Gray-Scott's cubic?**

   Gray-Scott uses: f(u,v) = u²v, -u²v (polynomial)
   Lenia uses: G(U) = exp(-(U-μ)²/(2σ²)) * 2 - 1 (Gaussian bell)

   The bell curve creates a "life zone" where growth happens in a specific band of U.
   This is more flexible than the cubic which has fixed zeros.

2. **Can we find Lenia "species" in an RD system?**

   If we treat each component's kernel as a "niche" and the growth parameters as "species traits",
   the interaction between A and B through the U terms could create:
   - Predator-prey dynamics
   - Symbiosis
   - Ecosystem of Lenia species

3. **Does stochastic updating improve RD-Lenia stability?**

   Based on our earlier finding that p=0.5 update probability enables survival,
   we could test this in the hybrid system.

## Design

### Two-Component Lenia

```python
def rdl_step(A, B, params):
    # Each component has its own kernel
    U_A = FFT_conv(A, K_A)
    U_B = FFT_conv(B, K_B)
    
    # Growth with cross-coupling
    G_A = lenia_growth(U_A + alpha_AB * U_B, mu_A, sigma_A)
    G_B = lenia_growth(U_B + alpha_BA * U_A, mu_B, sigma_B)
    
    # Reaction terms (like Gray-Scott)
    R_A = G_A - fed * B   # B inhibits A (predation-like)
    R_B = G_B + kill * B  # B decays (prey-like)
    
    A_new = A + (D_A * laplacian(A) + R_A) * dt
    B_new = B + (D_B * laplacian(B) + R_B) * dt
    
    return clip(A_new), clip(B_new)
```

### Parameter Space

| Parameter | Meaning | Typical Range |
|-----------|---------|---------------|
| R_A, R_B | Kernel radii | 5-30 |
| mu_A, mu_B | Growth centers | 0.05-0.3 |
| sigma_A, sigma_B | Growth widths | 0.01-0.05 |
| D_A, D_B | Diffusion rates | 0.05-0.5 |
| alpha_AB | A→B coupling | -0.2 to 0.2 |
| alpha_BA | B→A coupling | -0.2 to 0.2 |
| fed, kill | Gray-Scott rates | 0.01-0.1 |

## Connection to Our Previous Work

### 1. Multi-channel Lenia → Direct precursor
Multi-channel showed that **different parameters on different channels** creates diversity.
Two-component RD adds explicit predator-prey dynamics.

### 2. Pheromone Coupling → Weak coupling insight
Weak spatial coupling (influence=0.05) works better than strong.
Same principle should apply to RDL: small alpha values are more stable.

### 3. Stochastic Updates → Temporal noise
Async updates (p=0.5) prevent oscillation death.
Likely even more important in 2-component systems where oscillations are inherent.

### 4. Edge of Chaos → Sweet spot
R=20 was the sweet spot for single-channel Lenia.
RDL adds diffusion rates as a new dimension — classic Turing instability requires D_U << D_V.

## Hypotheses

1. **H1**: RDL produces more diverse patterns than either RD or Lenia alone
2. **H2**: Small cross-coupling (|alpha| < 0.1) yields the most interesting behavior
3. **H3**: Stochastic updates are crucial for stability in 2-component systems
4. **H4**: There exist parameter combinations where Lenia species and Turing spots coexist

## Implementation Plan

1. Basic RDL in NumPy (quick prototype)
2. JAX acceleration (for parameter sweeps)
3. Phase diagram: R vs mu vs D_A/D_B ratio
4. Visual comparison: standard RD vs RDL

## Related Work

- Bert Chan's Lenia paper mentions multi-component extensions but doesn't explore RD hybrids
- Gray-Scott is the classic RD system (Pearson, 1993)
- No published work on exact RDL hybridization found in our scan

---

**Tag**: #reaction-diffusion #lenia #hybrid #turing-patterns #emergence
