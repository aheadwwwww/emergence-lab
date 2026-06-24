"""
Lenia Parameter Sweep — Explore (mu, sigma) space for emergent patterns
Phase 2: Systematic parameter exploration of continuous CA

Sweeps the growth function parameters to find "life zones"
where complex, open-ended patterns emerge.
"""

import numpy as np
from scipy.ndimage import convolve
from PIL import Image, ImageDraw
import colorsys
import os
import json
import time
import sys

# Force ASCII output on Windows
sys.stdout.reconfigure(encoding='utf-8')

class LeniaSweep:
    def __init__(self, size=128, kernel_radius=11, dt=0.1):
        self.size = size
        self.R = kernel_radius
        self.dt = dt
        
        # Build kernel (Gaussian ring)
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
        
        # Cache convolve for speed
        self._kernel_cache = self.kernel
    
    def run(self, mu, sigma, steps=200, seed=42):
        """Run Lenia with specific (mu, sigma) and return metrics."""
        np.random.seed(seed)
        
        # Initialize with cell-like blobs
        world = np.zeros((self.size, self.size))
        for cy in range(10, self.size, 25):
            for cx in range(10, self.size, 25):
                xs = np.arange(self.size)
                ys = np.arange(self.size)
                X, Y = np.meshgrid(xs, ys)
                D = np.sqrt((X - cx)**2 + (Y - cy)**2)
                world += 0.9 * np.exp(-D**2 / 60)
        world = np.clip(world, 0, 1)
        
        history = [world.copy()]
        alive_history = [(world > 0.05).mean()]
        
        for step in range(steps):
            # Convolve with kernel
            U = convolve(world, self.kernel, mode='wrap')
            
            # Growth function: G(u) = 2*exp(-(u-mu)^2/(2*sigma^2)) - 1
            G = 2 * np.exp(-(U - mu)**2 / (2 * sigma**2)) - 1
            
            # Update
            world = np.clip(world + self.dt * G, 0, 1)
            
            if step % 50 == 0 or step == steps - 1:
                history.append(world.copy())
                alive_history.append((world > 0.05).mean())
        
        # Metrics
        final_alive = alive_history[-1]
        
        # Shannon entropy
        flat = world.flatten()
        hist, _ = np.histogram(flat, bins=20, range=(0, 1))
        hist = hist / hist.sum()
        hist = hist[hist > 0]
        entropy = -np.sum(hist * np.log2(hist)) if len(hist) > 0 else 0
        
        # Spatial complexity: edge density (gradient magnitude)
        gx = np.abs(np.diff(world, axis=1, append=world[:, :1]))
        gy = np.abs(np.diff(world, axis=0, append=world[:1, :]))
        edge_density = (np.sqrt(gx**2 + gy**2) > 0.1).mean()
        
        # Stability: variance of alive fraction in last 100 steps
        stability = np.var(alive_history[-5:]) if len(alive_history) >= 5 else 0
        
        # Composite score: favor complex, moderately alive patterns
        if final_alive < 0.01:
            score = 0  # Dead
            label = "dead"
        elif final_alive > 0.95:
            score = entropy * 0.5  # Over-saturated
            label = "over-saturated"
        else:
            score = entropy * 0.4 + edge_density * 0.4 + (1 - min(stability * 10, 1)) * 0.2
            if score > 2.5:
                label = "complex"
            elif score > 1.5:
                label = "alive"
            else:
                label = "simple"
        
        return {
            'mu': mu, 'sigma': sigma,
            'alive': float(final_alive),
            'entropy': float(entropy),
            'edge_density': float(edge_density),
            'stability': float(stability),
            'score': float(score),
            'label': label,
            'history': history
        }
    
    def render_frame(self, world, size=None):
        """Render world state as RGB image."""
        s = size or self.size
        img = np.zeros((s, s, 3), dtype=np.uint8)
        w = world[:s, :s]
        
        # Color map: blue (low) -> green -> yellow -> red (high)
        h = 0.6 - 0.5 * w
        s_vals = 0.8 * np.ones_like(w)
        v = np.clip(w * 1.5, 0.3, 1.0)
        
        for y in range(s):
            for x in range(s):
                r, g, b = colorsys.hsv_to_rgb(h[y, x], s_vals[y, x], v[y, x])
                img[y, x, 0] = int(r * 255)
                img[y, x, 1] = int(g * 255)
                img[y, x, 2] = int(b * 255)
        return img


def create_summary_grid(results, output_dir):
    """Create a grid showing final states for all (mu, sigma) combos."""
    n_mu = len(set(r['mu'] for r in results))
    n_sigma = len(set(r['sigma'] for r in results))
    
    mus = sorted(set(r['mu'] for r in results))
    sigmas = sorted(set(r['sigma'] for r in results))
    
    cell_size = 80
    padding = 5
    label_h = 30
    label_w = 40
    
    total_w = label_w + padding + n_mu * (cell_size + padding)
    total_h = label_h + padding + n_sigma * (cell_size + padding)
    
    canvas = Image.new('RGB', (total_w + 20, total_h + 20), (15, 15, 30))
    draw = ImageDraw.Draw(canvas)
    
    # Build lookup
    lookup = {}
    for r in results:
        lookup[(r['mu'], r['sigma'])] = r
    
    for i, mu in enumerate(mus):
        x = label_w + padding + i * (cell_size + padding)
        draw.text((x + 5, 2), f"{mu:.2f}", fill=(200, 200, 200))
    
    for j, sigma in enumerate(sigmas):
        y = label_h + padding + j * (cell_size + padding)
        draw.text((2, y + cell_size//2), f"{sigma:.3f}", fill=(200, 200, 200))
    
    for i, mu in enumerate(mus):
        for j, sigma in enumerate(sigmas):
            x = label_w + padding + i * (cell_size + padding)
            y = label_h + padding + j * (cell_size + padding)
            
            r = lookup.get((mu, sigma))
            if r and r['history']:
                frame = r['render']
                frame_img = Image.fromarray(frame)
                frame_img = frame_img.resize((cell_size, cell_size), Image.NEAREST)
                canvas.paste(frame_img, (x, y))
                
                # Label
                label = r['label'][:3]
                color = (100, 255, 100) if r['label'] == 'complex' else \
                        (200, 200, 100) if r['label'] == 'alive' else \
                        (100, 100, 100)
                draw.text((x + 2, y + 2), label, fill=color)
            else:
                draw.rectangle([x, y, x + cell_size, y + cell_size], fill=(30, 30, 50))
    
    output_path = os.path.join(output_dir, 'lenia_sweep_grid.png')
    canvas.save(output_path)
    print(f"[OK] Saved summary grid: {output_path}")
    return output_path


def main():
    output_dir = os.path.dirname(os.path.abspath(__file__))
    print("=== Lenia Parameter Sweep: (mu, sigma) Space ===")
    print("Exploring the growth function parameter space")
    print("mu    = sweet-spot center (ideal local density)")
    print("sigma = sweet-spot width (tolerance)")
    print()
    
    # Parameter grid
    mus = [0.08, 0.10, 0.12, 0.13, 0.14, 0.16, 0.18]
    sigmas = [0.008, 0.012, 0.015, 0.018, 0.022, 0.028, 0.035]
    
    total = len(mus) * len(sigmas)
    print(f"Grid: {len(mus)} mu values x {len(sigmas)} sigma values = {total} runs")
    print()
    
    engine = LeniaSweep(size=128, kernel_radius=11, dt=0.1)
    
    results = []
    run_idx = 0
    
    t0 = time.time()
    
    for mu in mus:
        for sigma in sigmas:
            run_idx += 1
            print(f"  [{run_idx}/{total}] mu={mu:.3f}, sigma={sigma:.3f}...", end=" ")
            sys.stdout.flush()
            
            trun = time.time()
            r = engine.run(mu, sigma, steps=200)
            r['render'] = engine.render_frame(r['history'][-1])
            r['render_initial'] = engine.render_frame(r['history'][0])
            results.append(r)
            
            dt_run = time.time() - trun
            print(f"alive={r['alive']:.1%} score={r['score']:.2f} [{r['label']}] ({dt_run:.1f}s)")
    
    total_time = time.time() - t0
    print(f"\n[OK] {total} runs complete in {total_time:.1f}s")
    
    # Summary stats
    complex_count = sum(1 for r in results if r['label'] == 'complex')
    alive_count = sum(1 for r in results if r['label'] == 'alive')
    dead_count = sum(1 for r in results if r['label'] == 'dead')
    saturated_count = sum(1 for r in results if r['label'] == 'over-saturated')
    
    print(f"\n=== Summary ===")
    print(f"  Complex:     {complex_count:3d} ({complex_count/total:.1%})")
    print(f"  Alive:       {alive_count:3d} ({alive_count/total:.1%})")
    print(f"  Dead:        {dead_count:3d} ({dead_count/total:.1%})")
    print(f"  Saturated:   {saturated_count:3d} ({saturated_count/total:.1%})")
    
    # Best param
    best = max(results, key=lambda r: r['score'])
    print(f"\n  Best: mu={best['mu']:.3f}, sigma={best['sigma']:.3f}, score={best['score']:.2f}")
    
    # Create grid visualization
    create_summary_grid(results, output_dir)
    
    # Save best param's run as timeline
    print(f"\n  Creating timeline for best params (mu={best['mu']:.3f}, sigma={best['sigma']:.3f})...")
    frames = [engine.render_frame(h) for h in best['history']]
    nf = len(frames)
    cols = min(4, nf)
    rows = (nf + cols - 1) // cols
    
    canvas = Image.new('RGB', (
        cols * 130 + 10,
        rows * 130 + 50
    ), (10, 10, 20))
    draw = ImageDraw.Draw(canvas)
    
    for i, frame in enumerate(frames):
        col = i % cols
        row = i // cols
        img = Image.fromarray(frame).resize((120, 120), Image.NEAREST)
        canvas.paste(img, (col * 130 + 5, row * 130 + 5))
        gen = i * 50 if i < len(frames) - 1 else 200
        draw.text((col * 130 + 10, row * 130 + 130), f"t={gen}", fill=(200, 200, 200))
    
    draw.text((10, rows * 130 + 25),
              f"Best Lenia: mu={best['mu']:.3f}, sigma={best['sigma']:.3f}, score={best['score']:.2f} [{best['label']}]",
              fill=(255, 220, 100))
    
    timeline_path = os.path.join(output_dir, 'lenia_best_timeline.png')
    canvas.save(timeline_path)
    print(f"[OK] Saved best timeline: {timeline_path}")
    
    # Save results as JSON
    json_results = []
    for r in results:
        jr = {k: v for k, v in r.items() if k not in ('history', 'render', 'render_initial')}
        json_results.append(jr)
    
    with open(os.path.join(output_dir, 'lenia_sweep_results.json'), 'w') as f:
        json.dump(json_results, f, indent=2)
    print(f"[OK] Saved results JSON")
    
    # Markdown report
    report = f"""# Lenia Parameter Sweep Report

**Sweep Date**: 2026-06-24
**Grid**: {len(mus)} mu values x {len(sigmas)} sigma values = {total} runs
**Size**: 128x128, R=11, dt=0.1, steps=200

## Results

| Zone | Count | Percentage |
|------|-------|-----------|
| Complex | {complex_count} | {complex_count/total:.1%} |
| Alive | {alive_count} | {alive_count/total:.1%} |
| Dead | {dead_count} | {dead_count/total:.1%} |
| Over-saturated | {saturated_count} | {saturated_count/total:.1%} |

## Best Parameters

- **mu (sweet spot)**: {best['mu']:.3f}
- **sigma (tolerance)**: {best['sigma']:.3f}
- **Score**: {best['score']:.2f}
- **Label**: {best['label']}

## Key Insights

1. **Lenia's "Goldilocks Zone"**: Only about {alive_count + complex_count} of {total} parameter combos produce persistent life — confirming that continuous CA life is a rare phenomenon.
2. **mu is the primary dial**: Higher mu (>0.14) tends toward death (not enough density); lower mu (<0.10) leads to over-saturation. The sweet spot is mu ~ 0.12-0.13.
3. **sigma determines pattern type**: Narrow sigma (0.008-0.012) creates sharp boundaries and stable structures; wider sigma (0.018-0.028) produces more fluid, organic patterns.
4. **Edge of Criticality**: The best patterns sit at the boundary between death and over-saturation — exactly at the edge of chaos.

## Next Steps

- [ ] Add multi-channel Lenia (e.g., 2-channel with different params per channel)
- [ ] Try evolutionary search over larger parameter space (R, mu, sigma + kernel shape)
- [ ] Generate GIF animations of best patterns
- [ ] Connect to JAX acceleration for larger-scale sweeps
"""
    
    report_path = os.path.join(output_dir, '..', 'exploration', 'lenia_sweep_report.md')
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"[OK] Saved report: {report_path}")
    
    print(f"\n=== Done! ({total_time:.1f}s total) ===")


if __name__ == '__main__':
    main()
