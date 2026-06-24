"""
Lorenz96 - Spatiotemporal Chaos Experiment
A simplified atmospheric model that exhibits emergent chaotic behavior
across spatial dimensions. Good metaphor for networked systems.
"""

import numpy as np
from PIL import Image
from pathlib import Path
import random
from abc import ABC, abstractmethod

# Avoid circular import - define minimal base locally
class _BaseExperiment(ABC):
    name = ""
    description = ""
    supports_animation = False
    
    @abstractmethod
    def generate_params(self) -> dict: pass
    @abstractmethod
    def run(self, params: dict) -> dict: pass
    @abstractmethod
    def visualize(self, result: dict) -> Image.Image: pass
    @abstractmethod
    def describe(self, params: dict, result: dict) -> str: pass
    
    def animate(self, params: dict) -> list: return []
    
    def save_image(self, img: Image.Image) -> str:
        import time
        timestamp = int(time.time())
        path = Path('D:/emergence_experiments') / f'{self.name}_{timestamp}.png'
        img.save(path)
        return str(path)
    
    def save_gif(self, frames: list, name_prefix: str = "", duration: int = 100) -> str:
        if not frames: return ""
        import time
        timestamp = int(time.time())
        prefix = name_prefix or self.name
        path = Path('D:/emergence_experiments') / f'{prefix}_{timestamp}.gif'
        frames[0].save(path, save_all=True, append_images=frames[1:],
                       duration=duration, loop=0, optimize=False)
        return str(path)

class Lorenz96Experiment(_BaseExperiment):
    name = "lorenz96"
    description = "Lorenz96 - 空间混沌，从局部规则涌现全局不可预测性"
    supports_animation = True
    
    def generate_params(self):
        return {
            'N': random.choice([40, 60, 80]),  # spatial grid points
            'F': random.uniform(7.0, 9.0),     # forcing (chaos at F > ~5)
            'steps': random.randint(2000, 5000),
            'dt': 0.01
        }
    
    def run(self, params):
        N = params['N']
        F = params['F']
        steps = params['steps']
        dt = params['dt']
        
        # Initialize with small perturbation
        x = F * np.ones(N) + 0.5 * np.random.randn(N)
        
        # Lorentz96 equations: dx_i/dt = (x_{i+1} - x_{i-2}) * x_{i-1} - x_i + F
        full_history = np.zeros((steps // 10 + 1, N))
        
        for t in range(steps):
            # Lorenz96 update
            dx = np.zeros(N)
            for i in range(N):
                dx[i] = (x[(i+1) % N] - x[(i-2) % N]) * x[(i-1) % N] - x[i] + F
            x += dx * dt
            
            if t % 10 == 0:
                full_history[t // 10] = x.copy()
        
        return {
            'final_state': x,
            'history': full_history,
            'N': N,
            'F': F,
            'steps': steps
        }
    
    def _state_to_img(self, state, history=None):
        """Visualize as a spacetime plot if history given, else as a bar chart"""
        if history is not None:
            # Spacetime heatmap
            h_steps, N = history.shape
            # Normalize
            h_min, h_max = history.min(), history.max()
            h_norm = ((history - h_min) / (h_max - h_min + 1e-8) * 255).astype(np.uint8)
            
            # Create heatmap with color
            img = Image.new('RGB', (N * 3, h_steps * 2), (10, 10, 20))
            pixels = img.load()
            
            for t in range(h_steps):
                for i in range(N):
                    v = h_norm[t, i]
                    # Blue (cold) to red (hot) colormap
                    if v < 128:
                        r = 20
                        g = int(20 + v * 1.5)
                        b = int(20 + v * 1.8)
                    else:
                        r = int(20 + (v - 128) * 1.8)
                        g = int(200 - (v - 128) * 1.2)
                        b = 240 - v
                    
                    r, g, b = max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
                    
                    for dt in range(2):
                        for di in range(3):
                            py = t * 2 + dt
                            px = i * 3 + di
                            if 0 <= px < N * 3 and 0 <= py < h_steps * 2:
                                pixels[px, py] = (r, g, b)
            
            return img
        else:
            # Bar chart of final state
            N = len(state)
            img = Image.new('RGB', (N * 4, 300), (10, 10, 20))
            pixels = img.load()
            
            s_min, s_max = state.min(), state.max()
            if s_max - s_min < 1e-8:
                s_max = s_min + 1
            
            for i in range(N):
                bar_h = int((state[i] - s_min) / (s_max - s_min) * 250) + 20
                for y in range(300 - bar_h, 300):
                    if y < 0 or y >= 300:
                        continue
                    # Gradient from blue to red
                    ratio = (state[i] - s_min) / (s_max - s_min + 1e-8)
                    r = int(40 + ratio * 200)
                    g = int(200 - ratio * 160)
                    b = int(240 - ratio * 200)
                    for di in range(4):
                        px = i * 4 + di
                        if 0 <= px < N * 4:
                            pixels[px, y] = (max(0, min(255, r)),
                                           max(0, min(255, g)),
                                           max(0, min(255, b)))
            
            return img
    
    def visualize(self, result):
        return self._state_to_img(result['final_state'], result['history'])
    
    def animate(self, params):
        """Show time evolution in slices"""
        N = params['N']
        F = params['F']
        steps = params['steps']
        dt = params['dt']
        
        x = F * np.ones(N) + 0.5 * np.random.randn(N)
        
        frames = []
        save_every = max(1, steps // 30)
        history_buffer = np.zeros((min(steps // 10, 100), N))
        buf_idx = 0
        
        for t in range(steps):
            dx = np.zeros(N)
            for i in range(N):
                dx[i] = (x[(i+1) % N] - x[(i-2) % N]) * x[(i-1) % N] - x[i] + F
            x += dx * dt
            
            if t % 10 == 0 and buf_idx < len(history_buffer):
                history_buffer[buf_idx] = x.copy()
                buf_idx += 1
            
            if t % save_every == 0 or t == steps - 1:
                # Use accumulated history for spacetime view
                active = history_buffer[:buf_idx]
                if len(active) > 1:
                    frames.append(self._state_to_img(x, active))
                else:
                    frames.append(self._state_to_img(x))
        
        return frames
    
    def describe(self, params, result):
        final = result['final_state']
        std_dev = np.std(final)
        chaos_level = "高" if std_dev > 1.5 else "中" if std_dev > 0.5 else "低"
        return (f"Lorenz96: N={result['N']}, F={result['F']:.1f}, "
                f"混沌度={chaos_level}(σ={std_dev:.2f})")

# 注册表扩展函数
def register_lorenz96():
    return Lorenz96Experiment()

if __name__ == '__main__':
    # 快速测试
    exp = Lorenz96Experiment()
    params = exp.generate_params()
    print(f"Params: {params}")
    result = exp.run(params)
    print(f"Result: {exp.describe(params, result)}")
    
    img = exp.visualize(result)
    img.save('lorenz96_test.png')
    print("Saved lorenz96_test.png")
    
    # 测试动画
    frames = exp.animate(params)
    if frames:
        frames[0].save('lorenz96_anim.gif', save_all=True, 
                       append_images=frames[1:], duration=80, loop=0)
        print(f"Saved lorenz96_anim.gif ({len(frames)} frames)")
