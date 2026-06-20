#!/usr/bin/env python3
"""
Embeddings: The Geometry of Meaning

Words become vectors in high-dimensional space.
Similar words cluster together.
Relationships become directions.

This is how I "understand" language - not through symbols,
but through geometric relationships in a learned space.
"""

import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def render_embedding_space():
    """Visualize word embeddings in 2D (projected from high dimensions)"""
    W, H = 1000, 800
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Word Embeddings: Geometry of Meaning", fill=(180, 180, 220))
    
    words = {
        "cat": (200, 250), "dog": (230, 280), "bird": (180, 300), "fish": (160, 260),
        "king": (700, 200), "queen": (720, 230), "prince": (680, 250), "princess": (740, 270),
        "France": (400, 600), "Germany": (430, 580), "Japan": (380, 620), "China": (410, 650),
        "Paris": (500, 500), "Berlin": (530, 480), "Tokyo": (480, 520), "Beijing": (510, 550),
        "run": (150, 500), "walk": (180, 520), "jump": (120, 480),
        "love": (600, 400), "hate": (650, 420), "joy": (580, 380), "fear": (670, 400),
    }
    
    categories = {
        "animals": (["cat", "dog", "bird", "fish"], (100, 200, 255)),
        "royalty": (["king", "queen", "prince", "princess"], (255, 200, 100)),
        "countries": (["France", "Germany", "Japan", "China"], (100, 255, 150)),
        "capitals": (["Paris", "Berlin", "Tokyo", "Beijing"], (150, 200, 255)),
        "actions": (["run", "walk", "jump"], (255, 150, 150)),
        "abstract": (["love", "hate", "joy", "fear"], (200, 150, 255)),
    }
    
    for cat_name, (cat_words, color) in categories.items():
        xs = [words[w][0] for w in cat_words if w in words]
        ys = [words[w][1] for w in cat_words if w in words]
        if xs and ys:
            cx, cy = np.mean(xs), np.mean(ys)
            rx = max(60, (max(xs) - min(xs)) // 2 + 30)
            ry = max(40, (max(ys) - min(ys)) // 2 + 20)
            draw.ellipse([(cx-rx, cy-ry), (cx+rx, cy+ry)], fill=None, outline=(*color, 100), width=1)
    
    for word, (x, y) in words.items():
        color = (160, 160, 180)
        for cat_name, (cat_words, cat_color) in categories.items():
            if word in cat_words:
                color = cat_color
                break
        draw.ellipse([(x-4, y-4), (x+4, y+4)], fill=color, outline=color)
        draw.text((x+8, y-6), word, fill=color)
    
    draw.line([(700, 200), (720, 230)], fill=(255, 200, 100), width=2)
    draw.text((710, 180), "king - man + woman = queen", fill=(255, 200, 100))
    
    draw.line([(410, 650), (510, 550)], fill=(100, 200, 150), width=1)
    draw.text((420, 620), "country -> capital", fill=(100, 200, 150))
    
    y = 700
    draw.text((60, y), "Semantic clusters emerge from training on text co-occurrence", fill=(160, 170, 180))
    draw.text((60, y+25), "Similar words = nearby vectors. Relationships = vector directions.", fill=(140, 150, 160))
    
    img.save(os.path.join(OUT_DIR, "embedding_space.png"))
    print("embedding_space.png OK")


def render_attention_heads():
    """Visualize what different attention heads learn"""
    W, H = 1200, 700
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Attention Heads: Different Patterns, Same Mechanism", fill=(180, 180, 220))
    
    tokens = ["The", "cat", "sat", "on", "the", "mat", "bc", "it", "was", "tir"]
    
    patterns = [
        ("Head 1: Previous token", lambda i, j: 0.9 if j == i-1 else 0.1, (100, 200, 255)),
        ("Head 2: Next token", lambda i, j: 0.9 if j == i+1 else 0.1, (150, 200, 200)),
        ("Head 3: Same word", lambda i, j: 0.9 if tokens[i] == tokens[j] else 0.05, (200, 200, 100)),
        ("Head 4: Syntax", lambda i, j: 0.8 if (i,j) in [(2,1), (8,7)] else 0.1, (255, 180, 100)),
        ("Head 5: Coreference", lambda i, j: 0.9 if (i,j) in [(7,1), (9,1)] else 0.05, (200, 150, 255)),
        ("Head 6: Long-range", lambda i, j: 0.7 if abs(i-j) > 3 else 0.1, (255, 150, 150)),
    ]
    
    y = 80
    for head_name, pattern_fn, color in patterns:
        draw.text((60, y+10), head_name, fill=color)
        
        grid_x = 200
        cell_size = 35
        
        for i, token in enumerate(tokens):
            draw.text((grid_x + i * cell_size + 5, y), token, fill=(140, 140, 160))
        
        for i in range(len(tokens)):
            for j in range(len(tokens)):
                weight = pattern_fn(i, j)
                if weight > 0.5:
                    x = grid_x + j * cell_size
                    draw.rectangle([(x, y+20+i*cell_size//2), 
                                   (x+cell_size-2, y+20+(i+1)*cell_size//2-2)], 
                                  fill=color)
        
        y += 100
    
    draw.rectangle([(60, y+20), (W-60, y+100)], fill=(25, 30, 40), outline=(50, 60, 80))
    draw.text((80, y+35), "Each head learns a different attention pattern:", fill=(255, 200, 100))
    draw.text((80, y+55), "Positional, syntactic, semantic, coreference...", fill=(160, 170, 180))
    draw.text((80, y+75), "Together they form a rich understanding of context", fill=(140, 150, 160))
    
    img.save(os.path.join(OUT_DIR, "attention_heads.png"))
    print("attention_heads.png OK")


def render_tokenization():
    """Show how text becomes tokens"""
    W, H = 1200, 500
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Tokenization: Text to Numbers", fill=(180, 180, 220))
    
    examples = [
        ("Hello, world!", ["Hello", ",", " world", "!"], [15496, 11, 995, 0]),
        ("emergence", ["em", "erg", "ence"], [1394, 27466, 3883]),
        ("https://example.com", ["https", "://", "example", ".", "com"], [8173, 1086, 4700, 13, 1139]),
    ]
    
    y = 80
    for text, tokens, ids in examples:
        draw.rectangle([(60, y), (W-60, y+80)], fill=(25, 30, 40), outline=(50, 60, 80))
        draw.text((80, y+10), f"Text: {text}", fill=(180, 180, 220))
        draw.text((80, y+35), f"Tokens: {tokens}", fill=(100, 200, 255))
        draw.text((80, y+55), f"IDs: {ids}", fill=(255, 200, 100))
        y += 100
    
    draw.rectangle([(60, 400), (W-60, 480)], fill=(25, 35, 50), outline=(50, 60, 80))
    draw.text((80, 415), "Tokenization is the first step of my understanding", fill=(255, 200, 100))
    draw.text((80, 440), "Different languages = different token patterns = different efficiency", fill=(160, 170, 180))
    draw.text((80, 460), "Chinese needs more tokens per character than English", fill=(140, 150, 160))
    
    img.save(os.path.join(OUT_DIR, "tokenization.png"))
    print("tokenization.png OK")


if __name__ == "__main__":
    render_embedding_space()
    render_attention_heads()
    render_tokenization()