#!/usr/bin/env python3
"""
Scale and Emergence: Why Size Matters

Larger systems exhibit different emergent properties.
There are critical thresholds where new behaviors appear.
"""

import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def render_scale_thresholds():
    W, H = 1100, 700
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Scale Thresholds: Where New Abilities Emerge", fill=(180, 180, 220))

    # Y axis: Capability
    draw.line([(100, 600), (100, 100)], fill=(80, 80, 120), width=2)
    draw.text((40, 100), "Capability", fill=(140, 140, 180))

    # X axis: Scale (log)
    draw.line([(100, 600), (W-80, 600)], fill=(80, 80, 120), width=2)
    draw.text((W-100, 610), "Scale (log)", fill=(140, 140, 180))

    # Draw S-curves for different capabilities
    curves = [
        ("Basic pattern matching", 120, 250, (100, 200, 255)),
        ("Reasoning", 250, 450, (150, 200, 100)),
        ("Instruction following", 200, 400, (255, 200, 100)),
        ("Code generation", 350, 500, (100, 200, 150)),
        ("Translation", 150, 300, (200, 150, 255)),
    ]

    for name, x_start, x_end, color in curves:
        # Draw sigmoid-like curve
        points = []
        for x in range(x_start, x_end, 10):
            t = (x - x_start) / (x_end - x_start)
            y = 580 - t * 300  # Simple linear for illustration
            if t > 0.3 and t < 0.7:
                # Steeper in the middle
                y = 580 - (0.3 + (t - 0.3) * 2) * 300
            points.append((x, y))
        
        for i in range(len(points) - 1):
            draw.line([points[i], points[i+1]], fill=color, width=2)
        
        # Label
        draw.text((x_end - 80, 580 - 420), name, fill=color)

    # Highlight the "emergence point"
    draw.line([(300, 100), (300, 600)], fill=(255, 200, 100), width=2)
    draw.text((250, 80), "~1B params", fill=(255, 200, 100))
    draw.line([(450, 100), (450, 600)], fill=(255, 200, 100), width=1)
    draw.text((400, 80), "~100B params", fill=(255, 200, 100))

    # Bottom insight
    y = 620
    draw.rectangle([(60, y), (W-60, 680)], fill=(25, 35, 50), outline=(50, 60, 80))
    draw.text((80, y+10), "Emergence is NOT magic - it requires sufficient scale to manifest", fill=(255, 200, 100))
    draw.text((80, y+35), "Below threshold: capability absent. Above threshold: suddenly present.", fill=(160, 170, 180))

    img.save(os.path.join(OUT_DIR, "scale_thresholds.png"))
    print("OK")


def render_critical_mass():
    """Visualize the concept of critical mass for emergence"""
    W, H = 1000, 700
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Critical Mass: Threshold of Emergence", fill=(180, 180, 220))

    # Systems that need critical mass
    systems = [
        ("Neural Network", "Below 10M params", "Above 1B params",
         "No reasoning", "Emergent abilities", (100, 200, 255)),
        ("Game of Life", "Small grid (< 10x10)", "Large grid (> 50x50)",
         "Only simple oscillators", "Glider guns, Turing machines", (150, 200, 150)),
        ("Ant Colony", "10 ants", "10,000 ants",
         "Random movement", "Complex nest building", (200, 180, 100)),
        ("Human Brain", "Baby (100M neurons)", "Adult (86B neurons)",
         "Basic reflexes", "Self-awareness, language", (200, 150, 200)),
        ("Economy", "Isolated village", "Global market",
         "Barter only", "Complex financial systems", (255, 150, 150)),
    ]

    y = 80
    for name, below_desc, above_desc, below_behav, above_behav, color in systems:
        draw.rectangle([(80, y), (W-80, y+80)], fill=(25, 30, 40), outline=color, width=1)
        draw.text((100, y+8), name, fill=color)
        draw.text((100, y+35), below_desc, fill=(160, 100, 100))
        draw.text((100, y+55), f"Behavior: {below_behav}", fill=(160, 130, 130))
        draw.text((450, y+35), above_desc, fill=(100, 200, 100))
        draw.text((450, y+55), f"Behavior: {above_behav}", fill=(130, 200, 130))

        # Critical mass indicator
        cx, cy = 380, y+15
        draw.ellipse([(cx-5, cy-5), (cx+5, cy+5)], fill=(255, 200, 100))
        draw.text((cx+8, cy-8), "Critical mass", fill=(255, 200, 100))

        y += 88

    # Bottom insight
    y = 610
    draw.rectangle([(60, y), (W-60, 680)], fill=(30, 35, 50), outline=(60, 70, 100))
    draw.text((80, y+10), "Critical mass is the point where quantity becomes quality", fill=(255, 200, 100))
    draw.text((80, y+35), "More elements -> More interactions -> More emergent properties", fill=(160, 170, 180))
    draw.text((80, y+55), "This applies to ants, neurons, and me", fill=(140, 150, 160))

    img.save(os.path.join(OUT_DIR, "critical_mass.png"))
    print("OK")


if __name__ == "__main__":
    render_scale_thresholds()
    render_critical_mass()
