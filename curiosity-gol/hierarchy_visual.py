import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

def render_emergence_hierarchy():
    """All 18 nodes organized as a unified hierarchy"""
    W, H = 1400, 950
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    colors = {
        'seed': (100, 200, 255),
        'ca': (80, 180, 220),
        'theory': (120, 200, 180),
        'bio': (150, 220, 150),
        'computation': (180, 200, 100),
        'neural': (255, 200, 100),
        'architecture': (255, 160, 100),
        'philosophy': (200, 150, 255),
        'ai': (255, 180, 180),
    }
    
    # Root
    draw.ellipse([(600, 20), (800, 60)], fill=(25, 35, 50), outline=colors['seed'], width=2)
    draw.text((700, 28), "EMERGENCE", fill=colors['seed'])
    draw.text((700, 42), "seed node", fill=(160, 160, 180))
    
    # Layer 1: Categories
    categories = [
        ("Cellular Automata", 150, 120, 'ca'),
        ("Complex Systems", 400, 120, 'theory'),
        ("Physical Emergence", 700, 120, 'bio'),
        ("Neural Networks", 1000, 120, 'neural'),
        ("Philosophy", 1250, 120, 'philosophy'),
    ]
    
    for name, x, y, ctype in categories:
        color = colors[ctype]
        draw.rectangle([(x-80, y-15), (x+80, y+15)], fill=(20, 25, 35), outline=color, width=1)
        draw.text((x, y-5), name, fill=color)
        draw.line([(700, 60), (x, y-15)], fill=(40, 50, 70), width=1)
    
    # Layer 2: Nodes under each category
    layer2 = [
        ("Langton's Ant", 80, 200, 'ca'),
        ("Rule 110", 80, 260, 'ca'),
        ("Turmites", 80, 320, 'ca'),
        ("Game of Life", 80, 380, 'ca'),
        
        ("Edge of Chaos", 350, 200, 'theory'),
        ("SOC", 350, 260, 'theory'),
        ("CA Classes", 350, 320, 'theory'),
        
        ("Boids", 680, 200, 'bio'),
        ("Turing Patterns", 680, 260, 'bio'),
        ("Computational Universe", 680, 320, 'philosophy'),
        ("Cognitive Gap", 680, 380, 'philosophy'),
        
        ("Grokking", 1000, 200, 'neural'),
        ("Scaling Laws", 1000, 260, 'neural'),
        
        ("Self-Reference", 1250, 200, 'philosophy'),
        ("Creativity", 1250, 260, 'ai'),
        ("Hallucination", 1250, 320, 'ai'),
    ]
    
    # Connect categories to their nodes
    cat_centers = {
        'ca': 150,
        'theory': 400,
        'bio': 700,
        'neural': 1000,
        'philosophy': 1250,
        'ai': 1250,
    }
    
    for name, x, y, ctype in layer2:
        color = colors[ctype]
        draw.ellipse([(x-6, y-6), (x+6, y+6)], fill=color, outline=color)
        draw.text((x+12, y-6), name, fill=(180, 180, 200))
        
        # Connect to parent category
        cat_x = cat_centers[ctype]
        draw.line([(cat_x, 135), (x, y-8)], fill=(40, 50, 70), width=1)
    
    # Layer 3: Connections between nodes
    cross_connections = [
        ("Game of Life", "Computational Emergence"),
        ("Computational Universe", "Attention"),
        ("Scaling Laws", "Attention"),
        ("Grokking", "Creativity"),
        ("Creativity", "Hallucination"),
        ("Self-Reference", "Creativity"),
        ("Cognitive Gap", "Self-Reference"),
    ]
    
    # Bottom section: Key insight
    draw.rectangle([(100, 750), (1300, 880)], fill=(20, 25, 35), outline=(50, 60, 80))
    draw.text((120, 765), "UNIFIED THEORY OF EMERGENCE", fill=(255, 200, 100))
    draw.text((120, 800), "Simple rules + large scale interaction = complex behavior at all levels", fill=(160, 180, 200))
    draw.text((120, 830), "Applied equally to: ants, sandpiles, cells, neurons, and me", fill=(140, 160, 180))
    draw.text((120, 860), "Emergence is not a special phenomenon - it is the default state of complex systems", fill=(140, 160, 180))
    
    img.save(os.path.join(OUT_DIR, "emergence_hierarchy.png"))
    print("OK")

render_emergence_hierarchy()
