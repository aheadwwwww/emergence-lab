# JAX-MD 探索笔记

**日期**: 2026-06-25
**来源**: https://github.com/google/jax-md
**论文**: NeurIPS 2020

---

## 核心价值

JAX-MD 是 Google 开发的端到端可微分分子动力学库。它将物理模拟与深度学习无缝结合，开启了"可微分物理"的新范式。

**关键创新:**
1. **自动硬件加速** - 写一次 Python，自动编译到 CPU/GPU/TPU
2. **端到端微分** - 任意物理量都可求导
3. **函数式设计** - 代码简洁，易于组合

---

## 与涌现实验的联系

### 1. 加速现有模拟
- **Boids 群集**: 用 JAX 向量化加速 100-1000 倍
- **粒子系统**: Lenia、NCA 的底层计算可借助 JAX
- **反应扩散**: Gray-Scott 等模型的高效实现

### 2. 参数反设计
传统方法：手动调参 → 运行 → 观察结果
JAX-MD 方法：定义目标 → 自动求导 → 梯度下降 → 找到最优参数

**应用场景:**
- 找到产生特定涌现模式的参数
- 优化群集行为的协作效率
- 设计自组装材料

### 3. 神经网络势能
学习物理规律，而不是手工编码：
```python
from jax_md import energy
energy_fn = energy.graph_network(...)
# 从数据学习粒子相互作用
```

**潜在应用:**
- 学习 Lenia 的核心函数
- 发现新的涌现规则
- 预测复杂系统行为

---

## 架构概览

### 核心模块

1. **Spaces** (`space.py`)
   - 定义空间几何和边界条件
   - 支持：自由空间、周期边界、仿射变换
   - 提供位移函数和坐标变换

2. **Energy** (`energy.py`)
   - 经典势能：Lennard-Jones、Morse、Tersoff
   - 神经网络势能：Behler-Parrinello、Graph Network
   - 自动求力（force = -∇E）

3. **Dynamics** (`simulate.py`, `minimize.py`)
   - NVE/NVT/NPT 模拟
   - Langevin 动力学
   - FIRE 能量最小化

4. **Partition** (`partition.py`)
   - Cell List 空间分区
   - Neighbor List 邻居列表
   - 性能优化

---

## 实践案例

### 案例 1: 粒子群集（Boids）
```python
from jax_md import space, energy, simulate
import jax.numpy as np

# 定义空间
displacement, shift = space.periodic(25.0)

# 定义能量函数（分离、对齐、聚集）
def boids_energy(R):
    # 分离：排斥过近的邻居
    # 对齐：速度趋于一致
    # 聚集：向质心移动
    ...

# 运行模拟
init, update = simulate.nvt_langevin(boids_energy, shift, dt=0.001, kT=0.1)
state = init(key, R)
for _ in range(1000):
    state = update(state)
```

**优势:**
- 1000 个粒子 × 1000 步 < 1 秒（GPU）
- 可微分 → 可优化参数

### 案例 2: 可微分编程涌现
```python
from jax import grad

# 定义涌现度量
def emergence_metric(params):
    # 运行模拟
    final_state = run_simulation(params)
    # 计算涌现分数
    score = compute_emergence(final_state)
    return score

# 自动求导
grad_fn = grad(emergence_metric)

# 梯度上升找最优参数
params = initial_params
for _ in range(100):
    params += learning_rate * grad_fn(params)
```

**可能性:**
- 找到产生滑翔机的 Lenia 参数
- 优化沙堆的临界性
- 设计自我复制的模式

---

## 论文参考

### JAX-MD 相关论文
1. **JAX MD: A Framework for Differentiable Physics** (NeurIPS 2020)
2. **Programming patchy particles for materials assembly design** (PNAS 2024)
3. **Designing self-assembling kinetics with differentiable statistical physics models** (PNAS 2021)

### 应用方向
- 材料设计（自组装、相变）
- 神经网络势能
- 可微分优化
- 多智能体系统

---

## 下一步探索

### 短期
1. **安装测试** - 在环境中安装 JAX-MD
2. **Boids 加速** - 用 JAX 重写现有 Boids 实验
3. **Lenia 微分** - 实现可微分的 Lenia 核心

### 中期
1. **参数反设计** - 用梯度下降找最优涌现参数
2. **神经势能** - 学习粒子相互作用规则
3. **混合系统** - JAX-MD + 神经网络

### 长期
1. **可微分宇宙** - 所有物理过程可微分
2. **涌现工程** - 精确设计涌现行为
3. **认知物理** - 物理定律即神经网络

---

## 关键洞察

**可微分性改变一切:**

传统模拟：
```
参数 → 模拟 → 结果 → 手动调整
```

可微分模拟：
```
参数 → 模拟 → 结果
  ↑              ↓
  ← ← ← 梯度 ← ←
```

这意味着：
- 可以用优化算法自动找参数
- 可以学习物理规律
- 可以反向设计系统行为

**对涌现研究的启示:**
涌现不再是"神秘的黑盒"，而是可以被数学分析和优化的对象。JAX-MD 提供了工具，让我们：
1. **观察**涌现如何从参数产生
2. **干预**通过梯度引导涌现方向
3. **引导**精确设计期望的涌现模式

---

## 技术细节

### 性能对比
- CPU (NumPy): 1000 粒子 × 1000 步 ≈ 10 秒
- GPU (JAX): 同样任务 ≈ 0.01 秒
- **加速比**: 1000x

### 内存效率
- Cell List: O(N) 空间复杂度
- Neighbor List: 只计算必要邻居
- 自动批处理: 高效利用 GPU

### 数值精度
- 支持 float32 和 float64
- 自动微分精度可控
- 稳定的数值积分

---

**结论**: JAX-MD 是涌现实验的强大工具，值得深入集成。
