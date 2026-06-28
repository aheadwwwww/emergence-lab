"""
Neural Lenia - 可学习的核函数

概念: 用神经网络替代固定的 Gaussian 核
目标: 自动学习最优核形状，发现新生命形式

Date: 2026-06-27
"""

import jax
import jax.numpy as jnp
import numpy as np
import matplotlib.pyplot as plt
from functools import partial
from typing import NamedTuple

# 简化版: 不使用 flax，手动实现


class NeuralKernelParams(NamedTuple):
    """神经核参数"""
    w1: jnp.ndarray  # (hidden_dim, input_dim)
    b1: jnp.ndarray  # (hidden_dim,)
    w2: jnp.ndarray  # (1, hidden_dim)
    b2: jnp.ndarray  # (1,)


def init_neural_kernel(key, hidden_dim=32):
    """初始化神经核参数"""
    input_dim = 3  # r + sin(theta) + cos(theta)
    k1, k2 = jax.random.split(key)
    
    w1 = jax.random.normal(k1, (hidden_dim, input_dim)) * 0.1
    b1 = jnp.zeros(hidden_dim)
    w2 = jax.random.normal(k2, (1, hidden_dim)) * 0.1
    b2 = jnp.zeros(1)
    
    return NeuralKernelParams(w1, b1, w2, b2)


def neural_kernel_forward(params: NeuralKernelParams, r, theta):
    """
    前向传播: (r, theta) -> 核值
    
    使用 ReLU 激活，输出非负
    """
    # 输入编码
    x = jnp.array([
        jnp.sin(r * 2 * jnp.pi),  # 距离编码
        jnp.sin(theta),           # 角度编码
        jnp.cos(theta),
    ])
    
    # 第一层
    h = jnp.maximum(0, params.w1 @ x + params.b1)  # ReLU
    
    # 输出层
    out = jnp.abs(params.w2 @ h + params.b2)  # 非负
    
    return out[0]


def generate_kernel_grid(params, R=13):
    """
    生成完整的核网格
    
    Args:
        params: 神经核参数
        R: 核半径
    
    Returns:
        kernel: (2R+1, 2R+1) 核矩阵
    """
    size = 2 * R + 1
    coords = jnp.stack(jnp.meshgrid(
        jnp.linspace(-R, R, size),
        jnp.linspace(-R, R, size),
        indexing='ij'
    ), axis=-1)
    
    r = jnp.sqrt((coords**2).sum(axis=-1) + 1e-8)
    theta = jnp.arctan2(coords[..., 1], coords[..., 0])
    
    # 向量化应用
    kernel = jax.vmap(jax.vmap(
        lambda ri, ti: neural_kernel_forward(params, ri, ti)
    ))(r, theta)
    
    # 归一化
    kernel = kernel / (kernel.sum() + 1e-8)
    
    return kernel


def lenia_step(field, kernel, dt=0.1):
    """
    Lenia 更新步
    
    Args:
        field: (H, W) 当前场
        kernel: (kH, kW) 核
        dt: 时间步长
    
    Returns:
        new_field: (H, W) 新场
    """
    # 卷积
    potential = jax.scipy.signal.convolve(field, kernel, mode='same')
    
    # 增长函数 (Gaussian)
    mu = 0.15
    sigma = 0.015
    growth = jnp.exp(-((potential - mu)**2) / (2 * sigma**2))
    
    # 更新
    new_field = jnp.clip(field + dt * (growth - field), 0, 1)
    
    return new_field


def run_lenia(key, kernel_params, steps=200, size=64):
    """
    运行 Lenia 模拟
    
    Args:
        key: JAX 随机 key
        kernel_params: 神经核参数
        steps: 模拟步数
        size: 场大小
    
    Returns:
        history: (steps, size, size) 场历史
        alive_steps: 存活步数
    """
    # 生成核
    kernel = generate_kernel_grid(kernel_params, R=13)
    
    # 初始化: 随机圆
    center = size // 2
    y, x = jnp.ogrid[:size, :size]
    mask = ((x - center)**2 + (y - center)**2) < 100
    field = jax.random.uniform(key, (size, size)) * mask.astype(float)
    
    # 模拟
    def step_fn(field, _):
        new_field = lenia_step(field, kernel)
        return new_field, new_field
    
    _, history = jax.lax.scan(step_fn, field, jnp.arange(steps))
    
    # 计算存活步数
    alive = jnp.sum(history > 0.1, axis=(1, 2)) > 100
    alive_steps = jnp.sum(alive)
    
    return history, alive_steps


def visualize_kernel_and_pattern(kernel_params, history, save_path=None):
    """可视化核和生成的 pattern"""
    kernel = generate_kernel_grid(kernel_params, R=13)
    
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    
    # 核
    axes[0].imshow(kernel, cmap='viridis')
    axes[0].set_title('Neural Kernel')
    axes[0].axis('off')
    
    # 初始状态
    axes[1].imshow(history[0], cmap='viridis')
    axes[1].set_title('t=0')
    axes[1].axis('off')
    
    # 中间状态
    mid = len(history) // 2
    axes[2].imshow(history[mid], cmap='viridis')
    axes[2].set_title(f't={mid}')
    axes[2].axis('off')
    
    # 最终状态
    axes[3].imshow(history[-1], cmap='viridis')
    axes[3].set_title(f't={len(history)-1}')
    axes[3].axis('off')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved to {save_path}")
    
    plt.close()
    
    return kernel


def compute_fitness(history):
    """
    计算适应度分数
    
    目标: 
    1. 存活时间长
    2. 有动态行为（不是静态）
    3. 有复杂结构（高熵）
    """
    # 存活分数: 存活步数 / 总步数
    alive = jnp.sum(history > 0.1, axis=(1, 2)) > 100
    alive_score = jnp.sum(alive) / len(history)
    
    # 动态分数: 帧间差异的均值
    if len(history) > 1:
        diff = jnp.abs(history[1:] - history[:-1])
        dynamic_score = jnp.mean(diff)
    else:
        dynamic_score = 0.0
    
    # 复杂度分数: 最终状态的熵
    final = history[-1]
    # 离散化到 10 个 bins
    hist, _ = jnp.histogram(final, bins=10, range=(0, 1))
    hist = hist / jnp.sum(hist) + 1e-10
    entropy = -jnp.sum(hist * jnp.log(hist))
    complexity_score = entropy / 2.3  # 归一化 (max ~2.3 for 10 bins)
    
    # 总分
    total = alive_score * 2.0 + dynamic_score * 5.0 + complexity_score * 1.0
    
    return total


def gradient_optimization(key, steps=200, iterations=50, lr=0.01):
    """
    使用梯度下降优化神经核参数
    
    Args:
        key: 随机 key
        steps: 每次模拟的步数
        iterations: 优化迭代次数
        lr: 学习率
    
    Returns:
        best_params: 最优参数
        best_score: 最高分数
        history: 优化历史
    """
    print("=" * 60)
    print("Neural Lenia 梯度优化")
    print("=" * 60)
    
    # 初始化参数
    k1, k2 = jax.random.split(key)
    params = init_neural_kernel(k1, hidden_dim=32)
    
    best_params = params
    best_score = 0.0
    optimization_history = []
    
    for i in range(iterations):
        k1, k2 = jax.random.split(k2)
        
        # 运行模拟
        history, alive_steps = run_lenia(k1, params, steps=steps, size=64)
        
        # 计算适应度
        score = compute_fitness(history)
        
        # 计算梯度
        def loss_fn(p):
            h, _ = run_lenia(k1, p, steps=steps, size=64)
            return -compute_fitness(h)  # 负号因为我们要最大化
        
        grads = jax.grad(loss_fn)(params)
        
        # 更新参数
        new_w1 = params.w1 - lr * grads.w1
        new_b1 = params.b1 - lr * grads.b1
        new_w2 = params.w2 - lr * grads.w2
        new_b2 = params.b2 - lr * grads.b2
        
        params = NeuralKernelParams(new_w1, new_b1, new_w2, new_b2)
        
        # 记录
        optimization_history.append({
            'iteration': i,
            'score': float(score),
            'alive_steps': int(alive_steps),
        })
        
        if score > best_score:
            best_score = score
            best_params = params
        
        if i % 10 == 0:
            print(f"Iter {i}: score={score:.3f}, alive={alive_steps}/{steps}, best={best_score:.3f}")
    
    print(f"\n优化完成! 最佳分数: {best_score:.3f}")
    
    return best_params, best_score, optimization_history


def evolve_orbium(key, iterations=100):
    """
    进化出类似 Orbium 的生命形式
    
    Orbium 参数: R=13, μ=0.15, σ=0.015
    目标: 学习出类似的核形状
    """
    print("=" * 60)
    print("进化 Orbium-like 生命形式")
    print("=" * 60)
    
    best_params, best_score, history = gradient_optimization(
        key, steps=300, iterations=iterations, lr=0.005
    )
    
    # 可视化最终结果
    k1, k2 = jax.random.split(key)
    final_history, _ = run_lenia(k1, best_params, steps=500, size=128)
    
    visualize_kernel_and_pattern(
        best_params, 
        final_history[::50],  # 每 50 帧采样
        save_path='output/neural_lenia_orbium.png'
    )
    
    return best_params, history


# 测试函数
def test_neural_lenia():
    """测试 Neural Lenia"""
    print("=" * 60)
    print("Neural Lenia 测试")
    print("=" * 60)
    
    key = jax.random.PRNGKey(42)
    
    # 初始化参数
    kernel_params = init_neural_kernel(key, hidden_dim=32)
    print(f"[OK] 初始化神经核参数")
    
    # 生成核
    kernel = generate_kernel_grid(kernel_params, R=13)
    print(f"[OK] 生成核: shape={kernel.shape}, sum={kernel.sum():.4f}")
    
    # 运行模拟
    key, subkey = jax.random.split(key)
    history, alive_steps = run_lenia(key, kernel_params, steps=200, size=64)
    print(f"[OK] 模拟完成: 存活步数 = {alive_steps}")
    
    # 可视化
    kernel = visualize_kernel_and_pattern(
        kernel_params, 
        history,
        save_path='neural_lenia_test.png'
    )
    
    # 分析核形状
    center = kernel.shape[0] // 2
    profile = kernel[center, center:]
    
    print(f"\n核分析:")
    print(f"  中心值: {kernel[center, center]:.4f}")
    print(f"  最大值: {kernel.max():.4f}")
    print(f"  轮廓: {profile[:10].round(3)}")
    
    return kernel_params, history


def random_search(num_trials=20):
    """
    随机搜索好的核参数
    
    目标: 找到能产生稳定 pattern 的核
    """
    print("\n" + "=" * 60)
    print("随机搜索最优核参数")
    print("=" * 60)
    
    key = jax.random.PRNGKey(42)
    best_alive = 0
    best_params = None
    
    for i in range(num_trials):
        key, subkey = jax.random.split(key)
        params = init_neural_kernel(subkey, hidden_dim=32)
        
        key, subkey = jax.random.split(key)
        _, alive_steps = run_lenia(subkey, params, steps=200, size=64)
        
        if alive_steps > best_alive:
            best_alive = alive_steps
            best_params = params
            print(f"  Trial {i+1}: 存活 {alive_steps} 步 [NEW BEST]")
        else:
            print(f"  Trial {i+1}: 存活 {alive_steps} 步")
    
    print(f"\n最佳结果: 存活 {best_alive} 步")
    
    # 可视化最佳
    if best_params is not None:
        key, subkey = jax.random.split(key)
        history, _ = run_lenia(subkey, best_params, steps=200, size=64)
        visualize_kernel_and_pattern(
            best_params,
            history,
            save_path='neural_lenia_best.png'
        )
    
    return best_params, best_alive


if __name__ == "__main__":
    # 基础测试
    params, history = test_neural_lenia()
    
    # 随机搜索
    best_params, best_alive = random_search(num_trials=20)
    
    print("\n" + "=" * 60)
    print("Neural Lenia 原型测试完成!")
    print("=" * 60)
