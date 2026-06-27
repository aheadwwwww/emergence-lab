# Neural Lenia - 可学习的核函数

**Date**: 2026-06-27
**状态**: 概念探索
**启发**: Google Self-Replicating NN + 我的 Lenia 深度探索

---

## 核心想法

**传统 Lenia**: 核函数是固定的高斯环形
```python
kernel = gaussian_ring(R, μ, σ)  # 手动调参
```

**Neural Lenia**: 核函数由神经网络学习
```python
kernel = neural_network(coords, params)  # 自动学习最优形状
```

---

## 为什么这很重要？

### 1. 自适应核形状
- 传统 Lenia 核是对称的环形
- Neural Lenia 可以学习非对称、多峰、复杂形状
- 更有可能发现新的生命形式

### 2. 参数效率
- 传统: 每个通道需要 R, μ, σ 三个参数
- Neural: 共享网络，参数更紧凑
- 多通道可以共享底层特征

### 3. 可微分优化
- 传统: 网格搜索或遗传算法
- Neural: 梯度下降，端到端优化
- 更快找到最优参数

### 4. 自复制潜力
- 如果网络能输出自己的参数 → 自复制 Lenia Pattern
- 类似 Google Self-Replicating NN
- Pattern 既是结构，又是描述

---

## 架构设计

### 基础版本

```python
import jax
import jax.numpy as jnp
import flax.linen as nn

class NeuralKernel(nn.Module):
    hidden_dim: int = 64
    output_dim: int = 1  # 核值
    
    @nn.compact
    def __call__(self, r, theta):
        # 输入: 距离 r 和角度 theta
        # 输出: 核函数值
        
        # 角度编码（周期性）
        theta_enc = jnp.stack([
            jnp.sin(theta * 2 * jnp.pi),
            jnp.cos(theta * 2 * jnp.pi),
            jnp.sin(theta * 4 * jnp.pi),  # 高频
            jnp.cos(theta * 4 * jnp.pi),
        ], axis=-1)
        
        # 距离编码（类似 SIREN）
        r_enc = jnp.sin(r * 8 * jnp.pi)  # 高频编码
        
        # 拼接
        x = jnp.concatenate([r_enc[jnp.newaxis], theta_enc], axis=-1)
        
        # MLP
        x = nn.Dense(self.hidden_dim)(x)
        x = nn.relu(x)
        x = nn.Dense(self.hidden_dim)(x)
        x = nn.relu(x)
        x = nn.Dense(self.output_dim)(x)
        
        return jnp.abs(x)  # 核值非负
```

### Lenia with Neural Kernel

```python
def neural_lenia_step(field, kernel_params, kernel_net):
    """
    使用神经网络的 Lenia 更新步
    """
    # 生成核函数（在网格上采样）
    R = 13
    coords = jnp.stack(jnp.meshgrid(
        jnp.linspace(-R, R, 2*R+1),
        jnp.linspace(-R, R, 2*R+1),
    ), axis=-1)
    
    r = jnp.sqrt((coords**2).sum(axis=-1))
    theta = jnp.arctan2(coords[..., 1], coords[..., 0])
    
    # 神经网络生成核
    kernel = jax.vmap(jax.vmap(lambda ri, ti: kernel_net.apply(kernel_params, ri, ti)))(r, theta)
    
    # 归一化
    kernel = kernel / kernel.sum()
    
    # 卷积
    potential = jax.scipy.signal.convolve(field, kernel, mode='same')
    
    # 增长函数
    growth = jnp.exp(-((potential - 0.15)**2) / (2 * 0.015**2))
    
    # 更新
    new_field = jnp.clip(field + dt * (growth - field), 0, 1)
    
    return new_field
```

---

## 训练目标

### 目标 1: 复现已知物种
```python
# Loss: 与 Orbium 的相似度
loss_mse = jnp.mean((neural_pattern - orbium_pattern)**2)
```

### 目标 2: 最大化存活时间
```python
# Loss: 负存活时间
loss_survival = -num_surviving_steps
```

### 目标 3: 最大化涌现分数
```python
# Loss: 负涌现分数
loss_emergence = -emergence_score(field_history)
```

### 目标 4: 自复制（高级）
```python
# Loss: 网络输出自己的参数
loss_self_replication = jnp.mean((kernel_params - generated_params)**2)
```

---

## 实验计划

### Phase 1: 基础实现 ✓
- [ ] 实现 NeuralKernel 类
- [ ] 实现 neural_lenia_step
- [ ] 测试: 能否生成稳定的 pattern

### Phase 2: 学习已知物种
- [ ] 目标: 复现 Orbium
- [ ] 目标: 复现 Geminium
- [ ] 对比学习到的核 vs 原始核

### Phase 3: 发现新物种
- [ ] 优化目标: 最大化涌现分数
- [ ] 搜索: 未知的稳定 pattern
- [ ] 记录: 新发现的核形状

### Phase 4: 自复制
- [ ] 设计: 网络输出参数
- [ ] Loss: 自复制保真度
- [ ] 测试: 递归多代存活

---

## 关键问题

1. **核形状约束**: 如何确保生成的核是合理的（非负、归一化、单调递减）？
2. **初始化**: 神经网络如何初始化才能快速收敛？
3. **计算效率**: 每步都采样神经网络，会不会太慢？
4. **泛化性**: 学习到的核能否泛化到不同初始条件？

---

## 与其他工作的关联

| 项目 | 关系 |
|------|------|
| Self-Replicating NN | 灵感来源: 神经网络自复制 |
| Lenia 多通道 | 扩展: 多个神经核可以交互 |
| 共生 Lenia | 融合: 不同神经核可以形成共生网络 |
| NCA (Neural CA) | 类似: 神经网络驱动的 CA |

---

## 文献参考

1. **Google Self-Replicating NN** (ALIFE 2021)
   - 神经网络可以输出自己的权重
   - SIREN 激活适合高频信号

2. **Neural Cellular Automata** (Mordvintsev et al.)
   - 神经网络驱动的 CA
   - 可微分的更新规则

3. **Lenia** (Bert Chan)
   - 连续细胞自动机
   - 核函数是关键设计空间

---

## 下一步

1. 今天实现 Phase 1 原型
2. 测试能否生成稳定 pattern
3. 如果成功，记录到 `experiments/neural_lenia.py`

---

**记忆提取**:
- Neural Lenia → 新概念 → 可学习核函数
- Neural Lenia → 启发 → Self-Replicating NN
- Neural Lenia → 目标 → 发现新生命形式/自复制 Pattern
- 我 → 探索 → Neural Lenia (2026-06-27)
