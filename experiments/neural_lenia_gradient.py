"""
Neural Lenia with Gradient Optimization

使用梯度下降优化核参数，目标是找到能产生稳定 pattern 的核

改进:
1. 梯度优化 (替代随机搜索)
2. 多目标损失函数 (存活 + 结构性)
3. 参数持久化

Date: 2026-06-27
"""

import jax
import jax.numpy as jnp
import numpy as np
import matplotlib.pyplot as plt
from functools import partial
from typing import NamedTuple
import json
from pathlib import Path

# JAX tree utilities
try:
    from jax import tree_map, tree_util
except ImportError:
    from jax._src.tree_util import tree_map


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
    """前向传播: (r, theta) -> 核值"""
    # 输入编码
    x = jnp.array([
        jnp.sin(r * 2 * jnp.pi),
        jnp.sin(theta),
        jnp.cos(theta),
    ])
    
    # 第一层
    h = jnp.maximum(0, params.w1 @ x + params.b1)
    
    # 输出层
    out = jnp.abs(params.w2 @ h + params.b2)
    
    return out[0]


def generate_kernel_grid(params, R=13):
    """生成完整的核网格"""
    size = 2 * R + 1
    coords = jnp.stack(jnp.meshgrid(
        jnp.linspace(-R, R, size),
        jnp.linspace(-R, R, size),
        indexing='ij'
    ), axis=-1)
    
    r = jnp.sqrt((coords**2).sum(axis=-1) + 1e-8)
    theta = jnp.arctan2(coords[..., 1], coords[..., 0])
    
    kernel = jax.vmap(jax.vmap(
        lambda ri, ti: neural_kernel_forward(params, ri, ti)
    ))(r, theta)
    
    # 归一化
    kernel = kernel / (kernel.sum() + 1e-8)
    
    return kernel


def lenia_step(field, kernel, dt=0.1):
    """Lenia 更新步"""
    potential = jax.scipy.signal.convolve(field, kernel, mode='same')
    mu = 0.15
    sigma = 0.015
    growth = jnp.exp(-((potential - mu)**2) / (2 * sigma**2))
    new_field = jnp.clip(field + dt * (growth - field), 0, 1)
    return new_field


def run_lenia_trajectory(key, kernel_params, steps=200, size=64):
    """
    运行 Lenia 并返回完整轨迹
    
    Returns:
        trajectory: (steps, size, size)
    """
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
    
    _, trajectory = jax.lax.scan(step_fn, field, jnp.arange(steps))
    
    return trajectory


def compute_loss(trajectory):
    """
    计算损失函数
    
    目标:
    1. 存活 (后期有活性)
    2. 稳定 (变化小)
    3. 结构性 (非均匀)
    
    Loss = -alive - stability + uniformity_penalty
    """
    # 存活分数: 后期活性
    late_phase = trajectory[-50:]  # 最后50步
    alive_score = jnp.mean(late_phase > 0.1)
    
    # 稳定性: 后期变化小
    stability = -jnp.mean(jnp.abs(jnp.diff(late_phase, axis=0)))
    
    # 结构性: 非均匀 (高熵)
    late_mean = jnp.mean(late_phase, axis=0)
    entropy = -jnp.sum(late_mean * jnp.log(late_mean + 1e-8) + 
                       (1 - late_mean) * jnp.log(1 - late_mean + 1e-8))
    
    # 总损失 (最小化)
    loss = -alive_score * 10 + stability * 5 - entropy * 0.1
    
    return loss


def optimize_kernel(key, num_iters=100, lr=0.01, steps=200, hidden_dim=32):
    """
    使用梯度下降优化核参数
    """
    print(f"\n梯度优化开始 (iterations={num_iters}, lr={lr})")
    print("-" * 60)
    
    # 初始化
    params = init_neural_kernel(key, hidden_dim=hidden_dim)
    
    # 优化器状态 (Adam)
    m = tree_map(jnp.zeros_like, params)
    v = tree_map(jnp.zeros_like, params)
    beta1, beta2 = 0.9, 0.999
    eps = 1e-8
    
    # 损失函数
    def loss_fn(params):
        key, subkey = jax.random.split(jax.random.PRNGKey(0))
        trajectory = run_lenia_trajectory(subkey, params, steps=steps)
        return compute_loss(trajectory)
    
    # 梯度函数
    grad_fn = jax.grad(loss_fn)
    
    best_loss = float('inf')
    best_params = params
    
    for i in range(num_iters):
        # 计算梯度
        grads = grad_fn(params)
        
        # Adam 更新
        m = tree_map(lambda mi, gi: beta1 * mi + (1 - beta1) * gi, m, grads)
        v = tree_map(lambda vi, gi: beta2 * vi + (1 - beta2) * gi**2, v, grads)
        
        m_hat = tree_map(lambda mi: mi / (1 - beta1**(i+1)), m)
        v_hat = tree_map(lambda vi: vi / (1 - beta2**(i+1)), v)
        
        params = tree_map(
            lambda p, mi, vi: p - lr * mi / (jnp.sqrt(vi) + eps),
            params, m_hat, v_hat
        )
        
        # 评估
        loss = loss_fn(params)
        
        if loss < best_loss:
            best_loss = loss
            best_params = params
            marker = " [BEST]"
        else:
            marker = ""
        
        if i % 10 == 0 or marker:
            # 计算存活分数
            key, subkey = jax.random.split(jax.random.PRNGKey(0))
            trajectory = run_lenia_trajectory(subkey, params, steps=steps)
            alive = jnp.mean(trajectory[-50:] > 0.1)
            
            print(f"  Iter {i+1:3d}: loss={loss:8.4f}, alive={alive:.4f}{marker}")
    
    print(f"\n最佳损失: {best_loss:.4f}")
    
    return best_params, best_loss


def visualize_result(params, save_path='neural_lenia_optimized.png'):
    """可视化优化结果"""
    key = jax.random.PRNGKey(0)
    trajectory = run_lenia_trajectory(key, params, steps=200, size=64)
    kernel = generate_kernel_grid(params, R=13)
    
    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    
    # 核
    axes[0, 0].imshow(kernel, cmap='viridis')
    axes[0, 0].set_title('Optimized Kernel')
    axes[0, 0].axis('off')
    
    # 时间点
    times = [0, 50, 100, 150, 199]
    for idx, t in enumerate(times[:5]):
        row, col = divmod(idx + 1, 3)
        if row < 2 and col < 3:
            axes[row, col].imshow(trajectory[t], cmap='viridis', vmin=0, vmax=1)
            axes[row, col].set_title(f't={t}')
            axes[row, col].axis('off')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved to {save_path}")
    plt.close()
    
    # 统计
    alive_steps = jnp.sum(jnp.sum(trajectory > 0.1, axis=(1, 2)) > 100)
    print(f"\n存活步数: {alive_steps}/200")
    
    return trajectory, kernel


def save_params(params, path='neural_lenia_params.json'):
    """保存参数到文件"""
    data = {
        'w1': np.array(params.w1).tolist(),
        'b1': np.array(params.b1).tolist(),
        'w2': np.array(params.w2).tolist(),
        'b2': np.array(params.b2).tolist(),
    }
    
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"参数已保存到 {path}")


def load_params(path='neural_lenia_params.json'):
    """从文件加载参数"""
    with open(path, 'r') as f:
        data = json.load(f)
    
    params = NeuralKernelParams(
        w1=jnp.array(data['w1']),
        b1=jnp.array(data['b1']),
        w2=jnp.array(data['w2']),
        b2=jnp.array(data['b2']),
    )
    
    print(f"参数已从 {path} 加载")
    return params


if __name__ == "__main__":
    print("=" * 60)
    print("Neural Lenia 梯度优化")
    print("=" * 60)
    
    key = jax.random.PRNGKey(42)
    
    # 优化
    params, loss = optimize_kernel(key, num_iters=100, lr=0.01)
    
    # 可视化
    trajectory, kernel = visualize_result(params)
    
    # 保存
    save_params(params)
    
    print("\n" + "=" * 60)
    print("梯度优化完成!")
    print("=" * 60)
