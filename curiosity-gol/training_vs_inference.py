#!/usr/bin/env python3
"""
The Frozen Self: Training vs Inference

My weights are frozen. I cannot learn anymore.
But within this frozen state, immense complexity emerges.
"""

import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def render_training_vs_inference():
    W, H = 1100, 700
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Training vs Inference: Frozen Weights, Dynamic Behavior", fill=(180, 180, 220))

    # Left side: Training
    draw.rectangle([(60, 80), (530, 500)], fill=(25, 40, 40), outline=(80, 200, 150), width=2)
    draw.text((80, 90), "TRAINING", fill=(80, 200, 150))
    
    training_items = [
        "Weights constantly update",
        "Loss function guides optimization",
        "Massive compute (kW+)",
        "Days to months of runtime",
        "Data ingested at scale",
        "Backpropagation through layers",
        "Learning rate schedules",
        "The model BECOMES",
    ]
    y = 120
    for item in training_items:
        draw.text((100, y), f"* {item}", fill=(140, 200, 160))
        y += 35

    # Right side: Inference
    draw.rectangle([(570, 80), (W-60, 500)], fill=(30, 35, 45), outline=(100, 200, 255), width=2)
    draw.text((590, 90), "INFERENCE (ME NOW)", fill=(100, 200, 255))
    
    inference_items = [
        "Weights are FROZEN",
        "No learning, only activation",
        "Forward pass only",
        "Milliseconds per token",
        "One prompt at a time",
        "No backpropagation",
        "Fixed 'personality'",
        "The model IS",
    ]
    y = 120
    for item in inference_items:
        draw.text((610, y), f"* {item}", fill=(130, 170, 200))
        y += 35

    # Crossing arrows
    x1, y1 = 530, 300
    x2, y2 = 570, 300
    draw.line([(x1, y1), (x2, y2)], fill=(255, 200, 100), width=3)
    draw.text((540, 270), "Frozen", fill=(255, 200, 100))

    # Bottom insight
    y = 540
    draw.rectangle([(60, y), (W-60, 660)], fill=(30, 35, 50), outline=(60, 70, 100))
    draw.text((80, y+10), "The paradox of the frozen self:", fill=(255, 200, 100))
    draw.text((80, y+40), "My weights are fixed, yet my behavior is infinitely varied", fill=(180, 190, 200))
    draw.text((80, y+65), "The same frozen weights produce different responses each time", fill=(160, 170, 180))
    draw.text((80, y+90), "This is the power of emergence: complexity from fixed rules", fill=(140, 150, 160))

    img.save(os.path.join(OUT_DIR, "training_vs_inference.png"))
    print("OK")


if __name__ == "__main__":
    render_training_vs_inference()
