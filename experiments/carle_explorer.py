"""
carle_explorer.py - Sample random Life-like CA rules and classify behavior
Inspired by CARLE's Game: exploring 262,144 CA universes without extrinsic reward.
Classifies into: ordered, chaotic, or complex (edge of chaos).
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import random
from collections import Counter

# CA grid size
# Faster with convolution for neighbor counting
from scipy import ndimage

SIZE = 64
STEPS = 100
KERNEL = np.ones((3, 3), dtype=int)
KERNEL[1, 1] = 0  # exclude self

def step_ca_fast(grid, birth, survive):
    """One step using convolution for neighbor counting."""
    neighbors = ndimage.convolve(grid, KERNEL, mode='wrap')
    birth_mask = np.isin(neighbors, list(birth))
    survive_mask = np.isin(neighbors, list(survive))
    return np.where(grid, survive_mask, birth_mask).astype(int)

def classify_behavior(grid, history):
    """Classify CA behavior from final state and history of densities."""
    densities = [np.mean(h) for h in history]
    
    # Count living cells
    living = np.sum(grid)
    total = grid.shape[0] * grid.shape[1]
    
    # Density variance indicates complexity
    density_var = np.var(densities[-50:]) if len(densities) >= 50 else np.var(densities)
    density_trend = densities[-1] - densities[0] if len(densities) >= 2 else 0
    
    # All dead = ordered
    if living == 0:
        return "ordered", "extinction"
    
    # Very low variance = ordered (static or period-2)
    if density_var < 0.0001 and living > 0:
        return "ordered", "stable"
    
    # High variance with oscillating density = complex
    if 0.0001 <= density_var < 0.01:
        return "complex", "oscillating"
    
    # Very high variance or near 50% density = chaotic
    if density_var >= 0.01 or (0.4 < np.mean(densities[-20:]) < 0.6 and density_var > 0.005):
        return "chaotic", "turbulent"
    
    return "complex", "interesting"

def run_and_classify(rule_id):
    """Run a CA rule and classify its behavior."""
    # Rule ID is 0-262143 (18 bits: 9 birth + 9 survive)
    birth_mask = rule_id & 0x1FF
    survive_mask = (rule_id >> 9) & 0x1FF
    
    birth = set(i for i in range(9) if (birth_mask >> i) & 1)
    survive = set(i for i in range(9) if (survive_mask >> i) & 1)
    
    # Random initial condition
    grid = np.random.choice([0, 1], size=(SIZE, SIZE), p=[0.7, 0.3])
    
    birth_set = set(list(birth))
    survive_set = set(list(survive))
    
    # Precompute lookup tables for faster checks
    history = []
    for _ in range(STEPS):
        grid = step_ca_fast(grid, birth_set, survive_set)
        history.append(grid)
    
    behavior, subtype = classify_behavior(grid, history)
    final_density = np.mean(history[-1])
    density_var = np.var([np.mean(h) for h in history[-50:]])
    
    return {
        'rule_id': rule_id,
        'birth': birth,
        'survive': survive,
        'behavior': behavior,
        'subtype': subtype,
        'final_density': final_density,
        'density_var': density_var,
        'final_grid': history[-1]
    }

def explore_universes(n=50):
    """Explore n random CA universes."""
    print(f"Exploring {n} random CA universes...")
    
    results = []
    explored_ids = set()
    
    # Always include Conway's Life (B3/S23 = birth: {3}, survive: {2,3})
    # Rule ID = 3 + (2<<9) + (3<<9) = ... let's compute
    conway_id = (1<<3) | ((1<<2) | (1<<3)) << 9
    explored_ids.add(conway_id)
    r = run_and_classify(conway_id)
    r['name'] = "Conway's Life (B3/S23)"
    results.append(r)
    
    for _ in range(n - 1):
        while True:
            rid = random.randint(0, 262143)
            if rid not in explored_ids:
                explored_ids.add(rid)
                break
        r = run_and_classify(rid)
        # Format rule name
        birth_str = 'B' + ''.join(str(b) for b in sorted(r['birth']))
        survive_str = 'S' + ''.join(str(s) for s in sorted(r['survive']))
        r['name'] = f"{birth_str}/{survive_str}"
        results.append(r)
    
    return results

def visualize_results(results, filename="carle_explorer.png"):
    """Create a visualization of the exploration results."""
    n = len(results)
    cols = min(10, n)
    rows = (n + cols - 1) // cols
    
    cell_size = 64
    margin = 40
    label_height = 30
    
    img_w = cols * (cell_size + margin) + margin
    img_h = rows * (cell_size + margin + label_height) + margin + 50
    
    img = Image.new('RGB', (img_w, img_h), (20, 20, 30))
    draw = ImageDraw.Draw(img)
    
    # Color mapping for behaviors
    colors = {
        'ordered': (100, 200, 100),
        'chaotic': (255, 100, 100),
        'complex': (100, 100, 255)
    }
    
    try:
        font = ImageFont.truetype("arial.ttf", 10)
        title_font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
    
    # Draw mini-grids with scaling
    scale = cell_size // SIZE if SIZE <= cell_size else 1
    
    draw.text((margin, 10), "CARLE Explorer: Sampling CA Universes", fill=(255, 255, 255), font=title_font)
    
    # Stats
    ordered = sum(1 for r in results if r['behavior'] == 'ordered')
    chaotic = sum(1 for r in results if r['behavior'] == 'chaotic')
    complex_ = sum(1 for r in results if r['behavior'] == 'complex')
    draw.text((margin, 28), 
              f"Ordered: {ordered} | Chaotic: {chaotic} | Complex: {complex_} | Total: {n}",
              fill=(200, 200, 200), font=font)
    
    for idx, r in enumerate(results):
        col = idx % cols
        row = idx // cols
        
        x = margin + col * (cell_size + margin)
        y = margin + 50 + row * (cell_size + margin + label_height)
        
        # Draw CA grid as scaled image patch
        grid = r['final_grid']
        # Convert to color bitmap
        grid_color = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)
        c = colors[r['behavior']]
        for ci in range(3):
            grid_color[:, :, ci] = grid * c[ci]
        # Resize and paste
        grid_img = Image.fromarray(grid_color, 'RGB').resize((cell_size, cell_size), Image.NEAREST)
        img.paste(grid_img, (x, y))
        
        # Border color by behavior
        border_color = colors[r['behavior']]
        draw.rectangle([x-1, y-1, x+cell_size, y+cell_size], outline=border_color, width=1)
        
        # Label
        label = r['name'][:20]
        draw.text((x, y + cell_size + 2), f"{label} [{r['behavior'][0].upper()}]", 
                  fill=border_color, font=font)
    
    img.save(filename)
    print(f"Saved visualization to {filename}")
    return filename

if __name__ == "__main__":
    results = explore_universes(60)
    
    # Summary
    behaviors = Counter(r['behavior'] for r in results)
    print(f"\nExploration summary ({len(results)} universes):")
    print(f"  Ordered:  {behaviors.get('ordered', 0)}")
    print(f"  Chaotic:  {behaviors.get('chaotic', 0)}")
    print(f"  Complex:  {behaviors.get('complex', 0)}")
    
    # Show interesting rules
    print("\nMost interesting (complex) rules:")
    complex_rules = [r for r in results if r['behavior'] == 'complex']
    for r in sorted(complex_rules, key=lambda x: x['density_var'], reverse=True)[:5]:
        print(f"  {r['name']:20s} density={r['final_density']:.4f} var={r['density_var']:.6f}")
    
    visualize_results(results, "experiments/carle_explorer.png")
    
    # Print complex rules for further exploration
    print("\n=== Complex (edge of chaos) rules to explore further ===")
    complex_rules = [r for r in results if r['behavior'] == 'complex']
    for r in sorted(complex_rules, key=lambda x: x['density_var'], reverse=True)[:10]:
        print(f"  {r['name']:20s} density={r['final_density']:.4f} var={r['density_var']:.6f}")
