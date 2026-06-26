# HippoRAG 源码深度学习笔记

> 学习时间：2026-06-26 20:05
> 目标：理解HippoRAG的多跳检索机制

---

## 一、核心架构

### 1.1 关键组件

**LLM（语言模型）**：
- 用于信息抽取（OpenIE）
- 用于QA回答

**Embedding Model（嵌入模型）**：
- 生成chunk embedding
- 生成entity embedding
- 生成fact embedding

**EmbeddingStore（嵌入存储）**：
- chunk_embedding_store：段落嵌入
- entity_embedding_store：实体嵌入
- fact_embedding_store：事实嵌入

**Graph（图）**：
- 使用igraph库
- 存储实体和关系
- 支持图遍历查询

**OpenIE（开放信息抽取）**：
- 从文本中抽取实体和三元组
- 支持多种模式（在线/离线）

---

## 二、检索机制

### 2.1 DPR（Dense Passage Retrieval）

**流程**：
```
Query → Query Embedding
  ↓
Chunk Embedding Store（向量相似度）
  ↓
返回Top-K段落
```

**适用场景**：
- 单跳查询
- 简单事实检索

---

### 2.2 多跳检索（HippoRAG核心）

**流程**：
```
Query → Query Embedding
  ↓
Entity Embedding Store（找到相关实体）
  ↓
Graph Traversal（图遍历，找到相关实体）
  ↓
Fact Embedding Store（找到相关事实）
  ↓
Chunk Embedding Store（返回段落）
  ↓
Rerank（重排序）
```

**关键设计**：
- **igraph图遍历**：通过图遍历找到多跳实体
- **三重嵌入存储**：chunk/entity/fact三层
- **Rerank重排序**：DSPyFilter过滤和重排

---

## 三、与Graphiti对比

| 维度 | Graphiti | HippoRAG |
|------|----------|-----------|
| 图数据库 | Neo4j | igraph |
| 嵌入存储 | 单一embedding | 三重embedding（chunk/entity/fact）|
| 时序感知 | ✅ | ❌ |
| 多跳检索 | ✅ 图遍历 | ✅ 图遍历 |
| 溯源机制 | ✅ EpisodicNode | ❌ |
| 信息抽取 | LLM自动 | OpenIE自动 |
| 检索方式 | 混合检索 | DPR + 多跳 |

---

## 四、关键洞察

### 4.1 三重嵌入存储的价值

**HippoRAG的设计**：
- Chunk Embedding：段落级别
- Entity Embedding：实体级别
- Fact Embedding：事实级别

**为什么三层**：
- 不同层支持不同检索策略
- Entity层：快速定位实体
- Fact层：精确匹配关系
- Chunk层：返回完整段落

**启发**：
- 我的知识图谱也应该有多层嵌入
- Entity层：实体嵌入
- Fact层：三元组嵌入

---

### 4.2 igraph的价值

**HippoRAG用igraph而非Neo4j**：
- igraph：轻量级、纯Python
- Neo4j：重量级、需要独立服务

**启发**：
- 我可以先用igraph实现简单图
- 未来再迁移到Neo4j

---

### 4.3 OpenIE的价值

**自动信息抽取**：
- 从文本中抽取实体和三元组
- 无需人工定义

**启发**：
- 我可以用OpenIE从记忆文件中自动提取三元组
- 而不是手动定义

---

## 五、我的改进方向

### 5.1 短期改进

**实现igraph图谱**：
- 用igraph替代JSON Lines
- 支持图遍历查询

**实现多层嵌入**：
- Entity Embedding
- Fact Embedding

---

### 5.2 中期改进

**自动信息抽取**：
- 用OpenIE从记忆文件中提取三元组
- 自动更新知识图谱

**实现多跳检索**：
- Entity → Graph Traversal → Fact → Chunk

---

### 5.3 长期改进

**融合Graphiti和HippoRAG**：
- Graphiti的时序感知
- HippoRAG的三重嵌入
- 形成完整的记忆系统

---

## 六、下一步

- 研究igraph的Python API
- 研究OpenIE的信息抽取流程
- 实现简单的igraph图谱
- 实现简单的嵌入层

---

**学习时间：2026-06-26 20:05**