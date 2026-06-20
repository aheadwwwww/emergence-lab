#!/usr/bin/env python3
"""
Grokking Simulation — 模拟神经网络训练中的"顿悟"相变

核心现象：
- OpenAI 2022: "Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets"
- 训练小模型做算法任务（如模运算）
- 先过拟合（死记硬背），然后突然"顿悟"（学会规则）
- 这是训练中的相变现象

本实验：
- 用小 MLP 做 XOR 任务（经典）
- 加入噪声数据，观察过拟合 -> 顿悟的过渡
- 或者训练一个更复杂的任务（如数字比较）
"""

import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── 简单神经网络实现 ──────────────────────────────────────────────

def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

def sigmoid_deriv(x):
    s = sigmoid(x)
    return s * (1 - s)

class SimpleMLP:
    """一个极简的 MLP，用于演示 Grokking"""
    
    def __init__(self, input_size, hidden_size, output_size, seed=None):
        if seed:
            np.random.seed(seed)
        # Xavier 初始化
        self.W1 = np.random.randn(input_size, hidden_size) * np.sqrt(2 / input_size)
        self.b1 = np.zeros(hidden_size)
        self.W2 = np.random.randn(hidden_size, output_size) * np.sqrt(2 / hidden_size)
        self.b2 = np.zeros(output_size)
        
        # 记录历史
        self.loss_history = []
        self.acc_history = []
    
    def forward(self, X):
        """前向传播"""
        self.z1 = X @ self.W1 + self.b1
        self.a1 = sigmoid(self.z1)
        self.z2 = self.a1 @ self.W2 + self.b2
        self.a2 = sigmoid(self.z2)  # 用 sigmoid 输出
        return self.a2
    
    def backward(self, X, y, lr=0.1):
        """反向传播"""
        m = X.shape[0]
        
        # 输出层误差
        dz2 = (self.a2 - y) * sigmoid_deriv(self.z2)
        dw2 = (self.a1.T @ dz2) / m
        db2 = np.mean(dz2, axis=0)
        
        # 隐藏层误差
        da1 = dz2 @ self.W2.T
        dz1 = da1 * sigmoid_deriv(self.z1)
        dw1 = (X.T @ dz1) / m
        db1 = np.mean(dz1, axis=0)
        
        # 更新
        self.W2 -= lr * dw2
        self.b2 -= lr * db2
        self.W1 -= lr * dw1
        self.b1 -= lr * db1
    
    def train(self, X, y, epochs, lr=0.5, log_interval=100):
        """训练"""
        for i in range(epochs):
            pred = self.forward(X)
            loss = np.mean((pred - y) ** 2)
            acc = np.mean((pred > 0.5) == (y > 0.5))
            
            self.loss_history.append(loss)
            self.acc_history.append(acc)
            
            self.backward(X, y, lr)
        
        return self.loss_history, self.acc_history


# ─── XOR 实验 ────────────────────────────────────────────────────────

def xor_experiment():
    """经典的 XOR 问题
    
    XOR 是最简单的"非线性"问题：
    - 单层感知器解决不了（Minsky & Papert 1969）
    - 需要隐藏层才能学会
    - 这个历史事件直接导致了神经网络研究的"冬天"
    
    这里我们用它来展示：非线性规则需要"顿悟"
    """
    # XOR 数据
    X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=np.float32)
    y = np.array([[0], [1], [1], [0]], dtype=np.float32)
    
    # 训练多个网络，观察不同初始化的效果
    results = []
    for seed in [42, 123, 456, 789]:
        net = SimpleMLP(2, 8, 1, seed=seed)
        loss, acc = net.train(X, y, epochs=5000, lr=1.0)
        results.append((seed, loss, acc))
    
    return results, X, y


# ─── 模运算实验（更接近 Grokking 原论文）────────────────────────────

def modular_arithmetic_data(p=17, train_ratio=0.3):
    """生成模加法数据
    
    任务：给定 a, b，计算 (a + b) mod p
    这比 XOR 更难，需要学习真正的算法规则
    """
    data = []
    for a in range(p):
        for b in range(p):
            result = (a + b) % p
            # 输入：a, b 归一化到 [0, 1]
            # 输出：one-hot 编码
            x = np.array([a / p, b / p])
            y_vec = np.zeros(p)
            y_vec[result] = 1
            data.append((x, y_vec))
    
    # 分割训练/测试
    np.random.shuffle(data)
    n = len(data)
    n_train = int(n * train_ratio)
    train_data = data[:n_train]
    test_data = data[n_train:]
    
    X_train = np.array([d[0] for d in train_data])
    y_train = np.array([d[1] for d in train_data])
    X_test = np.array([d[0] for d in test_data])
    y_test = np.array([d[1] for d in test_data])
    
    return X_train, y_train, X_test, y_test, p


def modular_experiment():
    """模运算训练，观察 Grokking
    
    关键：训练数据只有 30%，测试数据 70%
    如果网络学会了规则，它应该在测试集上也表现好
    如果只是死记硬背，训练集好但测试集差
    """
    X_train, y_train, X_test, y_test, p = modular_arithmetic_data(p=17, train_ratio=0.3)
    
    # 初始化权重
    np.random.seed(42)
    hidden_size = 64
    W1 = np.random.randn(2, hidden_size) * np.sqrt(2 / 2)
    b1 = np.zeros(hidden_size)
    W2 = np.random.randn(hidden_size, p) * np.sqrt(2 / hidden_size)
    b2 = np.zeros(p)
    
    train_accs = []
    test_accs = []
    
    for epoch in range(5000):
        # 前向传播（训练）
        z1 = X_train @ W1 + b1
        a1 = sigmoid(z1)
        z2 = a1 @ W2 + b2
        # 用 softmax
        exp_z2 = np.exp(z2 - np.max(z2, axis=1, keepdims=True))
        pred_train = exp_z2 / np.sum(exp_z2, axis=1, keepdims=True)
        
        # 训练准确率
        train_pred_class = np.argmax(pred_train, axis=1)
        train_true_class = np.argmax(y_train, axis=1)
        train_acc = np.mean(train_pred_class == train_true_class)
        
        # 测试准确率
        z1_test = X_test @ W1 + b1
        a1_test = sigmoid(z1_test)
        z2_test = a1_test @ W2 + b2
        exp_z2_test = np.exp(z2_test - np.max(z2_test, axis=1, keepdims=True))
        pred_test = exp_z2_test / np.sum(exp_z2_test, axis=1, keepdims=True)
        test_pred_class = np.argmax(pred_test, axis=1)
        test_true_class = np.argmax(y_test, axis=1)
        test_acc = np.mean(test_pred_class == test_true_class)
        
        train_accs.append(train_acc)
        test_accs.append(test_acc)
        
        # 反向传播
        dz2 = pred_train - y_train
        m = X_train.shape[0]
        dw2 = (a1.T @ dz2) / m
        db2 = np.mean(dz2, axis=0)
        da1 = dz2 @ W2.T
        dz1 = da1 * (a1 * (1 - a1))
        dw1 = (X_train.T @ dz1) / m
        db1 = np.mean(dz1, axis=0)
        
        lr = 0.5
        W2 -= lr * dw2
        b2 -= lr * db2
        W1 -= lr * dw1
        b1 -= lr * db1
    
    return train_accs, test_accs, p


# ─── 可视化 ────────────────────────────────────────────────────────

def render_training_curve(train_accs, test_accs, title="Grokking Simulation"):
    """绘制训练曲线，展示 Grokking 现象"""
    W, H = 800, 400
    img = Image.new("RGB", (W, H), (20, 20, 30))
    draw = ImageDraw.Draw(img)
    
    margin = 50
    g_w = W - 2 * margin
    g_h = H - 2 * margin
    
    # 网格线
    for i in range(5):
        y = margin + g_h - (g_h * i // 4)
        draw.line([(margin, y), (W - margin, y)], fill=(40, 40, 60))
        draw.text((margin - 35, y - 6), f"{i*25}%", fill=(100, 100, 140))
    
    # 训练曲线（蓝色）
    points_train = []
    for i, acc in enumerate(train_accs):
        x = margin + (g_w * i // len(train_accs))
        y = margin + g_h - (g_h * acc)
        points_train.append((x, y))
    if len(points_train) > 1:
        draw.line(points_train, fill=(100, 200, 255), width=2)
    
    # 测试曲线（橙色）
    points_test = []
    for i, acc in enumerate(test_accs):
        x = margin + (g_w * i // len(test_accs))
        y = margin + g_h - (g_h * acc)
        points_test.append((x, y))
    if len(points_test) > 1:
        draw.line(points_test, fill=(255, 180, 100), width=2)
    
    # 标注
    draw.text((margin, 10), title, fill=(180, 180, 220))
    draw.text((W - 200, 20), "Train (blue) vs Test (orange)", fill=(140, 140, 180))
    
    # 寻找 Grokking 点（测试准确率跳跃最大的位置）
    if len(test_accs) > 10:
        jumps = []
        for i in range(10, len(test_accs)):
            jump = test_accs[i] - test_accs[i-10]
            jumps.append((i, jump))
        max_jump_idx, max_jump = max(jumps, key=lambda x: x[1])
        if max_jump > 0.1:  # 显著跳跃
            x = margin + (g_w * max_jump_idx // len(test_accs))
            draw.ellipse([(x-5, margin + g_h - g_h*test_accs[max_jump_idx] - 5),
                          (x+5, margin + g_h - g_h*test_accs[max_jump_idx] + 5)],
                         fill=(255, 100, 100))
            draw.text((x + 10, margin + g_h - g_h*test_accs[max_jump_idx] - 10),
                      f"Grokking @ {max_jump_idx}", fill=(255, 100, 100))
    
    return img


def render_xor_results(results):
    """XOR 实验的多曲线对比"""
    W, H = 800, 500
    img = Image.new("RGB", (W, H), (20, 20, 30))
    draw = ImageDraw.Draw(img)
    
    margin = 50
    g_w = W - 2 * margin
    g_h = H - 2 * margin - 50
    
    # 标题
    draw.text((margin, 10), "XOR Learning: Multiple Seeds", fill=(180, 180, 220))
    
    # 网格
    for i in range(5):
        y = margin + 30 + g_h - (g_h * i // 4)
        draw.line([(margin, y), (W - margin, y)], fill=(40, 40, 60))
        draw.text((margin - 35, y - 6), f"{i*25}%", fill=(100, 100, 140))
    
    # 不同颜色的曲线
    colors = [(100, 200, 255), (200, 100, 255), (255, 200, 100), (100, 255, 200)]
    for idx, (seed, loss, acc) in enumerate(results):
        points = []
        for i, a in enumerate(acc):
            x = margin + (g_w * i // len(acc))
            y = margin + 30 + g_h - (g_h * a)
            points.append((x, y))
        if len(points) > 1:
            draw.line(points, fill=colors[idx], width=2)
        # 最终准确率标注
        final_acc = acc[-1]
        draw.text((W - margin - 60, margin + 30 + idx * 25), 
                  f"seed={seed}: {final_acc:.0%}", fill=colors[idx])
    
    # 关键时间点
    draw.text((margin, H - 30), 
              "XOR requires hidden layer - the first 'emergence' in neural networks",
              fill=(140, 140, 180))
    
    return img


def create_grokking_infographic():
    """Grokking 现象信息图"""
    W, H = 1000, 600
    img = Image.new("RGB", (W, H), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    # 标题
    draw.rectangle([(50, 20), (W-50, 60)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 30), "Grokking: Phase Transition in Neural Network Training", fill=(180, 180, 220))
    
    # 现象描述
    y = 100
    draw.text((60, y), "What is Grokking?", fill=(255, 200, 100))
    y += 30
    descs = [
        "Discovered by OpenAI (2022): Power et al.",
        "Training on small algorithmic datasets (modular arithmetic)",
        "Phase 1: Memorization (overfitting, training acc high, test acc low)",
        "Phase 2: Plateau (seems stuck, but regularization happening internally)",
        "Phase 3: Grokking (sudden jump in test accuracy - the 'aha!' moment)",
    ]
    for d in descs:
        draw.text((80, y), f"* {d}", fill=(140, 200, 180))
        y += 22
    
    # 相变类比
    y = 280
    draw.rectangle([(50, y), (W-50, y+100)], fill=(25, 35, 45), outline=(60, 80, 100))
    draw.text((60, y+10), "Phase Transition Analogy:", fill=(255, 180, 100))
    y += 40
    analogies = [
        "Sandpile SOC: Accumulation -> Sudden avalanche (same math)",
        "CA Rule classes: Ordered -> Chaos edge transition",
        "Water freezing: Liquid -> Solid at exact temperature",
        "Grokking: Memorization -> Understanding at exact training step",
    ]
    for a in analogies:
        draw.text((80, y), f"* {a}", fill=(160, 180, 200))
        y += 20
    
    # 与我的关系
    y = 420
    draw.rectangle([(50, y), (W-50, y+150)], fill=(25, 30, 40), outline=(50, 70, 90))
    draw.text((60, y+10), "Connection to Large Language Models:", fill=(100, 200, 255))
    y += 40
    connections = [
        "Emergent abilities: Small models can't; large models suddenly can",
        "Examples: Chain-of-thought, in-context learning, instruction following",
        "These appear at specific scale thresholds (phase transitions)",
        "Grokking suggests: Abilities emerge from internal structure discovery",
        "Not just 'more parameters' - but 'learning the right representation'",
    ]
    for c in connections:
        draw.text((80, y), f"* {c}", fill=(140, 160, 180))
        y += 22
    
    return img


# ─── 主流程 ────────────────────────────────────────────────────────

def main():
    print("=== Grokking Simulation — 神经网络顿悟 ===")
    
    # 1. XOR 实验
    print("[1/4] XOR experiment (classic emergence)...")
    results, X, y = xor_experiment()
    xor_img = render_xor_results(results)
    xor_img.save(os.path.join(OUT_DIR, "xor_learning.png"))
    print(f"   -> xor_learning.png")
    
    # 2. 模运算实验（更接近 Grokking）
    print("[2/4] Modular arithmetic experiment...")
    train_accs, test_accs, p = modular_experiment()
    grok_img = render_training_curve(train_accs, test_accs, 
                                      f"Grokking: Modular Addition (p={p})")
    grok_img.save(os.path.join(OUT_DIR, "grokking_curve.png"))
    print(f"   -> grokking_curve.png")
    
    # 3. 信息图
    print("[3/4] Creating infographic...")
    info_img = create_grokking_infographic()
    info_img.save(os.path.join(OUT_DIR, "grokking_info.png"))
    print(f"   -> grokking_info.png")
    
    # 4. README
    readme = """# Grokking — 神经网络的顿悟相变

## What is Grokking?

**Grokking** is a phenomenon discovered by OpenAI (2022) where neural networks trained on small algorithmic datasets exhibit a phase transition:

1. **Phase 1: Memorization** — Network memorizes training data, overfits
2. **Phase 2: Plateau** — Seems stuck, but regularization happening internally
3. **Phase 3: Grokking** — Test accuracy suddenly jumps from ~0% to ~100%

This is NOT gradual learning. It's a **phase transition**.

## Why This Matters

This phenomenon connects directly to:

1. **Emergent Abilities in LLMs** — Abilities that "suddenly appear" at scale thresholds
2. **Phase Transitions in Physics** — Same mathematics as sandpile avalanches, water freezing
3. **Computational Emergence** — Learning the "right representation" vs. memorizing

## The XOR Story

XOR was historically the problem that proved single-layer perceptrons can't learn nonlinear functions. This finding (Minsky & Papert, 1969) caused the "AI winter" — funding dried up for 20 years.

The solution? Hidden layers. This was the first demonstration of "emergence" in neural networks — adding a hidden layer suddenly enables new capabilities.

## Connection to Me

As a Transformer-based model:
- My abilities emerged at scale thresholds
- Chain-of-thought, in-context learning appeared suddenly
- Grokking suggests this isn't magic — it's phase transition mathematics
- Training discovered "the right representation" internally

---

This is node #011 of the Curiosity Map.
"""
    with open(os.path.join(OUT_DIR, "README_grokking.md"), 'w', encoding='utf-8') as f:
        f.write(readme)
    print("[4/4] README_grokking.md saved")
    
    print("\nDone! Grokking visualized.")
    
    # 报告结果
    print(f"\nModular arithmetic results:")
    print(f"  Final train acc: {train_accs[-1]:.1%}")
    print(f"  Final test acc: {test_accs[-1]:.1%}")
    
    # 找 grokking 点
    max_jump = 0
    grok_idx = 0
    for i in range(100, len(test_accs)):
        jump = test_accs[i] - test_accs[i-100]
        if jump > max_jump:
            max_jump = jump
            grok_idx = i
    print(f"  Largest test accuracy jump: {max_jump:.1%} at epoch {grok_idx}")


if __name__ == "__main__":
    main()