"""
生成涌现实验的汇总图：把6个实验结果拼成一张图
"""

from PIL import Image
import os

output_dir = r'C:\Users\许耀仁\.openclaw\workspace\experiments'

# Load all images
imgs = {
    'Langton Ant': Image.open(os.path.join(output_dir, 'langtons_ant.png')),
    'Boids+Predator': Image.open(os.path.join(output_dir, 'boids_predators.gif')).convert('RGB'),
    'Game of Life': Image.open(os.path.join(output_dir, 'game_of_life.gif')).convert('RGB'),
    'Turing Spots': Image.open(os.path.join(output_dir, 'turing_spots.png')),
    'Turing Stripes': Image.open(os.path.join(output_dir, 'turing_stripes.png')),
    'Sandpile': Image.open(os.path.join(output_dir, 'sandpile_final.png')),
}

# Resize all to same size
TARGET = 300
resized = {}
for name, img in imgs.items():
    ratio = min(TARGET / img.width, TARGET / img.height)
    new_size = (int(img.width * ratio), int(img.height * ratio))
    resized[name] = img.resize(new_size, Image.LANCZOS)

# Create 2x3 grid
PADDING = 10
TITLE_H = 30
cols, rows = 3, 2
cell_w = TARGET + PADDING
cell_h = TARGET + TITLE_H + PADDING
total_w = cols * cell_w + PADDING
total_h = rows * cell_h + PADDING

canvas = Image.new('RGB', (total_w, total_h), (255, 255, 255))

from PIL import ImageDraw, ImageFont

draw = ImageDraw.Draw(canvas)

names = list(resized.keys())
for idx, name in enumerate(names):
    row = idx // cols
    col = idx % cols
    x = PADDING + col * cell_w
    y = PADDING + row * cell_h
    
    # Draw title
    draw.text((x + 10, y + 5), name, fill=(30, 30, 30))
    
    # Paste image
    img = resized[name]
    paste_x = x + (TARGET - img.width) // 2
    paste_y = y + TITLE_H + (TARGET - img.height) // 2
    canvas.paste(img, (paste_x, paste_y))

output_path = os.path.join(output_dir, 'emergence_overview.png')
canvas.save(output_path)
print(f'Overview saved to: {output_path}')
