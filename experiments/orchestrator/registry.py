"""
实验注册表 - 编排器的实验库
所有实验遵循统一接口，存储到 D:/emergence_experiments/
"""

import numpy as np
from PIL import Image, ImageDraw
from pathlib import Path
import random
import time
from abc import ABC, abstractmethod

OUTPUT_DIR = Path('D:/emergence_experiments')

class BaseExperiment(ABC):
    """实验基类"""
    name = ""
    description = ""
    
    @abstractmethod
    def generate_params(self) -> dict:
        pass
    
    @abstractmethod
    def run(self, params: dict) -> dict:
        pass
    
    @abstractmethod
    def visualize(self, result: dict) -> Image.Image:
        pass
    
    @abstractmethod
    def describe(self, params: dict, result: dict) -> str:
        pass
    
    def save_image(self, img: Image.Image) -> str:
        timestamp = int(time.time())
        path = OUTPUT_DIR / f'{self.name}_{timestamp}.png'
        img.save(path)
        return str(path)

# ===== 实验实现 =====

class LangtonsAnt(BaseExperiment):
    name = "langtons_ant"
    description = "朗顿蚂蚁 - 简单规则产生复杂模式"
    
    def generate_params(self):
        return {'size': random.choice([100, 150, 200]), 'steps': random.randint(5000, 20000)}
    
    def run(self, params):
        size, steps = params['size'], params['steps']
        grid = np.zeros((size, size), dtype=np.int8)
        x, y = size // 2, size // 2
        d = 0
        dx, dy = [0, 1, 0, -1], [-1, 0, 1, 0]
        for _ in range(steps):
            if grid[y, x] == 0:
                d = (d + 1) % 4; grid[y, x] = 1
            else:
                d = (d - 1) % 4; grid[y, x] = 0
            x = (x + dx[d]) % size; y = (y + dy[d]) % size
        return {'grid': grid, 'steps': steps}
    
    def visualize(self, result):
        g = result['grid']; s = len(g)
        img = Image.new('RGB', (s*3, s*3), (20,20,30)); p = img.load()
        for i in range(s):
            for j in range(s):
                c = (255,255,255) if g[i,j] else (20,20,30)
                for di in range(3):
                    for dj in range(3): p[j*3+dj, i*3+di] = c
        return img
    
    def describe(self, params, result):
        return f"Langton's Ant on {params['size']}x{params['size']}, {result['steps']} steps"

class GameOfLife(BaseExperiment):
    name = "game_of_life"
    description = "康威生命游戏 - 自组织模式"
    
    def generate_params(self):
        return {'size': 150, 'steps': 200, 'density': random.uniform(0.2, 0.4)}
    
    def run(self, params):
        g = (np.random.random((params['size'], params['size'])) < params['density']).astype(np.int8)
        for _ in range(params['steps']):
            n = sum(np.roll(np.roll(g, i, 0), j, 1) for i in (-1,0,1) for j in (-1,0,1) if (i,j)!=(0,0))
            g = ((g==1)&((n==2)|(n==3)))|((g==0)&(n==3)); g = g.astype(np.int8)
        return {'grid': g, 'survivors': int(g.sum())}
    
    def visualize(self, result):
        g = result['grid']; s = len(g)
        img = Image.new('RGB', (s*2, s*2), (10,10,20)); p = img.load()
        for i in range(s):
            for j in range(s):
                c = (60, 200, 100) if g[i,j] else (10,10,20)
                for di in range(2):
                    for dj in range(2): p[j*2+dj, i*2+di] = c
        return img
    
    def describe(self, params, result):
        return f"Conway's Game of Life: {result['survivors']} cells survived"

class Sandpile(BaseExperiment):
    name = "sandpile"
    description = "沙堆模型 - 自组织临界性"
    
    def generate_params(self):
        return {'size': random.choice([50, 75]), 'drops': random.randint(5000, 15000)}
    
    def run(self, params):
        size, drops = params['size'], params['drops']
        g = np.zeros((size, size), dtype=np.int16)
        for _ in range(drops):
            g[size//2, size//2] += 1
            x, y = size//2, size//2
            while g[x, y] >= 4:
                g[x, y] -= 4
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < size and 0 <= ny < size:
                        g[nx, ny] += 1
                        if g[nx, ny] >= 4: x, y = nx, ny
        return {'grid': g, 'drops': drops}
    
    def visualize(self, result):
        g = result['grid']; s = len(g)
        colors = [(20,20,40), (50,80,150), (150,200,255), (255,100,100)]
        img = Image.new('RGB', (s*4, s*4), (10,10,20)); p = img.load()
        for i in range(s):
            for j in range(s):
                c = colors[min(g[i,j], 3)]
                for di in range(4):
                    for dj in range(4): p[j*4+dj, i*4+di] = c
        return img
    
    def describe(self, params, result):
        return f"Sandpile: {params['drops']} grains, SOC reached"

class BoidsExperiment(BaseExperiment):
    name = "boids"
    description = "Boids 群集行为 - 涌现群体智能"
    
    def generate_params(self):
        return {'n': random.choice([100, 200, 300]), 'steps': 100}
    
    def run(self, params):
        n, steps = params['n'], params['steps']
        np.random.seed(int(time.time()*1000) % 2**32)
        
        # 位置和速度
        pos = np.random.rand(n, 2) * 500
        vel = (np.random.rand(n, 2) - 0.5) * 4
        
        for _ in range(steps):
            # 分离、对齐、聚集规则
            for i in range(n):
                # 分离
                sep = np.zeros(2)
                for j in range(n):
                    if i != j:
                        d = pos[i] - pos[j]
                        dist = np.linalg.norm(d)
                        if dist < 30 and dist > 0:
                            sep += d / dist
                
                # 对齐
                aligned = np.mean(vel[np.linalg.norm(pos - pos[i], axis=1) < 80], axis=0)
                
                # 聚集
                center = np.mean(pos[np.linalg.norm(pos - pos[i], axis=1) < 80], axis=0)
                cohesion = (center - pos[i]) / 100
                
                vel[i] += sep * 2 + (aligned - vel[i]) * 0.1 + cohesion * 0.05
                
                # 边界反弹
                for k in range(2):
                    if pos[i, k] < 0: vel[i, k] += 1
                    if pos[i, k] > 500: vel[i, k] -= 1
                
                # 限速
                speed = np.linalg.norm(vel[i])
                if speed > 5: vel[i] = vel[i] / speed * 5
            
            pos += vel
        
        return {'positions': pos, 'velocities': vel}
    
    def visualize(self, result):
        pos = result['positions']
        img = Image.new('RGB', (500, 500), (5, 5, 15))
        draw = ImageDraw.Draw(img)
        
        # 画鸟
        for p in pos:
            x, y = int(p[0]), int(p[1])
            draw.ellipse([x-3, y-3, x+3, y+3], fill=(100, 180, 255))
        
        # 画质心
        cx, cy = np.mean(pos, axis=0)
        draw.ellipse([int(cx)-5, int(cy)-5, int(cx)+5, int(cy)+5], fill=(255, 100, 50))
        
        return img
    
    def describe(self, params, result):
        return f"Boids: {params['n']} agents, heading = {np.mean(result['positions'], axis=0)[:2].round(1)}"

class TuringPatterns(BaseExperiment):
    name = "turing_patterns"
    description = "图灵斑图 - 反应扩散系统"
    
    def generate_params(self):
        return {
            'size': 200, 'steps': 2000,
            'Du': random.uniform(0.1, 0.2),
            'Dv': random.uniform(0.05, 0.1),
            'F': random.uniform(0.03, 0.06),
            'k': random.uniform(0.06, 0.08)
        }
    
    def run(self, params):
        s, steps = params['size'], params['steps']
        Du, Dv, F, k = params['Du'], params['Dv'], params['F'], params['k']
        
        u = np.ones((s, s), dtype=np.float32)
        v = np.zeros((s, s), dtype=np.float32)
        
        # 随机种子
        r = np.random.randint(0, s, 100)
        c = np.random.randint(0, s, 100)
        u[r, c] = 0.5
        v[r, c] = 0.25
        
        def laplacian(arr):
            return (np.roll(arr, 1, 0) + np.roll(arr, -1, 0) +
                    np.roll(arr, 1, 1) + np.roll(arr, -1, 1) - 4*arr)
        
        dt = 1.0
        for _ in range(steps):
            dudt = Du * laplacian(u) - u * v * v + F * (1 - u)
            dvdt = Dv * laplacian(v) + u * v * v - (F + k) * v
            u += dudt * dt
            v += dvdt * dt
        
        return {'u': u, 'v': v}
    
    def visualize(self, result):
        u = result['u']; s = len(u)
        u_norm = ((u - u.min()) / (u.max() - u.min() + 1e-8) * 255).astype(np.uint8)
        img = Image.fromarray(u_norm, 'L').resize((s*2, s*2), Image.NEAREST)
        return img.convert('RGB')
    
    def describe(self, params, result):
        return f"Turing Patterns: F={params['F']:.3f}, k={params['k']:.3f}"

class WolframCA(BaseExperiment):
    name = "wolfram_ca"
    description = "沃尔夫拉姆元胞自动机 - 四类行为"
    
    def generate_params(self):
        return {'width': 300, 'height': 200, 'rule': random.choice([30, 90, 110, 184, 150])}
    
    def run(self, params):
        w, h, rule = params['width'], params['height'], params['rule']
        
        # 解析规则
        rule_bin = format(rule, '08b')
        rules = {7-i: int(rule_bin[i]) for i in range(8)}
        
        grid = np.zeros((h, w), dtype=np.int8)
        grid[0, w//2] = 1
        
        for i in range(1, h):
            for j in range(1, w-1):
                pattern = grid[i-1, j-1]*4 + grid[i-1, j]*2 + grid[i-1, j+1]
                grid[i, j] = rules[pattern]
        
        return {'grid': grid, 'rule': rule}
    
    def visualize(self, result):
        g = result['grid']; h, w = g.shape
        img = Image.new('RGB', (w*2, h*2), (10,10,10)); p = img.load()
        for i in range(h):
            for j in range(w):
                c = (220, 220, 255) if g[i,j] else (10,10,10)
                for di in range(2):
                    for dj in range(2): p[j*2+dj, i*2+di] = c
        return img
    
    def describe(self, params, result):
        classes = {30:'Class 3', 90:'Class 2', 110:'Class 4', 184:'Class 2', 150:'Class 2'}
        return f"Wolfram Rule {result['rule']} ({classes.get(result['rule'], '')})"

class StrangeAttractors(BaseExperiment):
    name = "strange_attractors"
    description = "奇怪吸引子 - 确定性混沌"
    
    def generate_params(self):
        return {'system': random.choice(['lorenz', 'rossler', 'chen']), 'steps': 10000}
    
    def run(self, params):
        steps = params['steps']
        dt = 0.01
        
        # 初始条件微小随机偏移
        x, y, z = 1.0 + random.uniform(-0.1, 0.1), 1.0, 1.0
        
        if params['system'] == 'lorenz':
            s, r, b = 10, 28, 8/3
            def f(x,y,z): return (s*(y-x), x*(r-z)-y, x*y-b*z)
        elif params['system'] == 'rossler':
            a, b0, c = 0.2, 0.2, 5.7
            def f(x,y,z): return (-y-z, x+a*y, b0+z*(x-c))
        else:  # chen
            a, b0, c = 35, 3, 28
            def f(x,y,z): return (a*(y-x), (c-a)*x - x*z + c*y, x*y - b0*z)
        
        pts = np.zeros((steps, 3))
        for i in range(steps):
            k1 = f(x, y, z)
            k2 = f(x+dt*k1[0]/2, y+dt*k1[1]/2, z+dt*k1[2]/2)
            k3 = f(x+dt*k2[0]/2, y+dt*k2[1]/2, z+dt*k2[2]/2)
            k4 = f(x+dt*k3[0], y+dt*k3[1], z+dt*k3[2])
            x += dt*(k1[0]+2*k2[0]+2*k3[0]+k4[0])/6
            y += dt*(k1[1]+2*k2[1]+2*k3[1]+k4[1])/6
            z += dt*(k1[2]+2*k2[2]+2*k3[2]+k4[2])/6
            pts[i] = [x, y, z]
        
        return {'points': pts, 'system': params['system']}
    
    def visualize(self, result):
        pts = result['points']
        # 归一化
        for k in range(3):
            pts[:,k] = (pts[:,k] - pts[:,k].min()) / (pts[:,k].max() - pts[:,k].min() + 1e-8)
        
        img = Image.new('RGB', (600, 600), (5, 5, 15))
        p = img.load()
        
        scale = 580
        for i in range(1, len(pts)):
            x1, y1 = int(pts[i-1, 0]*scale + 10), int(pts[i-1, 1]*scale + 10)
            x2, y2 = int(pts[i, 0]*scale + 10), int(pts[i, 1]*scale + 10)
            brightness = int(i / len(pts) * 200 + 55)
            try:
                for t in np.linspace(0, 1, 5):
                    x, y = int(x1 + (x2-x1)*t), int(y1 + (y2-y1)*t)
                    if 0 <= x < 600 and 0 <= y < 600:
                        p[x, y] = (brightness//2, brightness, brightness//3)
            except:
                pass
        
        return img
    
    def describe(self, params, result):
        return f"{result['system'].title()} Attractor: deterministic chaos"

# ===== 注册表 =====

REGISTRY = {
    'langtons_ant': LangtonsAnt(),
    'game_of_life': GameOfLife(),
    'sandpile': Sandpile(),
    'boids': BoidsExperiment(),
    'turing_patterns': TuringPatterns(),
    'wolfram_ca': WolframCA(),
    'strange_attractors': StrangeAttractors(),
}

def get_experiment(name):
    return REGISTRY.get(name)

def list_experiments():
    return list(REGISTRY.keys())
