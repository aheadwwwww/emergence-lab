"""
Boids 群聚模拟
三条规则：
1. Separation（分离）：避免与邻近个体碰撞
2. Alignment（对齐）：与邻近个体方向一致
3. Cohesion（凝聚）：向邻近个体的中心移动

观察：从随机分布逐渐形成协调的群体运动
"""

import numpy as np
from PIL import Image, ImageDraw
import os

# Parameters
NUM_BOIDS = 50
WIDTH, HEIGHT = 400, 400
STEPS = 200
PERCEPTION_RADIUS = 50

# Boid state
positions = np.random.rand(NUM_BOIDS, 2) * [WIDTH, HEIGHT]
velocities = (np.random.rand(NUM_BOIDS, 2) - 0.5) * 4

def separation(i, positions, velocities):
    """Steer away from nearby boids"""
    diff = np.zeros(2)
    count = 0
    for j in range(len(positions)):
        if i != j:
            dist = np.linalg.norm(positions[i] - positions[j])
            if dist < PERCEPTION_RADIUS * 0.5 and dist > 0:
                diff -= (positions[j] - positions[i]) / dist
                count += 1
    return diff * 0.05 if count > 0 else np.zeros(2)

def alignment(i, positions, velocities):
    """Match velocity of nearby boids"""
    avg_vel = np.zeros(2)
    count = 0
    for j in range(len(positions)):
        if i != j:
            dist = np.linalg.norm(positions[i] - positions[j])
            if dist < PERCEPTION_RADIUS:
                avg_vel += velocities[j]
                count += 1
    if count > 0:
        avg_vel /= count
        return (avg_vel - velocities[i]) * 0.1
    return np.zeros(2)

def cohesion(i, positions, velocities):
    """Move toward center of nearby boids"""
    center = np.zeros(2)
    count = 0
    for j in range(len(positions)):
        if i != j:
            dist = np.linalg.norm(positions[i] - positions[j])
            if dist < PERCEPTION_RADIUS:
                center += positions[j]
                count += 1
    if count > 0:
        center /= count
        return (center - positions[i]) * 0.01
    return np.zeros(2)

# Run simulation and save frames
frames = []
for step in range(STEPS):
    # Update each boid
    for i in range(NUM_BOIDS):
        # Calculate three forces
        sep = separation(i, positions, velocities)
        ali = alignment(i, positions, velocities)
        coh = cohesion(i, positions, velocities)
        
        # Apply forces
        velocities[i] += sep + ali + coh
        
        # Limit speed
        speed = np.linalg.norm(velocities[i])
        if speed > 4:
            velocities[i] = velocities[i] / speed * 4
        
        # Update position
        positions[i] += velocities[i]
        
        # Wrap around edges
        positions[i] = positions[i] % [WIDTH, HEIGHT]
    
    # Create frame
    img = Image.new('L', (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(img)
    for pos in positions:
        x, y = int(pos[0]), int(pos[1])
        draw.ellipse([x-2, y-2, x+2, y+2], fill=0)
    frames.append(img)

# Save as GIF
output_path = r'C:\Users\许耀仁\.openclaw\workspace\experiments\boids.gif'
frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=50, loop=0)

print(f'Boids simulation completed: {NUM_BOIDS} boids, {STEPS} steps')
print(f'GIF saved to: {output_path}')
