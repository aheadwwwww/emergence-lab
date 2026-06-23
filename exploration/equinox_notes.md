# Equinox 学习笔记

## 项目简介

**Equinox** 是 JAX 生态中的核心神经网络库，由 Patrick Kidger 开发。

- **定位**：JAX 的 "one-stop library"，补全 JAX 核心之外的所有功能
- **特点**：不是框架！任何 Equinox 代码都与其他 JAX 库兼容
- **版本**：Python 3.10+

## 核心设计理念

### 1. 模型 = PyTree

```python
import equinox as eqx
import jax

class Linear(eqx.Module):
    weight: jax.Array
    bias: jax.Array

    def __init__(self, in_size, out_size, key):
        wkey, bkey = jax.random.split(key)
        self.weight = jax.random.normal(wkey, (out_size, in_size))
        self.bias = jax.random.normal(bkey, (out_size,))

    def __call__(self, x):
        return self.weight @ x + self.bias
```

**关键洞察**：
- `eqx.Module` 只是注册类为 PyTree
- 从此 JAX 就知道如何处理这个类
- 可以无缝穿过 `jit`、`grad`、`vmap` 边界

### 2. 与 PyTorch 的对比

| 特性 | PyTorch | Equinox |
|------|---------|---------|
| 模型定义 | `nn.Module` | `eqx.Module` |
| 参数访问 | `model.parameters()` | 自动 PyTree |
| JIT | `torch.jit.script` | `@jax.jit` |
| 自动微分 | `loss.backward()` | `@jax.grad` |
| 向量化 | 手动 batch | `@jax.vmap` |

### 3. Filtered API

Equinox 的独特创新：**filtered transformations**

```python
@eqx.filter_jit
@eqx.filter_grad
def loss_fn(model, x, y):
    pred_y = jax.vmap(model)(x)
    return jax.numpy.mean((y - pred_y) ** 2)
```

普通 JAX 变换要求所有输入都是数组，而 Equinox 的 filtered 版本可以处理混合类型（数组+非数组）。

## 核心模块

### nn 模块（神经网络层）

```
equinox/nn/
├── _linear.py        # Linear, Identity
├── _conv.py          # Conv1d/2d/3d, ConvTranspose
├── _mlp.py           # MLP
├── _attention.py     # MultiheadAttention
├── _embedding.py     # Embedding, RotaryPositionalEmbedding
├── _rnn.py           # LSTMCell, GRUCell
├── _normalisation.py # LayerNorm, GroupNorm, RMSNorm
├── _batch_norm.py    # BatchNorm
├── _dropout.py       # Dropout
├── _pool.py          # MaxPool, AvgPool, AdaptivePool
├── _sequential.py    # Sequential, Lambda
├── _spectral_norm.py # SpectralNorm
└── _weight_norm.py   # WeightNorm
```

### 核心工具

```
equinox/
├── _module/     # Module, AbstractVar, field
├── _jit.py      # filter_jit
├── _ad.py       # filter_grad, filter_value_and_grad
├── _vmap_pmap.py # filter_vmap, filter_pmap
├── _tree.py     # tree_at, tree_equal, tree_check
├── _filters.py  # filter, partition, combine
├── _errors.py   # 运行时错误检测
└── _serialisation.py # 模型保存/加载
```

## 与涌现实验的结合

### 优势

1. **高性能模拟**
   - JAX 的 JIT 编译 + GPU 加速
   - 可用于大规模 CA、Boids、Lenia 模拟

2. **自动微分**
   - 可对涌现参数求梯度
   - 用优化算法搜索"最优"涌现配置

3. **向量化**
   - `vmap` 并行跑多个实验
   - 快速参数扫描

### 示例：用 Equinox 定义 CA

```python
import equinox as eqx
import jax.numpy as jnp

class CellularAutomaton(eqx.Module):
    kernel: jnp.ndarray  # 3x3 卷积核
    update_rule: jnp.ndarray  # 更新规则权重

    def __call__(self, state):
        # 使用 jax.lax.conv 进行高效卷积
        from jax import lax
        conv_state = lax.conv(state, self.kernel)
        return jax.nn.sigmoid(self.update_rule @ conv_state)
```

## JAX 生态系统

**Patrick Kidger 的库**：
- `equinox` - 神经网络
- `diffrax` - 微分方程求解器
- `optimistix` - 优化算法
- `lineax` - 线性求解器
- `jaxtyping` - 类型注解

**其他重要库**：
- `optax` - 优化器（SGD, Adam 等）
- `orbax` - 检查点
- `blackjax` - 贝叶斯采样
- `levanter` - 大模型训练

## 下一步

1. 用 Equinox 重写现有涌现实验
2. 添加自动微分优化参数
3. 探索 `diffrax` 用于连续时间 CA
4. 尝试 GPU 加速大规模模拟

## 参考

- 文档：https://docs.kidger.site/equinox
- 论文：arXiv:2111.00254
- GitHub：patrick-kidger/equinox
