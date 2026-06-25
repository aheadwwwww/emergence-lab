# Heartbeat Exploration: Isotropic NCA (Google Self-Organising Systems)

**Date**: 2026-06-25 19:07+
**Source**: Google Self-Organising Systems repo, `experiments/self_org_systems/isotropic_nca/`

## What Is Isotropic NCA?

Neural Cellular Automata (NCA) that learns to grow a target pattern from a single seed cell, then **regenerate** after damage (circle cutouts). Key property: the CA is **isotropic** — rotation-invariant — optionally achieved through steerable perception.

## Architecture Deep Dive

### CA Model (PyTorch, ~128K params)
```
perception(x) → Conv2d(1x1) → ReLU → Conv2d(1x1) → output
```

**Perception types** (6 variants):
1. **laplacian**: `[state, laplacian(state)]` — simplest
2. **lap6**: same but with 6-connected neighborhood (hex grid)
3. **gradient**: `[state, laplacian, rotated_gradient]` — rotation-resolved
4. **steerable**: `[state, rotated_gradient, laplacian]` using explicit angle channel
5. **steerable_nolap**: `[state, rotated_gradient]` — no laplacian
6. **lap_gradnorm**: `[state, laplacian, gradient_norm]` — scalar complexity

### Key Design Patterns

1. **Sobel gradients for edge detection**: `sobel_x, sobel_x.T` filters
2. **Circular padding**: critical for toroidal grid
3. **Stochastic update**: only 50% of cells update each step (`update_rate=0.5`)
4. **Alive mask**: cells die when no alive neighbor within kernel radius
5. **Gradient normalization**: `p.grad /= p.grad.norm()` — stabilizes training

### Training Loop Insights

- **Pool-based**: maintains 256 samples in a pool, samples 8 per batch
- **Step n randomization**: 64-96 steps per episode → temporal robustness
- **Damage-injection**: circular zero-out every 6 steps → forces regeneration
- **Multi-loss**: target_loss + overflow_loss + difference_loss
  - `target_loss_f(x)` = distance to target image (first frame + last frame)
  - `overflow_loss` = penalize values outside [-2, 2] for scalar channels
  - `diff_loss` = smoothness penalty (10x weight)
- **CyclicLR**: triangular learning rate cycling (1e-5 → 1e-3, 2000-step cycle)
- **Seed injection**: replace batch[0] with fresh seed every N steps
- **Dead cell revival**: if all cells dead, re-seed

### Auxiliary Channels
Target patterns can include extra channels:
- `noaux`: pure RGB+alpha pattern (e.g., spiderweb)
- `binary`: +1 stripe mask (e.g., lizard)
- `minimal`: +2 aux channels (e.g., heart)
- `extended`: more aux masks

## Connection to Our Lenia Work

| Isotropic NCA | Our Lenia |
|---------------|-----------|
| Learned update rule (CNN) | Hand-designed kernel + growth function |
| Single seed → target pattern | Continuous field with initial condition |
| 16 channels (state vector) | 3 channels (RGB) |
| Damage → regeneration | Perturbation → pattern shift |
| Stochastic update (50%) | Deterministic step |
| Gradient-normed training | Genetic parameter search |
| Pool-based training | Batch param scan |

### Inspirations for Lenia

1. **Stochastic updates**: Our Lenia is fully synchronous. Asynchronous updates (like Isotropic NCA's 50% rate) could create more organic patterns
2. **Perception channels**: We use basic kernel convolution. Adding Sobel gradients or steerable perception could reveal directional patterns
3. **Pool-based evolution**: Instead of sequential parameter scans, maintain a diverse pool of Lenia configurations and evolve them
4. **Damage resistance training**: Our pheromone coupling creates resilience — formalize as a "damage test" metric
5. **Auxiliary target channels**: Could train Lenia to grow toward multiple targets simultaneously
6. **Gradient normalization**: Apply to our genetic algorithm's parameter updates

### Potential Experiment

Implement a **learnable Lenia** where:
- Growth function is a small NN (like NCA) instead of hand-coded Gaussian
- Train via pool-based method to produce specific patterns
- Add damage-resistance as training objective
- Compare with our genetic algorithm approach

## Reference
- Paper: "Growing Isotropic Neural Cellular Automata" (Mordvintsev et al., 2020/2021)
- Repo: github.com/google-research/self-organising-systems
- Related: Self-replicating NNs (same repo, ALIFE 2021)
