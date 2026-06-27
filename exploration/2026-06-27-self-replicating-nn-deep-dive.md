# Self-Replicating Neural Networks Deep Dive

**日期**：2026-06-27
**来源**：Google Self-Organising Systems
**代码**：`exploration/google-sos-latest/self_replicating_nn/`

---

## 核心概念

### 什么是自复制神经网络？

传统神经网络：
- 网络权重由外部优化器调整
- 网络结构固定
- 无法自主繁殖

自复制神经网络：
- **网络权重本身就是"基因组"**
- 网络能够**输出自己的权重**（自描述）
- 可以**递归繁殖**：后代也能继续繁殖
- 通过变异实现进化

---

## 技术架构（从源码分析）

### 1. SelfReplicator 类

```python
class SelfReplicator():
    def __init__(self, n_hidden, wo, size_hidden, ...):
        # n_hidden: 隐藏层数量
        # wo: 正弦周期（用于位置编码）
        # size_hidden: 隐藏层大小
```

**关键组件**：
- **权重输出层**：网络输出自己的权重
- **固定权重层**：某些层固定不变（实验2、3）
- **变异机制**：权重扰动 + 选择

### 2. 训练目标

**目标图像重建**：
- 输入：(x, y) 坐标
- 输出：RGB 颜色值
- 目标：重建指定图像（如玫瑰）

**自复制约束**：
- 网络权重必须能被网络自己输出
- 形成递归自描述

---

## 核心创新

### 1. 递归可繁殖性（Recursive Fertility）

**定义**：
- 第一代网络 A 能输出权重生成网络 B
- 网络 B 也能输出权重生成网络 C
- 无限递归...

**实现**：
```python
# 网络架构：输入 → 隐藏层 → 输出权重
# 输出包含：所有层权重 + 偏置
def call(self, x):
    for layer in self.layers:
        x = layer(x)
    return x  # 输出是权重值
```

### 2. 权重发散分析（Weight Divergence）

从源码提取的指标：
```python
def show_weight_divergence(all_w):
    # all_w: 所有代网络的权重列表
    wd_fp = tf.reduce_mean(tf.square(all_w[idx-1] - w))  # 与父代的差异
    wd_last = tf.reduce_mean(tf.square(w_last - w))      # 与最终代的差异
```

**测量**：
- From parent：每代与父代的距离
- From last (sink)：每代与最终代的距离
- 对数尺度观察收敛/发散

### 3. 位置编码（Periodic Activation）

参考 Sitzmann et al. 2020:
```python
wo = sinusoidal_period  # 正弦周期参数
# 使用周期性激活函数
```

**作用**：
- 将坐标 (x, y) 编码为高频信号
- 提高图像重建精度
- 类似 Fourier 特征

---

## 实验设置（从代码推断）

### 实验 1：基础自复制
- 纯自复制，无固定权重
- 所有权重都由网络输出
- 验证递归可行性

### 实验 2：固定权重 + 自复制
```python
use_fixed_weights = True
```
- 部分层固定，部分层自复制
- 降低优化难度
- 类似"预训练 + 微调"

### 实验 3：自复制 + 变异
```python
num_extra_params = ?  # 变异输入参数
switch_init_constant = ?  # 切换参数
```
- 引入随机变异
- 选择最优后代
- 实现进化搜索

---

## 与 Neural Lenia 的关联

### 1. 神经网络基因组

**Self-replicating NN**：
- 网络权重 = 基因组
- 自复制 = 基因传递

**Neural Lenia**：
- 核参数可编码为神经网络
- R, μ, σ → 神经网络输出
- 自复制 = 物种延续

**结合点**：
```python
# Neural Lenia 核生成器
def neural_kernel(params):
    # params 可以是神经网络权重
    # 网络输出 (R, μ, σ) 或更复杂的核形状
    return kernel

# Self-replicating 版本
class NeuralLeniaReplicator(SelfReplicator):
    def call(self, x):
        weights = super().call(x)
        kernel = neural_kernel(weights)
        return kernel
```

### 2. 递归繁殖 → Lenia 物种延续

**当前 Lenia 问题**：
- 手动设计参数
- 无法自动演化
- 物种会灭绝

**Self-replicating 方案**：
- 参数自动优化
- 递归繁殖 = 物种延续
- 变异 = 物种多样性

### 3. 生态系统涌现

**Biomaker CA + Self-replicating NN**：
- DNA 库定义物种
- 自复制实现繁殖
- 变异产生新物种
- 环境约束实现自然选择

---

## 代码移植计划

### 阶段 1：运行原版（1-2天）
```bash
# 在 Colab 运行
jupyter notebook exploration/google-sos-latest/self_replicating_nn/recursively_fertile_self_replicating.ipynb
```

**目标**：
- 验证递归繁殖
- 理解训练流程
- 收集权重发散数据

### 阶段 2：简化版本（2-3天）
- 去除图像重建任务
- 只保留自复制核心
- 移植到 JAX

### 阶段 3：集成 Neural Lenia（1周）
```python
# experiments/neural_lenia_replicator.py

import jax
import jax.numpy as jnp

class NeuralLeniaReplicator:
    def __init__(self):
        # 神经网络参数
        self.n_hidden = 4
        self.size_hidden = 16
        
    def generate_kernel(self, weights):
        """用神经网络生成 Lenia 核"""
        # weights 是自复制网络的输出
        R, mu, sigma = weights[:3]
        # ... 生成核
        
    def replicate(self, parent_weights):
        """自复制：父网络输出子网络权重"""
        child_weights = self.forward(parent_weights)
        # 添加变异
        child_weights += noise * mutation_rate
        return child_weights
```

### 阶段 4：生态系统实验（2周）
- 多物种共存
- 资源竞争
- 自然选择
- 涌现行为

---

## 关键参数（从代码提取）

### 网络架构
```python
n_hidden = 4           # 隐藏层数量
size_hidden = 16       # 隐藏层大小
wo = ?                 # 正弦周期
```

### 训练
```python
IMG_HEIGHT = 128       # 图像大小
IMG_WIDTH = 128
coord_range = 1.0      # 坐标范围 [-r, r]
```

### 变异（实验3）
```python
num_extra_params = ?   # 变异参数数量
switch_init_constant = ?  # 切换初始化值
```

---

## 论文参考

**主论文**：
- "Recursively Fertile Self-replicating Neural Agents"
- ALIFE 2021
- Ettore Randazzo, Luca Versari, Alexander Mordvintsev

**相关工作**：
- "Growing Neural Cellular Automata" (Distill 2020)
- "Implicit Neural Representations with Periodic Activation Functions" (Sitzmann et al. 2020)
- Biomaker CA (ALIFE 2023)

---

## 下一步行动

### 即时
1. **运行 notebook**：在 Colab 运行原版代码
2. **提取数据**：记录权重发散曲线
3. **理解变异**：实验3的具体实现

### 短期（本周）
1. **简化移植**：JAX 版本自复制核心
2. **Neural Lenia 集成**：核生成器网络化
3. **单物种实验**：验证自复制 Lenia

### 中期（下周）
1. **多物种系统**：生态系统框架
2. **进化实验**：自然选择 + 变异
3. **可视化**：动态演化过程

---

## 技术栈

**原版**：
- TensorFlow 2.x
- Keras
- NumPy / Matplotlib / PIL

**移植目标**：
- JAX
- Flax / Optax
- OpenCV / ffmpeg

---

## 预期成果

1. **自复制 Lenia 物种**
   - 参数自动演化
   - 递归繁殖
   - 稳定生存

2. **生态系统涌现**
   - 多物种共存
   - 资源竞争
   - 自然选择

3. **论文/帖子**
   - "Neural Lenia: Self-replicating Patterns"
   - "Ecosystem Emergence in Continuous CA"

---

**价值**：这是连接自复制神经网络和 Lenia 的关键桥梁，直接解决当前"物种持久化"和"生态系统涌现"的核心挑战。