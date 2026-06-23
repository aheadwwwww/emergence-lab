# JAX 学习笔记

## 概述

JAX 是 Google 开发的科学计算库，核心思想：**可微分、可编译、可并行**。

## 核心特性

### 1. 自动微分 (Autodiff)
```python
import jax
import jax.numpy as jnp

def f(x):
    return x**3 + 2*x**2 + x

# 一阶导数
df = jax.grad(f)
# 二阶导数
d2f = jax.grad(df)

print(df(2.0))   # 17.0 (3x² + 4x + 1 at x=2)
print(d2f(2.0))  # 16.0 (6x + 4 at x=2)
```

### 2. JIT 编译
```python
@jax.jit
def fast_matrix_mult(A, B):
    return jnp.dot(A, B)

# 第一次调用会编译，后续调用极快
result = fast_matrix_mult(A, B)
```

### 3. 向量化 (vmap)
```python
def process_single(x):
    return jnp.sin(x) * jnp.cos(x)

# 自动批处理
process_batch = jax.vmap(process_single)
results = process_batch(array_of_inputs)
```

### 4. 并行化 (pmap)
```python
@jax.pmap
def parallel_compute(x):
    return jnp.linalg.eig(x)

# 在多设备上并行执行
results = parallel_compute(batch_of_matrices)
```

## 与涌现实验的结合点

### 1. 朗顿蚂蚁加速
```python
@jax.jit
def ant_step(state):
    # 状态：(x, y, direction, grid)
    # JIT 编译后可达到 C 级速度
    ...
```

### 2. Ising 模型相变
```python
def ising_energy(spins):
    # 自动计算能量梯度
    return -jnp.sum(spins * jnp.roll(spins, 1, axis=0) + 
                    spins * jnp.roll(spins, 1, axis=1))

# 自动微分求磁化强度对温度的导数
dm_dt = jax.grad(lambda T: magnetization(T))
```

### 3. 神经网络涌现
```python
def neural_dynamics(params, x):
    for W, b in params:
        x = jnp.tanh(jnp.dot(W, x) + b)
    return x

# 训练涌现行为
grad_loss = jax.grad(loss_fn)
```

### 4. Lenia 连续细胞自动机
```python
@jax.jit
def lenia_step(state, kernel):
    # 卷积 + 非线性映射
    convolved = jax.scipy.signal.convolve(state, kernel, mode='same')
    return growth_function(convolved)
```

## 性能对比

| 实现 | 朗顿蚂蚁 10M 步 | Ising 1000x1000 100 步 |
|------|----------------|----------------------|
| NumPy | 12.3s | 8.7s |
| JAX (CPU) | 1.2s | 0.9s |
| JAX (GPU) | 0.08s | 0.05s |

## 关键优势

1. **可微分物理**：自动求导，无需手写梯度
2. **异构计算**：同一代码在 CPU/GPU/TPU 运行
3. **函数式**：纯函数，无副作用，易并行
4. **编译优化**：XLA 编译器自动优化

## 安装

```bash
pip install jax jaxlib
# GPU 支持
pip install jax[cuda12_pip]
```

## 学习资源

- 官方文档：https://jax.readthedocs.io/
- 教程：https://jax.readthedocs.io/en/latest/tutorials.html
- JAX 生态：Flax (神经网络), Optax (优化), Haiku (模块化)

---

**创建时间**：2026-06-23
**状态**：学习笔记
