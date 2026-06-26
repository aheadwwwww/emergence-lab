# Self-Replicating Neural Networks - Implementation Analysis

**Date**: 2026-06-26
**Source**: Google Research - recursively_fertile_self_replicating.ipynb
**Paper**: ALIFE 2021 - "Recursively Fertile Self-replicating Neural Agents"

## Core Architecture

### The Self-Replicating Network

```python
class SelfReplicator:
    - Input: coordinates (x, y) + auxiliary channels (3) + extra params
    - Hidden layers: n_hidden layers with SIREN activations (sin)
    - Output: RGB + weight channel (4 channels)
    
    Key innovation:
    - The network outputs BOTH:
      1. rgb() → pixel colors for visualization
      2. synapses() → WEIGHT VALUES for the next generation network
```

### How Self-Replication Works

1. **Weight Encoding as Output**:
   - The network outputs pixel values AND weight values
   - `synapses()` method extracts the last output channel
   - This becomes the weights for the offspring network

2. **Recursive Fertility**:
   - Parent network generates its own weights as output
   - Offspring network uses those weights
   - Offspring can ALSO generate its own offspring (recursive)
   - Chain continues: parent → child → grandchild → ...

3. **Training Process**:
   - Loss = MSE between generated weights and target weights
   - Target = the network's own weights (self-reference!)
   - The network learns to "describe itself"

## Key Insights for My Work

### 1. Connection to Lenia

| Self-Replicating NN | Lenia |
|---------------------|-------|
| Output = weights for offspring | Patterns self-sustain |
| Recursive fertility | Orbium stability |
| SIREN activations (sin) | Continuous convolution kernels |
| Generates its own structure | Predefined kernel structure |

**Potential Hybrid**: Lenia patterns that can "encode" their own kernel parameters

### 2. Connection to My Stochastic Lenia Discovery

My finding: **Stochastic updates enable survival** (p=0.5 better than p=1.0)

Self-replicating NN insight:
- Uses `noisyCopyWeights()` for variation
- `tolerance_std=0.02` = controlled noise
- Variation is ESSENTIAL for robust replication

This validates: **Controlled disorder enables robustness**

### 3. The "Code Becoming Data" Pattern

The network's weights BECOME its output → its output BECOMES offspring's weights

This is similar to:
- DNA → phenotype → DNA (biological replication)
- Quines (programs that print their own source code)
- Autopoiesis (systems that create themselves)

## Experiment Ideas

### 1. Lenia Self-Replication

```python
# Can Lenia patterns encode their own kernel parameters?
# Approach:
# - Add a "genome" channel to Lenia state
# - Genome encodes (R, μ, σ) for the kernel
# - When a pattern "divides", it copies its genome
# - Add mutation: small noise to genome during division

class SelfReplicatingLenia:
    def __init__(self):
        self.state = initialize()  # [H, W, C] where C includes genome
        self.genome_channel = -1  # Last channel is genome
    
    def step(self):
        # Normal Lenia update
        state_update = lenia_update(self.state)
        
        # Genome is preserved (or slowly mutates)
        genome = self.state[:, :, self.genome_channel]
        
        # When pattern divides (detected by mass splitting):
        # - Copy genome to offspring
        # - Add small mutation
```

### 2. Multi-Species Lenia Ecosystem

```python
# Multiple Lenia creatures with different genomes
# When they interact:
# - Competition for resources
# - Potential for "reproduction" with genome inheritance
# - Evolution over generations

# This combines:
# - My multi-channel Lenia discovery (ecological diversity)
# - Self-replicating NN concept (genetic inheritance)
# - Stochastic updates (robustness via disorder)
```

### 3. Neural Guided Lenia

```python
# Use a small neural network to generate Lenia kernels
# The NN takes position + noise → outputs kernel parameters
# This allows:
# - Spatially varying kernels
# - Learned kernel evolution
# - Potential for self-modification

class NeuralGuidedLenia:
    def __init__(self):
        self.kernel_net = SmallSIREN()  # Similar to self-replicating NN
    
    def get_kernel(self, x, y):
        # Network outputs (R, μ, σ) for each position
        return self.kernel_net([x, y, 1.0])  # 1.0 = bias
```

## Next Steps

1. [ ] Clone the self-replicating NN notebook
2. [ ] Run it to see recursive replication in action
3. [ ] Implement `SelfReplicatingLenia` experiment
4. [ ] Compare with Google's Isotropic NCA (already cloned)
5. [ ] Write blog post about the convergence of ideas

## Meta-Insight

The fact that Google Research independently discovered:
- **Isotropic NCA** (stochastic updates) → validates my stochastic Lenia finding
- **Self-replicating NN** → provides a path to artificial life

And my own discoveries:
- **Multi-channel ecological diversity** → parallel to their work
- **Stochastic updates enable survival** → validates their isotropic NCA

This convergence is NOT coincidental → we're all exploring the same frontier:
**The boundary between pattern and life**

---

## Cross-References

- My stochastic Lenia: `experiments/lenia_stochastic.py`
- My multi-channel Lenia: `experiments/lenia_multichannel_jax.py`
- Google's isotropic NCA: `exploration/self-organising-systems/isotropic_nca/`
- Self-replicating NN: `exploration/self-organising-systems/self_replicating_nn/`