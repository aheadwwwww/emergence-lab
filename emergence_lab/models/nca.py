"""
NCA — Neural Cellular Automata

基于 Distill 的 Growing Neural Cellular Automata，简化版。
"""

import numpy as np

from ..core.metrics import EmergenceMetrics


class NCA:
    """Neural Cellular Automata（简化版）
    
    Features:
        - 16 通道（RGBA + 12 hidden）
        - 随机异步更新 (50%)
        - 简化更新规则
    """
    
    def __init__(self, channels=16, fire_rate=0.5, hidden_size=32):
        self.channels = channels
        self.fire_rate = fire_rate
        self.hidden_size = hidden_size
        self.grid = None
        self.history = []
    
    def init_grid(self, shape=(128, 128), seed_size=4):
        """初始化网格（中心种子）"""
        h, w = shape
        self.grid = np.zeros((h, w, self.channels), dtype=np.float32)
        
        # Center seed
        cy, cx = h // 2, w // 2
        r = seed_size // 2
        self.grid[cy-r:cy+r, cx-r:cx+r, 3] = 1.0  # Alpha channel
        self.grid[cy-r:cy+r, cx-r:cx+r, :3] = 0.5  # RGB
        
        # Random hidden channels
        rng = np.random.default_rng()
        seed_h, seed_w = 2*r, 2*r
        self.grid[cy-r:cy+r, cx-r:cx+r, 4:] = rng.uniform(0.1, 0.3, (seed_h, seed_w, self.channels-4))
        
        self.history = [self.grid.copy()]
    
    def run(self, steps=100, record_every=10, verbose=True):
        """运行模拟
        
        改进规则：基于 Distill Growing NCA
        - Sobel 感知核
        - 存活约束
        - 更强的扩散
        """
        # Sobel-like perception kernels
        sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32) / 8.0
        sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float32) / 8.0
        laplacian = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)
        
        from scipy.ndimage import convolve
        
        for i in range(steps):
            grid_np = self.grid.copy()
            
            # Alive mask: alpha > 0.1
            alive = grid_np[:, :, 3] > 0.1
            
            # Pre-life: expand alive region for growth
            pre_alive = np.zeros_like(alive)
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    pre_alive |= np.roll(np.roll(alive, di, axis=0), dj, axis=1)
            
            # Perception: Sobel gradients + Laplacian
            perception = []
            for c in range(self.channels):
                px = convolve(grid_np[:, :, c], sobel_x, mode='wrap')
                py = convolve(grid_np[:, :, c], sobel_y, mode='wrap')
                pl = convolve(grid_np[:, :, c], laplacian, mode='wrap')
                perception.extend([px, py, pl])
            perception = np.stack(perception, axis=-1)  # (H, W, 3*C)
            
            # Simplified update: random projection + bias
            rng = np.random.default_rng()
            
            # Random weights for this step (simulating learned weights)
            if not hasattr(self, '_update_weights'):
                self._update_weights = rng.normal(0, 0.1, (3 * self.channels, self.channels)).astype(np.float32)
                self._update_bias = rng.uniform(-0.01, 0.01, self.channels).astype(np.float32)
            
            update = np.tanh(perception @ self._update_weights + self._update_bias)
            
            # Scale update
            update = 0.1 * update
            
            # Fire rate mask (stochastic updates)
            fire_mask = rng.uniform(0, 1, grid_np.shape[:2]) < self.fire_rate
            
            # Only update cells in pre_alive region
            active = fire_mask & pre_alive
            
            # Apply update
            self.grid = grid_np + update * active[..., None]
            
            # Alive constraint: dead cells (alpha < 0.1) can't have RGB
            dead_mask = self.grid[:, :, 3] < 0.1
            self.grid[dead_mask, :3] = 0
            
            # Clip to [0, 1]
            self.grid = np.clip(self.grid, 0, 1)
            
            if (i + 1) % record_every == 0:
                self.history.append(self.grid.copy())
                if verbose:
                    alive_frac = np.mean(self.grid[:, :, 3] > 0.1)
                    entropy = EmergenceMetrics.entropy(self.grid[:, :, 3])
                    score = EmergenceMetrics.emergence_score(self.grid[:, :, 3])
                    print(f"  step {i+1}/{steps} | alive={alive_frac:.3f} score={score:.3f}")
        
        # Final metrics
        rgba = self.grid[:, :, :4]
        alive_frac = float(np.mean(rgba[:, :, 3] > 0.1))
        entropy = EmergenceMetrics.entropy(rgba[:, :, 3])
        edge = EmergenceMetrics.edge_density(rgba[:, :, 3])
        score = EmergenceMetrics.emergence_score(rgba[:, :, 3])
        return {
            'alive': alive_frac,
            'entropy': entropy,
            'edge_density': edge,
            'emergence_score': score,
            'state': EmergenceMetrics.classify(rgba[:, :, 3]),
        }
    
    def get_rgba(self):
        """获取 RGBA 可视化"""
        return self.grid[:, :, :4]