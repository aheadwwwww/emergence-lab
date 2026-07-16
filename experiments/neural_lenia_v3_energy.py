"""
Neural Lenia v3 — Energy-Constrained Evolution

灵感来源: ALIEN (chrxh/alien) 的能量经济系统
- Depot cells store energy, Digestor cells harvest, Constructor costs energy
→ 自然选择压力，只有高效模式存活

核心改进:
1. 每个像素有"能量预算" — 生长消耗能量，死亡释放能量
2. 扩散能量场 — 相邻像素间能量流动
3. 神经网络不仅学核形状，还学能量效率
4. 多地形的能量分布（富/贫/梯度）
5. 只有能量高效的核才能长期存活

Date: 2026-07-16
"""

import jax
import jax.numpy as jnp
from functools import partial
import numpy as np
import matplotlib.pyplot as plt
import json

# 复用基础组件
from neural_lenia import (
    init_neural_kernel, neural_kernel_forward,
    generate_kernel_grid, NeuralKernelParams
)


# ══════════════════════════════════════════════
# Part 1: 能量感知的 Lenia
# ══════════════════════════════════════════════

def energy_lenia_step(field, energy, kernel, dt=0.1, growth_cost=0.05, base_decay=0.001):
    """
    带能量约束的 Lenia 步进
    
    规则:
    - 生长消耗能量: field 增加需要消耗 energy
    - 没有能量的区域无法增长
    - 能量从高浓度向低浓度扩散
    - 死亡区域释放能量回环境
    
    Args:
        field: (H, W) 场值 [0, 1]
        energy: (H, W) 能量值 [0, 1]
        kernel: 核
        dt: 时间步长
        growth_cost: 单位生长消耗的能量
        base_decay: 基础能量衰减
    
    Returns:
        new_field, new_energy
    """
    # 标准 Lenia 计算 (但添加能量门控)
    potential = jax.scipy.signal.convolve2d(field, kernel, mode='same')
    growth = jnp.clip(potential, 0, 1)
    
    # 能量门控: 只有在能量充足时才能生长
    energy_gate = jnp.clip(energy / growth_cost, 0, 1)
    
    # 场更新
    df = dt * growth * energy_gate
    new_field = jnp.clip(field + df, 0, 1)
    
    # 能量更新: 消耗 = 生长量, 释放 = 死亡量
    energy_consumed = dt * growth * field * growth_cost  # 生长消耗
    death_release = dt * jnp.maximum(0, field - new_field) * 0.5  # 死亡释放50%
    
    # 能量扩散 (简单拉普拉斯)
    kernel_lap = jnp.array([[0, 0.25, 0],
                             [0.25, -1, 0.25],
                             [0, 0.25, 0]])
    diffusion = 0.1 * jax.scipy.signal.convolve2d(energy, kernel_lap, mode='same')
    
    new_energy = jnp.clip(energy - energy_consumed + death_release + diffusion - base_decay, 0, 1)
    
    return new_field, new_energy


def create_energy_landscape(size, landscape_type='uniform'):
    """创建不同的能量地形"""
    if landscape_type == 'uniform':
        return jnp.ones((size, size)) * 0.5
    
    elif landscape_type == 'rich_center':
        y, x = jnp.ogrid[:size, :size]
        center = size // 2
        dist = jnp.sqrt((x - center)**2 + (y - center)**2) / (size // 2)
        return 0.8 - 0.6 * jnp.clip(dist, 0, 1)  # 中心高，边缘低
    
    elif landscape_type == 'gradient':
        y, x = jnp.ogrid[:size, :size]
        return 0.3 + 0.4 * (x / size)  # 左→右梯度
    
    elif landscape_type == 'patches':
        key = jax.random.PRNGKey(sum(ord(c) for c in landscape_type))
        noise = jax.random.uniform(key, (size, size))
        # 平滑化
        kernel_smooth = jnp.ones((5, 5)) / 25
        smoothed = jax.scipy.signal.convolve2d(noise, kernel_smooth, mode='same')
        return 0.3 + 0.4 * smoothed
    
    elif landscape_type == 'scarce':
        return jnp.ones((size, size)) * 0.15  # 稀缺环境
    
    else:
        return jnp.ones((size, size)) * 0.5


# ══════════════════════════════════════════════
# Part 2: 多核竞争模拟
# ══════════════════════════════════════════════

def multi_kernel_competition(key, kernel_params_list, steps=500, size=128, 
                              landscape='uniform', growth_cost=0.05):
    """
    多核竞争: 多个核共享同一个能量场和空间
    
    每个核占据网格的一部分，争夺有限能量
    
    Returns:
        histories: (n_kernels, steps, size, size)
        energy_history: (steps, size, size)
        survival: (n_kernels,) 最终存活率
    """
    n_kernels = len(kernel_params_list)
    
    # 生成所有核
    kernels = []
    for params in kernel_params_list:
        k = generate_kernel_grid(params, R=13)
        kernels.append(k)
    
    # 初始化: 每个核占据一个区域
    fields = []
    for i in range(n_kernels):
        y, x = jnp.ogrid[:size, :size]
        # 分配区域: 均匀分布
        col = i % 3
        row = i // 3
        cx = size * (col + 0.5) / 3
        cy = size * (row + 0.5) / ((n_kernels + 2) // 3)
        radius = size / 6
        mask = ((x - cx)**2 + (y - cy)**2) < radius**2
        f = mask.astype(float) * 0.6
        fields.append(f)
    
    # 能量初始化
    energy = create_energy_landscape(size, landscape)
    
    def step_fn(carry, _):
        fields, energy = carry
        
        new_fields = []
        total_consumed = jnp.zeros((size, size))
        total_released = jnp.zeros((size, size))
        
        for i, (field, kernel) in enumerate(zip(fields, kernels)):
            new_f, new_e = energy_lenia_step(field, energy, kernel, 
                                              growth_cost=growth_cost)
            new_fields.append(new_f)
        
        # 合并死亡释放
        for i, (field, new_f) in enumerate(zip(fields, new_fields)):
            death = jnp.maximum(0, field - new_f) * 0.5
            energy = jnp.clip(energy + death, 0, 1)
        
        # 能量自然恢复
        base_recovery = 0.002
        energy = jnp.clip(energy + base_recovery, 0, 1)
        
        return (new_fields, energy), (jnp.stack(new_fields), energy)
    
    (_, _), (histories, energy_history) = jax.lax.scan(
        step_fn, (fields, energy), jnp.arange(steps)
    )
    
    # 计算存活率
    survival = []
    for i in range(n_kernels):
        final = histories[-1, i]
        alive = jnp.sum(final > 0.1)
        survival.append(float(alive) / (size * size))
    
    return histories, energy_history, survival


# ══════════════════════════════════════════════
# Part 3: 能量效率适应度
# ══════════════════════════════════════════════

def energy_efficiency_fitness(history, energy_history):
    """
    能量效率适应度
    
    不仅看存活，还看:
    1. 存活时间 (longevity)
    2. 能量效率 (biomass / energy consumed)
    3. 稳态能力 (低波动)
    """
    steps = history.shape[0]
    
    # 1. 长期存活
    alive_mask = jnp.sum(history > 0.1, axis=(1, 2)) > 10
    longevity = jnp.mean(alive_mask.astype(float))
    
    # 2. 最后20步的生物量 (避免短暂爆发)
    final_biomass = jnp.mean(history[-20:])
    
    # 3. 能量效率: 生物量 / 消耗的能量
    energy_consumed = jnp.mean(jnp.abs(energy_history[1:] - energy_history[:-1]))
    efficiency = final_biomass / (energy_consumed + 1e-6)
    
    # 4. 稳定性 (生物量标准差越低越好)
    biomass_ts = jnp.mean(history[-50:], axis=(1, 2))
    stability = 1.0 / (jnp.std(biomass_ts) + 0.1)
    
    # 加权总分
    score = (
        longevity * 3.0 +
        final_biomass * 2.0 +
        efficiency * 1.0 +
        stability * 1.0
    )
    
    return score


# ══════════════════════════════════════════════
# Part 4: 进化算法 (带能量选择)
# ══════════════════════════════════════════════

def energy_based_evolution(key, population_size=20, generations=50, 
                            landscape='scarce', growth_cost=0.08):
    """
    基于能量效率的进化
    
    低能量 + 高生长成本 → 强烈选择压力
    只有能量高效的核才能生存
    """
    print("=" * 60)
    print("Neural Lenia v3 — Energy-Constrained Evolution")
    print(f"Landscape: {landscape}, Growth Cost: {growth_cost}")
    print("=" * 60)
    
    # 初始化种群
    keys = jax.random.split(key, population_size)
    population = [init_neural_kernel(k, hidden_dim=32) for k in keys]
    
    best_score_overall = 0
    best_params_overall = None
    
    for gen in range(generations):
        k1, key = jax.random.split(key)
        
        # 评估所有个体
        scores = []
        for i, params in enumerate(population):
            kp, k1 = jax.random.split(k1)
            history, energy_hist, survival = multi_kernel_competition(
                kp, [params], steps=200, size=64, 
                landscape=landscape, growth_cost=growth_cost
            )
            score = energy_efficiency_fitness(history[0], energy_hist)
            scores.append(float(score))
        
        scores = jnp.array(scores)
        
        # 选择 top 50%
        n_keep = population_size // 2
        top_indices = jnp.argsort(scores)[::-1][:n_keep]
        
        best_gen_score = scores[top_indices[0]]
        if best_gen_score > best_score_overall:
            best_score_overall = best_gen_score
            best_params_overall = population[int(top_indices[0])]
        
        print(f"Gen {gen:3d}: best={best_gen_score:.3f} | "
              f"mean={jnp.mean(scores):.3f} | "
              f"overall_best={best_score_overall:.3f}")
        
        # 生成下一代
        new_population = []
        for i in range(population_size):
            p1_idx = int(top_indices[jax.random.randint(k1, (), 0, n_keep)])
            p2_idx = int(top_indices[jax.random.randint(k1, (), 0, n_keep)])
            k1, km = jax.random.split(k1)
            
            if p1_idx == p2_idx:
                # 变异
                child = mutate_params(km, population[p1_idx])
            else:
                # 交叉 + 变异
                child = crossover_and_mutate(km, population[p1_idx], population[p2_idx])
            
            new_population.append(child)
        
        population = new_population
    
    return best_params_overall, best_score_overall


def mutate_params(key, params, mutation_rate=0.1, sigma=0.05):
    """高斯变异"""
    keys = jax.random.split(key, len(params._fields))
    
    new_fields = {}
    for i, field in enumerate(params._fields):
        val = getattr(params, field)
        noise = jax.random.normal(keys[i], val.shape) * sigma
        mask = jax.random.bernoulli(keys[i], mutation_rate, val.shape)
        new_val = val + noise * mask
        new_fields[field] = new_val
    
    return type(params)(**new_fields)


def crossover_and_mutate(key, p1, p2, crossover_rate=0.5, mutation_rate=0.1):
    """均匀交叉 + 变异"""
    k1, k2 = jax.random.split(key)
    
    new_fields = {}
    for field in p1._fields:
        v1 = getattr(p1, field)
        v2 = getattr(p2, field)
        # 均匀交叉
        mask = jax.random.bernoulli(k1, crossover_rate, v1.shape)
        crossed = v1 * mask + v2 * (1 - mask)
        # 变异
        noise = jax.random.normal(k2, crossed.shape) * 0.03
        mut_mask = jax.random.bernoulli(k2, mutation_rate, crossed.shape)
        new_fields[field] = crossed + noise * mut_mask
    
    return type(p1)(**new_fields)


# ══════════════════════════════════════════════
# Part 5: 可视化
# ══════════════════════════════════════════════

def visualize_competition(histories, energy_history, survivals, save_path=None):
    """可视化多核竞争结果"""
    n_kernels = histories.shape[1]
    steps = histories.shape[0]
    
    fig, axes = plt.subplots(2, max(3, n_kernels), 
                              figsize=(4 * max(3, n_kernels), 8))
    
    # 时间轴采样
    t_samples = [0, steps//3, 2*steps//3, steps-1]
    
    for row, t in enumerate(t_samples[:2]):
        for i in range(n_kernels):
            ax = axes[row, i] if n_kernels > 1 else axes[row, 0]
            im = ax.imshow(histories[t, i], cmap='viridis', vmin=0, vmax=1)
            ax.set_title(f'Kernel {i} (t={t})' if row == 0 else '')
            ax.axis('off')
    
    # 第二行: 存活率柱状图 + 能量场
    if n_kernels > 1:
        ax_bar = axes[1, :n_kernels]
        colors = plt.cm.tab10(range(n_kernels))
        for i in range(n_kernels):
            ax_bar[i].bar([0], [survivals[i]], color=colors[i])
            ax_bar[i].set_ylim(0, max(survivals) * 1.2)
            ax_bar[i].set_title(f'Survival: {survivals[i]:.3f}')
            ax_bar[i].set_xticks([])
    else:
        # 能量场最终状态
        ax_energy = axes[1, 0] if n_kernels > 1 else axes[1, 0]
        im_e = ax_energy.imshow(energy_history[-1], cmap='YlOrRd', vmin=0, vmax=1)
        ax_energy.set_title(f'Final Energy Field')
        ax_energy.axis('off')
        plt.colorbar(im_e, ax=ax_energy)
    
    plt.suptitle('Multi-Kernel Competition under Energy Constraints', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    plt.show()


# ══════════════════════════════════════════════
# Part 6: 独立运行 (单核能量约束)
# ══════════════════════════════════════════════

def run_energy_lenia(params, steps=500, size=128, landscape='uniform', 
                      growth_cost=0.05, seed=42):
    """
    运行单个能量约束 Lenia，返回场和能量历史
    """
    key = jax.random.PRNGKey(seed)
    
    # 生成核
    kernel = generate_kernel_grid(params, R=13)
    
    # 初始化场 (中央圆斑)
    y, x = jnp.ogrid[:size, :size]
    center = size // 2
    mask = ((x - center)**2 + (y - center)**2) < (size // 6)**2
    field = mask.astype(float) * 0.6
    
    # 初始化能量
    energy = create_energy_landscape(size, landscape)
    
    def step_fn(carry, _):
        f, e = carry
        new_f, new_e = energy_lenia_step(f, e, kernel, growth_cost=growth_cost)
        return (new_f, new_e), (new_f, new_e)
    
    (_, _), (field_hist, energy_hist) = jax.lax.scan(
        step_fn, (field, energy), jnp.arange(steps)
    )
    
    return field_hist, energy_hist


# ══════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['single', 'evolve', 'compete'], default='single')
    parser.add_argument('--generations', type=int, default=30)
    parser.add_argument('--pop_size', type=int, default=16)
    parser.add_argument('--steps', type=int, default=300)
    parser.add_argument('--size', type=int, default=128)
    parser.add_argument('--landscape', default='scarce')
    parser.add_argument('--growth_cost', type=float, default=0.08)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    
    key = jax.random.PRNGKey(args.seed)
    
    if args.mode == 'single':
        print(f"Running single energy-constrained Lenia...")
        print(f"Landscape: {args.landscape}, Growth Cost: {args.growth_cost}")
        
        params = init_neural_kernel(key, hidden_dim=32)
        field_hist, energy_hist = run_energy_lenia(
            params, steps=args.steps, size=args.size,
            landscape=args.landscape, growth_cost=args.growth_cost
        )
        
        # Quick stats
        alive_end = jnp.sum(field_hist[-1] > 0.1)
        print(f"Alive pixels at end: {alive_end} / {args.size**2} "
              f"({100*alive_end/args.size**2:.1f}%)")
        print(f"Final energy: mean={float(jnp.mean(energy_hist[-1])):.3f}")
        
        # Visualize
        fig, axes = plt.subplots(2, 4, figsize=(16, 8))
        t_samples = [0, args.steps//4, args.steps//2, args.steps-1]
        for i, t in enumerate(t_samples):
            axes[0, i].imshow(field_hist[t], cmap='viridis', vmin=0, vmax=1)
            axes[0, i].set_title(f'Field t={t}')
            axes[0, i].axis('off')
            axes[1, i].imshow(energy_hist[t], cmap='YlOrRd', vmin=0, vmax=1)
            axes[1, i].set_title(f'Energy t={t}')
            axes[1, i].axis('off')
        plt.suptitle(f'Energy-Constrained Lenia ({args.landscape})')
        plt.tight_layout()
        plt.savefig('../output/energy_lenia_single.png', dpi=150)
        plt.show()
    
    elif args.mode == 'evolve':
        best_params, best_score = energy_based_evolution(
            key, population_size=args.pop_size, generations=args.generations,
            landscape=args.landscape, growth_cost=args.growth_cost
        )
        
        print(f"\n进化完成! 最佳分数: {best_score:.3f}")
        
        # 可视化最佳
        field_hist, energy_hist = run_energy_lenia(
            best_params, steps=args.steps, size=args.size,
            landscape=args.landscape, growth_cost=args.growth_cost
        )
        
        # 保存
        import pickle
        with open('../output/energy_lenia_best_params.pkl', 'wb') as f:
            pickle.dump(best_params, f)
    
    elif args.mode == 'compete':
        print("Multi-kernel competition...")
        n_kernels = 4
        kernel_params = [init_neural_kernel(jax.random.PRNGKey(42 + i), hidden_dim=32) 
                        for i in range(n_kernels)]
        
        histories, energy_hist, survivals = multi_kernel_competition(
            key, kernel_params, steps=args.steps, size=args.size,
            landscape=args.landscape, growth_cost=args.growth_cost
        )
        
        for i, s in enumerate(survivals):
            print(f"  Kernel {i}: survival={s:.4f}")
        
        visualize_competition(histories, energy_hist, survivals,
                             save_path='../output/energy_competition.png')
