# Self-Replicating Neural Networks: Deep Dive

**Date**: 2026-06-27 20:35
**Source**: Google Research - self-organising-systems
**Paper**: "Recursively Fertile Self-replicating Neural Agents" (ALIFE 2021)

---

## Core Concept

A neural network that outputs its own weights.

### Architecture

```
Input: (x, y, aux) coordinates
  ↓
Hidden layers (sin activations)
  ↓
Output: [RGB, weight_scalar]
```

**Key insight**: The network has TWO output modes:
1. **Image mode**: Given (x,y) coordinates → outputs RGB pixel
2. **Weight mode**: Given weight coordinate → outputs weight value

This enables **recursive self-replication**:
- Network generates an image
- Network generates its own weights
- Noisy copy = mutation
- Offspring can replicate again

---

## Technical Details

### 1. Coordinate Encoding

Weights are indexed by binary coordinates:
- Layer index
- Row index
- Column index

Example: `W[layer][row][col]` → binary encoding → network input

### 2. Sinusoidal Activations

From SIREN paper (Sitzmann et al.):
- `sin(x)` activation enables periodic functions
- Better for encoding spatial patterns
- First layer scaled by `wo` (omega_0)

### 3. Self-Replication Process

```python
# Generate new weights
for each weight coordinate:
    new_weight = network(weight_coordinate)[-1]  # Last output channel

# Add noise (mutation)
new_weights = old_weights + noise * std(old_weights) * tolerance
```

### 4. Recursive Fertility

**Definition**: An agent is "fertile" if its offspring can also reproduce.

**Achievement**: The paper shows networks can be trained to be recursively fertile for many generations.

---

## JAX Implementation

Created `experiments/self_replicating_nn_jax.py`:

```python
class SelfReplicatorJAX:
    def __init__(self, n_hidden=4, size_hidden=64):
        # Initialize network
        self.params = self._init_params()
        
    def __call__(self, inputs):
        # Forward pass with sin activations
        x = inputs
        for layer in self.params:
            x = x @ W + b
            x = sin(x)  # Except last layer
        return x  # [RGB, weight]
    
    def generate_image(self, height, width):
        # Create coordinate grid
        # Forward pass
        # Return RGB
        
    def noisy_copy(self, params, noise_std=0.02):
        # Add noise proportional to weight std
        # Return new params
```

**Test results**:
- Successfully generates images
- Self-replication creates variation
- 5 generations tested

---

## Applications to Our Work

### 1. Neural Lenia Integration

**Current Neural Lenia**: Fixed architecture, learns kernel shape
**Self-Replicating NN**: Network IS the genome

**Idea**: Combine both!
- Neural Lenia learns Lenia kernel
- Self-replicating NN learns to reproduce itself
- Result: Self-replicating Lenia species

### 2. Biomaker CA Ecosystems

Biomaker CA uses:
- DNA library (genome)
- Environment logic
- Agent logic
- Mutation

Self-replicating NN can replace DNA:
- Network weights = genome
- Noisy copy = mutation
- Forward pass = behavior

### 3. Emergence-Lab Integration

Add to `emergence-lab`:
```python
class SelfReplicatingModel:
    """Self-replicating neural agent."""
    def __init__(self, genome=None):
        self.network = SelfReplicatorJAX()
        if genome:
            self.network.set_weights(genome)
            
    def replicate(self, mutation_rate=0.02):
        """Create offspring with mutation."""
        offspring_genome = self.network.noisy_copy(
            self.network.params, 
            noise_std=mutation_rate
        )
        return SelfReplicatingModel(genome=offspring_genome)
```

---

## Key Insights

### 1. Weights as Genome

Traditional: Weights are parameters to optimize
Self-replicating: Weights are the organism itself

This is a **paradigm shift**:
- No external optimizer needed
- Evolution IS the optimization
- Fitness = reproductive success

### 2. Recursive Fertility

The paper proves networks can be:
- Trained to reproduce target images
- AND reproduce their own weights
- AND offspring can do the same

This is **true self-replication**, not just copying.

### 3. Mutation as Variation

Noisy copying creates diversity:
- `new = old + noise * std(old) * tolerance`
- Proportional to weight magnitude
- Preserves structure while allowing variation

### 4. Sin Activations

Why `sin(x)`?
- Periodic → can encode repeating patterns
- Bounded → stable training
- Differentiable → gradient-based optimization
- Universal approximation → can learn any function

---

## Comparison with Other Approaches

| Approach | Genome | Replication | Evolution |
|----------|--------|-------------|-----------|
| **Self-replicating NN** | Network weights | Network outputs weights | Noisy copy |
| **Neural Lenia** | Kernel params | External | Gradient descent |
| **Biomaker CA** | DNA array | Explicit copy | Mutation operators |
| **NCA** | Network weights | None (fixed) | Gradient descent |

Self-replicating NN is the **most elegant**:
- Genome = weights (no separate representation)
- Replication = forward pass (no external mechanism)
- Evolution = noise (no mutation operators)

---

## Next Steps

### Immediate

1. **Train to reproduce Orbium**
   - Use Orbium pattern as target image
   - Train network with gradient descent
   - Test self-replication quality

2. **Multi-generation experiment**
   - Start with trained network
   - Replicate for 10+ generations
   - Measure image quality decay
   - Find stable "species"

3. **Integrate with Lenia**
   - Use self-replicating NN as Lenia kernel
   - Test if it creates stable patterns
   - Compare with fixed kernels

### Medium-term

4. **Ecosystem simulation**
   - Multiple species (different trained networks)
   - Interaction rules
   - Competition/cooperation
   - Measure diversity

5. **Fitness landscape**
   - Train networks for different targets
   - Map weight space
   - Find basins of attraction
   - Identify "stable species"

### Long-term

6. **Recursive fertility threshold**
   - How many generations can networks replicate?
   - What determines stability?
   - Can we evolve more fertile networks?

7. **Open-ended evolution**
   - No target image
   - Fitness = reproductive success
   - What patterns emerge?

---

## Code Structure

```
experiments/
├── self_replicating_nn_jax.py  # JAX implementation
├── neural_lenia.py             # Neural Lenia (existing)
└── lenia_jax.py                # Lenia (existing)

exploration/
├── 2026-06-27-google-sos-latest.md
└── 2026-06-27-self-replicating-nn-deep-dive.md  # This file
```

---

## References

1. **Paper**: Randazzo et al. "Recursively Fertile Self-replicating Neural Agents" (ALIFE 2021)
2. **Code**: https://github.com/google-research/self-organising-systems
3. **SIREN**: Sitzmann et al. "Implicit Neural Representations with Periodic Activation Functions"
4. **Related**: Biomaker CA, Isotropic NCA, Neural Lenia

---

## Impact Assessment

**Relevance to our work**: ⭐⭐⭐⭐⭐ (5/5)

This directly addresses our core questions:
- How can patterns self-replicate? ✓
- How can species emerge? ✓
- How can evolution occur without external optimization? ✓
- How can we create open-ended systems? ✓

**Integration potential**: High
- Can replace Neural Lenia's fixed architecture
- Can add to emergence-lab as new model
- Can inspire ecosystem experiments

**Novelty**: High
- Weights-as-genome is a paradigm shift
- Recursive fertility is a new concept
- Sin activations for self-replication is elegant

---

**Conclusion**: Self-replicating neural networks are a breakthrough for artificial life research. They provide a minimal, elegant mechanism for self-replication that can be integrated into our existing frameworks. The next step is to train networks to reproduce Lenia patterns and test multi-generation stability.