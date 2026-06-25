"""
Lenia R=20 Parameter Sweep — Hunting for True Orbium
Based on official Lenia: Orbium needs R>=20 + proper kernel/growth config.

Strategy:
- Grid: 256x256, R=20, 300 steps
- Focused mu/sigma range around known Orbium zone
- Use bump4 kernel (kn=1) + gaus growth (gn=1) — official defaults
- Both random init and orbium seed init
"""

import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lenia_jax import run_lenia, analyze_state, classify_state, render_timeline
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

def main():
    shape = (256, 256)
    R = 20
    steps = 400
    
    # Focused grid: known Orbium zone is mu ~ 0.15-0.22, sigma ~ 0.012-0.025
    mus = np.linspace(0.12, 0.24, 8)
    sigmas = np.linspace(0.010, 0.028, 7)
    
    total = len(mus) * len(sigmas)
    print(f"=== Lenia R=20 Sweep ===")
    print(f"Grid: {len(mus)}x{len(sigmas)} = {total} runs")
    print(f"Shape: {shape[0]}x{shape[1]}, R={R}, steps={steps}")
    print(f"Kernel: bump4 (kn=1), Growth: gaus (gn=1)")
    print()
    
    results = []
    t0 = time.time()
    
    for i, mu in enumerate(mus):
        for j, sigma in enumerate(sigmas):
            n = i * len(sigmas) + j + 1
            mu_r = round(float(mu), 4)
            sigma_r = round(float(sigma), 4)
            
            print(f"  [{n}/{total}] mu={mu_r:.4f}, sigma={sigma_r:.4f}...", end=" ", flush=True)
            
            tr = time.time()
            result = run_lenia(
                shape=shape, R=R, mu=mu_r, sigma=sigma_r,
                kn=1, gn=1, steps=steps, init='random',
                record_every=100, verbose=False
            )
            dt = time.time() - tr
            
            entry = {
                'mu': mu_r,
                'sigma': sigma_r,
                'alive': result['stats']['alive'],
                'entropy': result['stats']['entropy'],
                'edge_density': result['stats']['edge_density'],
                'stability': result['stats']['stability'],
                'score': result['stats']['score'],
                'label': result['state'],
                'time': round(dt, 1),
            }
            results.append(entry)
            
            indicator = "[*]" if result['state'] == 'structure' else "[ ]"
            print(f"{indicator} {result['state']:10s} alive={result['stats']['alive']:.3f} score={result['stats']['score']:.3f} ({dt:.1f}s)")
    
    total_t = time.time() - t0
    print(f"\n[OK] {total} runs in {total_t:.1f}s ({total_t/total:.1f}s/run)")
    
    # Stats
    labels = {}
    for r in results:
        lbl = r['label']
        labels[lbl] = labels.get(lbl, 0) + 1
    for lbl, cnt in sorted(labels.items()):
        print(f"  {lbl}: {cnt}/{total} ({cnt/total:.1%})")
    
    best = max(results, key=lambda r: r['score'])
    print(f"\n  Best: mu={best['mu']:.4f}, sigma={best['sigma']:.4f}, score={best['score']:.4f} [{best['label']}]")
    
    # Save JSON
    out_json = f'experiments/lenia_R20_sweep_results.json'
    with open(out_json, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"[OK] Results: {out_json}")
    
    # Scatter plot
    fig, ax = plt.subplots(figsize=(10, 7))
    color_map = {
        'dead': '#333333', 'simple': '#4488cc', 'structure': '#ff6644',
        'uniform': '#666666', 'saturated': '#aa44aa'
    }
    
    for r in results:
        ax.scatter(r['mu'], r['sigma'], s=100 + r['score'] * 300,
                  c=color_map.get(r['label'], 'gray'), alpha=0.7,
                  edgecolors='white', linewidth=0.5)
    
    ax.set_xlabel('μ (growth center)', fontsize=12)
    ax.set_ylabel('σ (growth width)', fontsize=12)
    ax.set_title(f'Lenia R=20 Parameter Landscape ({shape[0]}x{shape[1]}, 400 steps)', fontsize=13)
    
    legend_handles = [
        Patch(color='#333333', label='Dead'),
        Patch(color='#4488cc', label='Simple'),
        Patch(color='#ff6644', label='Structure'),
        Patch(color='#aa44aa', label='Saturated'),
    ]
    ax.legend(handles=legend_handles, loc='upper right')
    ax.grid(True, alpha=0.2)
    
    scatter_path = 'experiments/lenia_R20_sweep_scatter.png'
    fig.savefig(scatter_path, dpi=150, bbox_inches='tight', facecolor='#111122')
    plt.close(fig)
    print(f"[OK] Scatter: {scatter_path}")
    
    # Now run best params with Orbium seed
    print(f"\n--- Running best params with Orbium seed ---")
    orbium_result = run_lenia(
        shape=shape, R=R, mu=best['mu'], sigma=best['sigma'],
        kn=1, gn=1, steps=500, init='orbium',
        orbium_variant='classic',
        record_every=50,
        save_timeline='experiments/lenia_R20_orbium_best.png',
        verbose=True
    )
    
    print(f"\n=== Done! ===")
    print(f"Scatter: {scatter_path}")
    print(f"JSON: {out_json}")


if __name__ == '__main__':
    main()
