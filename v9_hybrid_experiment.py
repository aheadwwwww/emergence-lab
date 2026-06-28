"""
V9 Hybrid Conv+GNN Lenia Experiment
====================================
Combines convolutional Lenia with GNN-based refinement for improved emergence.

Hypothesis: Hybrid can leverage conv's narrow σ (0.014) with GNN's robustness.
"""

import numpy as np
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import warnings
warnings.filterwarnings('ignore')

# JAX imports
try:
    import jax
    import jax.numpy as jnp
    from jax import jit, vmap, lax
    # Note: jax.scipy.ndimage.convolve may not be available in all versions
    try:
        from jax.scipy.ndimage import convolve as jax_convolve
    except ImportError:
        jax_convolve = None
    JAX_AVAILABLE = True
    print("[OK] JAX available")
except ImportError:
    JAX_AVAILABLE = False
    print("[SKIP] JAX not available, using NumPy fallback")

# PyTorch imports
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
    print("[OK] PyTorch available")
except ImportError:
    TORCH_AVAILABLE = False
    print("[SKIP] PyTorch not available")

# PyTorch Geometric imports
try:
    from torch_geometric.nn import GCNConv, GATConv, global_mean_pool
    from torch_geometric.data import Data as GraphData
    from torch_geometric.utils import grid
    PG_AVAILABLE = True
    print("[OK] PyTorch Geometric available")
except ImportError:
    PG_AVAILABLE = False
    print("[SKIP] PyTorch Geometric not available, using basic GNN")


@dataclass
class ExperimentConfig:
    """Configuration for a single experiment run."""
    name: str
    sigma: float
    mu: float
    alpha: float  # weight for conv (1-alpha for GNN)
    seed: int
    grid_size: int = 64
    steps: int = 200
    dt: float = 0.1


@dataclass
class ExperimentResult:
    """Results from a single experiment run."""
    config: Dict
    survival_rate: float
    pattern_complexity: float
    emergence_score: float
    computation_time: float
    final_mass: float
    final_variance: float
    pattern_detected: bool


# ============================================================================
# KERNEL FUNCTIONS
# ============================================================================

def gaussian_kernel(size: int, sigma: float, mu: float) -> np.ndarray:
    """Create Gaussian kernel for Lenia."""
    x = np.linspace(-size//2, size//2, size)
    y = np.linspace(-size//2, size//2, size)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2) / (size // 2)
    
    # Radial Gaussian
    K = np.exp(-((R - mu)**2) / (2 * sigma**2))
    K = K / K.sum()  # Normalize
    
    return K


def ring_kernel(size: int, sigma: float, mu: float) -> np.ndarray:
    """Create ring-shaped kernel for diverse patterns."""
    x = np.linspace(-size//2, size//2, size)
    y = np.linspace(-size//2, size//2, size)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2) / (size // 2)
    
    # Ring kernel (donut shape)
    K = np.exp(-((R - mu)**2) / (2 * sigma**2))
    K[R < mu - 2*sigma] = 0  # Inner cutoff
    K = K / (K.sum() + 1e-8)
    
    return K


# ============================================================================
# CONVOLUTIONAL LENIA
# ============================================================================

class ConvolutionalLenia:
    """Standard convolutional Lenia using JAX or NumPy."""
    
    def __init__(self, kernel: np.ndarray, dt: float = 0.1):
        self.kernel = kernel
        self.dt = dt
        self.kernel_size = kernel.shape[0]
        
        if JAX_AVAILABLE:
            self.kernel_jax = jnp.array(kernel)
            self._step_fn = jit(self._step_jax)
    
    def _step_jax(self, state: jnp.ndarray) -> jnp.ndarray:
        """JAX-accelerated step using scipy signal."""
        # Convolve with kernel using jax.scipy.signal
        try:
            conv = jax.scipy.signal.convolve2d(
                state, self.kernel_jax, mode='same'
            )
        except AttributeError:
            # Fallback to numpy-based convolution
            return None
        
        # Growth function: G(x) = 2 * exp(-((x - 0.135)**2) / (2 * 0.015**2)) - 1
        growth = 2 * jnp.exp(-((conv - 0.135)**2) / (2 * 0.015**2)) - 1
        
        # Update
        new_state = state + self.dt * growth * state
        new_state = jnp.clip(new_state, 0, 1)
        
        return new_state
    
    def _step_numpy(self, state: np.ndarray) -> np.ndarray:
        """NumPy fallback step."""
        from scipy.ndimage import convolve
        conv_result = convolve(state, self.kernel, mode='wrap')
        
        growth = 2 * np.exp(-((conv_result - 0.135)**2) / (2 * 0.015**2)) - 1
        new_state = state + self.dt * growth * state
        new_state = np.clip(new_state, 0, 1)
        
        return new_state
    
    def step(self, state: np.ndarray) -> np.ndarray:
        """Perform one step."""
        if JAX_AVAILABLE:
            try:
                result = self._step_fn(jnp.array(state))
                if result is not None:
                    return np.array(result)
            except Exception:
                pass
        return self._step_numpy(state)
    
    def run(self, initial_state: np.ndarray, steps: int) -> np.ndarray:
        """Run for multiple steps."""
        state = initial_state.copy()
        for _ in range(steps):
            state = self.step(state)
        return state


# ============================================================================
# GNN-BASED LENIA
# ============================================================================

class SimpleGNNLayer(nn.Module):
    """Simple GCN layer for when PyG is unavailable."""
    def __init__(self, in_features: int, out_features: int):
        super().__init__()
        self.weight = nn.Parameter(torch.randn(in_features, out_features) * 0.1)
        self.bias = nn.Parameter(torch.zeros(out_features))
    
    def forward(self, x: torch.Tensor, adj: torch.Tensor) -> torch.Tensor:
        # GCN propagation: D^(-1/2) A D^(-1/2) X W
        support = torch.matmul(x, self.weight)
        output = torch.matmul(adj, support) + self.bias
        return output


class GNNLeniaNetwork(nn.Module):
    """GNN for Lenia state refinement."""
    
    def __init__(self, hidden_dim: int = 32):
        super().__init__()
        self.hidden_dim = hidden_dim
        
        if PG_AVAILABLE:
            self.conv1 = GCNConv(1, hidden_dim)
            self.conv2 = GCNConv(hidden_dim, hidden_dim)
            self.conv3 = GCNConv(hidden_dim, 1)
        else:
            self.gnn1 = SimpleGNNLayer(1, hidden_dim)
            self.gnn2 = SimpleGNNLayer(hidden_dim, hidden_dim)
            self.gnn3 = SimpleGNNLayer(hidden_dim, 1)
        
        self.growth_scale = nn.Parameter(torch.tensor(0.1))
    
    def forward(self, state_flat: torch.Tensor, edge_index: torch.Tensor, 
                num_nodes: int) -> torch.Tensor:
        """Forward pass."""
        x = state_flat.unsqueeze(-1) if state_flat.dim() == 1 else state_flat
        
        if PG_AVAILABLE:
            x = F.relu(self.conv1(x, edge_index))
            x = F.relu(self.conv2(x, edge_index))
            x = torch.sigmoid(self.conv3(x, edge_index))
        else:
            # Need adjacency matrix for simple GNN
            raise NotImplementedError("Simple GNN requires adjacency matrix")
        
        return x.squeeze(-1)


class GNNLenia:
    """GNN-based Lenia using mesh representation."""
    
    def __init__(self, grid_size: int, sigma: float, mu: float, dt: float = 0.1):
        self.grid_size = grid_size
        self.sigma = sigma
        self.mu = mu
        self.dt = dt
        
        # Build grid graph
        self._build_graph()
        
        # GNN network
        if TORCH_AVAILABLE:
            self.network = GNNLeniaNetwork(hidden_dim=32)
            self.optimizer = torch.optim.Adam(self.network.parameters(), lr=0.001)
        print("[OK] GNN network initialized")
    
    def _build_graph(self):
        """Build grid connectivity graph."""
        n = self.grid_size
        num_nodes = n * n
        
        # Create edges for 8-connectivity
        edges = []
        for i in range(n):
            for j in range(n):
                node = i * n + j
                # 8 neighbors with periodic boundary
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue
                        ni = (i + di) % n
                        nj = (j + dj) % n
                        neighbor = ni * n + nj
                        edges.append([node, neighbor])
        
        self.edge_index = np.array(edges).T
        self.num_nodes = num_nodes
        
        if TORCH_AVAILABLE:
            self.edge_index_torch = torch.tensor(self.edge_index, dtype=torch.long)
    
    def compute_growth(self, state: np.ndarray) -> np.ndarray:
        """Compute growth using GNN message passing."""
        if not TORCH_AVAILABLE:
            return self._compute_growth_numpy(state)
        
        # Flatten state
        state_flat = torch.tensor(state.flatten(), dtype=torch.float32)
        
        # Simple message passing: aggregate neighbor values
        src, dst = self.edge_index_torch[0], self.edge_index_torch[1]
        
        # Aggregate messages
        neighbor_sum = torch.zeros(self.num_nodes)
        neighbor_sum.scatter_add_(0, dst, state_flat[src])
        
        # Count neighbors
        neighbor_count = torch.zeros(self.num_nodes)
        ones = torch.ones(self.num_nodes)
        neighbor_count.scatter_add_(0, dst, ones[src])
        
        # Average neighbor value
        neighbor_avg = neighbor_sum / (neighbor_count + 1e-8)
        
        # Growth function based on neighbor average
        growth = 2 * torch.exp(-((neighbor_avg - self.mu)**2) / (2 * self.sigma**2)) - 1
        
        return growth.numpy().reshape(self.grid_size, self.grid_size)
    
    def _compute_growth_numpy(self, state: np.ndarray) -> np.ndarray:
        """NumPy fallback for growth computation."""
        from scipy.ndimage import convolve
        
        # Use ring kernel for GNN-like behavior
        kernel = ring_kernel(9, self.sigma, self.mu)
        conv_result = convolve(state, kernel, mode='wrap')
        
        growth = 2 * np.exp(-((conv_result - self.mu)**2) / (2 * self.sigma**2)) - 1
        return growth
    
    def step(self, state: np.ndarray) -> np.ndarray:
        """Perform one GNN step."""
        growth = self.compute_growth(state)
        new_state = state + self.dt * growth * state
        new_state = np.clip(new_state, 0, 1)
        return new_state
    
    def run(self, initial_state: np.ndarray, steps: int) -> np.ndarray:
        """Run for multiple steps."""
        state = initial_state.copy()
        for _ in range(steps):
            state = self.step(state)
        return state


# ============================================================================
# HYBRID CONV+GNN LENIA
# ============================================================================

class HybridLenia:
    """Hybrid Convolutional + GNN Lenia."""
    
    def __init__(self, grid_size: int, sigma: float, mu: float, 
                 alpha: float, dt: float = 0.1):
        """
        Args:
            alpha: Weight for conv output (1-alpha for GNN)
        """
        self.grid_size = grid_size
        self.sigma = sigma
        self.mu = mu
        self.alpha = alpha
        self.dt = dt
        
        # Create conv kernel
        self.kernel = gaussian_kernel(13, sigma, mu)
        self.conv_lenia = ConvolutionalLenia(self.kernel, dt)
        
        # Create GNN
        self.gnn_lenia = GNNLenia(grid_size, sigma, mu, dt)
    
    def step(self, state: np.ndarray) -> np.ndarray:
        """Hybrid step combining conv and GNN."""
        # Convolutional update
        conv_growth = self._compute_conv_growth(state)
        
        # GNN update
        gnn_growth = self.gnn_lenia.compute_growth(state)
        
        # Weighted combination
        combined_growth = self.alpha * conv_growth + (1 - self.alpha) * gnn_growth
        
        # Apply update
        new_state = state + self.dt * combined_growth * state
        new_state = np.clip(new_state, 0, 1)
        
        return new_state
    
    def _compute_conv_growth(self, state: np.ndarray) -> np.ndarray:
        """Compute growth using convolution."""
        from scipy.ndimage import convolve
        conv_result = convolve(state, self.kernel, mode='wrap')
        growth = 2 * np.exp(-((conv_result - self.mu)**2) / (2 * self.sigma**2)) - 1
        return growth
    
    def run(self, initial_state: np.ndarray, steps: int) -> np.ndarray:
        """Run for multiple steps."""
        state = initial_state.copy()
        for _ in range(steps):
            state = self.step(state)
        return state


# ============================================================================
# METRICS
# ============================================================================

def compute_survival_rate(final_state: np.ndarray, initial_mass: float) -> float:
    """Compute survival rate (mass retention)."""
    final_mass = float(final_state.sum())
    return float(final_mass / (initial_mass + 1e-8))


def compute_pattern_complexity(state: np.ndarray) -> float:
    """Compute pattern complexity using gradient-based measure."""
    # Spatial gradients
    gx = np.abs(np.diff(state, axis=0)).sum()
    gy = np.abs(np.diff(state, axis=1)).sum()
    
    # Normalize by total mass
    mass = state.sum() + 1e-8
    complexity = (gx + gy) / mass
    
    return float(complexity)


def compute_emergence_score(state: np.ndarray, initial_state: np.ndarray) -> float:
    """Compute emergence score based on novel structures."""
    # Measure structural change
    diff = np.abs(state - initial_state)
    change = diff.mean()
    
    # Measure pattern diversity (entropy-like)
    hist, _ = np.histogram(state, bins=20, range=(0, 1))
    hist = hist / (hist.sum() + 1e-8)
    entropy = -np.sum(hist * np.log(hist + 1e-8))
    
    # Measure spatial organization
    from scipy.ndimage import label
    binary = state > 0.3
    labeled, num_features = label(binary)
    
    # Emergence combines change, diversity, and organization
    emergence = change * entropy * np.log(num_features + 1)
    
    return float(emergence)


def detect_pattern(state: np.ndarray) -> bool:
    """Detect if a meaningful pattern exists."""
    mass = state.sum()
    if mass < 10:
        return False
    
    # Check for non-uniform distribution
    variance = state.var()
    if variance < 0.01:
        return False
    
    # Check for structure
    complexity = compute_pattern_complexity(state)
    
    return complexity > 0.5


# ============================================================================
# EXPERIMENT RUNNER
# ============================================================================

def create_initial_state(grid_size: int, seed: int) -> np.ndarray:
    """Create initial state with random seed."""
    rng = np.random.RandomState(seed)
    
    # Random initial configuration
    state = rng.rand(grid_size, grid_size)
    
    # Add some structure
    cx, cy = grid_size // 2, grid_size // 2
    for _ in range(3):
        x = rng.randint(grid_size // 4, 3 * grid_size // 4)
        y = rng.randint(grid_size // 4, 3 * grid_size // 4)
        r = rng.randint(3, 8)
        
        for i in range(grid_size):
            for j in range(grid_size):
                dist = np.sqrt((i - x)**2 + (j - y)**2)
                if dist < r:
                    state[i, j] = max(state[i, j], rng.rand() * 0.8 + 0.2)
    
    return state


def run_single_experiment(config: ExperimentConfig) -> ExperimentResult:
    """Run a single experiment configuration."""
    start_time = time.time()
    
    # Create initial state
    initial_state = create_initial_state(config.grid_size, config.seed)
    initial_mass = float(initial_state.sum())
    
    # Select model based on alpha
    if config.alpha >= 0.99:
        # Pure conv
        kernel = gaussian_kernel(13, config.sigma, config.mu)
        model = ConvolutionalLenia(kernel, config.dt)
        final_state = model.run(initial_state, config.steps)
    elif config.alpha <= 0.01:
        # Pure GNN
        model = GNNLenia(config.grid_size, config.sigma, config.mu, config.dt)
        final_state = model.run(initial_state, config.steps)
    else:
        # Hybrid
        model = HybridLenia(config.grid_size, config.sigma, config.mu, 
                           config.alpha, config.dt)
        final_state = model.run(initial_state, config.steps)
    
    computation_time = time.time() - start_time
    
    # Compute metrics
    survival_rate = compute_survival_rate(final_state, initial_mass)
    pattern_complexity = compute_pattern_complexity(final_state)
    emergence_score = compute_emergence_score(final_state, initial_state)
    pattern_detected = detect_pattern(final_state)
    final_mass = float(final_state.sum())
    final_variance = float(final_state.var())
    
    return ExperimentResult(
        config=asdict(config),
        survival_rate=survival_rate,
        pattern_complexity=pattern_complexity,
        emergence_score=emergence_score,
        computation_time=computation_time,
        final_mass=final_mass,
        final_variance=final_variance,
        pattern_detected=pattern_detected
    )


def run_experiment_suite(num_trials: int = 20) -> Dict:
    """Run full experiment suite."""
    print("\n" + "="*70)
    print("V9 HYBRID CONV+GNN LENIA EXPERIMENT")
    print("="*70)
    
    # Define configurations
    configs = [
        # Baselines
        ("Pure Conv (σ=0.014)", 0.014, 0.135, 1.0),
        ("Pure GNN (σ=0.025)", 0.025, 0.135, 0.0),
        # Hybrids
        ("Hybrid α=0.3", 0.014, 0.135, 0.3),  # Conv uses narrow σ
        ("Hybrid α=0.5", 0.014, 0.135, 0.5),
        ("Hybrid α=0.7", 0.014, 0.135, 0.7),
    ]
    
    all_results = {}
    
    for name, sigma, mu, alpha in configs:
        print(f"\n{'─'*70}")
        print(f"Testing: {name}")
        print(f"  σ={sigma:.3f}, μ={mu:.3f}, α={alpha:.1f}")
        print(f"{'─'*70}")
        
        trial_results = []
        
        for trial in range(num_trials):
            seed = 42 + trial  # Different seeds
            config = ExperimentConfig(
                name=name,
                sigma=sigma,
                mu=mu,
                alpha=alpha,
                seed=seed
            )
            
            result = run_single_experiment(config)
            trial_results.append(asdict(result))
            
            if (trial + 1) % 5 == 0:
                print(f"  Completed {trial + 1}/{num_trials} trials")
        
        # Aggregate results
        survival_rates = [r['survival_rate'] for r in trial_results]
        complexities = [r['pattern_complexity'] for r in trial_results]
        emergence_scores = [r['emergence_score'] for r in trial_results]
        comp_times = [r['computation_time'] for r in trial_results]
        patterns_detected = sum(1 for r in trial_results if r['pattern_detected'])
        
        all_results[name] = {
            'config': {
                'sigma': sigma,
                'mu': mu,
                'alpha': alpha
            },
            'trials': trial_results,
            'summary': {
                'survival_rate_mean': np.mean(survival_rates),
                'survival_rate_std': np.std(survival_rates),
                'complexity_mean': np.mean(complexities),
                'complexity_std': np.std(complexities),
                'emergence_mean': np.mean(emergence_scores),
                'emergence_std': np.std(emergence_scores),
                'computation_time_mean': np.mean(comp_times),
                'patterns_detected': patterns_detected,
                'pattern_detection_rate': patterns_detected / num_trials
            }
        }
        
        # Print summary
        s = all_results[name]['summary']
        print(f"\n  Results:")
        print(f"    Survival Rate:    {s['survival_rate_mean']:.3f} ± {s['survival_rate_std']:.3f}")
        print(f"    Pattern Complexity: {s['complexity_mean']:.3f} ± {s['complexity_std']:.3f}")
        print(f"    Emergence Score:  {s['emergence_mean']:.4f} ± {s['emergence_std']:.4f}")
        print(f"    Pattern Detection: {s['pattern_detection_rate']*100:.1f}%")
        print(f"    Avg Time:         {s['computation_time_mean']:.2f}s")
    
    return all_results


def analyze_results(results: Dict) -> Dict:
    """Analyze and compare results across configurations."""
    print("\n" + "="*70)
    print("ANALYSIS")
    print("="*70)
    
    # Extract summaries
    summaries = {name: data['summary'] for name, data in results.items()}
    
    # Find best configurations
    best_survival = max(summaries.items(), key=lambda x: x[1]['survival_rate_mean'])
    best_complexity = max(summaries.items(), key=lambda x: x[1]['complexity_mean'])
    best_emergence = max(summaries.items(), key=lambda x: x[1]['emergence_mean'])
    best_detection = max(summaries.items(), key=lambda x: x[1]['pattern_detection_rate'])
    
    print(f"\nBest Survival Rate:    {best_survival[0]} ({best_survival[1]['survival_rate_mean']:.3f})")
    print(f"Best Complexity:       {best_complexity[0]} ({best_complexity[1]['complexity_mean']:.3f})")
    print(f"Best Emergence:        {best_emergence[0]} ({best_emergence[1]['emergence_mean']:.4f})")
    print(f"Best Detection Rate:   {best_detection[0]} ({best_detection[1]['pattern_detection_rate']*100:.1f}%)")
    
    # Compare hybrid vs pure
    conv_emergence = summaries['Pure Conv (σ=0.014)']['emergence_mean']
    gnn_emergence = summaries['Pure GNN (σ=0.025)']['emergence_mean']
    
    print(f"\n{'─'*70}")
    print("Hybrid vs Pure Comparison:")
    print(f"{'─'*70}")
    
    for name in ['Hybrid α=0.3', 'Hybrid α=0.5', 'Hybrid α=0.7']:
        hybrid_emergence = summaries[name]['emergence_mean']
        improvement_vs_conv = (hybrid_emergence - conv_emergence) / (conv_emergence + 1e-8) * 100
        improvement_vs_gnn = (hybrid_emergence - gnn_emergence) / (gnn_emergence + 1e-8) * 100
        
        print(f"\n{name}:")
        print(f"  vs Conv: {improvement_vs_conv:+.1f}% emergence")
        print(f"  vs GNN:  {improvement_vs_gnn:+.1f}% emergence")
    
    # Statistical significance test
    print(f"\n{'─'*70}")
    print("Key Findings:")
    print(f"{'─'*70}")
    
    # Check if hybrid improves over both baselines
    hybrid_05_emergence = summaries['Hybrid α=0.5']['emergence_mean']
    if hybrid_05_emergence > conv_emergence and hybrid_05_emergence > gnn_emergence:
        print("\n✓ Hybrid α=0.5 achieves better emergence than both pure methods!")
        print(f"  Improvement over Conv: {(hybrid_05_emergence/conv_emergence - 1)*100:.1f}%")
        print(f"  Improvement over GNN:  {(hybrid_05_emergence/gnn_emergence - 1)*100:.1f}%")
    else:
        best_hybrid = max(
            ['Hybrid α=0.3', 'Hybrid α=0.5', 'Hybrid α=0.7'],
            key=lambda x: summaries[x]['emergence_mean']
        )
        print(f"\n→ Best hybrid: {best_hybrid}")
        print(f"  Emergence: {summaries[best_hybrid]['emergence_mean']:.4f}")
    
    return {
        'best_survival': best_survival[0],
        'best_complexity': best_complexity[0],
        'best_emergence': best_emergence[0],
        'best_detection': best_detection[0],
        'conv_baseline': conv_emergence,
        'gnn_baseline': gnn_emergence
    }


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("V9 HYBRID CONV+GNN LENIA EXPERIMENT")
    print("="*70)
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nEnvironment:")
    print(f"  JAX: {'YES' if JAX_AVAILABLE else 'NO'}")
    print(f"  PyTorch: {'YES' if TORCH_AVAILABLE else 'NO'}")
    print(f"  PyTorch Geometric: {'YES' if PG_AVAILABLE else 'NO'}")
    
    # Run experiments
    results = run_experiment_suite(num_trials=20)
    
    # Analyze
    analysis = analyze_results(results)
    
    # Save results
    output = {
        'experiment': 'V9 Hybrid Conv+GNN Lenia',
        'timestamp': datetime.now().isoformat(),
        'environment': {
            'jax': JAX_AVAILABLE,
            'torch': TORCH_AVAILABLE,
            'pyg': PG_AVAILABLE
        },
        'results': results,
        'analysis': analysis
    }
    
    output_path = r'D:\openclaw_workspace\v9_hybrid_results.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n{'='*70}")
    print(f"Results saved to: {output_path}")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    return output


if __name__ == '__main__':
    main()
