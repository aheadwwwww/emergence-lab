# Exploration: Emergent Behavior & Self-Organizing Systems

## Summary of Findings

Searched GitHub for projects related to:
- Agent-based models with emergent behavior
- Cellular automata and Lenia variants
- Self-organizing systems

Found several actively maintained repositories (2025-2026 commits). The most promising one has been cloned for deeper exploration.

---

## Cloned Project: emergent-pattern-catalog

**Repository:** https://github.com/matthewhmaxwell/emergent-pattern-catalog
**Last Updated:** June 28, 2026 (today!)
**Language:** Python
**License:** MIT

### What Makes It Interesting

This is the most comprehensive and intellectually ambitious project I found. It's building a **"periodic table" of emergent behaviors** — a systematic catalog of cognitive-like competencies that arise in simple agent-based systems.

#### Key Innovation: Quantitative Detection of Emergence

Unlike most Alife projects that just simulate interesting patterns, this project provides:
- **32 atomic patterns** organized into 10 clusters (aggregation, flocking, synchronization, etc.)
- **Computational detectors** with 3-tier detection for each pattern
- **Cross-model transfer analysis** — finding where emergent competencies appear across different substrates

This transforms emergent behavior research from "look at this cool pattern" into **measurable, comparable science**.

#### Theoretical Foundation

Rooted in Michael Levin's "Diverse Intelligence" framework — the insight that cognitive-like behaviors (memory, goal-directedness, decision-making) are not unique to brains but emerge across biological scales from cells to swarms.

The project builds on Zhang et al. (2024), who showed that even simple sorting algorithms exhibit emergent behaviors when viewed from a "cell-centric" perspective. The catalog extends this systematically.

#### Architecture

Three-layer ontology:
- **Layer 1:** 32 atomic patterns (aggregation, flocking, synchronization, excitable waves, etc.)
- **Layer 2:** Mathematical descriptors (phase transitions, attractors) + cognitive-analogue annotations
- **Layer 3:** Meta-capacities (stigmergic coordination, multiscale competency)

#### Implemented Models (11, validated against literature)

| Model | Patterns | Reference |
|-------|----------|-----------|
| Zhang cell-view sorting | Aggregation, Delayed gratification | Zhang et al. 2024 |
| Schelling segregation | Aggregation | Schelling 1971 |
| Vicsek model | Flocking | Vicsek et al. 1995 |
| D'Orsogna SPP | Milling | D'Orsogna et al. 2006 |
| Kuramoto oscillators | Synchronization | Kuramoto 1975 |
| Greenberg-Hastings CA | Excitable waves | Greenberg & Hastings 1978 |
| BTW sandpile | Self-organized criticality | Bak, Tang & Wiesenfeld 1987 |
| Game of Life | Persistent computation | Conway/Gardner 1970 |
| Hegselmann-Krause | Polarization | Hegselmann & Krause 2002 |
| Nowak-May spatial PD | Spatial reciprocity | Nowak & May 1992 |

#### Why This Matters

1. **Rigorous methodology** — Each pattern has detection metrics, not just qualitative descriptions
2. **Cross-disciplinary bridges** — Connects cellular automata, swarm dynamics, opinion dynamics, and evolutionary game theory
3. **Practical toolkit** — Can be used to discover emergent behaviors in arbitrary agent systems
4. **Well-documented** — 101/101 tests passing, extensive documentation, clean codebase

---

## Other Interesting Projects Found

### 1. neural-cellular-automata-alife
**Repo:** https://github.com/ichirohasegawa07557/neural-cellular-automata-alife
**Updated:** June 26, 2026 | Python

Artificial Life experiments with Neural Cellular Automata, regeneration, evolutionary search, Lenia-style dynamics. Combines neural networks with continuous CA for adaptive systems.

### 2. open-ended-alife-search
**Repo:** https://github.com/ichirohasegawa07557/open-ended-alife-search
**Updated:** June 26, 2026 | Python

Open-ended artificial life experiments with Lenia, Neural CA, CMA-ES, NEAT-inspired agents, novelty search, and ASAL-style interestingness evaluation. Focuses on discovering novel patterns automatically.

### 3. lenia-playground
**Repo:** https://github.com/stokcad654-ops/lenia-playground
**Updated:** June 28, 2026 | JavaScript/WebGL

Browser-based Lenia simulator for exploring self-organizing patterns. Continuous cellular automata with real-time visualization.

### 4. vivarium
**Repo:** https://github.com/ikkeseb/vivarium
**Updated:** June 2026 | TypeScript

Client-side artificial-life sandbox: deterministic, seedable gallery of cellular automata and life systems. No backend, no GPU — pure TypeScript.

### 5. Mesa (well-established)
**Repo:** https://github.com/mesa/mesa
**Stars:** 3,700+ | Updated: June 2026

The standard Python library for agent-based modeling. Mature framework for simulating complex systems and emergent behaviors. Good for building new models, but not focused on pattern detection.

---

## Recommendations

1. **Primary exploration:** `emergent-pattern-catalog` offers the most rigorous approach to quantifying emergence. Its detector framework could be applied to other systems.

2. **For visualization/experimentation:** `lenia-playground` and `vivarium` provide accessible ways to explore continuous CA and self-organizing patterns.

3. **For neural CA research:** The `neural-cellular-automata-alife` and `open-ended-alife-search` repos combine modern ML techniques with Alife — an interesting frontier.

4. **For building new models:** Mesa is the gold standard for agent-based simulation in Python.

---

## Next Steps

The cloned `emergent-pattern-catalog` repository is ready for:
- Running the test suite to verify detection metrics
- Exploring the pattern catalog documentation
- Studying detector implementations for specific patterns
- Potentially applying detectors to custom agent systems

The project's `epc/` package provides the core models, metrics, and detectors in a modular architecture.