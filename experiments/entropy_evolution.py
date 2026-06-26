"""
熵演化实验：测量涌现系统的熵随时间变化

目标：
1. 验证热力学第二定律在涌现系统中的适用性
2. 找到"负熵流"的条件（开放 vs 封闭）
3. 测量涌现结构的生命周期
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import convolve
import os

def lenia_step(grid, kernel, params):
    """单步 Lenia 更新"""
    R, mu, sigma = params
    conv = convolve(grid, kernel, mode='wrap')
    
    # Growth function
    growth = 2 * np.exp(-(conv - mu)**2 / (2 * sigma**2)) - 1
    
    # Update
    new_grid = np.clip(grid + 0.1 * growth, 0, 1)
    return new_grid

def create_kernel(R, smooth=True):
    """创建 Lenia 内核"""
    size = 2 * R + 1
    kernel = np.zeros((size, size))
    
    for i in range(size):
        for j in range(size):
            dist = np.sqrt((i - R)**2 + (j - R)**2)
            if dist <= R:
                kernel[i, j] = 1
    
    if smooth:
        # Gaussian smoothing
        from scipy.ndimage import gaussian_filter
        kernel = gaussian_filter(kernel, sigma=R/3)
    
    # Normalize
    kernel = kernel / kernel.sum()
    return kernel

def calculate_entropy(grid, bins=50):
    """计算网格的熵（信息熵）"""
    # 将网格值离散化为 bins
    hist, _ = np.histogram(grid.flatten(), bins=bins, range=(0, 1))
    hist = hist / hist.sum()  # 归一化
    
    # 移除零值避免 log(0)
    hist = hist[hist > 0]
    
    # 计算信息熵
    entropy = -np.sum(hist * np.log2(hist))
    return entropy

def calculate_spatial_entropy(grid, block_size=10):
    """计算空间熵（局部模式的多样性）"""
    h, w = grid.shape
    n_blocks_h = h // block_size
    n_blocks_w = w // block_size
    
    patterns = []
    for i in range(n_blocks_h):
        for j in range(n_blocks_w):
            block = grid[i*block_size:(i+1)*block_size, 
                        j*block_size:(j+1)*block_size]
            # 将块量化为特征向量
            pattern = (block.mean(), block.std(), block.max(), block.min())
            patterns.append(pattern)
    
    # 计算模式的熵
    patterns = np.array(patterns)
    entropies = []
    for col in range(patterns.shape[1]):
        hist, _ = np.histogram(patterns[:, col], bins=20)
        hist = hist / hist.sum()
        hist = hist[hist > 0]
        entropies.append(-np.sum(hist * np.log2(hist)))
    
    return np.mean(entropies)

def calculate_alive_cells(grid, threshold=0.1):
    """计算活跃细胞数量"""
    return np.sum(grid > threshold)

def run_entropy_evolution(R=13, mu=0.15, sigma=0.015, 
                          grid_size=100, steps=500,
                          initial_type='random'):
    """运行熵演化实验"""
    
    # 初始化
    if initial_type == 'random':
        grid = np.random.rand(grid_size, grid_size) * 0.1
    elif initial_type == 'spot':
        grid = np.zeros((grid_size, grid_size))
        cx, cy = grid_size // 2, grid_size // 2
        r = 10
        for i in range(grid_size):
            for j in range(grid_size):
                if (i - cx)**2 + (j - cy)**2 < r**2:
                    grid[i, j] = np.random.rand()
    elif initial_type == 'orbium':
        # Orbium 参数
        grid = np.zeros((grid_size, grid_size))
        cx, cy = grid_size // 2, grid_size // 2
        # 创建 Orbium 形状
        for i in range(grid_size):
            for j in range(grid_size):
                dist = np.sqrt((i - cx)**2 + (j - cy)**2)
                if dist < 10:
                    grid[i, j] = 0.5 + 0.3 * np.cos(dist / 2)
    
    kernel = create_kernel(R)
    params = (R, mu, sigma)
    
    # 记录数据
    entropies = []
    spatial_entropies = []
    alive_cells = []
    
    # 运行
    for step in range(steps):
        grid = lenia_step(grid, kernel, params)
        
        if step % 10 == 0:
            ent = calculate_entropy(grid)
            spat_ent = calculate_spatial_entropy(grid)
            alive = calculate_alive_cells(grid)
            
            entropies.append(ent)
            spatial_entropies.append(spat_ent)
            alive_cells.append(alive)
    
    return {
        'entropy': entropies,
        'spatial_entropy': spatial_entropies,
        'alive_cells': alive_cells,
        'final_grid': grid
    }

def compare_open_vs_closed(R=13, mu=0.15, sigma=0.015, 
                           grid_size=100, steps=500):
    """对比开放系统 vs 封闭系统"""
    
    # 开放系统：有外部能量输入（随机扰动）
    # 封闭系统：完全自主演化
    
    kernel = create_kernel(R)
    params = (R, mu, sigma)
    
    grid_open = np.random.rand(grid_size, grid_size) * 0.1
    grid_closed = grid_open.copy()
    
    entropies_open = []
    entropies_closed = []
    alive_open = []
    alive_closed = []
    
    for step in range(steps):
        # 开放系统：每 50 步注入一点能量
        grid_open = lenia_step(grid_open, kernel, params)
        if step % 50 == 0:
            grid_open += np.random.rand(grid_size, grid_size) * 0.02
            grid_open = np.clip(grid_open, 0, 1)
        
        # 封闭系统：完全自主
        grid_closed = lenia_step(grid_closed, kernel, params)
        
        if step % 10 == 0:
            entropies_open.append(calculate_entropy(grid_open))
            entropies_closed.append(calculate_entropy(grid_closed))
            alive_open.append(calculate_alive_cells(grid_open))
            alive_closed.append(calculate_alive_cells(grid_closed))
    
    return {
        'entropy_open': entropies_open,
        'entropy_closed': entropies_closed,
        'alive_open': alive_open,
        'alive_closed': alive_closed,
        'final_open': grid_open,
        'final_closed': grid_closed
    }

def plot_results(results, title, save_path):
    """绘制结果"""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # 熵演化
    axes[0, 0].plot(results['entropy'], label='Value Entropy', linewidth=2)
    axes[0, 0].plot(results['spatial_entropy'], label='Spatial Entropy', linewidth=2)
    axes[0, 0].set_xlabel('Time (×10 steps)')
    axes[0, 0].set_ylabel('Entropy (bits)')
    axes[0, 0].set_title('Entropy Evolution')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 活跃细胞
    axes[0, 1].plot(results['alive_cells'], color='green', linewidth=2)
    axes[0, 1].set_xlabel('Time (×10 steps)')
    axes[0, 1].set_ylabel('Alive Cells')
    axes[0, 1].set_title('Alive Cells Over Time')
    axes[0, 1].grid(True, alpha=0.3)
    
    # 最终状态
    axes[1, 0].imshow(results['final_grid'], cmap='viridis')
    axes[1, 0].set_title('Final State')
    axes[1, 0].axis('off')
    
    # 熵 vs 活跃度散点图
    min_len = min(len(results['entropy']), len(results['alive_cells']))
    axes[1, 1].scatter(results['entropy'][:min_len], 
                       results['alive_cells'][:min_len], 
                       alpha=0.5, c=range(min_len), cmap='viridis')
    axes[1, 1].set_xlabel('Entropy')
    axes[1, 1].set_ylabel('Alive Cells')
    axes[1, 1].set_title('Entropy vs Alive Cells (color = time)')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")

def plot_open_vs_closed(results, save_path):
    """绘制开放 vs 封闭对比"""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # 熵对比
    axes[0, 0].plot(results['entropy_open'], label='Open System', linewidth=2)
    axes[0, 0].plot(results['entropy_closed'], label='Closed System', linewidth=2)
    axes[0, 0].set_xlabel('Time (×10 steps)')
    axes[0, 0].set_ylabel('Entropy (bits)')
    axes[0, 0].set_title('Entropy: Open vs Closed System')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 活跃度对比
    axes[0, 1].plot(results['alive_open'], label='Open System', linewidth=2)
    axes[0, 1].plot(results['alive_closed'], label='Closed System', linewidth=2)
    axes[0, 1].set_xlabel('Time (×10 steps)')
    axes[0, 1].set_ylabel('Alive Cells')
    axes[0, 1].set_title('Alive Cells: Open vs Closed System')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # 最终状态 - 开放
    axes[1, 0].imshow(results['final_open'], cmap='viridis')
    axes[1, 0].set_title('Open System (with energy input)')
    axes[1, 0].axis('off')
    
    # 最终状态 - 封闭
    axes[1, 1].imshow(results['final_closed'], cmap='viridis')
    axes[1, 1].set_title('Closed System (autonomous)')
    axes[1, 1].axis('off')
    
    plt.suptitle('Thermodynamics in Emergent Systems\n(Entropy Evolution in Lenia)', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")

if __name__ == "__main__":
    output_dir = "D:/emergence_experiments"
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("熵演化实验：涌现系统的热力学")
    print("=" * 60)
    
    # 实验 1：基本熵演化
    print("\n[1/3] 运行基本熵演化实验...")
    results1 = run_entropy_evolution(R=13, mu=0.15, sigma=0.015, steps=500)
    plot_results(results1, "Entropy Evolution in Lenia (R=13, μ=0.15, σ=0.015)",
                 os.path.join(output_dir, "entropy_evolution_basic.png"))
    
    # 实验 2：不同参数对比
    print("\n[2/3] 运行参数对比实验...")
    results2 = run_entropy_evolution(R=20, mu=0.22, sigma=0.04, steps=500)
    plot_results(results2, "Entropy Evolution in Lenia (R=20, μ=0.22, σ=0.04)",
                 os.path.join(output_dir, "entropy_evolution_orbium.png"))
    
    # 实验 3：开放 vs 封闭
    print("\n[3/3] 运行开放 vs 封闭对比实验...")
    results3 = compare_open_vs_closed(R=13, mu=0.15, sigma=0.015, steps=500)
    plot_open_vs_closed(results3, 
                        os.path.join(output_dir, "entropy_open_vs_closed.png"))
    
    print("\n" + "=" * 60)
    print("实验完成！")
    print(f"输出目录: {output_dir}")
    print("=" * 60)