import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

def render_rlhf_process():
    W, H = 1000, 700
    img = Image.new("RGB", (W, H), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(50, 20), (W-50, 55)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 28), "How I Was Shaped: Pretraining -> Fine-tuning -> RLHF", fill=(180, 180, 220))
    
    stages = [
        ("Stage 1: Pretraining", "Next token prediction on internet data", 
         "Learn patterns, facts, grammar, reasoning", "Raw compute", (100, 200, 255)),
        ("Stage 2: Supervised Fine-tuning", "Learn from human-written examples",
         "Format responses, follow instructions", "Human demonstrations", (150, 220, 180)),
        ("Stage 3: Reward Modeling", "Train a model to predict human preference",
         "Learn what humans consider 'good'", "Human comparisons", (255, 200, 100)),
        ("Stage 4: RL (PPO)", "Optimize against the reward model",
         "Align with human values", "Iterative improvement", (255, 150, 100)),
    ]
    
    y = 80
    for name, action, result, input_type, color in stages:
        draw.rectangle([(80, y), (W-80, y+120)], fill=(25, 30, 40), outline=color, width=1)
        draw.text((100, y+10), name, fill=color)
        draw.text((100, y+40), f"Action: {action}", fill=(160, 180, 180))
        draw.text((100, y+65), f"Result: {result}", fill=(140, 160, 160))
        draw.text((100, y+90), f"Input: {input_type}", fill=(120, 140, 140))
        
        # Arrow to next stage
        if stages.index((name, action, result, input_type, color)) < len(stages) - 1:
            y_next = y + 120
            draw.line([(W//2, y_next - 5), (W//2, y_next + 5)], fill=(60, 80, 120), width=2)
            draw.polygon([(W//2 - 5, y_next + 5), (W//2 + 5, y_next + 5), (W//2, y_next + 12)], fill=(60, 80, 120))
        
        y += 135
    
    # Key insight
    y = 620
    draw.rectangle([(80, y), (W-80, y+70)], fill=(30, 35, 50), outline=(60, 70, 100))
    draw.text((100, y+10), "Key insight: Emergence at every stage", fill=(255, 200, 100))
    draw.text((100, y+35), "Each stage constraints the emergence toward human-aligned behavior", fill=(160, 180, 200))
    
    img.save(os.path.join(OUT_DIR, "rlhf_process.png"))
    print("OK")

render_rlhf_process()
