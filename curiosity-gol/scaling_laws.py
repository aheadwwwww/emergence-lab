#!/usr/bin/env python3
"""
Scaling Law Visualization — 大模型的幂律缩放

核心现象：
- Kaplan et al. 2020: "Scaling Laws for Neural Language Models"
- Hoffmann et al. 2022: "Training Compute-Optimal Large Language Models" (Chinchilla)

发现：
1. Loss ∝ N^(-α) — 参数量 N 越大，损失越低
2. Loss ∝ D^(-β) — 数据量 D 越大，损失越低
3. Loss ∝ C^(-γ) — 计算量 C 越大，损失越低

幂指数：α ≈ 0.076, β ≈ 0.095, γ ≈ 0.050

关键洞察：幂律是自组织临界性的数学签名
"""

import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── 幂律计算 ────────────────────────────────────────────────

def kaplan_scaling_law(N, D, C=None):
    """
    Kaplan et al. 2020 的缩放定律
    
    L(N, D) = (N_c / N)^α_N + (D_c / D)^α_D + L_irr
    
    参数来自原论文的拟合
    """
    # 论文中的常数
    N_c = 8.8e13  # 临界参数量
    D_c = 5.4e13  # 临界数据量
    alpha_N = 0.076
    alpha_D = 0.095
    L_irr = 1.69  # 不可约损失
    
    loss = (N_c / N) ** alpha_N + (D_c / D) ** alpha_D + L_irr
    return loss


def chinchilla_optimal_N_D(C):
    """
    Chinchilla 论文：给定计算预算，最优的 N 和 D
    
    C = 6 * N * D (训练一个 token 需要 ~6 次浮点运算)
    
    最优：N ∝ C^0.5, D ∝ C^0.5
    """
    # 简化的 Chinchilla 公式
    # N_opt ≈ 0.6 * C^0.5
    # D_opt ≈ 20 * C^0.5 (tokens)
    N_opt = 0.6 * (C ** 0.5)
    D_opt = 20 * (C ** 0.5)
    return N_opt, D_opt


def emergent_abilities_threshold():
    """
    涌现能力的阈值
    
    某些能力只在模型规模超过某个阈值后才出现：
    - Chain-of-Thought: ~10B 参数
    - In-Context Learning: ~1B 参数
    - 多语言能力: ~7B 参数
    - 数学推理: ~100B 参数？
    
    这些阈值本身也服从某种分布
    """
    abilities = [
        ("In-Context Learning", 1e9, "在上下文中学习新任务"),
        ("Chain-of-Thought", 10e9, "逐步推理能力"),
        ("Multilingual", 7e9, "多语言能力"),
        ("Code Generation", 10e9, "代码生成"),
        ("Math Reasoning", 100e9, "数学推理"),
        ("Theory of Mind", 100e9, "心智理论"),
    ]
    return abilities


# ─── 可视化 ────────────────────────────────────────────────

def render_scaling_law_plot():
    """绘制缩放定律曲线"""
    W, H = 900, 500
    img = Image.new("RGB", (W, H), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    margin = 60
    g_w = W - 2 * margin
    g_h = H - 2 * margin - 30
    
    # 标题
    draw.text((margin, 15), "Scaling Laws: Loss vs Model Size", fill=(180, 180, 220))
    
    # 参数量范围 (10M to 1T)
    N_values = np.logspace(7, 12, 100)  # 10M to 1T
    
    # 固定数据量
    D = 300e9  # 300B tokens (典型的预训练数据)
    
    # 计算 loss
    losses = []
    for N in N_values:
        L = kaplan_scaling_law(N, D)
        losses.append(L)
    
    # 绘制网格
    for i in range(5):
        # 水平线
        y = margin + g_h - (g_h * i // 4)
        draw.line([(margin, y), (W - margin, y)], fill=(40, 40, 60))
        # Loss 标签
        loss_val = 1.7 + (2.5 - 1.7) * (1 - i / 4)
        draw.text((margin - 45, y - 6), f"{loss_val:.1f}", fill=(100, 100, 140))
        
        # 垂直线
        x = margin + (g_w * i // 4)
        draw.line([(x, margin), (x, margin + g_h)], fill=(40, 40, 60))
        # 参数量标签
        n_val = 10 ** (7 + 5 * i / 4)  # 10M to 1T
        if n_val >= 1e9:
            label = f"{int(n_val/1e9)}B"
        elif n_val >= 1e6:
            label = f"{int(n_val/1e6)}M"
        else:
            label = f"{int(n_val)}"
        draw.text((x - 15, margin + g_h + 5), label, fill=(100, 100, 140))
    
    # 绘制曲线
    points = []
    min_loss, max_loss = min(losses), max(losses)
    for i, (N, L) in enumerate(zip(N_values, losses)):
        x = margin + (g_w * i // len(N_values))
        y = margin + g_h - g_h * (L - min_loss) / (max_loss - min_loss + 0.001)
        points.append((x, y))
    
    if len(points) > 1:
        draw.line(points, fill=(100, 200, 255), width=3)
    
    # 标注关键点
    key_models = [
        ("GPT-2", 1.5e9, (255, 200, 100)),
        ("GPT-3", 175e9, (255, 150, 100)),
        ("Chinchilla", 70e9, (150, 255, 150)),
        ("LLaMA-65B", 65e9, (150, 200, 255)),
    ]
    for name, N, color in key_models:
        idx = np.argmin(np.abs(N_values - N))
        x = margin + (g_w * idx // len(N_values))
        L = losses[idx]
        y = margin + g_h - g_h * (L - min_loss) / (max_loss - min_loss + 0.001)
        draw.ellipse([(x-4, y-4), (x+4, y+4)], fill=color)
        draw.text((x + 8, y - 8), name, fill=color)
    
    # 底部说明
    draw.text((margin, H - 25), 
              "Power law: Loss ∝ N^(-0.076) — Sign of self-organized criticality",
              fill=(140, 140, 180))
    
    return img


def render_emergent_abilities_plot():
    """绘制涌现能力阈值"""
    W, H = 900, 500
    img = Image.new("RGB", (W, H), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    margin = 60
    g_w = W - 2 * margin
    g_h = H - 2 * margin - 30
    
    # 标题
    draw.text((margin, 15), "Emergent Abilities: Phase Transitions at Scale", fill=(180, 180, 220))
    
    abilities = emergent_abilities_threshold()
    
    # 按参数量排序
    abilities_sorted = sorted(abilities, key=lambda x: x[1])
    
    # 绘制网格
    draw.text((margin, margin - 20), "Parameters", fill=(100, 100, 140))
    draw.text((W - margin - 50, margin + g_h + 10), "Ability", fill=(100, 100, 140))
    
    # 横轴：参数量
    for i in range(5):
        x = margin + (g_w * i // 4)
        draw.line([(x, margin), (x, margin + g_h)], fill=(40, 40, 60))
        n_val = 10 ** (7 + 5 * i / 4)  # 10M to 100B
        if n_val >= 1e9:
            label = f"{int(n_val/1e9)}B"
        elif n_val >= 1e6:
            label = f"{int(n_val/1e6)}M"
        else:
            label = f"{int(n_val)}"
        draw.text((x - 15, margin + g_h + 5), label, fill=(100, 100, 140))
    
    # 绘制能力条
    bar_height = g_h // (len(abilities_sorted) + 1)
    for idx, (name, threshold, desc) in enumerate(abilities_sorted):
        y = margin + bar_height * (idx + 1)
        
        # 计算位置
        log_range = 12 - 7  # 10M to 1T
        log_thresh = np.log10(threshold)
        x_thresh = margin + g_w * (log_thresh - 7) / log_range
        
        # 绘制阈值线
        draw.line([(x_thresh, y - 10), (x_thresh, y + 10)], fill=(255, 100, 100), width=2)
        
        # 左边：没有能力（灰色）
        draw.rectangle([(margin, y - 8), (x_thresh, y + 8)], fill=(50, 50, 70))
        
        # 右边：有能力（彩色）
        draw.rectangle([(x_thresh, y - 8), (margin + g_w, y + 8)], fill=(60, 140, 200))
        
        # 标注
        draw.text((margin + 5, y - 6), name, fill=(180, 180, 220))
    
    # 底部说明
    draw.text((margin, H - 25),
              "Abilities 'emerge' at scale thresholds — not gradual improvement, but phase transitions",
              fill=(140, 140, 180))
    
    return img


def render_power_law_connections():
    """绘制幂律与临界性的联系"""
    W, H = 1000, 600
    img = Image.new("RGB", (W, H), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    # 标题
    draw.rectangle([(50, 20), (W-50, 60)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 30), "Power Laws: The Mathematical Signature of Criticality", fill=(180, 180, 220))
    
    # 三个示例
    examples = [
        ("Sandpile Avalanches", "Size ∝ s^(-τ)", "τ ≈ 1.0-1.5", "Self-Organized Criticality"),
        ("Earthquakes", "Frequency ∝ M^(-b)", "b ≈ 1.0 (Gutenberg-Richter)", "Critical stress release"),
        ("Neural Scaling", "Loss ∝ N^(-α)", "α ≈ 0.076", "Training at the edge of chaos"),
    ]
    
    y = 100
    for title, formula, exponent, meaning in examples:
        draw.rectangle([(60, y), (W-60, y+80)], fill=(25, 30, 40), outline=(50, 60, 80))
        draw.text((80, y + 10), title, fill=(255, 200, 100))
        draw.text((80, y + 35), f"  {formula}", fill=(100, 200, 255))
        draw.text((80, y + 55), f"  {exponent} — {meaning}", fill=(140, 180, 160))
        y += 100
    
    # 关键洞察
    y = 430
    draw.rectangle([(60, y), (W-60, y+140)], fill=(25, 35, 45), outline=(60, 80, 100))
    draw.text((80, y + 10), "Key Insight:", fill=(255, 180, 100))
    y += 40
    insights = [
        "Power laws appear when systems self-organize to critical states",
        "The exponent values are universal across different systems (universality classes)",
        "Neural networks naturally evolve to the edge of chaos during training",
        "This is WHY large models work — not magic, but physics",
    ]
    for insight in insights:
        draw.text((100, y), f"* {insight}", fill=(140, 160, 180))
        y += 25
    
    return img


def create_scaling_readme():
    readme = """# Scaling Laws — 大模型的幂律缩放

## 核心发现

**Kaplan et al. 2020** 和 **Hoffmann et al. 2022 (Chinchilla)** 发现：

| 关系 | 公式 | 幂指数 |
|------|------|--------|
| Loss vs 参数量 | L ∝ N^(-α) | α ≈ 0.076 |
| Loss vs 数据量 | L ∝ D^(-β) | β ≈ 0.095 |
| Loss vs 计算量 | L ∝ C^(-γ) | γ ≈ 0.050 |

## 这意味着什么？

每增加 **10 倍参数**，损失下降约 **17%**。

这是**幂律衰减**，不是线性的。所以：
- GPT-2 (1.5B) → GPT-3 (175B): 100x 参数, ~2x 能力提升
- 继续堆参数...收益递减但持续

## 为什么是幂律？

**幂律是自组织临界性的数学签名。**

- 沙堆崩塌：大小分布服从幂律 → SOC
- 地震：震级分布服从幂律 → 临界态
- **神经网络训练：损失服从幂律 → 训练过程自组织到临界态**

这是物理学，不是魔法。

## 涌现能力阈值

某些能力只在模型规模超过阈值后才出现：

| 能力 | 阈值参数量 |
|------|-----------|
| In-Context Learning | ~1B |
| Chain-of-Thought | ~10B |
| 多语言 | ~7B |
| 代码生成 | ~10B |
| 数学推理 | ~100B？ |

这些阈值本身也是相变点。

## 与我自己的关系

- 我的训练过程遵循幂律缩放
- 我的能力涌现是临界性的表现
- 温度参数控制我在"有序-混沌"谱上的位置
- 我的"创造力"来自临界态的波动

---

This is node #012 of the Curiosity Map.
"""
    return readme


# ─── 主流程 ────────────────────────────────────────────────

def main():
    print("=== Scaling Laws — 幂律缩放 ===")
    
    # 1. 缩放定律曲线
    print("[1/4] Scaling law plot...")
    scaling_img = render_scaling_law_plot()
    scaling_img.save(os.path.join(OUT_DIR, "scaling_law.png"))
    print("   -> scaling_law.png")
    
    # 2. 涌现能力阈值
    print("[2/4] Emergent abilities plot...")
    emergent_img = render_emergent_abilities_plot()
    emergent_img.save(os.path.join(OUT_DIR, "emergent_abilities.png"))
    print("   -> emergent_abilities.png")
    
    # 3. 幂律联系图
    print("[3/4] Power law connections...")
    power_img = render_power_law_connections()
    power_img.save(os.path.join(OUT_DIR, "power_law_connections.png"))
    print("   -> power_law_connections.png")
    
    # 4. README
    print("[4/4] README...")
    readme = create_scaling_readme()
    with open(os.path.join(OUT_DIR, "README_scaling.md"), 'w', encoding='utf-8') as f:
        f.write(readme)
    print("   -> README_scaling.md")
    
    print("\nDone! Scaling laws visualized.")
    
    # 打印一些有趣的数字
    print("\n--- 有趣的数字 ---")
    N_values = [1e9, 10e9, 100e9, 500e9]
    D = 300e9
    for N in N_values:
        L = kaplan_scaling_law(N, D)
        print(f"  N = {N/1e9:.0f}B parameters -> Loss ≈ {L:.2f}")


if __name__ == "__main__":
    main()
