"""
Graph Neural Lenia V9 - Learnable Message Passing
==================================================

MOTIVATION FROM V8:
- V8 discovered that GNN requires WIDER growth functions (σ ≥ 0.025)
- V7-evolved parameters (σ=0.074) achieved 49% survival on GNN mesh
- BUT: Fixed message weights limit adaptability

V9 HYPOTHESIS:
If we make the message passing weights LEARNABLE, the GNN can:
1. Discover optimal interaction patterns for Lenia dynamics
2. Potentially overcome the stability-emergence trade-off
3. Adapt to different pattern types automatically

ARCHITECTURE:
- Same icosahedral mesh as V8 (642 nodes)
- Learnable message weights: W(r) for each neighbor distance r
- Gradient descent to optimize emergence metrics
- Compare with fixed-kernel V8 results

KEY INNOVATION:
Instead of fixed Gaussian ring kernel, use:
    m_ij = W(d_ij) * state_j
    state_i_new = growth(∑_j m_ij)

Where W is a small neural network (or piecewise function) that can be learned.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any
import json

try:
    import jax
    import jax.numpy as jnp
    from jax import jit, grad, vmap
    from jax import random as jax_random
    import optax
    HAS_JAX = True
    print("JAX available for gradient-based learning")
except ImportError:
    HAS_JAX = False
    import numpy as jnp
    print("JAX not available, using NumPy (no gradients)")


# ============================================================================
# Icosahedral Mesh (Same as V8)
# ============================================================================

def create_icosahedral_mesh(resolution: int = 3) -> Dict[str, Any]:
    """Create icosahedral mesh for spherical Lenia."""
    phi = (1 + np.sqrt(5)) / 2
    
    vertices = np.array([
        [-1, phi, 0], [1, phi, 0], [-1, -phi, 0], [1, -phi, 0],
        [0, -1, phi], [0, 1, phi], [0, -1, -phi], [0, 1, -phi],
        [phi, 0, -1], [phi, 0, 1], [-phi, 0, -1], [-phi, 0, 1]
    ], dtype=np.float64)
    
    vertices = vertices / np.linalg.norm(vertices, axis=1, keepdims=True)
    
    faces = np.array([
        [0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
        [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
        [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
        [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]
    ])
    
    # Subdivide
    for _ in range(resolution):
        new_faces = []
        edge_to_mid = {}
        
        for face in faces:
            mids = []
            for i in range(3):
                edge = tuple(sorted([face[i], face[(i+1)%3]]))
                if edge not in edge_to_mid:
                    mid = (vertices[edge[0]] + vertices[edge[1]]) / 2
                    mid = mid / np.linalg.norm(mid)
                    edge_to_mid[edge] = len(vertices)
                    vertices = np.vstack([vertices, mid])
                mids.append(edge_to_mid[edge])
            
            v0, v1, v2 = face
            m0, m1, m2 = mids
            new_faces.extend([
                [v0, m0, m2], [v1, m1, m0], [v2, m2, m1], [m0, m1, m2]
            ])
        
        faces = np.array(new_faces)
    
    # Build neighbor graph
    n_nodes = len(vertices)
    neighbor_edges = set()
    for face in faces:
        for i in range(3):
            edge = tuple(sorted([face[i], face[(i+1)%3]]))
            neighbor_edges.add(edge)
    
    neighbors = {i: [] for i in range(n_nodes)}
    for i, j in neighbor_edges:
        neighbors[i].append(j)
        neighbors[j].append(i)
    
    # Compute distances
    distances = {}
    for i in range(n_nodes):
        for j in neighbors[i]:
            dist = np.linalg.norm(vertices[i] - vertices[j])
            distances[(i, j)] = dist
    
    return {
        'nodes': vertices,
        'edges': list(neighbor_edges),
        'faces': faces,
        'neighbors': neighbors,
        'distances': distances,
        'n_nodes': n_nodes
    }


# ============================================================================
# Learnable Kernel Functions
# ============================================================================

def gaussian_ring_kernel(r: float, params: Dict) -> float:
    """
    Traditional Gaussian ring kernel (baseline).
    
    params: {'mu': center, 'sigma': width, 'amplitude': peak height}
    """
    mu = params.get('mu', 0.15)
    sigma = params.get('sigma', 0.074)  # V8 best value
    amp = params.get('amplitude', 1.0)
    
    return amp * np.exp(-((r - mu)**2) / (2 * sigma**2))


def learnable_piecewise_kernel(r: float, weights: np.ndarray, r_bins: np.ndarray) -> float:
    """
    Piecewise linear kernel with learnable weights.
    
    weights: array of weight values at each r_bin
    r_bins: array of distance values
    """
    return np.interp(r, r_bins, weights)


def neural_kernel(r: float, W: np.ndarray, b: np.ndarray) -> float:
    """
    Small neural network kernel.
    
    W: weight matrix (hidden_dim x 1)
    b: bias vector (hidden_dim)
    
    Architecture: r -> tanh(W*r + b) -> output (scalar)
    """
    hidden = np.tanh(W * r + b)
    output = np.mean(hidden)  # Collapse to scalar
    return output


# ============================================================================
# GNN Simulation
# ============================================================================

def simulate_gnn_lenia(
    mesh: Dict,
    kernel_params: Dict,
    n_steps: int = 100,
    seed_type: str = 'random',
    learnable_weights: np.ndarray = None
) -> Dict:
    """
    Simulate Graph Neural Lenia with either fixed or learnable kernel.
    
    Returns metrics: survival, diversity, persistence, complexity
    """
    n_nodes = mesh['n_nodes']
    neighbors = mesh['neighbors']
    distances = mesh['distances']
    
    # Initialize state
    if seed_type == 'random':
        state = np.random.rand(n_nodes)
    elif seed_type == 'spot':
        state = np.zeros(n_nodes)
        center = n_nodes // 2
        state[center] = 1.0
        for j in neighbors[center]:
            state[j] = 0.8
    elif seed_type == 'wave':
        theta = np.linspace(0, 4*np.pi, n_nodes)
        state = 0.5 + 0.3 * np.sin(theta)
    else:
        state = np.random.rand(n_nodes)
    
    # Track history
    history = [state.copy()]
    
    # Determine kernel type
    use_learnable = learnable_weights is not None
    
    if use_learnable:
        # Use learnable piecewise kernel
        r_max = max(distances.values())
        r_bins = np.linspace(0, r_max * 1.5, len(learnable_weights))
    
    # Simulation loop
    for step in range(n_steps):
        new_state = np.zeros(n_nodes)
        
        for i in range(n_nodes):
            # Aggregate messages from neighbors
            messages = []
            for j in neighbors[i]:
                r = distances[(i, j)]
                
                if use_learnable:
                    # Use learnable kernel
                    k = learnable_piecewise_kernel(r, learnable_weights, r_bins)
                else:
                    # Use fixed Gaussian ring kernel
                    k = gaussian_ring_kernel(r, kernel_params)
                
                messages.append(k * state[j])
            
            # Aggregate
            U = np.sum(messages) / len(messages) if messages else 0
            
            # Growth function
            mu = kernel_params.get('mu', 0.135)
            sigma = kernel_params.get('sigma', 0.074)
            
            growth = 2 * np.exp(-((U - mu)**2) / (2 * sigma**2)) - 1
            
            # Update
            new_state[i] = np.clip(state[i] + 0.1 * growth, 0, 1)
        
        state = new_state
        history.append(state.copy())
    
    # Compute metrics
    final_state = history[-1]
    
    survival = np.mean(final_state > 0.1)
    
    diversity = np.std(final_state)
    
    if len(history) > 10:
        persistence = np.corrcoef(history[-10], history[-20])[0, 1]
        if np.isnan(persistence):
            persistence = 0.0
    else:
        persistence = 0.0
    
    complexity = survival * diversity * (1 + abs(persistence))
    
    return {
        'final_state': final_state,
        'history': history,
        'survival': survival,
        'diversity': diversity,
        'persistence': persistence,
        'complexity': complexity,
        'metrics': {
            'survival': float(survival),
            'diversity': float(diversity),
            'persistence': float(persistence),
            'complexity': float(complexity)
        }
    }


# ============================================================================
# Gradient-Based Optimization (JAX)
# ============================================================================

def jax_simulate_and_score(learnable_weights: jnp.ndarray, mesh: Dict, seed_type: str) -> float:
    """
    JAX-compatible simulation for gradient computation.
    
    Returns complexity score to maximize.
    """
    if not HAS_JAX:
        return 0.0
    
    n_nodes = mesh['n_nodes']
    neighbors = mesh['neighbors']
    distances = mesh['distances']
    
    # Initialize state
    key = jax_random.PRNGKey(42)
    if seed_type == 'random':
        state = jax_random.uniform(key, (n_nodes,))
    elif seed_type == 'spot':
        state = jnp.zeros(n_nodes)
        center = n_nodes // 2
        state = state.at[center].set(1.0)
    else:
        state = jax_random.uniform(key, (n_nodes,))
    
    # Fixed params for growth function
    mu = 0.135
    sigma = 0.074
    
    # Pre-compute neighbor structure
    neighbor_list = []
    distance_list = []
    for i in range(n_nodes):
        neigh = neighbors[i]
        dists = [distances[(i, j)] for j in neigh]
        neighbor_list.append(neigh)
        distance_list.append(dists)
    
    # Simulation (simplified for JAX)
    r_max = max(distances.values())
    r_bins = jnp.linspace(0, r_max * 1.5, len(learnable_weights))
    
    def kernel_fn(r):
        return jnp.interp(r, r_bins, learnable_weights)
    
    # Run simulation
    n_steps = 50  # Shorter for gradient computation
    for step in range(n_steps):
        new_state = jnp.zeros(n_nodes)
        
        for i in range(n_nodes):
            messages = []
            for idx, j in enumerate(neighbor_list[i]):
                r = distance_list[i][idx]
                k = kernel_fn(r)
                messages.append(k * state[j])
            
            if messages:
                U = jnp.sum(jnp.array(messages)) / len(messages)
            else:
                U = 0.0
            
            growth = 2 * jnp.exp(-((U - mu)**2) / (2 * sigma**2)) - 1
            new_state = new_state.at[i].set(jnp.clip(state[i] + 0.1 * growth, 0, 1))
        
        state = new_state
    
    # Compute score
    survival = jnp.mean(state > 0.1)
    diversity = jnp.std(state)
    complexity = survival * diversity
    
    return complexity


def optimize_learnable_kernel(mesh: Dict, n_iterations: int = 100) -> Tuple[np.ndarray, List[float]]:
    """
    Optimize learnable kernel weights using gradient descent.
    
    Returns: (optimized_weights, score_history)
    """
    if not HAS_JAX:
        print("JAX required for gradient optimization")
        return None, []
    
    # Initialize weights
    n_weights = 10
    key = jax_random.PRNGKey(0)
    initial_weights = jax_random.uniform(key, (n_weights,), minval=0.0, maxval=1.0)
    
    # Optimizer
    optimizer = optax.adam(learning_rate=0.01)
    opt_state = optimizer.init(initial_weights)
    
    # Loss function (negative complexity)
    def loss_fn(weights):
        score = jax_simulate_and_score(weights, mesh, seed_type='spot')
        return -score  # Minimize negative = maximize positive
    
    # Gradient function
    grad_fn = jit(grad(loss_fn))
    
    # Optimization loop
    weights = initial_weights
    score_history = []
    
    print("Optimizing learnable kernel weights...")
    
    for i in range(n_iterations):
        grads = grad_fn(weights)
        updates, opt_state = optimizer.update(grads, opt_state)
        weights = optax.apply_updates(weights, updates)
        
        # Clamp to valid range
        weights = jnp.clip(weights, 0.0, 1.0)
        
        # Track score
        score = -loss_fn(weights)
        score_history.append(float(score))
        
        if i % 20 == 0:
            print(f"  Iteration {i}: complexity = {score:.4f}")
    
    print(f"Optimization complete: final complexity = {score_history[-1]:.4f}")
    
    return np.array(weights), score_history


# ============================================================================
# Experiment Runner
# ============================================================================

def run_v9_experiment():
    """Run V9 learnable kernel experiment."""
    
    print("=" * 70)
    print("V9: Learnable Message Passing for Graph Neural Lenia")
    print("=" * 70)
    
    # Create mesh
    print("\nCreating icosahedral mesh (resolution 3)...")
    mesh = create_icosahedral_mesh(resolution=3)
    print(f"  Nodes: {mesh['n_nodes']}")
    print(f"  Edges: {len(mesh['edges'])}")
    
    # Baseline: Fixed Gaussian ring kernel
    print("\nTesting baseline (fixed Gaussian ring kernel)...")
    baseline_params = {'mu': 0.135, 'sigma': 0.074}  # V8 best params
    
    baseline_results = {}
    for seed in ['random', 'spot', 'wave']:
        result = simulate_gnn_lenia(mesh, baseline_params, n_steps=100, seed_type=seed)
        baseline_results[seed] = result
        print(f"  {seed}: survival={result['survival']:.3f}, "
              f"diversity={result['diversity']:.3f}, "
              f"complexity={result['complexity']:.3f}")
    
    # Learnable kernel optimization
    if HAS_JAX:
        print("\nOptimizing learnable kernel weights...")
        optimized_weights, score_history = optimize_learnable_kernel(mesh, n_iterations=100)
        
        # Test optimized kernel
        print("\nTesting optimized learnable kernel...")
        learnable_results = {}
        for seed in ['random', 'spot', 'wave']:
            result = simulate_gnn_lenia(
                mesh, baseline_params, n_steps=100, 
                seed_type=seed, learnable_weights=optimized_weights
            )
            learnable_results[seed] = result
            print(f"  {seed}: survival={result['survival']:.3f}, "
                  f"diversity={result['diversity']:.3f}, "
                  f"complexity={result['complexity']:.3f}")
        
        # Compare
        print("\nComparison (Baseline vs Learnable):")
        for seed in ['random', 'spot', 'wave']:
            b = baseline_results[seed]
            l = learnable_results[seed]
            improvement = (l['complexity'] - b['complexity']) / b['complexity'] * 100
            print(f"  {seed}: {b['complexity']:.3f} → {l['complexity']:.3f} ({improvement:+.1f}%)")
        
        # Save results
        output_dir = Path('output/lenia_v9_learnable')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save optimization history
        plt.figure(figsize=(10, 6))
        plt.plot(score_history)
        plt.xlabel('Iteration')
        plt.ylabel('Complexity Score')
        plt.title('V9: Learnable Kernel Optimization')
        plt.grid(True, alpha=0.3)
        plt.savefig(output_dir / 'optimization_history.png', dpi=150)
        print(f"\nSaved: {output_dir / 'optimization_history.png'}")
        
        # Save optimized weights
        np.save(output_dir / 'optimized_weights.npy', optimized_weights)
        
        # Save metrics
        results = {
            'baseline': {seed: r['metrics'] for seed, r in baseline_results.items()},
            'learnable': {seed: r['metrics'] for seed, r in learnable_results.items()},
            'optimized_weights': optimized_weights.tolist(),
            'score_history': score_history
        }
        
        with open(output_dir / 'results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Saved: {output_dir / 'results.json'}")
        
        return results
    
    else:
        print("\nJAX not available - skipping optimization")
        return baseline_results


if __name__ == '__main__':
    results = run_v9_experiment()
    
    print("\n" + "=" * 70)
    print("V9 Experiment Complete")
    print("=" * 70)
