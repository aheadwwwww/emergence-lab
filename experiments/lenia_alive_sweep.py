"""
Lenia Alive Mask Parameter Sweep
扫描 alive_threshold 参数对存活率的影响
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import convolve

def lenia_kernel(R=13, params=None):
    """生成 Lenia 卷积核"""
    if params is None:
        params = {'mu': 0.5, 'sigma': 0.15}
    
    size = 2 * R + 1
    y, x = np.ogrid[-R:R+1, -R:R+1]
    dist = np.sqrt(x**2 + y**2) / R
    
    # 环形核
    kernel = np.exp(-((dist - params['mu'])**2) / (2 * params['sigma']**2))
    kernel[dist > 1] = 0
    kernel = kernel / kernel.sum()
    
    return kernel

def lenia_growth(U, mu=0.5, sigma=0.15):
    """Lenia 增长函数"""
    return np.exp(-((U - mu)**2) / (2 * sigma**2))

def get_alive_mask(grid, threshold=0.1, nhood_radius=3):
    """检测存活细胞邻域"""
    # 成熟细胞：alpha channel > threshold
    mature = (grid > threshold).astype(np.float32)
    
    # 邻域卷积
    nhood_size = 2 * nhood_radius + 1
    nhood_kernel = np.ones((nhood_size, nhood_size)) / (nhood_size ** 2)
    alive_neighbors = convolve(mature, nhood_kernel, mode='wrap')
    
    # 存活条件：邻域存活率 > 0.5
    return alive_neighbors > 0.5

def lenia_step_stochastic_alive(grid, kernel, params, update_rate=0.5, alive_threshold=0.1):
    """Stochastic + Alive Mask 更新"""
    # 卷积
    U = convolve(grid, kernel, mode='wrap')
    
    # 增长
    G = lenia_growth(U, params['mu'], params['sigma'])
    
    # Alive mask
    alive = get_alive_mask(grid, threshold=alive_threshold)
    
    # 随机更新
    update_mask = np.random.random(grid.shape) < update_rate
    
    # 组合更新
    new_grid = np.where(update_mask & alive, G, grid)
    new_grid = np.clip(new_grid, 0, 1)
    
    return new_grid

def run_experiment(alive_threshold, steps=200, R=13):
    """运行单次实验"""
    kernel = lenia_kernel(R=R)
    params = {'mu': 0.5, 'sigma': 0.15}
    
    # 初始化：随机种子
    grid = np.random.random((100, 100)) * 0.1
    center = 50
    grid[center-5:center+5, center-5:center+5] = np.random.random((10, 10))
    
    alive_ratios = []
    
    for _ in range(steps):
        grid = lenia_step_stochastic_alive(grid, kernel, params, 
                                           update_rate=0.5, 
                                           alive_threshold=alive_threshold)
        alive_ratios.append((grid > 0.1).mean())
    
    return alive_ratios

def main():
    """主函数：参数扫描"""
    print("=" * 60)
    print("Lenia Alive Mask Parameter Sweep")
    print("=" * 60)
    
    # 扫描参数
    thresholds = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
    
    results = {}
    
    for thresh in thresholds:
        print(f"\nTesting alive_threshold = {thresh}...")
        alive_ratios = run_experiment(thresh)
        
        final_ratio = alive_ratios[-1]
        max_ratio = max(alive_ratios)
        
        results[thresh] = {
            'final': final_ratio,
            'max': max_ratio,
            'history': alive_ratios
        }
        
        status = "OK" if final_ratio > 0.1 else "FAIL"
        print(f"  Final: {final_ratio:.1%}, Max: {max_ratio:.1%} {status}")
    
    # 可视化
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 演化曲线
    ax1 = axes[0]
    for thresh, data in results.items():
        ax1.plot(data['history'], label=f'thresh={thresh}')
    ax1.set_xlabel('Step')
    ax1.set_ylabel('Alive Ratio')
    ax1.set_title('Alive Ratio Evolution')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 最终存活率
    ax2 = axes[1]
    final_ratios = [results[t]['final'] for t in thresholds]
    colors = ['green' if r > 0.1 else 'red' for r in final_ratios]
    ax2.bar([str(t) for t in thresholds], final_ratios, color=colors, alpha=0.7)
    ax2.axhline(y=0.1, color='orange', linestyle='--', label='Survival threshold')
    ax2.set_xlabel('Alive Threshold')
    ax2.set_ylabel('Final Alive Ratio')
    ax2.set_title('Final Alive Ratio by Threshold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('output/lenia_alive_sweep.png', dpi=150)
    print(f"\n[OK] Saved: output/lenia_alive_sweep.png")
    
    # 找最优
    best_thresh = max(results.keys(), key=lambda t: results[t]['final'])
    print(f"\n最佳 alive_threshold = {best_thresh}")
    print(f"  最终存活率: {results[best_thresh]['final']:.1%}")

if __name__ == '__main__':
    main()
