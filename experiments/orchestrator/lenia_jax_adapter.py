"""
Lenia JAX Adapter for Orchestrator

将 emergence_lab 的 Lenia 集成到编排器中。
"""

import sys
from pathlib import Path

# Add paths
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))
sys.path.insert(0, str(workspace_root / 'experiments' / 'orchestrator'))

# Import BaseExperiment directly
import importlib.util
spec = importlib.util.spec_from_file_location("registry", workspace_root / 'experiments' / 'orchestrator' / 'registry.py')
registry_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(registry_module)
BaseExperiment = registry_module.BaseExperiment
import numpy as np
from PIL import Image
import random
import time

# Import emergence_lab Lenia
try:
    from emergence_lab import Lenia
    from emergence_lab.core.metrics import EmergenceMetrics
    LENIA_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Lenia not available: {e}")
    LENIA_AVAILABLE = False


class LeniaJAX(BaseExperiment):
    """Lenia with JAX acceleration"""
    name = "lenia_jax"
    description = "Lenia 连续元胞自动机 - JAX 加速版"
    supports_animation = True
    
    def __init__(self):
        if not LENIA_AVAILABLE:
            raise ImportError("emergence_lab.Lenia not available. Install JAX and dependencies.")
    
    def generate_params(self):
        """生成随机 Lenia 参数"""
        # Classic creatures with some randomization
        templates = [
            {'R': 13, 'mu': 0.15, 'sigma': 0.014},  # Orbium-like
            {'R': 12, 'mu': 0.15, 'sigma': 0.013},  # Geminium-like
            {'R': 14, 'mu': 0.26, 'sigma': 0.036},  # Hydrogeminium-like
        ]
        params = random.choice(templates)
        
        # Add some randomization
        params['mu'] += random.uniform(-0.02, 0.02)
        params['sigma'] += random.uniform(-0.005, 0.005)
        
        params['shape'] = random.choice([(128, 128), (256, 256)])
        params['steps'] = random.randint(100, 300)
        
        return params
    
    def run(self, params):
        """运行 Lenia 实验"""
        R = params['R']
        mu = params['mu']
        sigma = params['sigma']
        shape = params['shape']
        steps = params['steps']
        
        # Create Lenia instance
        lenia = Lenia(R=R, mu=mu, sigma=sigma)
        lenia.init_grid(shape=shape, mode='random')
        
        # Run simulation
        result = lenia.run(steps=steps, record_every=50, verbose=False)
        
        # Convert JAX array to numpy for storage
        grid_np = np.array(lenia.grid)
        
        return {
            'grid': grid_np,
            'emergence_score': result['emergence_score'],
            'alive': result['alive'],
            'state': result['state'],
            'params': {'R': R, 'mu': mu, 'sigma': sigma}
        }
    
    def animate(self, params):
        """生成动画帧"""
        # For now, just return final frame
        # TODO: Implement proper history extraction
        result = self.run(params)
        return [self.visualize(result)]
    
    def visualize(self, result):
        """可视化 Lenia 状态"""
        grid = result['grid']
        h, w = grid.shape
        
        # Normalize to [0, 255]
        grid_norm = ((grid - grid.min()) / (grid.max() - grid.min() + 1e-8) * 255).astype(np.uint8)
        
        # Create RGB image with colormap
        img_array = np.zeros((h, w, 3), dtype=np.uint8)
        
        # Color mapping: low = dark blue, high = cyan/white
        img_array[:, :, 0] = (grid_norm * 0.3).astype(np.uint8)  # R
        img_array[:, :, 1] = (grid_norm * 0.8).astype(np.uint8)  # G
        img_array[:, :, 2] = grid_norm  # B
        
        img = Image.fromarray(img_array, 'RGB')
        
        # Scale up for visibility
        scale = max(2, 512 // max(h, w))
        if scale > 1:
            img = img.resize((w * scale, h * scale), Image.NEAREST)
        
        return img
    
    def describe(self, params, result):
        """生成描述文本"""
        return (f"Lenia (JAX): R={params['R']}, μ={params['mu']:.3f}, σ={params['sigma']:.4f} | "
                f"State: {result['state']}, Score: {result['emergence_score']:.3f}")


# Test the adapter
if __name__ == '__main__':
    if LENIA_AVAILABLE:
        print("Testing LeniaJAX adapter...")
        adapter = LeniaJAX()
        
        params = adapter.generate_params()
        print(f"Generated params: {params}")
        
        result = adapter.run(params)
        print(f"Result: {adapter.describe(params, result)}")
        
        img = adapter.visualize(result)
        print(f"Image size: {img.size}")
        
        # Save
        output_path = Path('D:/emergence_experiments') / f'lenia_jax_test_{int(time.time())}.png'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path)
        print(f"Saved to: {output_path}")
    else:
        print("Lenia not available. Please install emergence_lab dependencies.")
