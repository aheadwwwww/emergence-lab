"""
Evolutionary Lenia V8 - Graph Neural Lenia Proof-of-Concept
============================================================

CONCEPT: Replace Lenia's FFT convolution with Graph Neural Network message passing.

MOTIVATION from Pareto Front Analysis (V6):
- Stability-Emergence trade-off is inherent to convolution-based kernels
- Graph neural networks can learn adaptive interaction patterns
- GraphCast (DeepMind) successfully uses GNN for weather prediction on spherical meshes

ADVANTAGES:
1. Works on arbitrary meshes (not just regular grids)
2. Extends to spherical topology (no boundary issues)
3. Learnable interaction kernels
4. Potential for adaptive mesh refinement

ARCHITECTURE:
- Icosahedral mesh (like GraphCast)
- Each node has a state value (like Lenia cell)
- GNN message passing replaces convolution
- Growth function applied to aggregated messages

SIMPLIFIED VERSION FOR PROOF-OF-CONCEPT:
- Small mesh (resolution 3-4)
- Simple GNN (2 layers, 16 hidden dim)
- Compare emergence metrics with convolution-based Lenia
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional
import json
import time

# Try to import JAX/NumPy for computation
try:
    import jax
    import jax.numpy as jnp
    from jax import jit, vmap
    HAS_JAX = True
except ImportError:
    HAS_JAX = False
    import numpy as jnp


# ============================================================================
# Icosahedral Mesh Generation (Simplified)
# ============================================================================

def create_icosahedral_mesh(resolution: int = 3) -> Dict[str, Any]:
    """
    Create an icosahedral mesh for spherical Lenia.
    
    Resolution 3 = ~642 nodes, ~1280 triangles
    Resolution 4 = ~2562 nodes, ~5120 triangles
    
    Returns:
        Dict with 'nodes', 'edges', 'faces', 'neighbors'
    """
    # Golden ratio
    phi = (1 + np.sqrt(5)) / 2
    
    # Initial icosahedron vertices (12 nodes)
    vertices = np.array([
        [-1, phi, 0], [1, phi, 0], [-1, -phi, 0], [1, -phi, 0],
        [0, -1, phi], [0, 1, phi], [0, -1, -phi], [0, 1, -phi],
        [phi, 0, -1], [phi, 0, 1], [-phi, 0, -1], [-phi, 0, 1]
    ], dtype=np.float64)
    
    # Normalize to unit sphere
    vertices = vertices / np.linalg.norm(vertices, axis=1, keepdims=True)
    
    # Initial faces (20 triangles)
    faces = np.array([
        [0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
        [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
        [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
        [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]
    ])
    
    # Subdivide mesh
    for _ in range(resolution):
        vertices, faces = _subdivide_mesh(vertices, faces)
    
    # Compute edges from faces
    edges = set()
    for face in faces:
        for i in range(3):
            edge = tuple(sorted([face[i], face[(i+1) % 3]]))
            edges.add(edge)
    edges = np.array(list(edges))
    
    # Compute neighbors for each node
    n_nodes = len(vertices)
    neighbors = [[] for _ in range(n_nodes)]
    for i, j in edges:
        neighbors[i].append(j)
        neighbors[j].append(i)
    neighbors = [np.array(n) for n in neighbors]
    
    return {
        'nodes': vertices,
        'edges': edges,
        'faces': faces,
        'neighbors': neighbors,
        'resolution': resolution,
        'n_nodes': n_nodes,
        'n_edges': len(edges),
    }


def _subdivide_mesh(vertices: np.ndarray, faces: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Subdivide each triangle into 4 smaller triangles."""
    edge_midpoints = {}
    new_vertices = list(vertices)
    
    def get_midpoint(i: int, j: int) -> int:
        edge = tuple(sorted([i, j]))
        if edge in edge_midpoints:
            return edge_midpoints[edge]
        
        midpoint = (vertices[i] + vertices[j]) / 2
        midpoint = midpoint / np.linalg.norm(midpoint)  # Project to sphere
        idx = len(new_vertices)
        new_vertices.append(midpoint)
        edge_midpoints[edge] = idx
        return idx
    
    new_faces = []
    for face in faces:
        v1, v2, v3 = face
        a = get_midpoint(v1, v2)
        b = get_midpoint(v2, v3)
        c = get_midpoint(v3, v1)
        
        new_faces.append([v1, a, c])
        new_faces.append([v2, b, a])
        new_faces.append([v3, c, b])
        new_faces.append([a, b, c])
    
    return np.array(new_vertices), np.array(new_faces)


# ============================================================================
# Graph Neural Lenia
# ============================================================================

@dataclass
class GraphNeuralLeniaConfig:
    """Configuration for Graph Neural Lenia."""
    mesh_resolution: int = 3
    hidden_dim: int = 16
    n_gnn_layers: int = 2
    mu: float = 0.15  # Growth center
    sigma: float = 0.014  # Growth width
    dt: float = 0.1
    sim_steps: int = 200
    seed_type: str = 'random'


class GraphNeuralLenia:
    """
    Graph Neural Lenia - Lenia dynamics on graph/mesh structure.
    
    Key difference from traditional Lenia:
    - Traditional: FFT-based convolution on regular grid
    - Graph: Message passing on arbitrary mesh
    
    This enables:
    - Spherical topology
    - Non-uniform resolution
    - Learnable interaction kernels
    """
    
    def __init__(self, config: GraphNeuralLeniaConfig):
        self.config = config
        self.mesh = create_icosahedral_mesh(config.mesh_resolution)
        self.n_nodes = self.mesh['n_nodes']
        
        # Initialize GNN-like parameters (simplified)
        # In a full implementation, these would be learned
        self._init_message_weights()
    
    def _init_message_weights(self):
        """Initialize message passing weights."""
        # Simple learned kernel weights (distance-based)
        nodes = self.mesh['nodes']
        n = self.n_nodes
        
        # Precompute geodesic distances on sphere
        self.distances = np.zeros((n, n))
        for i in range(n):
            for j in self.mesh['neighbors'][i]:
                # Geodesic distance on unit sphere
                self.distances[i, j] = np.arccos(np.clip(np.dot(nodes[i], nodes[j]), -1, 1))
        
        # Initialize kernel weights (like Lenia's ring kernel)
        self.kernel_r0 = 0.5  # Ring center
        self.kernel_width = 0.15  # Ring width
    
    def _kernel_weight(self, dist: float) -> float:
        """Compute kernel weight for a given distance."""
        return np.exp(-((dist - self.kernel_r0) ** 2) / (2 * self.kernel_width ** 2))
    
    def init_state(self, seed_type: str = 'random') -> np.ndarray:
        """Initialize state on mesh nodes."""
        n = self.n_nodes
        
        if seed_type == 'random':
            state = np.random.rand(n).astype(np.float32)
        elif seed_type == 'spot':
            # Create a localized spot
            nodes = self.mesh['nodes']
            center = np.array([1, 0, 0])
            dists = np.array([np.arccos(np.clip(np.dot(n, center), -1, 1)) for n in nodes])
            state = np.exp(-dists**2 / 0.1).astype(np.float32)
        elif seed_type == 'wave':
            # Create wave pattern
            nodes = self.mesh['nodes']
            state = (0.5 + 0.5 * np.sin(nodes[:, 0] * 4 * np.pi)).astype(np.float32)
        else:
            state = np.random.rand(n).astype(np.float32)
        
        return state
    
    def step(self, state: np.ndarray) -> np.ndarray:
        """
        Single step of Graph Neural Lenia.
        
        Equivalent to Lenia's:
        1. Convolution -> Message aggregation
        2. Growth function -> Applied to aggregated messages
        3. Update -> State update
        """
        new_state = np.zeros_like(state)
        
        mu = self.config.mu
        sigma = self.config.sigma
        dt = self.config.dt
        
        for i in range(self.n_nodes):
            # Aggregate messages from neighbors (like convolution)
            msg_sum = 0.0
            weight_sum = 0.0
            
            for j in self.mesh['neighbors'][i]:
                dist = self.distances[i, j]
                weight = self._kernel_weight(dist)
                msg_sum += weight * state[j]
                weight_sum += weight
            
            # Normalize (like convolution normalization)
            if weight_sum > 0:
                conv_value = msg_sum / weight_sum
            else:
                conv_value = 0.0
            
            # Apply growth function (Gaussian)
            growth = np.exp(-((conv_value - mu) ** 2) / (2 * sigma ** 2)) * 2 - 1
            
            # Update state
            new_state[i] = np.clip(state[i] + dt * growth, 0, 1)
        
        return new_state
    
    def simulate(self, steps: Optional[int] = None, seed_type: Optional[str] = None) -> Dict[str, Any]:
        """Run full simulation."""
        steps = steps or self.config.sim_steps
        seed_type = seed_type or self.config.seed_type
        
        state = self.init_state(seed_type)
        history = [state.copy()]
        
        for _ in range(steps):
            state = self.step(state)
            history.append(state.copy())
        
        return {
            'history': np.array(history),
            'final_state': state,
            'mesh': self.mesh,
        }
    
    def compute_metrics(self, history: np.ndarray) -> Dict[str, float]:
        """Compute emergence metrics."""
        initial = history[0]
        final = history[-1]
        
        # Survival: fraction of non-zero cells
        survival = np.mean(final > 0.01)
        
        # Activity: mean change over time
        diffs = np.abs(np.diff(history, axis=0))
        activity = np.mean(diffs) if len(diffs) > 0 else 0.0
        
        # Diversity: variance of final state
        diversity = np.std(final)
        
        # Persistence: correlation between initial and final
        persistence = np.corrcoef(initial, final)[0, 1] if len(initial) > 1 else 0.0
        
        # Complexity: approximate entropy
        hist, _ = np.histogram(final, bins=20, range=(0, 1))
        hist = hist / hist.sum()
        hist = hist[hist > 0]
        complexity = -np.sum(hist * np.log(hist + 1e-10))
        
        return {
            'survival': float(survival),
            'activity': float(activity),
            'diversity': float(diversity),
            'persistence': float(persistence),
            'complexity': float(complexity),
        }


# ============================================================================
# Comparison Experiment
# ============================================================================

def run_comparison_experiment(
    mesh_resolution: int = 3,
    mu: float = 0.15,
    sigma: float = 0.014,
    steps: int = 200,
    seed_type: str = 'spot',
) -> Dict[str, Any]:
    """
    Run Graph Neural Lenia and compute metrics.
    """
    print(f"\n{'='*60}")
    print(f"Graph Neural Lenia V8 - Proof of Concept")
    print(f"{'='*60}")
    print(f"  Mesh resolution: {mesh_resolution}")
    print(f"  Nodes: ~{10 * 4**mesh_resolution + 2}")
    print(f"  Growth params: μ={mu:.4f}, σ={sigma:.5f}")
    print(f"  Steps: {steps}")
    print(f"  Seed: {seed_type}")
    
    config = GraphNeuralLeniaConfig(
        mesh_resolution=mesh_resolution,
        mu=mu,
        sigma=sigma,
        sim_steps=steps,
        seed_type=seed_type,
    )
    
    gnl = GraphNeuralLenia(config)
    
    print(f"\n  Mesh created: {gnl.n_nodes} nodes, {len(gnl.mesh['edges'])} edges")
    
    # Run simulation
    t0 = time.time()
    result = gnl.simulate()
    elapsed = time.time() - t0
    
    # Compute metrics
    metrics = gnl.compute_metrics(result['history'])
    
    print(f"\n  Simulation time: {elapsed:.2f}s")
    print(f"\n  Metrics:")
    print(f"    Survival:   {metrics['survival']:.4f}")
    print(f"    Activity:   {metrics['activity']:.4f}")
    print(f"    Diversity:  {metrics['diversity']:.4f}")
    print(f"    Persistence:{metrics['persistence']:.4f}")
    print(f"    Complexity: {metrics['complexity']:.4f}")
    
    return {
        'config': {
            'mesh_resolution': mesh_resolution,
            'mu': mu,
            'sigma': sigma,
            'steps': steps,
            'seed_type': seed_type,
        },
        'mesh_stats': {
            'n_nodes': gnl.n_nodes,
            'n_edges': len(gnl.mesh['edges']),
        },
        'metrics': metrics,
        'elapsed': elapsed,
    }


def run_parameter_sweep() -> List[Dict[str, Any]]:
    """Run parameter sweep to find good Graph Neural Lenia parameters."""
    
    print("\n" + "="*60)
    print("PARAMETER SWEEP - Graph Neural Lenia V8")
    print("="*60)
    
    results = []
    
    # Test different growth parameters (based on V6 Pareto findings)
    param_sets = [
        # (mu, sigma, name)
        (0.15, 0.014, 'Orbium-like'),
        (0.15, 0.025, 'Wide-growth'),
        (0.20, 0.020, 'Medium'),
        (0.25, 0.030, 'High-mu'),
        (0.135, 0.074, 'V7-evolved'),
    ]
    
    seed_types = ['random', 'spot', 'wave']
    
    for mu, sigma, name in param_sets:
        for seed_type in seed_types:
            print(f"\n--- {name} (μ={mu}, σ={sigma}) | Seed: {seed_type} ---")
            
            try:
                result = run_comparison_experiment(
                    mesh_resolution=3,
                    mu=mu,
                    sigma=sigma,
                    steps=100,
                    seed_type=seed_type,
                )
                result['param_name'] = name
                results.append(result)
            except Exception as e:
                print(f"  ERROR: {e}")
    
    return results


def save_results(results: List[Dict[str, Any]], output_dir: Path):
    """Save results to JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Convert to serializable format
    serializable = []
    for r in results:
        serializable.append({
            'param_name': r.get('param_name', 'unknown'),
            'config': r['config'],
            'mesh_stats': r['mesh_stats'],
            'metrics': r['metrics'],
            'elapsed': r['elapsed'],
        })
    
    with open(output_dir / 'v8_graph_neural_lenia_results.json', 'w') as f:
        json.dump(serializable, f, indent=2)
    
    print(f"\n[OK] Results saved to {output_dir}/")


def create_visualization(results: List[Dict[str, Any]], output_dir: Path):
    """Create visualization of results."""
    
    if not results:
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Extract data
    names = [r.get('param_name', 'unknown') for r in results]
    seeds = [r['config']['seed_type'] for r in results]
    
    survival = [r['metrics']['survival'] for r in results]
    diversity = [r['metrics']['diversity'] for r in results]
    complexity = [r['metrics']['complexity'] for r in results]
    persistence = [r['metrics']['persistence'] for r in results]
    
    # Plot 1: Survival by parameter
    ax = axes[0, 0]
    unique_names = list(set(names))
    for name in unique_names:
        mask = [n == name for n in names]
        ax.bar([i for i, m in enumerate(mask) if m], 
               [s for s, m in zip(survival, mask) if m],
               label=name, alpha=0.7)
    ax.set_ylabel('Survival')
    ax.set_title('Survival by Parameter Set')
    ax.legend(fontsize=8)
    
    # Plot 2: Diversity vs Complexity
    ax = axes[0, 1]
    colors = plt.cm.tab10(range(len(set(names))))
    for i, name in enumerate(unique_names):
        mask = [n == name for n in names]
        ax.scatter([d for d, m in zip(diversity, mask) if m],
                   [c for c, m in zip(complexity, mask) if m],
                   c=[colors[i]], label=name, s=100, alpha=0.7)
    ax.set_xlabel('Diversity')
    ax.set_ylabel('Complexity')
    ax.set_title('Diversity vs Complexity')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    
    # Plot 3: Persistence by seed type
    ax = axes[1, 0]
    unique_seeds = list(set(seeds))
    for i, seed in enumerate(unique_seeds):
        mask = [s == seed for s in seeds]
        vals = [p for p, m in zip(persistence, mask) if m]
        ax.bar(i, np.mean(vals), label=seed, alpha=0.7)
        ax.errorbar(i, np.mean(vals), np.std(vals), fmt='k_')
    ax.set_xticks(range(len(unique_seeds)))
    ax.set_xticklabels(unique_seeds)
    ax.set_ylabel('Persistence')
    ax.set_title('Persistence by Seed Type')
    
    # Plot 4: Summary metrics
    ax = axes[1, 1]
    metric_names = ['survival', 'diversity', 'complexity', 'persistence']
    means = [np.mean([r['metrics'][m] for r in results]) for m in metric_names]
    stds = [np.std([r['metrics'][m] for r in results]) for m in metric_names]
    ax.bar(metric_names, means, yerr=stds, alpha=0.7, color=['blue', 'green', 'orange', 'purple'])
    ax.set_ylabel('Score')
    ax.set_title('Average Metrics Across All Runs')
    
    plt.suptitle('Graph Neural Lenia V8 - Proof of Concept Results', 
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    plt.savefig(output_dir / 'v8_graph_neural_lenia.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"[OK] Visualization saved to {output_dir}/v8_graph_neural_lenia.png")


def main():
    """Run V8 Graph Neural Lenia experiment."""
    
    print("="*60)
    print("EVOLUTIONARY LENIA V8 - GRAPH NEURAL LENIA")
    print("="*60)
    print("\nCONCEPT: Replace Lenia's FFT convolution with GNN message passing")
    print("BENEFITS: Spherical topology, learnable kernels, adaptive mesh")
    print()
    
    output_dir = Path('D:/openclaw_workspace/output/evo_lenia_v8_graph_neural')
    
    # Run parameter sweep
    results = run_parameter_sweep()
    
    if results:
        # Save results
        save_results(results, output_dir)
        
        # Create visualization
        create_visualization(results, output_dir)
        
        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        
        best_survival = max(results, key=lambda r: r['metrics']['survival'])
        best_diversity = max(results, key=lambda r: r['metrics']['diversity'])
        best_complexity = max(results, key=lambda r: r['metrics']['complexity'])
        
        print(f"\nBest Survival: {best_survival['param_name']} ({best_survival['config']['seed_type']})")
        print(f"  Score: {best_survival['metrics']['survival']:.4f}")
        
        print(f"\nBest Diversity: {best_diversity['param_name']} ({best_diversity['config']['seed_type']})")
        print(f"  Score: {best_diversity['metrics']['diversity']:.4f}")
        
        print(f"\nBest Complexity: {best_complexity['param_name']} ({best_complexity['config']['seed_type']})")
        print(f"  Score: {best_complexity['metrics']['complexity']:.4f}")
        
        print("\n" + "="*60)
        print("V8 PROOF OF CONCEPT COMPLETE")
        print("="*60)
        print("\nNext steps:")
        print("1. Implement full GNN with learnable message weights")
        print("2. Compare with convolution-based Lenia on same metrics")
        print("3. Test on spherical surface (no boundary artifacts)")
        print("4. Explore mesh refinement for pattern concentration")
    
    return results


if __name__ == '__main__':
    main()
