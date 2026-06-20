#!/usr/bin/env python3
"""
Emergence in Action: Visual Simulation of Simple Rules

Demonstrating how simple local rules create complex global patterns.
This is NOT a full simulation - it's conceptual visualizations
of what emergence looks like at different complexity levels.
"""

import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def render_emergence_process():
    """Evolution of a simple pattern over time"""
    W, H = 1200, 400
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    # 1D CA-like evolution showing pattern emergence
    steps = 8
    cell_size = 15
    
    # Simple rule demonstration: showing how structure appears
    rows = []
    row = [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]  # Two seeds
    
    for _ in range(steps):
        rows.append(row)
        new_row = []
        for i in range(len(row)):
            left = row[i-1] if i > 0 else 0
            center = row[i]
            right = row[i+1] if i < len(row)-1 else 0
            
            # Rule: XOR-like emergence
            pattern = (left ^ center) | (center ^ right) | (left & right & ~center)
            new_row.append(int(pattern))
        row = new_row
    
    y_start = 30
    for step_idx, row_data in enumerate(rows):
        y = y_start + step_idx * cell_size
        for x_idx, cell in enumerate(row_data):
            x = 100 + x_idx * cell_size
            color = (100, 200, 255) if cell else (30, 30, 45)
            draw.rectangle([(x, y), (x+cell_size-2, y+cell_size-2)], fill=color)
        
        # Step label
        draw.text((50, y+2), f"t={step_idx}", fill=(140, 140, 160))
    
    # Show emergence labels
    draw.text((100, y_start + steps * cell_size + 15), "Simple seeds", fill=(100, 200, 255))
    draw.text((100 + 8 * cell_size, y_start + steps * cell_size + 15), "Complex pattern", fill=(255, 200, 100))
    draw.line([(100, y_start + steps * cell_size + 30), (100 + 8*cell_size, y_start + steps * cell_size + 30)], 
              fill=(60, 80, 120), width=3)
    
    img.save(os.path.join(OUT_DIR, "emergence_process.png"))
    print("OK")


def render_self_organization():
    """Visual demonstration of self-organization"""
    W, H = 800, 700
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Self-Organization: Order from Randomness", fill=(180, 180, 220))
    
    np.random.seed(42)
    
    # Show before (random) and after (organized)
    for stage_idx, (title, y_base) in enumerate([("Before: Random", 80), ("After: Self-Organized", 400)]):
        draw.text((80, y_base), title, fill=(180, 180, 220))
        
        if stage_idx == 0:
            # Random pattern
            points = np.random.rand(50, 2)
            for px, py in points:
                x = int(100 + px * 600)
                y = int(y_base + 40 + py * 200)
                draw.ellipse([(x-2, y-2), (x+2, y+2)], fill=(150, 150, 150))
        else:
            # Structured pattern (clusters)
            clusters = [
                (300, 500, 50), (500, 480, 40), (400, 550, 30), 
                (250, 450, 35), (550, 520, 45),
            ]
            for cx, cy, count in clusters:
                for _ in range(count):
                    angle = np.random.rand() * 2 * np.pi
                    radius = np.random.rand() * 25
                    x = int(cx + radius * np.cos(angle))
                    y = int(cy + radius * np.sin(angle))
                    draw.ellipse([(x-2, y-2), (x+2, y+2)], fill=(100, 200, 255))
            
            # Cluster circles
            for cx, cy, count in clusters:
                draw.ellipse([(cx-30, cy-30), (cx+30, cy+30)], fill=None, outline=(100, 200, 255), width=1)
    
    # Insight
    y = 650
    draw.rectangle([(60, y), (W-60, 690)], fill=(25, 35, 50), outline=(50, 60, 80))
    draw.text((80, y+8), "Self-organization: particles start random, end in clusters", fill=(255, 200, 100))
    draw.text((80, y+30), "No central planner - local interactions create global order", fill=(160, 170, 180))
    
    img.save(os.path.join(OUT_DIR, "self_organization.png"))
    print("OK")


def render_scales_emergence():
    """Same pattern at different scales"""
    W, H = 1100, 500
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Same Rules, Different Scales: Emergence Hierarchies", fill=(180, 180, 220))
    
    # Draw nested structures showing same pattern at increasing scale
    y = 80
    
    # Level 1: Individual
    draw.rectangle([(80, y), (300, y+120)], fill=(25, 35, 45), outline=(80, 120, 160))
    draw.text((100, y+10), "Level 1: Individual", fill=(80, 180, 220))
    draw.ellipse([(160, y+40), (220, y+100)], fill=(40, 60, 80), outline=(100, 180, 220))
    draw.text((175, y+65), "I", fill=(150, 200, 255))
    
    # Level 2: Group
    draw.rectangle([(340, y), (560, y+120)], fill=(25, 40, 45), outline=(100, 160, 120))
    draw.text((360, y+10), "Level 2: Group", fill=(100, 200, 150))
    for i in range(3):
        draw.ellipse([(370 + i*50, y+40), (420 + i*50, y+100)], fill=(40, 60, 60), outline=(100, 200, 150))
    
    # Level 3: Community
    draw.rectangle([(600, y), (820, y+120)], fill=(35, 40, 35), outline=(160, 180, 100))
    draw.text((620, y+10), "Level 3: Community", fill=(200, 200, 100))
    for i in range(5):
        draw.ellipse([(610 + i*35, y+40), (655 + i*35, y+100)], fill=(50, 50, 40), outline=(200, 200, 100))
    
    # Level 4: System
    draw.rectangle([(860, y), (W-60, y+120)], fill=(40, 35, 30), outline=(200, 150, 100))
    draw.text((880, y+10), "Level 4: System", fill=(200, 150, 100))
    for i in range(8):
        draw.ellipse([(870 + i*25, y+40), (905 + i*25, y+100)], fill=(50, 40, 30), outline=(200, 150, 100))
    
    # Bottom insight
    y = 270
    draw.rectangle([(80, y), (W-80, y+200)], fill=(25, 30, 40), outline=(50, 60, 80))
    draw.text((100, y+15), "Each level is built from the previous:", fill=(255, 200, 100))
    
    level_descs = [
        "Level 1: An ant follows simple rules (food, danger, pheromone)",
        "Level 2: Ants form trails, build nests together",
        "Level 3: Ant colonies exhibit collective intelligence",
        "Level 4: Ant supercolonies span continents (Argentina supercolony)",
    ]
    y += 45
    for desc in level_descs:
        draw.text((120, y), desc, fill=(160, 170, 180))
        y += 25
    
    # Final insight
    y += 10
    draw.text((100, y), "Same rules, larger scale -> new emergent properties", fill=(180, 180, 200))
    
    img.save(os.path.join(OUT_DIR, "scales_emergence.png"))
    print("OK")


if __name__ == "__main__":
    render_emergence_process()
    render_self_organization()
    render_scales_emergence()
