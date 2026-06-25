"""
涌现度量工具

量化涌现行为的关键指标。
"""

import jax.numpy as jnp
import numpy as np


class EmergenceMetrics:
    """涌现度量类"""
    
    @staticmethod
    def alive(grid, threshold=0.01):
        """存活细胞比例"""
        return float(jnp.mean(grid > threshold))
    
    @staticmethod
    def entropy(grid, bins=50):
        """状态熵"""
        hist, _ = np.histogram(grid.flatten(), bins=bins, range=(0, 1))
        hist = hist[hist > 0]
        prob = hist / hist.sum()
        return float(-np.sum(prob * np.log2(prob)))
    
    @staticmethod
    def edge_density(grid, threshold=0.1):
        """边缘密度（结构化区域）"""
        # Sobel-like gradient
        dx = np.abs(np.diff(grid, axis=1))
        dy = np.abs(np.diff(grid, axis=0))
        edges = np.pad(dx, ((0,0),(0,1))) + np.pad(dy, ((0,1),(0,0)))
        return float(np.mean(edges > threshold))
    
    @staticmethod
    def stability(grid_history, window=10):
        """稳定性（最后 window 步的变化率）"""
        if len(grid_history) < window:
            return 0.0
        recent = grid_history[-window:]
        diffs = [np.mean(np.abs(recent[i+1] - recent[i])) for i in range(len(recent)-1)]
        return float(1.0 - np.mean(diffs))
    
    @staticmethod
    def emergence_score(grid, grid_history=None):
        """综合涌现指数
        
        结合 alive、entropy、edge_density 的综合评分
        """
        alive = EmergenceMetrics.alive(grid)
        entropy = EmergenceMetrics.entropy(grid)
        edge = EmergenceMetrics.edge_density(grid)
        
        # Normalize entropy to [0, 1] (max entropy for 50 bins is log2(50) ≈ 5.6)
        entropy_norm = min(entropy / 5.6, 1.0)
        
        # Weighted combination
        score = 0.4 * alive + 0.3 * entropy_norm + 0.3 * edge
        return float(score)
    
    @staticmethod
    def classify(grid, grid_history=None):
        """分类状态
        
        Returns:
            'dead': alive < 0.01
            'simple': alive > 0.01 but edge_density < 0.05
            'structure': edge_density >= 0.05
        """
        alive = EmergenceMetrics.alive(grid)
        edge = EmergenceMetrics.edge_density(grid)
        
        if alive < 0.01:
            return 'dead'
        elif edge < 0.05:
            return 'simple'
        else:
            return 'structure'
    
    @staticmethod
    def full_report(grid, grid_history=None):
        """完整度量报告"""
        return {
            'alive': EmergenceMetrics.alive(grid),
            'entropy': EmergenceMetrics.entropy(grid),
            'edge_density': EmergenceMetrics.edge_density(grid),
            'stability': EmergenceMetrics.stability(grid_history) if grid_history else 0.0,
            'emergence_score': EmergenceMetrics.emergence_score(grid, grid_history),
            'state': EmergenceMetrics.classify(grid, grid_history),
        }