"""
Particle Life: Emergent "life-like" patterns from simple particle interactions

Based on the concept by Jeffrey Ventrella (clusters, 2017) and popularized
by the Particle Life project (>3000★ on GitHub).

Core mechanism:
- Multiple types of particles, each with an attraction/repulsion matrix
- Particles interact via pairwise forces within a radius
- Complex patterns (cells, swarms, amoebas) emerge from simple rules
- No explicit "life" rules — just physics-like forces

Key parameters:
- Attraction matrix: A[type_i][type_j] ∈ [-1, 1]
- Interaction radius: r_max
- Force magnitude: β
- Friction: η
- Half-radius: r_min (repulsion switches to attraction)
"""
import numpy as np
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import time


class ParticleLife:
    def __init__(self, n_types=4, n_particles=200, size=1.0,
                 r_max=0.1, beta=0.3, friction=0.5,
                 seed=42):
        self.n_types = n_types
        self.n_particles = n_particles
        self.size = size
        self.r_max = r_max
        self.beta = beta
        self.friction = friction
        
        rng = np.random.default_rng(seed)
        
        # Initialize positions
        self.positions = rng.random((n_particles, 2)) * size
        
        # Initialize velocities
        self.velocities = rng.standard_normal((n_particles, 2)) * 0.01
        
        # Assign types (equally distributed)
        self.types = np.array([i % n_types for i in range(n_particles)])
        
        # Random attraction matrix
        self.attraction = rng.uniform(-1, 1, (n_types, n_types))
        
        # Colors per type
        self.colors = plt.cm.tab10(np.linspace(0, 1, max(n_types, 1)))[:n_types]
    
    def step(self):
        """Single simulation step using pairwise forces"""
        n = self.n_particles
        
        # Compute all pairwise distances
        dists = cdist(self.positions, self.positions)
        
        # Force accumulator
        forces = np.zeros((n, 2))
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                
                d = dists[i, j]
                if d <= 0 or d > self.r_max:
                    continue
                
                ti, tj = self.types[i], self.types[j]
                a = self.attraction[ti, tj]
                
                # Force direction: from j to i
                direction = self.positions[i] - self.positions[j]
                direction /= d  # normalize
                
                if d < self.r_max / 2:
                    # Short range: stronger force
                    f = (d / (self.r_max / 2) - 1) * a
                else:
                    # Long range: linear decay
                    f = a * (1 - d / self.r_max)
                
                forces[i] += f * direction * self.beta / n
        
        # Update velocities with friction
        self.velocities = self.velocities * (1 - self.friction) + forces
        
        # Update positions (wrap around)
        self.positions += self.velocities
        self.positions %= self.size
    
    def run(self, steps=500):
        """Run simulation, return position history"""
        history = [self.positions.copy()]
        for _ in range(steps):
            self.step()
            history.append(self.positions.copy())
        return history
    
    def measure_clustering(self):
        """Measure degree of clustering (emergence metric)"""
        n = self.n_particles
        clusters = 0
        for i in range(n):
            ti = self.types[i]
            same_type_nearby = 0
            total_nearby = 0
            for j in range(n):
                if i == j:
                    continue
                d = np.linalg.norm(self.positions[i] - self.positions[j])
                # Wrap-aware distance
                d = min(d, self.size - d)
                if d < self.r_max:
                    total_nearby += 1
                    if self.types[j] == ti:
                        same_type_nearby += 1
            if total_nearby > 0:
                if same_type_nearby / total_nearby > 0.5:
                    clusters += 1
        return clusters / n
    
    def plot_frame(self, ax, positions=None):
        """Plot a single frame"""
        if positions is None:
            positions = self.positions
        
        ax.clear()
        ax.set_xlim(0, self.size)
        ax.set_ylim(0, self.size)
        
        for t in range(self.n_types):
            mask = self.types == t
            ax.scatter(positions[mask, 0], positions[mask, 1],
                      c=[self.colors[t]], s=10, alpha=0.7, label=f'Type {t}')
        
        ax.legend(loc='upper right', fontsize=6)
        ax.set_xticks([])
        ax.set_yticks([])
    
    def create_gif(self, steps=200, filename='particle_life.gif', interval=30):
        """Create animated GIF"""
        fig, ax = plt.subplots(figsize=(6, 6))
        
        def animate(i):
            self.step()
            self.plot_frame(ax)
            return []
        
        anim = FuncAnimation(fig, animate, frames=steps, interval=interval, blit=True)
        writer = PillowWriter(fps=20)
        anim.save(filename, writer=writer)
        plt.close(fig)
        print(f"Saved {filename}")


def parameter_sweep():
    """Explore how parameters affect emergent clustering"""
    print("=" * 60)
    print("Particle Life: Parameter Sweep")
    print("=" * 60)
    
    n_types = 4
    n_particles = 300
    size = 1.0
    
    # Test different force magnitudes
    betas = [0.1, 0.3, 0.6, 1.0]
    
    results = []
    
    for beta in betas:
        print(f"\n--- β={beta} ---")
        pl = ParticleLife(n_types=n_types, n_particles=n_particles,
                         size=size, r_max=0.1, beta=beta, friction=0.3, seed=42)
        
        clustering_over_time = []
        
        for step in range(300):
            pl.step()
            if step % 20 == 0:
                c = pl.measure_clustering()
                clustering_over_time.append((step, c))
        
        final_c = clustering_over_time[-1][1]
        print(f"  Final clustering: {final_c:.4f}")
        results.append({
            'beta': beta,
            'final_clustering': final_c,
            'history': clustering_over_time
        })
    
    # Plot clustering over time for different betas
    fig, ax = plt.subplots(figsize=(8, 5))
    for r in results:
        steps, scores = zip(*r['history'])
        ax.plot(steps, scores, marker='o', markersize=3,
                label=f'β={r["beta"]}')
    
    ax.set_xlabel('Step')
    ax.set_ylabel('Clustering Score')
    ax.set_title('Particle Life: Clustering vs Force Magnitude')
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('experiments/particle_life_beta_sweep.png')
    plt.close()
    print("\n[OK] Saved particle_life_beta_sweep.png")
    
    return results


def multi_param_scan():
    """Scan combinations of beta and friction to find 'zones of life'"""
    print("\n" + "=" * 60)
    print("Particle Life: Beta × Friction Phase Diagram")
    print("=" * 60)
    
    betas = np.linspace(0.1, 1.0, 10)
    frictions = np.linspace(0.1, 0.9, 9)
    
    clustering_grid = np.zeros((len(frictions), len(betas)))
    
    for i, friction in enumerate(frictions):
        for j, beta in enumerate(betas):
            pl = ParticleLife(n_types=4, n_particles=200, size=1.0,
                            r_max=0.1, beta=beta, friction=friction, seed=42)
            for _ in range(200):
                pl.step()
            clustering_grid[i, j] = pl.measure_clustering()
    
    # Plot phase diagram
    fig, ax = plt.subplots(figsize=(9, 7))
    im = ax.imshow(clustering_grid, origin='lower', aspect='auto',
                   extent=[betas[0], betas[-1], frictions[0], frictions[-1]],
                   cmap='RdYlBu')
    
    ax.set_xlabel('Force Magnitude (β)')
    ax.set_ylabel('Friction')
    ax.set_title('Particle Life: Emergence Phase Diagram\n(Clustering Score)')
    
    # Annotate "zones"
    ax.axvspan(0.3, 0.7, alpha=0.1, color='green')
    ax.text(0.5, 0.15, '"Life Zone"', ha='center', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='green', alpha=0.2))
    
    plt.colorbar(im, label='Clustering Score')
    plt.tight_layout()
    plt.savefig('experiments/particle_life_phase_diagram.png')
    plt.close()
    print("[OK] Saved particle_life_phase_diagram.png")
    
    return clustering_grid


def create_final_vis():
    """Create final visualization: before/after with best parameters"""
    print("\n" + "=" * 60)
    print("Particle Life: Final Visualization")
    print("=" * 60)
    
    # Best params from sweep
    pl = ParticleLife(n_types=4, n_particles=300, size=1.0,
                     r_max=0.1, beta=0.5, friction=0.3, seed=42)
    
    # Initial state
    initial_pos = pl.positions.copy()
    
    # Run
    for _ in range(400):
        pl.step()
    
    final_pos = pl.positions.copy()
    final_clustering = pl.measure_clustering()
    
    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Before
    for t in range(pl.n_types):
        mask = pl.types == t
        ax1.scatter(initial_pos[mask, 0], initial_pos[mask, 1],
                   c=[pl.colors[t]], s=8, alpha=0.7)
    ax1.set_title('Initial (Random)')
    ax1.set_xticks([])
    ax1.set_yticks([])
    
    # After
    for t in range(pl.n_types):
        mask = pl.types == t
        ax2.scatter(final_pos[mask, 0], final_pos[mask, 1],
                   c=[pl.colors[t]], s=8, alpha=0.7)
    ax2.set_title(f'After 400 Steps\nClustering = {final_clustering:.3f}')
    ax2.set_xticks([])
    ax2.set_yticks([])
    
    fig.suptitle('Particle Life: Emergent Clustering from Simple Forces',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('experiments/particle_life_before_after.png')
    plt.close()
    print("[OK] Saved particle_life_before_after.png")
    
    return final_clustering


if __name__ == '__main__':
    t_start = time.time()
    
    # 1. Parameter sweep: beta
    sweep_results = parameter_sweep()
    
    # 2. Multi-param phase diagram
    phase_grid = multi_param_scan()
    
    # 3. Final visualization
    clustering = create_final_vis()
    
    # 4. Try to create GIF
    print("\n[4/4] Creating GIF...")
    try:
        pl = ParticleLife(n_types=4, n_particles=200, size=1.0,
                         r_max=0.1, beta=0.5, friction=0.3, seed=42)
        pl.create_gif(steps=200, filename='experiments/particle_life.gif', interval=30)
    except Exception as e:
        print(f"  [WARN] GIF skipped: {e}")
    
    elapsed = time.time() - t_start
    print(f"\n{'='*60}")
    print(f"Done in {elapsed:.1f}s")
    print(f"Final clustering score: {clustering:.3f}")
    print(f"{'='*60}")
