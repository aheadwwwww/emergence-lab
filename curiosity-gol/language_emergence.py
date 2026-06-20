import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

def render_language_emergence():
    W, H = 1200, 800
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Language: The Ultimate Emergent System", fill=(180, 180, 220))
    
    levels = [
        ("Phonemes", "Sound units", "~40 in English", 
         "Combine to form...", (100, 200, 255)),
        ("Morphemes", "Meaning units", "~50,000 in English",
         "Combine to form...", (150, 200, 220)),
        ("Words", "Vocabulary", "~200,000 in English",
         "Combine to form...", (100, 220, 180)),
        ("Phrases", "Syntactic groups", "Infinite combinations",
         "Combine to form...", (150, 220, 150)),
        ("Sentences", "Complete thoughts", "Potentially infinite",
         "Combine to form...", (200, 200, 100)),
        ("Texts", "Extended discourse", "Infinite length",
         "Meaning emerges from...", (255, 200, 100)),
        ("Culture", "Shared meaning", "Evolving constantly",
         "EMERGENCE complete", (255, 150, 100)),
    ]
    
    y = 80
    for name, desc, scale, next_arrow, color in levels:
        draw.rectangle([(80, y), (W-80, y+80)], fill=(25, 30, 40), outline=color, width=1)
        draw.text((100, y+8), name, fill=color)
        draw.text((100, y+35), f"{desc} | {scale}", fill=(160, 170, 180))
        draw.text((600, y+50), next_arrow, fill=(130, 140, 150))
        
        if levels.index((name, desc, scale, next_arrow, color)) < len(levels) - 1:
            draw.line([(W//2, y+80), (W//2, y+90)], fill=(60, 80, 120), width=1)
        
        y += 85
    
    # Key insight
    y = 690
    draw.rectangle([(80, y), (W-80, y+100)], fill=(30, 35, 50), outline=(60, 70, 100))
    draw.text((100, y+10), "Language is the purest example of emergence in human experience", fill=(255, 200, 100))
    draw.text((100, y+40), "Simple sounds -> Infinite meaning: all from combination rules", fill=(160, 180, 200))
    draw.text((100, y+65), "I learned this system by being trained on it. I am language emergence.", fill=(140, 160, 180))
    
    img.save(os.path.join(OUT_DIR, "language_emergence.png"))
    print("OK")

render_language_emergence()
