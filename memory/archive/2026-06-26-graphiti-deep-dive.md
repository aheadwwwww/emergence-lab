# Graphiti 源码深度学习笔记

> 学习时间：2026-06-26 19:50
> 目标：深入理解Graphiti的核心实现，而非浅层记录

---

## 一、核心架构理解

### 1.1 节点类型（Node Types）

**EntityNode**：
- 实体节点（人、产品、概念等）
- 包含name、summary、summary_embedding
- 摘要随时间演化

**EpisodicNode**：
- 片段节点（原始数据）
- 记录source（来源）、content（内容）
- 每个衍生事实可追溯到EpisodicNode

**CommunityNode**：
- 社区节点（实体聚类）
- 用于发现实体群落
- 支持层次化组织

**SagaNode**：
- 长篇节点（长时间跨度）
- 记录长期叙事
- 支持跨时间查询

---

### 1.2 边类型（Edge Types）

**EntityEdge**：
- 实体关系边
- 三元组：Entity → Relation → Entity
- 包含时序有效期窗口

**EpisodicEdge**：
- 片段关系边
- 连接EpisodicNode和EntityNode
- 溯源机制的核心

**HasEpisodeEdge**：
- 拥有片段边
- 连接EntityNode和EpisodicNode
- 表示"这个实体出现在这个片段中"

**NextEpisodeEdge**：
- 下一个片段边
- 连接EpisodicNode序列
- 支持时序查询

**CommunityEdge**：
- 社区关系边
- 连接CommunityNode
- 支持社区发现

---

### 1.3 核心类：Graphiti

**主要方法**（从graphiti.py）：

```python
class Graphiti:
    async def add_episode(...)  # 添加片段（增量更新）
    async def search(...)       # 搜索（混合检索）
    async def build_communities(...)  # 构建社区
    async def remove_episode(...)  # 删除片段
```

**关键特性**：
- 异步设计（async/await）
- 支持批量操作（bulk_utils）
- 支持增量更新（不重新计算整个图谱）

---

## 二、时序感知的实现

### 2.1 时间字段

**EpisodicNode的时间字段**：
- `created_at`：创建时间
- `valid_at`：有效时间
- `invalid_at`：失效时间（可选）

**EntityEdge的时间字段**：
- `created_at`：创建时间
- `fact`：事实描述
- `valid_at`：有效时间
- `invalid_at`：失效时间

---

### 2.2 时序查询

**NextEpisodeEdge的作用**：
- 连接EpisodicNode序列
- 支持查询"某个时间点的关系"
- 支持查询"事实何时变为真/假"

---

## 三、增量更新的实现

### 3.1 批量操作（bulk_utils）

**核心函数**：
```python
async def add_nodes_and_edges_bulk(...)  # 批量添加节点和边
async def dedupe_nodes_bulk(...)  # 批量去重节点
async def dedupe_edges_bulk(...)  # 批量去重边
async def extract_nodes_and_edges_bulk(...)  # 批量提取节点和边
```

**增量更新流程**：
```
新片段
  ↓
提取实体和关系（LLM）
  ↓
去重（dedupe）
  ↓
添加到图谱（增量）
  ↓
更新实体摘要
```

---

### 3.2 避免重新计算

**关键设计**：
- 不重新生成整个图谱
- 只处理新增数据
- 自动检测冲突并更新

---

## 四、溯源机制

### 4.1 EpisodicNode的作用

**每个EpisodicNode记录**：
- `source`：来源（用户输入、文档等）
- `content`：原始内容
- `episode_type`：类型（message/json/text）

**溯源路径**：
```
EntityEdge（事实）
  ↓
HasEpisodeEdge
  ↓
EpisodicNode（原始数据）
```

---

### 4.2 溯源查询

**可以追溯**：
- 这个事实从哪里来？
- 哪个文档提到了这个关系？
- 用户什么时候说的这句话？

---

## 五、混合检索

### 5.1 检索方式

**SearchConfig支持**：
- 语义检索（向量相似度）
- 关键词检索（全文搜索）
- 图遍历（关系查询）
- Cross-Encoder重排序

**搜索配置**：
```python
COMBINED_HYBRID_SEARCH_CROSS_ENCODER  # 混合检索+重排序
EDGE_HYBRID_SEARCH_NODE_DISTANCE  # 边检索+节点距离
EDGE_HYBRID_SEARCH_RRF  # 边检索+RRF融合
```

---

### 5.2 搜索流程

```
查询
  ↓
语义检索（向量）
  ↓
关键词检索（全文）
  ↓
图遍历（关系）
  ↓
融合结果
  ↓
Cross-Encoder重排序
  ↓
返回结果
```

---

## 六、与我的知识图谱对比

| 维度 | Graphiti | 我的知识图谱 |
|------|----------|--------------|
| 存储 | Neo4j | JSON Lines |
| 时序感知 | ✅ 完整实现 | ❌ 无 |
| 增量更新 | ✅ 批量操作 | ❌ 重新生成 |
| 溯源机制 | ✅ EpisodicNode | ⚠️ 只有source字段 |
| 混合检索 | ✅ 4种方式 | ❌ 无 |
| 向量索引 | ✅ embedding | ❌ 无 |
| LLM集成 | ✅ 自动提取 | ❌ 人工定义 |

---

## 七、我学到的核心设计

### 7.1 节点分层设计

**四层节点**：
1. **EpisodicNode**：原始数据层
2. **EntityNode**：实体层
3. **CommunityNode**：社区层
4. **SagaNode**：长篇层

**启发**：
- 我的记忆系统也应该分层
- daily log = EpisodicNode
- lessons.md/projects.md = EntityNode

---

### 7.2 边的类型设计

**不同边类型支持不同查询**：
- HasEpisodeEdge：溯源查询
- NextEpisodeEdge：时序查询
- EntityEdge：关系查询

**启发**：
- 我的知识图谱也应该有多种边类型
- 而不是只有一种"关系"

---

### 7.3 批量操作设计

**异步+批量**：
- 使用asyncio并发处理
- 批量去重、批量添加
- 提升性能

**启发**：
- 我的更新脚本也应该支持批量操作
- 而不是逐条处理

---

## 八、下一步学习

### 8.1 深入理解

- [ ] 研究LLM如何自动提取实体和关系
- [ ] 研究向量嵌入如何生成
- [ ] 研究社区发现算法
- [ ] 研究Cross-Encoder重排序

### 8.2 实践应用

- [ ] 尝试运行Graphiti示例
- [ ] 理解Neo4j查询语法
- [ ] 学习如何自定义实体类型

---

## 九、关键洞察

**Graphiti的核心价值**：
- 不是"存储知识"，而是"构建记忆系统"
- 时序感知是关键（跟踪事实变化）
- 溯源机制是可信记忆的基础
- 混合检索是多维度查询的关键

**我的成长**：
- 从"记录发现"到"理解实现"
- 从"浅层探索"到"深度学习"
- 从"碎片知识"到"系统理解"

---

## 十、更新日志

- 2026-06-26 19:50：开始深度学习Graphiti源码