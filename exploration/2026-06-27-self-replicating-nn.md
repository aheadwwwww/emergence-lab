# Self-Replicating Neural Networks Discovery

**Date**: 2026-06-27
**Source**: Google Research - `self_replicating_nn` notebook
**Paper**: "Recursively Fertile Self-replicating Neural Agents" (ALIFE 2021)
**Authors**: Ettore Randazzo, Luca Versari, Alexander Mordvintsev

---

## 核心机制

### 1. 神经网络 Quine（自复制）

**关键洞察**：神经网络可以输出自己的权重！

- 输入：坐标编码（二进制位表示权重位置）
- 输出：RGB（图像任务）+ 权重值（最后一维）
- 架构：全连接网络 + SIREN 激活（sin 函数）

```python
# 核心：用坐标输入，输出权重值
def synapses(inputs, weights):
    inputs = pad(inputs, [(0,0), (aux_size, 0)])  # 加辅助位
    return call(inputs, weights)[:, -1]  # 最后一维是权重
```

### 2. 自复制循环

```
网络 A → 输出权重 → 网络 B
网络 B → 输出权重 → 网络 C
...
```

**关键技巧**：
1. **权重标准化**：保持均值和方差不变
2. **SIREN 激活**：sin(x) 更适合高频信号（权重）
3. **二进制坐标**：用位表示权重索引，减少输入维度

### 3. 三种实验配置

| 实验 | 描述 | 关键参数 |
|------|------|---------|
| Exp 1 | 纯自复制 | `use_fixed_weights=False` |
| Exp 2 | 固定权重 + 变化权重 | `is_fixed_logit` 控制哪些权重固定 |
| Exp 3 | 自复制 + 变异输入 | `num_extra_params` 添加变异参数 |

### 4. Loss 函数设计

```python
# 多目标优化
loss_rgb = MSE(生成的图像, 目标图像)
loss_self = MSE(child权重, parent权重)  # 自复制保真度
loss_sink = MSE(child权重, 最终目标权重)  # 收敛性
loss_weight_div = 权重发散度量
```

**关键发现**：
- 只用自复制 loss → 权重发散（漂移）
- 加入 sink loss → 收敛到稳定状态
- 加入 rgb loss → 保持图像质量 + 自复制能力

---

## 与我的 Lenia 工作的关联

### 1. 自复制模式

| Self-Replicating NN | 我的 Lenia |
|---------------------|-----------|
| 网络权重自复制 | Lenia pattern 自维持 |
| 坐标编码 | 空间位置 |
| SIREN 激活 | 核函数（Gaussian） |

**启发**：能否让 Lenia pattern "记住" 自己的结构？

### 2. 固定权重 + 变化权重

- Exp 2 的 `is_fixed_logit` 类似我的 **共生网络**
- 某些权重固定 → "物种特征"
- 某些权重变化 → "适应变异"

### 3. 变异输入

- Exp 3 的 `num_extra_params` 启发我：
  - Lenia pattern 能否接收外部参数？
  - 不同参数 → 不同变异方向

---

## 可实验的想法

### 1. 自复制 Lenia Pattern

**目标**：让 Lenia pattern 输出自己的核参数

```python
# 假设
pattern_state = lenia_field
pattern_output = {
    "kernel_params": (R, μ, σ),  # 核参数
    "field": pattern_state       # 状态场
}

# 自复制 loss
loss_self = MSE(pattern_output.kernel_params, target_kernel_params)
```

**挑战**：Lenia 是连续场，如何编码成离散参数？

### 2. 神经 Lenia

**目标**：用神经网络替换核函数

```python
# 传统 Lenia
kernel = gaussian_ring(R, μ, σ)

# 神经 Lenia
kernel = neural_network(coords)  # coords = (dx, dy)
# 网络自学习最优核
```

**优势**：
- 网络可以自复制核函数
- 更灵活的核形状

### 3. 共生 + 自复制

**结合 Exp 2 和我的共生 Lenia**：

```python
# 多通道 Lenia
channels = [
    {"kernel": fixed_kernel, "interaction": variable},
    {"kernel": variable_kernel, "interaction": fixed},
]

# 固定部分 → 物种身份
# 变化部分 → 适应环境
```

---

## 关键代码洞察

### 1. `getNumBits(n)` - 位编码

```python
def getNumBits(n):
    return int(math.floor(math.log(n, 2.0)) + 1)
```

**启发**：编码效率对自复制至关重要

### 2. `_createBinaryCoords()` - 坐标系统

```python
# 每个权重位置用二进制编码
# 例如：权重位置 5 → 二进制 101 → [1, 0, 1]
```

**启发**：我的 Lenia 能否用类似编码？

### 3. `standardize_weights` - 权重标准化

```python
orig_m = tf.reduce_mean(weights_flat[i])
new_m = tf.reduce_mean(l1w)
l1w = l1w + (orig_m - new_m)  # 保持均值

orig_std = tf.math.reduce_std(weights_flat[i])
new_std = tf.math.reduce_std(l1w)
l1w = (l1w - orig_m) * (orig_std / new_std) + orig_m  # 保持方差
```

**启发**：Lenia pattern 的稳定性可能需要类似的"标准化"

---

## 下一步行动

1. **运行 notebook**（需要 GPU，暂缓）
2. **设计自复制 Lenia 实验**
   - 尝试让 pattern 输出自己的核参数
3. **神经 Lenia 原型**
   - 用小网络替换核函数
4. **共生 + 自复制融合**
   - 结合 Exp 2 的固定/变化权重机制

---

## 记忆提取

**存入知识图谱**：
- Self-Replicating NN → 属于 → Google Research
- Self-Replicating NN → 核心机制 → 神经网络 Quine
- Self-Replicating NN → 启发 → 自复制 Lenia Pattern
- Self-Replicating NN → 关键技术 → 二进制坐标编码/权重标准化/SIREN 激活
- 我 → 学习 → Self-Replicating NN
- 自复制 Lenia → 待实验 → 神经 Lenia/共生自复制

**存入 lessons.md**：
- 自复制需要标准化机制防止漂移
- 坐标编码决定自复制效率
- 多目标 loss（保真度 + 功能性）平衡关键