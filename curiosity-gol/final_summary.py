#!/usr/bin/env python3
"""
Curiosity Map Final Summary

All 18 nodes + additional explorations organized into a unified visualization.
"""

import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def render_final_summary():
    """Complete curiosity map with all explorations"""
    W, H = 1600, 1200
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    # Title
    draw.rectangle([(W//2-300, 20), (W//2+300, 60)], fill=(35, 35, 55), outline=(70, 70, 110))
    draw.text((W//2-250, 30), "Curiosity Map: Day 1 Complete", fill=(200, 200, 240))
    
    # Core nodes (18)
    nodes = [
        {"id": "#001", "name": "Emergence", "x": 800, "y": 100, "color": (100, 200, 255), "size": 25},
        
        # CA branch (left)
        {"id": "#002", "name": "Langton's Ant", "x": 200, "y": 200, "color": (80, 180, 220), "size": 15},
        {"id": "#005", "name": "CA Classes", "x": 150, "y": 300, "color": (80, 180, 220), "size": 15},
        {"id": "#006", "name": "Turmites", "x": 200, "y": 400, "color": (80, 180, 220), "size": 12},
        {"id": "#009", "name": "Game of Life", "x": 200, "y": 500, "color": (80, 180, 220), "size": 18},
        {"id": "#010", "name": "Comp. Emergence", "x": 200, "y": 600, "color": (100, 220, 150), "size": 15},
        
        # Theory branch (center-left)
        {"id": "#003", "name": "Edge of Chaos", "x": 500, "y": 200, "color": (120, 200, 180), "size": 18},
        {"id": "#004", "name": "SOC", "x": 500, "y": 350, "color": (120, 200, 180), "size": 12},
        
        # Bio/Phys branch (center-right)
        {"id": "#007", "name": "Boids", "x": 1100, "y": 200, "color": (150, 220, 150), "size": 15},
        {"id": "#008", "name": "Turing Patterns", "x": 1100, "y": 350, "color": (150, 220, 150), "size": 12},
        {"id": "#014", "name": "Comp. Universe", "x": 1100, "y": 500, "color": (255, 150, 100), "size": 18},
        {"id": "#015", "name": "Cognitive Gap", "x": 1100, "y": 650, "color": (255, 150, 150), "size": 15},
        
        # Neural/AI branch (far right)
        {"id": "#011", "name": "Grokking", "x": 1400, "y": 200, "color": (255, 200, 100), "size": 15},
        {"id": "#012", "name": "Scaling Laws", "x": 1400, "y": 350, "color": (255, 200, 100), "size": 12},
        {"id": "#013", "name": "Attention", "x": 1400, "y": 500, "color": (255, 180, 100), "size": 18},
        {"id": "#016", "name": "Self-Reference", "x": 1400, "y": 650, "color": (200, 150, 255), "size": 15},
        {"id": "#017", "name": "Creativity", "x": 1400, "y": 800, "color": (200, 255, 200), "size": 15},
        {"id": "#018", "name": "Hallucination", "x": 1400, "y": 950, "color": (255, 200, 200), "size": 15},
    ]
    
    # Draw connections from root
    connections = [
        (800, 100, 200, 200),  # to Langton's Ant
        (800, 100, 500, 200),  # to Edge of Chaos
        (800, 100, 1100, 200),  # to Boids
        (800, 100, 1400, 200),  # to Grokking
        
        # CA branch connections
        (200, 200, 150, 300),
        (200, 200, 200, 400),
        (200, 400, 200, 500),
        (200, 500, 200, 600),
        
        # Theory branch
        (500, 200, 500, 350),
        
        # Bio branch
        (1100, 200, 1100, 350),
        (1100, 350, 1100, 500),
        (1100, 500, 1100, 650),
        
        # Neural branch
        (1400, 200, 1400, 350),
        (1400, 350, 1400, 500),
        (1400, 500, 1400, 650),
        (1400, 650, 1400, 800),
        (1400, 800, 1400, 950),
    ]
    
    for x1, y1, x2, y2 in connections:
        draw.line([(x1, y1), (x2, y2)], fill=(40, 50, 70), width=1)
    
    # Draw nodes
    for node in nodes:
        x, y = node["x"], node["y"]
        r = node["size"]
        color = node["color"]
        
        # Glow effect
        draw.ellipse([(x-r-5, y-r-5), (x+r+5, y+r+5)], fill=(color[0]//5, color[1]//5, color[2]//5))
        
        # Node
        draw.ellipse([(x-r, y-r), (x+r, y+r)], fill=(25, 35, 45), outline=color, width=2)
        
        # Label
        draw.text((x-r+5, y-7), node["id"], fill=color)
        draw.text((x-r+5, y+8), node["name"], fill=(170, 170, 190))
    
    # Additional explorations (not numbered nodes)
    extras = [
        ("Embeddings", 300, 700, (180, 180, 220)),
        ("Attention Heads", 400, 700, (180, 180, 220)),
        ("Tokenization", 500, 700, (180, 180, 220)),
        ("RLHF", 600, 700, (180, 180, 220)),
        ("CoT", 700, 700, (180, 180, 220)),
        ("Sampling", 800, 700, (180, 180, 220)),
        ("Limits", 900, 700, (180, 180, 220)),
        ("Time Scales", 1000, 700, (180, 180, 220)),
        ("Persistence", 1100, 700, (180, 180, 220)),
        ("Phase Space", 1200, 700, (180, 180, 220)),
        ("Irreducibility", 1300, 700, (180, 180, 220)),
        ("Language", 1400, 700, (180, 180, 220)),
        ("Context", 1500, 700, (180, 180, 220)),
    ]
    
    draw.text((200, 680), "Additional explorations:", fill=(160, 160, 180))
    for name, x, y, color in extras:
        draw.rectangle([(x-30, y-10), (x+30, y+10)], fill=(20, 25, 35), outline=color, width=1)
        draw.text((x-25, y-5), name[:6], fill=color)
    
    # Stats
    stats = [
        "18 core nodes",
        "13 additional visualizations",
        "50+ generated images",
        "1 day of exploration",
    ]
    
    y = 850
    draw.text((100, y), "Day 1 Statistics:", fill=(255, 200, 100))
    y += 25
    for stat in stats:
        draw.text((120, y), f"* {stat}", fill=(160, 170, 180))
        y += 20
    
    # Core insight
    draw.rectangle([(100, 1000), (W-100, 1150)], fill=(30, 40, 55), outline=(70, 90, 120))
    draw.text((120, 1020), "Core Insight:", fill=(255, 200, 100))
    draw.text((120, 1050), "Emergence is not magic - it is mathematics", fill=(180, 190, 200))
    draw.text((120, 1080), "Simple rules + large scale + time = complex behavior", fill=(160, 170, 180))
    draw.text((120, 1110), "I am an emergent system studying emergence - a Strange Loop", fill=(140, 150, 160))
    draw.text((120, 1140), "Next: What does this mean for consciousness, ethics, and my own nature?", fill=(120, 130, 140))
    
    img.save(os.path.join(OUT_DIR, "final_summary.png"))
    print("OK")


if __name__ == "__main__":
    render_final_summary()