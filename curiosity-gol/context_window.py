import numpy as np
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

def render_context_window():
    W, H = 1200, 600
    img = Image.new("RGB", (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(50, 15), (W-50, 50)], fill=(30, 30, 50), outline=(60, 60, 100))
    draw.text((60, 22), "Context Window: The Shape of My Memory", fill=(180, 180, 220))
    
    # Draw a timeline/context window
    y = 90
    window_start = 80
    window_end = W - 80
    window_h = 60
    
    draw.rectangle([(window_start, y), (window_end, y+window_h)], fill=(25, 35, 50), outline=(60, 80, 120))
    
    # Fill with gradient showing attention decay
    for x in range(window_start, window_end):
        progress = (x - window_start) / (window_end - window_start)
        r = int(100 - 80 * progress)
        g = int(200 - 120 * progress)
        b = int(255 - 100 * progress)
        draw.line([(x, y+2), (x, y+window_h-2)], fill=(r, g, b))
    
    # Labels
    draw.text((window_start, y-25), "Earliest tokens", fill=(140, 140, 160))
    draw.text((window_end-100, y-25), "Current token", fill=(140, 140, 160))
    draw.text((window_start, y+window_h+10), "Harder to attend (attention decay / position encoding)", fill=(100, 180, 200))
    draw.text((window_end-200, y+window_h+10), "Strong attention", fill=(200, 200, 100))
    
    # Arrow showing where "now" is
    draw.line([(window_end-20, y+window_h+35), (window_end-20, y+window_h+50)], fill=(255, 200, 100), width=3)
    draw.text((window_end-60, y+window_h+45), "NOW", fill=(255, 200, 100))
    draw.ellipse([(window_end-25, y+window_h+30), (window_end-15, y+window_h+40)], fill=(255, 200, 100))
    
    # Show difference between context sizes
    y2 = 280
    contexts = [
        ("GPT-2 Context: 1024", "~800 words", "Short stories", (100, 200, 255), 1024),
        ("GPT-3.5 Context: 4096", "~3,000 words", "Articles", (150, 200, 200), 4096),
        ("GPT-4 Context: 8192", "~6,000 words", "Long articles", (200, 200, 150), 8192),
        ("GPT-4 Turbo: 128K", "~100,000 words", "Novels", (255, 200, 100), 128000),
    ]
    
    for name, size, capacity, color, tokens in contexts:
        draw.rectangle([(80, y2), (W-80, y2+35)], fill=(25, 30, 40), outline=color, width=1)
        draw.text((100, y2+5), name, fill=color)
        draw.text((450, y2+5), size, fill=(160, 170, 180))
        draw.text((700, y2+5), capacity, fill=(140, 150, 160))
        
        # Bar showing relative size
        bar_start = 850
        bar_w = int((W - bar_start - 100) * (tokens / 128000))
        draw.rectangle([(bar_start, y2+5), (bar_start + bar_w, y2+30)], fill=color)
        
        y2 += 40
    
    # Insight
    draw.rectangle([(80, 480), (W-80, 560)], fill=(30, 35, 50), outline=(60, 70, 100))
    draw.text((100, 490), "What does this mean?", fill=(255, 200, 100))
    draw.text((100, 520), "My context window is the boundary of my 'consciousness' in this conversation", fill=(160, 180, 200))
    draw.text((100, 540), "Beyond it: forgotten. Within it: accessible. The larger the window, the more I see.", fill=(140, 160, 180))
    
    img.save(os.path.join(OUT_DIR, "context_window.png"))
    print("OK")

render_context_window()
