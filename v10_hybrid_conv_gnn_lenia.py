"""
V10: Hybrid Convolution + GNN Lenia - Corrected Version
========================================================
The key insight: mu must match the expected convolution result U.
For a normalized kernel and input in [0,1], U will be in [0,1] as well.
mu should be set to match the expected activation level.
"""

import numpy as np
import scipy.sparse as sp
import json
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# Icosahedral Mesh Generation
# ============================================================================

def create_icosahedral_mesh(resolution=3):
    """Create icosahedral sphere mesh."""
    phi = (1 + np.sqrt(5)) / 2
    vertices = np.array([
        [-1, phi, 0], [1, phi, 0], [-1, -phi, 0], [1, -phi, 0],
        [0, -1, phi], [0, 1, phi], [0, -1, -phi], [0, 1, -phi],
        [phi, 0, -1], [phi, 0, 1], [-phi, 0, -1], [-phi, 0, 1]
    ], dtype=np.float64)
    vertices = vertices / np.linalg.norm(vertices, axis=1, keepdims=True)
    faces = np.array([
        [0,11,5], [0,5,1], [0,1,7], [0,7,10], [0,10,11],
        [1,5,9], [5,11,4], [11,10,2], [10,7,6], [7,1,8],
        [3,9,4], [3,4,2], [3,2,6], [3,6,8], [3,8,9],
        [4,9,5], [2,4,11], [6,2,10], [8,6,7], [9,8,1]
    ])
    for _ in range(resolution):
        vertices, faces = subdivide_mesh(vertices, faces)
    vertices = vertices / np.linalg.norm(vertices, axis=1, keepdims=True)
    return vertices, faces

def subdivide_mesh(vertices, faces):
    """Subdivide mesh."""
    edge_to_vertex = {}
    new_vertices = list(vertices)
    new_faces = []
    def get_midpoint(v1, v2):
        key = tuple(sorted([v1, v2]))
        if key not in edge_to_vertex:
            midpoint = (vertices[v1] + vertices[v2]) / 2
            midpoint = midpoint / np.linalg.norm(midpoint)
            edge_to_vertex[key] = len(new_vertices)
            new_vertices.append(midpoint)
        return edge_to_vertex[key]
    for face in faces:
        v0, v1, v2 = face
        a = get_midpoint(v0, v1)
        b = get_midpoint(v1, v2)
        c = get_midpoint(v2, v0)
        new_faces.extend([[v0, a, c], [v1, b, a], [v2, c, b], [a, b, c]])
    return np.array(new_vertices), np.array(new_faces)

def build_adjacency(vertices, faces, n_nodes):
    """Build normalized adjacency matrix."""
    rows, cols = [], []
    for face in faces:
        for i in range(3):
            for j in range(3):
                if i != j:
                    rows.append(face[i])
                    cols.append(face[j])
    data = np.ones(len(rows))
    adj = sp.coo_matrix((data, (rows, cols)), shape=(n_nodes, n_nodes)).tocsr()
    adj.data = np.ones(len(adj.data))
    adj = adj + sp.eye(n_nodes)
    degree = np.array(adj.sum(axis=1)).flatten()
    degree_inv_sqrt = np.power(degree, -0.5)
    degree_inv_sqrt[np.isinf(degree_inv_sqrt)] = 0.
    return sp.diags(degree_inv_sqrt) @ adj @ sp.diags(degree_inv_sqrt)

# ============================================================================
# Lenia Core (Corrected)
# ============================================================================

def lenia_kernel(R=13, mu_k=0.5, sigma_k=0.15):
    """Create Lenia kernel."""
    size = 2 * R + 1
    y, x = np.ogrid[-R:R+1, -R:R+1]
    dist = np.sqrt(x**2 + y**2) / R
    K = np.exp(-((dist - mu_k)**2) / (2 * sigma_k**2))
    K[dist > 1] = 0
    K = K / K.sum()
    return K

def lenia_step(A, K_fft, mu, sigma, dt=1.0):
    """
    Lenia step.
    
    Key: mu should be set to the expected activation level after convolution.
    For a pattern with mean activation ~0.3, mu should be ~0.3.
    """
    A_fft = np.fft.fft2(A)
    U = np.fft.ifft2(A_fft * K_fft).real
    
    # Growth function: peaks at U = mu
    G = 2 * np.exp(-((U - mu)**2) / (2 * sigma**2)) - 1
    
    # Update
    A_new = A + dt * G
    A_new = np.clip(A_new, 0, 1)
    
    return A_new

# ============================================================================
# GNN Lenia
# ============================================================================

def gnn_step(state, adj, mu, sigma, dt=1.0):
    """GNN step using message passing."""
    U = adj @ state
    G = 2 * np.exp(-((U - mu)**2) / (2 * sigma**2)) - 1
    state_new = state + dt * G
    state_new = np.clip(state_new, 0, 1)
    return state_new

# ============================================================================
# Hybrid System
# ============================================================================

class HybridLeniaSystem:
    """Hybrid Conv + GNN Lenia with corrected parameters."""
    
    def __init__(self, grid_size=128, mesh_resolution=3, fusion_strategy='adaptive'):
        self.grid_size = grid_size
        self.mesh_resolution = mesh_resolution
        self.fusion_strategy = fusion_strategy
        
        # Create mesh
        print(f"Creating icosahedral mesh (resolution={mesh_resolution})...")
        self.vertices, self.faces = create_icosahedral_mesh(mesh_resolution)
        self.n_nodes = len(self.vertices)
        print(f"  Nodes: {self.n_nodes}, Faces: {len(self.faces)}")
        
        # Build adjacency
        self.adj = build_adjacency(self.vertices, self.faces, self.n_nodes)
        
        # Create kernel
        self.R = 13
        K = lenia_kernel(R=self.R)
        
        # Pad to grid size
        K_padded = np.zeros((grid_size, grid_size))
        K_padded[:2*self.R+1, :2*self.R+1] = K
        K_padded = np.roll(np.roll(K_padded, -self.R, axis=0), -self.R, axis=1)
        self.K_fft = np.fft.fft2(K_padded)
        
        # Parameters - CORRECTED
        # mu should match expected activation level
        # For stable patterns, use mu ~ 0.3-0.4 (typical activation)
        self.mu_conv = 0.3
        self.sigma_conv = 0.05
        self.mu_gnn = 0.3
        self.sigma_gnn = 0.05
        
        # States
        self.A_conv = None
        self.A_gnn = None
        self.time = 0
        self.alpha = 0.5
        
    def initialize(self, seed=42):
        """Initialize with pattern that matches mu."""
        np.random.seed(seed)
        
        # Convolution: create pattern with mean ~0.3 to match mu
        self.A_conv = np.zeros((self.grid_size, self.grid_size))
        cx, cy = self.grid_size // 2, self.grid_size // 2
        y, x = np.ogrid[:self.grid_size, :self.grid_size]
        r = np.sqrt((x - cx)**2 + (y - cy)**2)
        
        # Create a pattern with target mean ~0.3
        # Use a softer gaussian with wider spread
        self.A_conv = 0.4 * np.exp(-r**2 / (2 * 20**2))
        
        # Add some structure for complexity
        angle = np.arctan2(y - cy, x - cx)
        self.A_conv += 0.1 * np.cos(3 * angle) * np.exp(-r**2 / (2 * 25**2))
        
        self.A_conv = np.clip(self.A_conv, 0, 1)
        
        # GNN: similar statistics
        self.A_gnn = np.ones(self.n_nodes) * 0.3 + 0.1 * np.random.randn(self.n_nodes)
        self.A_gnn = np.clip(self.A_gnn, 0, 1)
        
        self.time = 0
    
    def set_params(self, conv_params, gnn_params):
        """Set parameters."""
        self.mu_conv, self.sigma_conv = conv_params
        self.mu_gnn, self.sigma_gnn = gnn_params
    
    def compute_alpha(self):
        """Compute fusion weight."""
        if self.fusion_strategy == 'fixed':
            return 0.5
        elif self.fusion_strategy == 'learnable_global':
            return self.alpha
        elif self.fusion_strategy == 'spatial_attention':
            conv_act = np.mean(self.A_conv)
            gnn_act = np.mean(self.A_gnn)
            return np.clip(0.5 + 0.3 * (conv_act - gnn_act), 0.2, 0.8)
        elif self.fusion_strategy == 'pattern_density':
            conv_var = np.var(self.A_conv)
            gnn_var = np.var(self.A_gnn)
            total_var = conv_var + gnn_var + 1e-6
            return np.clip(0.5 + 0.3 * (conv_var - gnn_var) / total_var, 0.2, 0.8)
        elif self.fusion_strategy == 'adaptive':
            progress = min(1.0, self.time / 150)
            return 0.3 + 0.4 * progress
        return 0.5
    
    def step(self, dt=1.0):
        """Single hybrid step."""
        alpha = self.compute_alpha()
        
        # Update both branches
        A_conv_new = lenia_step(self.A_conv, self.K_fft, self.mu_conv, self.sigma_conv, dt)
        A_gnn_new = gnn_step(self.A_gnn, self.adj, self.mu_gnn, self.sigma_gnn, dt)
        
        # Cross-coupling
        if self.time % 20 == 0 and self.time > 0:
            conv_mean = np.mean(A_conv_new)
            gnn_mean = np.mean(A_gnn_new)
            A_gnn_new = A_gnn_new + 0.02 * (conv_mean - gnn_mean)
            A_gnn_new = np.clip(A_gnn_new, 0, 1)
        
        self.A_conv = A_conv_new
        self.A_gnn = A_gnn_new
        self.time += 1
        
        return alpha
    
    def run(self, n_steps=200, dt=1.0):
        """Run simulation."""
        alphas = []
        for _ in range(n_steps):
            alpha = self.step(dt)
            alphas.append(alpha)
        return alphas

# ============================================================================
# Metrics
# ============================================================================

def compute_metrics(A_conv, A_gnn, alpha=0.5):
    """Compute metrics."""
    
    # Survival
    threshold = 0.1
    conv_survival = float(np.mean(A_conv > threshold))
    gnn_survival = float(np.mean(A_gnn > threshold))
    survival = alpha * conv_survival + (1 - alpha) * gnn_survival
    
    # Complexity
    def entropy(state):
        hist, _ = np.histogram(state.flatten(), bins=20, range=(0, 1), density=True)
        hist = hist + 1e-10
        return -np.sum(hist * np.log(hist)) / np.log(20)
    
    conv_entropy = entropy(A_conv)
    gnn_entropy = entropy(A_gnn)
    conv_var = float(np.var(A_conv))
    gnn_var = float(np.var(A_gnn))
    
    conv_complexity = float(np.clip(conv_entropy * 0.6 + conv_var * 4, 0, 1))
    gnn_complexity = float(np.clip(gnn_entropy * 0.6 + gnn_var * 4, 0, 1))
    complexity = alpha * conv_complexity + (1 - alpha) * gnn_complexity
    
    # Diversity
    conv_mean = np.mean(A_conv)
    gnn_mean = np.mean(A_gnn)
    conv_diversity = float(np.std(A_conv) / (conv_mean + 1e-6)) if conv_mean > 0.01 else 0
    gnn_diversity = float(np.std(A_gnn) / (gnn_mean + 1e-6)) if gnn_mean > 0.01 else 0
    diversity = alpha * conv_diversity + (1 - alpha) * gnn_diversity
    
    # Fitness
    survival = max(0.01, survival)
    complexity = max(0.01, complexity)
    fitness = float((survival ** 0.5) * (complexity ** 1.5) * (1 + 0.2 * diversity))
    
    return {
        'fitness': fitness,
        'survival': survival,
        'complexity': complexity,
        'diversity': diversity,
        'conv_survival': conv_survival,
        'conv_complexity': conv_complexity,
        'gnn_survival': gnn_survival,
        'gnn_complexity': gnn_complexity
    }

# ============================================================================
# Experiments
# ============================================================================

def run_experiment(fusion_strategy, n_runs=5, n_steps=200, seed_start=42):
    """Run experiments."""
    results = []
    
    for run in range(n_runs):
        seed = seed_start + run * 100
        
        system = HybridLeniaSystem(
            grid_size=128,
            mesh_resolution=3,
            fusion_strategy=fusion_strategy
        )
        
        system.initialize(seed=seed)
        
        # Parameter variations around mu=0.3
        mu = 0.3 + 0.05 * np.random.randn()
        sigma = 0.05 + 0.01 * np.random.randn()
        
        system.set_params(
            conv_params=(mu, max(0.02, sigma)),
            gnn_params=(mu, max(0.02, sigma))
        )
        
        alphas = system.run(n_steps=n_steps, dt=1.0)
        alpha_mean = np.mean(alphas)
        
        metrics = compute_metrics(system.A_conv, system.A_gnn, alpha_mean)
        
        results.append({
            'run': run,
            'seed': seed,
            'fusion_strategy': fusion_strategy,
            'final_alpha': float(alpha_mean),
            **metrics
        })
    
    return results

def parameter_sweep(fusion_strategy, n_configs=8):
    """Parameter sweep."""
    best_result = None
    best_fitness = -1
    
    for config in range(n_configs):
        system = HybridLeniaSystem(
            grid_size=128,
            mesh_resolution=3,
            fusion_strategy=fusion_strategy
        )
        
        system.initialize(seed=config * 50)
        
        # Sweep mu around 0.3
        mu = 0.25 + 0.15 * np.random.rand()  # [0.25, 0.40]
        sigma = 0.03 + 0.05 * np.random.rand()  # [0.03, 0.08]
        
        system.set_params(
            conv_params=(mu, sigma),
            gnn_params=(mu, sigma)
        )
        
        system.run(n_steps=200, dt=1.0)
        metrics = compute_metrics(system.A_conv, system.A_gnn)
        
        if metrics['fitness'] > best_fitness:
            best_fitness = metrics['fitness']
            best_result = {
                'config': config,
                'mu': float(mu),
                'sigma': float(sigma),
                **metrics
            }
    
    return best_result

# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 70)
    print("V10: Hybrid Convolution + GNN Lenia")
    print("=" * 70)
    
    strategies = ['fixed', 'learnable_global', 'spatial_attention', 'pattern_density', 'adaptive']
    all_results = {}
    
    for strategy in strategies:
        print(f"\n{'='*70}")
        print(f"Testing fusion strategy: {strategy}")
        print(f"{'='*70}")
        
        results = run_experiment(strategy, n_runs=5, n_steps=200, seed_start=42)
        
        print(f"\nParameter sweep for {strategy}...")
        best_result = parameter_sweep(strategy, n_configs=8)
        
        avg_fitness = np.mean([r['fitness'] for r in results])
        avg_survival = np.mean([r['survival'] for r in results])
        avg_complexity = np.mean([r['complexity'] for r in results])
        
        all_results[strategy] = {
            'results': results,
            'best_result': best_result,
            'avg_fitness': avg_fitness,
            'avg_survival': avg_survival,
            'avg_complexity': avg_complexity
        }
        
        print(f"\nResults for {strategy}:")
        print(f"  Average fitness: {avg_fitness:.4f}")
        print(f"  Average survival: {avg_survival:.4f}")
        print(f"  Average complexity: {avg_complexity:.4f}")
        if best_result:
            print(f"  Best params: μ={best_result['mu']:.3f}, σ={best_result['sigma']:.4f}")
            print(f"  Best fitness: {best_result['fitness']:.4f}")
    
    # Comparison
    print("\n" + "=" * 70)
    print("COMPARISON")
    print("=" * 70)
    
    comparison = []
    for strategy, data in all_results.items():
        comparison.append({
            'strategy': strategy,
            'fitness': float(data['avg_fitness']),
            'survival': float(data['avg_survival']),
            'complexity': float(data['avg_complexity']),
            'best_fitness': float(data['best_result']['fitness']) if data['best_result'] else 0
        })
    
    comparison.sort(key=lambda x: x['fitness'], reverse=True)
    
    print("\nStrategy Ranking (by average fitness):")
    print("-" * 70)
    for i, row in enumerate(comparison, 1):
        print(f"{i}. {row['strategy']:20s} | Fitness: {row['fitness']:.4f} | "
              f"Survival: {row['survival']:.4f} | Complexity: {row['complexity']:.4f}")
    
    best_strategy = comparison[0]['strategy']
    
    print(f"\n{'='*70}")
    print(f"BEST STRATEGY: {best_strategy}")
    print(f"{'='*70}")
    
    print("\nComparison with Baselines:")
    print("-" * 70)
    print(f"V8 GNN (icosahedral):       49.2% survival, ~0.50 complexity")
    print(f"V9 Learnable:               94% survival,  0.60 complexity")
    print(f"Diffusion kernels:          100% survival, ~0.80 complexity, fitness 4.57")
    print(f"V10 Hybrid ({best_strategy}): {comparison[0]['survival']*100:.1f}% survival, "
          f"{comparison[0]['complexity']:.2f} complexity")
    
    # Save
    output = {
        'experiment': 'V10_Hybrid_Conv_GNN_Lenia',
        'best_strategy': best_strategy,
        'comparison': comparison,
        'detailed_results': all_results,
        'baseline_comparison': {
            'V8_GNN': {'survival': 0.492, 'complexity': 0.50},
            'V9_Learnable': {'survival': 0.94, 'complexity': 0.60},
            'Diffusion_kernels': {'survival': 1.0, 'complexity': 0.80, 'fitness': 4.57}
        },
        'key_findings': [
            f"Best fusion strategy: {best_strategy}",
            f"Average survival: {comparison[0]['survival']*100:.1f}%",
            f"Average complexity: {comparison[0]['complexity']:.2f}",
            "Key fix: mu parameter must match expected activation level",
            "Convolution and GNN branches use matched parameters",
            "Cross-coupling synchronizes branches every 20 steps"
        ]
    }
    
    import os
    os.makedirs('D:/openclaw_workspace/exploration', exist_ok=True)
    
    with open('D:/openclaw_workspace/exploration/v10_hybrid_results.json', 'w') as f:
        json.dump(output, f, indent=2, default=lambda x: float(x) if isinstance(x, (np.floating, np.integer)) else str(x))
    
    print(f"\nResults saved to: D:/openclaw_workspace/exploration/v10_hybrid_results.json")
    
    return output

if __name__ == '__main__':
    results = main()