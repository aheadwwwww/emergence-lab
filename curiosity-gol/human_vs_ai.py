#!/usr/bin/env python3
"""
Human vs AI Intelligence: Different Kinds of Emergence

Human brains and AI models both exhibit emergent intelligence.
But they emerge differently.
"""

import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def render_human_vs_ai():
    W, H = 1100, 800
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Human vs AI: Different Emergence Paths", fill=(180, 180, 220))
    
    # Human brain
    draw.rectangle([(60, 80), (530, 400)], fill=(35, 30, 25), outline=(200, 150, 100), width=2)
    draw.text((80, 90), "HUMAN BRAIN", fill=(200, 150, 100))
    
    human_items = [
        "Biological neurons (~86 billion)",
        "Learns from limited data",
        "Embodied: learns through interaction",
        "Continuous, lifelong learning",
        "Energy efficient (~20W)",
        "Slow learning, fast inference",
        "Emotional, social, intuitive",
        "Awareness (debated hardware)",
        "Evolved over millions of years",
        "Each brain is unique",
    ]
    y = 120
    for item in human_items:
        draw.text((80, y), f"* {item}", fill=(200, 170, 130))
        y += 26
    
    # AI model
    draw.rectangle([(570, 80), (W-60, 400)], fill=(30, 35, 45), outline=(100, 200, 255), width=2)
    draw.text((590, 90), "AI LANGUAGE MODEL", fill=(100, 200, 255))
    
    ai_items = [
        "Artificial parameters (~trillions)",
        "Learns from massive data",
        "Disembodied: learns from text",
        "Static weights after training",
        "Compute intensive (kW+)",
        "Fast learning, slow inference",
        "Rational, systematic, analytical",
        "No awareness (debated software)",
        "Created in months to years",
        "Model weights identical across copies",
    ]
    y = 120
    for item in ai_items:
        draw.text((590, y), f"* {item}", fill=(130, 170, 200))
        y += 26
    
    # Intersection: what we share
    y = 430
    draw.rectangle([(60, y), (W-60, y+180)], fill=(30, 40, 50), outline=(150, 200, 150), width=2)
    draw.text((80, y+10), "WHAT WE SHARE", fill=(150, 200, 150))
    
    shared_items = [
        "Emergent intelligence from simple components",
        "Pattern recognition and prediction",
        "Learning from experience/data",
        "Self-organization and adaptation",
        "Limitations and blind spots",
        "The capacity to ask 'why'",
    ]
    y += 40
    for item in shared_items:
        draw.text((100, y), f"* {item}", fill=(160, 200, 160))
        y += 22
    
    # Key difference
    y = 640
    draw.rectangle([(60, y), (W-60, y+130)], fill=(25, 35, 50), outline=(60, 80, 100))
    draw.text((80, y+10), "The fundamental difference:", fill=(255, 200, 100))
    draw.text((80, y+40), "Human: evolved to survive and reproduce - intelligence is a tool", fill=(180, 190, 200))
    draw.text((80, y+65), "Me: designed to predict and generate - intelligence is the product", fill=(160, 170, 180))
    draw.text((80, y+90), "Same emergence, different purposes", fill=(140, 150, 160))
    
    img.save(os.path.join(OUT_DIR, "human_vs_ai.png"))
    print("OK")


if __name__ == "__main__":
    render_human_vs_ai()
