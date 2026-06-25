# 异步 Lenia 实验 — 2026-06-25

## 背景

从 NCA (Neural Cellular Automata) 学到异步更新机制——每步只有 50% 的细胞更新。NCA 用这个机制提升鲁棒性，容忍局部错误。

尝试把异步更新引入 Lenia，测试效果。

## 方法

- R=20, μ=0.14, σ=0.024（最佳参数）
- fire_rate: 0.5 → 1.0
- 200 步，256×256 网格

## 结果

| fire_rate | 状态 | alive |
|-----------|------|-------|
| 0.50 | simple | **0.602** |
| 0.60 | simple | 0.527 |
| 0.70 | structure | 0.445 |
| 0.80 | structure | 0.367 |
| 0.90 | structure | 0.284 |
| 0.95 | structure | 0.247 |
| 1.00 | structure | 0.209 |

## 发现

### 1. 异步更新在 Lenia 中效果相反
- NCA：异步提升鲁棒性
- Lenia：异步降低结构稳定性

### 2. fire_rate 的临界点
- fire_rate < 0.7：simple 模式（无结构）
- fire_rate ≥ 0.7：structure 模式
- 临界点在 0.7，不是 0.5

### 3. alive vs structure 的悖论
- fire_rate=0.50 的 alive 最高（0.602），但标记为 simple
- 说明：异步让更多细胞"存活"，但失去协调性 → 随机波动

### 4. Lenia 需要更强的同步
- 核半径 R=20 覆盖大区域
- 需要全局协调维持结构
- 异步破坏这种协调

## 对比 NCA vs Lenia

| 维度 | NCA | Lenia |
|------|-----|-------|
| 感知范围 | Sobel（3×3邻居） | FFT核（R=20 ≈ 40×40） |
| 异步效果 | 提升鲁棒性 | 降低结构稳定性 |
| 临界 fire_rate | ~0.5 | ~0.7 |
| 协调需求 | 局部（邻居） | 全局（大核） |

## 结论

**异步更新不是万能机制**——它对不同的 CA 系统有不同效果：

- **小感知范围**（NCA）：异步有效，提升鲁棒性
- **大感知范围**（Lenia）：异步有害，破坏协调

Lenia 的结构依赖于全局同步，异步会让它退化为随机波动。

## 代码

- `experiments/lenia_async.py` — 异步 Lenia 实现
- `experiments/lenia_async_fire_rate_sweep.json` — 参数扫描结果