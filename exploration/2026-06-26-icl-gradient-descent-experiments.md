# In-Context Learning as Gradient Descent - Experiment Design

**Date**: 2026-06-26 23:35 GMT+8
**Based on**: arXiv:2212.07677 (Google Research)

---

## Core Hypothesis

**Transformers perform gradient descent during inference via attention.**

This means my knowledge graph should be structured as "training examples" not just facts.

---

## Experiment 1: Memory Format Comparison

### Setup

```python
# Fact-based memory (current)
fact_memory = [
    ("树林", "提出", "四词方法论"),
    ("四词方法论", "包含", "听炼铸行"),
    ("熔炉系统", "实现", "认知循环"),
]

# Example-based memory (proposed)
example_memory = [
    {
        "context": "当我不知道如何行动时",
        "method": "四词方法论",
        "steps": ["听-收集信息", "炼-提炼核心", "铸-建立框架", "行-付诸实践"],
        "outcome": "找到行动方向",
    },
    {
        "context": "当我要学习新领域时",
        "method": "熔炉系统",
        "steps": ["采集", "炼", "铸器", "输出"],
        "outcome": "建立知识体系",
    },
]
```

### Prediction

Example-based memory should improve:
- Task completion rate
- Response relevance
- Context utilization

---

## Experiment 2: Optimal Memory Size

The paper suggests gradient descent needs enough steps (attention layers = GD steps).

```python
# Hypothesis: There's an optimal memory size
# - Too small: underfitting (model doesn't learn)
# - Too large: overfitting (loses generalization)

memory_sizes = [10, 50, 100, 200, 500]
for size in memory_sizes:
    # Sample size triples from knowledge graph
    memory = kg.sample(size)
    # Test agent performance
    score = benchmark(memory)
    results.append((size, score))

# Expect inverted-U curve
```

---

## Experiment 3: Multi-Scale Memory

HippoRAG uses 3 embedding levels. This might correspond to multi-scale GD:

```python
# Chunk level = high-level direction
chunks = embed_chunks(documents)  # 768-dim

# Entity level = feature selection  
entities = embed_entities(extract_entities(documents))

# Fact level = parameter updates
facts = embed_facts(extract_triples(documents))

# Retrieval: combine all three scales
def retrieve(query):
    chunk_scores = cosine(query, chunks)
    entity_scores = cosine(query, entities)
    fact_scores = cosine(query, facts)
    return weighted_sum([chunk_scores, entity_scores, fact_scores])
```

---

## Connection to My Knowledge Graph

Current igraph implementation:
- 87 nodes, 91 edges
- Multi-hop queries
- Community detection

Next step: **Structure as examples**

```python
# Instead of just storing triples
kg.add_triple("树林", "提出", "四词方法论")

# Store with context
kg.add_example(
    subject="树林",
    relation="提出",
    obj="四词方法论",
    context="当面对复杂问题时，需要系统方法论",
    usage="用于分解问题、建立框架",
    examples=["用于认知工作", "用于项目管理"],
)
```

---

## Implementation Plan

1. [ ] Extend `tools/update_knowledge_graph.py` to accept context/examples
2. [ ] Add `get_examples()` method to `KnowledgeGraphQuery`
3. [ ] Test with real agent queries
4. [ ] Compare performance vs fact-only memory

---

*Created: 2026-06-26 23:35 GMT+8*
