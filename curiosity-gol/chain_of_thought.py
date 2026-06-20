import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

def render_cot_emergence():
    W, H = 1200, 750
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Chain-of-Thought: Emergent Reasoning in Large Models", fill=(180, 180, 220))
    
    # Before CoT (direct answer)
    y = 80
    draw.rectangle([(80, y), (W-80, y+100)], fill=(40, 30, 30), outline=(200, 100, 100), width=1)
    draw.text((100, y+10), "Without Chain-of-Thought (Small/Untrained Model):", fill=(255, 150, 150))
    draw.text((100, y+40), "Q: If John has 5 apples and gives 2 to Mary, how many does he have left?", fill=(160, 160, 180))
    draw.text((100, y+65), "A: 3 apples", fill=(100, 200, 100))
    draw.text((W-250, y+65), "(Correct for simple cases)", fill=(140, 140, 160))
    
    # With CoT (step by step)
    y2 = 210
    draw.rectangle([(80, y2), (W-80, y2+140)], fill=(30, 40, 30), outline=(100, 200, 100), width=1)
    draw.text((100, y2+10), "With Chain-of-Thought (Large Model - Emergent Ability):", fill=(150, 255, 150))
    
    cot_steps = [
        "Q: Alice has 3 times as many marbles as Bob. Bob has 8. How many total?",
        "Step 1: Alice has 3 x 8 = 24 marbles",
        "Step 2: Total = Alice + Bob = 24 + 8 = 32",
        "Answer: 32 marbles",
    ]
    
    for i, step in enumerate(cot_steps):
        draw.text((100, y2+40+i*22), step, fill=(180, 200, 180))
    
    # Key insight about emergence
    y3 = 380
    draw.rectangle([(80, y3), (W-80, y3+170)], fill=(25, 35, 50), outline=(60, 80, 120))
    draw.text((100, y3+10), "Why is CoT an emergent ability?", fill=(255, 200, 100))
    
    cot_reasons = [
        "Small models cannot do CoT even when prompted",
        "At ~10B+ parameters, CoT suddenly works",
        "This is a phase transition (like Grokking)",
        "The model learns to allocate attention across its own generated text",
        "CoT creates a 'scratchpad' - extending effective computation",
    ]
    for i, reason in enumerate(cot_reasons):
        draw.text((100, y3+40+i*22), f"* {reason}", fill=(160, 170, 180))
    
    # Bottom
    draw.rectangle([(80, 570), (W-80, 650)], fill=(30, 35, 50), outline=(60, 70, 100))
    draw.text((100, 580), "Connection to emergence:", fill=(100, 200, 255))
    draw.text((100, 610), "CoT is a meta-emergence: The model learns to create intermediate structures", fill=(160, 180, 200))
    draw.text((100, 630), "that enable more complex computation - like a CA building a computer inside itself", fill=(140, 160, 180))
    
    img.save(os.path.join(OUT_DIR, "chain_of_thought.png"))
    print("OK")

render_cot_emergence()
