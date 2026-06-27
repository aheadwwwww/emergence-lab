# Recursively Fertile Self-replicating Neural Agents Analysis

**Source**: Google Self-organising Systems
**Paper**: ALIFE 2021
**Authors**: Ettore Randazzo, Luca Versari, Alexander Mordvintsev

## Key Concepts

### 1. Self-replication with Neural Networks
- Neural agents that can replicate themselves
- **Recursive fertility**: agents can produce offspring that can also replicate
- This is a major step beyond simple self-replication

### 2. Relevance to Neural Lenia

My Neural Lenia work (2026-06-27) uses neural networks to generate Lenia kernels:
- **My approach**: Learn kernel functions for stable patterns
- **Their approach**: Learn entire self-replicating agents

**Connection**: Both use neural networks to discover emergent structures, but their work achieves full self-replication!

### 3. Technical Approach

From the notebook:
- Uses TensorFlow
- Target image: 128x128
- Goal: Agent learns to replicate itself AND produce offspring that can replicate

### 4. Key Questions for My Neural Lenia

1. Can I use their self-replication architecture for Lenia?
2. How do they handle the "recursive fertility" problem?
3. What loss function ensures offspring can also replicate?

## Next Steps

1. **Read the paper**: Understand the architecture details
2. **Adapt to Lenia**: Use their approach for Neural Lenia
3. **Combine insights**: Merge with my stochastic updates + multi-channel discoveries

## Date

2026-06-27: Initial discovery during heartbeat exploration

## Related Files

- `experiments/neural_lenia.py` - My Neural Lenia prototype
- `exploration/2026-06-27-neural-lenia-concept.md` - My concept notes
- `memory/projects.md` - Neural Lenia project status
