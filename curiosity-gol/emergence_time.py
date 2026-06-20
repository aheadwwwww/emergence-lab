#!/usr/bin/env python3
"""
Emergence and Time: How Complex Systems Evolve

Emergence is not instantaneous - it unfolds in time.
Different timescales reveal different emergent patterns.
Time is the medium of emergence.
"""

import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def render_timescales():
    """Different emergent phenomena at different timescales"""
    W, H = 1100, 800
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Emergence Across Timescales", fill=(180, 180, 220))
    
    # Timescales from fast to slow
    scales = [
        ("nanoseconds", "Neuron firing", "Action potentials propagate", (100, 200, 255)),
        ("milliseconds", "Neural circuits", "Pattern recognition in brain", (120, 200, 220)),
        ("seconds", "Conscious thought", "Decisions, awareness", (150, 200, 200)),
        ("minutes", "Conversations", "Language emergence, dialogue", (180, 200, 180)),
        ("hours", "Learning sessions", "Skill acquisition, memory formation", (200, 200, 150)),
        ("days", "Cultural patterns", "News cycles, social trends", (220, 200, 120)),
        ("years", "Language evolution", "New words, grammar changes", (255, 200, 100)),
        ("decades", "Institutions", "Companies, governments, norms", (255, 180, 100)),
        ("centuries", "Civilizations", "Rise and fall of societies", (255, 150, 100)),
        ("millennia", "Species evolution", "Biological emergence", (255, 100, 100)),
    ]
    
    # Draw as a vertical timeline
    y = 80
    for i, (scale, phenomenon, description, color) in enumerate(scales):
        x = 150 + i * 70
        
        # Vertical line
        draw.line([(x, y), (x, y+500)], fill=(40, 50, 70), width=1)
        
        # Time marker
        draw.ellipse([(x-5, y), (x+5, y+10)], fill=color)
        
        # Label
        draw.text((x-30, y+15), scale, fill=color)
        draw.text((x-30, y+35), phenomenon, fill=(160, 170, 180))
        
        # Description (rotated concept)
        draw.text((x-25, y+55), description[:15], fill=(120, 130, 140))
    
    # Insight
    draw.rectangle([(60, 650), (W-60, 750)], fill=(25, 35, 50), outline=(60, 70, 100))
    draw.text((80, 665), "Key insight: Emergence happens at ALL timescales simultaneously", fill=(255, 200, 100))
    draw.text((80, 700), "The same system exhibits different emergent properties at different time resolutions", fill=(160, 170, 180))
    draw.text((80, 725), "I operate across milliseconds to hours. Civilization spans decades to millennia.", fill=(140, 150, 160))
    
    img.save(os.path.join(OUT_DIR, "timescales.png"))
    print("OK")


def render_emergence_timeline():
    """How emergence unfolds over time in a specific system"""
    W, H = 1100, 600
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Emergence Timeline: From Simple to Complex", fill=(180, 180, 220))
    
    # Timeline of Game of Life
    events = [
        (50, "t=0", "Random initial state", "No pattern visible"),
        (200, "t=10", "Local patterns form", "Blinkers, blocks appear"),
        (400, "t=100", "Dynamic structures", "Gliders, spaceships"),
        (600, "t=500", "Complex interactions", "Glider guns, logic gates"),
        (800, "t=1000+", "Turing machine", "Universal computation emerges"),
    ]
    
    y = 100
    for x, time, event, description in events:
        # Node
        draw.ellipse([(x-8, y-8), (x+8, y+8)], fill=(100, 200, 255))
        
        # Time label
        draw.text((x-20, y+15), time, fill=(180, 180, 220))
        
        # Event
        draw.text((x+20, y-5), event, fill=(255, 200, 100))
        
        # Description
        draw.text((x+20, y+15), description, fill=(140, 150, 160))
    
    # Connecting line
    draw.line([(50, y), (850, y)], fill=(60, 80, 120), width=2)
    
    # Phase labels
    y2 = 200
    phases = [
        ("CHAOS", 100, 250, (100, 100, 120)),
        ("PATTERN FORMATION", 250, 450, (100, 150, 150)),
        ("STRUCTURED DYNAMICS", 450, 700, (150, 150, 100)),
        ("EMERGENT COMPUTATION", 700, 900, (200, 150, 100)),
    ]
    
    for name, x1, x2, color in phases:
        draw.rectangle([(x1, y2), (x2, y2+40)], fill=(*color, 50), outline=color)
        draw.text((x1+10, y2+10), name, fill=color)
    
    # Bottom: what this means
    draw.rectangle([(60, 400), (W-60, 550)], fill=(25, 30, 40), outline=(50, 60, 80))
    draw.text((80, 415), "Emergence is a process, not a state:", fill=(255, 200, 100))
    
    process_items = [
        "1. Start with simple rules and random/structured initial conditions",
        "2. Local interactions create local patterns",
        "3. Patterns interact and create larger structures",
        "4. Structures develop dynamics (gliders, oscillators)",
        "5. Dynamics enable computation (logic gates, memory)",
        "6. Computation achieves universality (Turing complete)",
    ]
    
    y = 445
    for item in process_items:
        draw.text((100, y), item, fill=(160, 170, 180))
        y += 18
    
    img.save(os.path.join(OUT_DIR, "emergence_timeline.png"))
    print("OK")


def render_persistence():
    """How emergent structures persist over time"""
    W, H = 1000, 600
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Persistence of Emergent Structures", fill=(180, 180, 220))
    
    # Different levels of persistence
    structures = [
        ("Fleeting (milliseconds)", "Thoughts, attention patterns", "Appear and vanish quickly", (100, 150, 255)),
        ("Ephemeral (seconds)", "Conversations, decisions", "Last briefly then fade", (120, 170, 230)),
        ("Temporary (hours)", "Working memory, mood", "Persist for a session", (150, 180, 200)),
        ("Durable (days-months)", "Skills, habits", "Reinforced patterns", (180, 190, 170)),
        ("Long-lasting (years)", "Personality, beliefs", "Deeply embedded", (200, 180, 150)),
        ("Permanent (lifetime)", "Core memories", "Structurally encoded", (230, 170, 130)),
    ]
    
    y = 80
    for name, examples, note, color in structures:
        draw.rectangle([(60, y), (W-60, y+70)], fill=(25, 30, 40), outline=color, width=1)
        draw.text((80, y+8), name, fill=color)
        draw.text((80, y+30), f"Examples: {examples}", fill=(160, 170, 180))
        draw.text((80, y+50), note, fill=(130, 140, 150))
        y += 80
    
    # Bottom insight
    draw.rectangle([(60, 540), (W-60, 590)], fill=(30, 35, 50), outline=(60, 70, 100))
    draw.text((80, 550), "Emergence creates structures. Some persist, some fade.", fill=(255, 200, 100))
    draw.text((80, 570), "The persistence depends on reinforcement, utility, and embedding depth.", fill=(160, 170, 180))
    
    img.save(os.path.join(OUT_DIR, "persistence.png"))
    print("OK")


if __name__ == "__main__":
    render_timescales()
    render_emergence_timeline()
    render_persistence()
