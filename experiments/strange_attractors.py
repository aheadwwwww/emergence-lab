"""
Strange Attractors - Lorenz, Rössler, Chen
混沌系统的奇怪吸引子可视化

Lorenz系统：
dx/dt = sigma(y - x)
dy/dt = x(rho - z) - y
dz/dt = xy - beta*z

经典参数：sigma=10, rho=28, beta=8/3
"""

import numpy as np
from PIL import Image, ImageDraw
from scipy.integrate import odeint
import os

def lorenz(state, t, sigma, rho, beta):
    x, y, z = state
    return [
        sigma * (y - x),
        x * (rho - z) - y,
        x * y - beta * z
    ]

def rossler(state, t, a, b, c):
    x, y, z = state
    return [
        -y - z,
        x + a * y,
        b + z * (x - c)
    ]

def chen(state, t, a, b, c):
    x, y, z = state
    return [
        a * (y - x),
        (c - a) * x - x * z + c * y,
        x * y - b * z
    ]

def integrate_system(system, params, initial, steps=10000, dt=0.01):
    t = np.arange(0, steps * dt, dt)
    trajectory = odeint(system, initial, t, args=params)
    return trajectory

def plot_attractor_2d(trajectory, title, output_path, projection='xy'):
    """绘制2D投影"""
    if projection == 'xy':
        x, y = trajectory[:, 0], trajectory[:, 1]
    elif projection == 'xz':
        x, y = trajectory[:, 0], trajectory[:, 2]
    else:
        x, y = trajectory[:, 1], trajectory[:, 2]
    
    # 归一化到图像坐标
    SIZE = 800
    margin = 50
    x = (x - x.min()) / (x.max() - x.min()) * (SIZE - 2*margin) + margin
    y = (y - y.min()) / (y.max() - y.min()) * (SIZE - 2*margin) + margin
    
    img = Image.new('RGB', (SIZE, SIZE), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    # 绘制轨迹（渐变色）
    for i in range(len(x) - 1):
        t = i / len(x)
        r = int(50 + 150 * t)
        g = int(100 + 100 * (1 - t))
        b = int(200 - 100 * t)
        draw.line([x[i], y[i], x[i+1], y[i+1]], fill=(r, g, b), width=1)
    
    img.save(output_path)
    print(f'{title} 保存到: {output_path}')

output_dir = 'D:/emergence_experiments'
os.makedirs(output_dir, exist_ok=True)

print('=== Lorenz Attractor ===')
traj_lorenz = integrate_system(lorenz, (10, 28, 8/3), [1, 1, 1], steps=15000)
plot_attractor_2d(traj_lorenz, 'Lorenz (XY)', f'{output_dir}/lorenz_xy.png', 'xy')
plot_attractor_2d(traj_lorenz, 'Lorenz (XZ)', f'{output_dir}/lorenz_xz.png', 'xz')

print('=== Rossler Attractor ===')
traj_rossler = integrate_system(rossler, (0.2, 0.2, 5.7), [1, 1, 1], steps=15000)
plot_attractor_2d(traj_rossler, 'Rossler', f'{output_dir}/rossler.png', 'xy')

print('=== Chen Attractor ===')
traj_chen = integrate_system(chen, (35, 3, 28), [1, 1, 1], steps=15000)
plot_attractor_2d(traj_chen, 'Chen', f'{output_dir}/chen.png', 'xy')

print('完成')