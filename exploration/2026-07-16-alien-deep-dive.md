# ALIEN Deep Dive — 2026-07-16

## Overview

**chrxh/alien**: 5449★, C++/CUDA, BSD-3-Clause
ALIEN = Artificial LIfe ENvironment

ALIEN is a CUDA-powered 2D particle engine for artificial life simulation, winner of ALIFE 2024 Virtual Creatures Competition. Simulates soft bodies and fluids with millions of particles entirely on GPU.

## Architecture

```
source/
├── EngineInterface/     # Public API layer
├── EngineImpl/          # Facade + worker coordination
├── EngineKernels/       # ~70 CUDA kernel files (the heart)
├── Gui/                 # OpenGL rendering + editing tools
└── Network/             # Simulation browser + sharing
```

Key observation: The project has a clean layer separation — EngineInterface defines contracts, EngineImpl orchestrates, EngineKernels does the heavy GPU lifting.

## Core Simulation Model

### Particle Network Organisms
- Each "organism" is a graph of particles connected by edges
- Particles have physical properties (mass, stiffness, adhesion)
- Neural networks control higher-level cell functions
- Genome encodes the blueprint for offspring

### Cell Types (15 types!)
Each node in the organism graph is a "cell" with a specific function:

| Type | Function |
|------|----------|
| Base | Structural cell |
| Depot | Energy storage |
| Sensor | Detect energy/solids/free cells/creatures (4 sub-modes) |
| Generator | Square or sawtooth signal generator |
| Attacker | Attack free cells or other creatures |
| Injector | Inject genes into targets |
| Muscle | 6 movement modes: auto/manual/angle bending, auto/manual crawling, direct |
| Defender | Defense against attacks |
| Reconnector | Connect to solids/free cells/creatures |
| Detonator | Countdown-based self-destruct |
| Digestor | Digest raw energy from environment |
| Memory | 4 modes: delay, recorder, storage, integrator |
| Communicator | Send/receive signals between organisms |
| Constructor | Build offspring from genome |
| Void | Placeholder / dead cell |

### Neural Network Architecture
- Per-cell neural network with NEURONS_PER_CELL neurons
- Full weight matrix: `weights[NEURONS_PER_CELL × NEURONS_PER_CELL]`
- Plus biases and activation functions
- Input = sum of connected cells' signals × connection weights
- Output = cell signal → drives cell behavior
- Runs entirely on CUDA via matrix-vector multiplication

### Genome Structure
```
Genome
├── id (uint64)
├── numGenes
├── Gene[]
│   ├── shape (ConstructorShape)
│   ├── stiffness
│   ├── connectionDistance
│   ├── homogeneousCellType
│   └── Node[]
│       ├── referenceAngle (position in organism)
│       ├── color
│       ├── neuralNetwork (NeuralNetGenome)
│       ├── cellType + cellTypeData
│       └── constructor (optional)
└── MutationRates (20+ mutation types!)
```

### Mutation System
ALIEN implements an extremely comprehensive mutation system:

**Neural mutations:**
- Neuron weight changes (with configurable sigma)
- Bias changes
- Activation function changes
- Connection weight/value changes

**Structural mutations:**
- Cell type property changes
- Cell type mode changes (e.g., sensor → muscle)
- Cell type changes
- Void mutations (deactivate cell)
- Geometry mutations

**Morphological mutations:**
- Add/delete/duplicate genes (whole body segments)
- Add/delete/trim/copy/move nodes
- Extend genes

**Constructor mutations:**
- Constructor property/value/enum changes
- Constructor toggle (enable/disable reproduction)

Each mutation has independent probability and magnitude parameters — this is hundreds of tunable knobs for evolution!

## Connections to Our Work

### 1. Cell Type System → Multi-Channel Lenia
ALIEN's 15 cell types are conceptually similar to our multi-channel Lenia. Each "channel" has different behavior rules. ALIEN formalizes this with typed cells + mode-specific parameterization.

**Insight:** We could design a "CellType" abstraction for Lenia channels — each channel gets a behavior specification (growth kernel, interaction matrix, energy budget) rather than just a different kernel.

### 2. Neural Network Control → Neural Lenia
ALIEN's per-cell neural networks are exactly what our Neural Lenia prototype aims for! Key differences:
- ALIEN: discrete particles, NN drives physical behavior
- Our Neural Lenia: continuous field, NN generates kernel values

**Insight:** ALIEN's approach of "NN output → behavior" (not "NN output → next state") is more biologically plausible. A cell's NN determines what it *does*, not what it *becomes*. We could reframe Neural Lenia: NN outputs growth/movement parameters, state update is a separate physics step.

### 3. Constructor System → Self-Replication
ALIEN has a full construction/reproduction pipeline:
- Constructor cell reads genome
- Builds offspring cell-by-cell at specified angle
- Optionally auto-triggers at intervals
- Provides energy to offspring

**Insight:** For Lenia self-replication, we'd need a different mechanism (continuous field can't "construct" discretely), but ALIEN's constructor concept — a specialized cell type that reads blueprint and executes construction — is transferable to CA architectures.

### 4. Energy Economy → Resource Constraints
ALIEN has a detailed energy system:
- Depot cells store energy
- Digestor cells harvest from environment
- Construction costs energy
- Muscle movement costs energy

**Insight:** Adding an energy/resource layer to Lenia would introduce natural selection pressure. Cells that grow efficiently survive; wasteful patterns die. This bridges "pretty patterns" → "ecosystem simulation."

### 5. Communication → Inter-Organism Signaling
ALIEN's Communicator cells can send/receive signals between organisms with:
- Range limits
- Color-based filtering
- Lineage-based filtering

**Insight:** Our multi-channel Lenia already has inter-channel interactions via the mixing matrix. ALIEN adds *spatial range* and *identity filtering* — these could be added to Lenia interaction matrices.

### 6. GPU-First Design
ALIEN runs *everything* on CUDA, including:
- Physics simulation
- Neural network computation
- Mutation application
- Statistics collection

**Insight:** Our JAX-based Lenia already uses GPU acceleration. ALIEN shows it's feasible to push even more computation (NN, evolution) to GPU for million-particle scale.

## Key Design Patterns

### Pattern 1: Entity-Component with GPU Arrays
ALIEN uses SoA (Structure of Arrays) layouts optimized for GPU coalesced access:
```cuda
Entities {
    Object[] objects;        // contiguous array
    // Each Object is POD, GPU-friendly
}
```

### Pattern 2: Processor-per-Behavior Pattern
Each cell behavior has its own Processor class:
- `NeuronProcessor::calcSignal()` — neural computation
- `MuscleProcessor::applyForce()` — movement
- `ConstructorProcessor::build()` — reproduction
- etc.

All processors read the same simulation data and write results to output buffers.

### Pattern 3: Genome as Pure Data
Genome is a POD struct with pointers to heap arrays. This allows:
- Direct GPU memory allocation
- Efficient copying for mutation
- Serialization for network transfer

## Takeaways for Our Projects

1. **Cell type taxonomy**: ALIEN's 15 cell types form a good vocabulary for agent-based simulation. We can adopt similar categories for emergence-lab v2.

2. **Comprehensive mutation**: ALIEN's 20+ mutation types show what "complete" evolution looks like. Our GA experiments only had basic bit-flip/sigma mutations.

3. **Energy economy matters**: ALIEN's depot/digestor/energy system creates real selection pressure. Without resource constraints, evolution is just "more complex = better."

4. **CUDA-native design**: Worth considering if we want to scale beyond what JAX can handle for interactive simulations.

5. **Constructor-driven reproduction**: A specialized "builder" cell type that reads genomes and assembles offspring is a powerful abstraction that could work in discrete CA too.
