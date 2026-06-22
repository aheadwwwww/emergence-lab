"""
Grokking - 机器学习中的"顿悟"现象

OpenAI 2022 年发现：模型在长时间过拟合后，突然泛化。
训练损失先下降到零（记忆），然后泛化损失突然下降（理解）。

本实验用简单的算法任务演示 Grokking：
- 模块算术：a + b mod p
- 观察：从记忆到泛化的突然切换
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import json

def generate_mod_arithmetic_data(p=97, train_fraction=0.5):
    """生成模块算术数据集"""
    data = []
    for a in range(p):
        for b in range(p):
            result = (a + b) % p
            data.append((a, b, result))
    
    np.random.shuffle(data)
    split = int(len(data) * train_fraction)
    train = data[:split]
    test = data[split:]
    
    return train, test

def simple_nn_forward(x, W1, W2, p):
    """简单的前向传播（用于可视化）"""
    h = np.maximum(0, x @ W1)  # ReLU
    out = h @ W2
    return out

def visualize_grokking_curve(train_acc, test_acc, output_path):
    """可视化 Grokking 曲线"""
    SIZE = 800
    MARGIN = 80
    WIDTH = SIZE - 2 * MARGIN
    HEIGHT = SIZE - 2 * MARGIN
    
    img = Image.new('RGB', (SIZE, SIZE), (20, 20, 30))
    draw = ImageDraw.Draw(img)
    
    # 绘制坐标轴
    draw.line([MARGIN, MARGIN, MARGIN, SIZE - MARGIN], fill=(100, 100, 100), width=2)
    draw.line([MARGIN, SIZE - MARGIN, SIZE - MARGIN, SIZE - MARGIN], fill=(100, 100, 100), width=2)
    
    # Y 轴标签
    draw.text((20, MARGIN), "100%", fill=(200, 200, 200))
    draw.text((20, SIZE - MARGIN), "0%", fill=(200, 200, 200))
    
    # X 轴标签
    draw.text((MARGIN, SIZE - 40), "0", fill=(200, 200, 200))
    draw.text((SIZE - MARGIN - 20, SIZE - 40), "Steps", fill=(200, 200, 200))
    
    # 绘制训练准确率（蓝色）
    steps = len(train_acc)
    for i in range(1, steps):
        x1 = MARGIN + (i - 1) / steps * WIDTH
        y1 = SIZE - MARGIN - train_acc[i - 1] * HEIGHT
        x2 = MARGIN + i / steps * WIDTH
        y2 = SIZE - MARGIN - train_acc[i] * HEIGHT
        draw.line([x1, y1, x2, y2], fill=(50, 150, 255), width=2)
    
    # 绘制测试准确率（橙色）
    for i in range(1, len(test_acc)):
        x1 = MARGIN + (i - 1) / steps * WIDTH
        y1 = SIZE - MARGIN - test_acc[i - 1] * HEIGHT
        x2 = MARGIN + i / steps * WIDTH
        y2 = SIZE - MARGIN - test_acc[i] * HEIGHT
        draw.line([x1, y1, x2, y2], fill=(255, 150, 50), width=2)
    
    # 标注
    draw.text((SIZE - 150, MARGIN + 20), "Training", fill=(50, 150, 255))
    draw.text((SIZE - 150, MARGIN + 40), "Test", fill=(255, 150, 50))
    
    # 标题
    draw.text((SIZE // 2 - 50, 20), "Grokking Curve", fill=(255, 255, 255))
    
    img.save(output_path)
    print(f'Saved: {output_path}')

def simulate_grokking():
    """模拟 Grokking 现象（简化的可视化）"""
    # 生成模拟数据：训练准确率快速上升到 100%，测试准确率滞后
    steps = 200
    
    # Grokking 模式：先记忆，后泛化
    train_acc = []
    test_acc = []
    
    for i in range(steps):
        t = i / steps
        
        # 训练准确率：快速上升
        train = 1 - np.exp(-10 * t)
        
        # 测试准确率：先慢（记忆），然后突然上升（grokking）
        if t < 0.3:
            test = 0.1 + 0.1 * t
        elif t < 0.7:
            # Grokking 阶段
            test = 0.1 + 0.1 * 0.3 + (t - 0.3) / 0.4 * 0.85
        else:
            test = 0.95 + 0.05 * (t - 0.7) / 0.3
        
        train_acc.append(min(train, 1.0))
        test_acc.append(min(test, 1.0))
    
    return train_acc, test_acc

if __name__ == '__main__':
    output_dir = r'C:\Users\许耀仁\.openclaw\workspace\experiments'
    
    print('=== Simulating Grokking ===')
    train_acc, test_acc = simulate_grokking()
    visualize_grokking_curve(train_acc, test_acc, f'{output_dir}/grokking_curve.png')
    
    print('Done')