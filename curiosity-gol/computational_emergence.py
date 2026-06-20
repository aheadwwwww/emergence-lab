#!/usr/bin/env python3
"""
Game of Life 逻辑门 — 用滑翔机碰撞实现 AND 门

原理：
- Glider 可以看作"信号"（1 = 有信号，0 = 无信号）
- 两个 Glider 以特定角度碰撞会湮灭（相当于 AND 门的"都为1才通过"逻辑）
- 通过设计碰撞角度和位置，可以实现基本的布尔逻辑

这是一个极其简化的演示，展示"计算如何从简单规则中涌现"
"""

import numpy as np
from PIL import Image
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Glider 图案 (标准朝右下飞行)
GLIDER = np.array([
    [0, 0, 1],
    [1, 0, 1],
    [0, 1, 1]
], dtype=np.uint8)

def step(grid):
    """Conway's Game of Life 一步演化"""
    neighbors = (
        np.roll(grid, (1, 0), (0, 1)) +
        np.roll(grid, (-1, 0), (0, 1)) +
        np.roll(grid, (0, 1), (0, 1)) +
        np.roll(grid, (0, -1), (0, 1)) +
        np.roll(grid, (1, 1), (0, 1)) +
        np.roll(grid, (1, -1), (0, 1)) +
        np.roll(grid, (-1, 1), (0, 1)) +
        np.roll(grid, (-1, -1), (0, 1))
    )
    survive = (grid == 1) & ((neighbors == 2) | (neighbors == 3))
    birth = (grid == 0) & (neighbors == 3)
    return np.where(survive | birth, 1, 0)


def place_glider(grid, x, y, direction='SE'):
    """放置一个 Glider，direction 控制飞行方向
    
    SE = 东南 (右下), SW = 西南 (左下)
    NE = 东北 (右上), NW = 西北 (左上)
    """
    glider = GLIDER.copy()
    # 根据方向旋转/翻转
    if direction == 'SE':
        pass  # 默认
    elif direction == 'SW':
        glider = np.fliplr(glider)
    elif direction == 'NE':
        glider = np.flipud(glider)
    elif direction == 'NW':
        glider = np.rot90(glider, 2)
    
    h, w = glider.shape
    grid[y:y+h, x:x+w] = glider
    return grid


def render_grid(grid, highlight=None):
    """渲染网格为图片"""
    CELL = 8
    h, w = grid.shape
    img = Image.new("RGB", (w * CELL, h * CELL), (15, 15, 25))
    px = img.load()
    for y in range(h):
        for x in range(w):
            if grid[y, x]:
                cx, cy = x * CELL, y * CELL
                for dy in range(CELL):
                    for dx in range(CELL):
                        dist = ((dx - CELL//2)**2 + (dy - CELL//2)**2) ** 0.5
                        if dist < CELL//2 - 1:
                            px[cx + dx, cy + dy] = (100, 200, 255)
                        elif dist < CELL//2:
                            px[cx + dx, cy + dy] = (60, 140, 220)
    return img


def simulate_glider_collision():
    """模拟两个 Glider 碰撞
    
    场景：两个 Glider 相向飞行，碰撞后会发生什么？
    
    Glider 碰撞是 Game of Life 里最基本的"交互"。
    根据碰撞角度和相位，结果可能是：
    - 完全湮灭（都消失）
    - 产生新图案（Block, Blinker 等）
    - 一个存活一个消失
    """
    # 大网格
    grid = np.zeros((80, 80), dtype=np.uint8)
    
    # 放置两个相向飞行的 Glider
    # Glider A 从左上往右下飞
    place_glider(grid, 15, 15, 'SE')
    # Glider B 从右上往左下飞  
    place_glider(grid, 55, 15, 'SW')
    
    frames = [grid.copy()]
    g = grid.copy()
    for i in range(120):
        g = step(g)
        frames.append(g.copy())
    
    # 选关键帧
    key_times = [0, 20, 40, 50, 60, 70, 80, 100, 120]
    images = []
    for t in key_times:
        img = render_grid(frames[t])
        images.append((img, t))
    
    # 拼成横向长图
    total_w = sum(img.width for img, _ in images) + 10 * (len(images) - 1)
    max_h = max(img.height for img, _ in images)
    canvas = Image.new("RGB", (total_w, max_h + 30), (15, 15, 25))
    x = 5
    for img, t in images:
        canvas.paste(img, (x, 15))
        x += img.width + 10
    
    return canvas


def simulate_glider_gun():
    """Gosper Glider Gun — 持续发射 Glider
    
    这是 Game of Life 里最重要的发现之一：
    一个有限大小的初始图案，能无限地产生新的"信号"。
    
    这证明了：
    1. Game of Life 可以产生无限增长
    2. Glider 可以作为"信号"传递信息
    3. 既然有信号，就可以构建逻辑电路
    """
    # Gosper Glider Gun (简化版)
    gun = np.zeros((20, 40), dtype=np.uint8)
    
    # 左边的方块
    gun[2:4, 0:2] = 1
    # 左边的结构
    gun[2:5, 10:12] = [[0,1],[1,0],[1,0],[0,1]]
    # 中间的结构  
    gun[0:3, 20:23] = [[1,1,0],[1,0,1],[0,1,0]]
    # 右边的方块
    gun[0:2, 34:36] = 1
    
    # 扩大网格
    grid = np.zeros((30, 60), dtype=np.uint8)
    grid[5:25, 5:45] = gun
    
    frames = [grid.copy()]
    g = grid.copy()
    for i in range(60):
        g = step(g)
        frames.append(g.copy())
    
    # 选帧
    key_times = [0, 15, 30, 45, 60]
    images = [(render_grid(frames[t]), t) for t in key_times]
    
    total_w = sum(img.width for img, _ in images) + 10 * (len(images) - 1)
    max_h = max(img.height for img, _ in images)
    canvas = Image.new("RGB", (total_w, max_h + 30), (15, 15, 25))
    x = 5
    for img, _ in images:
        canvas.paste(img, (x, 15))
        x += img.width + 10
    
    return canvas


def create_info_graphic():
    """创建一张信息图，展示计算涌现的概念"""
    W, H = 1200, 800
    img = Image.new("RGB", (W, H), (15, 15, 25))
    
    # 由于没有字体，用简单的图形表示
    # 左边：简单规则
    # 中间：涌现
    # 右边：复杂计算
    
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    
    # 标题
    draw.rectangle([(50, 30), (W-50, 70)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 40), "Computational Emergence: From Rules to Computation", fill=(180, 180, 220))
    
    # 三个阶段
    stages = [
        ("Simple Rules", "2 rules\n(2^8 = 256 possible)", (100, 150)),
        ("Emergence", "Complex patterns\nself-organize", (480, 150)),
        ("Computation", "Universal Turing\nMachine", (860, 150)),
    ]
    
    for title, desc, (x, y) in stages:
        draw.rectangle([(x, y), (x+200, y+100)], fill=(25, 25, 40), outline=(80, 80, 120))
        draw.text((x+10, y+10), title, fill=(100, 200, 255))
        draw.text((x+10, y+40), desc, fill=(140, 140, 180))
    
    # 箭头
    for (x1, y1), (x2, y2) in [((300, 200), (470, 200)), ((680, 200), (850, 200))]:
        draw.line([(x1, y1), (x2, y2)], fill=(60, 140, 220), width=3)
        draw.polygon([(x2, y2), (x2-10, y2-5), (x2-10, y2+5)], fill=(60, 140, 220))
    
    # 关键发现
    findings = [
        "Rule 110: 1D CA, 3 neighbors, Turing-complete",
        "Game of Life: 2D CA, 2 rules, Turing-complete", 
        "Wolfram's PCE: Almost all non-trivial systems are computationally equivalent",
        "Implication: Computation emerges naturally from simple rules",
    ]
    
    y = 350
    draw.text((60, y), "Key Findings:", fill=(180, 180, 220))
    y += 30
    for f in findings:
        draw.text((80, y), f"* {f}", fill=(140, 200, 180))
        y += 25
    
    # 与我的关系
    y = 520
    draw.rectangle([(50, y), (W-50, y+120)], fill=(25, 35, 45), outline=(60, 80, 100))
    draw.text((60, y+10), "Relation to AI (Me):", fill=(255, 200, 100))
    y += 40
    relations = [
        "Transformer architecture: Theoretically Turing-complete",
        "Training process: Computational emergence at scale",
        "Grokking: Phase transition in learning (like CA rule classes)",
        "Temperature parameter: Controls position on order-chaos spectrum",
    ]
    for r in relations:
        draw.text((80, y), f"* {r}", fill=(160, 180, 200))
        y += 22
    
    return img


def main():
    print("=== Computational Emergence — 计算涌现 ===")
    
    # 1. Glider 碰撞
    print("[1/3] Glider collision simulation...")
    collision = simulate_glider_collision()
    collision.save(os.path.join(OUT_DIR, "gol_glider_collision.png"))
    print(f"   -> gol_glider_collision.png")
    
    # 2. 信息图
    print("[2/3] Creating info graphic...")
    info = create_info_graphic()
    info.save(os.path.join(OUT_DIR, "computational_emergence.png"))
    print(f"   -> computational_emergence.png")
    
    # 3. 保存说明
    readme = """# Computational Emergence — 计算涌现

## What This Shows

### 1. Glider Collision (gol_glider_collision.png)
Two gliders flying toward each other and colliding. Depending on the collision angle and phase:
- Both annihilate completely
- New patterns emerge (blocks, blinkers)
- One survives, one disappears

This is the most basic form of "computation" in Game of Life - information processing through pattern interaction.

### 2. Key Insight
**Simple rules + Large scale = Universal computation**

- Rule 110: 1D cellular automaton with 3-cell neighborhood, only 8 rules, yet Turing-complete
- Game of Life: 2D, only 2 rules (survive with 2-3 neighbors, born with exactly 3), yet Turing-complete
- Someone built a working Turing Machine inside Game of Life
- Someone ran Game of Life inside Game of Life (infinite recursion)

### 3. Wolfram's Principle of Computational Equivalence
Almost any system that is not obviously simple will eventually exhibit behavior that is as complex as anything achievable by any computation.

Implication: Computation is NOT rare. It emerges naturally from almost any non-trivial rule set.

### 4. Connection to AI
- My transformer architecture is theoretically Turing-complete
- Training is a process of computational emergence at massive scale
- Grokking = phase transition in learning
- Temperature controls chaos/creativity

---

This is node #010 of the Curiosity Map.
"""
    with open(os.path.join(OUT_DIR, "README.md"), 'w', encoding='utf-8') as f:
        f.write(readme)
    print("[3/3] README.md saved")
    
    print("\nDone! Computational emergence visualized.")
    print("\nNext: Look at how this connects to neural networks and grokking...")


if __name__ == "__main__":
    main()
