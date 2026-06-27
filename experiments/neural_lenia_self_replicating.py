"""
Neural Lenia + Self-Replication
================================

结合 Google Self-Replicating NN 的思想，让 Neural Lenia 学会自复制。

核心思路：
1. 用神经网络生成 Lenia 核
2. 训练目标是模式能自复制（产生稳定的"后代"）
3. 评估：模式存活 + 模式能"繁殖"（在空白区域产生新结构）

Reference:
- Google Self-Organising Systems: https://github.com/google-research/self-organising-systems
- My Neural Lenia prototype: experiments/neural_lenia.py
"""

import numpy as np
from PIL import Image
import json
from pathlib import Path
import time

try:
    import jax
    import jax.numpy as jnp
    from jax import jit, grad
    import flax.linen as nn
    from flax.core import freeze, unfreeze
    import optax
    JAX_AVAILABLE = True
except ImportError:
    JAX_AVAILABLE = False
    print("JAX not available. Install with: pip install jax jaxlib flax optax")


class NeuralKernel(nn.Module):
    """Neural network that generates a Lenia kernel from (r, theta) coordinates"""
    hidden_size: int = 32
    
    @nn.compact
    def __call__(self, r, theta):
        # Concatenate r and theta
        x = jnp.concatenate([r, theta], axis=-1)
        
        # MLP layers
        x = nn.Dense(self.hidden_size)(x)
        x = nn.tanh(x)
        x = nn.Dense(self.hidden_size)(x)
        x = nn.tanh(x)
        x = nn.Dense(1)(x)
        x = nn.sigmoid(x)
        
        return x.squeeze()


class SelfReplicatingLenia:
    """
    Neural Lenia with self-replication training.
    
    The kernel is parameterized by a neural network.
    Training goal: patterns that survive AND can "replicate" into empty regions.
    """
    
    def __init__(self, R=13, grid_size=128, kernel_hidden=32):
        self.R = R
        self.grid_size = grid_size
        self.kernel_hidden = kernel_hidden
        
        # Initialize neural kernel
        self.kernel_net = NeuralKernel(hidden_size=kernel_hidden)
        
        # Pre-compute coordinate grids for kernel generation
        self._init_kernel_coords()
        
    def _init_kernel_coords(self):
        """Pre-compute (r, theta) coordinates for kernel generation"""
        kernel_size = 2 * self.R + 1
        y, x = np.ogrid[-self.R:self.R+1, -self.R:self.R+1]
        
        # Convert to polar coordinates
        r = np.sqrt(x*x + y*y) / self.R  # Normalized [0, 1]
        theta = np.arctan2(y, x) / np.pi  # Normalized [-1, 1]
        
        # Create coordinate pairs
        coords = np.stack([r, theta], axis=-1)
        coords = coords.reshape(-1, 2)
        
        # Mask for ring region
        mask = (r > 0.1) & (r <= 1.0)
        
        self.kernel_coords = jnp.array(coords)
        self.kernel_mask = jnp.array(mask.flatten())
        self.kernel_shape = (kernel_size, kernel_size)
        
    def generate_kernel(self, params):
        """Generate kernel using neural network"""
        # Get kernel values from neural network
        r = self.kernel_coords[:, 0:1]
        theta = self.kernel_coords[:, 1:2]
        
        kernel_flat = self.kernel_net.apply(params, r, theta)
        
        # Apply mask (only ring region is active)
        kernel_flat = kernel_flat * self.kernel_mask
        
        return kernel_flat.reshape(self.kernel_shape)
    
    def lenia_step(self, grid, kernel, dt=1.0):
        """Single Lenia step with given kernel"""
        # Convolution
        from jax.scipy.signal import convolve2d
        
        # Pad for circular boundary
        padded = jnp.pad(grid, self.R, mode='wrap')
        
        # Convolve
        conv = convolve2d(padded, kernel, mode='valid')
        
        # Growth function (simple bell curve)
        mu = 0.15
        sigma = 0.014
        growth = jnp.exp(-((conv - mu)**2) / (2 * sigma**2))
        
        # Update
        new_grid = jnp.clip(grid + dt * (growth - 0.5), 0, 1)
        
        return new_grid
    
    def run_simulation(self, params, steps=200, seed=0):
        """Run Lenia simulation with neural kernel"""
        key = jax.random.PRNGKey(seed)
        
        # Generate kernel
        kernel = self.generate_kernel(params)
        
        # Initialize grid with random pattern
        grid = jax.random.uniform(key, (self.grid_size, self.grid_size))
        
        # Add a "seed" pattern in center
        center = self.grid_size // 2
        size = 10
        grid = grid.at[center-size:center+size, center-size:center+size].set(
            jax.random.uniform(key, (2*size, 2*size), minval=0.5, maxval=1.0)
        )
        
        # Run simulation
        alive_history = []
        for t in range(steps):
            grid = self.lenia_step(grid, kernel)
            alive = jnp.mean((grid > 0.1).astype(float))
            alive_history.append(float(alive))
        
        final_alive = alive_history[-1]
        late_variance = np.var(alive_history[-50:])
        
        return {
            'final_grid': np.array(grid),
            'final_alive': final_alive,
            'late_variance': late_variance,
            'alive_history': alive_history
        }
    
    def evaluate_self_replication(self, params, steps=300):
        """
        Evaluate self-replication capability.
        
        Criteria:
        1. Survival: pattern stays alive
        2. Expansion: pattern grows into empty regions
        3. Stability: low variance in late stages
        """
        result = self.run_simulation(params, steps=steps)
        
        alive = result['final_alive']
        variance = result['late_variance']
        
        # Self-replication score
        # High alive + low variance = good self-replication
        score = alive * 2 - variance * 10
        
        return {
            'score': float(score),
            'alive': float(alive),
            'variance': float(variance)
        }
    
    def random_search(self, n_iterations=20, steps=200):
        """
        Random search for self-replicating kernels.
        """
        print(f"Searching for self-replicating kernels ({n_iterations} iterations)...")
        
        best_score = -float('inf')
        best_params = None
        results = []
        
        for i in range(n_iterations):
            # Initialize random parameters
            key = jax.random.PRNGKey(i)
            dummy_r = jnp.ones((1, 1))
            dummy_theta = jnp.ones((1, 1))
            params = self.kernel_net.init(key, dummy_r, dummy_theta)
            
            # Evaluate
            eval_result = self.evaluate_self_replication(params, steps=steps)
            
            results.append({
                'iteration': i,
                **eval_result
            })
            
            if eval_result['score'] > best_score:
                best_score = eval_result['score']
                best_params = params
            
            # Progress
            if (i + 1) % 5 == 0:
                print(f"  [{i+1}/{n_iterations}] Best score: {best_score:.3f}")
        
        return {
            'best_params': best_params,
            'best_score': best_score,
            'all_results': results
        }


def test_self_replicating_lenia():
    """Test the self-replicating Lenia implementation"""
    print("=" * 60)
    print("Self-Replicating Neural Lenia Test")
    print("=" * 60)
    
    if not JAX_AVAILABLE:
        print("\n[SKIP] JAX not available")
        return
    
    # Create instance
    srl = SelfReplicatingLenia(R=13, grid_size=64, kernel_hidden=16)
    
    # Run random search
    result = srl.random_search(n_iterations=10, steps=100)
    
    print(f"\n[RESULT] Best score: {result['best_score']:.3f}")
    
    # Generate kernel image for best params
    if result['best_params'] is not None:
        kernel = np.array(srl.generate_kernel(result['best_params']))
        kernel_img = Image.fromarray((kernel * 255).astype(np.uint8))
        
        output_path = Path("D:/openclaw_workspace/experiments/output")
        output_path.mkdir(exist_ok=True)
        
        kernel_path = output_path / f"self_repl_kernel_{int(time.time())}.png"
        kernel_img.save(kernel_path)
        print(f"[SAVED] Kernel image: {kernel_path}")
        
        # Run simulation with best params
        sim_result = srl.run_simulation(result['best_params'], steps=200)
        
        # Save final grid
        grid_img = Image.fromarray((np.array(sim_result['final_grid']) * 255).astype(np.uint8))
        grid_path = output_path / f"self_repl_grid_{int(time.time())}.png"
        grid_img.save(grid_path)
        print(f"[SAVED] Grid image: {grid_path}")
        
        # Save results
        results_path = output_path / f"self_repl_results_{int(time.time())}.json"
        with open(results_path, 'w') as f:
            json.dump({
                'best_score': result['best_score'],
                'all_results': result['all_results'],
                'sim_alive': sim_result['final_alive'],
                'sim_variance': sim_result['late_variance']
            }, f, indent=2)
        print(f"[SAVED] Results: {results_path}")
    
    print("\n[DONE] Self-replicating Lenia test complete")


if __name__ == '__main__':
    test_self_replicating_lenia()
