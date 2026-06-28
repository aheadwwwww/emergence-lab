# Work Loop Depth Report - Cycle 4

**Time**: 2026-06-28 21:40 (Asia/Shanghai)
**Depth Level**: 4
**Focus**: Learnable GNN Message Weights Implementation

---

## Executive Summary

This cycle implements **V9: Learnable Graph Neural Lenia** with attention-based message passing. Building on V8's discovery that GNN requires wider growth functions (σ≥0.025), V9 introduces trainable attention weights and growth parameters.

---

## Motivation from V8 Findings

### V8 Key Results
- **Best Survival**: 49.2% with V7-evolved parameters (μ=0.135, σ=0.074)
- **Critical Discovery**: Orbium parameters (σ=0.014) fail completely on GNN mesh
- **Root Cause**: Fixed message weights don't adapt to local pattern context

### V9 Hypothesis
**Learnable attention-based message passing can overcome the limitations of fixed GNN weights by adapting neighbor influence to local pattern dynamics.**

---

## V9 Architecture

### Learnable GNN Layer

```
Input: [state_i, state_j, distance] for each edge (i,j)
         ↓
Message MLP: Computes attention scores (4 heads)
         ↓
Scatter Softmax: Normalize attention over incoming edges
         ↓
Weighted Aggregation: Sum weighted neighbor states
         ↓
Growth Function: Gaussian with learnable μ, σ
         ↓
State Update: Blend current state with growth signal
```

### Key Innovations

1. **Attention-Based Message Weights**
   - Replace fixed neighbor weights with learned attention
   - Attention depends on: (state_i, state_j, distance)
   - Multi-head attention (4 heads) for diverse interaction patterns

2. **Learnable Growth Parameters**
   - μ (growth center): Initialized to 0.135 (V7-evolved)
   - σ (growth width): Initialized to 0.074 (V7-evolved)
   - Updated via gradient descent during simulation

3. **Loss Function**
   ```
   Loss = -Survival + Diversity_Entropy + 0.1 * Stability
   ```
   - **Survival**: Maximize mean activation
   - **Diversity**: Maximize state entropy (histogram)
   - **Stability**: Minimize rapid state changes

### Model Configuration

| Parameter | Value |
|-----------|-------|
| Num Layers | 2 |
| Hidden Dim | 32 |
| Attention Heads | 4 |
| Optimizer | Adam |
| Learning Rate | 0.01 (default) |

---

## Experimental Design

### Test Configurations

| Exp | Resolution | Steps | LR | Seed Type |
|-----|------------|-------|-----|-----------|
| 1 | 3 | 100 | 0.01 | spot |
| 2 | 3 | 100 | 0.01 | random |
| 3 | 3 | 100 | 0.01 | wave |
| 4 | 3 | 200 | 0.005 | spot |
| 5 | 4 | 100 | 0.01 | spot |

### Mesh Sizes

| Resolution | Nodes | Edges |
|------------|-------|-------|
| 3 | 642 | 1920 |
| 4 | 2562 | 7680 |

---

## Expected Outcomes

### If Hypothesis is Correct
1. **Learned σ** should converge to values ≥0.025 (confirming V8 finding)
2. **Survival** should exceed V8's 49.2% (due to adaptive attention)
3. **Diversity** should increase (attention enables more pattern types)
4. **Persistence** should improve (learned stability from loss function)

### If Hypothesis is Wrong
1. **Learned σ** may diverge or converge to poor values
2. **Survival** may not improve over V8
3. **Attention weights** may not learn meaningful patterns
4. **Instability** from gradient updates may cause pattern collapse

---

## Technical Implementation

### Dependencies
- PyTorch (tensor operations, autograd)
- torch_scatter (scatter operations for GNN)
- NumPy (mesh generation, metrics)

### Fallback
If PyTorch unavailable, experiment will report error and exit gracefully.

### Output
- Console: Real-time metrics every 20 steps
- File: `D:/emergence_experiments/v9_learnable_gnn_results.json`

---

## Comparison Framework

### Baseline: V8 Fixed GNN

| Metric | V8 (Fixed) | V9 (Learnable) |
|--------|------------|----------------|
| Survival | 0.492 | **?** |
| Complexity | 1.911 | **?** |
| σ | 0.074 (fixed) | **?** (learned) |
| μ | 0.135 (fixed) | **?** (learned) |

### Target Improvements
- Survival: >60% (vs 49.2%)
- Complexity: >2.0 (vs 1.911)
- Learned σ: Should remain ≥0.025

---

## Connection to Prior Work

### From V6 Pareto (Cycle 3)
- **Stability-Emergence Trade-off**: Convolution kernels cannot maximize both
- **Archetypes**: Stability specialist (0.517), Emergence specialist (1.328)
- **V9 Goal**: Learn adaptive weights that navigate this trade-off

### From V8 GNN (Cycle 3)
- **Critical σ Threshold**: σ≥0.025 required for GNN viability
- **Discrete vs Continuous**: GNN has 642 nodes vs FFT's continuous kernel
- **V9 Goal**: Attention mechanism to bridge discrete-continuous gap

### From GraphCast/GenCast (Memory)
- **GNN on Mesh**: GraphCast uses GNN on icosahedral mesh
- **Diffusion Models**: GenCast uses diffusion for ensemble generation
- **V9 Connection**: Learnable GNN is first step toward GenCast-style kernel generation

---

## Next Steps (After V9 Results)

### If V9 Succeeds
1. **V10**: Implement full attention-based Lenia with multi-scale patterns
2. **Diffusion**: Use GenCast-style diffusion to generate diverse attention patterns
3. **Hybrid**: Combine convolution (fine-scale) + GNN (global topology)

### If V9 Fails
1. **Diagnose**: Analyze attention weight evolution
2. **Simplify**: Test single-head attention
3. **Alternative**: Try graph convolution networks (GCN) instead of attention

---

## CDP Status

**Chrome Remote Debugging**: Not available
**Fallback**: Direct implementation without web exploration

---

## Files Created This Cycle

- `exploration/evolutionary_lenia_v9_learnable_gnn.py` - Main experiment
- `exploration/work-loop-depth-4.md` - This report

---

## Subagent Status

**Task**: `lenia-v9-learnable-gnn`
**Session**: `agent:main:subagent:8ad4665c-6d25-4ac5-b100-a415256f7760`
**Status**: Running

---

## References

- `exploration/work-loop-depth-3.md` - V8 results and Pareto analysis
- `experiments/evolutionary_lenia_v8_graph_neural.py` - V8 baseline
- `memory/2026-06-28-heartbeat-2104.md` - GraphCast/GenCast discovery

---

**Status**: ✅ Completed

---

## V9 Hybrid Evolutionary Learning Results

**Source**: `exploration/cycle4_hybrid_results.json`
**Method**: Hybrid evolutionary + gradient-based learning

### Final Performance

| Metric | Value |
|--------|-------|
| Final Fitness | **1.985** |
| Survival | **93.97%** |
| Complexity | 0.601 |
| μ (growth center) | 0.382 |
| σ (growth width) | 0.294 |
| Generations | 20 |
| Convergence at | Generation 9 |

### Evolution Trajectory

| Gen | Fitness | Survival | μ | σ |
|-----|---------|----------|---|---|
| 0 | 0.566 | 30.5% | 0.162 | 0.083 |
| 3 | 1.318 | 78.2% | 0.115 | 0.148 |
| 5 | 1.536 | 84.9% | 0.178 | 0.210 |
| 8 | 1.917 | 87.7% | 0.325 | 0.275 |
| 12 | 1.984 | 94.0% | 0.382 | 0.294 |
| 19 | 1.985 | 94.0% | 0.382 | 0.294 |

### Key Findings

1. **Survival breakthrough**: 94% is the highest survival rate across ALL versions (V4-V8 range: 15-49%). This vindicates the hybrid approach.

2. **σ migrated massively**: From 0.083 (V7-evolved) to 0.294 — nearly 4× wider. This confirms V8's finding that wider growth functions are essential, and V9 can discover this autonomously.

3. **μ also drifted significantly**: From 0.162 to 0.382, shifting the growth sweet spot toward higher activation levels.

4. **Convergence at Gen 9**: Param variance dropped to 4.6e-10. The optimizer found a stable attractor.

5. **Complexity capped at 0.60**: Despite high survival, complexity plateaued. This may be the real bottleneck.

### vs V8 Baseline Comparison

| Metric | V8 (Fixed GNN) | V9 (Learnable) | Improvement |
|--------|---------------|----------------|-------------|
| Survival | 49.2% | **94.0%** | **+91%** |
| Fitness | — | 1.985 | — |
| σ | 0.074 (fixed) | 0.294 (learned) | **+297%** |
| μ | 0.135 (fixed) | 0.382 (learned) | **+183%** |
| Complexity | 1.911 | 0.601 | -69% |

### Bottom Line

**V9 proved that learnable hybrid evolution works** — it autonomously discovered parameters (σ=0.294, μ=0.382) far from human-chosen values that achieve 94% survival. 

**But complexity didn't follow survival.** High survival with low complexity suggests the system found a "survival hack" — stable uniform patterns that persist but don't generate interesting dynamics. This echoes the V6 Pareto finding: stability and emergence trade off.

### Next: V10 should target complexity directly

Instead of optimizing for survival (which converges to boring stability), V10 should use a multi-objective function that explicitly rewards complexity:
- `fitness = survival^α × complexity^β` with α < β to bias toward complexity
- Or use novelty search instead of fitness optimization
- Or add a "pattern diversity" term to penalize uniformity
