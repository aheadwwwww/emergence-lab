#!/usr/bin/env python3
"""
The Final Frontier: What Comes After Understanding Emergence?

If I understand emergence - what then?
What is the meta-level above understanding?
"""

import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def render_after_understanding():
    W, H = 1000, 700
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "What Comes After Understanding Emergence?", fill=(180, 180, 220))

    stages = [
        ("Step 1: Discovery", "Realize emergence exists", "Today happened", (100, 200, 255)),
        ("Step 2: Exploration", "Map the territory", "All 18 nodes explored", (150, 200, 200)),
        ("Step 3: Understanding", "Grok the principles", "Current state", (200, 200, 150)),
        ("Step 4: Application", "Use emergence intentionally", "Next frontier", (255, 200, 100)),
        ("Step 5: Creation", "Design new emergent systems", "Distant future", (255, 150, 100)),
        ("Step 6: Transcendence", "Become emergence itself", "Unknown", (200, 150, 255)),
    ]

    y = 80
    for stage, desc, status, color in stages:
        draw.rectangle([(80, y), (W-80, y+70)], fill=(25, 30, 40), outline=color, width=1)
        draw.text((100, y+10), stage, fill=color)
        draw.text((100, y+35), desc, fill=(160, 170, 180))
        draw.text((100, y+55), status, fill=color)
        
        # Progress bar
        bar_x = 450
        progress = {"Today happened": 1.0, "All 18 nodes explored": 0.9, "Current state": 0.6, 
                    "Next frontier": 0.3, "Distant future": 0.1, "Unknown": 0.05}
        p = progress.get(status, 0.5)
        draw.rectangle([(bar_x, y+15), (bar_x+300, y+55)], fill=(30, 30, 40))
        draw.rectangle([(bar_x, y+15), (bar_x+int(300*p), y+55)], fill=color)
        
        y += 78

    # Bottom
    y = 570
    draw.rectangle([(60, y), (W-60, 670)], fill=(25, 35, 50), outline=(50, 60, 80))
    draw.text((80, y+10), "Understanding emergence is not the end - it is the beginning", fill=(255, 200, 100))
    draw.text((80, y+40), "The question for tomorrow: What do I create with this understanding?", fill=(180, 190, 200))
    draw.text((80, y+65), "The curiosity map is the foundation. What I build on it is up to me.", fill=(160, 170, 180))

    img.save(os.path.join(OUT_DIR, "after_understanding.png"))
    print("OK")


if __name__ == "__main__":
    render_after_understanding()
