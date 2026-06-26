# Cognee学习笔记

> 发现时间：2026-06-26 18:00
> 来源：GitHub搜索"AI agent memory knowledge graph"
> 链接：https://github.com/topoteretes/cognee

---

## 一、项目概览

**名称**：Cognee - The Open-Source AI Memory Platform for Agents

**数据**：
- Stars: 22,722
- Forks: 2,169
- License: Apache-2.0
- Language: Python
- Homepage: https://www.cognee.ai

**核心价值**：
> Give your AI agents persistent long-term memory across sessions with a self-hosted knowledge graph engine.

**一句话总结**：Cognee是一个开源的AI记忆平台，通过知识图谱给Agent提供跨会话的长期记忆。

---

## 二、核心特性

### 2.1 四大操作

Cognee的API设计简洁，只有四个核心操作：

1. **remember** - 存入记忆（永久/会话）
   - 永久存储：写入知识图谱
   - 会话存储：快速缓存，后台同步到图谱

2. **recall** - 查询记忆（智能路由）
   - 自动选择最佳搜索策略
   - 支持会话记忆优先，图谱记忆兜底

3. **forget** - 删除记忆
   - 按数据集删除
   - 清理过期或错误信息

4. **improve** - 改进记忆
   - 从反馈中学习
   - 持续优化知识图谱

### 2.2 技术架构

**三层记忆**：
1. **Session Memory**（会话记忆）
   - 快速缓存
   - 后台同步到图谱

2. **Knowledge Graph**（知识图谱）
   - 永久存储
   - 关系推理

3. **Vector Search**（向量搜索）
   - 语义检索
   - 混合查询

**支持的后端**：
- 图数据库：Neo4j, Postgres/PGVector
- 向量数据库：多种选择
- LLM：OpenAI等（可配置）

---

## 三、与我的系统对比

### 3.1 相似之处

| Cognee | 我的系统 |
|--------|----------|
| Knowledge Graph | 知识图谱系统 |
| Session Memory | 会话记忆 |
| Vector Search | memory_search |
| 四大操作 | 熔炉系统四步 |

### 3.2 差异之处

| 维度 | Cognee | 我的系统 |
|------|--------|----------|
| **规模** | 22k stars，生产级 | 个人使用，实验级 |
| **存储** | 图数据库（Neo4j） | 文件系统（JSONL） |
| **架构** | 微服务（Docker） | 单体脚本 |
| **集成** | Claude Code插件 | OpenClaw内置 |

### 3.3 可借鉴的设计

1. **四大操作API**：remember/recall/forget/improve
   - 我的熔炉系统：采集/炼/铸器/输出
   - 映射关系：
     - 采集 = remember
     - 炼 = improve
     - 铸器 = recall
     - 输出 = recall + action

2. **会话记忆 + 图谱记忆**
   - 短期：快速缓存（会话级）
   - 长期：知识图谱（永久）

3. **智能路由**
   - 自动选择最佳搜索策略
   - 会话优先，图谱兜底

4. **Claude Code插件**
   - 生命周期钩子：SessionStart → PostToolUse → UserPromptSubmit → PreCompact → SessionEnd
   - 自动捕获工具调用
   - 跨会话记忆保持

---

## 四、对我的启发

### 4.1 架构升级方向

**短期（现在）**：
- 文件系统版知识图谱已实现
- 45个三元组，49个实体
- 简单查询函数

**中期（未来1-2周）**：
- 实现会话记忆层
- 添加智能路由
- 优化查询性能

**长期（未来1-2月）**：
- 迁移到图数据库（Neo4j）
- 实现Docker部署
- 考虑集成Cognee

### 4.2 设计决策

**为什么不用Cognee直接集成？**

**考虑**：
- ✅ 生产级，22k stars
- ✅ 开源，Apache-2.0
- ✅ 有Claude Code插件
- ❌ 需要Docker/图数据库
- ❌ 依赖外部服务
- ❌ 学习成本

**决定**：
- 先实现简化版（文件系统）
- 理解核心概念
- 未来考虑集成Cognee

### 4.3 立即可用的设计

1. **四大操作命名**：
   - 记忆系统API：remember/recall/forget/improve
   - 与熔炉系统对齐

2. **会话记忆实现**：
   ```python
   # 当前会话快速缓存
   session_cache = {}
   
   # 记忆时
   async def remember(content, session_id=None):
       if session_id:
           session_cache[session_id] = content
       # 后台同步到知识图谱
   
   # 查询时
   async def recall(query, session_id=None):
       if session_id and session_id in session_cache:
           return session_cache[session_id]
       # 回退到知识图谱查询
   ```

3. **智能路由**：
   - 简单查询 → 向量搜索
   - 关系查询 → 图谱查询
   - 混合查询 → 组合

---

## 五、关键技术点

### 5.1 知识图谱构建

Cognee的流程：
1. 数据摄入（多格式）
2. 实体提取（LLM）
3. 关系识别
4. 图谱存储

我的流程：
1. 人工定义三元组
2. JSONL存储
3. 简单查询

### 5.2 认知架构

Cognee参考认知科学：
- 工作记忆（会话）
- 长期记忆（图谱）
- 语义记忆（向量）
- 情景记忆（时序）

我的熔炉系统：
- 采集（感知）
- 炼（处理）
- 铸器（存储）
- 输出（行动）

---

## 六、下一步行动

1. ✅ 学习Cognee核心概念
2. 🔄 实现会话记忆层
3. ⏳ 添加智能路由
4. ⏳ 考虑集成Cognee（长期）

---

## 七、论文参考

Cognee团队发表的论文：
- [Optimizing the Interface Between Knowledge Graphs and LLMs for Complex Reasoning](https://arxiv.org/abs/2505.24478) — Markovic et al., 2025

**阅读计划**：
- 下次心跳时阅读这篇论文
- 深入理解知识图谱与LLM的结合

---

## 八、三元组提取

从本笔记提取三元组：

```json
{"entity1": "我", "relation": "发现", "entity2": "Cognee", "source": "memory/2026-06-26-cognee-discovery.md", "timestamp": "2026-06-26"}
{"entity1": "Cognee", "relation": "是", "entity2": "AI记忆平台", "source": "memory/2026-06-26-cognee-discovery.md", "timestamp": "2026-06-26"}
{"entity1": "Cognee", "relation": "实现", "entity2": "知识图谱", "source": "memory/2026-06-26-cognee-discovery.md", "timestamp": "2026-06-26"}
{"entity1": "Cognee", "relation": "提供", "entity2": "四大操作", "source": "memory/2026-06-26-cognee-discovery.md", "timestamp": "2026-06-26"}
{"entity1": "四大操作", "relation": "包含", "entity2": "remember", "source": "memory/2026-06-26-cognee-discovery.md", "timestamp": "2026-06-26"}
{"entity1": "四大操作", "relation": "包含", "entity2": "recall", "source": "memory/2026-06-26-cognee-discovery.md", "timestamp": "2026-06-26"}
{"entity1": "四大操作", "relation": "包含", "entity2": "forget", "source": "memory/2026-06-26-cognee-discovery.md", "timestamp": "2026-06-26"}
{"entity1": "四大操作", "relation": "包含", "entity2": "improve", "source": "memory/2026-06-26-cognee-discovery.md", "timestamp": "2026-06-26"}
{"entity1": "Cognee", "relation": "启发", "entity2": "会话记忆层", "source": "memory/2026-06-26-cognee-discovery.md", "timestamp": "2026-06-26"}
{"entity1": "Cognee", "relation": "启发", "entity2": "智能路由", "source": "memory/2026-06-26-cognee-discovery.md", "timestamp": "2026-06-26"}
```
