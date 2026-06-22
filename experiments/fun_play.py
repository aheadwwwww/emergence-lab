"""
#026 Fun & Play - 玩乐与探索

没有外部奖励，系统自发探索
例：儿童游戏、好奇心驱动学习

本实验生成有趣的视觉图案
"""

import numpy as np
from PIL import Image, ImageDraw
import math
import random

def playful_pattern(size=800):
    """生成一个有趣的图案"""
    img = Image.new('RGB', (size, size), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    center = size // 2
    
    # 随机选择一种图案类型
    pattern_type = random.choice(['spiral', 'flower', 'fractal', 'waves'])
    
    if pattern_type == 'spiral':
        # 螺旋
        for i in range(5000):
            angle = i * 0.1
            r = i * 0.05
            x = center + r * math.cos(angle)
            y = center + r * math.sin(angle)
            hue = (i * 2) % 360
            color = (
                int(128 + 127 * math.sin(math.radians(hue))),
                int(128 + 127 * math.sin(math.radians(hue + 120))),
                int(128 + 127 * math.sin(math.radians(hue + 240)))
            )
            draw.ellipse([x-2, y-2, x+2, y+2], fill=color)
    
    elif pattern_type == 'flower':
        # 花朵
        for i in range(360):
            for j in range(50):
                angle = math.radians(i)
                r = 100 + 150 * math.sin(5 * angle) + j * 3
                x = center + r * math.cos(angle)
                y = center + r * math.sin(angle)
                color = (
                    200 + int(55 * math.sin(j * 0.1)),
                    100 + int(100 * math.cos(i * 0.05)),
                    150
                )
                draw.point((x, y), fill=color)
    
    elif pattern_type == 'fractal':
        # 简单分形
        def draw_branch(x, y, length, angle, depth):
            if depth == 0 or length < 2:
                return
            
            x2 = x + length * math.cos(angle)
            y2 = y + length * math.sin(angle)
            
            color = (50 + depth * 20, 150, 200 - depth * 15)
            draw.line([x, y, x2, y2], fill=color, width=max(1, depth))
            
            draw_branch(x2, y2, length * 0.7, angle - 0.5, depth - 1)
            draw_branch(x2, y2, length * 0.7, angle + 0.5, depth - 1)
        
        draw_branch(center, size - 50, 120, -math.pi/2, 10)
    
    else:  # waves
        # 波纹
        for i in range(100):
            for j in range(100):
                x = i * 8
                y = j * 8
                dist = math.sqrt((x - center)**2 + (y - center)**2)
                wave = math.sin(dist * 0.05) * 50 + math.sin(i * 0.2) * 30
                color = (
                    int(100 + wave),
                    int(100 + math.cos(dist * 0.03) * 50),
                    int(150 + math.sin(i * 0.1 + j * 0.1) * 50)
                )
                draw.rectangle([x, y, x+6, y+6], fill=color)
    
    return img, pattern_type

if __name__ == '__main__':
    output_dir = r'C:\Users\许耀仁\.openclaw\workspace\experiments'
    
    print('=== Fun & Play ===')
    
    img, pattern_type = playful_pattern(800)
    output_path = f'{output_dir}/fun_play.png'
    img.save(output_path)
    print(f'Saved: {output_path}')
    print(f'Pattern type: {pattern_type}')
    
    print('Done')