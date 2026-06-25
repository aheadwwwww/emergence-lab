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
        
        简化规则：随机扰动 + 存活扩散
        """
        for i in range(steps):
            grid_np = self.grid.copy()
            
            # Alive mask: alpha > 0.1
            alive = grid_np[:, :, 3] > 0.1
            
            # Perceive neighbors (simplified: average neighbor state)
            perception = np.zeros_like(grid_np)
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue
                    rolled = np.roll(np.roll(grid_np, di, axis=0), dj, axis=1)
                    perception += rolled
            perception /= 8.0
            
            # Update rule: move toward local average + noise
            rng = np.random.default_rng()
            noise = rng.normal(0, 0.02, grid_np.shape).astype(np.float32)
            
            update = 0.1 * (perception - grid_np) + noise
            
            # Fire rate mask
            fire_mask = rng.uniform(0, 1, grid_np.shape[:2]) < self.fire_rate
            
            # Apply update (only to alive neighbors of alive cells)
            alive_2d = alive.any()
            active = fire_mask.copy()
            if alive_2d:
                # Only update cells near alive cells
                alive_neighbors = np.zeros_like(fire_mask)
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        alive_neighbors |= np.roll(np.roll(alive, di, axis=0), dj, axis=1)
                active = fire_mask & alive_neighbors
            
            self.grid = grid_np + update * active[..., None]
            self.grid = np.clip(self.grid, 0, 1)
            
            if (i + 1) % record_every == 0:
                self.history.append(self.grid.copy())
                if verbose:
                    alive_frac = np.mean(self.grid[:, :, 3] > 0.1)
                    print(f"  step {i+1}/{steps} | alive={alive_frac:.3f}")
        
        # Final metrics
        rgba = self.grid[:, :, :4]
        alive_frac = float(np.mean(rgba[:, :, 3] > 0.1))
        return {
            'alive': alive_frac,
            'state': 'structure' if alive_frac > 0.01 else 'dead',
        }
    
    def get_rgba(self):
        """获取 RGBA 可视化"""
        return self.grid[:, :, :4]