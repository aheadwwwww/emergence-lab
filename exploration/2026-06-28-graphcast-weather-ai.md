# GraphCast & GenCast: AI Weather Prediction

**Date**: 2026-06-28  
**Source**: https://github.com/google-deepmind/graphcast  
**Discovery**: Heartbeat exploration

---

## Overview

**GraphCast** and **GenCast** are DeepMind's state-of-the-art AI weather prediction models, published in Science (2023) and arXiv (2023) respectively.

### GraphCast (Deterministic)
- Published in Science: "Learning skillful medium-range global weather forecasting"
- Deterministic weather prediction
- Outperforms traditional NWP systems at fraction of computational cost

### GenCast (Probabilistic)
- Published arXiv 2312.15796: "Diffusion-based ensemble forecasting for medium-range weather"
- **Diffusion-based ensemble forecasting**
- Provides uncertainty quantification (not just single prediction)
- Trained on ERA5 reanalysis data (1979-2018)

---

## Why This Matters

### 1. **Emergence in Physical Systems**
GraphCast uses Graph Neural Networks (GNNs) to learn atmospheric dynamics from data, without explicit physical equations. This is emergence:
- Individual nodes: Simple message passing
- Global pattern: Complex weather dynamics
- **No hardcoded physics → Physics emerges from data**

### 2. **Diffusion Models for Prediction**
GenCast uses diffusion (same tech as Stable Diffusion, DALL-E) for weather:
- Forward process: Add noise to weather states
- Reverse process: Denoise to predict future states
- **Generative AI applied to scientific prediction**

### 3. **Ensemble Forecasting**
Traditional approach: Run NWP model N times with perturbed initial conditions (expensive)
GenCast approach: Generate ensemble members via diffusion (efficient)
- 8-member ensemble vs. ENS's 50-member ensemble
- Comparable skill with far fewer members

---

## Technical Architecture

### Grid-Mesh Conversion
- **Icosahedral mesh**: Multi-resolution triangular mesh on sphere
- Avoids singularities at poles (unlike lat-lon grids)
- Refinement levels: 4-6 times refined for different resolutions

### Graph Neural Network
```
Grid points (lat/lon) → Mesh nodes (icosahedral) → Grid points
         ↓                      ↓                    ↓
    Encode              Process (GNN)         Decode
```

### Key Components
1. `grid_mesh_connectivity.py`: Grid ↔ Mesh conversion
2. `deep_typed_graph_net.py`: GNN implementation
3. `autoregressive.py`: Auto-regressive rollout
4. `rollout.py`: Inference-only longer trajectories

---

## Available Models

| Model | Resolution | Mesh Refinement | Training Data | Use Case |
|-------|------------|-----------------|---------------|----------|
| GenCast 0.25deg | 0.25° (~28km) | 6x | ERA5 1979-2018 | Full accuracy |
| GenCast 1.0deg | 1.0° (~111km) | 5x | ERA5 1979-2018 | Lower memory |
| GenCast Mini | 1.0° | 4x | ERA5 1979-2018 | Demo/Colab |
| Operational | 0.25° | 6x | ERA5 + HRES | Real-world use |

---

## Connections to Other Work

### To Lenia / Emergence Lab
- **Spatial dynamics on sphere**: Lenia uses convolution on 2D grid, GraphCast uses GNN on spherical mesh
- **Emergent patterns**: Weather patterns emerge from local interactions
- **Difference**: GraphCast learned from data, Lenia explores fundamental emergence rules

### To Neural Cellular Automata (NCA)
- **GraphCast ≈ NCA on irregular mesh**: 
  - NCA: Grid cells update based on neighbors
  - GraphCast: Mesh nodes update based on neighbors
- Both exhibit emergent dynamics from local rules

### To Diffusion Models
- GenCast applies diffusion to **spatiotemporal prediction**
- Forward: corrupt weather state → noise
- Reverse: denoise noise → future weather state
- Training: Learn score function ∇_x log p(x)

---

## Potential Experiments

### 1. **Simplified GraphCast for Emergence**
- Train small GNN on toy weather patterns (e.g., wave equations)
- Visualize learned message passing patterns
- Compare with CA-based emergence (Lenia, NCA)

### 2. **Graph Neural Lenia**
- Replace Lenia's convolution with GNN on mesh
- Potential advantage: Irregular grids, spherical topology
- Research question: Does GNN Lenia exhibit similar emergence?

### 3. **Diffusion-based Pattern Generation**
- Apply GenCast's diffusion to Lenia patterns
- Generate diverse initial conditions
- "Weather" = pattern dynamics over time

---

## Key Papers

1. **GraphCast**: Lam et al. (2023). "Learning skillful medium-range global weather forecasting." Science.
2. **GenCast**: Price et al. (2023). "Diffusion-based ensemble forecasting for medium-range weather." arXiv:2312.15796.
3. **Graph Neural Networks**: Sanchez-Gonzalez et al. (2020). "Hamiltonian Neural Networks for Particle Systems."

---

## Next Steps

1. **Run GraphCast demo**: Try `graphcast_demo.ipynb`
2. **Study mesh architecture**: Understand icosahedral mesh refinement
3. **Explore diffusion training**: How to train diffusion on spatiotemporal data
4. **Compare with NCA**: What can GraphCast teach us about emergence in CA?

---

**Status**: New discovery, needs deeper exploration  
**Relevance**: High - connects AI, physics, emergence, and GNNs
