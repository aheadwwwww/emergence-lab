"""
Standalone Lenia Experiment Runner

直接运行 Lenia 实验，不依赖复杂的编排器结构。
"""

import sys
from pathlib import Path
import numpy as np
from PIL import Image
import time

# Import emergence_lab
try:
    from emergence_lab import Lenia
    from emergence_lab.core.metrics import EmergenceMetrics
    LENIA_AVAILABLE = True
except ImportError as e:
    print(f"Error: {e}")
    print("Please ensure emergence_lab is installed with dependencies.")
    LENIA_AVAILABLE = False


def run_lenia_experiment(R=13, mu=0.15, sigma=0.014, shape=(256, 256), steps=200):
    """运行单个 Lenia 实验"""
    
    print(f"\n{'='*60}")
    print(f"Running Lenia Experiment")
    print(f"Parameters: R={R}, μ={mu:.4f}, σ={sigma:.5f}")
    print(f"Grid: {shape}, Steps: {steps}")
    print(f"{'='*60}\n")
    
    # Create Lenia instance
    lenia = Lenia(R=R, mu=mu, sigma=sigma)
    lenia.init_grid(shape=shape, mode='random')
    
    # Run simulation
    start_time = time.time()
    result = lenia.run(steps=steps, record_every=50, verbose=True)
    elapsed = time.time() - start_time
    
    print(f"\n[OK] Completed in {elapsed:.2f}s")
    print(f"  State: {result['state']}")
    print(f"  Alive: {result['alive']:.4f}")
    print(f"  Emergence Score: {result['emergence_score']:.4f}")
    
    # Generate visualization
    grid_np = np.array(lenia.grid)
    h, w = grid_np.shape
    
    # Normalize
    grid_norm = ((grid_np - grid_np.min()) / (grid_np.max() - grid_np.min() + 1e-8) * 255).astype(np.uint8)
    
    # Color mapping
    img_array = np.zeros((h, w, 3), dtype=np.uint8)
    img_array[:, :, 0] = (grid_norm * 0.3).astype(np.uint8)
    img_array[:, :, 1] = (grid_norm * 0.8).astype(np.uint8)
    img_array[:, :, 2] = grid_norm
    
    img = Image.fromarray(img_array, 'RGB')
    
    # Scale up
    scale = max(2, 512 // max(h, w))
    if scale > 1:
        img = img.resize((w * scale, h * scale), Image.NEAREST)
    
    # Save
    output_dir = Path('D:/emergence_experiments')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = int(time.time())
    filename = f'lenia_R{R}_mu{mu:.3f}_{timestamp}.png'
    output_path = output_dir / filename
    
    img.save(output_path)
    print(f"  Saved: {output_path}")
    
    return {
        'grid': grid_np,
        'result': result,
        'image_path': str(output_path),
        'elapsed': elapsed
    }


def run_creature_gallery():
    """运行经典生物画廊"""
    
    creatures = {
        'Orbium': {'R': 13, 'mu': 0.15, 'sigma': 0.014},
        'Geminium': {'R': 12, 'mu': 0.15, 'sigma': 0.013},
        'Hydrogeminium': {'R': 14, 'mu': 0.26, 'sigma': 0.036},
        'Scutium': {'R': 18, 'mu': 0.147, 'sigma': 0.015},
        'Gyroginium': {'R': 14, 'mu': 0.175, 'sigma': 0.027},
    }
    
    print("\n" + "="*60)
    print("LENIA CREATURE GALLERY")
    print("="*60)
    
    results = {}
    
    for name, params in creatures.items():
        print(f"\n[{name}]")
        try:
            result = run_lenia_experiment(
                R=params['R'],
                mu=params['mu'],
                sigma=params['sigma'],
                shape=(256, 256),
                steps=200
            )
            results[name] = result
        except Exception as e:
            print(f"  ERROR: {e}")
            results[name] = {'error': str(e)}
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for name, res in results.items():
        if 'error' in res:
            print(f"{name:<20}: ERROR")
        else:
            r = res['result']
            print(f"{name:<20}: State={r['state']:<10} Score={r['emergence_score']:.4f} Alive={r['alive']:.4f}")
    
    return results


if __name__ == '__main__':
    if not LENIA_AVAILABLE:
        print("Lenia not available. Please install dependencies:")
        print("  pip install jax jaxlib numpy pillow")
        sys.exit(1)
    
    import argparse
    parser = argparse.ArgumentParser(description='Run Lenia experiments')
    parser.add_argument('--gallery', action='store_true', help='Run creature gallery')
    parser.add_argument('--R', type=int, default=13, help='Radius parameter')
    parser.add_argument('--mu', type=float, default=0.15, help='Mu parameter')
    parser.add_argument('--sigma', type=float, default=0.014, help='Sigma parameter')
    parser.add_argument('--steps', type=int, default=200, help='Number of steps')
    
    args = parser.parse_args()
    
    if args.gallery:
        run_creature_gallery()
    else:
        run_lenia_experiment(
            R=args.R,
            mu=args.mu,
            sigma=args.sigma,
            steps=args.steps
        )
