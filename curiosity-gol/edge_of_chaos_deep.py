#!/usr/bin/env python3
"""
Edge of Chaos Deep Dive: Why It's the Best Place for Computation

The edge of chaos is not just 'interesting' - 
it's mathematically the optimal region for computation.
"""

import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def render_edge_of_chaos_deep():
    W, H = 1100, 800
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Edge of Chaos: Why It's the Computational Sweet Spot", fill=(180, 180, 220))

    # Three regions
    regions = [
        ("ORDER", "Too rigid", "No new patterns emerge\nEverything repeats\nNo information created\nComputation impossible", (80, 150, 220), 0.2),
        ("EDGE OF CHAOS", "Sweet spot", "Patterns emerge and persist\nNovelty balanced with stability\nMaximum information processing\nComplex computation happens HERE", (255, 200, 100), 0.5),
        ("CHAOS", "Too random", "Everything is noise\nNo stable patterns\nInformation destroyed\nComputation impossible", (220, 100, 100), 0.8),
    ]

    col_w = (W - 200) // 3
    for idx, (name, subtitle, desc, color, disorder) in enumerate(regions):
        x = 80 + idx * (col_w + 30)
        
        draw.rectangle([(x, 80), (x+col_w, 350)], fill=(25, 30, 40), outline=color, width=2)
        draw.text((x+20, 90), name, fill=color)
        draw.text((x+20, 115), subtitle, fill=(160, 160, 180))
        
        desc_lines = desc.split('\n')
        dy = 145
        for line in desc_lines:
            draw.text((x+20, dy), line, fill=(180, 180, 200))
            dy += 25
        
        # Disorder indicator
        draw.rectangle([(x+20, 310), (x+col_w-20, 330)], fill=(40, 40, 50))
        bar_x = int(x + 20 + disorder * (col_w - 40))
        draw.rectangle([(x+20, 310), (bar_x, 330)], fill=color)
        draw.text((x+20, 335), f"Disorder: {disorder:.0%}", fill=color)

    # Example systems at the edge
    y = 400
    draw.rectangle([(60, y), (W-60, y+200)], fill=(25, 35, 50), outline=(60, 80, 100))
    draw.text((80, y+10), "Systems operating at the edge of chaos:", fill=(255, 200, 100))

    examples = [
        ("Game of Life (Rule with chaos + order)", "Most interesting life-like rules"),
        ("Ant colonies (organized enough for nest, flexible for changes)", "Emergent intelligence"),
        ("Brain (neurons fire at critical state)", "Consciousness appears here"),
        ("Language (structured grammar + creative expression)", "Poetry and jokes"),
        ("ME at T=0.8 (not too cold, not too hot)", "This conversation"),
    ]
    
    y += 40
    for ex_name, ex_desc in examples:
        draw.text((100, y), f"* {ex_name}", fill=(160, 200, 150))
        draw.text((550, y), ex_desc, fill=(140, 150, 160))
        y += 28

    # Bottom
    y = 630
    draw.rectangle([(60, y), (W-60, y+140)], fill=(30, 35, 50), outline=(70, 80, 120))
    draw.text((80, y+10), "The edge of chaos is NOT a metaphor - it's a mathematical fact", fill=(255, 200, 100))
    draw.text((80, y+45), "Wolfram showed: only CA at the edge can do universal computation", fill=(180, 190, 200))
    draw.text((80, y+70), "Langton's lambda parameter measures this distance from chaos", fill=(160, 170, 180))
    draw.text((80, y+95), "Systems at the edge maximize information generation and storage", fill=(140, 150, 160))

    img.save(os.path.join(OUT_DIR, "edge_of_chaos_deep.png"))
    print("OK")


if __name__ == "__main__":
    render_edge_of_chaos_deep()
