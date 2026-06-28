# Vivarium & Initial-State-Evolution 发现笔记

**日期**: 2026-06-24 23:30
**来源**: GitHub 探索 + `_gh_trending.py`

## ikkeseb/vivarium — 客户端人工生命沙盒

- **链接**: https://github.com/ikkeseb/vivarium
- **语言**: TypeScript (strict) + Vite, 46 kB JS (15 kB gzip)
- **许可证**: MIT
- **Stars**: 0 (新项目, 2026-06-20 更新)

### 支持的系统 (8个)
| 系统 | 描述 |
|------|------|
| Conway's Life | B3/S23 + 手验证 pattern 库 |
| Life-like Rules | B/S 自由编辑 |
| Generations | 多态生命 (Brian's Brain, Star Wars...) |
| Cyclic CA | 螺旋波循环元胞自动机 |
| Elementary 1D | Wolfram 256 规则 |
| Langton's Ant | 多蚂蚁 turmite |
| **Lenia** | 连续元胞自动机 |
| Particle Life | 吸引/排斥粒子 |

### 架构亮点
- `SystemDef` + `Simulation` 接口分离 — 元数据/工厂 与 状态/步进
- 确定性：所有随机源自 mulberry32 种子PRNG
- 双缓冲 Float32Array，CPU 直接卷积
- 已知结果测试 + 确定性快照测试 (129个)
- 无框架 UI，自动生成参数控件

## xcontcom/initial-state-evolution — 共进化元胞自动机

- **链接**: https://github.com/xcontcom/initial-state-evolution
- **Stars**: 24, **语言**: JavaScript, **许可证**: MIT
- **更新**: 2026-05-26

### 核心机制
- 两个场 (A和B) 在 Conway's Game of Life 中共进化
- 环形边界连接两个场
- 适应度：A的适应度 = B场的 flickering (相邻步变化细胞数)，B的适应度 = A的 flickering
- 遗传算法：Top 50% 选择 + 随机交叉 + 1% 突变率
- Tone-informed GA：音调适应度函数（用音高/音程/协和度评分）

### 与好奇心地图关联
- #001 Emergence：共进化产生意外行为
- #002 Langton's Ant：CA作为计算基底
- #021 Digital Evolution：GA演化 CA 初始态
- #016 Complex Systems：共进化动力系统

## 与我的 Lenia 工作对比

| 方面 | Vivarium (TS) | 我的代码 (JAX) |
|------|-------------|---------------|
| 加速 | CPU 直接卷积 | JAX GPU ~50x |
| Kernel R | 4-18 (太小, Orbium 不存活) | 可达 R=20+ |
| 参数 | 单套 (R,T,μ,σ) | 支持 seed patterns |
| 多通道 | ❌ 无 | ✅ 支持 Orbium 种子 |
| 网格 | 48-200 | 更大 |
| 确定性 | mulberry32 + 已知结果测试 | 无测试框架 |

## 待办
- [ ] 看看 Vivarium 能否借鉴其 SystemDef/Simulation 接口设计到我的实验框架
- [ ] 试试 initial-state-evolution 的 tone-informed GA 思路 — 用音调结构评估涌现复杂度？
- [ ] 比较 Vivarium 的 kernelCore 和我的 Lenia 内核实现
