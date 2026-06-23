"""
Lenia - Continuous Cellular Automata for Artificial Life

Lenia is a continuous generalization of Conway's Game of Life,
developed by Bert Wang-Chak Chan (2015-2019).

Unlike discrete CA, Lenia uses:
- Continuous state [0,1]
- Continuous space/time
- Smooth kernel-based neighborhood
- Growth function with "sweet spot"

This creates stunning lifelike, open-ended patterns.
Related to curiosity map nodes: #020 Artificial Life, #022 Open-Endedness
"""

import numpy as np
from PIL import Image, ImageDraw
import colorsys
import os

class Lenia:
    """
    Continuous cellular automaton with:
    - Smooth neighborhood kernel
    - Growth function with upper/lower bounds
    - Multiple channels for complex dynamics
    """
    
    def __init__(self, size=256, kernel_radius=13, dt=0.1):
        self.size = size
        self.R = kernel_radius
        self.dt = dt
        self.generation = 0
        
        # Kernel: Gaussian ring (mexican hat derivative)
        # Creates a donut-shaped neighborhood
        xs = np.linspace(-self.R, self.R, 2 * self.R + 1)
        ys = np.linspace(-self.R, self.R, 2 * self.R + 1)
        X, Y = np.meshgrid(xs, ys)
        D = np.sqrt(X**2 + Y**2)
        
        # Normalized distance r/R
        r = D / self.R
        
        # Kernel: bump function with support on [0, 1]
        # K(r) = exp(α - α/(4r(1-r))) for r in (0,1), 0 otherwise
        self.kernel = np.zeros_like(D)
        mask = (r > 0) & (r < 1)
        alpha = 4.0
        self.kernel[mask] = np.exp(alpha - alpha / (4 * r[mask] * (1 - r[mask])))
        self.kernel = self.kernel / self.kernel.sum()  # Normalize
        
        # Growth function parameters
        # μ: center of growth window
        # σ: width of growth window
        # Growth happens when local density is in [μ-3σ, μ+3σ]
        self.mu = 0.13   # Center of growth sweet spot (lower to match typical U)
        self.sigma = 0.022  # Width of growth window (wider = more forgiving)
    
    def growth_function(self, u):
        """Gaussian growth function G(u) = 2*exp(-(u-μ)^2/(2σ^2)) - 1"""
        return 2 * np.exp(-(u - self.mu)**2 / (2 * self.sigma**2)) - 1
    
    def init_orbium(self):
        """Initialize with Orbium - a classic Lenia glider pattern"""
        self.world = np.zeros((self.size, self.size))
        
        # Orbium parameters (a self-propelling pattern)
        cx, cy = self.size // 2, self.size // 2
        
        # Create multiple concentric rings to seed patterns
        for y in range(self.size):
            for x in range(self.size):
                dx = x - cx
                dy = y - cy
                d = np.sqrt(dx**2 + dy**2)
                
                # Create ring patterns
                for ring_r in range(10, 100, 15):
                    if abs(d - ring_r) < 5:
                        self.world[y, x] = 0.8
        
        # Add some random seeds to see what emerges
        np.random.seed(42)
        seeds = np.random.rand(self.size, self.size)
        self.world[seeds < 0.001] = np.random.rand() * 0.5 + 0.3
    
    def init_random(self, density=0.05):
        """Initialize with random noise"""
        self.world = np.zeros((self.size, self.size))
        mask = np.random.rand(self.size, self.size) < density
        self.world[mask] = np.random.rand(np.sum(mask)) * 0.5 + 0.25
    
    def init_cells(self):
        """Initialize with spaced cell-like blobs"""
        self.world = np.zeros((self.size, self.size))
        
        xs = np.arange(self.size)
        ys = np.arange(self.size)
        X, Y = np.meshgrid(xs, ys)
        
        # Create cell-like initial conditions with higher density
        for cy in range(15, self.size, 20):
            for cx in range(15, self.size, 20):
                D = np.sqrt((X - cx)**2 + (Y - cy)**2)
                self.world += 0.9 * np.exp(-D**2 / 80)  # Wider blobs
        
        self.world = np.clip(self.world, 0, 1)
    
    def step(self):
        """One Lenia update step"""
        from scipy.ndimage import convolve
        
        # Convolve with kernel to get local density
        U = convolve(self.world, self.kernel, mode='wrap')
        
        # Apply growth function
        G = self.growth_function(U)
        
        # Update state
        self.world = np.clip(self.world + self.dt * G, 0, 1)
        self.generation += 1
    
    def run(self, steps=500, save_interval=50):
        """Run simulation and save frames"""
        output_dir = os.path.dirname(os.path.abspath(__file__))
        frames = []
        
        for step in range(steps):
            self.step()
            
            if step % save_interval == 0 or step == steps - 1:
                frame = self.render_world()
                frames.append(frame)
                print(f'  Generation {self.generation}: mean={self.world.mean():.4f}, alive={(self.world > 0.1).mean():.4%}')
        
        # Create multi-panel image
        self.save_timeline(frames, output_dir, save_interval)
        return frames
    
    def render_world(self):
        """Render current world state as RGB image"""
        img = np.zeros((self.size, self.size, 3), dtype=np.uint8)
        
        w = self.world
        # Map state to color: blue(0) -> green(0.3) -> yellow(0.5) -> red(0.7) -> white(1.0)
        h = 0.6 - 0.5 * w  # Hue: blue to red
        s = 0.8 * np.ones_like(w)
        v = np.clip(w * 1.5, 0.3, 1.0)
        
        for y in range(self.size):
            for x in range(self.size):
                r, g, b = colorsys.hsv_to_rgb(h[y, x], s[y, x], v[y, x])
                img[y, x, 0] = int(r * 255)
                img[y, x, 1] = int(g * 255)
                img[y, x, 2] = int(b * 255)
        
        return img
    
    def save_timeline(self, frames, output_dir, save_interval):
        """Create timeline image with multiple frames"""
        n_frames = len(frames)
        cols = min(4, n_frames)
        rows = (n_frames + cols - 1) // cols
        
        padding = 4
        frame_size = self.size
        total_w = cols * (frame_size + padding) + padding
        total_h = rows * (frame_size + padding) + padding + 40  # Extra for title
        
        canvas = np.zeros((total_h, total_w, 3), dtype=np.uint8)
        canvas[:, :] = (10, 10, 20)
        
        for i, frame in enumerate(frames):
            row = i // cols
            col = i % cols
            y0 = padding + row * (frame_size + padding)
            x0 = padding + col * (frame_size + padding)
            canvas[y0:y0+frame_size, x0:x0+frame_size] = frame
            
            # Generation label
            gen = i * save_interval
            label_img = Image.fromarray(canvas)
            draw = ImageDraw.Draw(label_img)
            draw.text((x0 + 5, y0 + 5), f"t={gen}", fill=(255, 255, 255))
            canvas = np.array(label_img)
        
        # Title
        label_img = Image.fromarray(canvas)
        draw = ImageDraw.Draw(label_img)
        title_y = rows * (frame_size + padding) + padding + 5
        draw.text((padding + 5, title_y), 
                  f"Lenia - Continuous Artificial Life (μ={self.mu}, σ={self.sigma})", 
                  fill=(255, 200, 100))
        canvas = np.array(label_img)
        
        output_path = os.path.join(output_dir, 'lenia.png')
        Image.fromarray(canvas).save(output_path)
        print(f'Saved: {output_path}')

def analyze_open_endedness(world_history):
    """Analyze whether the system shows signs of open-endedness"""
    print('\n=== Open-Endedness Analysis ===')
    
    # Measure complexity over time
    complexities = []
    diversities = []
    
    for w in world_history:
        # Shannon entropy as complexity proxy
        hist, _ = np.histogram(w.flatten(), bins=20, range=(0, 1))
        hist = hist / hist.sum()
        hist = hist[hist > 0]  # Remove zeros
        entropy = -np.sum(hist * np.log2(hist))
        complexities.append(entropy)
        
        # Diversity = fraction of non-zero cells
        diversity = (w > 0.01).mean()
        diversities.append(diversity)
    
    complexity_change = complexities[-1] - complexities[0] if len(complexities) > 1 else 0
    diversity_change = diversities[-1] - diversities[0] if len(diversities) > 1 else 0
    
    print(f'  Complexity (entropy): {complexities[0]:.2f} → {complexities[-1]:.2f} (Δ={complexity_change:+.2f})')
    print(f'  Diversity (alive%):   {diversities[0]:.1%} → {diversities[-1]:.1%} (Δ={diversity_change:+.3%})')
    
    if complexity_change > 0:
        print('  ✓ System shows increasing complexity')
    else:
        print('  ○ System complexity is stable/declining - try different μ,σ')
    
    return complexities, diversities


if __name__ == '__main__':
    print("=== Lenia: Continuous Artificial Life ===\n")
    print("Inspired by Bert Wang-Chak Chan's Lenia (2015)")
    print("A continuous generalization of Conway's Game of Life")
    print()
    
    # Run with Orbium-friendly parameters
    lenia = Lenia(size=200, kernel_radius=13, dt=0.1)
    lenia.mu = 0.15
    lenia.sigma = 0.015
    
    print("Initializing with cell-like blobs (dense pattern)...")
    lenia.init_cells()
    
    print(f"Initial: mean={lenia.world.mean():.4f}, max={lenia.world.max():.4f}, alive={(lenia.world > 0.1).mean():.1%}")
    print("Running 300 generations...")
    frames = lenia.run(steps=300, save_interval=50)
    
    print('\nAnalysis:')
    # Collect world history for analysis
    world_history = [lenia.world.copy()]
    
    # Quick analysis
    complexity_hist, _ = np.histogram(lenia.world.flatten(), bins=20, range=(0, 1))
    complexity_hist = complexity_hist / complexity_hist.sum()
    complexity_hist = complexity_hist[complexity_hist > 0]
    entropy = -np.sum(complexity_hist * np.log2(complexity_hist))
    
    print(f'  Final entropy: {entropy:.3f} bits')
    print(f'  Final alive fraction: {(lenia.world > 0.05).mean():.2%}')
    print(f'  Mean state: {lenia.world.mean():.4f}')
    print()
    
    print("Key ideas:")
    print("  - Lenia generalizes CA from discrete to continuous")
    print("  - The 'growth function' creates a sweet-spot for life")
    print("  - Too sparse -> dies; too dense -> dies; just right -> thrives")
    print("  - Open-endedness emerges from the continuous dynamics")
    print()
    print("Done!")
