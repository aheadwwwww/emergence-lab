"""
Evolutionary Lenia V9: Learnable GNN Message Weights

Implements Graph Neural Lenia with learnable attention-based message passing.
Key innovation: Replace fixed message weights with trainable attention mechanism.

Based on V8 findings:
- GNN requires wider growth functions (σ≥0.025)
- V7-evolved parameters (μ=0.135, σ=0.074) achieved 49.2% survival
- Need to learn optimal neighbor influence patterns
"""

import numpy as np
import time
from pathlib import Path
import json

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch_scatter import scatter_softmax, scatter_sum
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("Warning: PyTorch not available. Install with: pip install torch torch_scatter")

try:
    import trimesh
    TRIMESH_AVAILABLE = True
except ImportError:
    TRIMESH_AVAILABLE = False


class LearnableGNNLayer(nn.Module):
    """
    Graph Neural Network layer with learnable attention-based message passing.
    
    Unlike fixed convolution kernels, attention weights adapt to local pattern context.
    """
    
    def __init__(self, hidden_dim=32, num_heads=4):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_heads = num_heads
        
        # Message network: takes (node_i, node_j, distance) -> message
        self.msg_mlp = nn.Sequential(
            nn.Linear(1 + 1 + 1, hidden_dim),  # [state_i, state_j, distance]
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, num_heads)  # One attention score per head
        )
        
        # State update network
        self.update_mlp = nn.Sequential(
            nn.Linear(2, hidden_dim),  # state + aggregated (both scalars)
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )
        
        # Growth function parameters (learnable)
        self.mu = nn.Parameter(torch.tensor(0.135))
        self.sigma = nn.Parameter(torch.tensor(0.074))
        
    def forward(self, state, edge_index, edge_attr):
        """
        Args:
            state: [N] node states
            edge_index: [2, E] edge indices (source, target)
            edge_attr: [E, 1] edge attributes (distance)
        
        Returns:
            Updated state: [N]
        """
        N = state.size(0)
        source, target = edge_index[0], edge_index[1]
        
        # Compute messages for all edges
        state_i = state[source].unsqueeze(-1)  # [E, 1]
        state_j = state[target].unsqueeze(-1)  # [E, 1]
        distances = edge_attr  # [E, 1]
        
        # Message input: [state_i, state_j, distance]
        msg_input = torch.cat([state_i, state_j, distances], dim=-1)  # [E, 3]
        
        # Compute attention scores
        attention_scores = self.msg_mlp(msg_input)  # [E, num_heads]
        
        # Softmax over incoming edges for each node
        attention_weights = scatter_softmax(attention_scores, target, dim=0)  # [E, num_heads]
        
        # Aggregate messages
        # For now, use simple weighted sum of neighbor states
        weighted_messages = (state_j * attention_weights.mean(dim=-1, keepdim=True)).squeeze(-1)  # [E]
        
        # Sum messages for each node
        aggregated = torch.zeros(N, device=state.device, dtype=torch.float32)
        aggregated = aggregated.scatter_add(0, target, weighted_messages.float())
        
        # Count neighbors for normalization
        neighbor_counts = torch.zeros(N, device=state.device, dtype=torch.float32)
        neighbor_counts = neighbor_counts.scatter_add(0, target, torch.ones_like(weighted_messages, dtype=torch.float32))
        neighbor_counts = neighbor_counts.clamp(min=1)  # Avoid division by zero
        
        # Normalize
        aggregated = aggregated / neighbor_counts
        
        # Replace any NaN with 0
        aggregated = torch.where(torch.isnan(aggregated), torch.zeros_like(aggregated), aggregated)
        
        # Apply growth function (ensure sigma is positive for numerical stability)
        sigma_safe = torch.abs(self.sigma) + 0.001
        growth = torch.exp(-((aggregated - self.mu)**2) / (2 * sigma_safe**2))
        
        # Update state
        update_input = torch.cat([state.unsqueeze(-1), aggregated.unsqueeze(-1)], dim=-1)
        update = torch.tanh(self.update_mlp(update_input)).squeeze(-1)
        
        # Replace NaN in update with 0
        update = torch.where(torch.isnan(update) | torch.isinf(update), torch.zeros_like(update), update)
        
        # New state: blend current state with growth
        new_state = state + update * (growth - state) * 0.5
        
        # Debug output
        # (removed for cleaner output)
        
        # Clamp to [0, 1] and replace any NaN
        new_state = torch.clamp(new_state, 0.0, 1.0)
        new_state = torch.where(torch.isnan(new_state) | torch.isinf(new_state), 
                                 torch.zeros_like(new_state), new_state)
        
        return new_state, attention_weights


class LearnableGraphLenia(nn.Module):
    """
    Graph Neural Lenia with learnable parameters.
    """
    
    def __init__(self, num_layers=3, hidden_dim=32, num_heads=4):
        super().__init__()
        self.num_layers = num_layers
        self.layers = nn.ModuleList([
            LearnableGNNLayer(hidden_dim, num_heads) 
            for _ in range(num_layers)
        ])
        
    def forward(self, state, edge_index, edge_attr):
        attention_history = []
        
        for layer in self.layers:
            state, attention = layer(state, edge_index, edge_attr)
            attention_history.append(attention)
        
        return state, attention_history


def create_icosahedral_mesh(resolution=3):
    """Create icosahedral mesh using numpy (fallback if trimesh unavailable)."""
    
    # Golden ratio
    phi = (1 + np.sqrt(5)) / 2
    
    # Base icosahedron vertices (12 vertices)
    vertices = np.array([
        [-1, phi, 0], [1, phi, 0], [-1, -phi, 0], [1, -phi, 0],
        [0, -1, phi], [0, 1, phi], [0, -1, -phi], [0, 1, -phi],
        [phi, 0, -1], [phi, 0, 1], [-phi, 0, -1], [-phi, 0, 1]
    ], dtype=np.float64)
    
    # Normalize to unit sphere
    vertices = vertices / np.linalg.norm(vertices, axis=1, keepdims=True)
    
    # Base faces (20 triangles)
    faces = np.array([
        [0,11,5], [0,5,1], [0,1,7], [0,7,10], [0,10,11],
        [1,5,9], [5,11,4], [11,10,2], [10,7,6], [7,1,8],
        [3,9,4], [3,4,2], [3,2,6], [3,6,8], [3,8,9],
        [4,9,5], [2,4,11], [6,2,10], [8,6,7], [9,8,1]
    ])
    
    # Subdivide to increase resolution
    for _ in range(resolution):
        new_vertices = [vertices]
        new_faces = []
        edge_midpoint = {}
        
        for face in faces:
            v0, v1, v2 = face
            
            # Get or create midpoints
            def get_midpoint(i, j):
                key = tuple(sorted([i, j]))
                if key not in edge_midpoint:
                    mid = (vertices[i] + vertices[j]) / 2
                    mid = mid / np.linalg.norm(mid)
                    edge_midpoint[key] = len(vertices) + len(new_vertices) - len(vertices)
                    new_vertices.append(mid)
                return edge_midpoint[key]
            
            a = get_midpoint(v0, v1)
            b = get_midpoint(v1, v2)
            c = get_midpoint(v2, v0)
            
            new_faces.extend([
                [v0, a, c],
                [v1, b, a],
                [v2, c, b],
                [a, b, c]
            ])
        
        vertices = np.vstack(new_vertices)
        faces = np.array(new_faces)
    
    # Build adjacency (edges)
    edges = set()
    for face in faces:
        for i in range(3):
            edge = tuple(sorted([face[i], face[(i+1)%3]]))
            edges.add(edge)
    
    edges = np.array(list(edges))
    
    return vertices, edges


def run_learnable_gnn_experiment(resolution=3, steps=100, lr=0.01, seed_type='spot'):
    """
    Run learnable GNN Lenia experiment with gradient-based optimization.
    """
    
    print(f"\n{'='*70}")
    print(f"V9: Learnable GNN Lenia")
    print(f"Resolution: {resolution}, Steps: {steps}, LR: {lr}, Seed: {seed_type}")
    print(f"{'='*70}\n")
    
    if not TORCH_AVAILABLE:
        print("ERROR: PyTorch not available")
        return None
    
    # Create mesh
    print("Creating icosahedral mesh...")
    vertices, edges = create_icosahedral_mesh(resolution)
    N = len(vertices)
    E = len(edges)
    
    print(f"  Nodes: {N}, Edges: {E}")
    
    # Compute edge distances (geodesic)
    edge_distances = np.linalg.norm(vertices[edges[:, 0]] - vertices[edges[:, 1]], axis=1)
    edge_distances = edge_distances / edge_distances.max()  # Normalize
    
    # Convert to PyTorch
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"  Device: {device}")
    
    edge_index = torch.tensor(edges.T, dtype=torch.long, device=device)
    edge_attr = torch.tensor(edge_distances, dtype=torch.float32, device=device).unsqueeze(-1)
    
    # Initialize state
    if seed_type == 'random':
        state = torch.rand(N, device=device)
    elif seed_type == 'spot':
        state = torch.zeros(N, device=device)
        # Activate region around a random node
        center_idx = np.random.randint(N)
        center_pos = vertices[center_idx]
        distances = np.linalg.norm(vertices - center_pos, axis=1)
        state = torch.tensor(np.exp(-distances**2 / 0.1), device=device, dtype=torch.float32)
    elif seed_type == 'wave':
        # Spherical wave pattern
        z_coords = vertices[:, 2]
        state = torch.tensor(0.5 + 0.3 * np.sin(4 * np.pi * z_coords), device=device, dtype=torch.float32)
    
    state = torch.clamp(state, 0.0, 1.0)
    
    # Ensure no NaN in initial state
    state = torch.where(torch.isnan(state), torch.rand_like(state), state)
    state = torch.clamp(state, 0.0, 1.0)
    
    # Create model
    model = LearnableGraphLenia(num_layers=2, hidden_dim=32, num_heads=4).to(device)
    
    # Optimizer
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    
    # Metrics tracking
    metrics_history = {
        'survival': [],
        'diversity': [],
        'persistence': [],
        'complexity': [],
        'loss': []
    }
    
    prev_state = state.clone()
    running_state = state.clone()
    
    print(f"\nRunning simulation with learnable parameters...")
    print(f"Initial μ: {model.layers[0].mu.item():.4f}, σ: {model.layers[0].sigma.item():.4f}")
    
    start_time = time.time()
    
    for step in range(steps):
        # Forward pass
        new_state, attention_history = model(state, edge_index, edge_attr)
        
        # Compute loss: encourage pattern survival and complexity
        # Loss 1: Survival (mean activation)
        survival_loss = -new_state.mean()  # Maximize survival
        
        # Loss 2: Diversity (entropy)
        hist = torch.histc(new_state, bins=20, min=0, max=1)
        hist_prob = hist / hist.sum()
        diversity_loss = (hist_prob * torch.log(hist_prob + 1e-8)).sum()  # Maximize entropy
        
        # Loss 3: Stability (avoid rapid changes)
        stability_loss = ((new_state - prev_state)**2).mean() * 0.1
        
        # Total loss
        loss = survival_loss + diversity_loss + stability_loss
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        # Gradient clipping to prevent exploding gradients
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        
        # Project parameters to valid range after each step
        # Also check for NaN and reset if needed
        for layer in model.layers:
            if torch.isnan(layer.mu.data) or torch.isinf(layer.mu.data):
                layer.mu.data.fill_(0.135)
            if torch.isnan(layer.sigma.data) or torch.isinf(layer.sigma.data):
                layer.sigma.data.fill_(0.074)
            layer.mu.data.clamp_(0.0, 1.0)
            layer.sigma.data.clamp_(0.01, 0.5)
            
            # Check MLP weights for NaN
            for name, param in layer.msg_mlp.named_parameters():
                if torch.isnan(param.data).any() or torch.isinf(param.data).any():
                    param.data = torch.randn_like(param.data) * 0.1
            for name, param in layer.update_mlp.named_parameters():
                if torch.isnan(param.data).any() or torch.isinf(param.data).any():
                    param.data = torch.randn_like(param.data) * 0.1
        
        # Update state
        prev_state = state.clone()
        state = new_state.detach()
        
        # Track metrics
        survival = state.mean().item()
        diversity = -diversity_loss.item()
        
        # Debug output for first 5 steps
        # (removed for cleaner output)
        
        metrics_history['survival'].append(survival)
        metrics_history['diversity'].append(diversity)
        metrics_history['loss'].append(loss.item())
        
        if step % 20 == 0:
            print(f"  Step {step:3d}: Survival={survival:.4f}, Diversity={diversity:.4f}, Loss={loss.item():.4f}")
    
    elapsed = time.time() - start_time
    
    # Final metrics
    final_survival = state.mean().item()
    final_diversity = metrics_history['diversity'][-1]
    
    # Persistence: correlation between initial and final state
    initial_state = running_state.cpu().numpy()
    final_state_np = state.cpu().numpy()
    persistence = np.corrcoef(initial_state, final_state_np)[0, 1]
    
    # Complexity: standard deviation of state changes
    complexity = np.std(final_state_np)
    
    # Learned parameters
    learned_mu = model.layers[0].mu.item()
    learned_sigma = model.layers[0].sigma.item()
    
    print(f"\n[OK] Completed in {elapsed:.2f}s")
    print(f"  Final Survival: {final_survival:.4f}")
    print(f"  Final Diversity: {final_diversity:.4f}")
    print(f"  Persistence: {persistence:.4f}")
    print(f"  Complexity: {complexity:.4f}")
    print(f"  Learned μ: {learned_mu:.4f} (initial: 0.135)")
    print(f"  Learned σ: {learned_sigma:.4f} (initial: 0.074)")
    
    return {
        'survival': final_survival,
        'diversity': final_diversity,
        'persistence': persistence,
        'complexity': complexity,
        'learned_mu': learned_mu,
        'learned_sigma': learned_sigma,
        'metrics_history': metrics_history,
        'elapsed': elapsed,
        'num_nodes': N,
        'num_edges': E
    }


def main():
    """Run V9 learnable GNN experiments."""
    
    print("\n" + "="*70)
    print("V9: LEARNABLE GNN LENIA EXPERIMENTS")
    print("="*70)
    
    if not TORCH_AVAILABLE:
        print("\nERROR: PyTorch not available")
        print("Install with: pip install torch torch_scatter")
        return
    
    # Test different configurations
    experiments = [
        {'resolution': 3, 'steps': 100, 'lr': 0.01, 'seed_type': 'spot'},
        {'resolution': 3, 'steps': 100, 'lr': 0.01, 'seed_type': 'random'},
        {'resolution': 3, 'steps': 100, 'lr': 0.01, 'seed_type': 'wave'},
        {'resolution': 3, 'steps': 200, 'lr': 0.005, 'seed_type': 'spot'},  # Longer run
        {'resolution': 4, 'steps': 100, 'lr': 0.01, 'seed_type': 'spot'},  # Higher resolution
    ]
    
    results = {}
    
    for i, config in enumerate(experiments):
        print(f"\n{'='*70}")
        print(f"Experiment {i+1}/{len(experiments)}")
        print(f"{'='*70}")
        
        result = run_learnable_gnn_experiment(**config)
        
        key = f"exp_{i+1}_{config['seed_type']}"
        results[key] = result
        
        if result:
            print(f"\n  Summary:")
            print(f"    Survival: {result['survival']:.4f}")
            print(f"    Learned (μ, σ): ({result['learned_mu']:.4f}, {result['learned_sigma']:.4f})")
    
    # Save results
    output_dir = Path('D:/emergence_experiments')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / 'v9_learnable_gnn_results.json'
    
    with open(output_file, 'w') as f:
        def safe_json(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, (np.floating, np.integer)):
                return float(obj) if not np.isnan(obj) and not np.isinf(obj) else None
            if isinstance(obj, float):
                if np.isnan(obj) or np.isinf(obj):
                    return None
            return obj
        json.dump(results, f, indent=2, default=safe_json)
    
    print(f"\n{'='*70}")
    print("RESULTS SAVED")
    print(f"{'='*70}")
    print(f"  File: {output_file}")
    
    # Summary
    print(f"\n{'='*70}")
    print("EXPERIMENT SUMMARY")
    print(f"{'='*70}")
    
    for key, result in results.items():
        if result:
            print(f"\n{key}:")
            print(f"  Survival: {result['survival']:.4f}")
            print(f"  Diversity: {result['diversity']:.4f}")
            print(f"  Persistence: {result['persistence']:.4f}")
            print(f"  Complexity: {result['complexity']:.4f}")
            print(f"  Learned (μ, σ): ({result['learned_mu']:.4f}, {result['learned_sigma']:.4f})")


if __name__ == '__main__':
    main()
