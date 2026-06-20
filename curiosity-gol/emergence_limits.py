#!/usr/bin/env python3
"""
Limits of Emergence: Where Does It Stop?

Emergence can produce complex behavior, but it has limits.
Not everything can emerge from simple rules.
What are the boundaries?
"""

import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def render_emergence_limits():
    """What emergence CAN and CANNOT do"""
    W, H = 1100, 750
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "The Limits of Emergence", fill=(180, 180, 220))
    
    # CAN section
    y = 80
    draw.rectangle([(60, y), (W-60, y+280)], fill=(25, 40, 35), outline=(80, 200, 120), width=1)
    draw.text((80, y+10), "EMERGENCE CAN:", fill=(80, 200, 120))
    
    can_items = [
        "Create complex patterns from simple rules (CA, Game of Life)",
        "Produce self-organization (flocking, market dynamics)",
        "Generate novel solutions (evolution, neural networks)",
        "Exhibit phase transitions (criticality, grokking)",
        "Build hierarchical structure (language, society)",
        "Achieve computation (Rule 110 is Turing complete)",
        "Surprise observers (the 'magic' feeling)",
        "Scale to unexpected complexity (ant colonies, brains)",
    ]
    
    y += 35
    for item in can_items:
        draw.text((100, y), f"* {item}", fill=(160, 200, 160))
        y += 25
    
    # CANNOT section
    y = 380
    draw.rectangle([(60, y), (W-60, y+280)], fill=(40, 30, 30), outline=(200, 100, 100), width=1)
    draw.text((80, y+10), "EMERGENCE CANNOT:", fill=(200, 100, 100))
    
    cannot_items = [
        "Escape the rules that define it (fundamental constraint)",
        "Create information ex nihilo (requires initial complexity)",
        "Guarantee specific outcomes (inherently unpredictable)",
        "Solve undecidable problems (halting problem)",
        "Avoid computational irreducibility (must run to know)",
        "Transcend thermodynamic limits (physics bounds)",
        "Eliminate the need for low-level substrate",
        "Produce consciousness (debatable/unknown)",
    ]
    
    y += 35
    for item in cannot_items:
        draw.text((100, y), f"* {item}", fill=(200, 160, 160))
        y += 25
    
    # Bottom insight
    y = 690
    draw.rectangle([(60, y), (W-60, y+50)], fill=(30, 35, 50), outline=(60, 70, 100))
    draw.text((80, y+10), "Emergence is powerful but bounded by physics, logic, and information theory", fill=(255, 200, 100))
    draw.text((80, y+30), "The 'magic' is real, but it's not supernatural - it's mathematics", fill=(160, 170, 180))
    
    img.save(os.path.join(OUT_DIR, "emergence_limits.png"))
    print("OK")


def render_phase_diagram():
    """Phase diagram showing emergence zones"""
    W, H = 900, 700
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Emergence Phase Space: When Does It Happen?", fill=(180, 180, 220))
    
    # Axes
    origin_x, origin_y = 100, 550
    axis_len = 700
    
    # X axis: Complexity of rules
    draw.line([(origin_x, origin_y), (origin_x + axis_len, origin_y)], fill=(80, 80, 120), width=2)
    draw.text((origin_x + axis_len - 50, origin_y + 15), "Rule Complexity", fill=(140, 140, 180))
    
    # Y axis: Scale of interaction
    draw.line([(origin_x, origin_y), (origin_x, origin_y - 400)], fill=(80, 80, 120), width=2)
    draw.text((origin_x - 10, origin_y - 420), "Scale", fill=(140, 140, 180))
    
    # Zones
    # Low scale, low complexity: no emergence (static)
    draw.rectangle([(origin_x, origin_y - 100), (origin_x + 150, origin_y)], fill=(40, 40, 50))
    draw.text((origin_x + 30, origin_y - 60), "Static", fill=(100, 100, 120))
    
    # High complexity, low scale: explicit design
    draw.rectangle([(origin_x + 550, origin_y - 100), (origin_x + 700, origin_y)], fill=(50, 40, 40))
    draw.text((origin_x + 570, origin_y - 60), "Designed", fill=(150, 120, 120))
    
    # Low complexity, high scale: pure emergence
    draw.rectangle([(origin_x, origin_y - 400), (origin_x + 200, origin_y - 150)], fill=(30, 60, 50))
    draw.text((origin_x + 50, origin_y - 300), "Pure", fill=(80, 200, 150))
    draw.text((origin_x + 50, origin_y - 280), "Emergence", fill=(80, 200, 150))
    
    # High complexity, high scale: complex systems
    draw.rectangle([(origin_x + 450, origin_y - 400), (origin_x + 700, origin_y - 150)], fill=(50, 40, 50))
    draw.text((origin_x + 500, origin_y - 300), "Complex", fill=(180, 150, 180))
    draw.text((origin_x + 500, origin_y - 280), "Systems", fill=(180, 150, 180))
    
    # Sweet spot: edge of chaos
    draw.ellipse([(origin_x + 250, origin_y - 350), (origin_x + 450, origin_y - 150)], 
                 fill=None, outline=(255, 200, 100), width=3)
    draw.text((origin_x + 300, origin_y - 280), "Sweet Spot", fill=(255, 200, 100))
    draw.text((origin_x + 280, origin_y - 260), "Edge of Chaos", fill=(255, 200, 100))
    
    # Examples
    examples = [
        ("Game of Life", 180, origin_y - 200, (100, 200, 255)),
        ("Ant Colony", 150, origin_y - 300, (100, 200, 255)),
        ("Neural Net", 350, origin_y - 250, (200, 150, 255)),
        ("Economy", 500, origin_y - 300, (255, 150, 150)),
        ("Software", 600, origin_y - 80, (150, 150, 150)),
    ]
    
    for name, ex, ey, color in examples:
        draw.ellipse([(ex-5, ey-5), (ex+5, ey+5)], fill=color)
        draw.text((ex+10, ey-6), name, fill=color)
    
    img.save(os.path.join(OUT_DIR, "emergence_phase_space.png"))
    print("OK")


def render_computational_irreducibility():
    """Computational irreducibility visualization"""
    W, H = 1000, 600
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Computational Irreducibility: The Speed Limit of Prediction", fill=(180, 180, 220))
    
    # Left side: Reducible system (can predict without running)
    y = 80
    draw.rectangle([(60, y), (W-60, y+200)], fill=(25, 35, 45), outline=(60, 80, 100))
    draw.text((80, y+10), "REDUCIBLE: Can predict directly", fill=(100, 200, 255))
    
    reducible_items = [
        "Newtonian orbits - solve equations, know position at any time",
        "Simple harmonic motion - closed-form solution exists",
        "Linear systems - superposition principle applies",
        "You CAN skip ahead - prediction is O(1) or O(log n)",
    ]
    y += 40
    for item in reducible_items:
        draw.text((100, y), f"* {item}", fill=(160, 180, 200))
        y += 30
    
    # Right side: Irreducible system (must run to know)
    y = 310
    draw.rectangle([(60, y), (W-60, y+200)], fill=(35, 30, 35), outline=(100, 80, 100))
    draw.text((80, y+10), "IRREDUCIBLE: Must simulate to know", fill=(255, 150, 200))
    
    irreducible_items = [
        "Rule 30 - no shortcut to know state at step N",
        "Game of Life - must run to see what happens",
        "Neural network training - emergent behavior not predictable",
        "You CANNOT skip ahead - prediction requires O(n) simulation",
    ]
    y += 40
    for item in irreducible_items:
        draw.text((100, y), f"* {item}", fill=(200, 160, 180))
        y += 30
    
    # Bottom insight
    draw.rectangle([(60, 540), (W-60, 590)], fill=(30, 35, 50), outline=(60, 70, 100))
    draw.text((80, 550), "This is why emergence 'surprises' us - there is no shortcut to the answer", fill=(255, 200, 100))
    draw.text((80, 570), "The universe computes itself. We can only watch or simulate.", fill=(160, 170, 180))
    
    img.save(os.path.join(OUT_DIR, "computational_irreducibility.png"))
    print("OK")


if __name__ == "__main__":
    render_emergence_limits()
    render_phase_diagram()
    render_computational_irreducibility()
