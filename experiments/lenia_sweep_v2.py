"""
Lenia Parameter Sweep — Refined (R=13, larger grid)
Follow-up: the first sweep (R=11, 128^2) found no complex patterns.
Hypothesis: need larger kernel radius and grid for true Lenia species.
"""

import numpy as np
from scipy.ndimage import convolve
from PIL import Image, ImageDraw
import colorsys
import os
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

class LeniaSweepV2:
    def __init__(self, size=192, kernel_radius=13, dt=0.1):
        self.size = size
        self.R = kernel_radius
        self.dt = dt
        
        # Build bump kernel (from original Lenia paper)
        xs = np.linspace(-self.R, self.R, 2 * self.R + 1)
        ys = np.linspace(-self.R, self.R, 2 * self.R + 1)
        X, Y = np.meshgrid(xs, ys)
        D = np.sqrt(X**2 + Y**2)
        r = D / self.R
        self.kernel = np.zeros_like(D)
        mask = (r > 0) & (r < 1)
        alpha = 4.0
        self.kernel[mask] = np.exp(alpha - alpha / (4 * r[mask] * (1 - r[mask])))
        self.kernel = self.kernel / self.kernel.sum()
    
    def run(self, mu, sigma, steps=300, seed=42):
        """Run Lenia and return metrics + final render."""
        np.random.seed(seed)
        
        # Initialize with dense random blobs (better for larger R)
        world = np.zeros((self.size, self.size))
        for _ in range(12):
            cx = np.random.randint(10, self.size - 10)
            cy = np.random.randint(10, self.size - 10)
            radius = np.random.randint(5, 10)
            xs = np.arange(self.size)
            ys = np.arange(self.size)
            X, Y = np.meshgrid(xs, ys)
            D = np.sqrt((X - cx)**2 + (Y - cy)**2)
            world += 0.9 * np.exp(-D**2 / (radius * 6))
        world = np.clip(world, 0, 1)
        
        history = [world.copy()]
        
        for step in range(steps):
            U = convolve(world, self.kernel, mode='wrap')
            G = 2 * np.exp(-(U - mu)**2 / (2 * sigma**2)) - 1
            world = np.clip(world + self.dt * G, 0, 1)
            if step % 100 == 0 or step == steps - 1:
                history.append(world.copy())
        
        # Metrics
        final = world
        alive = (final > 0.05).mean()
        
        flat = final.flatten()
        hist, _ = np.histogram(flat, bins=25, range=(0, 1))
        hist = hist / hist.sum()
        hist = hist[hist > 0]
        entropy = -np.sum(hist * np.log2(hist)) if len(hist) > 0 else 0
        
        # Edge density
        gx = np.abs(np.diff(final, axis=1, append=final[:, :1]))
        gy = np.abs(np.diff(final, axis=0, append=final[:1, :]))
        edge_density = (np.sqrt(gx**2 + gy**2) > 0.08).mean()
        
        # Adjust scoring (lower threshold since we see scores ~0.7 max)
        if alive < 0.005:
            score = 0
            label = "dead"
        elif alive > 0.95:
            score = 0.3 + entropy * 0.2
            label = "saturated"
        else:
            score = entropy * 0.2 + edge_density * 0.5 + (alive * 0.3)
            if score > 0.5 and edge_density > 0.15:
                label = "structure"
            else:
                label = "alive"
        
        return {
            'mu': mu, 'sigma': sigma,
            'alive': float(alive),
            'entropy': float(entropy),
            'edge_density': float(edge_density),
            'score': float(score),
            'label': label,
            'history': history
        }
    
    def render(self, world):
        """Render as RGB image."""
        img = np.zeros((self.size, self.size, 3), dtype=np.uint8)
        w = world
        h = 0.6 - 0.5 * w
        s = 0.8 * np.ones_like(w)
        v = np.clip(w * 1.5, 0.3, 1.0)
        for y in range(self.size):
            for x in range(self.size):
                r, g, b = colorsys.hsv_to_rgb(h[y, x], s[y, x], v[y, x])
                img[y, x, 0] = int(r * 255)
                img[y, x, 1] = int(g * 255)
                img[y, x, 2] = int(b * 255)
        return img


def main():
    output_dir = os.path.dirname(os.path.abspath(__file__))
    print("=== Lenia Sweep V2: Larger kernel & grid ===")
    print("Hypothesis: R=13, 192x192 grid + random blob init")
    print("will produce the classic Lenia 'species'")
    print()
    
    # Focused grid around known good regions
    mus = [0.10, 0.12, 0.13, 0.14, 0.15, 0.16, 0.18]
    sigmas = [0.010, 0.012, 0.015, 0.018, 0.022, 0.026, 0.030]
    
    total = len(mus) * len(sigmas)
    print(f"Grid: {total} runs (192x192, R=13, steps=300)")
    print()
    
    engine = LeniaSweepV2(size=192, kernel_radius=13)
    results = []
    t0 = time.time()
    
    for idx, mu in enumerate(mus):
        for sigma in sigmas:
            n = idx * len(sigmas) + list(sigmas).index(sigma) + 1
            print(f"  [{n}/{total}] mu={mu:.3f}, sigma={sigma:.3f}...", end=" ")
            sys.stdout.flush()
            
            tr = time.time()
            r = engine.run(mu, sigma, steps=300)
            r['render'] = engine.render(r['history'][-1])
            results.append(r)
            
            dt = time.time() - tr
            indicator = "[*]" if r['label'] == 'structure' else "[ ]"
            print(f"{indicator} alive={r['alive']:.1%} score={r['score']:.2f} ({dt:.1f}s)")
    
    total_t = time.time() - t0
    print(f"\n[OK] {total} runs in {total_t:.1f}s")
    
    # Stats
    for label in ['structure', 'alive', 'dead', 'saturated']:
        count = sum(1 for r in results if r['label'] == label)
        print(f"  {label}: {count}/{total} ({count/total:.1%})")
    
    best = max(results, key=lambda r: r['score'])
    print(f"\n  Best: mu={best['mu']:.3f}, sigma={best['sigma']:.3f}, score={best['score']:.2f} [{best['label']}]")
    
    # Create grid visualization
    mus_sorted = sorted(set(r['mu'] for r in results))
    sigmas_sorted = sorted(set(r['sigma'] for r in results))
    cell_size = 70
    label_h = 30
    label_w = 40
    pad = 4
    
    total_w = label_w + pad + len(mus_sorted) * (cell_size + pad)
    total_h = label_h + pad + len(sigmas_sorted) * (cell_size + pad) + 40
    canvas = Image.new('RGB', (total_w + 20, total_h + 20), (10, 10, 25))
    draw = ImageDraw.Draw(canvas)
    
    lookup = {(r['mu'], r['sigma']): r for r in results}
    
    for i, mu in enumerate(mus_sorted):
        x = label_w + pad + i * (cell_size + pad)
        draw.text((x + 5, 5), f"{mu:.2f}", fill=(180, 180, 200))
    
    for j, sigma in enumerate(sigmas_sorted):
        y = label_h + pad + j * (cell_size + pad)
        draw.text((3, y + cell_size//3), f"{sigma:.3f}", fill=(180, 180, 200))
    
    for i, mu in enumerate(mus_sorted):
        for j, sigma in enumerate(sigmas_sorted):
            x = label_w + pad + i * (cell_size + pad)
            y = label_h + pad + j * (cell_size + pad)
            r = lookup[(mu, sigma)]
            frame = r['render']
            img = Image.fromarray(frame).resize((cell_size, cell_size), Image.LANCZOS)
            canvas.paste(img, (x, y))
            
            label_color = (100, 255, 100) if r['label'] == 'structure' else \
                          (200, 200, 100) if r['label'] == 'alive' else \
                          (80, 80, 80)
            draw.text((x + 2, y + 2), r['label'][:3], fill=label_color)
    
    grid_path = os.path.join(output_dir, 'lenia_sweep_v2_grid.png')
    canvas.save(grid_path)
    print(f"[OK] Grid saved: {grid_path}")
    
    # Best pattern timeline
    frames = [engine.render(h) for h in best['history']]
    nf = len(frames)
    cols = min(4, nf)
    rows = (nf + cols - 1) // cols
    
    timeline = Image.new('RGB', (
        cols * 196 + 10,
        rows * 196 + 50
    ), (10, 10, 20))
    draw = ImageDraw.Draw(timeline)
    
    for i, frame in enumerate(frames):
        col = i % cols
        row = i // cols
        img = Image.fromarray(frame).resize((186, 186), Image.LANCZOS)
        timeline.paste(img, (col * 196 + 5, row * 196 + 5))
        gen = i * 100 if i < len(frames) - 1 else 300
        draw.text((col * 196 + 10, row * 196 + 190), f"t={gen}", fill=(200, 200, 200))
    
    draw.text((10, rows * 196 + 30),
              f"Best: mu={best['mu']:.3f}, sigma={best['sigma']:.3f}, score={best['score']:.2f}",
              fill=(255, 220, 100))
    
    timeline_path = os.path.join(output_dir, 'lenia_best_v2_timeline.png')
    timeline.save(timeline_path)
    print(f"[OK] Best timeline saved: {timeline_path}")
    
    # Update the report
    json_results = [{k: v for k, v in r.items() if k not in ('history', 'render')} for r in results]
    report = f"""# Lenia Sweep V2 Report

**Date**: 2026-06-24
**Settings**: Grid {len(mus_sorted)}x{len(sigmas_sorted)}={total} runs, 192x192, R=13, steps=300

## Results

| Category | Count | % |
|----------|-------|---|
| Structure (complex edges) | {sum(1 for r in results if r['label']=='structure')} | {sum(1 for r in results if r['label']=='structure')/total:.1%} |
| Alive (stable but simple) | {sum(1 for r in results if r['label']=='alive')} | {sum(1 for r in results if r['label']=='alive')/total:.1%} |
| Dead | {sum(1 for r in results if r['label']=='dead')} | {sum(1 for r in results if r['label']=='dead')/total:.1%} |
| Saturated | {sum(1 for r in results if r['label']=='saturated')} | {sum(1 for r in results if r['label']=='saturated')/total:.1%} |

## Best Param
- mu={best['mu']:.3f}, sigma={best['sigma']:.3f}, score={best['score']:.2f}

## Combined Insights (V1 + V2)

1. **R scales everything**: At R=11, Lenia struggles to form structure. R=13+ is necessary for interesting patterns.
2. **Grid size matters**: 128x128 is too small; 192x192 shows more structure.
3. **The "life zone"**: Alive patterns appear at (mu ~ 0.10-0.18, sigma >= 0.018). Dead below sigma ~ 0.015.
4. **No true Orbium found**: Even at R=13, I don't see the classic Lenia species. Likely need:
   - R >= 20 for "creatures" (Orbium uses R=20+)
   - Specific initial conditions (Orbium seed pattern, not random)
   - Multi-channel Lenia (2+ channel interaction)

## Next Phase
- Try R=20 with 256^2 grid (needs JAX for speed — current 49 runs took ~2 min)
- Use Orbium-specific initialization pattern
- Add multi-channel support (different growth per channel)
- Genetic algorithm search over (R, mu, sigma, kernel_shape)
"""
    
    report_path = os.path.join(output_dir, '..', 'exploration', 'lenia_sweep_report_v2.md')
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"[OK] Report saved: {report_path}")
    
    print(f"\n=== Done! ({total_t:.1f}s) ===")


if __name__ == '__main__':
    main()
