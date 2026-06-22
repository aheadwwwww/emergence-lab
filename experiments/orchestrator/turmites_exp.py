"""
Turmites - 二维图灵机
在网格上移动，根据状态改变颜色和方向
"""

import numpy as np
from PIL import Image, ImageDraw
import random
import time
from pathlib import Path

OUTPUT_DIR = Path('D:/emergence_experiments')

class TurmitesExperiment:
    name = "turmites"
    description = "Turmites - 二维图灵机，简单规则产生复杂轨迹"
    
    def generate_params(self):
        return {
            'size': random.choice([150, 200]),
            'steps': random.randint(8000, 15000),
            'n_states': random.choice([2, 3, 4]),
            'n_colors': random.choice([2, 3])
        }
    
    def run(self, params):
        size = params['size']
        steps = params['steps']
        n_states = params['n_states']
        n_colors = params['n_colors']
        
        # 随机生成状态转移表
        # transition[state][color] = (new_color, turn, new_state)
        # turn: 0=左, 1=右, 2=直行
        transition = {}
        for s in range(n_states):
            transition[s] = {}
            for c in range(n_colors):
                transition[s][c] = (
                    random.randint(0, n_colors - 1),
                    random.choice([0, 1, 2]),
                    random.randint(0, n_states - 1)
                )
        
        grid = np.zeros((size, size), dtype=np.int8)
        x, y = size // 2, size // 2
        direction = 0
        dx, dy = [0, 1, 0, -1], [-1, 0, 1, 0]
        state = 0
        
        for _ in range(steps):
            current_color = grid[y, x]
            new_color, turn, new_state = transition[state][current_color]
            
            grid[y, x] = new_color
            
            # 转向
            if turn == 0:
                direction = (direction - 1) % 4
            elif turn == 1:
                direction = (direction + 1) % 4
            # turn == 2 直行
            
            state = new_state
            x = (x + dx[direction]) % size
            y = (y + dy[direction]) % size
        
        return {'grid': grid, 'steps': steps, 'n_states': n_states, 'n_colors': n_colors}
    
    def visualize(self, result):
        grid = result['grid']
        size = len(grid)
        n_colors = result['n_colors']
        
        # 颜色调色板
        colors = [
            (20, 20, 40),
            (100, 180, 255),
            (255, 150, 100),
            (150, 255, 150)
        ]
        
        img = Image.new('RGB', (size * 2, size * 2), (10, 10, 20))
        pixels = img.load()
        
        for i in range(size):
            for j in range(size):
                c = colors[min(grid[i, j], len(colors) - 1)]
                for di in range(2):
                    for dj in range(2):
                        pixels[j * 2 + dj, i * 2 + di] = c
        
        return img
    
    def describe(self, params, result):
        return f"Turmites: {result['n_states']} states, {result['n_colors']} colors, {result['steps']} steps"
    
    def save_image(self, img):
        timestamp = int(time.time())
        path = OUTPUT_DIR / f'{self.name}_{timestamp}.png'
        img.save(path)
        return str(path)

if __name__ == '__main__':
    exp = TurmitesExperiment()
    params = exp.generate_params()
    print(f'Params: {params}')
    
    result = exp.run(params)
    print(f'Done: {exp.describe(params, result)}')
    
    img = exp.visualize(result)
    path = exp.save_image(img)
    print(f'Saved: {path}')
