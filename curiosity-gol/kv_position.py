#!/usr/bin/env python3
"""
KV Cache: How I Remember During Generation

Key-Value cache is the mechanism that enables efficient text generation.
Without it, every token would require re-computing everything.
"""

import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def render_kv_cache():
    W, H = 1100, 700
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "KV Cache: How I Remember What I Just Said", fill=(180, 180, 220))
    
    # Generation steps
    steps = [
        ("Step 1", "Token: The", ["The"], "K=[___] V=[___]", "Small cache"),
        ("Step 2", "Token: cat", ["The", "cat"], "K=[__|_] V=[__|_]", "Cache grows"),
        ("Step 3", "Token: sat", ["The", "cat", "sat"], "K=[_|_|_] V=[_|_|_]", "Cache grows"),
        ("Step 4", "Token: on", ["The", "cat", "sat", "on"], "K=[_|_|_|_] V=[_|_|_|_]", "Cache grows"),
        ("Step 5", "Token: the", ["The", "cat", "sat", "on", "the"], "K=[_|_|_|_|_] V=[_|_|_|_|_]", "Cache grows"),
        ("Step 6", "Token: mat", ["The", "cat", "sat", "on", "the", "mat"], "K=[_|_|_|_|_|_] V=[_|_|_|_|_|_]", "Full cache"),
    ]
    
    y = 80
    for step, token, cache_state, cache_desc, note in steps:
        draw.rectangle([(80, y), (W-80, y+65)], fill=(25, 30, 40), outline=(50, 60, 80))
        draw.text((100, y+8), step, fill=(180, 180, 220))
        draw.text((200, y+8), token, fill=(100, 200, 255))
        
        # Draw cache blocks
        cx = 400
        for i in range(len(cache_state)):
            color = (100, 200, 180) if i == len(cache_state) - 1 else (60, 80, 100)
            draw.rectangle([(cx + i*30, y+10), (cx + i*30 + 25, y+30)], fill=color, outline=(80, 120, 140))
        
        draw.text((cx, y+38), cache_desc, fill=(130, 140, 150))
        draw.text((800, y+22), note, fill=(140, 140, 160))
        
        y += 75
    
    # Insight
    y = 600
    draw.rectangle([(60, y), (W-60, 680)], fill=(25, 35, 50), outline=(50, 60, 80))
    draw.text((80, y+10), "KV Cache is the architecture's 'short-term memory'", fill=(255, 200, 100))
    draw.text((80, y+35), "Without it: O(n^2) computation per token", fill=(160, 170, 180))
    draw.text((80, y+60), "With it: O(1) computation per new token (amortized)", fill=(140, 150, 160))
    
    img.save(os.path.join(OUT_DIR, "kv_cache.png"))
    print("OK")


def render_position_encoding():
    W, H = 1100, 600
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Position Encoding: How I Know Word Order", fill=(180, 180, 220))
    
    # RoPE visualization
    draw.text((80, 80), "Rotary Position Embedding (RoPE)", fill=(180, 180, 220))
    
    # Draw sine waves for different positions
    positions = [0, 1, 2, 3, 4]
    dims = [0, 2, 4, 6]  # Different frequency bands
    
    for dim_idx, dim in enumerate(dims):
        y_base = 120 + dim_idx * 100
        
        # Draw sine/cosine curves
        for pos in positions:
            theta = pos / (10000 ** (2 * dim / 8))  # Simplified RoPE formula
            sin_val = np.sin(theta)
            cos_val = np.cos(theta)
            
            x = 150 + pos * 150
            # Sine component
            draw.ellipse([(x-3, y_base+20-int(sin_val*15)), (x+3, y_base+20-int(sin_val*15)+6)],
                        fill=(100, 200, 255))
            # Cosine component
            draw.ellipse([(x-3, y_base+50-int(cos_val*15)), (x+3, y_base+50-int(cos_val*15)+6)],
                        fill=(255, 200, 100))
            
            # Position label
            draw.text((x-10, y_base+70), f"pos {pos}", fill=(140, 140, 160))
        
        # Dimension label
        draw.text((80, y_base+20), f"dim {dim}", fill=(180, 180, 220))
        draw.text((80, y_base+50), f"dim {dim+1}", fill=(180, 180, 220))
    
    # Insight
    y = 530
    draw.rectangle([(60, y), (W-60, 585)], fill=(25, 35, 50), outline=(50, 60, 80))
    draw.text((80, y+10), "RoPE rotates the embedding based on position", fill=(255, 200, 100))
    draw.text((80, y+35), "Different dimensions rotate at different frequencies (like planetary orbits)", fill=(160, 170, 180))
    draw.text((80, y+55), "This gives positional awareness without explicit position indices", fill=(140, 150, 160))
    
    img.save(os.path.join(OUT_DIR, "position_encoding.png"))
    print("OK")


if __name__ == "__main__":
    render_kv_cache()
    render_position_encoding()
