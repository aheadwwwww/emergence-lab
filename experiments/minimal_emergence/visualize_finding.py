"""
可视化最小涌现宇宙的发现
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

OUTPUT_DIR = Path('D:/emergence_experiments')


def draw_finding():
    """绘制发现总结图"""
    img = Image.new('RGB', (800, 600), (20, 20, 30))
    draw = ImageDraw.Draw(img)
    
    # 标题
    draw.text((400, 30), "最小涌现宇宙实验", fill=(255, 255, 255), anchor='mt')
    draw.text((400, 60), "Emergence Requires Self-Expansion", fill=(200, 200, 200), anchor='mt')
    
    # 表格数据
    systems = [
        ("基础", "6", "6", "否"),
        ("+记忆(4bit)", "48", "19", "否"),
        ("+状态(8)", "16", "12", "否"),
        ("+反馈", "48", "18", "否"),
        ("+进化", "动态", "-", "否"),
        ("+自扩展", "1→21", "∞", "是"),
    ]
    
    # 表头
    y = 100
    draw.text((100, y), "系统", fill=(150, 200, 255))
    draw.text((250, y), "状态空间", fill=(150, 200, 255))
    draw.text((400, y), "最大周期", fill=(150, 200, 255))
    draw.text((550, y), "开放式", fill=(150, 200, 255))
    
    y += 30
    draw.line([(80, y), (700, y)], fill=(80, 80, 100), width=1)
    
    # 数据行
    for i, (name, space, cycle, open_flag) in enumerate(systems):
        y += 35
        color = (100, 255, 100) if open_flag == "是" else (200, 200, 200)
        draw.text((100, y), name, fill=color)
        draw.text((250, y), space, fill=color)
        draw.text((400, y), cycle, fill=color)
        draw.text((550, y), open_flag, fill=color)
    
    # 结论框
    y += 60
    draw.rectangle([(80, y), (720, y + 120)], outline=(100, 150, 200), width=2)
    
    draw.text((400, y + 20), "涌现五元素", fill=(255, 200, 100), anchor='mt')
    
    elements = "状态 + 规则 + 反馈 + 记忆 + 自扩展"
    draw.text((400, y + 50), elements, fill=(255, 255, 255), anchor='mt')
    
    insight = "有限状态空间 → 有限周期 → 无开放式涌现"
    draw.text((400, y + 80), insight, fill=(200, 200, 200), anchor='mt')
    
    insight2 = "自扩展状态空间 → 无限状态 → 开放式涌现"
    draw.text((400, y + 105), insight2, fill=(100, 255, 100), anchor='mt')
    
    # 保存
    path = OUTPUT_DIR / 'minimal_emergence_finding.png'
    img.save(path)
    return str(path)


if __name__ == '__main__':
    path = draw_finding()
    print(f"可视化保存到: {path}")