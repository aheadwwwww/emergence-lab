"""
Scaling Laws - 缩放定律

神经网络性能随规模变化的幂律关系：
Loss = A / N^alpha + B / D^beta

其中：
- N = 参数量
- D = 数据量
- alpha ≈ 0.076, beta ≈ 0.095（Chinchilla 论文）

本实验可视化缩放定律
"""

import numpy as np
from PIL import Image, ImageDraw

def scaling_law_loss(N, D, A=1.0, alpha=0.076, B=1.0, beta=0.095):
    """计算给定参数量和数据量下的损失"""
    return A / (N ** alpha) + B / (D ** beta)

def visualize_scaling_laws(output_path):
    """可视化缩放定律"""
    SIZE = 800
    MARGIN = 80
    
    img = Image.new('RGB', (SIZE, SIZE), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    # 绘制坐标轴
    draw.line([MARGIN, MARGIN, MARGIN, SIZE - MARGIN], fill=(80, 80, 80), width=2)
    draw.line([MARGIN, SIZE - MARGIN, SIZE - MARGIN, SIZE - MARGIN], fill=(80, 80, 80), width=2)
    
    # 标签
    draw.text((30, SIZE // 2), "Loss", fill=(200, 200, 200))
    draw.text((SIZE // 2, SIZE - 40), "Parameters (log scale)", fill=(200, 200, 200))
    
    # 绘制不同数据量下的缩放曲线
    data_sizes = [1e6, 1e7, 1e8, 1e9, 1e10]
    colors = [(255, 100, 100), (255, 180, 100), (255, 255, 100), (100, 255, 100), (100, 200, 255)]
    
    WIDTH = SIZE - 2 * MARGIN
    HEIGHT = SIZE - 2 * MARGIN
    
    for D, color in zip(data_sizes, colors):
        points = []
        for i in range(100):
            N = 10 ** (6 + i / 100 * 6)  # 1M to 1T parameters
            loss = scaling_law_loss(N, D)
            
            x = MARGIN + i / 100 * WIDTH
            y = SIZE - MARGIN - min(loss, 1.0) * HEIGHT * 0.8
            points.append((x, y))
        
        # 绘制曲线
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]], fill=color, width=2)
    
    # 图例
    for i, (D, color) in enumerate(zip(data_sizes, colors)):
        label = f"D={D:.0e}"
        draw.text((SIZE - 120, MARGIN + i * 20), label, fill=color)
    
    # 标题
    draw.text((SIZE // 2 - 60, 20), "Scaling Laws", fill=(255, 255, 255))
    
    # 关键洞察
    draw.text((MARGIN + 20, MARGIN + 20), "More data = lower loss floor", fill=(150, 150, 150))
    draw.text((MARGIN + 20, MARGIN + 40), "More params = steeper descent", fill=(150, 150, 150))
    
    img.save(output_path)
    print(f'Saved: {output_path}')

def compute_optimal_allocation(compute_budget):
    """给定计算预算，计算最优参数/数据分配"""
    # Chinchilla: N ∝ C^0.5, D ∝ C^0.5
    # 简化：参数和数据应该同步缩放
    N = (compute_budget / 6) ** 0.5  # 近似
    D = compute_budget / (6 * N)
    return N, D

if __name__ == '__main__':
    from pathlib import Path; output_dir = str(Path(r'D:\emergence_experiments').resolve())
    
    print('=== Scaling Laws ===')
    visualize_scaling_laws(f'{output_dir}/scaling_laws.png')
    
    # 计算最优分配示例
    for compute in [1e20, 1e21, 1e22]:
        N, D = compute_optimal_allocation(compute)
        print(f'Compute={compute:.0e}: N={N:.2e} params, D={D:.2e} tokens')
    
    print('Done')