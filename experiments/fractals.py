"""
好奇心地图 - 分形实验
Fractals: Mandelbrot, Julia, Sierpinski, Koch

分形 = 自相似 + 递归 + 简单规则生成无限复杂
Mandelbrot 集的边界是 "混沌边缘" 的完美可视化
"""

import numpy as np
from PIL import Image
import os

SAVE_DIR = "D:/emergence_experiments"
os.makedirs(SAVE_DIR, exist_ok=True)

# ─── 1. Mandelbrot Set ───────────────────────────────────────
def mandelbrot(h=800, w=1000, max_iter=256, center=(-0.5, 0), zoom=1.0):
    """Mandelbrot set - the fractal that emerged from simple iteration z = z^2 + c"""
    xmin, xmax = center[0] - 2.0/zoom, center[0] + 2.0/zoom
    ymin, ymax = center[1] - 1.5/zoom, center[1] + 1.5/zoom
    x = np.linspace(xmin, xmax, w).astype(np.float32)
    y = np.linspace(ymin, ymax, h).astype(np.float32)
    C = x[np.newaxis, :] + 1j * y[:, np.newaxis]
    Z = np.zeros_like(C, dtype=np.complex64)
    diverge = np.zeros((h, w), dtype=np.int32)
    
    for n in range(max_iter):
        mask = np.abs(Z) <= 4
        Z[mask] = Z[mask]**2 + C[mask]
        diverge[mask & (np.abs(Z) > 4)] = n + 1
    diverge[diverge == 0] = max_iter
    
    # Smooth coloring
    img = np.log(diverge + 1) / np.log(max_iter)
    img = np.clip(img * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(img, 'L')

# ─── 2. Julia Set ─────────────────────────────────────────────
def julia(h=800, w=1000, max_iter=256, c=complex(-0.7, 0.27)):
    """Julia set: same iteration z = z^2 + c, fix c, vary z₀
    The coastline of Mandelbrot is full of unique Julia sets"""
    x = np.linspace(-1.5, 1.5, w).astype(np.float32)
    y = np.linspace(-1.5, 1.5, h).astype(np.float32)
    Z = x[np.newaxis, :] + 1j * y[:, np.newaxis]
    diverge = np.zeros((h, w), dtype=np.int32)
    
    for n in range(max_iter):
        mask = np.abs(Z) <= 4
        Z[mask] = Z[mask]**2 + c
        diverge[mask & (np.abs(Z) > 4)] = n + 1
    diverge[diverge == 0] = max_iter
    
    smoothed = np.log(diverge + 1)
    smoothed = smoothed / smoothed.max() * 255
    return Image.fromarray(smoothed.astype(np.uint8) if smoothed.max() > 0 else smoothed.astype(np.uint8), 'L')

# ─── 3. Sierpinski Triangle (iterated function system) ───────
def sierpinski_ifs(n_points=100000):
    """Sierpinski triangle via Chaos Game"""
    vertices = np.array([[0, 0], [1, 0], [0.5, np.sqrt(3)/2]], dtype=np.float32)
    points = np.zeros((n_points, 2), dtype=np.float32)
    p = np.array([0.5, 0.5], dtype=np.float32)
    
    for i in range(n_points):
        v = vertices[np.random.randint(0, 3)]
        p = (p + v) / 2
        points[i] = p
    
    # Render
    img_size = 800
    scale = img_size * 0.95
    offset = 20
    pixels = np.zeros((img_size, img_size), dtype=np.uint8)
    xs = (points[:, 0] * scale + offset).astype(int)
    ys = (img_size - 1 - (points[:, 1] * scale + offset)).astype(int)
    mask = (xs >= 0) & (xs < img_size) & (ys >= 0) & (ys < img_size)
    pixels[ys[mask], xs[mask]] = 255
    return Image.fromarray(pixels, 'L')

# ─── 4. Koch Snowflake ───────────────────────────────────────
def koch_snowflake(iterations=4):
    """Koch snowflake via L-system: F → F+F--F+F"""
    axiom = "F++F++F"
    rules = {"F": "F+F--F+F"}
    angle = 60
    
    # Expand
    for _ in range(iterations):
        axiom = "".join(rules.get(c, c) for c in axiom)
    
    # Turtle graphics
    import math
    x, y = 100, 500
    direction = 0
    points = [(x, y)]
    
    for cmd in axiom:
        if cmd == 'F':
            x += math.cos(math.radians(direction)) * 5
            y += math.sin(math.radians(direction)) * 5
            points.append((int(x), int(y)))
        elif cmd == '+':
            direction += angle
        elif cmd == '-':
            direction -= angle
    
    # Render
    img = Image.new('L', (700, 600), 0)
    px = img.load()
    for i in range(len(points) - 1):
        # Simple line drawing
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        steps = max(abs(x2-x1), abs(y2-y1))
        for t in range(steps + 1):
            sx = int(x1 + (x2-x1) * t / steps)
            sy = int(y1 + (y2-y1) * t / steps)
            if 0 <= sx < 700 and 0 <= sy < 600:
                px[sx, sy] = 255
    return img

# ─── 5. Barnsley Fern ────────────────────────────────────────
def barnsley_fern(n_points=50000):
    """Barnsley fern: IFS with 4 affine transformations"""
    affines = [
        (0.0, 0.0, 0.0, 0.16, 0.0, 0.0, 0.01),  # Stem
        (0.85, 0.04, -0.04, 0.85, 0.0, 1.6, 0.85),  # Leaflets
        (0.2, -0.26, 0.23, 0.22, 0.0, 1.6, 0.07),  # Left leaf
        (-0.15, 0.28, 0.26, 0.24, 0.0, 0.44, 0.07),  # Right leaf
    ]
    
    x, y = 0.0, 0.0
    points = np.zeros((n_points, 2), dtype=np.float32)
    
    for i in range(n_points):
        r = np.random.random()
        cum = 0
        for a, b, c, d, e, f, prob in affines:
            cum += prob
            if r <= cum:
                x_new = a * x + b * y + e
                y_new = c * x + d * y + f
                x, y = x_new, y_new
                break
        points[i] = [x, y]
    
    # Scale and render
    img_size = 600
    offset_x, offset_y = 200, 100
    scale = 80
    pixels = np.zeros((img_size, img_size), dtype=np.uint8)
    xs = (points[:, 0] * scale + offset_x).astype(int)
    ys = (img_size - 1 - (points[:, 1] * scale)).astype(int)
    mask = (xs >= 0) & (xs < img_size) & (ys >= 0) & (ys < img_size)
    pixels[ys[mask], xs[mask]] = 255
    return Image.fromarray(pixels, 'L')

# ─── Run ──────────────────────────────────────────────────────
def apply_colormap(gray_img, palette='fire'):
    """Apply a colormap to grayscale image"""
    gray = np.array(gray_img)
    if palette == 'fire':
        r = np.clip(gray * 3, 0, 255).astype(np.uint8)
        g = np.clip(gray * 1.5 - 128, 0, 255).astype(np.uint8)
        b = np.clip(gray * 0.5 - 64, 0, 255).astype(np.uint8)
    elif palette == 'ocean':
        r = np.clip(gray * 0.3, 0, 255).astype(np.uint8)
        g = np.clip(gray * 0.5 + 50, 0, 255).astype(np.uint8)
        b = np.clip(gray * 1.5, 0, 255).astype(np.uint8)
    elif palette == 'plasma':
        r = np.clip(gray * 1.2 + 30, 0, 255).astype(np.uint8)
        g = np.clip(np.abs(gray - 128) * 2, 0, 255).astype(np.uint8)
        b = np.clip(255 - gray * 1.5, 0, 255).astype(np.uint8)
    else:
        return gray_img
    return Image.fromarray(np.stack([r, g, b], axis=-1), 'RGB')

print("=== 分形实验 ===")
print("1. Mandelbrot Set...")
img = mandelbrot(h=800, w=1000, max_iter=256)
colored = apply_colormap(img, 'fire')
colored.save(f"{SAVE_DIR}/mandelbrot.png")
print(f"  -> {SAVE_DIR}/mandelbrot.png")

print("2. Julia Sets (3 variations)...")
variants = [complex(-0.7, 0.27), complex(-0.8, 0.156), complex(0.285, 0.01)]
names = ["julia_dendritic", "julia_siegel", "julia_rabbit"]
for c, name in zip(variants, names):
    img = julia(h=800, w=1000, max_iter=256, c=c)
    colored = apply_colormap(img, 'plasma')
    colored.save(f"{SAVE_DIR}/{name}.png")
    print(f"  -> {SAVE_DIR}/{name}.png")

print("3. Sierpinski Triangle...")
img = sierpinski_ifs(100000)
img.save(f"{SAVE_DIR}/sierpinski.png")
print(f"  -> {SAVE_DIR}/sierpinski.png")

print("4. Koch Snowflake...")
img = koch_snowflake(4)
img.save(f"{SAVE_DIR}/koch_snowflake.png")
print(f"  -> {SAVE_DIR}/koch_snowflake.png")

print("5. Barnsley Fern...")
img = barnsley_fern(100000)
img = apply_colormap(img, 'ocean')
img.save(f"{SAVE_DIR}/barnsley_fern.png")
print(f"  -> {SAVE_DIR}/barnsley_fern.png")

print("\n=== 完成! 共生成 6 张分形图 ===")
print("\n分形与涌现的关联:")
print("- Mandelbrot: z = z² + c, 简单迭代 → 无限复杂边界")
print("- Julia集: Mandelbrot边界上的每一点对应一个独特Julia集")
print("- IFS: 有限仿射变换 → 自然形态（蕨、树、雪花）")
print("- 分形维度: 自相似结构的经济编码")
print("- 混沌边缘: Mandelbrot集的边界就是Edge of Chaos")
