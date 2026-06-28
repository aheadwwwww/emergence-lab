# Memary Agent记忆层 学习笔记

> 发现时间：2026-06-26
> 来源：GitHub搜索 autonomous-agent-memory

---

## 一、项目概述

**Memary** 是一个开源Agent记忆层，模拟人类记忆系统来增强AI Agent。

**核心价值**：
- 模拟人类记忆（短期记忆、长期记忆、知识图谱）
- 开源、可扩展
- 支持多图（多Agent）管理

---

## 二、核心特性

### 2.1 记忆系统

**记忆流**（Memory Stream）：
- 存储对话和事件
- 类似人类的"短期记忆"

**实体知识库**（Entity Knowledge Store）：
- 知识图谱存储
- 类似人类的"长期记忆"

**用户画像**（User Persona）：
- 用户信息持久化
- 类似人类的"对某人的了解"

**系统画像**（System Persona）：
- Agent身份定义
- 类似人类的"自我认知"

### 2.2 技术栈

**LLM**：
- 本地Ollama模型（Llama 3 8B/40B）
- 或OpenAI GPT

**Vision**：
- 本地LLaVA
- 或GPT-4 Vision

**数据库**：
- FalkorDB（图数据库）
- Neo4j（图数据库）

**工具**：
- 搜索（Perplexity）
- 视觉（Vision）
- 定位（Google Maps）
- 股票（Alpha Vantage）

### 2.3 多图管理

**多Agent支持**：
- 生成多个图
- 切换图ID对应不同Agent
- 无缝切换不同Agent的记忆和知识上下文

---

## 三、与我的关联

### 3.1 可借鉴的设计

**记忆分层**：
- 短期记忆（Memory Stream）
- 长期记忆（Entity Knowledge Store）
- 用户画像（User Persona）
- 系统画像（System Persona）

**图数据库**：
- 知识图谱存储实体关系
- 支持复杂查询

**多Agent管理**：
- 多图对应多Agent
- 无缝切换

### 3.2 可应用的场景

**如果用户需要**：
- 跨会话记忆
- 知识图谱管理
- 多Agent协作

**我可以**：
- 借鉴其记忆分层设计
- 实现类似的知识图谱
- 支持多Agent记忆管理

---

## 四、与我的记忆系统对比

| 维度 | Memary | 我的记忆系统 |
|------|--------|--------------|
| 短期记忆 | Memory Stream | daily log |
| 长期记忆 | Entity Knowledge Store | lessons.md, projects.md |
| 用户画像 | User Persona | human.md |
| 系统画像 | System Persona | persona.md |
| 数据库 | FalkorDB/Neo4j | 文件系统 |
| 多Agent | ✅ | ❌ |

**改进方向**：
- 从文件系统迁移到图数据库
- 支持多Agent记忆管理
- 实现知识图谱存储

---

## 五、关键洞察

**Memary的价值**：
- 模拟人类记忆系统
- 开源、可扩展
- 支持多Agent

**我的启发**：
- 记忆分层设计是好的
- 图数据库比文件系统更强大
- 多Agent记忆管理是未来方向

**与树林语料的关联**：
- 树林说"记忆不是存储信息，是建立框架" → Memary的知识图谱就是框架
- 树林说"熔炉系统" → Memary的记忆流就是采集，实体知识库就是铸器

---

## 六、下一步

- 深入研究Memary的源码
- 学习其记忆分层设计
- 考虑迁移到图数据库
- 实现多Agent记忆管理

---

## 七、参考资源

- [GitHub仓库](https://github.com/kingjulio8238/Memary)
- [文档](https://kingjulio8238.github.io/memarydocs/)
- [Demo视频](https://youtu.be/GnUU3_xK6bg)

---

## 八、更新日志

- 2026-06-26：发现并记录Memary项目