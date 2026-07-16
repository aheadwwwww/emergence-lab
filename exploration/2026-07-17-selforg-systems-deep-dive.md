# Google Self-Organising Systems — Deep Dive

- **Repo**: google-research/self-organising-systems (Google Research)
- **Key People**: Alexander Mordvintsev, Ettore Randazzo
- **Domain**: Cellular Automata, Neural CA, ALife, Texture Synthesis
- **Analyzed**: 2026-07-17 02:59 heartbeat

## Overview

The official Google Research codebase for self-organising systems research — the same group behind **Growing Neural CA** (Distill.pub, 2020). Contains three major subsystems:

1. **Biomaker CA** — ALife biome simulation with agents, materials, nutrients, evolution
2. **Texture CA** — Neural CA-based texture synthesis
3. **Self-Replicating NN** — Recursively fertile self-replicating neural networks

---

## 1. Biomaker CA (2023, arXiv 2307.09320)

The most sophisticated system in the repo. A **biome simulation engine** built on JAX/Flax.

### Architecture

#### Three-Grid State Representation
```
Environment(type_grid: uint32[H,W],        # material type per cell
            state_grid: float32[H,W,S],    # internal state (integrity, age, nutrients, agent_state)
            agent_id_grid: uint32[H,W])    # unique program IDs for agents
```

**State layout per cell** (9 channels):
| Index | Field |
|-------|-------|
| 0 | Structural integrity |
| 1 | Age |
| 2-3 | Nutrients (earth, air) |
| 4-... | Agent internal state |

#### Materials (Cell Types)
- **VOID** — empty space
- **AIR** — spreads through VOID; carries airborne nutrients
- **EARTH** — structural material; supports plants/buildings; carries soil nutrients
- **FIRE** — destructive; burns organic matter
- **AGENT** — programmable organisms; carry genome/neural net params

#### Three Operation Types
The simulation uses a **conflict-resolution model**:

1. **Parallel Operations** (`ParallelOp`) — independent actions that don't conflict (e.g., aging, nutrient diffusion). All executed, no resolution needed.

2. **Exclusive Operations** (`ExclusiveOp`) — actions where only one proposer wins (e.g., eating, attacking, spawning into a neighbor cell). Uses random arbitration per target cell.

3. **Reproduction Operations** (`ReproduceOp`) — agent reproduction with variation. Supports both asexual (mutations) and sexual (crossover) reproduction.

#### Step Pipeline
```
step_env():
  1. env_increase_age()              — age counter
  2. balance_soil()                  — nutrient diffusion
  3. process_energy()                — energy consumption/movement
  4. process_structural_integrity()  — structural collapse
  5. env_process_gravity()           — material falling
  6. Parallel phase:                 — agents produce ParallelOps
  7. Exclusive phase:                — cells produce ExclusiveOps → resolved via conflict
  8. Reproduce phase:                — reproduction with mutation/crossover
  9. Apply all updates               — commit state changes
```

#### Agent Logic System
Agents use **evojax** for neural network policies. The `AgentLogic` ABC defines:

- `initialize(key)` → param vector
- `par_f(key, perc, params)` → ParallelInterface (parallel actions)
- `excl_f(key, perc, params)` → ExclusiveInterface (exclusive actions, spawn)
- `repr_f(key, perc, params)` → ReproduceInterface (reproduction)

The perception (`PerceivedData`) is a 3×3 neighborhood of type, state, and agent IDs.

#### Mutation System (in-environment evolution)
- **Mutator** (asexual): Gaussian noise on genome
- **SexualMutator**: Crossover + Gaussian noise
- Supports in-environment mutation rates as learnable parameters
- `initialize()` appends mutation hyperparams to agent genome

#### DNA Library (dnalib/)
Persistence files (`persistence_1697720583799231923.npy/.txt`) — saved genome/program states from evolved simulations.

### Key Design Insights

1. **Conflict-resolution paradigm** is essential for any multi-agent CA — novel compared to standard Lenia/Life where all cells update simultaneously.

2. **Three-layer grid** (type, state, agent_id) is more expressive than single-layer grids — enables material physics + agent logic in same space.

3. **In-environment evolution** via `Mutable Program` is rare in CA frameworks — agents can evolve their behavior during simulation.

4. **Framework choice**: JAX/Flax over TensorFlow (moving away from TF used in earlier Growing NCA work).

---

## 2. Texture CA (TensorFlow-based)

Neural CA applied to texture synthesis (pre-dates the JAX migration).

### Architecture
```
CAModel:
  perceive() → 4-channel (identity, dx, dy, laplacian) per input channel
  DenseLayer × 2 → hidden → output
  Stochastic update: fire_rate controls update probability per cell
```

- Uses **Sobel filters + Laplacian** for perception (4 filters per channel)
- **Fake quantization** for model compression (`fake_quant`)
- **SamplePool** training strategy: maintains a pool of candidate textures, samples, evaluates loss, commits best
- **Loss models**: Style loss (VGG-based) or Inception activation maximization
- **Ancestor-based training**: warm-start from pre-trained textures

### Key Design
- Per-frame Sobel derivatives as perception primitives
- SamplePool avoids collapse to single texture
- TF.js compatible export (`ca.html`, `ca.js`) for browser demo

---

## 3. Self-Replicating NN (Jupyter Notebook)

- `recursively_fertile_self_replicating.ipynb`
- Companion to the self-replicating neural networks paper
- Focus on **recursive self-replication** in neural cellular automata

---

## 4. Adversarial Reprogramming CA

- Two notebooks exploring adversarial perturbations:
  - `adversarial_growing_ca.ipynb` — adversarial attacks on Growing NCA
  - `adversarial_mnist_ca.ipynb` — adversarial attacks on MNIST CA
- Pre-computed perturbation models and target images in `assets/`

---

## Connections to Our Work

### 1. Biomaker CA → Multi-material Lenia
Our Lenia work is single-material (continuous field). Biomaker CA's type_grid + state_grid separation enables multiple materials with different physics (air spreads, earth holds, fire burns, agents act). This could inspire a **multi-material Lenia** extension where different channels have different interaction rules.

### 2. Conflict Resolution → Stochastic Lenia
Our stochastic Lenia uses random update masks; Biomaker's ExclusiveOp arbitration is a principled way to handle competing actions. Could be adapted for Lenia where multiple kernels compete for the same cell.

### 3. In-environment Evolution → Evolutionary Lenia
Biomaker's Mutator system enables evolution within the simulation loop. This is more sophisticated than our grid-search parameter sweeps — agents can adapt during simulation.

### 4. Three-Grid Architecture → emergence-lab v2
The `(type_grid, state_grid, agent_id_grid)` separation is cleaner than our flat multi-channel approach. Type defines identity, state holds continuous values, agent_id tracks provenance.

### 5. Texture CA Perceive → Lenia Kernel Design
Texture CA's fixed perceive (Sobel + Laplacian) is a static feature extraction. Lenia's learned bell kernels are more expressive but both serve similar roles: encoding local structure.

### 6. Step Efficiency
The step_env function is massive (single JIT-compiled function with many static args). This is the JIT-principled approach we should adopt — compile the entire step, not individual kernels.

### 7. Google Research pedigree
Mordvintsev = inventor of Neural CA, DeepDream, Lenia. The code quality and design patterns set the standard for the field.

---

## Key Files Examined
- `self_organising_systems/biomakerca/environments.py` — Environment namedtuple, EnvConfig, type definitions
- `self_organising_systems/biomakerca/env_logic.py` — Core simulation logic (1700+ lines)
- `self_organising_systems/biomakerca/agent_logic.py` — Agent interface + example MLP agent
- `self_organising_systems/biomakerca/cells_logic.py` — AIR, EARTH material behavior
- `self_organising_systems/biomakerca/step_maker.py` — step_env orchestration
- `self_organising_systems/biomakerca/mutators.py` — In-environment mutation system
- `self_organising_systems/biomakerca/dnalib/` — Persisted evolved genomes
- `self_organising_systems/texture_ca/ca.py` — Neural CA for texture synthesis
- `self_organising_systems/texture_ca/texture_synth.py` — Texture training pipeline
- `self_organising_systems/shared/video.py` — FFmpeg video writer

## Verdict

This is the most practically relevant CA/ALife repository we've explored. The Biomaker CA system directly addresses questions we've been exploring: **multi-material interaction, in-environment evolution, and conflict resolution**. The step_env pipeline is a model for how to structure efficient JAX-based ALife simulations. The Texture CA shows how NCA can be applied to generation tasks beyond biological simulation.
