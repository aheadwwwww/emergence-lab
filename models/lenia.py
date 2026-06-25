"""
Lenia — 连续细胞自动机

基于 Bert Chan 的 Lenia，用 JAX 加速。
"""

import jax
import jax.numpy as jnp
from jax import jit
import numpy as np
from functools import partial
import time

from ..core.metrics import EmergenceMetrics


class Lenia:
    """Lenia 连续细胞自动机
    
    Parameters:
        R: 核半径
        mu: 生长中心
        sigma: 生长宽度
        kn: 核类型 (1=bump4)
        gn: 生长函数类型 (1=gaussian)
        fire_rate: 异步更新比例 (1.0=全同步)
    """
    
    def __init__(self, R=20, mu=0.15, sigma=0.03, kn=1, gn=1, fire_rate=1.0):
        self.R = R
        self.mu = mu
        self.sigma = sigma
        self.kn = kn
        self.gn = gn
        self.fire_rate = fire_rate
        self.kernel_fft = None
        self.grid = None
        self.history = []
    
    def _make_kernel(self, shape):
        """创建 FFT 核"""
        h, w = shape
        R = self.R
        kn = self.kn
        
        # Create disk kernel
        y, x = np.ogrid[-R:R+1, -R:R+1]
        r = np.sqrt(x**2 + y**2)
        kernel = (1 - (r / R)**2) ** kn if kn > 0 else np.exp(-(r/R)**2)
        kernel[r > R] = 0
        kernel = kernel / kernel.sum()
        
        # Pad and shift
        kh, kw = kernel.shape
        pad_h, pad_w = (h - kh) // 2, (w - kw) // 2
        kernel_pad = np.pad(kernel, ((pad_h, h-kh-pad_h), (pad_w, w-kw-pad_w)))
        kernel_pad = np.roll(kernel_pad, -(pad_h + R), axis=0)
        kernel_pad = np.roll(kernel_pad, -(pad_w + R), axis=1)
        
        self.kernel_fft = jnp.fft.fft2(jnp.array(kernel_pad))
    
    def init_grid(self, shape=(256, 256), mode='random'):
        """初始化网格
        
        Args:
            shape: 网格形状
            mode: 'random' 或 'orbium'
        """
        h, w = shape
        self._make_kernel(shape)
        
        if mode == 'random':
            rng = np.random.default_rng()
            self.grid = rng.uniform(0, 0.2, (h, w)).astype(np.float32)
            cy, cx = h // 2, w // 2
            r = min(shape) // 6
            blob = rng.uniform(0.2, 0.6, (2*r+1, 2*r+1))
            self.grid[cy-r:cy+r+1, cx-r:cx+r+1] = blob
        else:
            # Orbium seed
            from lenia_jax import make_orbium
            self.grid = make_orbium(shape, self.R)
        
        self.grid = jnp.array(self.grid)
        self.history = [np.array(self.grid)]
    
    @partial(jit, static_argnums=(0,))
    def _step(self, grid, kernel_fft, mu, sigma):
        """单步更新"""
        h, w = grid.shape
        
        # Convolution
        grid_fft = jnp.fft.fft2(grid)
        potential = jnp.fft.ifft2(grid_fft * kernel_fft).real
        potential = jnp.clip(potential, 0, 1)
        
        # Growth
        growth = jnp.exp(-((potential - mu)**2) / (2 * sigma**2)) * 2 - 1
        
        # Apply fire_rate as mask (all cases, even fire_rate=1.0)
        # This is handled outside JIT by caller
        new_grid = jnp.clip(grid + 0.1 * growth, 0, 1)
        return new_grid
    
    def run(self, steps=100, record_every=10, verbose=True):
        """运行模拟
        
        Args:
            steps: 步数
            record_every: 记录间隔
            verbose: 是否打印进度
        """
        for i in range(steps):
            # JIT step
            self.grid = self._step(
                self.grid, self.kernel_fft, 
                self.mu, self.sigma
            )
            
            # Async mask (outside JIT)
            if self.fire_rate < 1.0:
                rng = np.random.default_rng()
                mask = rng.uniform(0, 1, self.grid.shape) < self.fire_rate
                self.grid = self.grid * mask + self.history[-1] * (1 - mask)
                self.grid = jnp.array(self.grid)
            
            if (i + 1) % record_every == 0:
                self.history.append(np.array(self.grid))
                if verbose:
                    metrics = EmergenceMetrics.full_report(self.grid)
                    print(f"  step {i+1}/{steps} | alive={metrics['alive']:.3f} score={metrics['emergence_score']:.3f}")
        
        return EmergenceMetrics.full_report(self.grid, self.history)
    
    def measure(self):
        """度量当前状态"""
        return EmergenceMetrics.full_report(self.grid, self.history)
    
    def classify(self):
        """分类当前状态"""
        return EmergenceMetrics.classify(self.grid, self.history)
    
    def get_frame(self, index=-1):
        """获取指定帧"""
        return self.history[index]
    
    def get_timeline(self):
        """获取所有帧"""
        return self.history