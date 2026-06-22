"""
Boids 群聚模拟 - 增强版
加入障碍物和捕食者，观察群体动态变化

三条基本规则 + 两条增强：
1. Separation（分离）：避免碰撞
2. Alignment（对齐）：方向一致
3. Cohesion（凝聚）：向中心移动
4. Obstacle Avoidance（避障）：远离障碍物
5. Predator Flee（逃跑）：远离捕食者
"""

import numpy as np
from PIL import Image, ImageDraw
import os

# Parameters
NUM_BOIDS = 80
NUM_PREDATORS = 2
WIDTH, HEIGHT = 500, 500
STEPS = 300
PERCEPTION_RADIUS = 40
PREDATOR_RADIUS = 80
OBSTACLE_RADIUS = 30

# Obstacles (x, y, radius)
OBSTACLES = [(150, 150, 25), (350, 350, 25), (250, 250, 35)]

# Boid state
positions = np.random.rand(NUM_BOIDS, 2) * [WIDTH, HEIGHT]
velocities = (np.random.rand(NUM_BOIDS, 2) - 0.5) * 4

# Predator state
pred_positions = np.array([[100.0, 400.0], [400.0, 100.0]])
pred_velocities = np.array([[1.0, -1.0], [-1.0, 1.0]])

def get_neighbors(pos, all_pos, radius):
    dists = np.linalg.norm(all_pos - pos, axis=1)
    mask = (dists < radius) & (dists > 0)
    return mask, all_pos[mask], dists[mask]

def separation_force(pos, neighbors, dists):
    if len(neighbors) == 0:
        return np.zeros(2)
    diff = pos - neighbors
    dists_safe = np.maximum(dists, 1.0)
    weighted = diff / dists_safe[:, np.newaxis]
    return np.mean(weighted, axis=0) * 2.0

def alignment_force(vel, neighbors_vel):
    if len(neighbors_vel) == 0:
        return np.zeros(2)
    avg_vel = np.mean(neighbors_vel, axis=0)
    return (avg_vel - vel) * 0.1

def cohesion_force(pos, neighbors):
    if len(neighbors) == 0:
        return np.zeros(2)
    center = np.mean(neighbors, axis=0)
    return (center - pos) * 0.008

def obstacle_force(pos):
    force = np.zeros(2)
    for ox, oy, r in OBSTACLES:
        obs = np.array([ox, oy])
        diff = pos - obs
        dist = np.linalg.norm(diff)
        if dist < OBSTACLE_RADIUS + r and dist > 0:
            force += diff / (dist * dist) * 50
    return force

def predator_force(pos):
    force = np.zeros(2)
    for pp in pred_positions:
        diff = pos - pp
        dist = np.linalg.norm(diff)
        if dist < PREDATOR_RADIUS and dist > 0:
            force += diff / (dist * dist) * 80
    return force

def predator_chase(pos, all_boids):
    # Find nearest boid
    dists = np.linalg.norm(all_boids - pos, axis=1)
    nearest = np.argmin(dists)
    direction = all_boids[nearest] - pos
    dist = np.linalg.norm(direction)
    if dist > 0:
        return direction / dist * 0.3
    return np.zeros(2)

# Run simulation
frames = []
for step in range(STEPS):
    new_velocities = velocities.copy()
    
    for i in range(NUM_BOIDS):
        mask, neighbors, dists = get_neighbors(positions[i], positions, PERCEPTION_RADIUS)
        neighbor_vels = velocities[mask]
        
        sep = separation_force(positions[i], neighbors, dists)
        ali = alignment_force(velocities[i], neighbor_vels)
        coh = cohesion_force(positions[i], neighbors)
        obs = obstacle_force(positions[i])
        pre = predator_force(positions[i])
        
        new_velocities[i] += sep + ali + coh + obs + pre
        
        # Limit speed
        speed = np.linalg.norm(new_velocities[i])
        if speed > 5:
            new_velocities[i] = new_velocities[i] / speed * 5
        if speed < 1:
            new_velocities[i] = new_velocities[i] / max(speed, 0.1) * 1
    
    velocities = new_velocities
    positions = (positions + velocities) % [WIDTH, HEIGHT]
    
    # Update predators
    for j in range(NUM_PREDATORS):
        chase = predator_chase(pred_positions[j], positions)
        pred_velocities[j] += chase
        speed = np.linalg.norm(pred_velocities[j])
        if speed > 3.5:
            pred_velocities[j] = pred_velocities[j] / speed * 3.5
        pred_positions[j] = (pred_positions[j] + pred_velocities[j]) % [WIDTH, HEIGHT]
    
    # Create frame
    img = Image.new('RGB', (WIDTH, HEIGHT), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw obstacles
    for ox, oy, r in OBSTACLES:
        draw.ellipse([ox-r, oy-r, ox+r, oy+r], fill=(180, 180, 180), outline=(100, 100, 100))
    
    # Draw boids
    for pos in positions:
        x, y = int(pos[0]), int(pos[1])
        draw.ellipse([x-2, y-2, x+2, y+2], fill=(30, 120, 220))
    
    # Draw predators
    for pp in pred_positions:
        x, y = int(pp[0]), int(pp[1])
        draw.ellipse([x-4, y-4, x+4, y+4], fill=(220, 50, 50))
    
    frames.append(img)

# Save as GIF
output_path = r'C:\Users\许耀仁\.openclaw\workspace\experiments\boids_predators.gif'
frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=50, loop=0)
print(f'Enhanced Boids completed: {NUM_BOIDS} boids, {NUM_PREDATORS} predators, {STEPS} steps')
print(f'GIF saved to: {output_path}')
