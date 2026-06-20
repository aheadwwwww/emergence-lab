NODES = [
    ("#001 Emergence", "Seeds", (100, 200, 255), 0.8),
    ("#002 Langton's Ant", "CA-emergence", (100, 200, 255), 0.3),
    ("#003 Edge of Chaos", "order-chaos boundary", (100, 200, 255), 0.4),
    ("#004 SOC", "self-organized criticality", (100, 200, 255), 0.3),
    ("#005 CA Classes", "Wolfram classification", (100, 200, 255), 0.5),
    ("#006 Turmites", "multi-color CA", (100, 200, 255), 0.3),
    ("#007 Boids", "flocking emergence", (100, 200, 255), 0.4),
    ("#008 Turing Patterns", "reaction-diffusion", (100, 200, 255), 0.3),
    ("#009 Game of Life", "2D CA textbook", (100, 200, 255), 0.5),
    ("#010 Computational Emergence", "rules to computation", (150, 255, 150), 0.5),
    ("#011 Grokking", "neural phase transition", (255, 200, 100), 0.5),
    ("#012 Scaling Laws", "power law criticality", (255, 200, 100), 0.4),
    ("#013 Attention", "information routing", (255, 180, 100), 0.6),
    ("#014 Computational Universe", "universe = computation", (255, 150, 100), 0.5),
    ("#015 Cognitive Gap", "why emergence feels magic", (255, 150, 150), 0.4),
    ("#016 Self-Reference", "AI understands itself", (200, 150, 255), 0.5),
    ("#017 Creativity", "edge of chaos creativity", (200, 255, 200), 0.4),
    ("#018 Hallucination", "creativity's dark side", (255, 200, 200), 0.4),
]


import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    W, H = 1400, 1000
    img = Image.new("RGB", (W, H), (12, 12, 22))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(W//2-250, 15), (W//2+250, 50)], fill=(25, 25, 40), outline=(50, 50, 80))
    draw.text((W//2-220, 22), "Curiosity Map - 18 Nodes", fill=(180, 180, 220))

    positions = [
        (700, 80),
        (200, 220),
        (500, 220),
        (500, 380),
        (120, 380),
        (200, 540),
        (900, 220),
        (900, 380),
        (200, 700),
        (200, 860),
        (1200, 220),
        (1200, 380),
        (1200, 540),
        (900, 540),
        (900, 700),
        (1200, 700),
        (1200, 860),
        (700, 860),
    ]

    connections = [
        (0, 1), (0, 2), (0, 6), (0, 10),
        (1, 4), (1, 5), (1, 8),
        (2, 3), (2, 4),
        (6, 7), (6, 13),
        (10, 11), (10, 12),
        (13, 14), (13, 12),
        (12, 15), (8, 5), (8, 9), (9, 5), (9, 8),
        (15, 16), (15, 17), (14, 15), (14, 16),
    ]

    for start, end in connections:
        if start < len(positions) and end < len(positions):
            x1, y1 = positions[start]
            x2, y2 = positions[end]
            draw.line([(x1, y1), (x2, y2)], fill=(40, 50, 70), width=1)

    for idx, ((x, y), (name, desc, color, size)) in enumerate(zip(positions, NODES)):
        r = 18 + int(size * 15)
        draw.ellipse([(x-r, y-r), (x+r, y+r)], fill=(30, 35, 50), outline=color, width=2)
        draw.text((x-r+5, y-8), name, fill=color)
        draw.text((x-r+5, y+10), desc[:25], fill=(160, 160, 180))

    img.save(os.path.join(OUT_DIR, "curiosity_map.png"))
    print("Saved: curiosity_map.png")


if __name__ == "__main__":
    main()
