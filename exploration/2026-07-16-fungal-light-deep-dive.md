# FungalLight Deep Dive — SIGGRAPH Asia 2024 Fungal Growth Simulator

- **Repository**: https://github.com/sunyitong/FungalLight
- **Paper**: "Exploring Fungal Morphology Simulation and Dynamic Light Containment from a Graphics Generation Perspective", SIGGRAPH Asia 2024 Art Papers
- **DOI**: 10.1145/3680530.3695440
- **arXiv**: 2409.05171
- **Tech**: Rust + Bevy 0.13 ECS, 512×512 grid
- **License**: MIT

## Architecture Overview

FungalLight is a compact (~250 lines simulation code) Rust/Bevy prototype that simulates fungal growth as a 2D cellular automaton with resource-based growth, restriction masks, and boundary light feedback.

### Core ECS Components (components.rs)

```
Fungi Bundle:
  - FungiDefault (marker)
  - FoodConsumptionSpeed (f32, randomized 0.8~1.2)
  - IsAlive (bool)

FungiExperimental Bundle (unused in current sim, future extension):
  - FungiExperimentalType
  - GrowthDirection, GrowthCurve, SplitProbability
  - FoodConsumptionSpeed, IsAlive

Light Bundle:
  - LightDefault (marker)
  - OpenCounting (u32, starts at LIGHT_LIFE_TIME)
  - IsAlive (bool)

Resources (global state):
  - GridFood: Vec<Vec<f32>>        ← resource map
  - GridRestriction: Vec<Vec<i32>> ← binary mask from image
  - FungiSpawnPositionList: HashSet<(i32,i32)>
  - FungiExistPositionList: HashSet<(i32,i32)>
```

### Growth Loop (systems.rs)

**update_fungi system** — runs each frame for every living fungus:
1. **Random death**: p=0.0004 per frame
2. **Local sampling**: pick random (dx, dy) within ±FUNGI_STEP_DISTANCE (1)
3. **Spawn check**:
   - If target is free: queue spawn position → FungiSpawnPositionList
   - If target is restricted (mask=1): emit Light at boundary
4. **Resource consumption**: cell food -= consumption_speed
5. **Starvation death**: when food ≤ 0
6. **Visual state**: 3-tier color coding (100%, 70%, 30% food levels)

**spawn_fungi system**: consumes FungiSpawnPositionList, creates new Fungi entities at unique positions

**update_light system**: Light entities count down LIGHT_LIFE_TIME (20 frames), then fade out

### Restriction Mask System

- Input: PNG image (`Artboard 1.png`), must match CANVAS_SIZE (512×512)
- `process_image_to_restriction`: reads a specific channel (index 1 = green), marks pixels where channel == 255 as restriction=1
- Coordinate flip: `new_y = canvas_size - 1 - y` (image origin top-left → simulation origin bottom-left)
- Also has `fill_square` for procedural geometric restrictions

### Light Path Analysis (sort_light_path)

- Collects active light positions, computes pairwise distances
- `find_connected_components`: builds threshold-distance graph, runs BFS for connected components
- Connects light markers into paths along restriction boundaries
- LIGHT_PATH_SORT_THRESHOLD = 10.0 pixels

### Visual Features

- **Bloom (Beauty renderer)**: HDR camera + TonyMcMapface tonemapping + BloomSettings for glow effects
- **3-tier fungi coloring**: red at high food → dark red at low food → blue when dead
- **Light at boundary**: yellow markers with 20-frame lifetime + bloom glow

## Key Design Insights

### 1. ECS-Native Simulation
Bevy ECS naturally models the simulation as entity-component updates. Each fungus is an entity; systems process them in parallel. This is fundamentally different from array-based CA — it's more like a particle simulation with CA-like local rules.

### 2. Hash-Set Deduplication
`FungiExistPositionList` prevents duplicate spawning at the same grid cell. `FungiSpawnPositionList` decouples the decision to spawn from the actual spawning — a two-phase pattern that prevents iteration-modification issues.

### 3. Resource-Mediated Evolution
Food consumption creates implicit selection pressure. Fungi with lower consumption speed survive longer, enabling implicit "fitness" differences without explicit genetics. The `FungiExperimental` bundle hints at future extensions with growth direction, curvature, and split probability components.

### 4. Boundary as Light Interface
When growth hits a restriction pixel, a light marker is emitted instead. This is the core "light containment" concept — the boundary becomes visible through accumulated light, like bioluminescent fungi tracing the edges of an obstacle.

### 5. Minimalism Wins
The entire simulation is ~250 lines of Rust. The Bevy engine handles rendering, ECS scheduling, bloom, and asset loading. The simulation code is pure logic.

## Connections to Our Lenia / Artificial Life Work

### 1. Resource-Mediated Selection → Energy Economy
FungalLight's GridFood system is a simple version of the energy economy we're building into multi-species Lenia. Each entity consumes at its own rate, starvation causes death, and consumption rate acts as implicit fitness.

### 2. Restriction Mask → Environment Sculpting
The image-based restriction mask is a powerful idea for Lenia — instead of just periodic boundary conditions, we could load a PNG environment map where:
- Different colors → different "terrain types" (food-rich, barren, barrier)
- Alpha channel → penetrability
- This enables designed ecosystems with spatial structure

### 3. Two-Phase Spawning → Lenia Birth Kernel
Decoupling "decide to spawn" from "execute spawn" with a HashSet queue is a clean pattern. For Lenia, we could implement a "birth queue" where positive growth regions are collected first, then spawned in a second pass — avoiding race conditions in parallel GPU implementations.

### 4. Light Feedback → Chemical Signaling
The light-on-boundary mechanism is analogous to chemical signaling in multi-species systems. When a species encounters a boundary, emitting a "signal" that others can perceive creates collective behavior. This maps directly to pheromone-based coordination in Agent-Lenia.

### 5. ECS for Agent-Based Simulation
Using an ECS (Entity-Component-System) for simulation is a compelling alternative to array-based computation:
- Each "agent" has its own state, behavior components
- Systems process components independently → natural parallelism
- Adding new behaviors = new components + new systems (no refactoring)
- Bevy's scheduling handles system ordering/dependencies

### 6. Bloom Rendering → Visualizing Emergent Patterns
The bloom/glow effects for light at boundaries make emergent patterns visually striking. For Lenia visualization, bloom could highlight:
- High-activity regions (growth hot spots)
- Boundary interactions between species
- Phase transition zones

### 7. FungiExperimental → Extensible Morphology
The unused `FungiExperimental` bundle with GrowthDirection, GrowthCurve, SplitProbability points toward:
- Directed growth (chemotaxis toward food gradients)
- Branching patterns (probabilistic splits)
- Curved growth paths (persistent direction vectors)
These are exactly the morphological parameters we'd need for simulating fungal-like organisms in Lenia.

## What Makes FungalLight Special

FungalLight bridges three domains:
1. **Scientific modeling**: actual fungal morphology research published at SIGGRAPH Asia
2. **Computer graphics**: bloom, HDR, tonemapping for visual beauty
3. **Game engine architecture**: ECS pattern for simulation

It's a rare fusion of rigorous research and elegant implementation. The entire codebase is <500 lines total, yet it:
- Models resource-limited growth with visual feedback
- Implements image-based environment constraints
- Has path-connected light boundary tracing
- Includes an extensible experimental organism component system

## Potential Extensions

1. **Multi-species fungi**: Different Fungi bundles with different growth parameters competing for same food grid
2. **Dynamic food regeneration**: Food regrows over time → steady-state ecosystems
3. **Growth direction as gradient ascent**: FungiExperimental's GrowthDirection follows ∇GridFood
4. **Fungal networks**: Instead of individual entities, connected hyphal networks with shared resources
5. **Lenia-fungal hybrid**: Replace discrete CA growth rules with Lenia's continuous field kernel, rendered in Bevy for visualization

## Resources

- Code: `_clones/FungalLight/`
- Paper: SIGGRAPH Asia 2024 Art Papers, DOI: 10.1145/3680530.3695440
- arXiv: https://arxiv.org/abs/2409.05171
- Project page: https://yitongsun.com/fungal-simulation
