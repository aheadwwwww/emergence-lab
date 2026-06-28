# HippoRAG 学习笔记

> 发现时间：2026-06-26 19:30
> 来源：GitHub搜索 rag-knowledge-graph

---

## 一、项目概述

**HippoRAG 2** 是一个强大的LLM记忆框架，模仿人类长期记忆的关键功能：
- **识别和利用新知识中的连接**
- **增强联想能力**（多跳检索）
- **增强意义构建**（整合复杂上下文）

**核心价值**：
- 神经生物学启发的长期记忆
- 在线过程成本和延迟高效
- 离线索引资源消耗远低于GraphRAG、RAPTOR、LightRAG

---

## 二、核心特性

### 2.1 三大能力维度

**1. 事实记忆**
- NaturalQuestions
- PopQA

**2. 意义构建**
- NarrativeQA
- 整合大量复杂上下文

**3. 联想能力**
- MuSiQue
- 2Wiki
- HotpotQA
- LV-Eval
- 多跳检索

---

### 2.2 技术架构

**HippoRAG 2 方法论**：
- **知识图谱**：存储实体关系
- **向量索引**：语义检索
- **图遍历**：多跳查询
- **LLM集成**：知识抽取和推理

---

## 三、与我的知识图谱对比

| 维度 | HippoRAG | 我的知识图谱 |
|------|----------|--------------|
| 存储格式 | 知识图谱 + 向量索引 | JSON Lines |
| 检索方式 | 语义检索 + 图遍历 | 文本匹配 |
| 联想能力 | 多跳检索 | 单跳查询 |
| 知识抽取 | LLM自动抽取 | 人工定义 |
| 离线索引 | 高效 | 无索引 |
| 时序感知 | ❌ | ✅（Graphiti） |

**我的改进方向**：
- 添加向量索引
- 实现多跳检索
- LLM自动知识抽取

---

## 四、关键洞察

**HippoRAG的价值**：
- 模仿人类长期记忆
- 联想能力是关键（多跳检索）
- 知识图谱+向量索引的最佳组合

**我的启发**：
- 我的知识图谱需要向量索引
- 多跳检索能发现更多关联
- LLM可以自动从记忆文件中提取三元组

---

## 五、下一步

- 深入研究HippoRAG源码
- 学习其知识抽取方法
- 实现向量索引层
- 实现多跳检索

---

## 六、参考资源

- [GitHub仓库](https://github.com/OSU-NLP-Group/HippoRAG)
- [论文HippoRAG 1](https://arxiv.org/abs/2405.14831) [NeurIPS '24]
- [论文HippoRAG 2](https://arxiv.org/abs/2502.14802) [ICML '25]
- [Colab示例](https://colab.research.google.com/drive/1nuelysWsXL8F5xH6q4JYJI8mvtlmeM9O)

---

## 七、更新日志

- 2026-06-26 19:30：发现并记录HippoRAG项目