# Minimal Emergence: Key Finding

**Date**: 2026-06-23
**Source**: `experiments/minimal_emergence/`

## The Question

Can a minimal rule system (≤3 states, ≤1bit memory, ≤5 rules) produce
**open-ended evolution** — i.e. continuously generate novel structures?

## Experiments

### 1. Basic Universe (3 states, 1bit memory)
- State space: 6 (3 states × 2 memory)
- Default rules: A→B→C→A cycle (length 3, non-open)
- Random rules: avg cycle ~1.9, max cycle 6
- **Verdict**: Always periodic, never open-ended.

### 2. Scaled Parameters

| Variant | State Space | Max Cycle | Open-Ended? |
|---------|-------------|-----------|-------------|
| Baseline (3 states, 1bit) | 6 | 6 | No |
| +Memory (4bit) | 48 | 22 | No |
| +States (8) | 16 | 12 | No |
| +Feedback | 48 | 18 | No |
| +Evolution | Dynamic | - | No |
| **+Self-Expansion** | **1→∞** | **∞** | **Yes** |

### 3. Self-Expanding Systems (The Breakthrough)
- Tree-structured self-expansion: 1 → 21+ unique states
- Recursive rules create new states on-the-fly
- **Only system that achieved open-endedness**

### 4. Meta-Evolution
- Self-modifying rules that can mutate themselves
- Tested 50 runs: **0/50** produced novel patterns
- Self-modification alone is insufficient without space expansion

## Core Insight

**Finite state space → Finite cycles → No emergence.**
**Self-expanding state space → Infinite dynamics → Emergence.**

Rules constrain behavior in a fixed space. True open-ended evolution
requires the system to expand its own state space — reminiscent of
autocatalytic sets, Gödelian self-reference, and the concept of
"metastable" dynamical systems.

## Implications

1. **Artificial Life**: Open-ended evolution needs self-space-expanding
   architectures, not just larger fixed state spaces.
2. **Minimal models**: The transition from "complex periodic" to "open"
   happens at the self-expansion threshold, not at a complexity threshold.
3. **Connection to**: Gödel-Löb modal logic, Chaitin's Ω, and the
   concept of "creative" systems that must be able to redefine their
   own rule space.
