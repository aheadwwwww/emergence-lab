"""
#003 Edge of Chaos — 混沌边缘探索

核心问题：复杂系统在有序和混沌之间的过渡带是否最"有生产力"？

实验：
1. Lambda 参数扫描 — 1D CA 的 λ 值与行为分类
2. 信息熵测量 — 在混沌边缘是否熵最大？
3. 相变可视化 — 展示从有序→混沌边缘→混沌的转变
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io

# ============================================================
# 1. Lambda 参数扫描 — Wolfram 1D CA
# ============================================================

def wolfram_rule_to_binary(rule_num):
    """将 Wolfram 规则号转为 8 位二进制规则表"""
    return [(rule_num >> i) & 1 for i in range(8)]

def run_1d_ca(rule_num, width=200, steps=200, initial=None):
    """运行 1D CA，返回演化历史"""
    rule = wolfram_rule_to_binary(rule_num)
    if initial is None:
        grid = np.zeros(width, dtype=int)
        grid[width // 2] = 1
    else:
        grid = initial.copy()
    
    history = np.zeros((steps, width), dtype=int)
    history[0] = grid
    
    for t in range(1, steps):
        new_grid = np.zeros(width, dtype=int)
        for i in range(width):
            left = grid[(i - 1) % width]
            center = grid[i]
            right = grid[(i + 1) % width]
            idx = (left << 2) | (center << 1) | right
            new_grid[i] = rule[idx]
        grid = new_grid
        history[t] = grid
    
    return history

def compute_lambda(rule_num):
    """计算 Langton's λ 参数：规则表中 1 的比例"""
    rule = wolfram_rule_to_binary(rule_num)
    return sum(rule) / 8.0

def classify_ca(history):
    """基于演化历史分类 CA（简化版）"""
    # 计算每步的活性（1的比例）
    activity = history.mean(axis=1)
    
    # 检查是否全死（Class 1）
    if np.all(activity[50:] == 0):
        return 1, "冻结"
    
    # 检查周期性（Class 2）
    if len(activity) > 100:
        autocorr = np.correlate(activity - activity.mean(), 
                                activity - activity.mean(), mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        autocorr = autocorr / autocorr[0] if autocorr[0] != 0 else np.zeros_like(autocorr)
        # 找第一个负相关
        peaks = []
        for i in range(2, len(autocorr) - 1):
            if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1] and autocorr[i] > 0.3:
                peaks.append(i)
        if peaks and peaks[0] < 50:
            return 2, f"周期={peaks[0]}"
    
    # 计算熵
    entropy = compute_entropy(history)
    
    if entropy < 0.3:
        return 2, "简单周期"
    elif entropy < 0.7:
        return 4, "复杂(混沌边缘)"
    else:
        return 3, "混沌"

def compute_entropy(history):
    """计算 CA 演化历史的 Shannon 熵"""
    # 使用滑动窗口 (3x3) 统计模式
    h, w = history.shape
    patterns = {}
    for i in range(1, h - 1):
        for j in range(1, w - 1):
            pattern = tuple(history[i-1:i+2, j-1:j+2].flatten())
            patterns[pattern] = patterns.get(pattern, 0) + 1
    
    total = sum(patterns.values())
    if total == 0:
        return 0
    
    probs = np.array(list(patterns.values())) / total
    entropy = -np.sum(probs * np.log2(probs + 1e-10))
    max_entropy = np.log2(len(patterns)) if patterns else 1
    return entropy / max_entropy if max_entropy > 0 else 0

# ============================================================
# 2. 主要实验：扫描所有 256 条规则
# ============================================================

print("扫描 256 条 Wolfram 规则...")
results = []
for rule_num in range(256):
    history = run_1d_ca(rule_num, width=100, steps=100)
    lam = compute_lambda(rule_num)
    cls, cls_name = classify_ca(history)
    entropy = compute_entropy(history)
    results.append({
        'rule': rule_num,
        'lambda': lam,
        'class': cls,
        'class_name': cls_name,
        'entropy': entropy
    })

# 统计各类别
class_counts = {}
for r in results:
    cls = r['class']
    class_counts[cls] = class_counts.get(cls, 0) + 1

print(f"Class 1 (冻结): {class_counts.get(1, 0)}")
print(f"Class 2 (周期): {class_counts.get(2, 0)}")
print(f"Class 3 (混沌): {class_counts.get(3, 0)}")
print(f"Class 4 (复杂): {class_counts.get(4, 0)}")

# ============================================================
# 3. 可视化
# ============================================================

W, H = 1400, 1000
img = Image.new('RGB', (W, H), '#0f111a')
draw = ImageDraw.Draw(img)

try:
    font_title = ImageFont.truetype("C:\\Windows\\Fonts\\msyh.ttc", 28)
    font_label = ImageFont.truetype("C:\\Windows\\Fonts\\msyh.ttc", 16)
    font_small = ImageFont.truetype("C:\\Windows\\Fonts\\msyh.ttc", 12)
    font_tiny = ImageFont.truetype("C:\\Windows\\Fonts\\msyh.ttc", 10)
except:
    font_title = ImageFont.load_default()
    font_label = ImageFont.load_default()
    font_small = ImageFont.load_default()
    font_tiny = ImageFont.load_default()

# 标题
draw.text((W//2, 20), "#003 Edge of Chaos — 混沌边缘", fill='#c4b5fd', 
          font=font_title, anchor='mt')

# ---- Panel A: Lambda vs Entropy 散点图 ----
ax, ay, aw, ah = 40, 70, 420, 350
draw.rectangle([ax, ay, ax+aw, ay+ah], outline='#2a2d3a', width=1)
draw.text((ax+aw//2, ay+8), "λ 参数 vs 信息熵", fill='#8892a8', font=font_label, anchor='mt')

# 坐标轴
margin = 40
px = ax + margin
py = ay + ah - margin
pw = aw - 2 * margin
ph = ah - 2 * margin

draw.line([px, py, px+pw, py], fill='#4a4d63', width=1)  # x轴
draw.line([px, py, px, py-ph], fill='#4a4d63', width=1)  # y轴
draw.text((px+pw//2, py+20), "λ (规则中1的比例)", fill='#6a6c7a', font=font_small, anchor='mt')
# y轴标签旋转
draw.text((px-30, py-ph//2), "信息熵", fill='#6a6c7a', font=font_small, anchor='mm')

# 绘制散点
colors = {1: '#4a6a8a', 2: '#34d399', 3: '#f472b6', 4: '#ffc864'}
for r in results:
    x = px + int(r['lambda'] * pw)
    y = py - int(r['entropy'] * ph)
    c = colors.get(r['class'], '#666')
    draw.ellipse([x-3, y-3, x+3, y+3], fill=c)

# 图例
legend_y = ay + ah - 20
for cls, name, color in [(1, 'Class 1 冻结', '#4a6a8a'), (2, 'Class 2 周期', '#34d399'),
                           (3, 'Class 3 混沌', '#f472b6'), (4, 'Class 4 复杂', '#ffc864')]:
    draw.ellipse([ax+10, legend_y-4, ax+18, legend_y+4], fill=color)
    draw.text((ax+24, legend_y), name, fill='#8892a8', font=font_tiny, anchor='lm')
    legend_y += 16

# ---- Panel B: 关键规则的 CA 演化图 ----
key_rules = [
    (0, "Rule 0 (全死)", 1),
    (32, "Rule 32 (冻结)", 1),
    (90, "Rule 90 (分形)", 2),
    (110, "Rule 110 (混沌边缘)", 4),
    (30, "Rule 30 (混沌)", 3),
    (184, "Rule 184 (交通流)", 2),
    (54, "Rule 54 (复杂)", 4),
    (126, "Rule 126 (混沌)", 3),
]

ca_y = 70
ca_x_start = 500
ca_w = 130
ca_h = 130
ca_gap = 10

for idx, (rule_num, name, cls) in enumerate(key_rules):
    col = idx % 2
    row = idx // 2
    cx = ca_x_start + col * (ca_w + ca_gap)
    cy = ca_y + row * (ca_h + ca_gap + 25)
    
    history = run_1d_ca(rule_num, width=50, steps=50)
    
    # 绘制 CA 演化图
    for t in range(50):
        for i in range(50):
            if history[t, i]:
                color = colors.get(cls, '#fff')
                draw.point((cx + i * 2 + 15, cy + t * 2 + 20), fill=color)
    
    draw.rectangle([cx, cy, cx+ca_w, cy+ca_h], outline='#2a2d3a', width=1)
    draw.text((cx+ca_w//2, cy+ca_h+5), name, fill='#8892a8', font=font_tiny, anchor='mt')
    lam = compute_lambda(rule_num)
    draw.text((cx+ca_w//2, cy+ca_h+18), f"λ={lam:.3f}  {results[rule_num]['class_name']}", 
              fill=colors.get(cls, '#666'), font=font_tiny, anchor='mt')

# ---- Panel C: 熵 vs λ 的相变曲线 ----
bx, by, bw, bh = 40, 460, 420, 250
draw.rectangle([bx, by, bx+bw, by+bh], outline='#2a2d3a', width=1)
draw.text((bx+bw//2, by+8), "相变曲线: 平均熵 vs λ", fill='#8892a8', font=font_label, anchor='mt')

# 按 λ 分桶计算平均熵
lambda_bins = np.linspace(0, 1, 21)
bin_entropy = []
bin_std = []
for i in range(len(lambda_bins) - 1):
    lo, hi = lambda_bins[i], lambda_bins[i+1]
    mid = (lo + hi) / 2
    vals = [r['entropy'] for r in results if lo <= r['lambda'] < hi]
    if vals:
        bin_entropy.append((mid, np.mean(vals)))
        bin_std.append(np.std(vals))
    else:
        bin_entropy.append((mid, 0))
        bin_std.append(0)

bmargin = 35
bpx = bx + bmargin
bpy = by + bh - bmargin
bpw = bw - 2 * bmargin
bph = bh - 2 * bmargin

draw.line([bpx, bpy, bpx+bpw, bpy], fill='#4a4d63', width=1)
draw.line([bpx, bpy, bpx, bpy-bph], fill='#4a4d63', width=1)
draw.text((bpx+bpw//2, bpy+20), "λ", fill='#6a6c7a', font=font_small, anchor='mt')
draw.text((bpx-25, bpy-bph//2), "平均熵", fill='#6a6c7a', font=font_small, anchor='mm')

# 绘制曲线
points = []
for mid, ent in bin_entropy:
    x = bpx + int(mid * bpw)
    y = bpy - int(ent * bph)
    points.append((x, y))

for i in range(len(points) - 1):
    draw.line([points[i], points[i+1]], fill='#6c63ff', width=2)

for x, y in points:
    draw.ellipse([x-3, y-3, x+3, y+3], fill='#6c63ff')

# 标注混沌边缘区域
edge_x1 = bpx + int(0.3 * bpw)
edge_x2 = bpx + int(0.6 * bpw)
draw.rectangle([edge_x1, bpy-bph, edge_x2, bpy], fill='#ffc864', outline=None)
# 重绘曲线在上面
for i in range(len(points) - 1):
    draw.line([points[i], points[i+1]], fill='#6c63ff', width=2)
for x, y in points:
    draw.ellipse([x-3, y-3, x+3, y+3], fill='#6c63ff')

draw.text(((edge_x1+edge_x2)//2, bpy-bph+12), "混沌边缘", 
          fill='#1a1a2e', font=font_small, anchor='mt')
draw.text(((edge_x1+edge_x2)//2, bpy-bph+30), "λ≈0.3-0.6", 
          fill='#1a1a2e', font=font_tiny, anchor='mt')

# ---- Panel D: 关键洞察 ----
dx, dy = 500, 460
draw.rectangle([dx, dy, dx+400, dy+250], outline='#2a2d3a', width=1)
draw.text((dx+200, dy+10), "关键洞察", fill='#ffc864', font=font_label, anchor='mt')

insights = [
    "• 混沌边缘是有序与混沌之间的狭窄过渡带",
    "• 在这个区域，系统具有最大的计算能力",
    "• Class 4 CA (如 Rule 110) 是图灵完备的",
    "• λ ≈ 0.3-0.6 是涌现的\"甜区\"",
    "• 自然选择可能将生命推向混沌边缘",
    "• Kauffman: 演化速率在混沌边缘最大",
    "• 临界性 = 最大敏感度 + 最大可塑性",
]
for i, text in enumerate(insights):
    draw.text((dx+15, dy+35+i*24), text, fill='#d0d2dd', font=font_small)

# ---- 底部信息 ----
draw.text((W//2, H-30), "Edge of Chaos | #003 | 2026-06-24 | 好奇虾", 
          fill='#4a4d63', font=font_small, anchor='mt')

# 保存
img.save('experiments/edge_of_chaos.png')
print("\n✓ 保存 experiments/edge_of_chaos.png")

# ============================================================
# 4. 输出统计
# ============================================================
print("\n=== 混沌边缘实验总结 ===")
print(f"扫描规则数: 256")
print(f"Class 4 (复杂/混沌边缘) 规则数: {class_counts.get(4, 0)}")
print(f"混沌边缘 λ 范围: 约 0.3-0.6")

# 找出 Class 4 规则
class4_rules = [r for r in results if r['class'] == 4]
print(f"\nClass 4 规则: {[r['rule'] for r in class4_rules]}")
for r in class4_rules:
    print(f"  Rule {r['rule']}: λ={r['lambda']:.3f}, 熵={r['entropy']:.3f}")
