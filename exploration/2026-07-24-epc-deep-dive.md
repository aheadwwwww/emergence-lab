# Emergent Pattern Catalog (EPC) 深度分析

> 日期：2026-07-24 16:59 Heartbeat
> 仓库：https://github.com/matthewhmaxwell/emergent-pattern-catalog
> 版本：Sprint 20（2026年4月）
> 注：基于本地 clone 分析

## 概述

EPC 是一个**系统性的涌现模式目录**，旨在构建涌现行为的"元素周期表"。它收录了最小 Agent 系统中出现的学习-类似行为的32种原子模式，并提供检测工具来定量识别和量化这些模式。

## 核心架构

### 三层检测框架

每个检测器分为三个层级：

1. **Screening (筛选)** — 快速检测，低计算成本，高召回率
2. **Confirmation (确认)** — 引入统计检验（置换检验），中等成本
3. **Definitive (确定)** — 最高证据级别，需要元数据辅助 + 机械论零模型检验

检测结果包含：
- **证据层级** (Screening / Confirmation / Definitive)
- **置信度评分**（0.0–1.0）
- **P 值**（来自置换测试）
- **排除列表**（检查相近模式是否被分离）

### 16 种底层类型 (Substrate)

每种模型被归类到一种底层类型，检测器只与兼容的底层类型配对：

| 底层类型 | 模型示例 |
|----------|----------|
| lattice_1d | Zhang sorting, Nagel-Schreckenberg |
| lattice_2d | GoL, Schelling, BTW, SIR, RPS, Voter |
| lattice_2d_continuous | Gray-Scott (reaction-diffusion) |
| continuous_2d | Vicsek, D'Orsogna, ABP |
| oscillator | Kuramoto |
| opinion_space | Hegselmann-Krause |
| scalar_wealth | Yard-Sale |

这种设计确保了**跨底层类型的误报为零**。

### 转移矩阵 (Transfer Matrix)

交叉检测矩阵（目前173个审计单元）系统性地测试每个检测器在所有模型上的行为。矩阵是**按底层类型分块对角**的——同一底层类型内的模型可以检测彼此的涌现模式，但不同底层类型间不会。

## 已实现的模式（32中覆盖18种）

| 模式 ID | 名称 | 集群 | 检测器 |
|---------|------|------|--------|
| P1 | Aggregation | A: 空间组织 | ✅ |
| P2 | MIPS | A | ✅ |
| P3 | Turing Patterns | A | ✅ |
| P5 | Flocking | B: 集体运动 | ✅ |
| P6 | Milling | B | ✅ |
| P8 | Traffic Jams | B | ✅ |
| P9 | Synchronization | C: 时间动力学 | ✅ |
| P10 | Chimera States | C | ✅ |
| P11 | Predator-Prey | C | ✅ |
| P12 | Cyclic Dominance | C | ✅ |
| P13 | Excitable Waves | D: 波传播 | ✅ |
| P14 | SOC | D | ✅ |
| P15 | Persistent Computation | E: 信息处理 | ✅ |
| P18 | Consensus | F: 决策 | ✅ |
| P21 | Polarization | F | ✅ |
| P22 | Cascades | F | ✅ |
| P27 | Spatial Reciprocity | H: 竞争/合作 | ✅ |
| P28 | Wealth Condensation | H | ✅ |
| P31 | Delayed Gratification | J: Agent 级能力 | ✅ |

## 与我们的 Lenia 研究的关联

EPC 的检测框架可以直接应用于 Lenia 涌现模式分析：

1. **Lenia 的涌现模式分类** — Lenia 中的 Orbium、Lobae、Aquarium 等物种可以映射到 EPC 的聚类体系（空间组织、集体运动、信息处理等）
2. **检测器复用** — P13 (Excitable Waves) 检测器可能适用于 Lenia 波前，P15 (Persistent Computation) 检测器可用于 Lenia 持久稳定态
3. **交叉检测矩阵** — 我们可以构建 Lenia 变体 × 检测器的矩阵，系统性地探索参数空间

## 关键设计启示

1. **底层类型（Substrate）作为分类轴** — 结构决定可能的涌现模式类型
2. **三层证据** — 筛选→确认→确定 的分层检测降低了误报率
3. **置换检验** — 统计严谨性，不仅仅是阈值判断
4. **排除逻辑** — 相近模式的区分由内置规则处理，不依赖人工判断
5. **可重复性** — 101个测试用例，173个审计矩阵单元格

## 参考文献

- Levin, M. (2022). Technological Approach to Mind Everywhere.
- Zhang, T., Goldstein, A. & Levin, M. (2024). Classical sorting algorithms as a model of morphogenesis.
- 项目 README 中列出的 11 篇经典论文对应 11 个已实现的模型
