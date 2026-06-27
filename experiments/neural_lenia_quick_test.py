"""
Quick test: Neural Lenia gradient optimization (simplified)
Date: 2026-06-27
"""

import jax
import jax.numpy as jnp
import numpy as np
import matplotlib.pyplot as plt

# 简单核参数：直接优化 (R, μ, σ)
@jax.jit
def lenia_kernel(r, params):
    """简单高斯核"""
    R, mu, sigma = params
    return jnp.exp(-((r - mu * R)**2) / (2 * (sigma * R)**2))

@jax.jit
def lenia_step(grid, kernel):
    """Lenia 单步更新"""
    # 卷积
    from jax.scipy.signal import convolve2d
    U = convolve2d(grid, kernel, mode='same')
    
    # 增长函数
    G = 2 * jnp.exp(-((U - 0.15)**2) / 0.01) - 1
    
    # 更新
    return jnp.clip(grid + 0.1 * G, 0, 1)

def simulate(params, key, steps=100):
    """模拟 Lenia 演化"""
    R = 13
    size = 64
    
    # 生成核
    coords = jnp.stack(jnp.meshgrid(
        jnp.linspace(-R, R, 2*R+1),
        jnp.linspace(-R, R, 2*R+1),
        indexing='ij'
    ), axis=-1)
    r = jnp.sqrt((coords**2).sum(axis=-1) + 1e-8)
    kernel = lenia_kernel(r, params)
    kernel = kernel / (kernel.sum() + 1e-8)
    
    # 初始化网格
    grid = jax.random.uniform(key, (size, size))
    
    # 运行
    for _ in range(steps):
        grid = lenia_step(grid, kernel)
    
    # 评估
    alive = (grid > 0.1).mean()
    variance = grid.var()
    
    return alive, variance

@jax.jit
def loss_fn(params, key):
    """损失函数：最大化存活，最小化方差"""
    alive, var = simulate(params, key)
    return -alive + 0.01 * var

# 主优化循环
key = jax.random.PRNGKey(42)
params = jnp.array([13.0, 0.3, 0.05])  # R, mu, sigma

print("Starting gradient optimization...")
print(f"Initial params: R={params[0]:.1f}, μ={params[1]:.3f}, σ={params[2]:.3f}")

for i in range(20):
    key, subkey = jax.random.split(key)
    loss, grads = jax.value_and_grad(loss_fn)(params, subkey)
    
    # 梯度下降
    params = params - 0.01 * grads
    
    if i % 5 == 0:
        alive, var = simulate(params, key, steps=50)
        print(f"Iter {i}: loss={loss:.4f}, alive={alive:.3f}, var={var:.4f}")

print(f"\nFinal params: R={params[0]:.1f}, μ={params[1]:.3f}, σ={params[2]:.3f}")
