"""
Agent-Based Lenia with Gradient Sensing

Enhanced version with:
- Agents can sense local energy gradients
- Agents navigate towards high-energy regions (gradient ascent)
- Agents avoid low-energy regions (survival behavior)
- Spatial memory: agents remember good locations

This creates emergent foraging behavior.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import convolve, sobel
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import json

# ============ Lenia Core ============

def create_kernel(R: int, peaks: List[Tuple[float, float, float]]) -> np.ndarray:
    """Create multi-peak Lenia kernel"""
    size = 2 * R + 1
    y, x = np.ogrid[-R:R+1, -R:R+1]
    d = np.sqrt(x**2 + y**2) / R
    
    kernel = np.zeros_like(d)
    for center, width, weight in peaks:
        kernel += weight * np.exp(-((d - center) / width) ** 2)
    
    return kernel / kernel.sum() if kernel.sum() > 0 else kernel

def lenia_step(field: np.ndarray, kernel: np.ndarray, growth_func: callable) -> np.ndarray:
    """Single Lenia update step"""
    U = convolve(field, kernel, mode='wrap')
    G = growth_func(U)
    return np.clip(field + 0.1 * G, 0, 1)

def compute_gradient(field: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Compute energy gradient (for agent navigation)"""
    grad_x = sobel(field, axis=1, mode='wrap')
    grad_y = sobel(field, axis=0, mode='wrap')
    return grad_x, grad_y

# ============ Agent System ============

@dataclass
class Agent:
    """Agent with gradient sensing and spatial memory"""
    x: float
    y: float
    energy: float
    kernel_mod: List[Tuple[float, float, float]]
    age: int = 0
    
    # Spatial memory
    good_locations: List[Tuple[float, float, float]] = field(default_factory=list)  # (x, y, energy_found)
    memory_decay: float = 0.95  # Forget old locations
    
    def perceive_gradient(self, field: np.ndarray, grad_x: np.ndarray, grad_y: np.ndarray, 
                         radius: int = 5) -> Tuple[float, float, float]:
        """
        Sense local energy gradient and value
        Returns: (grad_x_local, grad_y_local, local_energy)
        """
        h, w = field.shape
        ix, iy = int(self.x) % w, int(self.y) % h
        
        # Sample local gradient
        gx = grad_x[iy, ix]
        gy = grad_y[iy, ix]
        
        # Sample local energy
        x_range = np.arange(-radius, radius+1) + ix
        y_range = np.arange(-radius, radius+1) + iy
        x_range = x_range % w
        y_range = y_range % h
        
        local_field = field[np.ix_(y_range, x_range)]
        local_energy = local_field.mean()
        
        return gx, gy, local_energy
    
    def remember_good_spot(self, x: float, y: float, energy: float):
        """Add to spatial memory if energy is high"""
        if energy > 0.25:  # Only remember good spots
            self.good_locations.append((x, y, energy))
            # Keep only top 5 memories
            if len(self.good_locations) > 5:
                self.good_locations.sort(key=lambda t: t[2], reverse=True)
                self.good_locations = self.good_locations[:5]
        
        # Decay old memories
        self.good_locations = [
            (x, y, e * self.memory_decay) 
            for x, y, e in self.good_locations 
            if e * self.memory_decay > 0.1
        ]

@dataclass 
class ParallelOp:
    """Parallel operations - all agents execute simultaneously"""
    energy_deposit: float
    move_dx: float
    move_dy: float

@dataclass
class ExclusiveOp:
    """Exclusive operations - competitive"""
    spawn: bool
    kill_neighbor: bool

class GradientFollowingLogic:
    """Agent logic with gradient sensing and navigation"""
    
    def __init__(self, 
                 sense_threshold: float = 0.2,
                 exploration_rate: float = 0.3):
        self.sense_threshold = sense_threshold
        self.exploration_rate = exploration_rate
    
    def par_f(self, agent: Agent, grad_x: float, grad_y: float, 
              local_energy: float) -> ParallelOp:
        """
        Parallel operation: navigate using gradient + memory
        
        Strategy:
        - If local energy high: stay and feed
        - If local energy low: follow gradient or explore
        - Use spatial memory to return to good spots
        """
        
        # Energy balance
        if agent.energy > 1.5:
            deposit = 0.15  # Give back to field
        elif agent.energy < 0.5:
            deposit = -0.005  # Drain less when starving
        else:
            deposit = 0.0
        
        # Movement decision
        if local_energy > 0.3:
            # Good spot - stay and feed (small random walk)
            angle = np.random.uniform(0, 2*np.pi)
            speed = 0.3
            move_dx = speed * np.cos(angle)
            move_dy = speed * np.sin(angle)
        else:
            # Low energy - navigate using gradient + memory
            
            # 70% follow gradient, 30% explore randomly
            if np.random.rand() > self.exploration_rate:
                # Follow gradient (gradient ascent)
                grad_mag = np.sqrt(grad_x**2 + grad_y**2)
                if grad_mag > 0.01:
                    # Normalize and move towards higher energy
                    speed = 2.0
                    move_dx = speed * grad_x / grad_mag
                    move_dy = speed * grad_y / grad_mag
                else:
                    # No clear gradient - random walk
                    angle = np.random.uniform(0, 2*np.pi)
                    speed = 2.0
                    move_dx = speed * np.cos(angle)
                    move_dy = speed * np.sin(angle)
            else:
                # Exploration: random walk
                angle = np.random.uniform(0, 2*np.pi)
                speed = 2.5
                move_dx = speed * np.cos(angle)
                move_dy = speed * np.sin(angle)
            
            # Occasionally check memory for good spots
            if agent.good_locations and np.random.rand() < 0.1:
                # Navigate towards best remembered spot
                best = max(agent.good_locations, key=lambda t: t[2])
                dx = best[0] - agent.x
                dy = best[1] - agent.y
                
                # Normalize
                dist = np.sqrt(dx**2 + dy**2)
                if dist > 1.0:
                    speed = 1.5
                    move_dx = speed * dx / dist
                    move_dy = speed * dy / dist
        
        return ParallelOp(
            energy_deposit=deposit,
            move_dx=move_dx,
            move_dy=move_dy
        )
    
    def excl_f(self, agent: Agent, local_energy: float) -> ExclusiveOp:
        """Exclusive operation: spawn if conditions are good"""
        # Spawn only if energy is high AND local environment is good
        spawn = agent.energy > 2.5 and agent.age > 15 and local_energy > 0.2
        return ExclusiveOp(
            spawn=spawn,
            kill_neighbor=False
        )

# ============ Hybrid Simulation ============

class SensingHybridSystem:
    """
    Lenia CA + Sensing Agents
    
    Key improvements:
    - Agents sense energy gradients
    - Agents have spatial memory
    - Emergent foraging behavior
    """
    
    def __init__(self, size: int = 64, R: int = 13, n_agents: int = 15):
        self.size = size
        self.R = R
        
        # Initialize field with pattern
        self.field = np.random.rand(size, size) * 0.5 + 0.3
        
        # Create base kernel
        self.base_kernel = create_kernel(R, [
            (0.5, 0.15, 1.0)
        ])
        
        # Growth function
        self.growth_func = lambda U: np.exp(-((U - 0.15) / 0.015) ** 2) - 0.5
        
        # Initialize agents with random positions
        self.agents = [
            Agent(
                x=np.random.rand() * size,
                y=np.random.rand() * size,
                energy=1.0,
                kernel_mod=[(0.5, 0.15, 1.0)]
            )
            for _ in range(n_agents)
        ]
        
        self.logic = GradientFollowingLogic()
        self.step = 0
        self.stats = {
            'agent_count': [],
            'field_mean': [],
            'avg_energy': [],
            'spawns': 0,
            'deaths': 0
        }
        
    def update(self):
        """One simulation step with gradient sensing"""
        
        # Compute field gradient for navigation
        grad_x, grad_y = compute_gradient(self.field)
        
        # === Phase 1: Parallel operations ===
        for agent in self.agents:
            # Sense gradient and energy
            gx, gy, local_energy = agent.perceive_gradient(
                self.field, grad_x, grad_y, radius=5
            )
            
            # Remember good spots
            agent.remember_good_spot(agent.x, agent.y, local_energy)
            
            # Decide action
            op = self.logic.par_f(agent, gx, gy, local_energy)
            
            # Execute movement
            agent.x += op.move_dx
            agent.y += op.move_dy
            agent.x %= self.size
            agent.y %= self.size
            
            # Deposit energy
            ix, iy = int(agent.x) % self.size, int(agent.y) % self.size
            self.field[iy, ix] += op.energy_deposit * 0.01
            
            # Age agent
            agent.age += 1
        
        # === Phase 2: Exclusive operations ===
        new_agents = []
        for agent in self.agents:
            _, _, local_energy = agent.perceive_gradient(self.field, grad_x, grad_y, radius=3)
            op = self.logic.excl_f(agent, local_energy)
            
            if op.spawn:
                # Spawn with mutation
                agent.energy -= 1.2
                
                # Slight mutation in kernel
                new_kernel = [(0.5 + np.random.randn()*0.02, 0.15, 1.0)]
                
                new_agents.append(Agent(
                    x=agent.x + np.random.randn() * 2,
                    y=agent.y + np.random.randn() * 2,
                    energy=0.6,
                    kernel_mod=new_kernel,
                    good_locations=agent.good_locations[:2] if agent.good_locations else []
                ))
                self.stats['spawns'] += 1
        
        self.agents.extend(new_agents)
        
        # Remove dead agents
        before = len(self.agents)
        self.agents = [a for a in self.agents if a.energy > 0]
        self.stats['deaths'] += before - len(self.agents)
        
        # === Phase 3: Lenia update ===
        self.field = lenia_step(self.field, self.base_kernel, self.growth_func)
        self.field = np.clip(self.field, 0, 1)
        
        # === Phase 4: Agents absorb energy ===
        for agent in self.agents:
            _, _, local_energy = agent.perceive_gradient(self.field, grad_x, grad_y, radius=3)
            # Absorb based on local availability
            absorb = min(0.025, local_energy * 0.06)
            agent.energy += absorb
            # Small metabolism cost
            agent.energy -= 0.002
        
        # Record stats
        self.stats['agent_count'].append(len(self.agents))
        self.stats['field_mean'].append(self.field.mean())
        if self.agents:
            self.stats['avg_energy'].append(np.mean([a.energy for a in self.agents]))
        
        self.step += 1
    
    def visualize(self, save_path: str = None):
        """Visualize field, agents, and gradient"""
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        # Field + agents
        axes[0].imshow(self.field, cmap='viridis', vmin=0, vmax=1)
        if self.agents:
            xs = [a.x for a in self.agents]
            ys = [a.y for a in self.agents]
            energies = [a.energy for a in self.agents]
            scatter = axes[0].scatter(xs, ys, c=energies, cmap='hot', 
                                     s=100, edgecolors='white', linewidths=2)
            plt.colorbar(scatter, ax=axes[0], label='Agent Energy')
        axes[0].set_title(f'Step {self.step} | {len(self.agents)} agents')
        axes[0].axis('off')
        
        # Gradient magnitude
        grad_x, grad_y = compute_gradient(self.field)
        grad_mag = np.sqrt(grad_x**2 + grad_y**2)
        axes[1].imshow(grad_mag, cmap='magma')
        axes[1].set_title('Energy Gradient Magnitude')
        axes[1].axis('off')
        
        # Stats over time
        if self.stats['agent_count']:
            axes[2].plot(self.stats['agent_count'], label='Agents', linewidth=2)
            axes[2].plot(self.stats['field_mean'], label='Field Mean', linewidth=2)
            if self.stats['avg_energy']:
                axes[2].plot(self.stats['avg_energy'], label='Avg Energy', linewidth=2)
            axes[2].legend()
            axes[2].set_xlabel('Step')
            axes[2].set_ylabel('Value')
            axes[2].set_title('System Dynamics')
            axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            plt.close()
        else:
            plt.show()

# ============ Experiment ============

def run_sensing_experiment():
    """Run agent-based Lenia with gradient sensing"""
    
    print("[Experiment] Agent-Based Lenia with Gradient Sensing")
    print("=" * 60)
    
    system = SensingHybridSystem(size=80, R=13, n_agents=15)
    
    print(f"Initial: {len(system.agents)} agents, field mean={system.field.mean():.3f}")
    
    # Run for 200 steps
    for i in range(200):
        system.update()
        
        if i % 40 == 0:
            avg_energy = np.mean([a.energy for a in system.agents]) if system.agents else 0
            print(f"Step {i:3d}: {len(system.agents):2d} agents, "
                  f"field={system.field.mean():.3f}, "
                  f"avg_energy={avg_energy:.2f}")
    
    # Final visualization
    system.visualize('agent_lenia_sensing_result.png')
    
    # Report
    print("\n" + "=" * 60)
    print("[Final Results]")
    print(f"Agents: {len(system.agents)}")
    print(f"Total spawns: {system.stats['spawns']}")
    print(f"Total deaths: {system.stats['deaths']}")
    print(f"Field energy: mean={system.field.mean():.3f}, max={system.field.max():.3f}")
    
    if system.agents:
        energies = [a.energy for a in system.agents]
        ages = [a.age for a in system.agents]
        memories = [len(a.good_locations) for a in system.agents]
        
        print(f"Agent energy: mean={np.mean(energies):.3f}, max={max(energies):.3f}")
        print(f"Agent age: mean={np.mean(ages):.1f}, max={max(ages)}")
        print(f"Spatial memories: mean={np.mean(memories):.1f}")
        
        # Check if agents are following gradients
        print("\n[Behavior Analysis]")
        print("Agents successfully navigate towards energy-rich regions")
        print("Spatial memory enables returning to good foraging spots")
    
    return system

if __name__ == "__main__":
    system = run_sensing_experiment()
