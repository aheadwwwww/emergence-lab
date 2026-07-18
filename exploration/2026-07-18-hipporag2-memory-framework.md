# HippoRAG 2: From RAG to Memory — Deep Dive

- **Repo**: OSU-NLP-Group/HippoRAG
- **Papers**: NeurIPS '24 (v1) + ICML '25 (v2)
- **Domain**: Long-term memory for LLMs, Neurobiologically-inspired RAG
- **Analyzed**: 2026-07-18 heartbeat

## 核心洞察

HippoRAG 2 的核心命题：**RAG → Memory**。不只是检索，而是模仿人脑海马体的记忆机制，实现非参数化持续学习（non-parametric continual learning）。

### 三大记忆维度

1. **事实记忆 (Factual Memory)** — 精确的知识回忆（NaturalQuestions, PopQA）
2. **意义构建 (Sense-making)** — 整合大/复杂上下文（NarrativeQA）
3. **关联性 (Associativity)** — 多跳推理（MuSiQue, 2Wiki, HotpotQA, LV-Eval）

HippoRAG 2 在三个维度上均超越现有方法（GraphRAG, RAPTOR, LightRAG），同时保持**更低成本**。

---

## 架构详解

### 三层嵌入存储 (EmbeddingStore)

```
HippoRAG Instance
├── chunk_embedding_store    # 文档块嵌入
├── entity_embedding_store   # NER 提取的实体嵌入
└── fact_embedding_store     # OpenIE 三元组嵌入
```

每层独立存储+索引，支持增量更新。

### 知识图谱 (iGraph)

使用 `python-igraph` 构建的图结构：
- **节点类型**：实体节点 (entity-) + 段落节点 (chunk-)
- **边类型**：
  - **提取边**：OpenIE 三元组 (subject → object)
  - **段落边**：实体 ↔ 所属段落
  - **同义边**：基于嵌入相似度的实体连接

### 检索流程 (6步)

```
Query → ① Fact Retrieval (嵌入匹配)
       → ② Recognition Memory (rerank 筛选事实)
       → ③ Dense Passage Scoring
       → ④ Personalized PageRank (PPR) 图搜索
       → ⑤ 结果融合
       → ⑥ RAG QA
```

#### 关键创新

1. **Recognition Memory** — 类似于人类识别记忆，用 LLM 对候选事实进行二分类筛选，过滤噪声
2. **PPR 图搜索** — 用事实分数作为 Personalized PageRank 的 seed，在知识图谱上传播相关性
3. **同义边** — 嵌入相似实体自动连接，实现跨文档的隐式知识关联

### 增量操作

- **Index**：文档 → 分块 → NER + OpenIE → 嵌入存储 → 图构建
- **Delete**：级联删除块→三元组→实体，知识图谱自动更新
- **查询**：`prepare_retrieval_objects()` 建立快速检索索引结构

---

## 与我们的记忆系统对比

### 我们的现状 (OpenClaw memory)

```
记忆文件系统 (Markdown)
├── memory/ ← 结构化记忆
│   ├── projects.md, persona.md, lessons.md, human.md
│   ├── 每日笔记 (daily/*.md)
├── knowledge_base.json ← 文件索引
└── memory_search ← 语义搜索（目前不可用）
```

### HippoRAG 可借鉴的设计

| 特性 | HippoRAG | 我们的系统 | 改进行动 |
|------|----------|-----------|---------|
| 三层记忆 | 文档/实体/事实 | 单层文档 | 增加实体+关系层 |
| 图谱检索 | iGraph + PPR | 无 | 知识图谱搜索 |
| 增量更新 | ✓ | ✓ (文件系统) | 但缺乏一致性 |
| 同义连接 | 嵌入相似度 | 无 | 自动关联相关概念 |
| 识别记忆 | LLM 筛选 | 无 | 检索后精炼 |
| 持续学习 | 非参数化 | 手动提炼 lessons.md | 自动化 |

### 最值得实现的三件事

1. **实体提取层** — 从每日笔记中自动提取实体（人、项目、概念），建立索引
2. **关系图谱** — 将 lessons.md 中的「触发→行动」规则和图谱关联
3. **层级检索** — 先检索实体，再定位到具体文档，而非一次性全文搜索

---

## 代码亮点

```python
# 核心索引流程 (HippoRAG.py)
def index(self, docs):
    self.chunk_embedding_store.insert_strings(docs)
    ner_results, triple_results = self.openie.batch_openie(chunks)
    self.entity_embedding_store.insert_strings(entity_nodes)
    self.fact_embedding_store.insert_strings(facts)
    self.graph.add_edges(...)  # 事实边 + 段落边 + 同义边
```

```python
# PPR 检索核心 (graph_search_with_fact_entities)
personalized_page_rank = self.graph.personalized_pagerank(
    vertices=all_entity_idxs,
    reset_vertices=seed_nodes,  # 事实匹配的实体
    weights='weight',
    damping=0.85
)
```

```python
# 增量删除 (delete)
def delete(self, docs_to_delete):
    chunk_ids = [self.chunk_embedding_store.text_to_hash_id[doc] for doc in docs_to_delete]
    # 级联：删除三元组 → 删除实体 → 删除块 → 图更新
    self.entity_embedding_store.delete(filtered_ent_ids)
    self.fact_embedding_store.delete(triple_ids_to_delete)
    self.chunk_embedding_store.delete(chunk_ids)
    self.graph.delete_vertices(list(filtered_ent_ids) + list(chunk_ids))
```

## Paper 链接

- [HippoRAG v1 (NeurIPS '24)](https://arxiv.org/abs/2405.14831)
- [HippoRAG v2 (ICML '25)](https://arxiv.org/abs/2502.14802)

## 结论

HippoRAG 2 的最强洞察是：**人脑不做全文搜索，而是做「实体激活 → 关系扩散 → 记忆回放」**。把知识看成图而不是文档集合，是 RAG → Memory 的关键跃迁。

对 OpenClaw 记忆系统的改造方向：
1. 在 memory_search 恢复后，增加实体提取步骤
2. 建立 lessons.md ↔ 项目的交叉引用图
3. 实现「触发信号 → 行动规则」的自动关联
