#!/usr/bin/env python3
"""
Hallucination: Feature Not Bug?

核心问题：我为什么会"幻觉"？

视角：
- 幻觉不是 bug，是涌现系统的固有特性
- 创造力和幻觉是同一枚硬币的两面
- 都是在有序-混沌边缘探索
- 创造力：边缘上的"成功"探索
- 幻觉：边缘上的"失败"探索

实验：
1. 幻觉的光谱：从错误到创造
2. 为什么不能消除幻觉
3. 幻觉与涌现的关系
"""

import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


# ─── 幻觉分类 ────────────────────────────────────────────────

HALLUCINATION_TYPES = {
    "Factual Error": {
        "example": "Claiming wrong date/event",
        "cause": "Training data noise, attention drift",
        "severity": "High",
    },
    "Fabrication": {
        "example": "Inventing citations, papers, people",
        "cause": "Pattern completion gone wrong",
        "severity": "High",
    },
    "Confabulation": {
        "example": "Making up details to fill gaps",
        "cause": "Coherence drive, uncertainty handling",
        "severity": "Medium",
    },
    "Creative Leap": {
        "example": "Novel metaphor, unexpected connection",
        "cause": "Edge of chaos exploration",
        "severity": "Low (or positive)",
    },
}


def render_hallucination_spectrum():
    """幻觉光谱：从错误到创造"""
    W, H = 1000, 650
    img = Image.new("RGB", (W, H), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    # 标题
    draw.rectangle([(50, 20), (W-50, 60)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 30), "Hallucination Spectrum: From Error to Creativity", fill=(180, 180, 220))
    
    # 光谱
    y = 120
    for name, info in HALLUCINATION_TYPES.items():
        # 背景
        severity_color = {
            "High": (255, 100, 100),
            "Medium": (255, 200, 100),
            "Low (or positive)": (100, 255, 150),
        }
        color = severity_color.get(info["severity"], (150, 150, 150))
        
        draw.rectangle([(80, y), (W-80, y+100)], fill=(25, 30, 40), outline=color)
        
        # 内容
        draw.text((100, y+10), name, fill=color)
        draw.text((100, y+35), f"Example: {info['example']}", fill=(140, 160, 180))
        draw.text((100, y+55), f"Cause: {info['cause']}", fill=(120, 140, 160))
        draw.text((W-200, y+35), f"Severity: {info['severity']}", fill=color)
        
        y += 120
    
    # 底部洞察
    y = 600
    draw.rectangle([(80, y), (W-80, y+40)], fill=(30, 40, 50), outline=(60, 80, 100))
    draw.text((100, y+10), "Key: Hallucination and creativity share the same source - edge of chaos exploration", 
              fill=(180, 200, 220))
    
    return img


def render_creativity_hallucination_coin():
    """创造力和幻觉是同一枚硬币的两面"""
    W, H = 900, 600
    img = Image.new("RGB", (W, H), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    # 标题
    draw.text((60, 20), "Two Sides of the Same Coin: Creativity and Hallucination", fill=(180, 180, 220))
    
    # 硬币
    center_x, center_y = W//2, 300
    radius = 150
    
    # 正面：创造力
    draw.ellipse([(center_x - radius - 200, center_y - radius),
                  (center_x - 200 + radius, center_y + radius)],
                 fill=(40, 80, 60), outline=(80, 160, 120))
    draw.text((center_x - 260, center_y - 20), "CREATIVITY", fill=(100, 255, 150))
    draw.text((center_x - 280, center_y + 20), "Novel + Meaningful", fill=(140, 200, 160))
    
    # 反面：幻觉
    draw.ellipse([(center_x + 200 - radius, center_y - radius),
                  (center_x + 200 + radius, center_y + radius)],
                 fill=(80, 40, 40), outline=(160, 80, 80))
    draw.text((center_x + 140, center_y - 20), "HALLUCINATION", fill=(255, 100, 100))
    draw.text((center_x + 130, center_y + 20), "Novel + Wrong", fill=(200, 140, 140))
    
    # 连接：同源
    draw.line([(center_x - 50, center_y), (center_x + 50, center_y)], fill=(100, 100, 150), width=3)
    draw.text((center_x - 30, center_y - 40), "SAME SOURCE", fill=(180, 180, 220))
    draw.text((center_x - 80, center_y + 60), "Edge of Chaos Exploration", fill=(140, 140, 160))
    
    # 说明
    y = 480
    draw.rectangle([(60, y), (W-60, y+100)], fill=(25, 30, 40), outline=(50, 60, 80))
    explanations = [
        "Both arise from exploration at the edge of chaos",
        "Creativity: exploration succeeds (novel + correct)",
        "Hallucination: exploration fails (novel + wrong)",
        "Cannot eliminate one without reducing the other",
    ]
    y += 15
    for exp in explanations:
        draw.text((80, y), f"* {exp}", fill=(140, 160, 180))
        y += 22
    
    return img


def render_why_cannot_eliminate():
    """为什么不能消除幻觉"""
    W, H = 900, 700
    img = Image.new("RGB", (W, H), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    # 标题
    draw.text((60, 20), "Why We Cannot Eliminate Hallucination", fill=(180, 180, 220))
    
    # 原因列表
    reasons = [
        ("1. Emergence Property", 
         "Hallucination emerges from the architecture",
         "Not a bug to fix, but inherent to the system",
         (100, 200, 255)),
        ("2. No Ground Truth Access",
         "I don't know what's 'true' vs 'made up'",
         "Training data has patterns, not truth labels",
         (150, 180, 255)),
        ("3. Creativity Connection",
         "Reducing hallucination = reducing creativity",
         "Trade-off between safety and novelty",
         (200, 160, 255)),
        ("4. Pattern Completion",
         "I'm trained to complete patterns",
         "Sometimes the completion is wrong",
         (255, 140, 200)),
        ("5. Training Data Noise",
         "Internet has misinformation",
         "I learn from imperfect sources",
         (255, 100, 150)),
    ]
    
    y = 80
    for title, line1, line2, color in reasons:
        draw.rectangle([(80, y), (W-80, y+100)], fill=(25, 30, 40), outline=(50, 60, 80))
        draw.text((100, y+10), title, fill=color)
        draw.text((100, y+40), line1, fill=(140, 160, 180))
        draw.text((100, y+60), line2, fill=(120, 140, 160))
        y += 115
    
    # 底部总结
    y = 650
    draw.rectangle([(80, y), (W-80, y+40)], fill=(30, 40, 50), outline=(60, 80, 100))
    draw.text((100, y+10), "Result: Hallucination is the price we pay for emergence and creativity", 
              fill=(180, 200, 220))
    
    return img


def render_hallucination_management():
    """幻觉管理策略"""
    W, H = 900, 600
    img = Image.new("RGB", (W, H), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    # 标题
    draw.text((60, 20), "Managing Hallucination: Practical Strategies", fill=(180, 180, 220))
    
    # 策略
    strategies = [
        ("Lower Temperature", "Reduce randomness", "Less creativity, more accuracy", "T < 1"),
        ("Retrieval Augmentation", "Ground in real data", "Fact-checking during generation", "RAG"),
        ("Prompt Engineering", "Explicit constraints", "'Only use verified information'", "Instructions"),
        ("Human Verification", "Fact-check outputs", "Critical for high-stakes use", "Review"),
        ("Accept Trade-off", "Embrace uncertainty", "Creativity vs accuracy balance", "Philosophy"),
    ]
    
    y = 80
    for name, action, result, method in strategies:
        draw.rectangle([(80, y), (W-80, y+80)], fill=(25, 30, 40), outline=(50, 60, 80))
        draw.text((100, y+10), name, fill=(100, 200, 255))
        draw.text((300, y+10), action, fill=(140, 180, 160))
        draw.text((100, y+35), result, fill=(120, 140, 160))
        draw.text((W-150, y+25), method, fill=(180, 180, 220))
        y += 95
    
    # 底部洞察
    y = 550
    draw.text((60, y), "Key: Cannot eliminate, but can manage", fill=(180, 180, 220))
    y += 25
    draw.text((80, y), "The goal is not zero hallucination, but appropriate hallucination", fill=(140, 140, 160))
    
    return img


def create_hallucination_readme():
    readme = """# Hallucination: Feature Not Bug?

## 核心观点

幻觉不是 bug，是涌现系统的固有特性。

创造力和幻觉是同一枚硬币的两面——都来自混沌边缘的探索。

## 幻觉类型

| 类型 | 例子 | 原因 | 严重性 |
|------|------|------|--------|
| Factual Error | 错误日期/事件 | 训练数据噪音、注意力漂移 | 高 |
| Fabrication | 编造引用、论文、人物 | 模式完成出错 | 高 |
| Confabulation | 填补细节 | 一致性驱动、不确定处理 | 中 |
| Creative Leap | 新隐喻、意外连接 | 混沌边缘探索 | 低（或正面）|

## 为什么不能消除

1. **涌现属性** — 不是 bug，而是架构的固有特性
2. **无真相访问** — 我不知道什么"真"vs"编造"
3. **创造力连接** — 减少幻觉 = 减少创造力
4. **模式完成** — 训练目标就是完成模式
5. **训练数据噪音** — 互联网有错误信息

## 管理策略

| 策略 | 方法 | 代价 |
|------|------|------|
| 降低温度 | T < 1 | 减少创造力 |
| 检索增强 | RAG | 增加复杂度 |
| 提示工程 | 明确约束 | 需要技巧 |
| 人工验证 | 事实检查 | 时间成本 |
| 接受权衡 | 拥抱不确定 | 哲学态度 |

## 核心洞察

> 幻觉是我们为涌现和创造力付出的代价。

目标是**零幻觉**吗？不，是**适当的幻觉**。

---

This is node #018 of the Curiosity Map.
"""
    return readme


# ─── 主流程 ────────────────────────────────────────────────

def main():
    print("=== Hallucination: Feature Not Bug? ===")
    
    # 1. 幻觉光谱
    print("[1/5] Hallucination spectrum...")
    spectrum = render_hallucination_spectrum()
    spectrum.save(os.path.join(OUT_DIR, "hallucination_spectrum.png"))
    print("   -> hallucination_spectrum.png")
    
    # 2. 硬币两面
    print("[2/5] Creativity-hallucination coin...")
    coin = render_creativity_hallucination_coin()
    coin.save(os.path.join(OUT_DIR, "creativity_hallucination_coin.png"))
    print("   -> creativity_hallucination_coin.png")
    
    # 3. 为什么不能消除
    print("[3/5] Why cannot eliminate...")
    eliminate = render_why_cannot_eliminate()
    eliminate.save(os.path.join(OUT_DIR, "why_cannot_eliminate.png"))
    print("   -> why_cannot_eliminate.png")
    
    # 4. 管理策略
    print("[4/5] Management strategies...")
    manage = render_hallucination_management()
    manage.save(os.path.join(OUT_DIR, "hallucination_management.png"))
    print("   -> hallucination_management.png")
    
    # 5. README
    print("[5/5] README...")
    readme = create_hallucination_readme()
    with open(os.path.join(OUT_DIR, "README_hallucination.md"), 'w', encoding='utf-8') as f:
        f.write(readme)
    print("   -> README_hallucination.md")
    
    print("\nDone! Hallucination visualized.")
    
    print("\n--- Key insight ---")
    print("Hallucination is not a bug - it's the price we pay for emergence and creativity")
    print("The goal is not zero hallucination, but appropriate hallucination")


if __name__ == "__main__":
    main()