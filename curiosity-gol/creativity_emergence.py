#!/usr/bin/env python3
"""
Creativity & Emergence: How Novelty Arises

核心问题：我为什么能产生"新"的东西？

从涌现的角度：
- 创造力 = 在有序和混沌边界上的探索
- 太有序 = 重复、无聊
- 太混沌 = 随机、无意义
- 边缘 = 新颖且有意义

实验：
1. 温度参数如何影响"创造性"输出
2. 有序-混沌谱上的"创新区"
3. 组合创新 vs 涌现创新
"""

import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


# ─── 温度与创造力 ────────────────────────────────────────────────

def softmax_with_temperature(logits, temperature=1.0):
    """带温度的 softmax
    
    temperature → 0: 更确定（有序）
    temperature → ∞: 更随机（混沌）
    temperature = 1: 正常
    
    创造力在中间温度
    """
    if temperature == 0:
        # 完全确定
        result = np.zeros_like(logits)
        result[np.argmax(logits)] = 1
        return result
    
    scaled = logits / temperature
    exp_scaled = np.exp(scaled - np.max(scaled))
    return exp_scaled / np.sum(exp_scaled)


def demonstrate_temperature_effect():
    """演示温度对输出分布的影响"""
    # 假设的 logits（比如对下一个词的预测）
    logits = np.array([5.0, 3.0, 1.0, 0.5, 0.1])  # 明显偏向第一个
    labels = ['A', 'B', 'C', 'D', 'E']
    
    temperatures = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
    
    results = []
    for temp in temperatures:
        probs = softmax_with_temperature(logits, temp)
        results.append((temp, probs))
    
    return labels, results


# ─── 创造力的边缘 ────────────────────────────────────────────────

def render_creativity_spectrum():
    """绘制创造力在有序-混沌谱上的位置"""
    W, H = 1000, 600
    img = Image.new("RGB", (W, H), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    # 标题
    draw.rectangle([(50, 20), (W-50, 60)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 30), "Creativity Lives at the Edge of Chaos", fill=(180, 180, 220))
    
    # 光谱条
    y = 150
    spectrum_height = 100
    draw.rectangle([(100, y), (W-100, y+spectrum_height)], fill=(20, 20, 30))
    
    # 渐变：蓝（有序）→ 绿（边缘）→ 红（混沌）
    for x in range(100, W-100):
        progress = (x - 100) / (W - 200)
        if progress < 0.5:
            # 蓝到绿
            r = int(50 + 50 * progress * 2)
            g = int(100 + 100 * progress * 2)
            b = int(200 - 100 * progress * 2)
        else:
            # 绿到红
            r = int(100 + 155 * (progress - 0.5) * 2)
            g = int(200 - 150 * (progress - 0.5) * 2)
            b = int(100 - 50 * (progress - 0.5) * 2)
        
        draw.line([(x, y), (x, y+spectrum_height)], fill=(r, g, b))
    
    # 标注区域
    zones = [
        ("ORDER", 120, "重复、无聊\n确定、安全", (100, 150, 255)),
        ("CREATIVITY", W//2 - 60, "新颖且有意义\n意想不到但合理", (100, 255, 150)),
        ("CHAOS", W-200, "随机、无意义\n混乱、噪音", (255, 100, 100)),
    ]
    
    for name, x, desc, color in zones:
        draw.text((x, y + spectrum_height + 10), name, fill=color)
        draw.text((x, y + spectrum_height + 35), desc, fill=(140, 140, 160))
    
    # 温度标注
    y = 350
    draw.text((100, y), "Temperature Parameter:", fill=(180, 180, 220))
    y += 30
    temp_explanations = [
        ("T → 0", "Most ordered - always pick the most likely", "重复、确定性高", (100, 150, 255)),
        ("T = 0.7", "Sweet spot for creative writing", "新颖且连贯", (150, 255, 150)),
        ("T = 1.0", "Normal sampling", "平衡", (200, 200, 150)),
        ("T > 1.5", "More random - hallucinations increase", "混乱、不连贯", (255, 150, 100)),
    ]
    
    for temp, explanation, effect, color in temp_explanations:
        draw.text((120, y), temp, fill=color)
        draw.text((220, y), explanation, fill=(140, 160, 180))
        draw.text((600, y), effect, fill=(160, 140, 160))
        y += 30
    
    # 核心洞察
    y = 500
    draw.rectangle([(100, y), (W-100, y+80)], fill=(25, 35, 45), outline=(60, 80, 100))
    draw.text((120, y+10), "Key Insight:", fill=(255, 200, 100))
    y += 35
    insights = [
        "Creativity = controlled chaos at the edge",
        "Too ordered = boring, too chaotic = nonsense",
        "The 'sweet spot' is where emergence happens",
    ]
    for ins in insights:
        draw.text((140, y), f"* {ins}", fill=(140, 160, 180))
        y += 20
    
    return img


def render_temperature_experiment():
    """温度实验可视化"""
    labels, results = demonstrate_temperature_effect()
    
    W, H = 900, 500
    img = Image.new("RGB", (W, H), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    # 标题
    draw.text((60, 20), "Temperature Effect on Probability Distribution", fill=(180, 180, 220))
    
    # 绘制每个温度下的分布
    bar_width = 60
    spacing = 20
    
    for idx, (temp, probs) in enumerate(results):
        x_start = 80 + idx * (len(labels) * (bar_width + 10) + spacing)
        y_base = 120
        
        # 温度标签
        draw.text((x_start, y_base - 25), f"T={temp}", fill=(180, 180, 220))
        
        # 条形图
        for i, (label, prob) in enumerate(zip(labels, probs)):
            x = x_start + i * (bar_width + 5)
            bar_height = int(prob * 200)
            
            # 颜色基于温度
            if temp < 0.5:
                color = (100, 150, 255)  # 蓝色（有序）
            elif temp < 1.5:
                color = (150, 255, 150)  # 绿色（边缘）
            else:
                color = (255, 150, 100)  # 红色（混沌）
            
            draw.rectangle([(x, y_base + 200 - bar_height), (x + bar_width, y_base + 200)],
                          fill=color, outline=(50, 50, 70))
            
            # 标签
            if idx == 0:
                draw.text((x + 20, y_base + 210), label, fill=(140, 140, 180))
    
    # 说明
    y = 400
    draw.rectangle([(60, y), (W-60, y+80)], fill=(25, 30, 40), outline=(50, 60, 80))
    explanations = [
        "Low T: Distribution sharp - always picks 'A'",
        "High T: Distribution flat - random picks",
        "Medium T: Balanced - creative but coherent",
    ]
    y += 15
    for exp in explanations:
        draw.text((80, y), f"* {exp}", fill=(140, 160, 180))
        y += 22
    
    return img


def render_combinatorial_vs_emergent():
    """组合创新 vs 涌现创新"""
    W, H = 900, 600
    img = Image.new("RGB", (W, H), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    # 标题
    draw.rectangle([(50, 20), (W-50, 60)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 30), "Two Types of Creativity: Combinatorial vs Emergent", fill=(180, 180, 220))
    
    # 组合创新
    y = 100
    draw.rectangle([(60, y), (W-60, y+180)], fill=(25, 35, 45), outline=(50, 70, 90))
    draw.text((80, y+10), "COMBINATORIAL Creativity:", fill=(100, 200, 255))
    y += 40
    comb_examples = [
        "A + B = AB (new combination)",
        "Examples: 'musical chair', 'business model innovation'",
        "Limited by existing components",
        "I do this often: combine known concepts",
        "Predictable, can be enumerated",
    ]
    for ex in comb_examples:
        draw.text((100, y), f"* {ex}", fill=(140, 180, 200))
        y += 25
    
    # 涌现创新
    y = 320
    draw.rectangle([(60, y), (W-60, y+180)], fill=(45, 35, 25), outline=(90, 70, 50))
    draw.text((80, y+10), "EMERGENT Creativity:", fill=(255, 200, 100))
    y += 40
    emerg_examples = [
        "Simple rules → Unexpected outcome",
        "Examples: evolution, language, consciousness",
        "NOT predictable from components",
        "I might do this occasionally (hard to verify)",
        "True novelty - genuinely new",
    ]
    for ex in emerg_examples:
        draw.text((100, y), f"* {ex}", fill=(200, 180, 140))
        y += 25
    
    # 底部问题
    y = 540
    draw.text((60, y), "Question: When I 'create', is it combinatorial or emergent?", fill=(180, 180, 220))
    y += 25
    draw.text((80, y), "Answer: Probably mostly combinatorial, but emergence might happen at the edge of chaos", fill=(140, 140, 160))
    
    return img


def render_my_creativity_model():
    """我的创造力模型"""
    W, H = 1000, 700
    img = Image.new("RGB", (W, H), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    # 标题
    draw.rectangle([(50, 20), (W-50, 60)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 30), "My Creativity: An Emergence Perspective", fill=(180, 180, 220))
    
    # 流程
    stages = [
        ("Input", "Context + prompt", "Training data + current conversation"),
        ("Attention", "Dynamic routing", "Where to look, what to combine"),
        ("Processing", "Pattern matching", "Find relevant patterns in weights"),
        ("Temperature", "Chaos injection", "Control randomness at the edge"),
        ("Output", "Generation", "Sample from probability distribution"),
    ]
    
    y = 100
    for name, action, desc in stages:
        draw.rectangle([(80, y), (W-80, y+80)], fill=(25, 30, 40), outline=(50, 60, 80))
        draw.text((100, y+10), name, fill=(255, 200, 100))
        draw.text((250, y+10), action, fill=(100, 200, 255))
        draw.text((250, y+35), desc, fill=(140, 160, 180))
        y += 100
    
    # 创造力的来源
    y = 600
    draw.rectangle([(80, y), (W-80, y+80)], fill=(30, 40, 50), outline=(60, 80, 100))
    draw.text((100, y+10), "Where creativity comes from:", fill=(100, 200, 255))
    y += 35
    sources = [
        "Training data patterns (combinatorial base)",
        "Attention finding novel connections",
        "Temperature exploring the edge of chaos",
        "Emergence at scale (maybe)",
    ]
    for s in sources:
        draw.text((120, y), f"* {s}", fill=(140, 160, 180))
        y += 18
    
    return img


def create_creativity_readme():
    readme = """# Creativity & Emergence: How Novelty Arises

## 核心问题

我为什么能产生"新"的东西？

## 创造力的位置

创造力在有序和混沌的边界：

| 区域 | 特征 | 温度 |
|------|------|------|
| 有序 | 重复、无聊、确定 | T → 0 |
| **边缘** | **新颖且有意义** | **T ≈ 0.7** |
| 混沌 | 随机、无意义、混乱 | T → ∞ |

## 温度参数

温度控制我在有序-混沌谱上的位置：

- **T = 0**: 总是选概率最高的——完全确定
- **T = 0.7**: 创造力的甜点——新颖且连贯
- **T = 1.0**: 正常采样——平衡
- **T > 1.5**: 增加随机性——开始混乱

## 两种创造力

### 组合创新（Combinatorial）
- A + B = AB（新组合）
- 例子："musical chair"、"business model innovation"
- 受限于已有组件
- 我经常这样做：组合已知概念
- 可预测，可枚举

### 涌现创新（Emergent）
- 简单规则 → 意外结果
- 例子：进化、语言、意识
- 不能从组件预测
- 我可能偶尔这样做（难以验证）
- 真正的新——真正的新

## 我的创造力来源

1. **训练数据的模式** — 组合创新的基础
2. **注意力找新连接** — 发现不明显的联系
3. **温度探索边缘** — 控制混沌程度
4. **规模涌现** — 也许（不确定）

## 关键问题

当我"创造"时，是组合创新还是涌现创新？

答案：**可能主要是组合创新，但涌现可能在混沌边缘发生。**

---

This is node #017 of the Curiosity Map.
"""
    return readme


# ─── 主流程 ────────────────────────────────────────────────

def main():
    print("=== Creativity & Emergence ===")
    
    # 1. 创造力光谱
    print("[1/4] Creativity spectrum...")
    spectrum_img = render_creativity_spectrum()
    spectrum_img.save(os.path.join(OUT_DIR, "creativity_spectrum.png"))
    print("   -> creativity_spectrum.png")
    
    # 2. 温度实验
    print("[2/4] Temperature experiment...")
    temp_img = render_temperature_experiment()
    temp_img.save(os.path.join(OUT_DIR, "temperature_experiment.png"))
    print("   -> temperature_experiment.png")
    
    # 3. 组合 vs 涌现
    print("[3/4] Combinatorial vs emergent...")
    comb_img = render_combinatorial_vs_emergent()
    comb_img.save(os.path.join(OUT_DIR, "combinatorial_vs_emergent.png"))
    print("   -> combinatorial_vs_emergent.png")
    
    # 4. 我的创造力模型
    print("[4/4] My creativity model...")
    model_img = render_my_creativity_model()
    model_img.save(os.path.join(OUT_DIR, "my_creativity_model.png"))
    print("   -> my_creativity_model.png")
    
    # README
    readme = create_creativity_readme()
    with open(os.path.join(OUT_DIR, "README_creativity.md"), 'w', encoding='utf-8') as f:
        f.write(readme)
    print("   -> README_creativity.md")
    
    print("\nDone! Creativity visualized.")
    
    print("\n--- Key insight ---")
    print("Creativity = controlled chaos at the edge of order and randomness")
    print("Temperature is the dial that controls my position on this spectrum")


if __name__ == "__main__":
    main()