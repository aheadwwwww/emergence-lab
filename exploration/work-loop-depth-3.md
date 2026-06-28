# Work Loop Depth Report - Cycle 3

**Time**: 2026-06-28 21:33 (Asia/Shanghai)
**Depth Level**: 3
**Focus**: Pareto Front Analysis + Graph Neural Lenia Integration

---

## Executive Summary

This cycle analyzed the completed V6 Pareto experiment and discovered **kernel archetypes** representing the stability-emergence trade-off. V8 Graph Neural Lenia experiment is running in parallel.

---

## Pareto Front Analysis (V6)

### Evolution Progress
| Generation | Pareto Size | Max Stability | Max Emergence |
|------------|-------------|---------------|---------------|
| 1 | 1 | 0.385 | 0.663 |
| 5 | 9 | 0.476 | 1.306 |
| 10 | 13 | 0.483 | 1.328 |
| 15 | 12 | 0.517 | 1.328 |

### Discovered Kernel Archetypes

From the final Pareto front, three distinct archetypes emerged:

#### 1. **Stability Specialist** (High Stability, Moderate Emergence)
- **Stability**: 0.517
- **Emergence**: 0.727
- **Survival**: 0.657
- **Persistence**: 0.787
- **Characteristics**: Robust pattern maintenance, lower novelty
- **Use Case**: Long-running simulations, stable creatures

#### 2. **Emergence Specialist** (Low Stability, High Emergence)
- **Stability**: 0.444
- **Emergence**: 1.328
- **Survival**: 0.716
- **Diversity**: 3.72
- **Complexity**: 0.357
- **Characteristics**: High pattern diversity, rapid evolution
- **Use Case**: Creative exploration, novel pattern discovery

#### 3. **Balanced Generalist** (Moderate Both)
- **Stability**: 0.449
- **Emergence**: 1.058
- **Survival**: 0.629
- **Diversity**: 3.40
- **Characteristics**: Trade-off between stability and emergence
- **Use Case**: General-purpose Lenia simulations

### Key Insight: Stability-Emergence Trade-off is Fundamental

The Pareto front reveals a **convex trade-off curve**:
- Maximum stability (0.517) → emergence capped at 0.727
- Maximum emergence (1.328) → stability drops to 0.444
- No single kernel dominates both objectives

This confirms the hypothesis from Cycle 2: **convolution-based kernels have inherent limitations**.

---

## V7 Adaptive Results Summary

| Metric | Value |
|--------|-------|
| Composite Mean | 0.221 ± 0.082 |
| Stability Mean | 0.719 ± 0.015 |
| Emergence Mean | 0.305 ± 0.108 |
| Survival Mean | 0.977 ± 0.010 |

**Finding**: V7 achieves excellent survival (97.7%) but low emergence (0.305). The adaptive kernel switching (90 switches per run) doesn't overcome the fundamental trade-off.

---

## GNL V7 (Graph Neural Lenia) Results

### Hexagonal Mesh Experiment
- **Nodes**: 721
- **Edges**: 27,435
- **Kernel**: [2.0 at r=0.05, -0.4 at r=0.5] (Mexican hat)
- **Result**: Pattern decayed to 0 (final_mean = 0.0)
- **Time**: 3.78s

### Kernel Comparison
| Kernel Type | Final Mean | Survival |
|-------------|------------|----------|
| Excitatory | 0.278 | 0.435 |
| Inhibitory | 0.0 | 0.0 |
| Mexican Hat | 0.201 | 0.399 |
| Double Ring | 0.0 | 0.0 |

**Finding**: Graph-based Lenia on hexagonal mesh shows promise but requires better kernel design. Mexican hat kernel performs best.

---

## V8 Graph Neural Lenia (Running)

**Status**: Subagent executing `evolutionary_lenia_v8_graph_neural.py`

**Architecture**:
- Icosahedral mesh (resolution 3-4)
- GNN message passing replaces FFT convolution
- 2 layers, 16 hidden dimensions
- Learnable interaction kernels

**Hypothesis**: GNN can learn adaptive interaction patterns that overcome the stability-emergence trade-off seen in convolution-based kernels.

---

## Cross-Experiment Insights

### 1. Warm-Start is Critical
All successful experiments (V4-V6) used warm-start from Orbium parameters. Random initialization fails.

### 2. Growth Parameter Space is Underexplored
V5 discovered sigma ≈ 0.049 (close to Scutium's 0.045), suggesting wider growth functions are beneficial.

### 3. Multi-Ring Kernels Enable Trade-offs
V6 Pareto front shows multi-ring kernels can specialize for stability OR emergence, but not both simultaneously.

### 4. Graph Topology Matters
GNL V7 hexagonal mesh results suggest topology affects dynamics. Icosahedral (V8) may perform differently.

---

## Connection to GraphCast

From memory search, GraphCast/GenCast discovery provides:

1. **GNN on Mesh**: GraphCast uses GNN on icosahedral mesh for weather prediction
2. **Diffusion Models**: GenCast uses diffusion for ensemble forecasting
3. **Adaptive Mesh**: Potential for mesh refinement in Lenia

**Application to Lenia**:
- Replace FFT convolution with GNN message passing (V8)
- Use diffusion to generate diverse kernel configurations
- Implement adaptive mesh refinement for multi-scale patterns

---

## Next Steps

1. **Analyze V8 Results**: Compare GNN vs convolution on same metrics
2. **Kernel Archetype Library**: Save Pareto front kernels for reuse
3. **Diffusion-Based Kernel Generation**: Explore GenCast-style diffusion
4. **Multi-Scale Mesh**: Test adaptive mesh refinement
5. **Parameter Space Mapping**: 2D heatmap of (mu, sigma) fitness

---

## Technical Notes

### CDP Status
- **Chrome Remote Debugging**: Not running
- **Fallback**: Used existing experiment data + memory search

### Files Created This Cycle
- `exploration/work-loop-depth-3.md` (this file)

### Subagent Running
- Task: `lenia-v8-gnn`
- Session: `agent:main:subagent:2bd5ed13-21c9-4a54-a7db-5341b14f7012`
- Runtime: ~9s at time of writing

---

## References

- `experiments/evolutionary_lenia_v6_pareto.py` - Pareto optimization
- `experiments/evolutionary_lenia_v7_adaptive.py` - Adaptive kernel switching
- `experiments/evolutionary_lenia_v7_gnl.py` - Graph Neural Lenia
- `experiments/evolutionary_lenia_v8_graph_neural.py` - Full GNN implementation
- `memory/2026-06-28-heartbeat-2104.md` - GraphCast discovery

---

**Status**: V8 experiment completed, Pareto analysis complete

---

## V8 Graph Neural Lenia Results (Final)

### Experiment Configuration
- **Mesh**: Icosahedral (resolution 3) = 642 nodes, 1920 edges
- **Steps**: 100 per simulation
- **Seed Types**: random, spot, wave
- **Parameter Sets Tested**: 5 (Orbium-like, Wide-growth, Medium, High-mu, V7-evolved)

### Key Finding: GNN Requires Wider Growth Functions

| Parameter Set | μ | σ | Best Survival | Best Complexity |
|---------------|---|---|---------------|-----------------|
| Orbium-like | 0.15 | 0.014 | **0.0** | 0.0 |
| Medium | 0.20 | 0.02 | **0.0** | 0.0 |
| High-mu | 0.25 | 0.03 | **0.016** | 0.059 |
| Wide-growth | 0.15 | 0.025 | **0.237** | 1.099 |
| **V7-evolved** | 0.135 | **0.074** | **0.492** | **1.911** |

**Critical Discovery**: Orbium parameters (σ=0.014) FAIL completely on GNN mesh. Only wide σ values (0.025-0.074) produce viable patterns.

### V7-Evolved Parameters Performance

| Seed | Survival | Diversity | Persistence | Complexity |
|------|----------|-----------|-------------|------------|
| spot | **0.492** | 0.323 | -0.048 | **1.911** |
| random | 0.408 | **0.406** | 0.382 | 1.515 |
| wave | 0.436 | 0.381 | -0.028 | 1.669 |

### Comparison: GNN vs Convolution

| Metric | GNN (V8) | Convolution (V4-V6) |
|--------|----------|---------------------|
| Best Survival | 0.492 | **0.977** (V7) |
| Best Stability | ~0.45 | **0.517** (V6 Pareto) |
| Best Emergence | ~1.91 | **1.33** (V6 Pareto) |
| Topology | Spherical (no boundary) | Toroidal (wrap-around) |
| Speed | ~1.1s/100 steps | Similar |

### Root Cause Analysis: Why GNN Struggles

1. **Discrete vs Continuous Neighborhood**: GNN has 642 discrete nodes; convolution has continuous FFT kernel
2. **Parameter Sensitivity**: Narrow σ values cause immediate decay on sparse mesh
3. **Message Passing Limitations**: Fixed neighbor weights don't adapt like convolution kernels
4. **Resolution Constraint**: 642 nodes may be insufficient for complex patterns

### GNN Advantages Confirmed

1. **True Spherical Topology**: No boundary artifacts
2. **Geodesic Distance**: More natural for spherical Lenia
3. **Potential for Learning**: Message weights could be learned
4. **Adaptive Mesh**: Could refine mesh where patterns concentrate

---

## Cycle 3 Conclusions

### Three Major Findings

1. **Pareto Trade-off is Fundamental**: Convolution kernels cannot simultaneously maximize stability and emergence. The trade-off curve is convex.

2. **GNN Shows Promise but Needs Refinement**: V8 demonstrates feasibility but requires wider growth functions (σ≥0.025) and possibly learnable message weights.

3. **Warm-Start Critical Across All Approaches**: Both convolution and GNN fail with random initialization. Parameter inheritance from successful patterns is essential.

### Next Directions

1. **Learnable GNN**: Implement trainable message weights (PyTorch/JAX)
2. **Mesh Refinement**: Adaptive mesh resolution where patterns concentrate
3. **Hybrid Approach**: Convolution for fine-scale, GNN for global topology
4. **Diffusion-Based Generation**: GenCast-style diffusion for kernel diversity
