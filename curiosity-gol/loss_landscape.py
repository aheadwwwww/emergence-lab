#!/usr/bin/env python3
"""
Loss Landscape: The Terrain of Learning

How optimization shapes an emergent system.
The loss landscape is the terrain. Gradient descent is the explorer.
"""

import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def render_loss_landscape():
    """Visualize the loss landscape of training"""
    W, H = 1000, 700
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "The Loss Landscape: Terrain of Learning", fill=(180, 180, 220))

    # Draw layered terrain
    np.random.seed(42)
    terrain = np.random.randn(50, 50) * 0.5
    # Add some structure (basins)
    for cx, cy, depth in [(20, 20, -2), (35, 35, -1.5), (10, 40, -1), (40, 15, -0.8)]:
        for x in range(max(0, cx-8), min(50, cx+8)):
            for y in range(max(0, cy-8), min(50, cy+8)):
                dist = np.sqrt((x-cx)**2 + (y-cy)**2)
                terrain[x, y] -= depth * np.exp(-dist/3)

    # Find global minimum
    min_pos = np.unravel_index(np.argmin(terrain), terrain.shape)

    # Draw terrain as colored cells
    x_start, y_start = 80, 80
    cell_size = 12

    for x in range(terrain.shape[0]):
        for y in range(terrain.shape[1]):
            val = terrain[x, y]
            # Normalize to 0-1
            norm = (val - terrain.min()) / (terrain.max() - terrain.min())
            # Color: blue (low/deep) to red (high/shallow)
            r = int(100 + 155 * (1 - norm))
            g = int(100 * (1 - norm))
            b = int(255 * (1 - norm) + 80 * norm)
            draw.rectangle([(x_start + x*cell_size, y_start + y*cell_size),
                           (x_start + x*cell_size + cell_size-1, y_start + y*cell_size + cell_size-1)],
                          fill=(r//2, g//2, b//2))

    # Mark global minimum
    gx = x_start + min_pos[0]*cell_size
    gy = y_start + min_pos[1]*cell_size
    draw.ellipse([(gx-6, gy-6), (gx+6, gy+6)], fill=(255, 200, 100))
    draw.text((gx+10, gy-5), "Global optimum", fill=(255, 200, 100))

    # Mark some local minima
    local_mins = [(15, 15), (40, 40), (10, 45), (45, 20)]
    for lx, ly in local_mins:
        dx = x_start + lx*cell_size
        dy = y_start + ly*cell_size
        draw.ellipse([(dx-4, dy-4), (dx+4, dy+4)], fill=(255, 150, 150))
        draw.text((dx+8, dy-8), "Local min", fill=(255, 150, 150))

    # Legend
    y = 570
    draw.rectangle([(60, y), (W-60, y+100)], fill=(25, 30, 40), outline=(50, 60, 80))
    draw.text((80, y+10), "Key concepts:", fill=(255, 200, 100))
    draw.text((80, y+35), "Deep blue = low loss (good). Red = high loss (bad).", fill=(160, 170, 180))
    draw.text((80, y+55), "Gradient descent: move downhill on this terrain", fill=(160, 170, 180))
    draw.text((80, y+75), "The billion-parameter model navigates an impossibly complex landscape", fill=(140, 150, 160))

    img.save(os.path.join(OUT_DIR, "loss_landscape.png"))
    print("OK")


def render_optimization_path():
    """Show the path of optimization through parameter space"""
    W, H = 1000, 400
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Optimization Path: From Random to Learned", fill=(180, 180, 220))

    # Draw a path from start (high loss) to end (low loss)
    np.random.seed(123)
    
    # S-shaped path through landscape
    path = []
    x, y = 100, 300
    for i in range(30):
        x += 25 + np.random.randn() * 5
        y += np.sin(i * 0.5) * 15 + np.random.randn() * 3
        y = max(80, min(y, 350))
        path.append((int(x), int(y)))

    # Draw background (simple gradient)
    for px, py in path:
        # Gradient from red (start) to green (end)
        idx = path.index((px, py))
        progress = idx / len(path)
        color = (int(255*(1-progress)), int(200*progress), int(100*(1-progress)))
        draw.ellipse([(px-8, py-8), (px+8, py+8)], fill=(*color, 60), outline=color, width=1)

    # Draw the path line
    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i+1]
        progress = i / len(path)
        color = (int(255*(1-progress)), int(200*progress), int(100*(1-progress)))
        draw.line([(x1, y1), (x2, y2)], fill=color, width=2)

    # Start/End labels
    draw.text((path[0][0]-15, path[0][1]+15), "Start (random)", fill=(255, 100, 100))
    draw.text((path[-1][0]-15, path[-1][1]-30), "End (trained)", fill=(100, 255, 100))

    # Insight
    y = 360
    draw.rectangle([(60, y), (W-60, 395)], fill=(25, 35, 50), outline=(50, 60, 80))
    draw.text((80, y+8), "Training: billions of steps through a billion-dimensional landscape", fill=(255, 200, 100))
    draw.text((80, y+28), "Random initialization -> careful optimization -> emergent abilities", fill=(160, 170, 180))

    img.save(os.path.join(OUT_DIR, "optimization_path.png"))
    print("OK")


if __name__ == "__main__":
    render_loss_landscape()
    render_optimization_path()
