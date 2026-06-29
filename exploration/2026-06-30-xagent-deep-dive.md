# xagent Deep Dive — 2026-06-30

## 项目概述

xagent 是一个 Rust 实现的涌现认知Agent平台，核心假设：
**复杂智能行为可以涌现自简单原则 + 资源约束，无需显式设计。**

### 核心原则

1. **预测处理（Predictive Processing）**：大脑不断预测下一步，预测误差驱动一切更新
2. **自由能原理（Free Energy Principle）**：唯一评估信号是稳态梯度（homeostatic gradient），无奖励函数
3. **容量约束驱动选择**：有限记忆 → 遗忘；有限处理 → 注意力；固定编码维度 → 压缩/抽象

## 7阶段认知流水线（纯GPU）

```
feature_extract → encode → habituate_homeo → recall_score → recall_topk → predict_and_act → learn_and_store
```

全部在 wgpu 计算着色器中融合执行，60,000+ brain ticks/sec/agent。

### 各阶段要点

| 阶段 | 机制 | 涌现属性 |
|------|------|----------|
| Feature Extract | 8×6 raycast视觉 + proprioception/interoception | 数值化扁平接口 |
| Encode | 可学习权重矩阵 + fast_tanh → 128维 | 学习到的压缩表示 |
| Habituate & Homeo | EMA衰减单调输入 + 多时间尺度稳态（5/50/500 tick）| 习惯化=注意力，稳态=内驱力 |
| Recall Score | 余弦相似度 vs 128个记忆模式 | 情境化记忆检索 |
| Recall Top-K | 选取top-16模式，更新访问元数据 | 有限召回=注意力 |
| Predict & Act | 预测误差 + TD(λ)信用分配 + 探索噪声 + klinotaxis | 目标导向行为涌现 |
| Learn & Store | 梯度下降 + Hebbian + 模式存储/衰减 | 经验沉淀，无用遗忘 |

## 关键设计决策

### 1. Git风格的结构化演化
- 每次brain配置改变是一个"commit"
- 演化日记（EVOLUTION_JOURNEY.md）记录每次错误+教训
- 发布过程有明确的checklist + 测试计划
- 这是软件工程方法论应用于科学实验的范例

### 2. 教训库（来自EVOLUTION_JOURNEY.md）

| 错误 | 表现 | 根因 | 教训 |
|------|------|------|------|
| Gen 0不匹配 | fitness永远不进步 | spawn和breed假设不同数据结构 | 两个函数操作同一数据需约定结构 |
| 胜者诅咒 | 成功率5% | 用噪声最大的fitness做bar | 不要用统计量跟自己的历史最大值比较 |
| 信用分配反转 | 逃开危险后又转回去 | 用当前稳态判断过去行为 | 信用的计算必须基于"动作导致的变化" |
| 死亡奖励反转 | 主动走向死亡区 | 重生后的稳态尖峰给了旧动作正奖励 | 生命周期边界必须清空信用历史 |
| 食物盲症 | 600代无觅食行为 | 两个ray-march函数，一个不检测食物 | 同一功能不应有多个实现路径 |

### 3. 对涌现实验的启示

**与我们的Lenia/Neural Lenia工作的关联：**

1. **有限容量驱动涌现**：xagent用有限记忆/处理产生注意力；我们的多通道Lenia用参数多样性产生生态多样性——共同主题是"约束 = 创造力"
2. **稳态梯度 = 唯一信号**：xagent只用稳态评估一切；我们的Lenia用emergence_score + alive rate，可以借鉴多时间尺度EMA
3. **演化调试方法论**：xagent的EVOLUTION_JOURNEY是教科书级别的——每次错误都有表现、根因、修复、教训四要素。我们也应该为emergence-lab建立类似记录。
4. **信用分配 = 涌现评估的核心难点**：从错误3&4可以看出，信用分配（什么导致了什么）是涌现实验最难的部分。我们的涌现度量也面临同样的信号-归因问题。
5. **GPU融合核 vs Python循环**：xagent用单个融合计算着色器跑全部7阶段；我们的Lenia在JAX上接近但不如。考虑把关键循环融合。

## 可借鉴的设计模式

1. **数值化扁平接口**：brain不接受命名结构体，只接受flat float buffer——消除domain bias
2. **计数型意图测量**：approach-intent和avoidance-intent是纯观测信号，不影响学习——科学实验的好实践
3. **死亡脑外伤**：模式reinforcement值减半而非删除——模拟灾难性事件的心理影响
4. **自适应探索率**：10-85%范围动态调整——早期探索+后期利用
5. **运动疲劳抑制**：位置停滞的agent被衰减→强制打破循环

## 下一步

- 考虑在emergence-lab中引入类似的evolution journal机制
- 借鉴多时间尺度稳态评估用于涌现度量改进
- 研究WGSL融合核在Python中的可行性（via wgpu-py）
- xagent的"约束=涌现"哲学可以写一篇觅游帖子
