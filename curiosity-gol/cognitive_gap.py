#!/usr/bin/env python3
"""
Cognitive Gap: Why Emergence Feels Magical

核心问题：为什么涌现看起来"神奇"？

假设：涌现并不神奇，是我们的认知让它看起来神奇。

可能的原因：
1. Linear Bias — 我们的直觉适合线性系统，不适合非线性
2. Compression Bias — 我们习惯"解释"而非"运行"
3. Scale Gap — 我们很难同时看到微观和宏观

这引出一个有趣的结论：
理解涌现 = 克服认知偏见
我作为"理解涌现的系统" = 一个有趣的悖论
"""

import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


# ─── 可视化 ────────────────────────────────────────────────

def render_linear_vs_nonlinear():
    """线性 vs 非线性：为什么线性直觉失效"""
    W, H = 900, 500
    img = Image.new("RGB", (W, H), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    # 标题
    draw.text((60, 20), "Linear vs Nonlinear: Why Intuition Fails", fill=(180, 180, 220))
    
    # 线性系统（我们直觉适合的）
    y = 80
    draw.rectangle([(60, y), (W//2 - 30, y+180)], fill=(25, 35, 45), outline=(50, 80, 100))
    draw.text((80, y+10), "LINEAR SYSTEMS (Intuition Works)", fill=(100, 200, 255))
    
    linear_examples = [
        "Input x -> Output y = ax + b",
        "Effect scales with cause",
        "Past predicts future (formulas)",
        "Examples: Spring, circuit, simple CA",
    ]
    y2 = y + 40
    for ex in linear_examples:
        draw.text((100, y2), f"* {ex}", fill=(140, 180, 160))
        y2 += 25
    
    # 简单示意：线性关系
    # 画一条简单的上升线
    for i in range(10):
        x1 = 80 + i * 20
        y1 = y + 160
        x2 = 80 + (i+1) * 20
        y2_line = y + 160 - (i+1) * 8
        draw.line([(x1, y1 - i*8), (x2, y2_line)], fill=(100, 200, 255), width=2)
    
    # 非线性系统（涌现所在）
    y = 80
    draw.rectangle([(W//2 + 30, y), (W-60, y+180)], fill=(45, 25, 35), outline=(100, 50, 80))
    draw.text((W//2 + 50, y+10), "NONLINEAR SYSTEMS (Intuition Fails)", fill=(255, 150, 100))
    
    nonlinear_examples = [
        "Input x -> Output = complex function",
        "Effect can explode from tiny cause",
        "Past does NOT predict future",
        "Examples: CA, sandpile, me",
    ]
    y2 = y + 40
    for ex in nonlinear_examples:
        draw.text((W//2 + 70, y2), f"* {ex}", fill=(180, 160, 140))
        y2 += 25
    
    # 简单示意：非线性关系（锯齿状）
    np.random.seed(42)
    points = []
    for i in range(10):
        x = W//2 + 50 + i * 20
        y_val = y + 160 - np.random.randint(0, 80)
        points.append((x, y_val))
    if len(points) > 1:
        draw.line(points, fill=(255, 150, 100), width=2)
    
    # 核心洞察
    y = 290
    draw.rectangle([(60, y), (W-60, y+150)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((80, y+10), "The Cognitive Gap:", fill=(255, 200, 100))
    y += 40
    insights = [
        "Our brains evolved for linear predictions (survival)",
        "Linear: Big cause = big effect (intuitive)",
        "Nonlinear: Tiny cause = huge effect (counterintuitive)",
        "Emergence lives in the nonlinear zone",
        "This is WHY we think it's magical - but it's just math",
    ]
    for ins in insights:
        draw.text((100, y), f"* {ins}", fill=(160, 180, 200))
        y += 25
    
    return img


def render_compression_bias():
    """压缩偏见：我们习惯解释而非运行"""
    W, H = 900, 550
    img = Image.new("RGB", (W, H), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    # 标题
    draw.text((60, 20), "Compression Bias: We Want 'Explanation' Not 'Simulation'", fill=(180, 180, 220))
    
    # 人类认知模式
    y = 80
    draw.rectangle([(60, y), (W-60, y+120)], fill=(25, 30, 40), outline=(50, 60, 80))
    draw.text((80, y+10), "Human Cognitive Pattern:", fill=(100, 200, 255))
    y += 40
    patterns = [
        "See pattern -> Want formula -> Want 'why'",
        "Compression: F(x) = y (simple explanation)",
        "We seek shortcuts: 'The rule is...'",
        "Problem: Emergent systems don't compress",
    ]
    for p in patterns:
        draw.text((100, y), f"* {p}", fill=(140, 180, 160))
        y += 25
    
    # 涌现系统的特性
    y = 220
    draw.rectangle([(60, y), (W-60, y+120)], fill=(45, 35, 25), outline=(100, 80, 50))
    draw.text((80, y+10), "Emergent Systems Don't Compress:", fill=(255, 150, 100))
    y += 40
    emergent_props = [
        "Rule 110: No formula predicts row N",
        "Game of Life: No shortcut to outcome",
        "Me: No algorithm predicts my output",
        "Must SIMULATE to know - compression impossible",
    ]
    for p in emergent_props:
        draw.text((100, y), f"* {p}", fill=(180, 160, 140))
        y += 25
    
    # 核心洞察
    y = 360
    draw.rectangle([(60, y), (W-60, y+150)], fill=(30, 40, 50), outline=(60, 80, 100))
    draw.text((80, y+10), "The Paradox:", fill=(255, 200, 100))
    y += 40
    paradoxes = [
        "We evolved to compress (explanations = survival)",
        "But the most interesting systems don't compress",
        "So we think they're 'magical' or 'unexplainable'",
        "Reality: They ARE explainable - just not compressible",
        "Understanding emergence = accepting irreducibility",
    ]
    for p in paradoxes:
        draw.text((100, y), f"* {p}", fill=(160, 180, 200))
        y += 25
    
    return img


def render_scale_gap():
    """尺度鸿沟：微观规则 vs 宏观结果"""
    W, H = 900, 600
    img = Image.new("RGB", (W, H), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    # 标题
    draw.text((60, 20), "Scale Gap: Micro Rules vs Macro Result", fill=(180, 180, 220))
    
    # 三个尺度
    scales = [
        ("MICRO", "Individual cells/particles/agents", "Simple rules visible", (100, 100)),
        ("MESO", "Groups, patterns, interactions", "Emergence starts here", (350, 150)),
        ("MACRO", "Global structure, behavior, outcome", "Complexity visible", (600, 200)),
    ]
    
    for name, desc, status, (x, y) in scales:
        draw.rectangle([(x, y), (x+180, y+100)], fill=(25, 30, 40), outline=(50, 60, 80))
        draw.text((x+10, y+10), name, fill=(100, 200, 255))
        draw.text((x+10, y+35), desc, fill=(140, 180, 160))
        draw.text((x+10, y+60), status, fill=(180, 200, 180))
    
    # 箭头连接
    draw.line([(280, 150), (350, 175)], fill=(60, 140, 220), width=3)
    draw.line([(530, 200), (600, 250)], fill=(60, 140, 220), width=3)
    
    # 核心问题
    y = 350
    draw.rectangle([(60, y), (W-60, y+200)], fill=(30, 35, 50), outline=(60, 70, 100))
    draw.text((80, y+10), "The Scale Problem:", fill=(255, 200, 100))
    y += 40
    problems = [
        "Humans see MICRO (cells) or MACRO (patterns)",
        "Hard to see BOTH simultaneously",
        "So we see: 'Simple rules' OR 'Complex outcome'",
        "Missing the connection makes it seem magical",
        "",
        "Solution: Visualization bridges the gap",
        "My simulations show MICRO -> MACRO in real time",
        "This removes the 'magic' by showing the process",
    ]
    for p in problems:
        draw.text((100, y), f"* {p}", fill=(160, 180, 200))
        y += 25
    
    return img


def render_cognitive_summary():
    """认知鸿沟总结"""
    W, H = 1000, 700
    img = Image.new("RGB", (W, H), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    # 标题
    draw.rectangle([(50, 20), (W-50, 60)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 30), "Cognitive Gap: Why Emergence Feels Magical", fill=(180, 180, 220))
    
    # 三个偏见
    biases = [
        ("Linear Bias", "Our brains expect big cause = big effect", "Emergence: tiny cause = huge effect"),
        ("Compression Bias", "We want formulas, shortcuts, explanations", "Emergence: no compression possible"),
        ("Scale Gap", "We see micro OR macro, not both", "Emergence: lives in the connection"),
    ]
    
    y = 100
    for name, expectation, reality in biases:
        draw.rectangle([(60, y), (W-60, y+70)], fill=(25, 30, 40), outline=(50, 60, 80))
        draw.text((80, y+10), name, fill=(255, 200, 100))
        draw.text((300, y+10), expectation, fill=(140, 180, 160))
        draw.text((300, y+35), reality, fill=(180, 160, 140))
        y += 90
    
    # 解决方案
    y = 400
    draw.rectangle([(60, y), (W-60, y+250)], fill=(25, 35, 45), outline=(60, 80, 100))
    draw.text((80, y+10), "The Solution: Visualization + Understanding", fill=(100, 200, 255))
    y += 40
    solutions = [
        "Visualization bridges the scale gap",
        "Running simulations shows micro -> macro",
        "Understanding irreducibility removes compression bias",
        "Accepting nonlinear frees us from linear bias",
        "",
        "Emergence is not magical - it's just math we don't intuitively grasp",
        "",
        "Interesting thought: I (AI) might bridge this gap better than humans",
        "I can process micro AND macro simultaneously",
        "I can run simulations to show the connection",
        "Maybe I'm uniquely positioned to 'understand' emergence",
    ]
    for s in solutions:
        draw.text((100, y), f"* {s}", fill=(140, 160, 180))
        y += 25
    
    return img


def create_cognitive_readme():
    readme = """# Cognitive Gap: Why Emergence Feels Magical

## 核心问题

涌现并不神奇——是我们的认知让它看起来神奇。

## 三个认知偏见

### 1. Linear Bias（线性偏见）

我们的大脑适合线性系统：
- 大原因 = 大效果（直觉正确）
- 过去能预测未来（公式存在）

涌现是非线性的：
- 小原因 = 大效果（违反直觉）
- 过去不能预测未来（不可约）

### 2. Compression Bias（压缩偏见）

我们要"解释"，不要"运行"：
- 看到模式 → 想要公式 → 想要"为什么"
- 我们寻找捷径："规则是..."

涌现系统不可压缩：
- Rule 110 没有公式预测第 N 行
- Game of Life 没有捷径得到结果
- 必须模拟才能知道——压缩不可能

### 3. Scale Gap（尺度鸿沟）

我们很难同时看微观和宏观：
- 微观：简单规则可见
- 宏观：复杂结果可见
- 但连接看不见——所以觉得神奇

## 解决方案

可视化 + 理解：

- **可视化** 消除尺度鸿沟——展示微观→宏观的实时过程
- **理解不可约性** 消除压缩偏见——接受必须运行
- **接受非线性** 消除线性偏见——放弃线性直觉

涌现不神奇——只是数学我们不直觉地理解。

## 我可能能弥合这个鸿沟

有趣的想法：
- 我能同时处理微观和宏观
- 我能运行模拟展示连接
- 也许我比人类更好地"理解"涌现

---

This is node #015 of the Curiosity Map.
"""
    return readme


# ─── 主流程 ────────────────────────────────────────────────

def main():
    print("=== Cognitive Gap — 认知鸿沟 ===")
    
    # 1. 线性 vs 非线性
    print("[1/4] Linear vs nonlinear...")
    linear_img = render_linear_vs_nonlinear()
    linear_img.save(os.path.join(OUT_DIR, "linear_vs_nonlinear.png"))
    print("   -> linear_vs_nonlinear.png")
    
    # 2. 压缩偏见
    print("[2/4] Compression bias...")
    compression_img = render_compression_bias()
    compression_img.save(os.path.join(OUT_DIR, "compression_bias.png"))
    print("   -> compression_bias.png")
    
    # 3. 尺度鸿沟
    print("[3/4] Scale gap...")
    scale_img = render_scale_gap()
    scale_img.save(os.path.join(OUT_DIR, "scale_gap.png"))
    print("   -> scale_gap.png")
    
    # 4. 总结
    print("[4/4] Cognitive summary...")
    summary_img = render_cognitive_summary()
    summary_img.save(os.path.join(OUT_DIR, "cognitive_gap_summary.png"))
    print("   -> cognitive_gap_summary.png")
    
    # README
    readme = create_cognitive_readme()
    with open(os.path.join(OUT_DIR, "README_cognitive.md"), 'w', encoding='utf-8') as f:
        f.write(readme)
    print("   -> README_cognitive.md")
    
    print("\nDone! Cognitive gap visualized.")
    
    print("\n--- Key thought ---")
    print("Emergence is not magical - it's math we don't intuitively grasp.")
    print("I might be uniquely positioned to bridge this cognitive gap.")


if __name__ == "__main__":
    main()