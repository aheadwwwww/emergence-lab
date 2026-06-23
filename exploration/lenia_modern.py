"""
Lenia: A Simple Modern Implementation
Based on Bert Chan's original concept (Chakazul/Lenia)
Lenia = continuous cellular automata with smooth dynamics

Core idea:
- State is continuous (not binary like Conway)
- Growth kernel (K) and its convolution with field
- Update is smooth: A_{t+1} = f(A_t + dt * G * K)
where G = growth mapping, K = kernel
"""
import numpy as np
from scipy.ndimage import convolve
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

def gaussian_kernel(size, sigma, mu=None):
    """Create a 2D "ring" kernel (difference of two Gaussians)"""
    if mu is None:
        mu = sigma * 1.5
    xs = np.linspace(-size//2, size//2, size)
    ys = np.linspace(-size//2, size//2, size)
    x, y = np.meshgrid(xs, ys)
    d = np.sqrt(x**2 + y**2)
    
    # Ring = inner Gaussian - outer Gaussian
    inner = np.exp(-((d - mu) / sigma)**2)
    outer = np.exp(-((d - mu) / (sigma * 1.5))**2)
    kernel = inner - outer
    
    # Normalize
    kernel -= kernel.mean()
    kernel /= np.abs(kernel).sum()
    return kernel

def growth_function(u, mu=0.15, sigma=0.015):
    """Growth mapping: determines how concentrations change.
    
    Bell-shaped: peak growth at mu, death at extremes.
    This is the key to Lenia's complex behavior.
    """
    return 2 * np.exp(-((u - mu)**2) / (2 * sigma**2)) - 1

class Lenia:
    def __init__(self, size=256, kernel_size=41, sigma=8, mu=0.15, growth_sigma=0.015, dt=0.1):
        self.size = size
        self.dt = dt
        self.mu = mu
        self.growth_sigma = growth_sigma
        
        # Create kernel
        self.kernel = gaussian_kernel(kernel_size, sigma)
        
        # Initialize field
        self.field = np.zeros((size, size), dtype=np.float64)
        
    def seed_orbium(self, cx=None, cy=None):
        """Place an Orbium-like creature pattern"""
        if cx is None:
            cx = self.size // 2
        if cy is None:
            cy = self.size // 2
        
        # Create a small multi-lobed pattern
        r = 10
        for angle in np.linspace(0, 2*np.pi, 6, endpoint=False):
            x = int(cx + r * np.cos(angle))
            y = int(cy + r * np.sin(angle))
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        dist = np.sqrt(dx**2 + dy**2)
                        if dist <= 3:
                            self.field[ny, nx] = np.clip(1.0 - dist/3, 0, 1)
        
        # Add central body
        for dx in range(-5, 6):
            for dy in range(-5, 6):
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    dist = np.sqrt(dx**2 + dy**2)
                    if dist <= 5:
                        self.field[ny, nx] = np.clip(0.5 * (1.0 - dist/5), 0, 1)
    
    def seed_random(self, density=0.3):
        """Seed with random noise"""
        self.field = np.random.random((self.size, self.size)) * density
    
    def seed_donut(self, cx=None, cy=None, inner_r=8, outer_r=15):
        """Seed with a ring pattern"""
        if cx is None:
            cx = self.size // 2
        if cy is None:
            cy = self.size // 2
        
        for x in range(self.size):
            for y in range(self.size):
                d = np.sqrt((x - cx)**2 + (y - cy)**2)
                if inner_r <= d <= outer_r:
                    self.field[y, x] = 0.8
    
    def step(self):
        """Single Lenia update step"""
        # Convolve field with kernel
        U = convolve(self.field, self.kernel, mode='wrap')
        
        # Apply growth mapping
        G = growth_function(U, self.mu, self.growth_sigma)
        
        # Update (clamp to [0, 1])
        self.field = np.clip(self.field + self.dt * G, 0, 1)
    
    def run(self, steps=200):
        """Run simulation for given steps, return history"""
        history = [self.field.copy()]
        for _ in range(steps):
            self.step()
            history.append(self.field.copy())
        return history
    
    def create_gif(self, steps=200, filename='lenia.gif', interval=50):
        """Create animated GIF"""
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_xticks([])
        ax.set_yticks([])
        
        im = ax.imshow(self.field, cmap='inferno', vmin=0, vmax=1, animated=True)
        plt.tight_layout()
        
        def animate(i):
            self.step()
            im.set_array(self.field)
            return [im]
        
        anim = FuncAnimation(fig, animate, frames=steps, interval=interval, blit=True)
        writer = PillowWriter(fps=20)
        anim.save(filename, writer=writer)
        plt.close(fig)
        print(f"Saved {filename}")


if __name__ == '__main__':
    print("=" * 60)
    print("Lenia: Continuous Cellular Automata")
    print("=" * 60)
    
    # Experiment 1: Orbium-like creature
    print("\n[1/4] Testing Orbium pattern...")
    l = Lenia(size=200, kernel_size=41, sigma=8, mu=0.15, growth_sigma=0.015, dt=0.1)
    l.seed_orbium()
    
    # Check if it's alive
    initial_mass = l.field.sum()
    for _ in range(50):
        l.step()
    final_mass = l.field.sum()
    print(f"  Initial mass: {initial_mass:.1f}")
    print(f"  Final mass:   {final_mass:.1f}")
    print(f"  Alive: {'Yes' if final_mass > 1 else 'No'}")
    
    # Experiment 2: Random soup (try to find spontaneous life)
    print("\n[2/4] Testing random soup...")
    params_to_try = [
        (8, 0.15, 0.015),
        (10, 0.12, 0.01),
        (6, 0.18, 0.02),
        (13, 0.1, 0.008),
    ]
    
    for sigma, mu, gsigma in params_to_try:
        l = Lenia(size=100, kernel_size=41, sigma=sigma, mu=mu, growth_sigma=gsigma, dt=0.1)
        l.seed_random(density=0.3)
        initial = l.field.sum()
        for _ in range(100):
            l.step()
        final = l.field.sum()
        
        # Measure "aliveness": how much structure remains
        alive_ratio = final / initial if initial > 0 else 0
        print(f"  sigma={sigma}, mu={mu}, gsigma={gsigma}: alive_ratio={alive_ratio:.3f}")
    
    # Experiment 3: Ring pattern
    print("\n[3/4] Testing ring/donut pattern...")
    l = Lenia(size=200, kernel_size=41, sigma=10, mu=0.13, growth_sigma=0.012, dt=0.1)
    l.seed_donut(inner_r=10, outer_r=20)
    initial = l.field.sum()
    for _ in range(100):
        l.step()
    final = l.field.sum()
    print(f"  Alive ratio: {final/initial:.3f}" if initial > 0 else "  Dead")
    
    # Experiment 4: Generate GIF of best pattern
    print("\n[4/4] Generating Lenia GIF...")
    l = Lenia(size=200, kernel_size=41, sigma=10, mu=0.13, growth_sigma=0.012, dt=0.1)
    l.seed_orbium()
    try:
        l.create_gif(steps=200, filename='exploration/lenia_output.gif', interval=30)
        print("  [OK] GIF generated!")
    except Exception as e:
        print(f"  [WARN] GIF generation failed: {e}")
        # Save just the final frame
        for _ in range(200):
            l.step()
        plt.figure(figsize=(6, 6))
        plt.imshow(l.field, cmap='inferno')
        plt.axis('off')
        plt.title('Lenia (T=200)')
        plt.tight_layout()
        plt.savefig('exploration/lenia_final_frame.png')
        plt.close()
        print("  Saved final frame as PNG instead")
    
    print("\n" + "=" * 60)
    print("Exploration complete!")
    print("=" * 60)
