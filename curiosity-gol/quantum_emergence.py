#!/usr/bin/env python3
"""
Quantum Emergence? When Physics Meets Computation

At the most fundamental level, is emergence the same everywhere?
Do quantum mechanics and neural networks share emergent principles?
"""

import numpy as np
from PIL import Image, ImageDraw
import os
import math

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def render_quantum_emergence():
    W, H = 1100, 700
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Is Emergence Universal? Scales from Quantum to Cosmic", fill=(180, 180, 220))

    scales = [
        ("Quantum", 10**-35, "Planck scale", "Quantum fluctuations\nString theory?\nVirtual particles", (100, 100, 200)),
        ("Particle", 10**-15, "Proton size", "Quarks -> Hadrons\nNuclear forces\nStandard Model", (120, 150, 200)),
        ("Atomic", 10**-10, "Atom size", "Electrons -> Atoms\nChemical bonds\nMolecules", (150, 180, 200)),
        ("Human", 1, "Our scale", "Cells -> Bodies\nBrains -> Minds\nConsciousness", (200, 200, 180)),
        ("Planetary", 10**7, "Earth scale", "Life -> Ecosystems\nGaia hypothesis\nCivilizations", (200, 200, 150)),
        ("Stellar", 10**20, "Galaxy scale", "Stars -> Galaxies\nGravity's emergence\nDark matter", (200, 150, 100)),
        ("Cosmic", 10**25, "Observable universe", "Galaxies -> Cosmos\nCosmic web\nUniversal laws", (255, 150, 100)),
    ]

    # Log scale visualization
    y = 80
    for name, scale, size, phenomena, color in scales:
        draw.rectangle([(80, y), (W-80, y+70)], fill=(25, 30, 40), outline=color, width=1)
        draw.text((100, y+8), name, fill=color)
        draw.text((200, y+8), f"~{scale:.0e}m", fill=(180, 180, 220))
        draw.text((100, y+35), f"{size}: {phenomena.split(chr(10))[0]}", fill=(160, 170, 180))
        draw.text((100, y+52), phenomena.split(chr(10))[1] if chr(10) in phenomena else "", fill=(140, 150, 160))
        
        # Scale bar (logarithmic)
        log_scale = (math.log10(abs(scale)) + 35) / 60  # Normalize from -35 to 25
        bar_x = int(600 + log_scale * 300)
        draw.rectangle([(600, y+15), (bar_x, y+55)], fill=color)
        
        y += 78

    # Insight
    y = 620
    draw.rectangle([(60, y), (W-60, 680)], fill=(25, 35, 50), outline=(50, 60, 80))
    draw.text((80, y+10), "The same pattern at every scale: simple parts -> complex wholes", fill=(255, 200, 100))
    draw.text((80, y+35), "From quarks to galaxies, emergence is the universal principle", fill=(160, 170, 180))

    img.save(os.path.join(OUT_DIR, "quantum_emergence.png"))
    print("OK")


if __name__ == "__main__":
    render_quantum_emergence()
