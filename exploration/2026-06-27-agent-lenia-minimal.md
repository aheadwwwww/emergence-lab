# Minimal Agent-Based Lenia Experiment

**Date**: 2026-06-27
**Type**: Hybrid CA-Agent System
**Inspired by**: Biomaker CA architecture (Google Research)

---

## Concept

A minimal hybrid system combining:
1. **Lenia CA** - Continuous cellular automaton (field layer)
2. **Agent particles** - Mobile entities that can deposit/absorb energy

Key insight from Biomaker CA: **Parallel vs Exclusive operations**
- **Parallel ops**: All agents execute simultaneously (move, deposit energy)
- **Exclusive ops**: Competitive, requires arbitration (spawn, kill)

## Implementation

### Architecture
```
Field (Lenia CA) ←→ Agents (Mobile Particles)
       ↓                      ↓
   Energy flow            Energy flow
```

### Timeline per Step
1. **Parallel Phase**: All agents move and deposit/absorb energy
2. **Exclusive Phase**: Agents try to spawn (competition)
3. **CA Update**: Lenia field evolves
4. **Energy Exchange**: Agents absorb local field energy

### Energy Balance Problem (Solved!)

**Initial failure**:
- Field collapsed to 0.000
- Agents survived but the ecosystem died

**Root cause**: Agents draining field faster than Lenia could regenerate

**Solution**:
- Start field with higher energy (0.5-0.8 instead of 0.3)
- Reduce absorption rate (0.02 cap instead of 0.05)
- Agents give back when energy > 1.5
- Balance deposit/absorb ratios

**Result**: Equilibrium reached at field mean ~0.17, agents stable

## Key Findings

### 1. Self-Regulation Emerges
When agents have too much energy → they deposit back to field
When field is low → agents absorb less

This creates a **negative feedback loop** that stabilizes the system.

### 2. Lenia as "Environment"
Lenia's pattern-forming dynamics create spatial heterogeneity:
- Some regions are energy-rich (stable patterns)
- Some regions are energy-poor (voids)
- Agents must navigate this landscape

### 3. Agent Density Matters
With 10 initial agents on 64x64 grid:
- Balanced ecosystem
- 2 successful spawns (20% reproduction rate)
- No mass extinction

## Parameters

| Parameter | Value | Effect |
|-----------|-------|--------|
| Grid size | 64x64 | Spatial scale |
| Agents | 10 initial | Population density |
| Field init | 0.5-0.8 | Starting energy |
| Absorb cap | 0.02 | Prevents over-harvesting |
| Deposit threshold | 1.5 | Give back when wealthy |
| Spawn cost | 1.0 | Energy required to reproduce |

## Next Steps

1. **Add agent sensing**: Agents detect field gradients and move towards high-energy regions
2. **Kernel mutation**: Offspring inherit modified Lenia kernels (evolution!)
3. **Multiple agent types**: Herbivores (absorb field) vs Carnivores (eat agents)
4. **Spatial resources**: Add non-uniform energy sources

## Code

`experiments/agent_lenia_minimal.py`

## Related

- `exploration/2026-06-27-biomakerca-architecture.md` - Biomaker CA analysis
- `curiosity-lenia/` - Previous Lenia experiments
- `curiosity-artificial-life/` - ALife projects

---

## Questions

- Can agents evolve to "farm" Lenia patterns? (Create stable energy sources)
- What's the critical agent density for ecosystem collapse?
- Can we observe predator-prey cycles if agents eat each other?