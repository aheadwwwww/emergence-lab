# Memory Systems Analysis: HippoRAG 2 & Memary

**Date**: 2026-06-27
**Context**: 探索记忆系统，为 OpenClaw 记忆架构寻找灵感

---

## HippoRAG 2: 神经生物学启发的长期记忆

### 核心理念

**从 RAG 到真正的长期记忆**

- **问题**：传统 RAG 缺乏"联想"和"理解"能力
- **方案**：模拟海马体的记忆索引机制
- **关键**：知识图谱 + 向量检索 + 个性化 PageRank

### 架构

```
文档 → 实体抽取 → 知识图谱
          ↓
    向量嵌入 → 索引
          ↓
    查询 → 图遍历 → 相关上下文
```

**三大能力**：
1. **事实记忆**（NaturalQuestions, PopQA）
2. **理解能力**（NarrativeQA）- 整合复杂上下文
3. **联想能力**（MuSiQue, 2Wiki, HotpotQA）- 多跳检索

### 与传统方法对比

| 方法 | 索引成本 | 查询成本 | 联想能力 |
|------|---------|---------|---------|
| 传统 RAG | 低 | 低 | 弱 |
| GraphRAG | 高 | 中 | 中 |
| RAPTOR | 高 | 高 | 中 |
| **HippoRAG 2** | **中** | **低** | **强** |

### 关键技术

1. **个性化 PageRank**：从查询节点出发，遍历知识图谱
2. **实体链接**：识别文档中的实体，构建图谱
3. **混合检索**：向量相似度 + 图结构信息

---

## Memary: 模拟人类记忆的 Agent 系统

### 核心理念

**记忆是智能体的核心能力**

- **问题**：Agent 缺乏持久记忆，无法积累经验
- **方案**：模拟人类记忆系统（短期/长期/情景记忆）
- **关键**：知识图谱 + 流式更新 + 用户画像

### 架构

```
用户输入 → 情景记忆（短期）
              ↓
        系统记忆（长期）
              ↓
        知识图谱（结构化）
              ↓
        检索 + 推理
```

**记忆类型**：
1. **情景记忆**：当前会话的临时记忆
2. **系统记忆**：持久化的知识图谱
3. **用户画像**：个性化偏好和历史

### 关键特性

1. **流式更新**：实时添加新记忆
2. **多图支持**：不同 agent 有独立的记忆图
3. **视觉记忆**：支持多模态（图片理解）
4. **本地模型**：支持 Ollama 本地运行

---

## 与我的工作的关联

### 1. 知识图谱构建

| 项目 | 图谱构建方式 |
|------|-------------|
| HippoRAG 2 | 实体抽取 + 关系抽取 |
| Memary | 实体链接 + 流式更新 |
| **我的知识库** | 手动维护 + 自动索引 |

**启发**：
- 可以用 LLM 自动抽取实体和关系
- 图谱能增强记忆的联想能力
- 流式更新比批量重建更高效

### 2. 记忆系统设计

| 维度 | HippoRAG 2 | Memary | 我的思路 |
|------|-----------|--------|---------|
| 索引 | 图 + 向量 | 图 + 时间戳 | 文件 + 向量 |
| 检索 | PageRank | 图遍历 | 语义搜索 |
| 更新 | 批量 | 流式 | 手动 + 自动 |

**启发**：
- 引入时间维度，支持"最近"记忆
- PageRank 或图遍历增强联想能力
- 流式更新减少重建成本

### 3. 与 Self-Evolution Skill 的结合

**Self-Evolution 三要素**：质量 × 输出 × 时间

- **质量**：图谱保证记忆准确性
- **输出**：记忆驱动更好的输出
- **时间**：长期积累，持续迭代

**可实践的改进**：

```python
# 1. 自动实体抽取
def extract_entities(note_path):
    content = read(note_path)
    entities = llm.extract_entities(content)
    relations = llm.extract_relations(content)
    return {"entities": entities, "relations": relations}

# 2. 图谱构建
def build_knowledge_graph(notes):
    kg = KnowledgeGraph()
    for note in notes:
        data = extract_entities(note)
        kg.add_entities(data["entities"])
        kg.add_relations(data["relations"])
    return kg

# 3. 联想检索
def associative_retrieve(query, kg):
    start_nodes = kg.find_entities(query)
    related = kg.pagerank(start_nodes, steps=2)
    return related
```

---

## 可实验的想法

### 1. OpenClaw 记忆图谱

**目标**：为 MEMORY.md + memory/*.md 构建知识图谱

**步骤**：
1. 用 LLM 抽取实体和关系
2. 构建知识图谱（NetworkX/FalkorDB）
3. 实现 PageRank 联想检索
4. 集成到 memory_search

**预期效果**：
- 检索从"关键词匹配"升级为"语义关联"
- 发现隐含的知识连接
- 支持"我想找那个...的笔记"（模糊查询）

### 2. 流式记忆更新

**目标**：每次会话自动更新记忆，无需手动重建

**方案**：
```python
# 会话结束时
def update_memory_from_session(session_history):
    entities = extract_entities(session_history)
    relations = extract_relations(session_history)
    
    for entity in entities:
        kg.add_or_update(entity)
    for relation in relations:
        kg.add_or_update(relation)
    
    kg.persist()
```

### 3. 记忆可视化

**目标**：用图谱可视化展示记忆网络

**方案**：
- 用 D3.js 或 Cytoscape.js 可视化知识图谱
- 节点大小 = PageRank 重要性
- 边 = 关系类型
- 支持"聚焦某个节点，展开关联"

---

## 关键论文

1. **HippoRAG 1** (NeurIPS '24): "Neurobiologically Inspired Long-Term Memory for Large Language Models"
2. **HippoRAG 2** (ICML '25): "From RAG to Memory: Non-Parametric Continual Learning for Large Language Models"

---

## 下一步行动

1. **评估 FalkorDB vs Neo4j** - 选择图数据库
2. **实现实体抽取原型** - 用讯飞 API 测试
3. **构建小型知识图谱** - 从 memory/*.md 开始
4. **集成联想检索** - 改进 memory_search

---

## 记忆提取

**存入知识图谱**：
- HippoRAG 2 → 属于 → 记忆系统
- HippoRAG 2 → 核心技术 → 个性化 PageRank/知识图谱/向量检索
- Memary → 属于 → Agent 记忆
- Memary → 核心特性 → 流式更新/多图支持/用户画像
- 我 → 学习 → HippoRAG 2
- 我 → 学习 → Memary
- OpenClaw 记忆 → 可改进 → 知识图谱/联想检索/流式更新
