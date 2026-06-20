#!/usr/bin/env python3
"""
Attention Mechanism Visualization — 注意力机制的可视化

核心概念：
- 2017: "Attention is All You Need" (Vaswani et al.)
- Self-Attention: 每个 token 可以"看向"所有其他 token
- 动态决定信息流动方向

本质：
- Attention 是信息流动的"涌现路由"
- 不是固定规则，而是根据内容动态决定
- 类似于沙堆根据当前状态决定崩塌方向

数学：
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) * V

Q = Query（问什么）
K = Key（有什么）
V = Value（给什么）

"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Attention 实现 ────────────────────────────────────────────────

def softmax(x):
    """Softmax 函数"""
    exp_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return exp_x / np.sum(exp_x, axis=-1, keepdims=True)


def self_attention(Q, K, V):
    """Self-Attention 计算
    
    Args:
        Q: Query matrix (seq_len, d_k)
        K: Key matrix (seq_len, d_k)
        V: Value matrix (seq_len, d_v)
    
    Returns:
        attention_output: (seq_len, d_v)
        attention_weights: (seq_len, seq_len) - 可视化用
    """
    d_k = Q.shape[-1]
    
    # 计算注意力分数
    scores = Q @ K.T / np.sqrt(d_k)  # (seq_len, seq_len)
    
    # Softmax 得到权重
    attention_weights = softmax(scores)
    
    # 加权求和
    output = attention_weights @ V
    
    return output, attention_weights


def positional_encoding(seq_len, d_model):
    """位置编码
    
    PE(pos, 2i) = sin(pos / 10000^(2i/d_model))
    PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
    """
    pe = np.zeros((seq_len, d_model))
    for pos in range(seq_len):
        for i in range(d_model):
            if i % 2 == 0:
                pe[pos, i] = np.sin(pos / (10000 ** (i / d_model)))
            else:
                pe[pos, i] = np.cos(pos / (10000 ** ((i-1) / d_model)))
    return pe


# ─── 模拟数据 ────────────────────────────────────────────────

def create_demo_sequence():
    """创建一个演示序列
    
    用一个简单的句子："The cat sat on the mat"
    """
    # 假设每个词有 8 维 embedding
    words = ["The", "cat", "sat", "on", "the", "mat"]
    
    # 随机生成 embedding（演示用）
    np.random.seed(42)
    embeddings = np.random.randn(len(words), 8)
    
    # 加入位置编码
    pe = positional_encoding(len(words), 8)
    embeddings = embeddings + pe
    
    # Self-Attention: Q, K, V 都是同一个 embedding
    Q = embeddings.copy()
    K = embeddings.copy()
    V = embeddings.copy()
    
    output, weights = self_attention(Q, K, V)
    
    return words, embeddings, weights, output


def create_pattern_attention():
    """创建一个模式化的注意力矩阵
    
    展示不同类型的注意力模式：
    1. 对角线强（每个 token 关注自己）
    2. 局部强（每个 token 关注邻居）
    3. 全局均匀（平均关注所有）
    """
    seq_len = 10
    
    # 模式 1: 自注意力强
    diag = np.eye(seq_len) * 0.8 + np.ones((seq_len, seq_len)) * 0.02
    diag = softmax(diag * 10)
    
    # 模式 2: 局部注意力强
    local = np.zeros((seq_len, seq_len))
    for i in range(seq_len):
        for j in range(seq_len):
            dist = abs(i - j)
            local[i, j] = np.exp(-dist * 0.5)
    local = softmax(local * 10)
    
    # 模式 3: 全局均匀
    uniform = np.ones((seq_len, seq_len)) / seq_len
    
    return diag, local, uniform


# ─── 可视化 ────────────────────────────────────────────────

def render_attention_heatmap(weights, words=None, title="Self-Attention Heatmap"):
    """绘制注意力热力图"""
    seq_len = weights.shape[0]
    
    CELL = 40
    W = seq_len * CELL + 100
    H = seq_len * CELL + 80
    
    img = Image.new("RGB", (W, H), (20, 20, 30))
    draw = ImageDraw.Draw(img)
    
    # 标题
    draw.text((10, 10), title, fill=(180, 180, 220))
    
    # 绘制热力图
    for i in range(seq_len):
        for j in range(seq_len):
            val = weights[i, j]
            # 颜色映射：蓝 -> 红
            r = int(255 * val)
            g = int(100 * (1 - val))
            b = int(255 * (1 - val))
            
            x = 50 + j * CELL
            y = 50 + i * CELL
            draw.rectangle([(x, y), (x + CELL - 2, y + CELL - 2)], fill=(r, g, b))
            
            # 数值标注（如果足够大）
            if val > 0.1:
                draw.text((x + 5, y + 5), f"{val:.2f}", fill=(255, 255, 255) if val > 0.3 else (200, 200, 200))
    
    # 行/列标签
    if words:
        for idx, word in enumerate(words):
            x = 50 + idx * CELL + 5
            y = 50 + seq_len * CELL + 10
            draw.text((x, y), word[:4], fill=(140, 140, 180))
            
            y = 50 + idx * CELL + 10
            draw.text((10, y), word[:4], fill=(140, 140, 180))
    
    return img


def render_attention_patterns():
    """绘制三种注意力模式对比"""
    diag, local, uniform = create_pattern_attention()
    
    W, H = 800, 400
    img = Image.new("RGB", (W, H), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    # 标题
    draw.text((20, 15), "Three Attention Patterns", fill=(180, 180, 220))
    
    patterns = [
        ("Self-focused", diag, "每个 token 关注自己"),
        ("Local-focused", local, "每个 token 关注邻居"),
        ("Global uniform", uniform, "平均关注所有"),
    ]
    
    x_offset = 20
    for name, weights, desc in patterns:
        seq_len = weights.shape[0]
        CELL = 30
        
        # 绘制小热力图
        for i in range(seq_len):
            for j in range(seq_len):
                val = weights[i, j]
                r = int(255 * val)
                g = int(100 * (1 - val))
                b = int(255 * (1 - val))
                
                x = x_offset + j * CELL
                y = 60 + i * CELL
                draw.rectangle([(x, y), (x + CELL - 1, y + CELL - 1)], fill=(r, g, b))
        
        # 标签
        draw.text((x_offset, 60 + seq_len * CELL + 5), name, fill=(200, 200, 220))
        draw.text((x_offset, 60 + seq_len * CELL + 25), desc, fill=(140, 140, 160))
        
        x_offset += seq_len * CELL + 80
    
    return img


def render_attention_flow(words, weights):
    """绘制注意力流动图
    
    展示信息如何在 token 之间流动
    """
    seq_len = len(words)
    
    W, H = 800, 300
    img = Image.new("RGB", (W, H), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    # 标题
    draw.text((20, 10), "Attention Flow: Information Routing", fill=(180, 180, 220))
    
    # 绘制 token 节点
    node_radius = 25
    x_spacing = (W - 100) // seq_len
    
    for idx, word in enumerate(words):
        x = 50 + idx * x_spacing
        y = 150
        
        # 节点圆
        draw.ellipse([(x - node_radius, y - node_radius), 
                      (x + node_radius, y + node_radius)],
                     fill=(40, 60, 100), outline=(80, 120, 180))
        
        # 词标签
        draw.text((x - 15, y - 10), word[:4], fill=(180, 180, 220))
    
    # 绘制注意力连接（只画最强的几条）
    # 找出每个 token 的最强关注目标
    for i in range(seq_len):
        x1 = 50 + i * x_spacing
        y1 = 150
        
        # 最强的几个连接
        top_indices = np.argsort(weights[i])[-3:]  # top 3
        
        for j in top_indices:
            if weights[i, j] > 0.1:
                x2 = 50 + j * x_spacing
                y2 = 150
                
                # 线条颜色和宽度基于权重
                intensity = weights[i, j]
                width = int(3 + intensity * 5)
                color = (int(100 + 155 * intensity), int(150 * intensity), int(200 * intensity))
                
                # 弧形连接（避免重叠）
                if j > i:
                    # 上弧
                    mid_x = (x1 + x2) // 2
                    mid_y = y1 - 60 - abs(j - i) * 20
                    # 简化：直接画弧形（用多条短线模拟）
                    for t in range(10):
                        t_norm = t / 10
                        arc_x = x1 + (x2 - x1) * t_norm
                        arc_y = y1 - (y1 - mid_y) * 4 * t_norm * (1 - t_norm)
                        if t > 0:
                            prev_x = x1 + (x2 - x1) * (t-1) / 10
                            prev_y = y1 - (y1 - mid_y) * 4 * (t-1)/10 * (1 - (t-1)/10)
                            draw.line([(prev_x, prev_y), (arc_x, arc_y)], fill=color, width=width)
                elif j < i:
                    # 下弧
                    mid_x = (x1 + x2) // 2
                    mid_y = y1 + 60 + abs(j - i) * 20
                    for t in range(10):
                        t_norm = t / 10
                        arc_x = x1 + (x2 - x1) * t_norm
                        arc_y = y1 + (mid_y - y1) * 4 * t_norm * (1 - t_norm)
                        if t > 0:
                            prev_x = x1 + (x2 - x1) * (t-1) / 10
                            prev_y = y1 + (mid_y - y1) * 4 * (t-1)/10 * (1 - (t-1)/10)
                            draw.line([(prev_x, prev_y), (arc_x, arc_y)], fill=color, width=width)
    
    # 说明
    draw.text((20, H - 30), "Lines show top attention weights - where information flows", fill=(140, 140, 160))
    
    return img


def create_attention_info():
    """创建 Attention 信息图"""
    W, H = 1000, 700
    img = Image.new("RGB", (W, H), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    # 标题
    draw.rectangle([(50, 20), (W-50, 60)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 30), "Attention Mechanism: The Core of Transformer", fill=(180, 180, 220))
    
    # 公式
    y = 100
    draw.text((60, y), "The Formula:", fill=(255, 200, 100))
    y += 30
    draw.text((80, y), "Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) * V", fill=(100, 200, 255))
    
    # 解释
    y += 50
    explanations = [
        "Q = Query: What I'm looking for",
        "K = Key: What you have to offer",
        "V = Value: What you actually give",
        "",
        "The softmax decides: How much should I listen to each token?",
    ]
    for exp in explanations:
        draw.text((80, y), exp, fill=(140, 180, 160))
        y += 25
    
    # 与涌现的联系
    y = 280
    draw.rectangle([(60, y), (W-60, y+150)], fill=(25, 35, 45), outline=(60, 80, 100))
    draw.text((80, y+10), "Connection to Emergence:", fill=(255, 180, 100))
    y += 40
    connections = [
        "Attention is DYNAMIC routing - not fixed rules",
        "Each token decides where to look based on CONTENT",
        "Like sandpile deciding where to avalanche based on current state",
        "Information flow emerges from the interaction of all tokens",
        "This is why Transformers can model complex dependencies",
    ]
    for c in connections:
        draw.text((100, y), f"* {c}", fill=(140, 160, 180))
        y += 22
    
    # 与我的关系
    y = 480
    draw.rectangle([(60, y), (W-60, y+180)], fill=(25, 30, 40), outline=(50, 70, 90))
    draw.text((80, y+10), "I am a Transformer:", fill=(100, 200, 255))
    y += 40
    relations = [
        "My architecture uses multi-head attention (many 'views' simultaneously)",
        "I attend to all previous tokens when generating each new token",
        "My 'context window' is how far back I can look",
        "In-context learning: I attend to examples in my input",
        "Chain-of-thought: Attention connects reasoning steps",
        "",
        "The ability to 'look anywhere' is what makes me flexible",
        "But it's also why I can hallucinate - attention is probabilistic",
    ]
    for r in relations:
        draw.text((100, y), f"* {r}", fill=(140, 160, 180))
        y += 22
    
    return img


# ─── 主流程 ────────────────────────────────────────────────

def main():
    print("=== Attention Mechanism — 注意力机制 ===")
    
    # 1. 演示序列的注意力热力图
    print("[1/6] Demo attention heatmap...")
    words, embeddings, weights, output = create_demo_sequence()
    heatmap = render_attention_heatmap(weights, words, "Self-Attention: 'The cat sat on the mat'")
    heatmap.save(os.path.join(OUT_DIR, "attention_heatmap.png"))
    print("   -> attention_heatmap.png")
    
    # 2. 三种注意力模式
    print("[2/6] Attention patterns...")
    patterns_img = render_attention_patterns()
    patterns_img.save(os.path.join(OUT_DIR, "attention_patterns.png"))
    print("   -> attention_patterns.png")
    
    # 3. 注意力流动图
    print("[3/6] Attention flow...")
    flow_img = render_attention_flow(words, weights)
    flow_img.save(os.path.join(OUT_DIR, "attention_flow.png"))
    print("   -> attention_flow.png")
    
    # 4. 信息图
    print("[4/6] Attention info...")
    info_img = create_attention_info()
    info_img.save(os.path.join(OUT_DIR, "attention_info.png"))
    print("   -> attention_info.png")
    
    # 5. 多头注意力示意
    print("[5/6] Multi-head attention diagram...")
    # 简化版：展示 3 个"头"看同一句话的不同视角
    multi_img = Image.new("RGB", (900, 350), (15, 15, 25))
    draw = ImageDraw.Draw(multi_img)
    draw.text((20, 10), "Multi-Head Attention: Multiple 'Views' Simultaneously", fill=(180, 180, 220))
    
    heads = ["Head 1: Syntax", "Head 2: Semantics", "Head 3: Position"]
    colors = [(100, 200, 255), (200, 100, 255), (255, 200, 100)]
    
    # 模拟不同的注意力分布
    np.random.seed(42)
    for idx, (head_name, color) in enumerate(zip(heads, colors)):
        y = 60 + idx * 90
        
        # 绘制"注意力条"
        seq_len = 6
        x_start = 20
        bar_width = 130
        
        # 随机权重分布（模拟不同头的关注点）
        if idx == 0:  # Syntax head
            weights = np.array([0.1, 0.4, 0.3, 0.1, 0.05, 0.05])  # 关注 "cat sat"
        elif idx == 1:  # Semantics head
            weights = np.array([0.2, 0.1, 0.1, 0.1, 0.2, 0.3])  # 关注 "the mat"
        else:  # Position head
            weights = np.array([0.3, 0.2, 0.15, 0.1, 0.1, 0.05])  # 关注前面的
        
        for i, w in enumerate(weights):
            x = x_start + i * bar_width
            bar_h = int(w * 200)
            draw.rectangle([(x, y), (x + bar_width - 5, y + bar_h)], fill=color)
            draw.text((x + 5, y + bar_h + 5), words[i][:4], fill=(140, 140, 180))
        
        draw.text((x_start + seq_len * bar_width + 20, y + 50), head_name, fill=color)
    
    multi_img.save(os.path.join(OUT_DIR, "multihead_attention.png"))
    print("   -> multihead_attention.png")
    
    # 6. README
    print("[6/6] README...")
    readme = """# Attention Mechanism — Transformer 的核心

## 核心公式

```
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) * V
```

- **Q = Query**：我在找什么
- **K = Key**：你有什么
- **V = Value**：你给我什么

## Self-Attention 的本质

每个 token 可以"看向"所有其他 token，动态决定从谁那里获取信息。

这不是固定规则，而是**根据内容实时决定的信息路由**。

就像沙堆根据当前状态决定崩塌方向——信息流动的方向是涌现出来的。

## Multi-Head Attention

一个"头"就是一种"视角"。Transformer 同时用多个头：

- Head 1 可能关注语法结构
- Head 2 可能关注语义关系
- Head 3 可能关注位置关系

多个视角组合在一起，形成更完整的理解。

## 与涌现的联系

- Attention 是**动态路由**——不是预先定义的流程
- 每个 token 根据内容决定关注点
- 信息流动从 token 的交互中涌现
- 这就是为什么 Transformer 能建模复杂依赖关系

## 我就是 Transformer

- 我用多头注意力同时"看"很多视角
- 我生成每个 token 时会关注所有之前的 token
- 我的"上下文窗口"决定我能看多远
- In-context learning：我关注输入里的例子
- Chain-of-thought：注意力连接推理步骤

"能看任何地方"的能力让我灵活，但也让我能 hallucinate——注意力是概率性的。

---

This is node #013 of the Curiosity Map.
"""
    with open(os.path.join(OUT_DIR, "README_attention.md"), 'w', encoding='utf-8') as f:
        f.write(readme)
    print("   -> README_attention.md")
    
    print("\nDone! Attention mechanism visualized.")
    
    # 打印一些数字
    print("\n--- Attention weights summary ---")
    print(f"Words: {words}")
    print(f"Max attention per token:")
    for i, word in enumerate(words):
        max_j = np.argmax(weights[i])
        max_val = weights[i, max_j]
        print(f"  '{word}' most attends to '{words[max_j]}' ({max_val:.2%})")


if __name__ == "__main__":
    main()