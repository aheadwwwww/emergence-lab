"""
Lenia R=15 Parameter Sweep — Middle ground between R11 and R20
R=11 found 57% alive but only simple patterns. R=20 found 0% alive.
R=15 should be the sweet spot where Orbium-like patterns might emerge.

Strategy:
- Grid: 192x192, R=15, 300 steps
- Wider mu/sigma range than R20 to catch the transition zone
- Use bump4 kernel (kn=1) + gaus growth (gn=1)
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
    shape = (192, 192)
    R = 15
    steps = 400
    
    # Wider grid: bridge R11 success zone and R20 failure zone
    mus = np.linspace(0.10, 0.26, 9)
    sigmas = np.linspace(0.008, 0.030, 8)
    
    total = len(mus) * len(sigmas)
    print(f"=== Lenia R=15 Sweep ===")
    print(f"Grid: {len(mus)}x{len(sigmas)} = {total} runs")
    print(f"Shape: {shape[0]}x{shape[1]}, R={R}, steps={steps}")
    print(f"Kernel: bump4 (kn=1), Growth: gaus (gn=1)")
    print()
    
    results = []
    t0 = time.time()
    
    for i, mu in enumerate(mus):
        for j, sigma in enumerate(sigmas):
            idx = i * len(sigmas) + j + 1
            print(f"  [{idx}/{total}] mu={mu:.4f}, sigma={sigma:.4f}...", end=" ")
            sys.stdout.flush()
            
            trun = time.time()
            
            try:
                result = run_lenia(
                    shape=shape, R=R, steps=steps,
                    mu=float(mu), sigma=float(sigma),
                    kn=1, gn=1,
                    init='random', verbose=False
                )
                
                world = result['state']
                analysis = analyze_state(world)
                label = classify_state(analysis)
                
                result = {
                    'mu': float(mu),
                    'sigma': float(sigma),
                    'alive': float(analysis['alive_fraction']),
                    'entropy': float(analysis.get('entropy', 0)),
                    'edge_density': float(analysis.get('edge_density', 0)),
                    'stability': float(analysis.get('stability', 0)),
                    'score': float(analysis.get('composite_score', 0)),
                    'label': label,
                }
                results.append(result)
                
                dt_run = time.time() - trun
                print(f"alive={result['alive']:.1%} score={result['score']:.2f} [{label}] ({dt_run:.1f}s)")
                
            except Exception as e:
                print(f"ERROR: {e}")
                results.append({
                    'mu': float(mu), 'sigma': float(sigma),
                    'alive': 0, 'entropy': 0, 'edge_density': 0,
                    'stability': 0, 'score': 0, 'label': 'error'
                })
    
    total_time = time.time() - t0
    print(f"\n[OK] {total} runs complete in {total_time:.1f}s")
    
    # Summary stats
    categories = {}
    for r in results:
        cat = r['label']
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\n=== Summary ===")
    for cat, count in sorted(categories.items()):
        print(f"  {cat:20s}: {count:3d} ({count/total:.1%})")
    
    # Best params
    survived = [r for r in results if r['label'] not in ('dead', 'error')]
    if survived:
        best = max(survived, key=lambda r: r['score'])
        print(f"\n  Best: mu={best['mu']:.4f}, sigma={best['sigma']:.4f}, score={best['score']:.2f} [{best['label']}]")
    
    # Create heatmap
    _create_heatmap(results, mus, sigmas, R)
    
    # Save results
    output_dir = os.path.dirname(os.path.abspath(__file__))
    json_results = [{k: v for k, v in r.items()} for r in results]
    with open(os.path.join(output_dir, f'lenia_sweep_R{R}_results.json'), 'w') as f:
        json.dump(json_results, f, indent=2)
    print(f"[OK] Saved results JSON")
    
    # Report
    _write_report(results, categories, total, R, mus, sigmas)
    
    print(f"\n=== Done! ({total_time:.1f}s total) ===")


def _create_heatmap(results, mus, sigmas, R):
    """Create score heatmap."""
    n_mu, n_sig = len(mus), len(sigmas)
    scores = np.zeros((n_sig, n_mu))
    labels = np.zeros((n_sig, n_mu), dtype=int)  # 0=dead, 1=simple, 2=alive, 3=complex
    
    label_map = {'dead': 0, 'error': 0, 'simple': 1, 'alive': 2, 'structure': 2, 'complex': 3, 'survived': 3}
    
    for r in results:
        i = np.argmin(np.abs(mus - r['mu']))
        j = np.argmin(np.abs(sigmas - r['sigma']))
        scores[j, i] = r['score']
        labels[j, i] = label_map.get(r['label'], 0)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    
    # Score heatmap
    im1 = ax1.imshow(scores, aspect='auto', origin='lower', cmap='viridis')
    ax1.set_xticks(range(n_mu))
    ax1.set_xticklabels([f'{m:.3f}' for m in mus], rotation=45)
    ax1.set_yticks(range(n_sig))
    ax1.set_yticklabels([f'{s:.3f}' for s in sigmas])
    ax1.set_xlabel('mu (sweet spot)')
    ax1.set_ylabel('sigma (tolerance)')
    ax1.set_title(f'Lenia R={R} — Composite Score')
    plt.colorbar(im1, ax=ax1)
    
    # Label heatmap
    cmap = plt.cm.colors.ListedColormap(['#333333', '#4488cc', '#44cc88', '#ffaa44'])
    im2 = ax2.imshow(labels, aspect='auto', origin='lower', cmap=cmap, vmin=0, vmax=3)
    ax2.set_xticks(range(n_mu))
    ax2.set_xticklabels([f'{m:.3f}' for m in mus], rotation=45)
    ax2.set_yticks(range(n_sig))
    ax2.set_yticklabels([f'{s:.3f}' for s in sigmas])
    ax2.set_xlabel('mu (sweet spot)')
    ax2.set_ylabel('sigma (tolerance)')
    ax2.set_title(f'Lenia R={R} — Pattern Classification')
    
    legend_elements = [
        Patch(facecolor='#333333', label='Dead'),
        Patch(facecolor='#4488cc', label='Simple'),
        Patch(facecolor='#44cc88', label='Alive/Structure'),
        Patch(facecolor='#ffaa44', label='Complex/Survived'),
    ]
    ax2.legend(handles=legend_elements, loc='upper right', fontsize=8)
    
    plt.tight_layout()
    output_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(output_dir, f'lenia_sweep_R{R}_heatmap.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved heatmap: {path}")


def _write_report(results, categories, total, R, mus, sigmas):
    """Write markdown report."""
    survived = [r for r in results if r['label'] not in ('dead', 'error')]
    best = max(survived, key=lambda r: r['score']) if survived else None
    
    report = f"""# Lenia R={R} Parameter Sweep Report

**Date**: 2026-06-25
**Grid**: {len(mus)} mu x {len(sigmas)} sigma = {total} runs
**Shape**: 192x192, R={R}, steps=400, dt=0.1
**Kernel**: bump4 (kn=1), Growth: gaus (gn=1)

## Results

| Category | Count | Percentage |
|----------|-------|-----------|
"""
    for cat, count in sorted(categories.items()):
        report += f"| {cat} | {count} | {count/total:.1%} |\n"
    
    if best:
        report += f"""
## Best Parameters

- **mu (sweet spot)**: {best['mu']:.4f}
- **sigma (tolerance)**: {best['sigma']:.4f}
- **Score**: {best['score']:.2f}
- **Label**: {best['label']}
- **Alive fraction**: {best['alive']:.1%}
"""
    
    # Compare with R11 and R20
    report += f"""
## Cross-Radius Comparison

| Radius | Survival Rate | Best Score | Notes |
|--------|--------------|------------|-------|
| R=11 | 57.1% | ~2.5 | Simple patterns only |
| R=15 | {sum(1 for r in results if r['label'] not in ('dead','error'))/total:.1%} | {f"{best['score']:.2f}" if best else 'N/A'} | Middle ground |
| R=20 | 0% | 0.30 | All dead — too demanding |

## Key Insights

1. **R={R} transition zone**: R=15 sits between the easy-life zone (R=11) and the no-life zone (R=20).
2. **Parameter sensitivity**: As R increases, the viable (mu, sigma) region shrinks dramatically.
3. **Next step**: If R=15 also fails, try R=13 with wider parameter sweep.
"""
    
    output_dir = os.path.dirname(os.path.abspath(__file__))
    report_path = os.path.join(output_dir, '..', 'exploration', f'lenia_sweep_R{R}_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"[OK] Saved report: {report_path}")


if __name__ == '__main__':
    main()
