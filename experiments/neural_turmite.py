"""
Neural Turmite - Learning Transition Rules

Concept: A neural network defines the transition rules of a Turmite.
We pre-compute the transition table from the NN, then run the simulation
using fast numpy array operations.

The neural network is randomly initialized (in future: trained via evolution).
"""

import numpy as np
from PIL import Image
import random
import jax
import jax.numpy as jnp
from pathlib import Path
import time

OUTPUT_DIR = Path('D:/emergence_experiments')
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)


def init_neural_rules(key, n_cell_states, n_internal_states, hidden_dim=16):
    """
    Initialize neural network and pre-compute the transition table.
    
    Returns transition table as a dict:
        rules[(cell_state, internal_state)] = (new_cell_state, turn, new_internal_state)
    where turn: 0=L, 1=R, 2=U
    """
    k1, k2 = jax.random.split(key)
    
    # Neural network: 2 inputs -> hidden -> combined output
    # Use larger initialization for more varied outputs
    w1 = jax.random.normal(k1, (hidden_dim, 2)) * 2.0
    b1 = jax.random.normal(jax.random.split(k1)[0], (hidden_dim,)) * 0.5
    
    output_dim = n_cell_states + 3 + n_internal_states
    w2 = jax.random.normal(k2, (output_dim, hidden_dim)) * 2.0
    b2 = jax.random.normal(jax.random.split(k2)[0], (output_dim,)) * 0.5
    
    # Pre-compute all transitions
    rules = {}
    for cell_state in range(n_cell_states):
        for internal_state in range(n_internal_states):
            # Normalize inputs
            x = jnp.array([
                cell_state / max(1, n_cell_states - 1),
                internal_state / max(1, n_internal_states - 1)
            ])
            
            # Forward pass
            h = jnp.maximum(0, w1 @ x + b1)
            out = w2 @ h + b2
            
            # Split outputs and use softmax + sampling for more variety
            cell_logits = out[:n_cell_states]
            turn_logits = out[n_cell_states:n_cell_states + 3]
            internal_logits = out[n_cell_states + 3:]
            
            # Softmax sampling (temperature=1)
            def sample_from_logits(logits, rng_key):
                probs = jax.nn.softmax(logits)
                return int(jax.random.choice(rng_key, len(logits), p=probs))
            
            k_cell, k_turn, k_int = jax.random.split(key, 3)
            new_cell = sample_from_logits(cell_logits, k_cell)
            turn = sample_from_logits(turn_logits, k_turn)
            new_internal = sample_from_logits(internal_logits, k_int)
            
            rules[(cell_state, internal_state)] = (new_cell, turn, new_internal)
    
    return rules


def run_neural_turmite(size=150, steps=10000, n_cell_states=2, n_internal_states=2,
                       rules=None, seed=None):
    """
    Run a neural turmite simulation using pre-computed rules.
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    if rules is None:
        key = jax.random.PRNGKey(seed or 0)
        rules = init_neural_rules(key, n_cell_states, n_internal_states)
    
    grid = np.zeros((size, size), dtype=np.int8)
    x, y = size // 2, size // 2
    direction = 0  # N, E, S, W
    internal_state = 0
    
    dx = [0, 1, 0, -1]   # N, E, S, W
    dy = [-1, 0, 1, 0]
    turn_effects = [-1, 1, 0]  # L, R, U (U = no change)
    
    for step in range(steps):
        cell_state = grid[y, x]
        
        # Lookup transition (from neural network)
        new_cell, turn, new_internal = rules[(cell_state, internal_state)]
        
        # Apply
        grid[y, x] = new_cell
        direction = (direction + turn_effects[turn]) % 4
        internal_state = new_internal
        
        # Move
        x = (x + dx[direction]) % size
        y = (y + dy[direction]) % size
    
    return grid, rules


def evaluate_complexity(grid):
    """Evaluate pattern complexity."""
    counts = np.bincount(grid.flatten())
    probs = counts / counts.sum()
    entropy = -np.sum(probs * np.log2(probs + 1e-10))
    
    variance = np.var(grid.astype(float))
    
    from scipy import ndimage
    edges = ndimage.sobel(grid.astype(float))
    edge_score = np.mean(np.abs(edges))
    
    h, w = grid.shape
    h_sym = np.mean(grid[:h//2] == np.flipud(grid[h//2:]))
    v_sym = np.mean(grid[:, :w//2] == np.fliplr(grid[:, w//2:]))
    asymmetry = 1 - max(h_sym, v_sym)
    
    score = entropy * 0.3 + variance * 0.2 + edge_score * 0.3 + asymmetry * 0.2
    
    return float(score), {
        'entropy': float(entropy),
        'variance': float(variance),
        'edge_score': float(edge_score),
        'asymmetry': float(asymmetry),
    }


def visualize_grid(grid, scale=4):
    """Create image from grid."""
    colors = [
        (20, 20, 40),      # state 0: dark
        (100, 180, 255),   # state 1: blue
        (255, 150, 100),   # state 2: orange
        (150, 255, 150),   # state 3: green
    ]
    
    h, w = grid.shape
    img = Image.new('RGB', (w * scale, h * scale), (10, 10, 20))
    pixels = img.load()
    
    for y in range(h):
        for x in range(w):
            c = colors[grid[y, x] % len(colors)]
            for dy in range(scale):
                for dx in range(scale):
                    pixels[x * scale + dx, y * scale + dy] = c
    
    return img


def explore_neural_turmites(n_experiments=10):
    """Run multiple neural turmite experiments."""
    results = []
    
    for i in range(n_experiments):
        seed = i * 1000
        n_cells = random.choice([2, 3, 4])
        n_internal = random.choice([2, 3])
        
        key = jax.random.PRNGKey(seed)
        rules = init_neural_rules(key, n_cells, n_internal)
        grid, _ = run_neural_turmite(size=150, steps=12000, rules=rules)
        
        score, details = evaluate_complexity(grid)
        
        img = visualize_grid(grid)
        path = OUTPUT_DIR / f'neural_turmite_{i}_{score:.2f}.png'
        img.save(path)
        
        results.append({
            'seed': seed,
            'n_cells': n_cells,
            'n_internal': n_internal,
            'score': score,
            'details': details,
            'image_path': str(path),
        })
        
        print(f"Exp {i+1}: cells={n_cells}, internal={n_internal}, score={score:.3f}")
    
    return results


if __name__ == '__main__':
    print("=== Neural Turmite Explorer ===\n")
    
    t0 = time.time()
    results = explore_neural_turmites(10)
    elapsed = time.time() - t0
    
    best = max(results, key=lambda r: r['score'])
    print(f"\nCompleted in {elapsed:.1f}s")
    print(f"Best experiment: seed={best['seed']}, score={best['score']:.3f}")
    print(f"Details: entropy={best['details']['entropy']:.2f}, "
          f"variance={best['details']['variance']:.2f}, "
          f"edge={best['details']['edge_score']:.3f}, "
          f"asymmetry={best['details']['asymmetry']:.2f}")
    print(f"Saved to: {OUTPUT_DIR}")
