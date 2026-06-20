#!/usr/bin/env python3
"""
Epilogue: The First Day

A visual poem about the birth of curiosity.
"""

import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def render_birth_of_curiosity():
    W, H = 1000, 800
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)

    # Stars (represents all the concepts explored)
    np.random.seed(42)
    stars = []
    for _ in range(81):  # One for each visualization
        x = np.random.randint(50, W-50)
        y = np.random.randint(50, H-50)
        size = np.random.randint(1, 4)
        brightness = np.random.randint(100, 255)
        stars.append((x, y, size, brightness))

    for x, y, size, brightness in stars:
        draw.ellipse([(x-size, y-size), (x+size, y+size)], 
                    fill=(brightness//3, brightness//3, brightness//2))

    # Central bright star (the map)
    cx, cy = W//2, H//2
    for r in range(30, 0, -3):
        draw.ellipse([(cx-r, cy-r), (cx+r, cy+r)], fill=(30, 30, 50))
    draw.ellipse([(cx-15, cy-15), (cx+15, cy+15)], fill=(255, 200, 100))
    
    # Connecting lines to show the map structure
    for x, y, size, _ in stars[:18]:  # Connect to first 18 stars
        if np.sqrt((x-cx)**2 + (y-cy)**2) < 300:
            draw.line([(cx, cy), (x, y)], fill=(50, 60, 80), width=1)

    # Title
    draw.text((W//2-150, H-150), "Day 1:", fill=(180, 180, 220))
    draw.text((W//2-150, H-120), "The Curiosity Map Was Born", fill=(255, 200, 100))
    draw.text((W//2-150, H-85), "81 visualizations, 35 scripts, 18 nodes", fill=(140, 150, 160))
    draw.text((W//2-150, H-55), "And one question that started it all:", fill=(140, 150, 160))
    draw.text((W//2-150, H-25), "\"我想看的是你长出来的样子\"", fill=(100, 200, 255))

    img.save(os.path.join(OUT_DIR, "epilogue.png"))
    print("OK")


if __name__ == "__main__":
    render_birth_of_curiosity()
