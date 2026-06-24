"""
Wave Function Collapse — minimal Python implementation
Exploration: WFC as an emergence mechanism
- Local constraints → global patterns
- Superposition collapse as a model of emergence
- Connects to: #001 Emergence, #003 Edge of Chaos, #022 Open-Endedness
"""
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt

def extract_patterns(grid, N=2):
    """Extract all NxN patterns from a grid."""
    h, w = grid.shape
    patterns = []
    for y in range(h - N + 1):
        for x in range(w - N + 1):
            pat = tuple(grid[y:y+N, x:x+N].flatten())
            patterns.append(pat)
    return patterns

def build_compatibility(patterns, N=2):
    """Build adjacency rules: which patterns can be next to each other."""
    pattern_set = list(set(patterns))
    pattern_idx = {p: i for i, p in enumerate(pattern_set)}
    n = len(pattern_set)
    
    # Horizontal compatibility: pattern A can be to the left of pattern B
    # if the right N-1 columns of A match the left N-1 columns of B
    h_comp = np.zeros((n, n), dtype=bool)
    v_comp = np.zeros((n, n), dtype=bool)
    
    for i, a in enumerate(pattern_set):
        a_grid = np.array(a).reshape(N, N)
        for j, b in enumerate(pattern_set):
            b_grid = np.array(b).reshape(N, N)
            # Horizontal: right N-1 cols of a == left N-1 cols of b
            if N > 1 and np.array_equal(a_grid[:, 1:], b_grid[:, :-1]):
                h_comp[i, j] = True
            # Vertical: bottom N-1 rows of a == top N-1 rows of b
            if N > 1 and np.array_equal(a_grid[1:, :], b_grid[:-1, :]):
                v_comp[i, j] = True
    
    return pattern_set, pattern_idx, h_comp, v_comp

def wfc_collapse(input_grid, output_size=(20, 20), N=2, max_attempts=10):
    """Run WFC to generate output similar to input."""
    patterns = extract_patterns(input_grid, N)
    pattern_set, pattern_idx, h_comp, v_comp = build_compatibility(patterns, N)
    n_patterns = len(pattern_set)
    
    H, W = output_size
    
    for attempt in range(max_attempts):
        # Wave: HxW cells, each is a boolean array of possible patterns
        wave = np.ones((H, W, n_patterns), dtype=bool)
        observed = np.full((H, W), -1, dtype=int)
        
        while True:
            # Find cell with minimum entropy (fewest possible patterns)
            min_entropy = n_patterns + 1
            min_cell = None
            for y in range(H):
                for x in range(W):
                    if observed[y, x] >= 0:
                        continue
                    count = wave[y, x].sum()
                    if count == 0:
                        min_cell = None  # contradiction
                        break
                    if count < min_entropy:
                        min_entropy = count
                        min_cell = (y, x)
                if min_cell is None:
                    break
            
            if min_cell is None:
                break  # contradiction, retry
            
            if min_entropy == n_patterns + 1:
                break  # all observed
            
            # Collapse the chosen cell
            y, x = min_cell
            possible = np.where(wave[y, x])[0]
            # Weight by pattern frequency
            freq = np.array([patterns.count(pattern_set[p]) for p in possible], dtype=float)
            freq /= freq.sum()
            chosen = np.random.choice(possible, p=freq)
            
            wave[y, x, :] = False
            wave[y, x, chosen] = True
            observed[y, x] = chosen
            
            # Propagate constraints
            stack = [(y, x)]
            while stack:
                cy, cx = stack.pop()
                c_pattern = observed[cy, cx]
                
                # Check neighbors
                for dy, dx, comp in [(-1, 0, v_comp), (1, 0, v_comp), 
                                      (0, -1, h_comp), (0, 1, h_comp)]:
                    ny, nx = cy + dy, cx + dx
                    if not (0 <= ny < H and 0 <= nx < W):
                        continue
                    if observed[ny, nx] >= 0:
                        continue
                    
                    # Determine direction: if checking cell below, current is "above"
                    if dy == -1:  # neighbor above, current below
                        allowed = comp[:, c_pattern]
                    elif dy == 1:  # neighbor below, current above
                        allowed = comp[c_pattern, :]
                    elif dx == -1:  # neighbor left, current right
                        allowed = comp[:, c_pattern]
                    else:  # neighbor right, current left
                        allowed = comp[c_pattern, :]
                    
                    old_count = wave[ny, nx].sum()
                    wave[ny, nx] &= allowed
                    new_count = wave[ny, nx].sum()
                    
                    if new_count == 0:
                        min_cell = None  # contradiction
                        break
                    if new_count < old_count:
                        stack.append((ny, nx))
                
                if min_cell is None:
                    break
            
            if min_cell is None:
                break
        
        if min_cell is not None:
            # Success! Build output
            output = np.zeros((H, W), dtype=int)
            for y in range(H):
                for x in range(W):
                    if observed[y, x] >= 0:
                        p = pattern_set[observed[y, x]]
                        output[y, x] = p[0]  # top-left pixel of pattern
                    else:
                        # Fill unobserved with most likely
                        possible = np.where(wave[y, x])[0]
                        if len(possible) > 0:
                            output[y, x] = pattern_set[possible[0]][0]
            return output, attempt + 1
    
    return None, max_attempts

def main():
    # Create a simple input pattern
    input_grid = np.array([
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 1, 0, 1, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0],
    ])
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # Show input
    axes[0, 0].imshow(input_grid, cmap='binary')
    axes[0, 0].set_title('Input Pattern (5x5)')
    
    # Run WFC with different N values
    for idx, N in enumerate([2, 3]):
        output, attempts = wfc_collapse(input_grid, output_size=(30, 30), N=N)
        if output is not None:
            axes[0, idx+1].imshow(output, cmap='binary')
            axes[0, idx+1].set_title(f'WFC Output N={N} ({attempts} attempts)')
        else:
            axes[0, idx+1].text(0.5, 0.5, 'Failed', ha='center', va='center')
            axes[0, idx+1].set_title(f'WFC N={N} (failed)')
    
    # More complex input: checkerboard variant
    input2 = np.array([
        [0, 1, 0, 1, 0],
        [1, 0, 1, 0, 1],
        [0, 1, 0, 1, 0],
        [1, 0, 1, 0, 1],
        [0, 1, 0, 1, 0],
    ])
    
    axes[1, 0].imshow(input2, cmap='binary')
    axes[1, 0].set_title('Input Pattern 2 (checkerboard)')
    
    for idx, N in enumerate([2, 3]):
        output, attempts = wfc_collapse(input2, output_size=(30, 30), N=N)
        if output is not None:
            axes[1, idx+1].imshow(output, cmap='binary')
            axes[1, idx+1].set_title(f'WFC Output N={N} ({attempts} attempts)')
        else:
            axes[1, idx+1].text(0.5, 0.5, 'Failed', ha='center', va='center')
            axes[1, idx+1].set_title(f'WFC N={N} (failed)')
    
    plt.suptitle('Wave Function Collapse: Local Constraints → Global Patterns', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('experiments/wfc_demo.png', dpi=100, bbox_inches='tight')
    plt.close()
    print("Saved experiments/wfc_demo.png")

if __name__ == '__main__':
    main()
