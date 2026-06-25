# Self-Replicating Neural Networks: A New Frontier

**Date**: 2026-06-25
**Source**: Google Self-Organising Systems (cloned to `experiments/self_org_systems/`)
**Paper**: "Recursively Fertile Self-replicating Neural Agents" (Randazzo, Versari, Mordvintsev, ALIFE 2021)

## What It Is
A neural network that can **copy itself** — weights, architecture, and all. The NN learns to output its own parameters, creating a recursive self-replication loop.

## Key Insight
This bridges two worlds:
1. **Artificial Life**: Self-replication is the holy grail of ALife (von Neumann's universal constructor)
2. **Deep Learning**: Neural networks as the substrate for self-replication

## Connection to Our Lenia Work

| Concept | Lenia | Self-Replicating NN |
|---------|-------|-------------------|
| Substrate | Continuous CA field | Neural network weights |
| Replication | Pattern stability across steps | Weight copying |
| Mutation | Parameter perturbation | Variation in copy |
| Selection | Survival (alive score) | Fitness on target task |
| Emergence | Local rules → global patterns | Learning → self-copy capability |

## Three Experiments
1. **Variable weights only**: NN learns to output all its weights
2. **Fixed + variable weights**: Some weights fixed, others learned → more stable
3. **Self-replication with variation**: NN copies itself with mutations → evolutionary dynamics

## Relevance to Our Work
- Our Lenia pheromone coupling creates **ecological niches** for different channels
- Self-replicating NNs create **evolutionary niches** through variation
- Both are about **emergent organization from local rules**

## Ideas to Explore
1. Can we train a small NN to predict Lenia channel survival?
2. Can self-replication dynamics inform our parameter search?
3. What if Lenia channels could "learn" to survive through weight adaptation?

## Files
- `experiments/self_org_systems/self_replicating_nn/recursively_fertile_self_replicating.ipynb`
- `experiments/self_org_systems/isotropic_nca/` — Isotropic Neural CA (related)
