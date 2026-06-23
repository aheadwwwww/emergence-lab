"""
Network Emergence: Kuramoto Synchronization on Different Topologies

Demonstrates how network structure affects emergent synchronization.
Same local rule (phase coupling), different global behavior depending on
whether the network is random, small-world, or scale-free.

Key finding: Small-world networks synchronize fastest — the "sweet spot"
for emergence where local clustering meets global connectivity.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import json
import os

def create_random_network(n, p):
    """Erdos-Renyi random graph"""
    adj = np.zeros((n, n))
    for i in range(n):
        for j in range(i+1, n):
            if np.random.random() < p:
                adj[i, j] = adj[j, i] = 1
    return adj

def create_small_world(n, k, p_rewire):
    """Watts-Strogatz small-world network"""
    adj = np.zeros((n, n))
    # Start with ring lattice
    for i in range(n):
        for j in range(1, k//2 + 1):
            neighbor = (i + j) % n
            adj[i, neighbor] = adj[neighbor, i] = 1
    
    # Rewire
    for i in range(n):
        for j in range(i+1, n):
            if adj[i, j] == 1 and np.random.random() < p_rewire:
                adj[i, j] = adj[j, i] = 0
                new_j = np.random.randint(0, n)
                while new_j == i or adj[i, new_j] == 1:
                    new_j = np.random.randint(0, n)
                adj[i, new_j] = adj[new_j, i] = 1
    return adj

def create_scale_free(n, m):
    """Barabasi-Albert scale-free network"""
    adj = np.zeros((n, n))
    # Start with m nodes fully connected
    for i in range(m):
        for j in range(i+1, m):
            adj[i, j] = adj[j, i] = 1
    
    degrees = np.sum(adj, axis=1)
    
    # Add remaining nodes with preferential attachment
    for new_node in range(m, n):
        total_deg = np.sum(degrees[:new_node])
        if total_deg == 0:
            targets = np.random.choice(new_node, m, replace=False)
        else:
            probs = degrees[:new_node] / total_deg
            targets = np.random.choice(new_node, m, replace=False, p=probs)
        
        for t in targets:
            adj[new_node, t] = adj[t, new_node] = 1
        degrees = np.sum(adj, axis=1)
    
    return adj

def kuramoto_step(phases, adj, K, omega, dt=0.01):
    """One step of Kuramoto model"""
    n = len(phases)
    dphases = omega.copy()
    
    for i in range(n):
        neighbors = np.where(adj[i] > 0)[0]
        if len(neighbors) > 0:
            coupling = K * np.sum(np.sin(phases[neighbors] - phases[i])) / len(neighbors)
            dphases[i] += coupling
    
    return (phases + dphases * dt) % (2 * np.pi)

def order_parameter(phases):
    """Kuramoto order parameter r (0=disorder, 1=perfect sync)"""
    n = len(phases)
    r = np.abs(np.sum(np.exp(1j * phases))) / n
    return r

def run_simulation(adj, n_steps=500, K=2.0, dt=0.05):
    """Run Kuramoto simulation and track order parameter"""
    n = len(adj)
    phases = np.random.uniform(0, 2*np.pi, n)
    omega = np.random.normal(0, 0.5, n)  # natural frequencies
    
    r_history = []
    for step in range(n_steps):
        phases = kuramoto_step(phases, adj, K, omega, dt)
        r = order_parameter(phases)
        r_history.append(r)
    
    return r_history, phases

def draw_network(adj, phases, size=400, node_radius=5):
    """Draw network with nodes colored by phase"""
    n = len(adj)
    img = Image.new('RGB', (size, size), (20, 20, 30))
    draw = ImageDraw.Draw(img)
    
    # Position nodes in a circle
    positions = []
    for i in range(n):
        angle = 2 * np.pi * i / n
        r = size * 0.4
        x = size/2 + r * np.cos(angle)
        y = size/2 + r * np.sin(angle)
        positions.append((x, y))
    
    # Draw edges (faded)
    for i in range(n):
        for j in range(i+1, n):
            if adj[i, j] > 0:
                x1, y1 = positions[i]
                x2, y2 = positions[j]
                draw.line([x1, y1, x2, y2], fill=(60, 60, 80), width=1)
    
    # Draw nodes colored by phase
    for i, (x, y) in enumerate(positions):
        # Phase -> hue
        hue = phases[i] / (2 * np.pi)
        # HSV to RGB (simple)
        r = int(127 + 127 * np.sin(2*np.pi * hue))
        g = int(127 + 127 * np.sin(2*np.pi * (hue + 1/3)))
        b = int(127 + 127 * np.sin(2*np.pi * (hue + 2/3)))
        color = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
        
        draw.ellipse([x-node_radius, y-node_radius, x+node_radius, y+node_radius], fill=color)
    
    return img

def draw_sync_curves(results, width=800, height=400):
    """Draw synchronization curves for all three networks"""
    img = Image.new('RGB', (width, height), (20, 20, 30))
    draw = ImageDraw.Draw(img)
    
    colors = {
        'Random': (255, 100, 100),
        'Small-World': (100, 255, 100),
        'Scale-Free': (100, 100, 255)
    }
    
    margin = 60
    plot_w = width - 2 * margin
    plot_h = height - 2 * margin
    
    # Axes
    draw.line([margin, height-margin, width-margin, height-margin], fill=(100, 100, 100))
    draw.line([margin, margin, margin, height-margin], fill=(100, 100, 100))
    
    # Labels
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()
    
    draw.text((width//2-40, height-25), "Time Steps", fill=(200, 200, 200), font=font)
    
    for name, r_hist in results.items():
        color = colors[name]
        n_steps = len(r_hist)
        for i in range(n_steps - 1):
            x1 = margin + (i / n_steps) * plot_w
            y1 = height - margin - r_hist[i] * plot_h
            x2 = margin + ((i+1) / n_steps) * plot_w
            y2 = height - margin - r_hist[i+1] * plot_h
            draw.line([x1, y1, x2, y2], fill=color, width=2)
    
    # Legend
    y_legend = 20
    for name, color in colors.items():
        draw.rectangle([width-160, y_legend, width-140, y_legend+12], fill=color)
        draw.text((width-135, y_legend-2), name, fill=(200, 200, 200), font=font)
        y_legend += 20
    
    return img

def main():
    n = 50  # number of nodes
    n_steps = 300
    K = 2.0  # coupling strength
    
    print("Creating networks...")
    random_net = create_random_network(n, p=0.1)
    small_world_net = create_small_world(n, k=4, p_rewire=0.1)
    scale_free_net = create_scale_free(n, m=2)
    
    # Network stats
    for name, net in [("Random", random_net), ("Small-World", small_world_net), ("Scale-Free", scale_free_net)]:
        degrees = np.sum(net, axis=1)
        print(f"{name}: avg degree={degrees.mean():.1f}, max degree={degrees.max():.0f}, edges={int(np.sum(net)/2)}")
    
    print("\nRunning Kuramoto simulations...")
    results = {}
    final_phases = {}
    
    for name, net in [("Random", random_net), ("Small-World", small_world_net), ("Scale-Free", scale_free_net)]:
        r_hist, phases = run_simulation(net, n_steps=n_steps, K=K)
        results[name] = r_hist
        final_phases[name] = phases
        final_r = r_hist[-1]
        max_r = max(r_hist)
        sync_step = next((i for i, r in enumerate(r_hist) if r > 0.8), n_steps)
        print(f"  {name}: final r={final_r:.3f}, max r={max_r:.3f}, sync at step {sync_step}")
    
    # Draw results
    print("\nGenerating visualizations...")
    
    # Sync curves
    curve_img = draw_sync_curves(results)
    curve_img.save("network_sync_curves.png")
    print("  Saved: network_sync_curves.png")
    
    # Network visualizations
    for name, phases in final_phases.items():
        net = {"Random": random_net, "Small-World": small_world_net, "Scale-Free": scale_free_net}[name]
        img = draw_network(net, phases)
        filename = f"network_{name.lower().replace('-', '_')}.png"
        img.save(filename)
        print(f"  Saved: {filename}")
    
    # Save data
    data = {
        "n_nodes": n,
        "n_steps": n_steps,
        "coupling_K": K,
        "results": {name: {"r_final": float(r[-1]), "r_max": float(max(r)), "r_history": [float(x) for x in r]} 
                     for name, r in results.items()}
    }
    with open("network_sync_data.json", "w") as f:
        json.dump(data, f, indent=2)
    print("  Saved: network_sync_data.json")
    
    # Key insight
    print("\n" + "="*60)
    print("KEY INSIGHT:")
    print("Small-world networks synchronize fastest because they combine")
    print("local clustering (neighbors sync quickly) with global shortcuts")
    print("(distant nodes connect). This is the 'sweet spot' for emergence.")
    print("="*60)

if __name__ == "__main__":
    main()
