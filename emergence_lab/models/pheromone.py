"""
PheromoneCA — 信息素耦合细胞自动机

多通道 CA + 信息素场，模拟蚁群/黏菌的涌现行为。
"""

import jax
import jax.numpy as jnp
import numpy as np
from functools import partial

from ..core.metrics import EmergenceMetrics


class PheromoneCA:
    """信息素耦合细胞自动机
    
    Features:
        - 多通道生物 + 信息素场
        - 通道间通过信息素耦合
        - 局部扩散 + 全局衰减
    """
    
    def __init__(self, channels=3, R=12, deposit_rate=0.1, decay_rate=0.01):
        self.channels = channels
        self.R = R
        self.deposit_rate = deposit_rate
        self.decay_rate = decay_rate
        self.grid = None
        self.pheromone = None
        self.history = []
    
    def init_grid(self, shape=(128, 128)):
        """初始化网格"""
        h, w = shape
        
        # 生物通道
        self.grid = np.zeros((h, w, self.channels), dtype=np.float32)
        rng = np.random.default_rng()
        
        # 随机种子
        for c in range(self.channels):
            cy = rng.integers(h//4, 3*h//4)
            cx = rng.integers(w//4, 3*w//4)
            r = 8
            self.grid[cy-r:cy+r, cx-r:cx+r, c] = rng.uniform(0.3, 0.6, (2*r, 2*r))
        
        # 信息素场
        self.pheromone = np.zeros((h, w, self.channels), dtype=np.float32)
        
        self.history = [(np.array(self.grid), np.array(self.pheromone))]
    
    def run(self, steps=100, record_every=10, verbose=True):
        """运行模拟"""
        for i in range(steps):
            # 生物通道更新（受信息素影响）
            grid_np = np.array(self.grid)
            pher_np = np.array(self.pheromone)
            
            # 扩散
            from scipy.ndimage import gaussian_filter
            for c in range(self.channels):
                grid_np[:, :, c] = gaussian_filter(grid_np[:, :, c], sigma=1.0)
            
            # 信息素沉积
            for c in range(self.channels):
                pher_np[:, :, c] += self.deposit_rate * grid_np[:, :, c]
            
            # 信息素衰减
            pher_np *= (1 - self.decay_rate)
            
            # 信息素影响生物
            for c in range(self.channels):
                # 同通道促进
                influence = 0.05 * pher_np[:, :, c]
                grid_np[:, :, c] = np.clip(grid_np[:, :, c] + influence, 0, 1)
            
            self.grid = jnp.array(grid_np)
            self.pheromone = jnp.array(pher_np)
            
            if (i + 1) % record_every == 0:
                self.history.append((np.array(self.grid), np.array(self.pheromone)))
                if verbose:
                    alive = np.mean(np.max(self.grid, axis=-1) > 0.01)
                    print(f"  step {i+1}/{steps} | alive={alive:.3f}")
        
        # Final metrics
        combined = np.max(np.array(self.grid), axis=-1)
        return EmergenceMetrics.full_report(combined)
    
    def get_combined(self):
        """获取合并的可视化"""
        return np.max(np.array(self.grid), axis=-1)