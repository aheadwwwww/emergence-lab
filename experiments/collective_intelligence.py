"""
Collective Intelligence - 集体智能

群体比个体更聪明
例：维基百科、预测市场、众包

本实验模拟"群体智慧"估计
"""

import numpy as np
from PIL import Image, ImageDraw
import random

def wisdom_of_crowds(n_people=100, true_value=100, individual_error=30):
    """群体智慧：多人估计的平均比单个人更准"""
    estimates = [true_value + random.gauss(0, individual_error) for _ in range(n_people)]
    
    mean_estimate = np.mean(estimates)
    individual_errors = [abs(e - true_value) for e in estimates]
    avg_individual_error = np.mean(individual_errors)
    collective_error = abs(mean_estimate - true_value)
    
    return {
        'estimates': estimates,
        'mean': mean_estimate,
        'individual_errors': individual_errors,
        'avg_individual_error': avg_individual_error,
        'collective_error': collective_error,
        'improvement': avg_individual_error / collective_error if collective_error > 0 else 0
    }

def diversity_prediction_theorem(n_simulations=1000):
    """多样性预测定理：群体误差 = 平均个体误差 - 群体多样性"""
    results = []
    
    for _ in range(n_simulations):
        true_value = random.uniform(50, 150)
        n = random.randint(10, 200)
        error = random.uniform(10, 50)
        
        result = wisdom_of_crowds(n, true_value, error)
        results.append(result)
    
    return results

def visualize_wisdom_of_crowds(output_path):
    """可视化群体智慧"""
    SIZE = 800
    MARGIN = 80
    
    img = Image.new('RGB', (SIZE, SIZE), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    # 模拟不同群体大小的误差
    true_value = 100
    group_sizes = [1, 5, 10, 20, 50, 100, 200]
    
    individual_errors = []
    collective_errors = []
    
    for n in group_sizes:
        errors = []
        for _ in range(100):  # 多次模拟
            result = wisdom_of_crowds(n, true_value, 30)
            errors.append(result['collective_error'])
        collective_errors.append(np.mean(errors))
        individual_errors.append(30)  # 个体误差恒定
    
    # 绘制
    WIDTH = SIZE - 2 * MARGIN
    HEIGHT = SIZE - 2 * MARGIN
    max_error = max(individual_errors)
    
    # 个体误差（红线）
    for i in range(len(group_sizes) - 1):
        x1 = MARGIN + i / (len(group_sizes) - 1) * WIDTH
        y1 = SIZE - MARGIN - individual_errors[i] / max_error * HEIGHT
        x2 = MARGIN + (i + 1) / (len(group_sizes) - 1) * WIDTH
        y2 = SIZE - MARGIN - individual_errors[i+1] / max_error * HEIGHT
        draw.line([x1, y1, x2, y2], fill=(255, 100, 100), width=3)
    
    # 集体误差（绿线）
    for i in range(len(group_sizes) - 1):
        x1 = MARGIN + i / (len(group_sizes) - 1) * WIDTH
        y1 = SIZE - MARGIN - collective_errors[i] / max_error * HEIGHT
        x2 = MARGIN + (i + 1) / (len(group_sizes) - 1) * WIDTH
        y2 = SIZE - MARGIN - collective_errors[i+1] / max_error * HEIGHT
        draw.line([x1, y1, x2, y2], fill=(100, 255, 150), width=3)
    
    # 标签
    draw.text((MARGIN + 10, MARGIN + 20), "Individual Error", fill=(255, 100, 100))
    draw.text((MARGIN + 10, MARGIN + 40), "Collective Error", fill=(100, 255, 150))
    draw.text((SIZE // 2 - 40, 20), "Wisdom of Crowds", fill=(255, 255, 255))
    draw.text((SIZE // 2 - 30, SIZE - 40), "Group Size", fill=(200, 200, 200))
    
    img.save(output_path)
    print(f'Saved: {output_path}')

if __name__ == '__main__':
    output_dir = r'C:\Users\许耀仁\.openclaw\workspace\experiments'
    
    print('=== Collective Intelligence ===')
    
    # 演示群体智慧
    result = wisdom_of_crowds(100, 100, 30)
    print(f'Average individual error: {result["avg_individual_error"]:.2f}')
    print(f'Collective error: {result["collective_error"]:.2f}')
    print(f'Improvement factor: {result["improvement"]:.2f}x')
    
    visualize_wisdom_of_crowds(f'{output_dir}/collective_intelligence.png')
    
    print('Done')