# JAX 学习笔记

## 项目简介

**JAX** 是 Google 开发的高性能数值计算库，专为加速器优化的数组计算和程序变换设计。

核心定位：
- 高性能数值计算
- 大规模机器学习
- 自动微分 + JIT 编译 + 自动向量化

## 核心特性

### 1. 可组合的函数变换

JAX 的核心是一个可扩展的**函数变换系统**，主要变换包括：

#### `jax.grad` - 自动微分
```python
import jax
import jax.numpy as jnp

def tanh(x):
    y = jnp.exp(-2.0 * x)
    return (1.0 - y) / (1.0 + y)

grad_tanh = jax.grad(tanh)
print(grad_tanh(1.0))  # 0.4199743

# 任意阶导数
print(jax.grad(jax.grad(jax.grad(tanh)))(1.0))  # 0.62162673
```

特点：
- 支持反向模式微分（backpropagation）
- 支持前向模式微分
- 可组合到任意阶
- 可对循环、分支、递归、闭包求导

#### `jax.jit` - 即时编译
```python
def slow_f(x):
    return x * x + x * 2.0

fast_f = jax.jit(slow_f)  # XLA 编译，融合操作
```

特点：
- 使用 XLA 编译器
- 自动内核融合
- 支持 GPU/TPU 加速

#### `jax.vmap` - 自动向量化
```python
def l1_distance(x, y):
    return jnp.sum(jnp.abs(x - y))

# 自动批处理
pairwise = jax.vmap(jax.vmap(l1_distance, (0, None)), (None, 0))
```

特点：
- 将函数沿数组轴映射
- 推送循环到底层操作
- 比 Python 循环快得多

### 2. 可组合性

这些变换可以**任意组合**：

```python
# 编译 + 梯度
grad_loss = jax.jit(jax.grad(loss))

# 向量化 + 梯度 + 编译（每个样本的梯度）
perex_grads = jax.jit(jax.vmap(grad_loss, in_axes=(None, 0, 0)))
```

### 3. 扩展性（Scaling）

JAX 支持多种并行模式：

| 模式 | 视角 | 显式分片 | 显式通信 |
|------|------|----------|----------|
| 自动 | 全局 | ❌ | ❌ |
| 显式 | 全局 | ✅ | ❌ |
| 手动 | 每设备 | ✅ | ✅ |

```python
from jax.sharding import PartitionSpec as P

# 数据分片
inputs = jax.device_put(inputs, P('data'))

# 自动并行化
gradfun = jax.jit(jax.grad(loss))
param_grads = gradfun(params, inputs, targets)
```

## 架构设计

### 核心组件
```
jax/
├── numpy/      # NumPy API 兼容层
├── lax/        # 低级原语操作
├── grad/       # 自动微分
├── jit/        # JIT 编译
├── vmap/       # 向量化映射
├── pmap/       # 并行映射
└── sharding/   # 数据分片
```

### 编译器后端
- **XLA** (Accelerated Linear Algebra)
- 支持 CPU, GPU, TPU

## 与涌现实验的结合

### 1. 高效模拟
```python
# 用 JAX 重写细胞自动机
@jax.jit
def lenia_step(state, kernel):
    u = jax.scipy.signal.convolve(state, kernel, mode='wrap')
    g = growth(u, m, s)
    return jnp.clip(state + g * 0.1, 0, 1)

# 向量化：一次跑多个参数
batch_step = jax.vmap(lenia_step, in_axes=(0, None))
```

### 2. 参数优化
```python
# 用自动微分优化涌现参数
def objective(params):
    state = run_lenia(params)
    return -entropy(state)  # 最大化熵

grad_obj = jax.grad(objective)
params = jax.jit(jax.value_and_grad(objective))
```

### 3. 神经网络涌现
- 用 JAX 实现神经网络模型
- 研究训练过程中的涌现（如 Grokking）
- 并行运行多个实验

## 与其他框架对比

| 特性 | NumPy | PyTorch | JAX |
|------|-------|---------|-----|
| 自动微分 | ❌ | ✅ | ✅ |
| JIT 编译 | ❌ | ✅ | ✅ |
| 向量化变换 | ❌ | ❌ | ✅ |
| 函数变换 | ❌ | ❌ | ✅ |
| TPU 支持 | ❌ | ❌ | ✅ |
| 无状态 API | ✅ | ❌ | ✅ |

## 优势

1. **函数式设计** - 无状态，易于推理和测试
2. **可组合变换** - grad(jit(vmap(f))) 随意组合
3. **高性能** - XLA 编译，自动并行
4. **NumPy 兼容** - 迁移成本低

## 注意事项

- **纯函数约束** - 避免副作用
- **静态形状** - 数组形状需要在编译时确定
- **控制流限制** - JIT 中需使用 jax.lax 的条件/循环

## 安装

```bash
# CPU
pip install -U jax

# NVIDIA GPU
pip install -U "jax[cuda13]"

# TPU
pip install -U "jax[tpu]"
```

## 参考资源

- 官方文档：https://docs.jax.dev/
- GitHub：https://github.com/google/jax
- 教程：https://docs.jax.dev/en/latest/tutorials.html
- Autodiff Cookbook：https://docs.jax.dev/en/latest/notebooks/autodiff_cookbook.html
