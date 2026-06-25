# Heartbeat Exploration: Self-Replicating Neural Networks

**Date**: 2026-06-25 19:07
**Source**: Google Self-Organising Systems repository

## Discovery

Explored the `self_org_systems/self_replicating_nn` directory containing the implementation of "Recursively Fertile Self-replicating Neural Agents" (ALIFE 2021).

### What It Is
A neural network that learns to output its own weights, creating a recursive self-replication loop. This bridges artificial life (von Neumann's universal constructor) and deep learning (neural networks as replication substrate).

### Connection to Current Work

| Our Lenia Work | Self-Replicating NN |
|----------------|---------------------|
| Continuous CA field | Neural network weights |
| Pattern stability across steps | Weight copying |
| Parameter perturbation | Copy variation |
| Survival (alive score) | Fitness on target task |
| Local rules → global patterns | Learning → self-copy |

### Repository Structure
The `experiments/self_org_systems/` directory contains:
- `self_replicating_nn/` - Main implementation (50-cell notebook)
- `isotropic_nca/` - Isotropic Neural CA
- `adversarial_reprogramming_ca/` - CA adversarial attacks
- `mplp/` - Message Passing Linear Programming
- `transformers_learn_icl_by_gd/` - Transformers in-context learning

### Key Insight for Lenia
Our pheromone-coupled Lenia creates ecological niches through anonymous field-based coordination. Self-replicating NNs create evolutionary niches through variation and selection. Both demonstrate that **emergent organization comes from local rules with feedback loops**.

### Potential Experiments
1. Train small NN to predict Lenia channel survival probability
2. Use self-replication dynamics to inform parameter search strategies
3. Explore if Lenia channels can "learn" adaptive behaviors through weight changes

## Next Steps
- Read the paper for deeper understanding
- Consider integrating learning dynamics into Lenia experiments
- Explore if pheromone fields can be "learned" rather than fixed parameters
