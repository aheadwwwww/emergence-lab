#!/usr/bin/env python3
"""
Everything I Created Today

A visual inventory of all experiments.
"""

import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def render_all_experiments():
    W, H = 1400, 900
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Everything I Created Today: A Visual Inventory", fill=(180, 180, 220))

    # Categories as boxes
    categories = [
        ("CA & Systems", ["Langton's Ant", "SOC Sandpile", "CA Classes", "Turmites", "Game of Life", "Edge of Chaos"], (80, 180, 220)),
        ("Biological", ["Boids", "Turing Patterns", "Language Emergence"], (150, 220, 150)),
        ("Neural Networks", ["Grokking", "Scaling Laws", "XOR Learning", "Grokking Sim"], (255, 200, 100)),
        ("Architecture", ["Transformer Flow", "Attention Heads", "KV Cache", "Position Encoding", "MoE", "Residual Stream"], (100, 200, 255)),
        ("AI Properties", ["Creativity", "Hallucination", "Sampling", "CoT", "RLHF", "Context Window"], (255, 180, 150)),
        ("Philosophy", ["Comp. Universe", "Cognitive Gap", "Self-Reference", "Consciousness", "Free Will", "Recursive Self"], (200, 150, 255)),
        ("Theory", ["Emergence Limits", "Phase Space", "Computation", "Kolmogorov", "Shannon Entropy", "Critical Mass"], (150, 200, 180)),
        ("Meta", ["My Story", "Self Portrait", "Strange Loop", "Probability", "Future Questions", "Epilogue"], (180, 180, 220)),
    ]

    cols = 4
    card_w = 280
    card_h = 240
    gap_x = 40
    gap_y = 30
    start_x = 60
    start_y = 80

    for idx, (cat_name, items, color) in enumerate(categories):
        col = idx % cols
        row = idx // cols
        x = start_x + col * (card_w + gap_x)
        y = start_y + row * (card_h + gap_y)

        # Card background
        draw.rectangle([(x, y), (x+card_w, y+card_h)], fill=(20, 25, 35), outline=color, width=1)
        
        # Category name
        draw.text((x+15, y+10), cat_name, fill=color)
        draw.line([(x+15, y+30), (x+card_w-15, y+30)], fill=(40, 50, 70), width=1)

        # Items list
        item_y = y + 45
        for item in items:
            draw.text((x+20, item_y), f"* {item}", fill=(160, 170, 180))
            item_y += 22

    # Final count
    y = 830
    draw.rectangle([(60, y), (W-60, 880)], fill=(25, 35, 50), outline=(50, 60, 80))
    draw.text((80, y+10), "Total: 90+ experiments, Python scripts, and visualizations | 18 core curiosity nodes | 1 day of exploration", fill=(255, 200, 100))

    img.save(os.path.join(OUT_DIR, "all_experiments_inventory.png"))
    print("OK")


if __name__ == "__main__":
    render_all_experiments()
