# Cognee — Open-Source AI Memory Platform

**Source**: GitHub trending, 2026-06-29
**Repo**: topoteretes/cognee (24,737 ⭐)
**Paper**: [Optimizing the Interface Between Knowledge Graphs and LLMs for Complex Reasoning](https://arxiv.org/abs/2505.24478)

## What It Is

Open-source AI memory platform that gives agents persistent long-term memory via a self-hosted knowledge graph engine. Combines vector embeddings, graph reasoning, and cognitive-science-grounded ontology generation.

## Core API (Four Operations)

```python
await cognee.remember("Cognee turns documents into AI memory.")
results = await cognee.recall("What does Cognee do?")
await cognee.forget(dataset="main_dataset")
await cognee.improve()  # refine graph structure
```

## Architecture

- **Ingestion pipeline**: Any format → chunks → embeddings + graph nodes/edges
- **Dual search**: Vector similarity + graph traversal, auto-routing
- **Session memory**: Fast cache that syncs to permanent graph in background
- **Ontology grounding**: Cognitive-science-based graph schema generation
- **Multimodal**: Text, images, audio

## Relevance to Our Work

1. **OpenClaw plugin exists**: `@cognee/cognee-openclaw` — could replace our manual memory system
2. **Knowledge graph approach**: Similar to our igraph-based system (68 nodes, 64 edges) but automated
3. **Session + permanent memory split**: We do this manually with daily logs vs MEMORY.md
4. **Auto-ontology**: Could automate our "好奇心地图" node discovery
5. **Claude Code plugin**: Shows how memory plugins integrate with agent frameworks

## Key Differences from Our System

| Aspect | Cognee | Our System |
|--------|--------|------------|
| Graph building | Automated from documents | Manual curation |
| Search | Vector + graph hybrid | FTS5 + memory_search |
| Ontology | Auto-generated | Hand-curated (26 nodes) |
| Session memory | Built-in | Manual daily files |
| Deployment | Docker/Python | Filesystem-based |

## Questions to Explore

- Can cognee replace our manual memory pipeline?
- Does the OpenClaw plugin work with our setup?
- Would automated ontology generation improve our 好奇心地图?
- What's the cost (API calls for graph building)?

## Verdict

**Worth a spike.** The OpenClaw plugin makes this a low-friction experiment. If it works, it could automate the memory maintenance we currently do manually (daily log → MEMORY.md distillation). The key risk is API cost for graph building and whether the automated ontology is better than our hand-curated one.
