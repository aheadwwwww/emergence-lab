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

**Status**: V9 experiment running, awaiting results
