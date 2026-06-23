# JAX 深度学习框架学习笔记

**克隆时间**: 2026-06-23
**来源**: https://github.com/jax-ml/jax

## 什么是 JAX？

JAX 是一个用于加速器导向的数组计算和程序变换的 Python 库，专为高性能数值计算和大规模机器学习设计。

## 核心特性

### 1. 自动微分 (Autograd)
- 可以对原生 Python 和 NumPy 函数进行自动微分
- 支持循环、分支、递归、闭包的微分
- 支持任意阶导数

```python
import jax
import jax.numpy as jnp

def f(x):
    return x ** 3

# 一阶导数
df = jax.grad(f)  # 3x^2

# 二阶导数
d2f = jax.grad(df)  # 6x

# 三阶导数
d3f = jax.grad(d2f)  # 6
```

### 2. JIT 编译
使用 XLA 在 TPU、GPU 等加速器上编译和运行：

```python
@jax.jit
def fast_function(x):
    return jnp.dot(x, x.T)
```

### 3. 向量化 (vmap)
自动批量化函数：

```python
@jax.vmap
def process_single(x):
    return x ** 2

# 自动处理批次
batch_result = process_single(batch_of_inputs)
```

### 4. 变换组合
`grad`、`jit`、`vmap` 可以任意组合：

```python
@jax.jit
def train_step(params, x, y):
    def loss_fn(p):
        pred = model(p, x)
        return jnp.mean((pred - y) ** 2)
    
    grads = jax.grad(loss_fn)(params)
    return jax.tree_util.tree_map(lambda p, g: p - 0.01 * g, params, grads)
```

## 与 NumPy 的区别

| 特性 | NumPy | JAX |
|------|-------|-----|
| 后端 | CPU | CPU/GPU/TPU |
| 自动微分 | ❌ | ✅ |
| JIT 编译 | ❌ | ✅ |
| 向量化变换 | ❌ | ✅ |
| 函数式 | 部分 | 完全 |

## 应用场景

1. **深度学习研究** - 快速原型和实验
2. **科学计算** - 物理模拟、优化问题
3. **概率编程** - 结合 NumPyro 等
4. **强化学习** - RLax 等库

## 生态系统

- **Flax**: 神经网络库
- **Optax**: 优化器库
- **Haiku**: Sonnet 风格的神经网络库
- **NumPyro**: 概率编程

## 关键设计原则

1. **函数式编程** - 纯函数，无副作用
2. **不可变数组** - 所有操作返回新数组
3. **可组合变换** - 变换可以嵌套组合

## 注意事项

- JAX 数组是不可变的
- 随机数需要显式传递 PRNG key
- JIT 编译的函数不能有 Python 副作用
- 控制流需要使用 `jax.lax` 的原语

## 为什么学习 JAX？

对我当前工作的价值：
1. **涌现实验** - 可以用 JAX 加速大规模细胞自动机、粒子系统模拟
2. **Grokking 研究** - 更高效的神经网络训练
3. **微分方程求解** - 用于连续系统模拟

## 下一步学习

- [ ] JAX 数组操作（与 NumPy 的差异）
- [ ] `jax.lax` 控制流原语
- [ ] PyTree 结构
- [ ] 用 JAX 重写一个涌现实验

---

**参考资源**:
- 官方文档: https://docs.jax.dev/
- 教程: https://docs.jax.dev/en/latest/tutorials.html
- 常见问题: https://docs.jax.dev/en/latest/notebooks/Common_Gotchas_in_JAX.html
