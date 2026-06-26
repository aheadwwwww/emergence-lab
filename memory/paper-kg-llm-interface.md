# Optimizing the Interface Between Knowledge Graphs and LLMs for Complex Reasoning

**Paper**: arxiv 2505.24478  
**Authors**: Vasilije Marković, Lazar Obradović, Laszlo Hajdu, Jovan Pavlović  
**Affiliation**: Cognee Inc., University of Primorska, Innorenew CoE  
**Date**: 2025 (preliminary version)

---

## Core Thesis/Problem

Integrating Large Language Models (LLMs) with Knowledge Graphs (KGs) creates complex systems with **numerous hyperparameters** that directly affect performance. While such systems are increasingly common in retrieval-augmented generation (RAG), the role of **systematic hyperparameter optimization remains underexplored**.

This paper studies hyperparameter optimization in graph-based RAG systems using **Cognee**—a modular framework for end-to-end KG construction and retrieval—evaluating on multi-hop QA benchmarks to understand how configuration choices affect performance.

---

## Key Methods

### 1. Cognee Framework Architecture

Cognee implements an **Extract–Cognify–Load (ECL) pipeline**:

| Stage | Description |
|-------|-------------|
| **Ingestion** | Load and normalize raw inputs (text, PDFs, images, audio, code) into file/object storage |
| **Tagging** | Classify by media type, merge metadata, deduplicate, organize into datasets |
| **Chunking** | Segment documents into token-limited chunks for extraction |
| **Graph Construction** | Extract entities and relations using LLMs, assemble graph fragments |
| **Indexing** | Write outputs to graph, relational, and vector storage systems |

### 2. Hyperparameter Optimization Framework (Dreamify)

The authors developed **Dreamify**, treating the entire Cognee pipeline as a parameterized process. Each trial = complete pipeline run from corpus construction to evaluation.

**Optimization Algorithm**: Tree-structured Parzen Estimator (TPE)  
- Well-suited for mixed discrete and integer-valued parameters
- Chosen over grid search (impractical at scale) and random search (underperformed)

### 3. Tunable Parameters

| Parameter | Description | Range/Options |
|-----------|-------------|---------------|
| **Chunk Size** | Tokens per document segment for graph extraction | 200–1000 tokens |
| **Retriever Type** | Strategy for context retrieval | `cognee_completion` (vector text chunks) or `cognee_graph_completion` (graph triplets) |
| **Top-K** | Number of retrieved items passed to LLM | 1–20 |
| **QA Prompt** | Instruction template for answer generation | Multiple templates |
| **Graph Prompt** | Template for entity/relation extraction | Multiple templates |
| **Task Getter** | Dataset preprocessing and summary handling | Configuration option |

### 4. Retrieval Strategies Compared

| Retriever | Description |
|-----------|-------------|
| Summary-Based | Retrieves chunk-level summaries using semantic similarity |
| Chunk-Level | Retrieves original text chunks via embedding similarity |
| Graph Neighborhood | Retrieves nodes adjacent to matched entity |
| RAG | Passes retrieved text chunks to LLM for answer generation |
| Graph Completion | Retrieves graph triples, uses LLM to generate response |
| Graph-Summary Completion | Summarizes subgraph with LLM before generating response |

### 5. Evaluation Setup

**Benchmarks**: HotPotQA, TwoWikiMultiHop, MuSiQue (multi-hop QA datasets)

**Metrics**:
- Exact Match (EM)
- Token-level F1
- **DeepEval's LLM-based correctness** (evaluates answer plausibility against gold reference)

---

## Main Findings/Results

### Performance Improvements

| Dataset | Metric | Baseline | Optimized | Improvement |
|---------|--------|----------|-----------|-------------|
| HotPotQA | EM | 0.143 | 0.200 | +40% |
| HotPotQA | F1 | 0.242 | 0.333 | +38% |
| HotPotQA | Correctness | 0.566 | 0.700 | +24% |
| TwoWikiMultiHop | EM | 0.046 | 0.086 | +87% |
| TwoWikiMultiHop | F1 | 0.125 | 0.221 | +77% |
| TwoWikiMultiHop | Correctness | 0.400 | 0.593 | +48% |
| MuSiQue | EM | 0.029 | 0.057 | +97% |
| MuSiQue | F1 | 0.056 | 0.136 | +143% |
| MuSiQue | Correctness | 0.267 | 0.400 | +50% |

### Key Observations

1. **Meaningful gains achievable through targeted tuning** — even modest parameter changes led to measurable improvements
2. **Gains are consistent but not uniform** — performance varies across datasets and metrics
3. **High-performing configurations shared parameter settings** — especially for chunk size and retrieval method
4. **Effects are nonlinear and task-specific** — no single configuration performed best across all benchmarks
5. **Generalization holds reasonably well** — test set performance showed moderate degradation from training scores

### Evaluation Metric Limitations

- **Exact Match & F1**: Penalize semantically correct answers phrased differently from reference
- **LLM-based correctness**: More tolerant of lexical variation but introduces inconsistencies (format sensitivity, implicit assumptions, noise in grading)

---

## Architecture Insights for Personal Knowledge Graph + LLM Systems

### 1. Modularity is Critical

Cognee's modular architecture enabled **clean separation and independent configuration** of pipeline components. For personal PKG systems:
- Design each stage (ingestion, chunking, extraction, retrieval, generation) as independent, swappable modules
- Allow per-component configuration without affecting others
- Support multiple storage backends (graph, vector, relational)

### 2. Graph vs Vector Retrieval Trade-offs

**Graph-based retrieval (`cognee_graph_completion`)**:
- Retrieves knowledge graph nodes and triplets
- Combines vector similarity with graph structure
- Emphasizes relational context — better for multi-hop reasoning
- Formats triplets as structured text for LLM

**Text-based retrieval (`cognee_completion`)**:
- Standard vector similarity over text chunks
- Simpler but may miss relational connections

**Insight**: For complex reasoning, graph-based retrieval provides structured context that supports multi-hop reasoning better than pure vector search.

### 3. Chunk Size Matters Significantly

- Range tested: 200–1000 tokens
- Affects both graph structure and retrieval granularity
- Smaller chunks = more granular graph, finer retrieval specificity
- Larger chunks = more context per extraction, but may dilute precision
- **Tune based on content type and reasoning requirements**

### 4. Hyperparameter Interactions are Complex

- No universal best configuration
- Chunk size and retriever type showed strongest effects
- Task characteristics strongly influence optimal settings
- **Recommendation**: Implement systematic tuning per domain/use case

### 5. Storage Architecture

Three-tier storage:
- **Graph database**: Entity and relation queries
- **Vector store**: Similarity-based retrieval
- **Relational store**: Metadata, question-answer pairs, evaluation data

For personal PKG:
- Consider Neo4j, NebulaGraph, or similar for graph layer
- Use pgvector, Qdrant, or similar for vector search
- SQLite or PostgreSQL for metadata

### 6. Evaluation Framework Design

Four-stage evaluation pipeline:
1. **Corpus construction** — clear memory, reprocess documents
2. **Question answering** — instantiate retriever, generate answers
3. **Answer evaluation** — compare against gold reference
4. **Metric aggregation** — bootstrap estimates, confidence intervals

For personal systems:
- Build benchmark datasets from your own Q&A pairs
- Track multiple metrics (EM, F1, LLM-graded correctness)
- Use bootstrap confidence intervals for reliable comparisons

### 7. Schema-Based Extraction

- Use Pydantic models to define entity types and relations
- Schema guides LLM extraction for consistent graph structure
- Enables domain-specific knowledge modeling

### 8. Prompt Engineering as Tunable Parameter

Both QA prompts and graph extraction prompts are tunable:
- Different prompts work better for different tasks
- Consider prompt templates as configuration parameters
- Test variations systematically rather than relying on intuition

---

## Takeaways for Building Personal KG + LLM Systems

### Architecture Recommendations

1. **Start with modular pipeline design**
   - Ingestion → Chunking → Extraction → Indexing → Retrieval → Generation
   - Each stage independently configurable

2. **Implement multiple retrieval strategies**
   - Pure vector search for simple semantic similarity
   - Graph traversal for multi-hop reasoning
   - Hybrid approaches for complex queries

3. **Design for systematic tuning**
   - Expose key parameters as configuration
   - Build evaluation into the pipeline
   - Track performance across parameter combinations

4. **Choose chunk size based on use case**
   - Smaller for precise retrieval, larger for broader context
   - Test empirically on your content

5. **Use graph format for structured knowledge**
   - Triplets (entity, relation, entity) provide explicit relationships
   - Supports multi-hop reasoning naturally
   - Combine with vector search for semantic matching

### Practical Implementation Notes

- **Cognee is open-source**: https://github.com/cognee-ai/cognee
- Supports heterogeneous inputs: text, images, audio, code
- Containerized deployment available
- Browser-accessible UI included

### Future Directions from Paper

- Alternative optimization algorithms (beyond TPE)
- Broader parameter spaces
- Multi-objective optimization (accuracy, latency, safety)
- Custom benchmarks for domain-specific evaluation
- Shared benchmark infrastructure for graph-augmented RAG

---

## Key Citation

> "The cognification of these systems will not happen through design alone, but through how they are tuned, measured, and adapted over time."

This paper demonstrates that **systematic hyperparameter tuning** in graph-based RAG systems leads to **consistent, measurable performance improvements**, but optimization is **task-specific**—no universal configuration exists. The key insight is treating the entire pipeline as a tunable system rather than optimizing components in isolation.