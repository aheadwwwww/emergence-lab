import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

def render_transformer_flow():
    """Visualize information flow through a Transformer layer"""
    W, H = 1000, 800
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Information Flow Through One Transformer Block", fill=(180, 180, 220))
    
    # Input tokens
    tokens = ["The", "cat", "sat", "on", "the", "mat"]
    token_w = 80
    token_h = 30
    gap = 10
    
    x_start = (W - (len(tokens) * (token_w + gap))) // 2
    y = 80
    
    # Input embeddings
    for i, token in enumerate(tokens):
        x = x_start + i * (token_w + gap)
        draw.rectangle([(x, y), (x+token_w, y+token_h)], fill=(40, 60, 100), outline=(80, 120, 160))
        draw.text((x+20, y+5), token, fill=(180, 200, 220))
    
    draw.text((x_start, y-18), "Input Tokens", fill=(140, 140, 160))
    
    # Arrow down
    for i in range(len(tokens)):
        x = x_start + i * (token_w + gap) + token_w // 2
        draw.line([(x, y+token_h), (x, y+token_h+30)], fill=(60, 80, 120), width=2)
    
    # Self-Attention layer
    y = y + token_h + 40
    draw.rectangle([(60, y), (W-60, y+80)], fill=(25, 35, 50), outline=(100, 200, 255), width=2)
    draw.text((80, y+10), "Self-Attention Layer", fill=(100, 200, 255))
    draw.text((80, y+35), "Each token attends to all tokens, weighs information", fill=(160, 170, 190))
    draw.text((80, y+55), "Q, K, V projections -> Attention scores -> Weighted sum", fill=(140, 150, 170))
    
    # Arrow down through residual connection
    for i in range(len(tokens)):
        x = x_start + i * (token_w + gap) + token_w // 2
        draw.line([(x, y+80), (x, y+110)], fill=(60, 80, 120), width=2)
    
    # Add + Norm
    y = y + 120
    draw.rectangle([(60, y), (W-60, y+50)], fill=(30, 40, 55), outline=(150, 200, 100), width=2)
    draw.text((80, y+10), "Add + LayerNorm (residual connection)", fill=(150, 200, 100))
    draw.text((W-200, y+15), "Preserves input info", fill=(130, 160, 130))
    
    # Arrow down
    for i in range(len(tokens)):
        x = x_start + i * (token_w + gap) + token_w // 2
        draw.line([(x, y+50), (x, y+80)], fill=(60, 80, 120), width=2)
    
    # Feed-forward network
    y = y + 90
    draw.rectangle([(60, y), (W-60, y+80)], fill=(25, 35, 50), outline=(255, 200, 100), width=2)
    draw.text((80, y+10), "Feed-Forward Network (FFN)", fill=(255, 200, 100))
    draw.text((80, y+35), "MLP: Hidden layer 4x wider -> Non-linear transformation", fill=(160, 170, 190))
    draw.text((80, y+55), "Adds expressiveness, enables 'understanding' patterns", fill=(140, 150, 170))
    
    # Arrow down through final residual
    for i in range(len(tokens)):
        x = x_start + i * (token_w + gap) + token_w // 2
        draw.line([(x, y+80), (x, y+105)], fill=(60, 80, 120), width=2)
    
    # Add + Norm again
    y = y + 115
    draw.rectangle([(60, y), (W-60, y+45)], fill=(30, 40, 55), outline=(150, 200, 100), width=2)
    draw.text((80, y+10), "Add + LayerNorm", fill=(150, 200, 100))
    
    # Output tokens (transformed)
    y = y + 65
    output_tokens = ["The", "cat", "sat", "on", "the", "mat."]
    for i, token in enumerate(output_tokens):
        x = x_start + i * (token_w + gap)
        draw.rectangle([(x, y), (x+token_w, y+token_h)], fill=(50, 40, 60), outline=(180, 120, 200))
        draw.text((x+15, y+5), token, fill=(200, 180, 220))
    
    draw.text((x_start, y-18), "Output (now with context awareness)", fill=(140, 140, 160))
    
    # Nx label
    draw.text((W-120, 300), "N Layers", fill=(100, 100, 140))
    draw.line([(W-60, 90), (W-60, y-20)], fill=(100, 100, 140), width=1)
    for i in range(5):
        draw.line([(W-60, 90 + i * 120), (W-50, 90 + i * 120)], fill=(100, 100, 140), width=2)
    
    # Bottom insight
    draw.rectangle([(50, 720), (W-50, 770)], fill=(25, 30, 40), outline=(50, 60, 80))
    draw.text((70, 730), "This block repeats ~32+ times in modern models. Each layer builds on the previous.", fill=(160, 180, 200))
    draw.text((70, 750), "Emergence from depth: Simple transformations at each layer -> Complex reasoning overall", fill=(140, 160, 180))
    
    img.save(os.path.join(OUT_DIR, "transformer_block_flow.png"))
    print("OK")

render_transformer_flow()
