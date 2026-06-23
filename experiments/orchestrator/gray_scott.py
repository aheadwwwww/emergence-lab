"""
Gray-Scott 反应扩散模型
产生斑点、条纹、波纹等丰富图案
"""

import numpy as np
from PIL import Image
import random
import time
from pathlib import Path

OUTPUT_DIR = Path('D:/emergence_experiments')


class GrayScott:
    """Gray-Scott 反应扩散模型 - 产生斑点、条纹、迷宫图案"""
    name = "gray_scott"
    description = "Gray-Scott 反应扩散 - 产生斑点、条纹、迷宫图案"
    supports_animation = True
    
    def generate_params(self):
        # 不同参数组合产生不同图案
        presets = [
            {'feed': 0.037, 'kill': 0.06},   # 斑点
            {'feed': 0.014, 'kill': 0.054},  # 迷宫
            {'feed': 0.025, 'kill': 0.06},   # 波纹
            {'feed': 0.078, 'kill': 0.061},  # 分裂
        ]
        preset = random.choice(presets)
        return {
            'size': random.choice([128, 160]),
            'steps': random.randint(2000, 4000),
            'feed': preset['feed'] + random.uniform(-0.002, 0.002),
            'kill': preset['kill'] + random.uniform(-0.002, 0.002),
            'Du': 0.16,
            'Dv': 0.08
        }
    
    def _laplacian(self, arr):
        """拉普拉斯算子（周期边界）"""
        return (
            np.roll(arr, 1, 0) + np.roll(arr, -1, 0) +
            np.roll(arr, 1, 1) + np.roll(arr, -1, 1) -
            4 * arr
        )
    
    def run(self, params):
        size = params['size']
        steps = params['steps']
        feed = params['feed']
        kill = params['kill']
        Du = params['Du']
        Dv = params['Dv']
        
        # 初始化：U=1，V=0，中心区域有扰动
        U = np.ones((size, size), dtype=np.float64)
        V = np.zeros((size, size), dtype=np.float64)
        
        # 在中心添加扰动
        c = size // 2
        r = size // 8
        U[c-r:c+r, c-r:c+r] = 0.5
        V[c-r:c+r, c-r:c+r] = 0.25
        
        # 添加随机噪声
        V += np.random.rand(size, size) * 0.1
        
        dt = 1.0
        for _ in range(steps):
            Lu = self._laplacian(U)
            Lv = self._laplacian(V)
            
            uvv = U * V * V
            U += (Du * Lu - uvv + feed * (1 - U)) * dt
            V += (Dv * Lv + uvv - (feed + kill) * V) * dt
            
            U = np.clip(U, 0, 1)
            V = np.clip(V, 0, 1)
        
        return {'U': U, 'V': V, 'feed': feed, 'kill': kill}
    
    def _arr_to_img(self, V):
        size = len(V)
        v_norm = ((V - V.min()) / (V.max() - V.min() + 1e-8) * 255).astype(np.uint8)
        img = Image.new('RGB', (size * 2, size * 2), (10, 10, 20))
        pixels = img.load()
        
        for i in range(size):
            for j in range(size):
                v = v_norm[i, j]
                # 蓝色到青色到白色渐变
                r_col = int(v * 0.6)
                g_col = int(v * 0.8 + 50)
                b_col = int(v * 0.9 + 30)
                for di in range(2):
                    for dj in range(2):
                        pixels[j * 2 + dj, i * 2 + di] = (r_col, g_col, b_col)
        return img
    
    def animate(self, params):
        """生成动画帧"""
        size = params['size']
        steps = params['steps']
        feed = params['feed']
        kill = params['kill']
        Du = params['Du']
        Dv = params['Dv']
        
        U = np.ones((size, size), dtype=np.float64)
        V = np.zeros((size, size), dtype=np.float64)
        c = size // 2
        r = size // 8
        U[c-r:c+r, c-r:c+r] = 0.5
        V[c-r:c+r, c-r:c+r] = 0.25
        V += np.random.rand(size, size) * 0.1
        
        dt = 1.0
        frame_interval = max(1, steps // 20)
        frames = []
        
        for step in range(steps):
            Lu = self._laplacian(U)
            Lv = self._laplacian(V)
            uvv = U * V * V
            U += (Du * Lu - uvv + feed * (1 - U)) * dt
            V += (Dv * Lv + uvv - (feed + kill) * V) * dt
            U = np.clip(U, 0, 1)
            V = np.clip(V, 0, 1)
            
            if step % frame_interval == 0 or step == steps - 1:
                frames.append(self._arr_to_img(V))
        
        return frames
    
    def visualize(self, result):
        return self._arr_to_img(result['V'])
    
    def describe(self, params, result):
        f, k = params['feed'], params['kill']
        return f"Gray-Scott: feed={f:.3f}, kill={k:.3f}"
    
    def save_image(self, img):
        timestamp = int(time.time())
        path = OUTPUT_DIR / f'{self.name}_{timestamp}.png'
        img.save(path)
        return str(path)
    
    def save_gif(self, frames, name_prefix="", duration=100):
        """保存帧序列为 GIF"""
        if not frames:
            return ""
        timestamp = int(time.time())
        prefix = name_prefix or self.name
        path = OUTPUT_DIR / f'{prefix}_{timestamp}.gif'
        frames[0].save(path, save_all=True, append_images=frames[1:],
                       duration=duration, loop=0, optimize=False)
        return str(path)


if __name__ == '__main__':
    exp = GrayScott()
    params = exp.generate_params()
    print('Params:', params)
    result = exp.run(params)
    print('Done:', exp.describe(params, result))
    img = exp.visualize(result)
    path = exp.save_image(img)
    print('Saved:', path)