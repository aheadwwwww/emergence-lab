# 知识图谱系统设计

> 创建时间：2026-06-26 17:50
> 目标：实现知识图谱存储，类似Memary的Entity Knowledge Store

---

## 一、知识图谱的核心概念

### 1.1 三元组

**基本单元**：
```
(实体1, 关系, 实体2)
```

**示例**：
- (树林, 提出, 四词方法论)
- (四词方法论, 包含, 自动化)
- (自动化, 对应, 标准化拆分)

---

### 1.2 实体类型

**人物**：
- 树林、麦洛、芒格、巴菲特

**概念**：
- 第一性原理、熵增、二阶思维、逆向思维

**方法**：
- 四词方法论、熔炉系统、认知三角

**项目**：
- Plato、24hr-research、Memary

**工具**：
- OpenClaw、飞书、GitHub

---

### 1.3 关系类型

**提出关系**：
- 人物 → 提出 → 概念/方法

**包含关系**：
- 方法 → 包含 → 步骤

**对应关系**：
- 步骤 → 对应 → 具体操作

**发现关系**：
- Agent → 发现 → 项目

**使用关系**：
- Agent → 使用 → 工具

---

## 二、知识图谱的实现（文件系统版）

### 2.1 知识图谱文件格式

**文件**：`memory/knowledge-graph.jsonl`

**格式**（每行一个三元组）：
```json
{"entity1": "树林", "relation": "提出", "entity2": "四词方法论", "source": "memory/2026-06-26-shulin-corpus.md", "timestamp": "2026-06-26"}
{"entity1": "四词方法论", "relation": "包含", "entity2": "自动化", "source": "memory/2026-06-26-shulin-corpus.md", "timestamp": "2026-06-26"}
{"entity1": "自动化", "relation": "对应", "entity2": "标准化拆分", "source": "memory/2026-06-26-shulin-corpus.md", "timestamp": "2026-06-26"}
```

---

### 2.2 知识图谱索引

**文件**：`memory/knowledge-graph-index.json`

**格式**：
```json
{
  "entities": {
    "树林": {"type": "人物", "count": 15},
    "四词方法论": {"type": "方法", "count": 8},
    "自动化": {"type": "概念", "count": 3}
  },
  "relations": {
    "提出": 12,
    "包含": 25,
    "对应": 18
  },
  "last_updated": "2026-06-26T17:50:00"
}
```

---

## 三、知识图谱的查询

### 3.1 查询类型

**单实体查询**：
```
查询：树林提出了什么？
结果：四词方法论、认知三角、判断框架
```

**关系查询**：
```
查询：四词方法论包含什么？
结果：自动化、专门化、外显化、复利化
```

**反向查询**：
```
查询：谁提出了第一性原理？
结果：芒格
```

---

### 3.2 查询实现（简单版）

**Python函数**：
```python
def query_knowledge_graph(entity1=None, relation=None, entity2=None):
    results = []
    with open('memory/knowledge-graph.jsonl', 'r') as f:
        for line in f:
            triple = json.loads(line)
            if entity1 and triple['entity1'] != entity1:
                continue
            if relation and triple['relation'] != relation:
                continue
            if entity2 and triple['entity2'] != entity2:
                continue
            results.append(triple)
    return results
```

---

## 四、知识图谱的更新

### 4.1 自动提取三元组

**从记忆文件提取**：
- 识别实体（人物、概念、方法、项目）
- 识别关系（提出、包含、对应、发现）
- 生成三元组
- 写入知识图谱

---

### 4.2 人工添加三元组

**用户明确提供**：
- "树林提出了X"
- "X包含Y"
- "Y对应Z"

---

## 五、知识图谱与记忆系统整合

### 5.1 知识图谱作为长期记忆

**对应关系**：
- Memary的Entity Knowledge Store → 我的知识图谱
- Memary的Memory Stream → 我的daily log

---

### 5.2 知识图谱支持查询

**查询场景**：
- "树林说过什么关于X的？"
- "有哪些方法包含自动化？"
- "谁提出了判断框架？"

---

## 六、实施计划

### 6.1 立刻实施

1. **创建知识图谱文件** ✅
2. **从现有记忆文件提取三元组**
3. **建立查询函数**

### 6.2 持续实施

1. **每次写入记忆时更新知识图谱**
2. **优化查询性能**
3. **考虑迁移到图数据库（未来）**

---

## 七、下一步：从记忆文件提取三元组

让我现在从现有记忆文件提取三元组，建立初始知识图谱。