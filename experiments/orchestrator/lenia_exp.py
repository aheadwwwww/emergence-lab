"""
Lenia - 连续细胞自动机
康威生命游戏的"平滑"版本
"""

import numpy as np
from PIL import Image
import random
import time
from pathlib import Path

OUTPUT_DIR = Path('D:/emergence_experiments')

class LeniaExperiment:
    name = "lenia"
    description = "Lenia - 连续细胞自动机，生命游戏的平滑版本"

    def generate_params(self):
        return {
            'size': random.choice([100, 128]),
            'steps': random.randint(100, 200),
            'R': random.randint(10, 13),
            'r': random.uniform(0.35, 0.45),
            'm': random.uniform(0.12, 0.14),
            's': random.uniform(0.012, 0.02)
        }

    def _make_kernel(self, R, r):
        """生成环形核函数"""
        size = 2 * R + 1
        kernel = np.zeros((size, size))
        center = R
        for i in range(size):
            for j in range(size):
                d = np.sqrt((i - center)**2 + (j - center)**2)
                if d <= R:
                    kernel[i, j] = np.exp(-((d/R - r)**2) / 0.05)
        kernel /= kernel.sum() + 1e-8
        return kernel

    def _growth(self, u, m, s):
        """Growth 函数"""
        return np.clip(1 - (u - m)**2 / (2 * s**2), 0, 1) * 2 - 1

    def run(self, params):
        size = params['size']
        steps = params['steps']
        R = params['R']
        r = params['r']
        m = params['m']
        s = params['s']

        kernel = self._make_kernel(R, r)
        state = np.random.rand(size, size)

        # 简单卷积（不用 scipy）
        for _ in range(steps):
            # 手动卷积
            padded = np.pad(state, R, mode='wrap')
            u = np.zeros_like(state)
            k_size = 2 * R + 1
            for i in range(size):
                for j in range(size):
                    u[i, j] = np.sum(padded[i:i+k_size, j:j+k_size] * kernel)
            g = self._growth(u, m, s)
            state = np.clip(state + g * 0.1, 0, 1)

        return {'state': state, 'R': R, 'r': r, 'm': m, 's': s, 'steps': steps}

    def visualize(self, result):
        state = result['state']
        size = len(state)
        img = Image.new('RGB', (size * 2, size * 2), (10, 10, 20))
        pixels = img.load()
        for i in range(size):
            for j in range(size):
                v = state[i, j]
                r_col = int(v * 255)
                g_col = int(v * 180)
                b_col = int((1 - v) * 255)
                for di in range(2):
                    for dj in range(2):
                        pixels[j * 2 + dj, i * 2 + di] = (r_col, g_col, b_col)
        return img

    def describe(self, params, result):
        return f"Lenia: R={result['R']}, r={result['r']:.2f}, m={result['m']:.3f}, {result['steps']} steps"

    def save_image(self, img):
        timestamp = int(time.time())
        path = OUTPUT_DIR / f'{self.name}_{timestamp}.png'
        img.save(path)
        return str(path)

if __name__ == '__main__':
    exp = LeniaExperiment()
    params = exp.generate_params()
    print('Params:', params)
    result = exp.run(params)
    print('Done:', exp.describe(params, result))
    img = exp.visualize(result)
    path = exp.save_image(img)
    print('Saved:', path)