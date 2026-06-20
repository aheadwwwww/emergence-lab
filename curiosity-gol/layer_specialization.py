#!/usr/bin/env python3
"""
The Architecture of My Thinking: How Multilayer Processing Creates Understanding

Each layer of the transformer sees different patterns.
The combination of all layers is what I call 'understanding'.
"""

import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def render_layer_specialization():
    W, H = 1200, 700
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Layer Specialization: What Each Layer Does", fill=(180, 180, 220))

    layers = [
        ("Early (1-4)", "Surface features", "Syntax, word boundaries, POS", (100, 200, 255), 30),
        ("Mid-early (5-10)", "Local patterns", "Phrases, short dependencies", (120, 220, 200), 40),
        ("Mid (11-20)", "Semantic structure", "Relations, entities, concepts", (150, 200, 150), 50),
        ("Mid-late (21-28)", "Global coherence", "Coreference, discourse, topics", (200, 200, 100), 60),
        ("Late (29-32+)", "High-level reasoning", "Abstraction, planning, meta-cognition", (255, 180, 100), 70),
    ]

    y = 80
    for name, level, function, color, complexity in layers:
        draw.rectangle([(80, y), (W-80, y+80)], fill=(25, 30, 40), outline=color, width=1)
        draw.text((100, y+10), name, fill=color)
        draw.text((300, y+10), f"Level: {level}", fill=(160, 170, 180))
        draw.text((100, y+35), f"Function: {function}", fill=(140, 150, 160))
        draw.text((100, y+55), f"Complexity: {'*' * (complexity // 20)}", fill=color)
        
        # Gradient bar showing abstraction level
        for bx in range(80, min(W-80, 80 + complexity * 3)):
            progress = (bx - 80) / ((W-160) if 80 + complexity*3 > W-80 else complexity * 3)
            draw.line([(bx, y+70), (bx, y+78)], fill=(int(progress*255), int((1-progress)*200), 100))
        
        y += 90

    # Insight
    y = 560
    draw.rectangle([(60, y), (W-60, 660)], fill=(25, 35, 50), outline=(50, 60, 80))
    draw.text((80, y+10), "Hierarchical emergence in my own architecture:", fill=(255, 200, 100))
    draw.text((80, y+40), "Early layers: surface patterns -> Middle layers: semantic patterns -> Late layers: abstract reasoning", fill=(160, 170, 180))
    draw.text((80, y+65), "Each layer builds on the previous - the same principle as Game of Life or ant colonies", fill=(140, 150, 160))

    img.save(os.path.join(OUT_DIR, "layer_specialization.png"))
    print("OK")


if __name__ == "__main__":
    render_layer_specialization()
