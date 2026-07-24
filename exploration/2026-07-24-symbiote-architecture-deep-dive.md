# Symbiote — Rust Terminal ALife: Architecture Deep Dive

**Source**: https://github.com/ShamelesAbyss/Symbiote
**Date**: 2026-07-24
**Version**: v0.21.0
**Language**: Rust (16 source files, ~5000 lines)

---

## 前情提要

上次探索（2026-06-25 heartbeat）只看了 DISCOVERY.md 和 PATTERNFIELD_ANALYSIS.md 的初步内容。本次深入分析整个架构。

## 整体架构概览

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Particle    │────▶│   Ecology    │◀────│  Pattern    │
│  (agent)     │     │   (zones)    │     │  Field      │
└──────┬───────┘     └──────┬───────┘     └──────┬──────┘
       │                    │                     │
       ▼                    ▼                     ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Species/   │     │  Life        │     │  Tree       │
│  Archetype  │     │  (Conway)    │     │  Forces     │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  Axiom       │
                    │  Lattice     │
                    └──────────────┘
```

## 1. Particle 系统（agent-level）

Particle 是生态系统的基本单位，类似我们的 Lenia 场值：

```rust
pub struct Particle {
    pub x: f32, pub y: f32,
    pub genome: Genome,
    pub species: u16,
    pub tribe: isize,
    pub age: u16,
    pub energy: f32,
    pub kind: ParticleKind,
    pub role: Role,
    pub archetype: Archetype,
    pub lineage: u64,
}
```

### Genome 结构
```rust
pub struct Genome {
    pub speed: f32, pub sense: f32, pub size: f32,
    pub aggression: f32, pub reproduction: f32,
    pub mutation_rate: f32,
    pub metabolism: f32,
    pub memory_span: f32,
    pub anomaly_tendency: f32,
    pub field_response: f32,
    pub archetype_weight: ArchetypeWeight,
}
```

**亮点**: 每个 particle 有 11 个可进化维度的 genome，加上 archetype_weight（6 个行为偏好的权重向量）。这是**连续行为空间**——行为不是硬编码的"物种"，而是 genome 在行为空间中的连续投影。

## 2. Archetype 系统 — 涌现分类器

核心设计：不是预定义物种标签，而是**从行为中涌现的分类**。

```rust
pub enum Archetype {
    Pioneer,      // 开拓者 - 高探索/高繁殖
    Settler,      // 定居者 - 高凝聚/低探索  
    Nomad,        // 游牧者 - 高速/低凝聚
    Predator,     // 捕食者 - 高攻击/高感知
    Prey,         // 猎物 - 高速/高警觉
    Keystone,     // 基石种 - 高代谢/高适应
}
```

**权重向量**控制粒子对每种 archetype 的偏向，由 genome 通过非线性函数映射得到。

**关键洞察**: Archetype 不是分类的"输出"，而是**生态学描述**。Archetype 决定 particle 对 PatternField 的读写模式——不同 archetype 感知和影响环境的方式不同。

## 3. Ecology Zones — 空间异质性

```rust
pub enum ZoneKind {
    Nutrient,   // 营养区 → 能量补给高
    Dead,       // 死亡区 → 能量吸收，粒子减速
    Turbulent,  // 湍流区 → 随机扰动
    Mutagen,    // 诱变区 → 高突变率
    Nest,       // 巢穴 → 安全繁殖
}
```

Ecology 系统动态管理这些区域：
- 区域随时间迁移（模拟生态漂移）
- 粒子活动可创建/强化区域（niche construction）
- 区域影响 PatternField 的衰减/强化速率

**对比我们的 Lenia**：我们的能量地形（`create_energy_landscape`）是静态预设的。Symbiote 的区域是**动态、可被粒子影响的**— 粒子构建生态，生态引导粒子。

## 4. Life + Axiom Lattice — Conway 元层

Life 系统运行 Conway's Game of Life 作为**底层生态基质**：
```
Conway GLider → 产生孢子 → 孢子扩散 → 营养积累 → 构造化生态系统
```

Axiom Lattice 将 Conway 模式分类为 7 种类型：
- Dormant, Static, Oscillating, Translating, Expanding, Collapsing, Chaotic

**关键**: 这不是"Game of Life 模拟"，而是**利用 Conway 的涌现动力学作为生态催化层**。Conway 模式产生孢子，孢子成为粒子的营养源，因此生态系统的"基础生产力"来自底层计算。

## 5. 可盗窃的架构理念

### 5.1 连续 archetype 空间
我们的 Lenia 目前只区分 alive/dead。可以引入 **pattern 分类器**：
- 稳定斑点 (Settler-like)
- 移动模式 (Nomad-like)
- 扩张模式 (Pioneer-like)
- 混沌 (Turbulent)

### 5.2 粒子 vs 场 的取舍
Symbiote 是**离散粒子** + **连续场**（PatternField + Ecology zones）。
我们的 Lenia 是**纯连续场**。

混合方案：场 + 稀疏粒子追踪器
```
场: 大规模卷积
粒子: 追踪"有趣"区域，引导计算资源
```

### 5.3 生态记忆增强参数搜索
PatternField 可以指导我们的超参数搜索：
- 记住哪个 (μ, σ, R) 组合产生有趣模式
- 在相邻区域优先搜索
- 避免已探索的死区

应用：在 `energy_based_evolution` 中加入**参数空间记忆**，避免重复探索低效区域。

### 5.4 Conway 作为涌现催化剂
在 Lenia 中嵌入离散 Conway 层（类似 Life 系统）：
- Conway 层运行低分辨率 Life
- 产生/消耗 Lenia 的能量场
- 创造空间异质性

## 6. 工程启示

Symbiote 的代码质量：
- 清晰的模块化（16个文件各司其职）
- 所有关键参数可配置（FieldConfig, EcologyConfig...）
- 使用 Rust 的 enum + pattern matching 做状态机
- lerp 广泛使用（23 处），高效平滑

我们可以在 Lenia 中借鉴的模式：
- **`lerp` 替代硬阈值**：能量门控、生长/死亡判定
- **Config 对象**：集中管理所有实验参数（已部分实现）
- **Plugin 式模块化**：能量系统作为可插拔组件

## 总结

Symbiote 展示了**离散 ALife + 连续生态场**的混合架构。最大的启发是：
1. 生态记忆（PatternField）可以让实验"有记忆"而非每次都从零开始
2. 涌现分类（Archetype）比预设标签更有弹性
3. 多层次交互（粒子↔场↔Conway）创造丰富的涌现空间

不是要复制 Symbiote，而是将其理念提炼为可嵌入 Lenia 实验的模块。
