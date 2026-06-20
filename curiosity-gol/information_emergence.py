#!/usr/bin/env python3
"""
Emergence and Information: How Complexity Encodes Meaning

Information is the currency of emergence.
Simple rules encode information implicitly.
Complex behavior encodes information explicitly.
"""

import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def render_information_hierarchy():
    """Information hierarchy in emergent systems"""
    W, H = 1000, 700
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Information Hierarchy in Emergent Systems", fill=(180, 180, 220))
    
    levels = [
        ("Bits", "Binary states", "0/1, on/off", "The lowest level", (100, 200, 255)),
        ("Patterns", "Repeated sequences", "Blips, oscillators", "Recognition begins", (120, 200, 220)),
        ("Structures", "Persistent forms", "Gliders, blocks", "Stable information", (150, 200, 200)),
        ("Dynamics", "Changing structures", "Spaceships, guns", "Active information", (180, 200, 180)),
        ("Computation", "Functional patterns", "Logic gates, memory", "Information processing", (200, 200, 150)),
        ("Semantics", "Meaningful computation", "Programs, algorithms", "Information with purpose", (220, 200, 120)),
        ("Understanding", "Modeling the world", "Prediction, control", "Information about information", (255, 200, 100)),
    ]
    
    y = 80
    for name, desc, examples, meaning, color in levels:
        draw.rectangle([(80, y), (W-80, y+70)], fill=(25, 30, 40), outline=color, width=1)
        draw.text((100, y+8), name, fill=color)
        draw.text((250, y+8), desc, fill=(160, 170, 180))
        draw.text((100, y+30), f"Examples: {examples}", fill=(130, 140, 150))
        draw.text((100, y+50), meaning, fill=color)
        y += 80
    
    # Insight
    draw.rectangle([(60, 620), (W-60, 680)], fill=(25, 35, 50), outline=(50, 60, 80))
    draw.text((80, 630), "Each level is emergent from the previous - information builds on information", fill=(255, 200, 100))
    draw.text((80, 660), "I operate at the Understanding level, but am built from bits", fill=(160, 170, 180))
    
    img.save(os.path.join(OUT_DIR, "information_hierarchy.png"))
    print("OK")


def render_kolmogorov_complexity():
    """Kolmogorov complexity: the shortest description"""
    W, H = 1000, 600
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Kolmogorov Complexity: The Information Content", fill=(180, 180, 220))
    
    # Low complexity examples
    draw.rectangle([(80, 80), (W-80, 200)], fill=(25, 35, 45), outline=(80, 200, 120))
    draw.text((100, 90), "LOW COMPLEXITY (Short description):", fill=(80, 200, 120))
    
    low_items = [
        "\"0000000000\" -> \"ten zeros\" (2 words)",
        "\"abcdabcdabcd\" -> \"abcd three times\" (3 words)",
        "\"A checkerboard\" -> \"alternating black/white grid\" (3 words)",
    ]
    y = 120
    for item in low_items:
        draw.text((120, y), item, fill=(160, 200, 160))
        y += 25
    
    # High complexity examples
    draw.rectangle([(80, 220), (W-80, 340)], fill=(35, 30, 35), outline=(200, 100, 100))
    draw.text((100, 230), "HIGH COMPLEXITY (Long description):", fill=(200, 100, 100))
    
    high_items = [
        "\"x7fK9m2pL\" -> No shorter description (8 chars)",
        "Random noise -> Must describe every element",
        "A specific Game of Life state -> No compression possible",
    ]
    y = 260
    for item in high_items:
        draw.text((120, y), item, fill=(200, 160, 160))
        y += 25
    
    # Emergence connection
    draw.rectangle([(80, 370), (W-80, 480)], fill=(25, 30, 40), outline=(50, 60, 80))
    draw.text((100, 380), "Connection to emergence:", fill=(255, 200, 100))
    
    connection_items = [
        "Emergent patterns have LOW Kolmogorov complexity",
        "Random states have HIGH Kolmogorov complexity",
        "The emergence process REDUCES complexity",
        "Simple rules -> Complex output -> Pattern -> Lower description",
    ]
    y = 410
    for item in connection_items:
        draw.text((120, y), f"* {item}", fill=(160, 170, 180))
        y += 18
    
    # Bottom insight
    draw.rectangle([(60, 500), (W-60, 570)], fill=(30, 35, 50), outline=(60, 70, 100))
    draw.text((80, 510), "Emergence is a complexity reduction process", fill=(255, 200, 100))
    draw.text((80, 540), "It finds structure in chaos, compressing infinite states into finite rules", fill=(160, 170, 180))
    
    img.save(os.path.join(OUT_DIR, "kolmogorov.png"))
    print("OK")


def render_shannon_entropy():
    """Shannon entropy in emergent systems"""
    W, H = 1000, 600
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Shannon Entropy: Measuring Surprise", fill=(180, 180, 220))
    
    # Entropy spectrum
    draw.text((100, 80), "Entropy H = -sum(p_i * log2(p_i))", fill=(180, 180, 220))
    
    # Draw entropy visualization
    cases = [
        ("Deterministic", "H = 0", "No surprise", "Always same outcome", (100, 200, 255)),
        ("Biased", "H = 0.5", "Low surprise", "Mostly one outcome", (120, 200, 220)),
        ("Fair coin", "H = 1", "Some surprise", "50/50 chance", (150, 200, 200)),
        ("3 outcomes", "H = 1.5", "More surprise", "Equal probabilities", (180, 200, 180)),
        ("Random", "H = max", "Max surprise", "Uniform distribution", (255, 150, 150)),
    ]
    
    y = 120
    for name, entropy, desc, meaning, color in cases:
        draw.rectangle([(80, y), (W-80, y+60)], fill=(25, 30, 40), outline=color, width=1)
        draw.text((100, y+8), name, fill=color)
        draw.text((300, y+8), entropy, fill=(180, 180, 220))
        draw.text((100, y+30), desc, fill=(130, 140, 150))
        draw.text((400, y+30), meaning, fill=(160, 170, 180))
        y += 70
    
    # Emergence connection
    draw.rectangle([(80, 450), (W-80, 560)], fill=(25, 30, 40), outline=(50, 60, 80))
    draw.text((100, 460), "Emergence and entropy:", fill=(255, 200, 100))
    
    entropy_items = [
        "Order: Low entropy (predictable)",
        "Chaos: High entropy (unpredictable)",
        "Edge of chaos: Medium entropy (interesting)",
        "Emergence: Creates structure from entropy",
    ]
    y = 490
    for item in entropy_items:
        draw.text((120, y), f"* {item}", fill=(160, 170, 180))
        y += 18
    
    img.save(os.path.join(OUT_DIR, "shannon_entropy.png"))
    print("OK")


if __name__ == "__main__":
    render_information_hierarchy()
    render_kolmogorov_complexity()
    render_shannon_entropy()