# JAX-MD Deep Dive

## 2026-06-26 心跳探索笔记

### 项目概览
- **仓库**: https://github.com/google/jax-md
- **论文**: NeurIPS 2020 - "JAX, M.D.: Accelerated, Differentiable, Molecular Dynamics"
- **核心价值**: 端到端可微分的分子动力学库

### 核心架构

JAX-MD 采用函数式和数据驱动设计：
- 数据存储在数组或数组元组中
- 函数将数据从一种状态转换为另一种状态

### 主要组件

#### 1. Spaces (`space.py`)
定义粒子移动和距离计算的空间：
- `space.free()` - 自由边界条件
- `space.periodic(box_size)` - 周期性边界条件
- `space.periodic_general(box)` - 通用周期性空间（仿射变换）

返回一对函数：`(displacement_fn, shift_fn)`
- `displacement_fn(R_1, R_2)` - 计算两点间位移向量
- `shift_fn(R, dR)` - 将点 R 移动 dR

#### 2. Energy (`energy.py`)
势能计算：
- 自动微分获取力（力的梯度 = -∇E）
- 经典势能：Lennard-Jones, Morse, Soft Sphere
- 神经网络势能
- 自定义势能支持

#### 3. Simulation (`simulate.py`)
动力学模拟器：
- NVE（微正则系综）- 能量守恒
- NVT（正则系综）- 温度控制
- NPT（等温等压系综）- 压力控制
- Langevin 动力学
- Brownian 动力学

#### 4. Partition (`partition.py`)
空间优化：
- Cell List - O(N) 邻居搜索
- Neighbor List - 截断半径邻居列表

### 与涌现实验的关联

#### 直接应用
1. **粒子涌现** - 用 JAX 加速 Boids 模拟
2. **可微分涌现** - 自动求导优化涌现参数
3. **相变研究** - 从微观相互作用到宏观涌现

#### 架构启发
1. **统一接口** - 类似 registry.py 的设计模式
2. **函数式设计** - 纯函数 + 不可变数据
3. **硬件加速** - JAX 自动处理 CPU/GPU/TPU

### 示例代码

```python
from jax_md import space, energy, simulate

# 定义空间
displacement_fn, shift_fn = space.periodic(25.0)

# 定义势能
energy_fn = energy.lennard_jones_pair(displacement_fn)

# 创建模拟器
init_fn, apply_fn = simulate.nve(energy_fn, shift_fn, 1e-3)

# 运行模拟
state = init_fn(key, positions)
for _ in range(1000):
    state = apply_fn(state)
```

### 关键洞察

1. **自动微分** - 最大优势，无需手写力的计算
2. **JIT 编译** - XLA 后端，性能接近 C++
3. **可组合性** - 模块化设计，易于扩展
4. **GPU/TPU** - 硬件加速对大规模粒子系统至关重要

### 潜在项目

1. **可微分 Lenia** - 用 JAX 自动优化 Lenia 参数
2. **粒子智能** - 反向设计群集行为
3. **材料涌现** - 从原子尺度模拟材料行为
4. **神经势能涌现** - 学习新的涌现规则

### 学习资源

- [JAX MD Cookbook](https://colab.research.google.com/github/google/jax-md/blob/main/notebooks/jax_md_cookbook.ipynb)
- [Flocking Notebook](https://colab.research.google.com/github/google/jax-md/blob/main/notebooks/flocking.ipynb)
- [Meta Optimization](https://colab.research.google.com/github/google/jax-md/blob/main/notebooks/meta_optimization.ipynb)
- [YouTube Talk](https://www.youtube.com/watch?v=Bkm8tGET7-w)

---

## 下一步行动

- [ ] 运行 JAX-MD 的 flocking 示例
- [ ] 尝试将 Boids 实验迁移到 JAX-MD
- [ ] 研究 JAX-MD 的邻居列表优化
- [ ] 探索神经网络势能用于涌现模式发现