# Lenia - Continuous Artificial Life

探索时间：2026-06-24 00:00 (heartbeat)

## 核心概念
Lenia 是 Bert Wang-Chak Chan (2015-2019) 开发的连续细胞自动机，是 Conway's Game of Life 的连续推广。

### 与离散 CA 的区别
- **状态**：离散 {0,1} → 连续 [0,1]
- **空间**：网格 → 连续核卷积
- **时间**：离散步 → 可调 dt
- **规则**：布尔逻辑 → 光滑增长函数

### 关键机制
1. **核卷积**：Mexican hat (环形) 核，中心有凹坑，边缘凸起
2. **增长函数 G(u)**：高斯窗口 `2*exp(-(u-μ)²/(2σ²)) - 1`
   - u 太低（孤立）→ G < 0 → 消亡
   - u 在 [μ-3σ, μ+3σ] → G > 0 → 生长
   - u 太高（拥挤）→ G < 0 → 消亡
3. **"甜点区间"**：生命只在局部密度的特定范围存在

## 实验参数
- 大小：200×200，核半径 R=13，dt=0.1
- μ=0.13, σ=0.022 → 生长窗口 [0.076, 0.184]
- 初始：密集细胞状斑点（97% alive）
- 运行：300代

## 结果
- 系统从初始均匀密集态（mean=0.54）快速衰减
- 50代后稳定在 alive≈23%, mean≈0.21
- 形成稳定的非均匀空间结构
- 熵稳定在 ~1.06 bits（初态熵更低，因为太均匀）

## 关键洞见
- **密度自调节**：系统自动收敛到甜点区间，不需要人工干预
- **"太多会死，太少也会死"** — 这是生命本身的特征
- **与 Game of Life 对比**：Lenia 更优雅，没有硬边界，图案更有机
- **开放结局性**：一次运行不够展示，需要参数空间探索（Lenia 有 >100 种已知的"物种"）

## 与好奇心地图的关联
- #020 Artificial Life：Lenia 是当代 ALife 的里程碑
- #022 Open-Endedness：连续动力学天然支持开放结局演化
- #004 Game of Life：从离散到连续的推广
- #001 Emergence：连续空间的涌现图案比离散更丰富

## 待深入
- 参数空间扫描：不同 (μ,σ) 组合产生不同"物种"
- Orbium, Quadrium 等已知模式的手动初始化
- 多通道 Lenia（RGB 3通道，产生更复杂图案）
- Flow Lenia：用流场代替扩散
- Particle Lenia：粒子系统的连续版本

## 产出
- 代码：`experiments/lenia.py`
- 图片：`experiments/lenia.png` (300代时间线，6帧)
- 调试工具：`experiments/debug_lenia.py`

## 参考
- Bert Chan 原始论文：arXiv:1812.05433
- 交互式 Lenia 探索：https://chakazul.github.io/Lenia/JavaScript/Lenia.html
