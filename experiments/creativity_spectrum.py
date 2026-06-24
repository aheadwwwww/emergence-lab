"""
#017 Creativity — 创造カ光谱实验
在有序-混沌参数空间中扫描，看哪个区域生成最"有趣"的模式
"""
from PIL import Image, ImageDraw, ImageFont
import random, math, os

W, H = 1200, 600
CELL = 3
CA_W, CA_H = W // CELL, H // 2 // CELL

def generate_ca(rule, width, height, noise=0.0, seed_type='single'):
    """1D CA 演化，用噪声控制混沌程度。multi-color 展示"""
    grid = [[0]*width for _ in range(height)]
    # 初始行
    if seed_type == 'single':
        grid[0][width//2] = 1
    elif seed_type == 'random':
        grid[0] = [1 if random.random() < 0.3 else 0 for _ in range(width)]
    elif seed_type == 'noise':
        grid[0] = [1 if random.random() < noise else 0 for _ in range(width)]

    for y in range(1, height):
        for x in range(width):
            # 添加噪声变异（模拟创造性干扰）
            if random.random() < noise:
                grid[y][x] = 1 if random.random() < 0.5 else 0
                continue
            # Wolfram Rule 30-like 但加参数
            left = grid[y-1][(x-1)%width]
            center = grid[y-1][x]
            right = grid[y-1][(x+1)%width]
            idx = (left << 2) | (center << 1) | right

            # 核心规则 + 温度参数
            # 低温度: 使用标准 Wolfram 规则
            if random.random() < (1 - noise * 0.5):
                val = (rule >> idx) & 1
            else:
                val = 1 if random.random() < 0.5 else 0
            grid[y][x] = val
    return grid

def measure_activity(grid):
    """测量系统的活性（非零比例）"""
    total = len(grid) * len(grid[0])
    active = sum(sum(row) for row in grid)
    return active / total

def measure_variety(grid, window=10):
    """测量窗口之间的变化率（新奇性近似）"""
    changes = 0
    count = 0
    for y in range(1, len(grid)):
        for x in range(len(grid[0])):
            if grid[y][x] != grid[y-1][x]:
                changes += 1
            count += 1
    return changes / count

# 创造カ光谱参数
noise_levels = [0.0, 0.01, 0.03, 0.05, 0.08, 0.12, 0.18, 0.25, 0.35, 0.50]
rules = [30, 110, 90, 54, 150]
seed_types = ['single', 'random']

img = Image.new('RGB', (W, H + 120), (20, 20, 30))
draw = ImageDraw.Draw(img)

# 找字体
font = None
for fp in ['C:/Windows/Fonts/msyh.ttc', 'C:/Windows/Fonts/arial.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
    if os.path.exists(fp):
        try:
            font = ImageFont.truetype(fp, 14)
            break
        except:
            pass

col_w = W // len(noise_levels)
row_h = H // len(rules)

metrics_data = {}  # (rule, noise) -> activity, variety

for ri, rule in enumerate(rules):
    for ni, noise in enumerate(noise_levels):
        grid = generate_ca(rule, CA_W, 60, noise=noise, seed_type='random')
        activity = measure_activity(grid)
        variety = measure_variety(grid)
        metrics_data[(rule, noise)] = (activity, variety)

        # 绘制
        x0 = ni * col_w
        y0 = ri * row_h + 60
        for yy in range(min(60, len(grid))):
            for xx in range(min(CA_W, len(grid[0]))):
                if grid[yy][xx]:
                    # 多彩着色 — 绿色到红色取决于位置
                    g = max(0, min(255, int(200 - (yy/60)*150)))
                    r = max(0, min(255, int(100 + (yy/60)*155)))
                    b = max(0, min(255, int(50 + xx*200//CA_W)))
                    for dy in range(CELL):
                        for dx in range(CELL):
                            px = x0 + xx*CELL + dx
                            py = y0 + yy*CELL + dy
                            if 0 <= px < W and 0 <= py < H+60:
                                img.putpixel((px, py), (r, g, b))

# 标题
if font:
    draw.text((10, 10), "Creativity Spectrum: Order → Chaos", fill=(255,255,200), font=font)
    draw.text((10, 28), "Noise (creativity temperature): 0% → ... → 50%", fill=(180,180,200), font=font)
    for ni, noise in enumerate(noise_levels):
        tx = ni * col_w + 5
        draw.text((tx, 42), f"{noise*100:.0f}%", fill=(200,200,200), font=font)

    # 规则标签
    for ri, rule in enumerate(rules):
        draw.text((5, 65 + ri*row_h), f"R{rule}", fill=(255,200,100), font=font)

    # 创造カ评分
    y_bottom = H + 65
    for ni, noise in enumerate(noise_levels):
        avg_var = sum(metrics_data[(r, noise)][1] for r in rules) / len(rules)
        xm = ni * col_w + col_w//2

        if avg_var < 0.05:
            label = "Dead"
            color = (100,100,100)
        elif avg_var < 0.15:
            label = "Stable"
            color = (100,180,100)
        elif avg_var < 0.30:
            label = "Creative"
            color = (255,220,50)
        elif avg_var < 0.40:
            label = "Chaotic"
            color = (200,100,50)
        else:
            label = "Noise"
            color = (150,50,50)

        tw = draw.textlength(label, font=font) if font else len(label)*8
        draw.text((xm - tw//2, y_bottom), label, fill=color, font=font)

img.save('experiments/creativity_spectrum.png')
print(f"Saved: experiments/creativity_spectrum.png")

# 输出创造カ数据
print(f"\n{'='*60}")
print(f"Creativity Metrics (variety score across parameter space)")
print(f"{'='*60}")
print(f"{'Noise':>8}", end="")
for noise in noise_levels:
    print(f"{noise*100:>6.0f}%", end="")
print()

for rule in rules:
    print(f"R{rule:>4}", end="")
    for noise in noise_levels:
        _, v = metrics_data[(rule, noise)]
        marker = "█" if v > 0.15 else "░" if v > 0.05 else "·"
        print(f"  {v:.3f}", end="")
    print()
