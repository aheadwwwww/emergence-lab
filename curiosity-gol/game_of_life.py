#!/usr/bin/env python3
"""Conway's Game of Life — 二维涌现的教科书"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── 核心逻辑 ────────────────────────────────────────────────

def step(grid):
    """一步演化"""
    neighbors = (
        np.roll(grid, (1, 0), (0, 1)) +  # up
        np.roll(grid, (-1, 0), (0, 1)) + # down
        np.roll(grid, (0, 1), (0, 1)) +  # right
        np.roll(grid, (0, -1), (0, 1)) + # left
        np.roll(grid, (1, 1), (0, 1)) +  # up-right
        np.roll(grid, (1, -1), (0, 1)) + # up-left
        np.roll(grid, (-1, 1), (0, 1)) + # down-right
        np.roll(grid, (-1, -1), (0, 1))  # down-left
    )
    survive = (grid == 1) & ((neighbors == 2) | (neighbors == 3))
    birth = (grid == 0) & (neighbors == 3)
    return np.where(survive | birth, 1, 0)


# ─── 经典图案 ────────────────────────────────────────────────

PATTERNS = {
    # 静物 (Still lifes)
    "Block": np.array([[1, 1], [1, 1]]),
    "Beehive": np.array([[0, 1, 1, 0], [1, 0, 0, 1], [0, 1, 1, 0]]),
    "Loaf": np.array([[0, 1, 1, 0], [1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 0]]),
    "Boat": np.array([[1, 1, 0], [1, 0, 1], [0, 1, 0]]),
    # 振荡器 (Oscillators)
    "Blinker": np.array([[0, 0, 0], [1, 1, 1], [0, 0, 0]]),
    "Toad": np.array([[0, 1, 1, 1], [1, 1, 1, 0]]),
    "Beacon": np.array([[1, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 1]]),
    # 飞船 (Spaceships)
    "Glider": np.array([[0, 0, 1], [1, 0, 1], [0, 1, 1]]),
    "LWSS": np.array([
        [0, 1, 1, 1, 1],
        [1, 0, 0, 0, 1],
        [0, 0, 0, 0, 1],
        [1, 0, 0, 1, 0],
    ]),
    # Methuselah
    "R-pentomino": np.array([[0, 1, 1], [1, 1, 0], [0, 1, 0]]),
}


# ─── 可视化 ──────────────────────────────────────────────────

CELL_SIZE = 12

def render_grid(grid, title=""):
    """numpy array -> PIL Image"""
    h, w = grid.shape
    img = Image.new("RGB", (w * CELL_SIZE, h * CELL_SIZE), (20, 20, 30))
    px = img.load()
    for y in range(h):
        for x in range(w):
            if grid[y, x]:
                cx, cy = x * CELL_SIZE, y * CELL_SIZE
                for dy in range(CELL_SIZE):
                    for dx in range(CELL_SIZE):
                        dist = ((dx - CELL_SIZE//2)**2 + (dy - CELL_SIZE//2)**2) ** 0.5
                        if dist < CELL_SIZE//2 - 1:
                            px[cx + dx, cy + dy] = (100, 200, 255)
                        elif dist < CELL_SIZE//2:
                            px[cx + dx, cy + dy] = (60, 140, 220)
    return img


def place_pattern(grid, pattern, x, y):
    h, w = pattern.shape
    grid[y:y+h, x:x+w] = pattern
    return grid


def run_simulation(grid, steps):
    """运行并返回每一步的原始网格 (list of numpy arrays)"""
    frames = []
    g = grid.copy()
    frames.append(g.copy())
    for _ in range(steps):
        g = step(g)
        frames.append(g.copy())
    return frames


def render_frames_side_by_side(frames, labels, title_prefix=""):
    """多个帧横向并排"""
    images = [render_grid(f, f"{title_prefix}{l}") for f, l in zip(frames, labels)]
    total_w = sum(img.width for img in images) + 10 * (len(images) - 1)
    max_h = max(img.height for img in images)
    canvas = Image.new("RGB", (total_w, max_h + 40), (15, 15, 25))
    x = 5
    for img in images:
        canvas.paste(img, (x, 20))
        x += img.width + 10
    return canvas


def render_patterns_grid(patterns_dict, steps=50, max_cols=4):
    """展示多个图案在中间帧和最终帧的对比"""
    rows = []
    row = []
    col = 0
    for name, pat in patterns_dict.items():
        pad = 3
        h, w = pat.shape
        grid = np.zeros((h + pad*2, w + pad*2), dtype=np.uint8)
        place_pattern(grid, pat, pad, pad)
        frames = run_simulation(grid, steps)
        mid = render_grid(frames[steps//2], f"{name} t={steps//2}")
        last = render_grid(frames[-1], f"{name} t={steps}")
        combined = Image.new("RGB", (mid.width + last.width + 20, max(mid.height, last.height)), (20, 20, 30))
        combined.paste(mid, (0, 0))
        combined.paste(last, (mid.width + 20, 0))
        row.append(combined)
        col += 1
        if col >= max_cols:
            rows.append(row)
            row = []
            col = 0
    if row:
        rows.append(row)
    col_w = max(r.width for row in rows for r in row) + 30
    row_h = 30 + max(r.height for row in rows for r in row)
    total_h = sum(row_h for _ in rows)
    canvas = Image.new("RGB", (col_w * max_cols, total_h), (15, 15, 25))
    y_off = 5
    for row in rows:
        x_off = 5
        max_h = 0
        for img in row:
            canvas.paste(img, (x_off, y_off))
            x_off += img.width + 20
            max_h = max(max_h, img.height)
        y_off += max_h + 30
    return canvas


# ─── 大规模随机演化 ──────────────────────────────────────────

def random_grid(h, w, p=0.3):
    return np.random.choice([0, 1], size=(h, w), p=[1-p, p])


def run_random_evolution(size=80, steps=200, sample_interval=10):
    """大网格随机初始"""
    g = random_grid(size, size, p=0.4)
    raw_frames = [g.copy()]
    for i in range(1, steps + 1):
        g = step(g)
        if i % sample_interval == 0 or i == steps:
            raw_frames.append(g.copy())
    labels = [f"t={0}"] + [f"t={i}" for i in range(sample_interval, steps + 1, sample_interval)]
    if steps not in range(sample_interval, steps + 1, sample_interval):
        labels.append(f"t={steps}")
    canvas = render_frames_side_by_side(raw_frames, labels, "Random ")
    return canvas, g


# ─── 人口统计 ──────────────────────────────────────────────

def population_plot(initial_grid, steps=300):
    """人口变化曲线"""
    g = initial_grid.copy()
    pops = [int(g.sum())]
    for _ in range(steps):
        g = step(g)
        pops.append(int(g.sum()))

    W, H = 800, 400
    img = Image.new("RGB", (W, H), (20, 20, 30))
    draw = ImageDraw.Draw(img)

    max_pop = max(pops) if pops else 1
    margin = 40
    g_w = W - 2 * margin
    g_h = H - 2 * margin

    for i in range(5):
        y = margin + g_h - (g_h * i // 4)
        draw.line([(margin, y), (W - margin, y)], fill=(40, 40, 60))
        draw.text((5, y - 6), str(max_pop * i // 4), fill=(100, 100, 140))

    points = []
    for i, p in enumerate(pops):
        x = margin + (g_w * i // len(pops))
        y = margin + g_h - (g_h * p // max_pop)
        points.append((x, y))

    if len(points) > 1:
        draw.line(points, fill=(100, 200, 255), width=2)

    draw.text((margin, 5), f"Population over {steps} steps", fill=(180, 180, 220))
    draw.text((margin, H - 18), f"Initial: {pops[0]}  Final: {pops[-1]}  Max: {max_pop}", fill=(120, 120, 160))

    return img


# ─── Gosper Glider Gun ────────────────────────────────────────

GOSPER_GLIDER_GUN = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
]
GOSPER_GLIDER_GUN = np.array(GOSPER_GLIDER_GUN)


def render_glider_gun_evolution():
    """Gosper Glider Gun 演化多帧"""
    h, w = GOSPER_GLIDER_GUN.shape
    g = np.zeros((h + 50, w + 150), dtype=np.uint8)
    g[:h, 5:5+w] = GOSPER_GLIDER_GUN

    key_times = [0, 10, 30, 50, 70, 100, 120, 150, 180, 200, 220, 250, 280, 300]
    raw_frames = []
    for i in range(301):
        if i in key_times:
            raw_frames.append(g.copy())
        g = step(g)

    labels = [f"t={t}" for t in key_times]
    canvas = render_frames_side_by_side(raw_frames, labels, "Gosper Gun ")
    return canvas


# ─── R-pentomino Methuselah ──────────────────────────────────

def render_rpentomino():
    """R-pentomino: 1103步后稳定"""
    rpent = np.zeros((30, 30), dtype=np.uint8)
    rpent[11:14, 10:13] = PATTERNS["R-pentomino"]
    g = rpent.copy()
    snapshots = [0, 10, 50, 100, 200, 500, 1000, 1103]
    raw_frames = []
    for i in range(1104):
        if i in snapshots:
            raw_frames.append(g.copy())
        g = step(g)
    labels = [f"t={t}" for t in snapshots]
    return render_frames_side_by_side(raw_frames, labels, "R-pentomino ")


# ─── 主流程 ──────────────────────────────────────────────────

def main():
    print("=== Conway's Game of Life — 好奇心地图 #009 ===")

    # 1. 经典图案展示
    print("[1/5] 经典图案演化...")
    img = render_patterns_grid(PATTERNS, steps=30, max_cols=4)
    img.save(os.path.join(OUT_DIR, "gol_patterns.png"))
    print(f"   -> gol_patterns.png ({img.size})")

    # 2. 随机大规模演化
    print("[2/5] 随机大网格 (80x80, 40%%密度, 200步)...")
    canvas, final = run_random_evolution(80, 200, 20)
    canvas.save(os.path.join(OUT_DIR, "gol_random_evolution.png"))
    print(f"   -> gol_random_evolution.png ({canvas.size})")
    print(f"   最终存活: {final.sum()}")

    # 3. 人口统计
    print("[3/5] 人口变化曲线 (80x80初始, 300步)...")
    init = random_grid(80, 80, 0.4)
    pop_img = population_plot(init, 300)
    pop_img.save(os.path.join(OUT_DIR, "gol_population.png"))
    print(f"   -> gol_population.png ({pop_img.size})")

    # 4. R-pentomino Methuselah
    print("[4/5] R-pentomino Methuselah (1103步稳定)...")
    rpent_img = render_rpentomino()
    rpent_img.save(os.path.join(OUT_DIR, "gol_rpentomino.png"))
    print(f"   -> gol_rpentomino.png ({rpent_img.size})")

    # 5. Gosper Glider Gun
    print("[5/5] Gosper Glider Gun (第一个无限增长结构, 300步)...")
    gg_img = render_glider_gun_evolution()
    gg_img.save(os.path.join(OUT_DIR, "gol_glider_gun.png"))
    print(f"   -> gol_glider_gun.png ({gg_img.size})")

    print("\n全部完成！")


if __name__ == "__main__":
    main()
