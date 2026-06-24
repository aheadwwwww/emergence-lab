"""
#021 Digital Evolution — 数字进化实验
探索计算系统中的进化动力学：复杂天花板、开放式搜索、POET 式环境生成

核心概念：
1. 适应度景观上的种群进化
2. 复杂天花板：简单环境代理变"聪明"→环境不够用→需要更复杂环境→天花板
3. POET (Paired Open-Ended Trailblazer)：环境和agent共同进化
4. 进化停滞 vs 突破：什么条件下产生质变
5. 多样性 vs 最优性：进化的双目标张力

实验结构：
- 实验1: Fitness Landscape Navigator — 种群爬山，测量复杂天花板
- 实验2: Co-evolving Environment — 种群和环境螺旋上升
- 实验3: Open-Ended Search — 新颖度搜索 vs 适应度搜索
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib
matplotlib.use('Agg')

# ─── 实验 1: 适应度景观上的种群进化 ───────────────────────────────

def generate_rugged_landscape(size=100, n_peaks=15, noise=0.05):
    """生成多峰适应度景观（NK-landscape风格）"""
    x = np.linspace(0, 1, size)
    landscape = np.zeros(size)
    
    # 随机峰值
    centers = np.random.uniform(0.1, 0.9, n_peaks)
    heights = np.random.uniform(0.3, 1.0, n_peaks)
    widths = np.random.uniform(0.02, 0.12, n_peaks)
    
    for c, h, w in zip(centers, heights, widths):
        landscape += h * np.exp(-((x - c) ** 2) / (2 * w ** 2))
    
    landscape += noise * np.random.randn(size)
    landscape = np.maximum(landscape, 0)
    return x, landscape / landscape.max()

def evolve_population(x, landscape, pop_size=50, generations=200, 
                      mutation_rate=0.05, selection_pressure=0.3):
    """在适应度景观上进化种群"""
    size = len(x)
    
    # 随机初始化
    population = np.random.randint(0, size, pop_size)
    fitness_history = []
    diversity_history = []
    best_history = []
    pop_center_history = []
    
    for gen in range(generations):
        # 适应度评估
        fitness = landscape[population]
        fitness_history.append(fitness.mean())
        best_history.append(fitness.max())
        
        # 多样性：种群占据的独特位置数
        diversity_history.append(len(np.unique(population)))
        
        # 种群中心
        pop_center_history.append(population.mean())
        
        # 选择（截断选择）
        sorted_idx = np.argsort(fitness)[::-1]
        elite_count = max(2, int(pop_size * (1 - selection_pressure)))
        
        # 精英
        new_pop = population[sorted_idx[:elite_count]].copy()
        
        # 繁殖填充
        while len(new_pop) < pop_size:
            parent = new_pop[np.random.randint(0, len(new_pop))]
            child = parent + np.random.randint(-int(size * mutation_rate), 
                                                int(size * mutation_rate) + 1)
            child = np.clip(child, 0, size - 1)
            new_pop = np.append(new_pop, child)
        
        population = new_pop[:pop_size]
    
    return np.array(fitness_history), np.array(diversity_history), \
           np.array(best_history), np.array(pop_center_history), population

# ─── 实验 2: 环境-种群共同进化 (POET 风格) ─────────────────────────

class SimpleEnvironment:
    """简化版环境：有阻力和障碍物"""
    def __init__(self, difficulty, num_obstacles=0):
        self.difficulty = difficulty  # 0-1, 越高越难
        self.obstacles = num_obstacles
        self.peak_shift = difficulty * 0.3  # 峰值偏移
        
    def fitness(self, trait, genome_size=100):
        """适应度 = 匹配当前环境难度的能力"""
        # 困难环境需要更精细的特征
        target = 0.3 + self.peak_shift  # 环境难度改变最优位置
        precision = 0.05 + self.difficulty * 0.15  # 困难环境要求更精确
        
        # 高斯适应度函数
        dist = abs(trait / genome_size - target)
        return np.exp(-dist ** 2 / (2 * precision ** 2))

def coevolution_experiment(n_environments=8, genome_size=100, 
                           pop_per_env=20, generations=150):
    """环境和种群共同进化"""
    # 初始化环境（从易到难）
    envs = [SimpleEnvironment(d * 0.12) for d in range(n_environments)]
    
    # 每个环境一个亚种群
    populations = {i: np.random.randint(0, genome_size, pop_per_env)
                    for i in range(n_environments)}
    
    history = {
        'env_fitness': {i: [] for i in range(n_environments)},
        'env_difficulty': [],
        'migration_events': []
    }
    
    for gen in range(generations):
        # 评估所有种群
        env_avg_fitness = {}
        for i, env in enumerate(envs):
            pop = populations[i]
            fit = np.array([env.fitness(t, genome_size) for t in pop])
            env_avg_fitness[i] = fit.mean()
            history['env_fitness'][i].append(fit.max())
        
        # 环境进化：表现好的环境可以产生更难的子环境
        if gen % 20 == 0 and gen > 0:
            best_env = max(env_avg_fitness, key=env_avg_fitness.get)
            # 如果最好环境的适应度超过阈值，增加新环境
            if env_avg_fitness[best_env] > 0.6 and len(envs) < 15:
                new_diff = min(1.0, envs[best_env].difficulty + 0.08)
                envs.append(SimpleEnvironment(new_diff))
                populations[len(populations)] = np.random.randint(0, genome_size, pop_per_env)
                history['env_fitness'][len(populations) - 1] = []
                history['migration_events'].append((gen, 'new_env', new_diff))
        
        history['env_difficulty'].append(np.mean([e.difficulty for e in envs]))
        
        # 迁移：每10代，表现最差的种群可以部分迁移到相邻环境
        if gen % 10 == 0 and gen > 0:
            n_envs_now = len(envs)
            for i in range(n_envs_now):
                if i in env_avg_fitness and env_avg_fitness[i] < 0.2:
                    # 从相邻更好环境迁移10%
                    donor = (i + 1) % n_envs_now
                    if donor in env_avg_fitness and env_avg_fitness[donor] > env_avg_fitness[i]:
                        n_migrants = max(1, pop_per_env // 10)
                        samples = np.random.choice(populations[donor], n_migrants)
                        replace_idx = np.random.choice(pop_per_env, n_migrants, replace=False)
                        populations[i][replace_idx] = samples
                        history['migration_events'].append((gen, i, donor))
        
        # 种群内进化（突变选择）
        for i in range(len(envs)):
            pop = populations[i]
            env = envs[i]
            fits = np.array([env.fitness(t, genome_size) for t in pop])
            
            # Elite selection
            sorted_idx = np.argsort(fits)[::-1]
            elite_n = max(1, pop_per_env // 3)
            new_pop = pop[sorted_idx[:elite_n]].copy()
            
            # 突变填充
            while len(new_pop) < pop_per_env:
                parent = new_pop[np.random.randint(0, len(new_pop))]
                child = parent + np.random.randint(-5, 6)
                child = np.clip(child, 0, genome_size - 1)
                new_pop = np.append(new_pop, child)
            
            populations[i] = new_pop[:pop_per_env]
    
    return envs, populations, history

# ─── 实验 3: 新颖度搜索 vs 适应度搜索 ──────────────────────────────

def novelty_search(landscape, pop_size=30, generations=150, 
                   novelty_threshold=0.01):
    """新颖度搜索：奖励勘探新区域而非最大化适应度"""
    size = len(landscape)
    
    # 存档已访问位置
    archive = set()
    population = np.random.randint(0, size, pop_size)
    
    novelty_history = []
    fitness_history = []
    coverage_history = []
    
    for gen in range(generations):
        fitness = landscape[population]
        fitness_history.append(fitness.mean())
        
        # 新颖度：到存档中最接近个体的距离
        novelties = np.zeros(pop_size)
        for i, pos in enumerate(population):
            if not archive:
                novelties[i] = 1.0
            else:
                archive_arr = np.array(list(archive))
                novelties[i] = np.min(np.abs(pos - archive_arr)) / size
        
        novelty_history.append(novelties.mean())
        
        # 加入存档
        for pos in population:
            archive.add(pos)
        coverage_history.append(len(archive))
        
        # 选择：新颖度 + 适应度的加权
        score = novelties * 0.7 + fitness * 0.3
        sorted_idx = np.argsort(score)[::-1]
        elite = population[sorted_idx[:pop_size // 2]]
        
        # 突变
        new_pop = elite.copy()
        while len(new_pop) < pop_size:
            parent = new_pop[np.random.randint(0, len(new_pop))]
            child = parent + np.random.randint(-int(size * 0.05), int(size * 0.05) + 1)
            child = np.clip(child, 0, size - 1)
            new_pop = np.append(new_pop, child)
        
        population = new_pop[:pop_size]
    
    return np.array(fitness_history), np.array(novelty_history), \
           np.array(coverage_history), archive

# ─── 可视化 ─────────────────────────────────────────────────────────

def main():
    np.random.seed(42)
    
    fig = plt.figure(figsize=(18, 14))
    gs = GridSpec(3, 3, figure=fig, hspace=0.4, wspace=0.35)
    
    # ═══ 实验1: 适应度景观上的种群进化 ═══
    x, landscape = generate_rugged_landscape(size=200, n_peaks=20)
    fit_hist, div_hist, best_hist, center_hist, final_pop = \
        evolve_population(x, landscape, pop_size=60, generations=150)
    
    # 1A: 适应度景观 + 最终种群
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(x, landscape, 'k-', linewidth=1.5, alpha=0.7, label='Fitness Landscape')
    ax1.scatter(x[final_pop], landscape[final_pop], c='red', s=20, 
                alpha=0.6, zorder=5, label='Final Population')
    ax1.set_title('Fitness Landscape with\nEvolved Population', fontsize=11, fontweight='bold')
    ax1.set_xlabel('Genome Position')
    ax1.set_ylabel('Fitness')
    ax1.legend(fontsize=8, loc='upper right')
    ax1.grid(True, alpha=0.3)
    
    # 1B: 适应度 + 多样性时间线
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(fit_hist, 'b-', label='Mean Fitness', linewidth=1.5, alpha=0.8)
    ax2.plot(best_hist, 'b--', label='Best Fitness', linewidth=1, alpha=0.5)
    ax2_twin = ax2.twinx()
    ax2_twin.plot(div_hist, 'orange', label='Diversity', linewidth=1.5, alpha=0.8)
    ax2.set_title('Fitness & Diversity Over Generations', fontsize=11, fontweight='bold')
    ax2.set_xlabel('Generation')
    ax2.set_ylabel('Fitness', color='b')
    ax2_twin.set_ylabel('Diversity (# unique)', color='orange')
    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, fontsize=7)
    ax2.grid(True, alpha=0.3)
    
    # 1C: 种群中心漂移
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.plot(center_hist, 'g-', linewidth=1.5)
    ax3.fill_between(range(len(center_hist)), 
                      center_hist - 20, center_hist + 20, alpha=0.15)
    ax3.axhline(y=100, color='gray', linestyle='--', alpha=0.5, label='Center')
    ax3.set_title('Population Center Position', fontsize=11, fontweight='bold')
    ax3.set_xlabel('Generation')
    ax3.set_ylabel('Mean Genome Position')
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)
    
    # ═══ 实验2: 环境-种群共进化 ═══
    envs, pops, co_history = coevolution_experiment()
    
    # 2A: 各环境的适应度
    ax4 = fig.add_subplot(gs[1, 0])
    colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(envs)))
    for i in range(len(envs)):
        if co_history['env_fitness'][i]:
            ax4.plot(co_history['env_fitness'][i], color=colors[i], 
                    linewidth=1.5, alpha=0.7, label=f'Env {i} (d={envs[i].difficulty:.2f})')
    ax4.set_title('Per-Environment Max Fitness\n(Co-evolution)', fontsize=11, fontweight='bold')
    ax4.set_xlabel('Generation')
    ax4.set_ylabel('Max Fitness')
    ax4.legend(fontsize=6, loc='lower right', ncol=2)
    ax4.grid(True, alpha=0.3)
    
    # 2B: 环境难度增长
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.plot(co_history['env_difficulty'], 'purple', linewidth=2, marker='.', 
             markersize=3, alpha=0.8)
    ax5.set_title('Environmental Difficulty Growth\n(POET-style)', fontsize=11, fontweight='bold')
    ax5.set_xlabel('Generation')
    ax5.set_ylabel('Mean Difficulty')
    ax5.grid(True, alpha=0.3)
    
    # 2C: 复杂天花板示意图
    ax6 = fig.add_subplot(gs[1, 2])
    t = np.linspace(0, 200, 200)
    # 不同参数的S曲线代表不同"复杂度"的进化轨迹
    for i, (scale, label) in enumerate(zip([0.5, 1.0, 2.0], ['Simple', 'Moderate', 'Complex'])):
        ceiling = 1 - np.exp(-scale * 0.03)
        sigmoid = ceiling / (1 + np.exp(-0.05 * (t - 80 / scale)))
        ax6.plot(t, sigmoid, linewidth=2, label=f'{label} (ceiling={ceiling:.2f})')
        ax6.axhline(y=ceiling, color='gray', linestyle=':', alpha=0.4)
    
    ax6.set_title('Complexity Ceiling Effect', fontsize=11, fontweight='bold')
    ax6.set_xlabel('Generations')
    ax6.set_ylabel('Achieved Complexity')
    ax6.legend(fontsize=8)
    ax6.grid(True, alpha=0.3)
    
    # ═══ 实验3: 新颖度搜索 vs 适应度搜索 ═══
    x_n, landscape_n = generate_rugged_landscape(size=300, n_peaks=25, noise=0.03)
    
    # 传统适应度搜索
    fit_h, div_h, best_h, _, _ = evolve_population(
        x_n, landscape_n, pop_size=30, generations=120)
    
    # 新颖度搜索
    n_fit_h, n_nov_h, n_cov_h, archive = novelty_search(
        landscape_n, pop_size=30, generations=120)
    
    # 3A: 适应度对比
    ax7 = fig.add_subplot(gs[2, 0])
    ax7.plot(fit_h, 'b-', linewidth=1.5, label='Fitness Search', alpha=0.8)
    ax7.plot(n_fit_h, 'r-', linewidth=1.5, label='Novelty Search', alpha=0.8)
    ax7.fill_between(range(len(fit_h)), 
                      np.minimum(fit_h, n_fit_h), 
                      np.maximum(fit_h, n_fit_h), 
                      color='gray', alpha=0.1)
    ax7.set_title('Mean Fitness: Fitness vs\nNovelty Search', fontsize=11, fontweight='bold')
    ax7.set_xlabel('Generation')
    ax7.set_ylabel('Mean Fitness')
    ax7.legend(fontsize=8)
    ax7.grid(True, alpha=0.3)
    
    # 3B: 新颖度 + 覆盖度
    ax8 = fig.add_subplot(gs[2, 1])
    ax8.plot(n_nov_h, 'orange', linewidth=1.5, label='Novelty Score', alpha=0.8)
    ax8_twin = ax8.twinx()
    ax8_twin.plot(n_cov_h, 'green', linewidth=1.5, label='Coverage', alpha=0.8)
    ax8.set_title('Novelty Search Metrics', fontsize=11, fontweight='bold')
    ax8.set_xlabel('Generation')
    ax8.set_ylabel('Mean Novelty Score', color='orange')
    ax8_twin.set_ylabel('Visited States', color='green')
    lines1, labels1 = ax8.get_legend_handles_labels()
    lines2, labels2 = ax8_twin.get_legend_handles_labels()
    ax8.legend(lines1 + lines2, labels1 + labels2, fontsize=7)
    ax8.grid(True, alpha=0.3)
    
    # 3C: 方法与概念总结
    ax9 = fig.add_subplot(gs[2, 2])
    ax9.axis('off')
    
    summary_text = (
        "DIGITAL EVOLUTION — KEY INSIGHTS\n"
        "═══════════════════════════════════\n\n"
        "1. Complexity Ceiling: Every static\n"
        "   environment imposes an upper bound.\n"
        "   Progress stops when ceiling hit.\n\n"
        "2. POET Solution: Environments & agents\n"
        "   co-evolve → rising ceiling → open-\n"
        "   ended complexity.\n\n"
        "3. Novelty > Fitness: Searching for new\n"
        "   behaviors finds stepping stones that\n"
        "   pure fitness optimization misses.\n\n"
        "4. Quality-Diversity: Maintain archive of\n"
        "   diverse high-fitness solutions, not\n"
        "   just the single best.\n\n"
        "Related: #003 Edge of Chaos,\n"
        "  #020 ALife, #022 Open-Endedness"
    )
    ax9.text(0.02, 0.98, summary_text, transform=ax9.transAxes,
             fontsize=9.5, verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    fig.suptitle('#021 Digital Evolution — Complexity Ceilings, Co-evolution & Novelty Search',
                 fontsize=14, fontweight='bold', y=0.98)
    
    plt.savefig('experiments/digital_evolution.png', dpi=150, bbox_inches='tight',
                facecolor='white')
    plt.close()
    
    # ─── 输出分析 ───────────────────────────────────────────────
    print("=" * 60)
    print("#021 Digital Evolution — Results")
    print("=" * 60)
    
    print("\n[Experiment 1] Fitness Landscape Evolution")
    print(f"  Initial fitness: {fit_hist[0]:.4f}")
    print(f"  Final fitness:   {fit_hist[-1]:.4f}")
    print(f"  Final best:      {best_hist[-1]:.4f}")
    print(f"  Final diversity: {div_hist[-1]} unique positions")
    print(f"  Fitness gain:    {(fit_hist[-1] - fit_hist[0]) / fit_hist[0] * 100:.1f}%")
    
    # Check for plateau
    late_fit = fit_hist[-30:]
    change_ratio = (late_fit[-1] - late_fit[0]) / (late_fit.max() - late_fit.min() + 1e-10)
    ceiling_hit = abs(change_ratio) < 0.1
    print(f"  Ceiling hit:     {'YES ⚠️' if ceiling_hit else 'NO (still improving)'}")
    
    print("\n[Experiment 2] Co-evolution")
    print(f"  Starting environments: 8")
    print(f"  Final environments:    {len(envs)}")
    print(f"  Final mean difficulty: {co_history['env_difficulty'][-1]:.3f}")
    print(f"  Migration events:      {len([e for e in co_history['migration_events'] if e[0] != 'new_env'])}")
    print(f"  New env births:        {len([e for e in co_history['migration_events'] if e[0] == 'new_env'])}")
    
    # Average fitness across environments
    final_fits = [co_history['env_fitness'][i][-1] for i in range(len(envs)) 
                  if co_history['env_fitness'][i]]
    print(f"  Final fitness range:   {min(final_fits):.3f} - {max(final_fits):.3f}")
    
    print("\n[Experiment 3] Novelty vs Fitness Search")
    print(f"  Fitness search - final mean fitness: {fit_h[-1]:.4f}")
    print(f"  Novelty search - final mean fitness: {n_fit_h[-1]:.4f}")
    print(f"  Fitness search - final coverage:     {div_h[-1]} states")
    print(f"  Novelty search - final coverage:     {n_cov_h[-1]} states")
    print(f"  Coverage advantage: {(n_cov_h[-1] / max(div_h[-1], 1) - 1) * 100:.1f}%")
    
    # Which search found better fitness?
    if fit_h[-1] > n_fit_h[-1]:
        print(f"  Winner: Fitness search (by {(fit_h[-1] - n_fit_h[-1]) / n_fit_h[-1] * 100:.1f}%)")
    else:
        print(f"  Winner: Novelty search (by {(n_fit_h[-1] - fit_h[-1]) / fit_h[-1] * 100:.1f}%)")
    
    print(f"\nOutput: experiments/digital_evolution.png")
    print("=" * 60)

if __name__ == '__main__':
    main()
