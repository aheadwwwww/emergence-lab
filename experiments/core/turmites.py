"""
Turmites - 2D Turing Machines
A generalization of Langton's Ant with arbitrary state machines.

Turmites are Turing machines on a 2D grid. Each cell can have multiple states,
and the turmite has its own internal state. The transition rules are:
- Read current cell state + turmite state
- Write new cell state
- Turn (L/R/U/D) and move
- Update turmite state

This creates complex emergent patterns from simple state transition tables.
"""

import numpy as np
from PIL import Image
import random
from pathlib import Path
import time

OUTPUT_DIR = Path('D:/emergence_experiments')
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)


class Turmite:
    """
    A 2D Turing machine (Turmite).
    
    State is (x, y, direction, internal_state)
    Transition table maps (cell_state, internal_state) -> (new_cell_state, turn, new_internal_state)
    """
    
    DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # N, E, S, W
    TURNS = {'L': -1, 'R': 1, 'U': 0, 'N': 0}  # Turn left/right/about-face/none
    
    def __init__(self, x, y, n_cell_states=2, n_internal_states=2, rules=None):
        self.x = x
        self.y = y
        self.dir = 0  # Start facing North
        self.internal_state = 0
        
        self.n_cell_states = n_cell_states
        self.n_internal_states = n_internal_states
        
        if rules is None:
            # Generate random rules
            self.rules = self._generate_random_rules()
        else:
            self.rules = rules
    
    def _generate_random_rules(self):
        """Generate random transition rules."""
        rules = {}
        for cell_state in range(self.n_cell_states):
            for internal_state in range(self.n_internal_states):
                new_cell_state = random.randint(0, self.n_cell_states - 1)
                turn = random.choice(['L', 'R', 'U'])
                new_internal_state = random.randint(0, self.n_internal_states - 1)
                rules[(cell_state, internal_state)] = (new_cell_state, turn, new_internal_state)
        return rules
    
    def step(self, grid):
        """Execute one step of the turmite."""
        # Read current cell
        cell_state = grid[self.y, self.x]
        
        # Lookup transition
        key = (cell_state, self.internal_state)
        if key in self.rules:
            new_cell_state, turn, new_internal_state = self.rules[key]
        else:
            # Default behavior if rule not found
            new_cell_state = (cell_state + 1) % self.n_cell_states
            turn = 'R'
            new_internal_state = self.internal_state
        
        # Write new cell state
        grid[self.y, self.x] = new_cell_state
        
        # Turn
        self.dir = (self.dir + self.TURNS[turn]) % 4
        
        # Move
        dx, dy = self.DIRECTIONS[self.dir]
        self.x = (self.x + dx) % grid.shape[1]
        self.y = (self.y + dy) % grid.shape[0]
        
        # Update internal state
        self.internal_state = new_internal_state


def run_turmite(size=200, steps=10000, n_cell_states=2, n_internal_states=2, 
                rules=None, seed=None):
    """
    Run a turmite simulation.
    
    Args:
        size: Grid size (size x size)
        steps: Number of steps to simulate
        n_cell_states: Number of possible cell states
        n_internal_states: Number of internal turmite states
        rules: Transition rules (if None, generate random)
        seed: Random seed for reproducibility
    
    Returns:
        dict with 'grid', 'rules', 'steps'
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    grid = np.zeros((size, size), dtype=np.int8)
    turmite = Turmite(size // 2, size // 2, n_cell_states, n_internal_states, rules)
    
    for _ in range(steps):
        turmite.step(grid)
    
    return {
        'grid': grid,
        'rules': turmite.rules,
        'steps': steps,
        'n_cell_states': n_cell_states,
        'n_internal_states': n_internal_states
    }


def visualize_turmite(result, color_palette=None):
    """
    Visualize turmite result as an image.
    
    Args:
        result: Dict from run_turmite
        color_palette: List of RGB tuples (auto-generated if None)
    
    Returns:
        PIL Image
    """
    grid = result['grid']
    n_states = result['n_cell_states']
    
    if color_palette is None:
        # Generate a nice color palette
        color_palette = []
        for i in range(n_states):
            hue = i / n_states
            # HSV to RGB approximation
            r = int(255 * (0.5 + 0.5 * np.cos(2 * np.pi * (hue + 0))))
            g = int(255 * (0.5 + 0.5 * np.cos(2 * np.pi * (hue + 0.33))))
            b = int(255 * (0.5 + 0.5 * np.cos(2 * np.pi * (hue + 0.67))))
            color_palette.append((r, g, b))
    
    # Scale up for visibility
    scale = max(1, 800 // grid.shape[0])
    img = Image.new('RGB', (grid.shape[1] * scale, grid.shape[0] * scale))
    pixels = img.load()
    
    for y in range(grid.shape[0]):
        for x in range(grid.shape[1]):
            color = color_palette[grid[y, x] % len(color_palette)]
            for dy in range(scale):
                for dx in range(scale):
                    pixels[x * scale + dx, y * scale + dy] = color
    
    return img


def classify_pattern(grid):
    """
    Classify the pattern type based on spatial distribution.
    
    Returns one of: 'highway', 'symmetric', 'chaotic', 'sparse', 'dense'
    """
    filled = np.sum(grid > 0)
    total = grid.size
    density = filled / total
    
    # Check for highway (strong directional pattern)
    vertical_sym = np.mean(grid == np.flip(grid, axis=0))
    horizontal_sym = np.mean(grid == np.flip(grid, axis=1))
    
    if density < 0.1:
        return 'sparse'
    elif density > 0.7:
        return 'dense'
    elif vertical_sym > 0.7 or horizontal_sym > 0.7:
        return 'symmetric'
    elif np.std(grid[grid > 0]) > 0.5 * np.mean(grid[grid > 0]):
        return 'chaotic'
    else:
        return 'highway'


def explore_turmites(n_experiments=10, size=150, steps=15000):
    """
    Run multiple turmite experiments and find interesting patterns.
    
    Returns list of results with pattern classifications.
    """
    results = []
    
    for i in range(n_experiments):
        # Vary complexity
        n_cell_states = random.choice([2, 3, 4])
        n_internal_states = random.choice([2, 3, 4])
        
        result = run_turmite(
            size=size,
            steps=steps,
            n_cell_states=n_cell_states,
            n_internal_states=n_internal_states,
            seed=i * 1000
        )
        
        result['pattern_type'] = classify_pattern(result['grid'])
        result['seed'] = i * 1000
        
        # Save image
        img = visualize_turmite(result)
        timestamp = int(time.time())
        path = OUTPUT_DIR / f'turmite_{result["pattern_type"]}_{timestamp}_{i}.png'
        img.save(path)
        result['image_path'] = str(path)
        
        results.append(result)
        print(f"Experiment {i+1}/{n_experiments}: {result['pattern_type']} "
              f"(cells={n_cell_states}, internal={n_internal_states})")
    
    return results


def create_famous_turmite(turmite_type='langton'):
    """
    Create famous turmite configurations.
    
    Types:
    - 'langton': Classic Langton's Ant (binary, single state)
    - 'turmita': Simple highway builder
    - 'spiral': Spiral pattern generator
    """
    if turmite_type == 'langton':
        # Classic Langton's Ant as a turmite
        rules = {
            (0, 0): (1, 'R', 0),
            (1, 0): (0, 'L', 0),
        }
        return {'rules': rules, 'n_cell_states': 2, 'n_internal_states': 1}
    
    elif turmite_type == 'turmita':
        # Creates highways
        rules = {
            (0, 0): (1, 'R', 0),
            (1, 0): (1, 'L', 1),
            (1, 1): (0, 'R', 0),
        }
        return {'rules': rules, 'n_cell_states': 2, 'n_internal_states': 2}
    
    elif turmite_type == 'spiral':
        # Creates spiral patterns
        rules = {
            (0, 0): (1, 'R', 1),
            (1, 1): (0, 'L', 0),
            (0, 1): (1, 'L', 0),
            (1, 0): (0, 'R', 1),
        }
        return {'rules': rules, 'n_cell_states': 2, 'n_internal_states': 2}
    
    return None


if __name__ == '__main__':
    print("=== Turmite Explorer ===\n")
    
    # Run famous turmites
    print("1. Classic Langton's Ant:")
    config = create_famous_turmite('langton')
    result = run_turmite(size=200, steps=15000, **config, seed=42)
    result['pattern_type'] = classify_pattern(result['grid'])
    print(f"   Pattern: {result['pattern_type']}")
    img = visualize_turmite(result)
    path = OUTPUT_DIR / f'langton_ant_{int(time.time())}.png'
    img.save(path)
    print(f"   Saved: {path}\n")
    
    # Explore random turmites
    print("2. Exploring random turmites:")
    results = explore_turmites(n_experiments=5, size=150, steps=10000)
    
    # Summary
    print("\n=== Summary ===")
    pattern_counts = {}
    for r in results:
        pt = r['pattern_type']
        pattern_counts[pt] = pattern_counts.get(pt, 0) + 1
    
    for pt, count in sorted(pattern_counts.items()):
        print(f"{pt}: {count}")
