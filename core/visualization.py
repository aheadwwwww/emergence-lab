"""
可视化工具
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


class Visualizer:
    """可视化工具类"""
    
    @staticmethod
    def plot_grid(grid, title="", save_path=None, cmap='coolwarm'):
        """绘制单个网格"""
        fig, ax = plt.subplots(figsize=(6, 6))
        
        if grid.ndim == 3:
            # RGBA
            ax.imshow(grid, vmin=0, vmax=1)
        else:
            # 单通道
            ax.imshow(grid, cmap=cmap, vmin=0, vmax=1)
        
        ax.set_title(title)
        ax.axis('off')
        
        if save_path:
            fig.savefig(save_path, dpi=100, bbox_inches='tight')
            plt.close(fig)
        else:
            plt.show()
    
    @staticmethod
    def plot_timeline(history, n_frames=5, save_path=None, titles=None):
        """绘制时间线"""
        total = len(history)
        indices = np.linspace(0, total-1, n_frames, dtype=int)
        
        fig, axes = plt.subplots(1, n_frames, figsize=(4*n_frames, 4))
        if n_frames == 1:
            axes = [axes]
        
        cmap = plt.cm.coolwarm
        
        for i, idx in enumerate(indices):
            frame = history[idx]
            if frame.ndim == 3:
                axes[i].imshow(frame)
            else:
                axes[i].imshow(frame, cmap=cmap, vmin=0, vmax=1)
            
            if titles:
                axes[i].set_title(titles[i])
            else:
                axes[i].set_title(f'Step {idx}')
            axes[i].axis('off')
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=100, bbox_inches='tight')
            plt.close(fig)
        else:
            plt.show()
    
    @staticmethod
    def plot_comparison(models, names=None, save_path=None):
        """对比多个模型"""
        n = len(models)
        fig, axes = plt.subplots(1, n, figsize=(4*n, 4))
        if n == 1:
            axes = [axes]
        
        for i, model in enumerate(models):
            grid = model.get_frame(-1) if hasattr(model, 'get_frame') else model
            axes[i].imshow(grid, cmap='coolwarm', vmin=0, vmax=1)
            axes[i].set_title(names[i] if names else f'Model {i+1}')
            axes[i].axis('off')
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=100, bbox_inches='tight')
            plt.close(fig)
        else:
            plt.show()
    
    @staticmethod
    def create_gif(history, save_path, fps=10):
        """创建 GIF 动画"""
        import imageio
        
        frames = []
        for grid in history:
            if grid.ndim == 3:
                frame = (grid * 255).astype(np.uint8)
            else:
                frame = plt.cm.coolwarm(grid)[:, :, :3]
                frame = (frame * 255).astype(np.uint8)
            frames.append(frame)
        
        imageio.mimsave(save_path, frames, fps=fps)
        print(f"Saved GIF: {save_path}")