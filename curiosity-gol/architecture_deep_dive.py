#!/usr/bin/env python3
"""
Emergent Intelligence: How I Actually Work Under the Hood

A deeper look at the architecture that enables my emergence.
"""

import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

def render_mixture_of_experts():
    """MoE architecture visualization"""
    W, H = 1200, 600
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Mixture of Experts: Specialized Sub-networks", fill=(180, 180, 220))
    
    # Input
    draw.rectangle([(500, 80), (700, 130)], fill=(25, 40, 55), outline=(100, 200, 255), width=2)
    draw.text((550, 95), "INPUT TOKEN", fill=(100, 200, 255))
    
    # Router
    draw.rectangle([(500, 160), (700, 210)], fill=(35, 35, 50), outline=(255, 200, 100), width=2)
    draw.text((545, 175), "ROUTER (GATE)", fill=(255, 200, 100))
    
    # Arrow to router
    draw.line([(600, 130), (600, 160)], fill=(60, 80, 120), width=2)
    
    # Experts
    experts = [
        ("Expert A: Syntax", 100, 280, (100, 200, 255)),
        ("Expert B: Semantics", 320, 280, (150, 200, 200)),
        ("Expert C: World Knowledge", 540, 280, (200, 200, 150)),
        ("Expert D: Math/Logic", 760, 280, (255, 180, 100)),
        ("Expert E: Creativity", 980, 280, (200, 150, 255)),
    ]
    
    for name, ex, ey, color in experts:
        draw.rectangle([(ex, ey), (ex+140, ey+60)], fill=(25, 30, 40), outline=color, width=1)
        draw.text((ex+15, ey+15), name, fill=color)
    
    # Router connections
    for name, ex, ey, color in experts:
        draw.line([(600, 210), (ex+70, ey)], fill=(40, 50, 70), width=1)
    
    # Output
    draw.rectangle([(500, 420), (700, 470)], fill=(25, 55, 40), outline=(100, 255, 150), width=2)
    draw.text((540, 435), "OUTPUT", fill=(100, 255, 150))
    
    # Expert to output connections
    for name, ex, ey, color in experts:
        draw.line([(ex+70, ey+60), (600, 420)], fill=(40, 50, 70), width=1)
    
    # Insight
    draw.rectangle([(60, 520), (W-60, 580)], fill=(25, 35, 50), outline=(50, 60, 80))
    draw.text((80, 530), "MoE: Only relevant experts activate per token. Sparse computation, rich capability.", fill=(255, 200, 100))
    draw.text((80, 560), "Emergent specialization: experts develop distinct skills through training", fill=(160, 170, 180))
    
    img.save(os.path.join(OUT_DIR, "mixture_of_experts.png"))
    print("OK")


def render_residual_stream():
    """How information flows through residual connections"""
    W, H = 800, 700
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Residual Stream: The Highway of Information", fill=(180, 180, 220))
    
    # Main residual stream
    layers = 8
    y_start = 80
    layer_h = 40
    gap = 30
    
    for i in range(layers):
        y = y_start + i * (layer_h + gap)
        
        # Main stream (residual)
        draw.rectangle([(100, y), (700, y+layer_h)], fill=(25, 35, 50), outline=(60, 80, 120), width=1)
        draw.text((120, y+10), f"Layer {i+1}", fill=(140, 140, 160))
        
        # Attention sub-layer
        draw.rectangle([(100, y-15), (300, y-2)], fill=(25, 40, 55), outline=(100, 200, 255), width=1)
        draw.text((120, y-13), "Self-Attention", fill=(100, 200, 255))
        
        # FFN sub-layer
        draw.rectangle([(350, y-15), (550, y-2)], fill=(35, 35, 50), outline=(255, 200, 100), width=1)
        draw.text((370, y-13), "FFN", fill=(255, 200, 100))
        
        # Add & Norm
        draw.rectangle([(600, y-15), (700, y-2)], fill=(25, 40, 40), outline=(100, 200, 150), width=1)
        draw.text((610, y-13), "Norm", fill=(100, 200, 150))
        
        # Arrows showing residual flow
        if i < layers - 1:
            draw.line([(400, y+layer_h), (400, y+layer_h+gap)], fill=(60, 80, 120), width=1)
    
    # Input label
    draw.text((100, y_start-20), "Input", fill=(180, 180, 220))
    draw.text((700, y_start-20), "Output", fill=(180, 180, 220))
    draw.line([(700, y_start), (720, y_start)], fill=(180, 180, 220), width=1)
    draw.line([(700, y_start+layers*(layer_h+gap)), (720, y_start+layers*(layer_h+gap))], fill=(180, 180, 220), width=1)
    
    # Insight
    y = y_start + layers * (layer_h + gap) + 20
    draw.rectangle([(60, y), (W-60, y+80)], fill=(30, 35, 50), outline=(60, 70, 100))
    draw.text((80, y+10), "Residual connections allow gradient flow during training", fill=(255, 200, 100))
    draw.text((80, y+35), "They also enable the model to 'remember' early layer information", fill=(160, 170, 180))
    draw.text((80, y+60), "Each layer adds refinement, not replacement", fill=(140, 150, 160))
    
    img.save(os.path.join(OUT_DIR, "residual_stream.png"))
    print("OK")


if __name__ == "__main__":
    render_mixture_of_experts()
    render_residual_stream()