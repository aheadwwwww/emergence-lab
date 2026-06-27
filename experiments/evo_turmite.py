"""
Evolutionary Search for Complex Turmite Rules

Use genetic algorithm to find transition rules that produce
visually complex emergent patterns.

Fitness = pattern complexity (entropy + edge density + asymmetry)
"""

import numpy as np
from PIL import Image
import random
from pathlib import Path
import time
from scipy import ndimage

OUTPUT_DIR = Path('D:/emergence_experiments')
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)


def generate_random_rules(n_cell_states, n_internal_states):
    """Generate random transition rules."""
    rules = {}
    for cs in range(n_cell_states):
        for iss in range(n_internal_states):
            rules[(cs, iss)] = (
                random.randint(0, n_cell_states - 1),  # new cell state
                random.choice([0, 1, 2]),               # turn: L, R, U
                random.randint(0, n_internal_states - 1) # new internal state
            )
    return rules


def run_turmite(size, steps, rules, n_cell_states, n_internal_states):
    """Run turmite simulation."""
    grid = np.zeros((size, size), dtype=np.int8)
    x, y = size // 2, size // 2
    direction = 0
    internal_state = 0
    
    dx = [0, 1, 0, -1]
    dy = [-1, 0, 1, 0]
    turn_effects = [-1, 1, 0]
    
    for _ in range(steps):
        cs = grid[y, x]
        new_cell, turn, new_int = rules[(cs, internal_state)]
        grid[y, x] = new_cell
        direction = (direction + turn_effects[turn]) % 4
        internal_state = new_int
        x = (x + dx[direction]) % size
        y = (y + dy[direction]) % size
    
    return grid


def fitness(grid):
    """
    Compute fitness score for a grid pattern.
    Higher = more visually interesting/complex.
    """
    counts = np.bincount(grid.flatten())
    probs = counts / counts.sum()
    entropy = -np.sum(probs * np.log2(probs + 1e-10))
    
    variance = np.var(grid.astype(float))
    
    edges = ndimage.sobel(grid.astype(float))
    edge_score = np.mean(np.abs(edges))
    
    h, w = grid.shape
    h_sym = np.mean(grid[:h//2] == np.flipud(grid[h//2:]))
    v_sym = np.mean(grid[:, :w//2] == np.fliplr(grid[:, w//2:]))
    asymmetry = 1 - max(h_sym, v_sym)
    
    # Density bonus: patterns should have some structure but not be empty
    density = np.mean(grid > 0)
    density_bonus = 1.0 if 0.05 < density < 0.8 else 0.5
    
    return entropy * 0.25 + variance * 0.15 + edge_score * 0.35 + asymmetry * 0.25 * density_bonus


def mutate_rules(rules, n_cell_states, n_internal_states, mutation_rate=0.1):
    """Mutate transition rules."""
    new_rules = dict(rules)
    for key in rules:
        if random.random() < mutation_rate:
            new_rules[key] = (
                random.randint(0, n_cell_states - 1),
                random.choice([0, 1, 2]),
                random.randint(0, n_internal_states - 1)
            )
    return new_rules


def crossover_rules(rules1, rules2):
    """Crossover two rule sets."""
    child = {}
    for key in rules1:
        child[key] = rules1[key] if random.random() < 0.5 else rules2[key]
    return child


def evolve_turmites(n_cell_states=3, n_internal_states=2,
                    population_size=20, generations=10,
                    size=100, steps=8000):
    """
    Evolve turmite rules to maximize pattern complexity.
    """
    # Initialize population
    population = [generate_random_rules(n_cell_states, n_internal_states) 
                  for _ in range(population_size)]
    
    best_overall = None
    best_score = -1
    
    for gen in range(generations):
        # Evaluate fitness
        scores = []
        for i, rules in enumerate(population):
            grid = run_turmite(size, steps, rules, n_cell_states, n_internal_states)
            score = fitness(grid)
            scores.append((score, i, rules, grid))
        
        scores.sort(reverse=True, key=lambda x: x[0])
        
        if scores[0][0] > best_score:
            best_score = scores[0][0]
            best_overall = scores[0]
        
        print(f"Gen {gen+1}: best={scores[0][0]:.3f}, avg={np.mean([s[0] for s in scores]):.3f}, "
              f"worst={scores[-1][0]:.3f}")
        
        # Selection: keep top 40%
        elite_count = max(2, population_size // 5)
        elites = [scores[i][2] for i in range(elite_count)]
        
        # Create next generation
        new_population = elites[:]  # Elitism
        
        while len(new_population) < population_size:
            # Tournament selection
            p1 = random.choice(elites)
            p2 = random.choice(elites)
            child = crossover_rules(p1, p2)
            child = mutate_rules(child, n_cell_states, n_internal_states, 
                                mutation_rate=0.05 + 0.1 * (1 - gen/generations))
            new_population.append(child)
        
        population = new_population
    
    return best_overall, best_score


def visualize_grid(grid, scale=4):
    """Create image from grid."""
    colors = [
        (20, 20, 40),
        (100, 180, 255),
        (255, 150, 100),
        (150, 255, 150),
        (255, 200, 50),
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


if __name__ == '__main__':
    print("=== Evolutionary Turmite Search ===\n")
    
    configs = [
        (2, 2, "binary ant"),
        (3, 2, "3-color"),
        (4, 2, "4-color"),
        (2, 3, "2-state"),
        (3, 3, "3x3"),
    ]
    
    for n_cells, n_internal, label in configs:
        print(f"\n--- {label} ({n_cells} colors × {n_internal} states) ---")
        t0 = time.time()
        
        (score, idx, rules, grid), best_score = evolve_turmites(
            n_cell_states=n_cells,
            n_internal_states=n_internal,
            population_size=20,
            generations=10,
            size=100,
            steps=8000
        )
        
        elapsed = time.time() - t0
        print(f"  Best score: {best_score:.3f} ({elapsed:.1f}s)")
        
        # Save best result
        img = visualize_grid(grid)
        path = OUTPUT_DIR / f'evo_turmite_{label.replace(" ", "_")}_{best_score:.3f}.png'
        img.save(path)
        print(f"  Saved: {path}")
    
    print("\n=== Done ===")
