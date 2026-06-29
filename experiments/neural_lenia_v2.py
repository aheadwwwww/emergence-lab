"""
Neural Lenia v2 — 改进的梯度优化

改进点:
1. Orbium-specific 适应度函数 (目标形状匹配)
2. 多随机种子评估 (降低噪声)
3. 梯度裁剪防止爆炸
4. Adam 优化器
5. Warmup + 渐进式步长

Date: 2026-06-30
"""

import jax
import jax.numpy as jnp
from functools import partial
import numpy as np
import matplotlib.pyplot as plt
import json

# 复用 v1 的基础组件
from neural_lenia import (
    init_neural_kernel, neural_kernel_forward,
    generate_kernel_grid, lenia_step, visualize_kernel_and_pattern,
    NeuralKernelParams
)


# ─────────────────────────────────────────────
# 标准 Orbium 核 (基准)
# ─────────────────────────────────────────────

def orbium_kernel(R=13, mu=0.15, sigma=0.015):
    """生成标准 Orbium Gaussian 核"""
    size = 2 * R + 1
    coords = jnp.stack(jnp.meshgrid(
        jnp.linspace(-R, R, size),
        jnp.linspace(-R, R, size),
        indexing='ij'
    ), axis=-1)
    r = jnp.sqrt((coords**2).sum(axis=-1) + 1e-8)
    kernel = jnp.exp(-((r - mu)**2) / (2 * sigma**2))
    kernel = kernel / kernel.sum()
    return kernel


def orbium_seed(size=64):
    """标准 Orbium 初始条件 (圆形 blob)"""
    center = size // 2
    y, x = jnp.ogrid[:size, :size]
    mask = ((x - center)**2 + (y - center)**2) < 100
    field = jnp.ones((size, size)) * mask.astype(float) * 0.8
    return field


# ─────────────────────────────────────────────
# v2: 改进的模拟与评估
# ─────────────────────────────────────────────

def run_lenia_multi_eval(key, kernel_params, steps=200, size=64, n_evals=3):
    """
    多随机种子评估 — 降低噪声
    
    Returns:
        histories: (n_evals, steps, size, size)
        scores: (n_evals,) 适应度
    """
    keys = jax.random.split(key, n_evals)
    
    def single_eval(k):
        kernel = generate_kernel_grid(kernel_params, R=13)
        field = jax.random.uniform(k, (size, size)) * 0.8
        # 限制初始区域
        center = size // 2
        y, x = jnp.ogrid[:size, :size]
        mask = ((x - center)**2 + (y - center)**2) < 100
        field = field * mask.astype(float)
        
        def step_fn(f, _):
            new_f = lenia_step(f, kernel)
            return new_f, new_f
        
        _, history = jax.lax.scan(step_fn, field, jnp.arange(steps))
        return history
    
    histories = jax.vmap(single_eval)(keys)
    return histories


def orbium_fitness(history, target_kernel, steps=200):
    """
    Orbium-specific 适应度
    
    目标:
    1. 存活到结束 (alive)
    2. 模式形状接近 Orbium (pattern_similarity)
    3. 有动态行为 (dynamic)
    
    评估方法: 用 Orbium 核跑相同的初始条件，比较轨迹
    """
    size = history.shape[-1]
    field = orbium_seed(size)
    
    # 用学到的核和目标核各自演化
    def step_fn(f, _):
        return lenia_step(f, target_kernel), f
    
    _, target_history = jax.lax.scan(step_fn, field, jnp.arange(steps))
    
    # 1. 存活分数
    alive = jnp.sum(history > 0.1, axis=(1, 2)) > 100
    alive_score = jnp.sum(alive) / steps
    
    # 2. 模式相似度 (最后 50 步的平均 L2 距离)
    final_self = history[-50:]
    final_target = target_history[-50:]
    # 离散化比较 (因为 Orbium 的精确位置可能偏移)
    def binarize(f):
        return (f > 0.2).astype(float)
    self_bin = jax.vmap(binarize)(final_self)
    target_bin = jax.vmap(binarize)(final_target)
    # IoU-like similarity
    intersection = jnp.sum(self_bin * target_bin, axis=(1, 2))
    union = jnp.sum(jnp.maximum(self_bin, target_bin), axis=(1, 2)) + 1e-8
    iou = jnp.mean(intersection / union)
    
    # 3. 动态分数
    if steps > 1:
        diff = jnp.abs(history[1:] - history[:-1])
        dynamic_score = jnp.mean(diff)
    else:
        dynamic_score = 0.0
    
    # 4. 质心稳定性 (Orbium 应保持在中心)
    final_field = history[-1]
    total_mass = jnp.sum(final_field) + 1e-8
    y_idx = jnp.arange(size).reshape(-1, 1)
    x_idx = jnp.arange(size).reshape(1, -1)
    cy = jnp.sum(y_idx * final_field) / total_mass
    cx = jnp.sum(x_idx * final_field) / total_mass
    centroid_dist = jnp.sqrt((cy - size/2)**2 + (cx - size/2)**2) / size
    centroid_score = 1.0 - centroid_dist
    
    # 总分
    total = (
        alive_score * 3.0 +
        iou * 5.0 +
        dynamic_score * 2.0 +
        centroid_score * 1.0
    )
    
    return total


def multi_eval_fitness(key, kernel_params, target_kernel, steps=200, size=64, n_evals=3):
    """多评估平均适应度"""
    histories = run_lenia_multi_eval(key, kernel_params, steps, size, n_evals)
    
    def single_fitness(h):
        return orbium_fitness(h, target_kernel, steps)
    
    scores = jax.vmap(single_fitness)(histories)
    return jnp.mean(scores)


# ─────────────────────────────────────────────
# Adam 优化器 (纯 JAX 状态)
# ─────────────────────────────────────────────

class AdamState:
    """Adam optimizer state for NamedTuple params.
    Avoids jax.tree_util.tree_map multi-input unpacking bug by iterating fields."""
    def __init__(self, params, lr=0.001, beta1=0.9, beta2=0.999, eps=1e-8):
        self.lr = lr
        self.beta1 = beta1
        self.beta2 = beta2
        self.eps = eps
        self.t = 0
        # Initialize moment buffers with zeros matching each param field
        self.m = {f: jnp.zeros_like(getattr(params, f)) for f in params._fields}
        self.v = {f: jnp.zeros_like(getattr(params, f)) for f in params._fields}
    
    def step(self, params, grads):
        """Return updated params. Mutates internal state."""
        self.t += 1
        t = self.t
        lr_t = self.lr * jnp.sqrt(1 - self.beta2**t) / (1 - self.beta1**t)
        
        new_fields = {}
        for field in params._fields:
            p = getattr(params, field)
            g = getattr(grads, field)
            # Update moments
            self.m[field] = self.beta1 * self.m[field] + (1 - self.beta1) * g
            self.v[field] = self.beta2 * self.v[field] + (1 - self.beta2) * g**2
            # Update param
            new_fields[field] = p - lr_t * self.m[field] / (jnp.sqrt(self.v[field]) + self.eps)
        
        return type(params)(**new_fields)


# ─────────────────────────────────────────────
# 主优化循环
# ─────────────────────────────────────────────

def gradient_optimization_v2(key, steps=200, iterations=100, lr=0.003):
    """改进版梯度优化，用 Adam + 多评估 + 渐进步长"""
    print("=" * 60)
    print("Neural Lenia v2 — Orbium 梯度优化")
    print("=" * 60)
    
    # 生成目标 Orbium 核
    target_kernel = orbium_kernel(R=13)
    
    # 初始化参数
    k1, k2 = jax.random.split(key)
    params = init_neural_kernel(k1, hidden_dim=32)
    
    # Adam 优化器
    adam = AdamState(params, lr=lr)
    
    best_params = params
    best_score = 0.0
    optimization_history = []
    
    for i in range(iterations):
        k1, k2 = jax.random.split(k2)
        
        # 渐进步长: 前 30 轮用 100 步，后面用 200 步
        current_steps = min(100 + (i * 3), steps)
        
        # 多评估适应度
        score = multi_eval_fitness(k1, params, target_kernel, 
                                    steps=current_steps, n_evals=3)
        
        # 损失函数
        def loss_fn(p):
            return -multi_eval_fitness(k1, p, target_kernel, 
                                        steps=current_steps, n_evals=3)
        
        grads = jax.grad(loss_fn)(params)
        
        # 梯度裁剪
        def clip_grad(g):
            return jnp.clip(g, -1.0, 1.0)
        grads = jax.tree_util.tree_map(clip_grad, grads)
        
        # Adam 更新
        params = adam.step(params, grads)
        
        # 记录
        optimization_history.append({
            'iteration': i,
            'score': float(score),
            'steps': current_steps,
        })
        
        if score > best_score:
            best_score = score
            best_params = params
        
        if i % 10 == 0:
            print(f"Iter {i:3d}: score={score:.3f} (steps={current_steps}) best={best_score:.3f}")
    
    print(f"\n{'='*60}")
    print(f"优化完成! 最佳分数: {best_score:.3f}")
    print(f"{'='*60}")
    
    return best_params, best_score, optimization_history, target_kernel


# ─────────────────────────────────────────────
# 结果可视化
# ─────────────────────────────────────────────

def visualize_comparison(learned_params, target_kernel, save_path=None):
    """对比学习到的核和 Orbium 核"""
    learned_kernel = generate_kernel_grid(learned_params, R=13)
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    
    # 第一行: 核
    im0 = axes[0, 0].imshow(target_kernel, cmap='viridis')
    axes[0, 0].set_title('Orbium Target Kernel')
    plt.colorbar(im0, ax=axes[0, 0])
    
    im1 = axes[0, 1].imshow(learned_kernel, cmap='viridis')
    axes[0, 1].set_title('Learned Neural Kernel')
    plt.colorbar(im1, ax=axes[0, 1])
    
    diff = jnp.abs(learned_kernel - target_kernel)
    im2 = axes[0, 2].imshow(diff, cmap='hot')
    axes[0, 2].set_title(f'|Difference| (MSE={jnp.mean(diff**2):.4f})')
    plt.colorbar(im2, ax=axes[0, 2])
    
    # 第二行: 径向轮廓
    center = learned_kernel.shape[0] // 2
    radii = jnp.arange(0, len(target_kernel) - center)
    
    target_profile = target_kernel[center, center:]
    learned_profile = learned_kernel[center, center:]
    
    axes[1, 0].plot(radii, target_profile, 'b-', label='Orbium', linewidth=2)
    axes[1, 0].plot(radii, learned_profile, 'r--', label='Learned', linewidth=2)
    axes[1, 0].set_xlabel('Radius')
    axes[1, 0].set_ylabel('Kernel Value')
    axes[1, 0].set_title('Radial Profile Comparison')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # 模拟结果对比
    seed = orbium_seed(64)
    
    def simulate(kernel, field, n_steps=200):
        def step(f, _):
            return lenia_step(f, kernel), f
        _, hist = jax.lax.scan(step, field, jnp.arange(n_steps))
        return hist
    
    target_hist = simulate(target_kernel, seed)
    learned_hist = simulate(learned_kernel, seed)
    
    axes[1, 1].imshow(target_hist[-1], cmap='viridis')
    axes[1, 1].set_title('Orbium t=200')
    axes[1, 1].axis('off')
    
    axes[1, 2].imshow(learned_hist[-1], cmap='viridis')
    axes[1, 2].set_title('Learned t=200')
    axes[1, 2].axis('off')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved to {save_path}")
    
    plt.show()


def plot_optimization_history(history, save_path=None):
    """绘制优化历史"""
    fig, ax = plt.subplots(figsize=(10, 4))
    iters = [h['iteration'] for h in history]
    scores = [h['score'] for h in history]
    
    ax.plot(iters, scores, 'b-', alpha=0.7, linewidth=1)
    ax.scatter(iters, scores, c=scores, cmap='viridis', s=20, alpha=0.5)
    
    # 最佳
    best_idx = np.argmax(scores)
    ax.scatter([iters[best_idx]], [scores[best_idx]], 
               color='red', s=100, zorder=5, marker='*')
    
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Fitness Score')
    ax.set_title('Neural Lenia Optimization History')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    plt.show()


# ─────────────────────────────────────────────
# 主入口
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Neural Lenia v2 Optimization')
    parser.add_argument('--iterations', type=int, default=100, help='优化迭代次数')
    parser.add_argument('--steps', type=int, default=200, help='每轮模拟步数')
    parser.add_argument('--lr', type=float, default=0.003, help='学习率')
    parser.add_argument('--seed', type=int, default=42, help='随机种子')
    parser.add_argument('--output', type=str, default='../output/neural_lenia_v2', help='输出前缀')
    args = parser.parse_args()
    
    key = jax.random.PRNGKey(args.seed)
    
    # 优化
    best_params, best_score, history, target_kernel = gradient_optimization_v2(
        key, steps=args.steps, iterations=args.iterations, lr=args.lr
    )
    
    # 保存结果
    result = {
        'best_score': float(best_score),
        'iterations': args.iterations,
        'steps': args.steps,
        'lr': args.lr,
        'seed': args.seed,
    }
    with open(f'{args.output}_result.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    # 可视化
    visualize_comparison(best_params, target_kernel, 
                         save_path=f'{args.output}_comparison.png')
    plot_optimization_history(history, 
                              save_path=f'{args.output}_history.png')
    
    print(f"\n结果已保存到 {args.output}_*")
