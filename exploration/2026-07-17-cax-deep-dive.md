# CAX (Cellular Automata Accelerated in JAX) — Deep Dive

- **Repo**: maxencefaldor/cax
- **Stars**: 262★
- **Paper**: ICLR 2025 Oral (arxiv 2410.02651)
- **License**: Apache 2.0
- **Language**: Python 3.12+, JAX/Flax (NNX)
- **Analyzed**: 2026-07-17 01:59 heartbeat

## Overview

CAX is a comprehensive JAX-based library for cellular automata and artificial life research. It unifies discrete CA, continuous CA (Lenia family), particle systems, boids, and neural CA under one API. **ICLR 2025 Oral paper** — this is the most polished and academically validated CA framework available.

## Architecture

### Three-Layer Design

```
ComplexSystem (abstract base)
  └─ Perceive (neighborhood gathering)
  └─ Update (state transition)
  └─ Render (visualization)
```

**Core abstractions** (`cax.core`):

1. **Perceive**: Converts state → perception. Subclasses:
   - `ConvPerceive`: Learned convolutional filters
   - `MoorePerceive`: Grid neighbor gathering
   - `VonNeumannPerceive`: Von Neumann neighbors
   - `NeighborhoodPerceive`: Generic kernel-based

2. **Update**: Transforms (state, perception) → next_state. Subclasses:
   - `MLPUpdate`: Channel-wise MLP (core of NCA)
   - `ResidualUpdate`: MLP + residual connection + dropout
   - `NCAUpdate`: Residual + alive mask (max_pool based)

3. **ComplexSystem**: `_step()` for single step, `__call__()` for multi-step via `nnx.scan`. Supports `remat` for gradient checkpointing.

### Complex Systems Zoo (20+ implementations)

| System | Type | Key Feature |
|--------|------|-------------|
| Elementary CA | Discrete 1D | Wolfram rules |
| Life | Discrete 2D | Golly rule string parsing |
| Langton's Ant | Discrete agent | Stateful agent on grid |
| Sandpile | Discrete 2D | Self-organized criticality |
| **Lenia** | Continuous | Multi-channel, kernel-based |
| **Flow Lenia** | Continuous | Transport field (advection) |
| **Particle Lenia** | Continuous | Particle-based Lenia variant |
| Reaction-Diffusion | Continuous PDE | Gray-Scott model |
| **Particle Life** | Particle system | N-type interaction matrix |
| Boids | Particle system | Flocking rules |
| **Growing NCA** | Neural CA | Self-organizing shapes |
| Conditional NCA | Neural CA | Conditioned regeneration |
| Unsupervised NCA | Neural CA | Self-discovery of patterns |
| **Diffusing NCA** | Neural CA | Paper's key contribution |
| Self-classifying MNIST | Neural CA | Distributed classification |
| Self-autoencoding MNIST | Neural CA | 3D VAE latent space self-encoding |
| Texture NCA | Neural CA | Style transfer |
| 1D-ARC NCA | Neural CA | Reasoning tasks |
| Attention NCA | Neural CA | Attention-based perception |
| **Leniabreeder** | Evolutionary | QD optimization of Lenia |

## Lenia Implementation Deep Dive

### Rule Parameters (Multi-Channel Support)
```python
LeniaRuleParams:
  channel_source: Array[K]   # which channel each kernel reads
  channel_target: Array[K]   # which channel each kernel writes
  weight: Array[K]           # normalized weight per kernel
  kernel_params: KernelParams(mu, sigma)  # bell-shaped kernel
  growth_params: GrowthParams(mean, std)  # growth function params
```

This is the **cleanest representation of multi-channel Lenia** I've seen. Instead of an explicit K×K interaction matrix, it uses `channel_source` + `channel_target` + `weight` arrays — a sparse, flexible encoding.

### Update Formula
```
G_k = weight_k * growth(U_k | mean_k, std_k)       # per-kernel growth
G   = dot(G_k, kernel_to_channel_matrix)            # aggregate to channels
state = clip(state + G / T, 0, 1)                   # Euler step
```

### Growth Functions
- `exponential_growth_fn`: `2 * bell(u, mean, std) - 1` — maps potential to [-1, 1]
- `bell` function: Gaussian-like peak for sweet-spot selectivity

## Flax NNX Design Patterns

CAX uses the **newest** Flax NNX API (not the older Linen API):

- `nnx.Module`: Replaces `nn.Module`
- `nnx.Pytree`: Data containers
- `nnx.data()`: Tracked parameters
- `nnx.scan`: Multi-step unrolling
- `nnx.Intermediate`: Sow/harvest intermediate states
- `nnx.remat`: Gradient checkpointing
- `nnx.Rngs`: In-module RNG management

This is the **modern JAX ecosystem** that we should adopt for emergence-lab v2.

## Key Innovations

### 1. Diffusing NCA (paper contribution)
- NCA with diffusion-based communication between cells
- Extends Growing NCA with learned diffusion rates
- 3D VAE for latent space self-encoding
- Addresses long-range coordination (weakness of local-only NCA)

### 2. Leniabreeder
- Quality-Diversity (QD) optimization of Lenia rules
- Evolutionary search for diverse, stable life forms
- Uses MAP-Elites algorithm
- Bridges Lenia and evolutionary computation

### 3. Type-Safe Generics
- Python 3.12 type parameters: `ComplexSystem[State, Input]`
- Makes the API self-documenting

## Connection Points to Our Work

1. **Multi-channel Lenia representation** → Our multi-channel Lenia experiments use explicit interaction matrices; CAX's `channel_source`/`channel_target` encoding is more flexible and sparser.

2. **Flax NNX over Linen** → Our emergence-lab uses raw JAX; adopting NNX would give us:
   - First-class pytree management
   - Built-in `nnx.scan` for multi-step (replacing our manual for loops)
   - Rematerialization for long backprop through time
   - Intermediate state harvesting

3. **Leniabreeder** → Our parameter searches are grid-based; QD optimization (MAP-Elites) would be much more efficient at finding diverse morphologies.

4. **Diffusing NCA** → Our stochastic Lenia uses random update masks; diffusing NCA uses continuous diffusion — a hybrid could produce smoother emergent patterns.

5. **Architecture template** → If we refactor emergence-lab v2, CAX's Perceive/Update/ComplexSystem separation is the right design:
   - `Perceive`: local neighborhood → perception (handles both grid and particle)
   - `Update`: perception → state delta (handles both rule-based and NN-based)
   - `ComplexSystem`: orchestration + multi-step + rendering

6. **20+ tested examples** → Each system has a Colab notebook. This is the benchmark for documentation quality.

## Key Files
- `src/cax/core/cs.py`: ComplexSystem base (multi-step scan driver)
- `src/cax/core/perceive/perceive.py`: Perception interface
- `src/cax/core/update/update.py`: Update interface
- `src/cax/core/update/nca_update.py`: NCA with alive mask
- `src/cax/cs/lenia/cs.py`: Lenia system
- `src/cax/cs/lenia/update.py`: Lenia growth + aggregation
- `src/cax/cs/lenia/rule.py`: Multi-channel rule params

## Verdict

**CAX is the best-engineered CA framework available.** It's not just a collection of implementations — it's a properly abstracted, tested, documented library with an ICLR 2025 oral paper. The Flax NNX integration sets a new standard for JAX-based ALife research.

**Action items for our work:**
1. Study Leniabreeder for our parameter search — replace grid search with QD
2. Adopt Perceive/Update separation in emergence-lab v2
3. Consider migrating to Flax NNX for pytree management
4. The `channel_source`/`channel_target` encoding is the right way to do multi-channel Lenia
