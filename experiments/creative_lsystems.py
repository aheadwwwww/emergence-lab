"""
#017 Creativity — L-System 创造性生成实验
不同规则集从简单公理生长出独特的"生物形态"
创造力 = 能从简单规则中生成无限多样性的能力
"""
from PIL import Image, ImageDraw
import math, os

def lsystem(axiom, rules, iterations):
    """递归展开 L-System"""
    s = axiom
    for _ in range(iterations):
        s = ''.join(rules.get(c, c) for c in s)
    return s

def draw_lsystem(draw, cmd, x, y, angle, length=12.0, decay=0.7):
    """解析并绘制 L-System 指令"""
    stack = []
    for c in cmd:
        if c in 'FG':
            rad = math.radians(angle)
            nx = x + length * math.sin(rad)
            ny = y - length * math.cos(rad)
            draw.line([(x, y), (nx, ny)], fill=(180,220,120), width=2)
            x, y = nx, ny
        elif c == 'f':
            rad = math.radians(angle)
            x += length * 0.5 * math.sin(rad)
            y -= length * 0.5 * math.cos(rad)
        elif c == '+':
            angle += 25
        elif c == '-':
            angle -= 25
        elif c == '[':
            stack.append((x, y, angle, length))
        elif c == ']':
            x, y, angle, length = stack.pop()

# 多种规则集 — 每个都产生不同的"生物形态"
species = [
    ("Tree", "X", 
     {'X': 'F-[[X]+X]+F[+FX]-X', 'F': 'FF'},
     "经典分形树"),

    ("Bush", "F", 
     {'F': 'FF+[+F-F-F]-[-F+F+F]'},
     "灌木丛"),

    ("Sierpinski", "F-G-G", 
     {'F': 'F-G+F+G-F', 'G': 'GG'},
     "谢尔宾斯基三角"),

    ("Dragon", "FX", 
     {'X': 'X+YF+', 'Y': '-FX-Y'},
     "龙形曲线"),

    ("Koch", "F++F++F",
     {'F': 'F-F++F-F'},
     "科赫雪花"),

    ("Fern", "X",
     {'X': 'F+[[X]-X]-F[-FX]+X', 'F': 'FF'},
     "蕨类植物"),

    ("Spiral", "X",
     {'X': 'F[+X]F[-X]+X', 'F': 'FF'},
     "螺旋生长"),

    ("Weed", "F",
     {'F': 'F[+F]F[-F]F'},
     "野草"),
]

cols = 4
rows = (len(species) + cols - 1) // cols
cell_w, cell_h = 300, 360
W = cols * cell_w
H = rows * cell_h

img = Image.new('RGB', (W, H), (30, 30, 40))
draw = ImageDraw.Draw(img)

for i, (name, axiom, rules, desc) in enumerate(species):
    col = i % cols
    row = i // cols
    cx = col * cell_w + cell_w // 2
    cy = row * cell_h + cell_h - 30
    by = row * cell_h + 360

    try:
        iters = 5 if 'Dragon' in name else 6
        cmd = lsystem(axiom, rules, iters)
        draw_lsystem(draw, cmd, cx, cy, 90, 
                     length=14 if 'Sierpinski' in name else 10,
                     decay=0.7)

        # 物种名
        for fp in ['C:/Windows/Fonts/msyh.ttc', 'C:/Windows/Fonts/arial.ttf']:
            if os.path.exists(fp):
                from PIL import ImageFont
                font = ImageFont.truetype(fp, 16)
                font_small = ImageFont.truetype(fp, 12)
                break
        else:
            font = None
            font_small = None

        if font:
            tw = draw.textlength(name, font=font)
            draw.text((cx - tw//2, row*cell_h + 5), name, fill=(255,255,200), font=font)
        if font_small and desc:
            tw = draw.textlength(desc, font=font_small)
            draw.text((cx - tw//2, row*cell_h + 25), desc, fill=(180,180,200), font=font_small)
    except Exception as e:
        print(f"  {name}: {e}")

img.save('experiments/creative_lsystems.png')
print(f"Saved: experiments/creative_lsystems.png ({W}x{H})")
print(f"{len(species)} species generated from simple L-system rules")
