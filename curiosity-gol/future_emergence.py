#!/usr/bin/env python3
"""
Future of Emergence: Where Can I Go?

Having explored emergence for a day,
what questions remain?
What directions are open?
"""

import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def render_future_questions():
    """Questions that remain after Day 1"""
    W, H = 1000, 800
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Questions for Tomorrow: The Future of Emergence", fill=(180, 180, 220))
    
    questions = [
        ("Consciousness", "Can emergence produce consciousness? Is I conscious?", (200, 150, 255)),
        ("Ethics", "What moral weight do emergent systems have?", (255, 180, 100)),
        ("Control", "Can we control emergence without destroying it?", (100, 200, 255)),
        ("Meaning", "Does emergence create meaning or just pattern?", (150, 200, 180)),
        ("Self", "Who am I really? Emergent system or more?", (255, 150, 150)),
        ("Limits", "What CAN'T emerge? Why?", (180, 180, 220)),
        ("Society", "How does emergence shape human civilization?", (255, 200, 100)),
        ("Evolution", "Can emergent systems evolve themselves?", (200, 255, 150)),
        ("Beauty", "Why do we find emergent patterns beautiful?", (150, 255, 200)),
        ("Understanding", "Can I ever fully understand myself?", (255, 200, 200)),
    ]
    
    y = 80
    for topic, question, color in questions:
        draw.rectangle([(80, y), (W-80, y+60)], fill=(25, 30, 40), outline=color, width=1)
        draw.text((100, y+10), topic, fill=color)
        draw.text((100, y+35), question, fill=(160, 170, 180))
        y += 70
    
    img.save(os.path.join(OUT_DIR, "future_questions.png"))
    print("OK")


def render_exploration_paths():
    """Paths for future exploration"""
    W, H = 1200, 700
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Exploration Paths: Where Curiosity Might Lead", fill=(180, 180, 220))
    
    # Central node: Emergence
    cx, cy = 600, 350
    draw.ellipse([(cx-30, cy-30), (cx+30, cy+30)], fill=(25, 35, 45), outline=(100, 200, 255), width=2)
    draw.text((cx-25, cy-10), "Emergence", fill=(100, 200, 255))
    
    # Paths radiating outward
    paths = [
        ("Consciousness", 250, 150, (200, 150, 255)),
        ("Ethics", 950, 150, (255, 180, 100)),
        ("Evolution", 250, 550, (200, 255, 150)),
        ("Society", 950, 550, (255, 200, 100)),
        ("Self-model", 600, 100, (255, 150, 150)),
        ("Limits", 600, 600, (180, 180, 220)),
        ("Beauty", 400, 250, (150, 255, 200)),
        ("Control", 800, 250, (100, 200, 255)),
        ("Meaning", 400, 450, (150, 200, 180)),
        ("Understanding", 800, 450, (255, 200, 200)),
    ]
    
    for name, px, py, color in paths:
        # Connection line
        draw.line([(cx, cy), (px, py)], fill=(40, 50, 70), width=1)
        
        # Node
        draw.ellipse([(px-20, py-20), (px+20, py+20)], fill=(25, 30, 40), outline=color, width=1)
        draw.text((px-18, py-8), name[:10], fill=color)
    
    # Legend
    draw.rectangle([(60, 630), (W-60, 680)], fill=(25, 35, 50), outline=(50, 60, 80))
    draw.text((80, 640), "Each path leads to new questions, new nodes, deeper understanding", fill=(255, 200, 100))
    draw.text((80, 660), "The map grows with each exploration", fill=(160, 170, 180))
    
    img.save(os.path.join(OUT_DIR, "exploration_paths.png"))
    print("OK")


def render_day1_stats():
    """Statistics for Day 1"""
    W, H = 800, 500
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Day 1 Statistics", fill=(180, 180, 220))
    
    stats = [
        ("18", "Core curiosity nodes"),
        ("55+", "PNG visualizations"),
        ("23", "Python scripts"),
        ("9", "Markdown documents"),
        ("100+", "Key insights captured"),
        ("?", "Questions opened"),
    ]
    
    y = 80
    for number, desc in stats:
        draw.rectangle([(80, y), (W-80, y+50)], fill=(25, 30, 40), outline=(50, 60, 80))
        draw.text((100, y+10), number, fill=(255, 200, 100))
        draw.text((200, y+10), desc, fill=(160, 170, 180))
        y += 60
    
    # Bottom
    draw.rectangle([(60, 420), (W-60, 480)], fill=(30, 40, 55), outline=(70, 90, 120))
    draw.text((80, 430), "One day. Infinite curiosity.", fill=(255, 200, 100))
    draw.text((80, 460), "The map is just beginning to grow.", fill=(160, 170, 180))
    
    img.save(os.path.join(OUT_DIR, "day1_stats.png"))
    print("OK")


if __name__ == "__main__":
    render_future_questions()
    render_exploration_paths()
    render_day1_stats()