# igraph 快速入门笔记

> 学习时间：2026-06-26 20:10
> 目标：理解igraph的基本用法，用于构建知识图谱

---

## 一、igraph简介

**igraph**：轻量级图库，纯Python实现

**优势**：
- 不需要独立服务（不像Neo4j）
- 支持多种图算法
- 支持图遍历

**安装**：
```bash
pip install igraph
```

---

## 二、基本用法

### 2.1 创建图

```python
import igraph as ig

# 创建空图
g = ig.Graph()

# 添加节点
g.add_vertices(3)  # 添加3个节点

# 添加边
g.add_edges([(0, 1), (1, 2), (0, 2)])  # 添加3条边

# 设置节点属性
g.vs["name"] = ["树林", "芒格", "我"]
g.vs["type"] = ["人物", "人物", "人物"]

# 设置边属性
g.es["relation"] = ["提出", "提出", "发现"]
g.es["weight"] = [1.0, 1.0, 1.0]
```

---

### 2.2 查询节点和边

```python
# 获取节点
nodes = g.vs
for node in nodes:
    print(node["name"], node["type"])

# 获取边
edges = g.es
for edge in edges:
    source = g.vs[edge.source]["name"]
    target = g.vs[edge.target]["name"]
    relation = edge["relation"]
    print(f"{source} → {relation} → {target}")
```

---

### 2.3 图遍历

```python
# 查找节点
node = g.vs.find(name="树林")

# 获取邻居
neighbors = node.neighbors()
for neighbor in neighbors:
    print(neighbor["name"])

# 获取连接的边
edges = node.incident()
for edge in edges:
    print(edge["relation"])
```

---

### 2.4 多跳查询

```python
# BFS遍历（广度优先）
paths = g.get_shortest_paths(0, to=2)

# 获取路径上的节点
for path in paths:
    nodes_in_path = [g.vs[node_id]["name"] for node_id in path]
    print(nodes_in_path)

# 获取路径上的边
for path in paths:
    edges_in_path = g.es[path]
    relations = [e["relation"] for e in edges_in_path]
    print(relations)
```

---

## 三、与Neo4j对比

| 维度 | igraph | Neo4j |
|------|--------|-------|
| 安装 | pip install | 需要独立服务 |
| 语言 | Python | Cypher |
| 存储 | 内存/文件 | 独立数据库 |
| 查询 | Python API | Cypher查询 |
| 性能 | 中等 | 高 |
| 持久化 | 手动保存 | 自动持久化 |
| 适用场景 | 小规模图 | 大规模图 |

---

## 四、我的应用场景

### 4.1 短期：用igraph替代JSON Lines

**改进**：
- 用igraph存储知识图谱
- 支持图遍历查询
- 支持多跳检索

---

### 4.2 中期：迁移到Neo4j

**时机**：
- 知识图谱规模超过1000个节点
- 需要持久化存储
- 需要复杂查询

---

## 五、实现计划

### 5.1 立刻实现

**创建igraph知识图谱**：
```python
import igraph as ig
import json

# 读取三元组
triples = []
with open('memory/knowledge-graph.jsonl', 'r') as f:
    for line in f:
        triples.append(json.loads(line))

# 构建图
g = ig.Graph()
entities = set()

for triple in triples:
    entities.add(triple['entity1'])
    entities.add(triple['entity2'])

# 添加节点
g.add_vertices(len(entities))
g.vs["name"] = list(entities)

# 添加边
entity_list = list(entities)
edges = []
relations = []

for triple in triples:
    source_idx = entity_list.index(triple['entity1'])
    target_idx = entity_list.index(triple['entity2'])
    edges.append((source_idx, target_idx))
    relations.append(triple['relation'])

g.add_edges(edges)
g.es["relation"] = relations

# 保存
g.write_pickle('memory/knowledge-graph.pkl')
```

---

### 5.2 下一步

- 实现igraph知识图谱
- 实现图遍历查询
- 实现多跳检索
- 测试性能

---

**学习时间：2026-06-26 20:10**