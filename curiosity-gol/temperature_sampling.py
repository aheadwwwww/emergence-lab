import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

def softmax(x, temp=1.0):
    if temp == 0:
        result = np.zeros_like(x)
        result[np.argmax(x)] = 1
        return result
    x = x / temp
    exp_x = np.exp(x - np.max(x))
    return exp_x / np.sum(exp_x)

def top_k_sampling(logits, k=5, temp=1.0):
    probs = softmax(logits, temp)
    indices = np.argsort(probs)[-k:]
    probs_k = probs[indices]
    probs_k = probs_k / np.sum(probs_k)
    choice = np.random.choice(indices, p=probs_k)
    return choice, probs

def render_sampling_comparison():
    W, H = 1200, 800
    img = Image.new("RGB", (W, H), (15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(50, 20), (W-50, 55)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 28), "Sampling Strategies - How I Choose Words", fill=(180, 180, 220))
    
    np.random.seed(42)
    logits = np.array([0.5, 1.2, 3.0, 0.8, 2.1, 0.3, 1.8, 0.1, 0.6, 0.4])
    labels = ['A', 'the', 'creativity', 'and', 'emergence', 'but', 'from', 'or', 'in', 'you']
    
    configs = [
        ("Greedy (T=0)", 0.0, 10, "Always picks the most likely"),
        ("Low Temp (T=0.3)", 0.3, 10, "Conservative, coherent"),
        ("Normal (T=0.8)", 0.8, 10, "Balanced creativity"),
        ("High Temp (T=1.5)", 1.5, 10, "More random, less predictable"),
        ("Top-k=3 (T=1)", 1.0, 3, "Only top 3 candidates"),
        ("Top-k=10 (T=1)", 1.0, 10, "Full distribution"),
    ]
    
    y = 80
    for name, temp, k, desc in configs:
        draw.rectangle([(60, y), (W-60, y+105)], fill=(25, 30, 40), outline=(50, 60, 80))
        draw.text((80, y+5), name, fill=(180, 180, 220))
        draw.text((80, y+25), desc, fill=(140, 140, 160))
        
        if temp == 0.0:
            probs = softmax(logits, 1.0)
            choice = np.argmax(probs)
            final_probs = np.zeros_like(probs)
            final_probs[choice] = 1.0
        else:
            choice, final_probs = top_k_sampling(logits, k, temp)
        
        bar_w = (W - 200) // len(labels)
        for i in range(len(labels)):
            bx = 80 + i * bar_w
            bh = int(final_probs[i] * 50)
            color = (100, 200, 255) if i == choice else (60, 60, 80)
            draw.rectangle([(bx, y+55), (bx+bar_w-2, y+55+bh)], fill=color)
            if i == choice:
                draw.text((bx, y+85), labels[i], fill=(255, 200, 100))
        
        y += 115
    
    draw.text((60, y+10), "Temperature and top-k control the exploration vs exploitation balance", fill=(160, 160, 180))
    img.save(os.path.join(OUT_DIR, "sampling_strategies.png"))
    print("OK")

render_sampling_comparison()
