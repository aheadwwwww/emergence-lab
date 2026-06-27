"""
Minimal Agent-Based Lenia

Inspired by Biomaker CA architecture, this implements a hybrid system:
- Lenia CA base layer (continuous CA)
- Agent particles that can move and modify Lenia kernel
- Goal: Study how agents shape their own environment

Key insight from Biomaker CA:
- Parallel operations (energy transfer, state update) - all agents act simultaneously
- Exclusive operations (spawn, kill) - competitive, requires arbitration
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import convolve
from dataclasses import dataclass
from typing import List, Tuple
import json

# ============ Lenia Core ============

def create_kernel(R: int, peaks: List[Tuple[float, float, float]]) -> np.ndarray:
    """
    Create multi-peak Lenia kernel
    peaks: [(center1, width1, weight1), ...]
    """
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

# ============ Agent System ============

@dataclass
class Agent:
    """Agent that lives on Lenia field and can modify it"""
    x: float
    y: float
    energy: float
    kernel_mod: List[Tuple[float, float, float]]  # How agent modifies local kernel
    age: int = 0
    
    def perceive(self, field: np.ndarray, radius: int = 5) -> float:
        """Sample local field energy"""
        h, w = field.shape
        ix, iy = int(self.x) % w, int(self.y) % h
        
        # Sample a small region
        x_range = np.arange(-radius, radius+1) + ix
        y_range = np.arange(-radius, radius+1) + iy
        x_range = x_range % w
        y_range = y_range % h
        
        local_field = field[np.ix_(y_range, x_range)]
        return local_field.mean()

@dataclass 
class ParallelOp:
    """Parallel operations - all agents execute simultaneously"""
    energy_deposit: float  # Energy to deposit into field
    move_dx: float         # Movement in x
    move_dy: float         # Movement in y

@dataclass
class ExclusiveOp:
    """Exclusive operations - competitive, requires arbitration"""
    spawn: bool            # Try to spawn offspring
    kill_neighbor: bool    # Try to kill nearby agent

class AgentLogic:
    """Simple agent decision logic"""
    
    def __init__(self, threshold: float = 0.3):
        self.threshold = threshold
    
    def par_f(self, agent: Agent, local_energy: float) -> ParallelOp:
        """Parallel operation: move and deposit energy"""
        # Balance: deposit energy back into field when high
        if agent.energy > 1.5:
            deposit = 0.2  # Give back to field
        elif agent.energy < 0.5:
            deposit = -0.01  # Drain less when starving
        else:
            deposit = 0.0
        
        # Biased walk towards higher energy regions
        angle = np.random.uniform(0, 2*np.pi)
        speed = 1.5
        
        return ParallelOp(
            energy_deposit=deposit,
            move_dx=speed * np.cos(angle),
            move_dy=speed * np.sin(angle)
        )
    
    def excl_f(self, agent: Agent, local_energy: float) -> ExclusiveOp:
        """Exclusive operation: spawn if energy high"""
        spawn = agent.energy > 2.0 and agent.age > 10
        return ExclusiveOp(
            spawn=spawn,
            kill_neighbor=False
        )

# ============ Hybrid Simulation ============

class HybridLeniaAgentSystem:
    """
    Lenia CA + Agent particles hybrid system
    
    Timeline:
    1. Agents perform parallel ops (move, deposit energy)
    2. Agents perform exclusive ops (spawn - with competition)
    3. Lenia field updates based on modified kernels
    4. Agents absorb energy from field
    """
    
    def __init__(self, size: int = 64, R: int = 13, n_agents: int = 10):
        self.size = size
        self.R = R
        
        # Initialize Lenia field with random pattern
        # Start with more energy to support agents
        self.field = np.random.rand(size, size) * 0.5 + 0.3
        
        # Create base kernel (standard Lenia)
        self.base_kernel = create_kernel(R, [
            (0.5, 0.15, 1.0)  # Single ring
        ])
        
        # Growth function
        self.growth_func = lambda U: np.exp(-((U - 0.15) / 0.015) ** 2) - 0.5
        
        # Initialize agents
        self.agents = [
            Agent(
                x=np.random.rand() * size,
                y=np.random.rand() * size,
                energy=1.0,
                kernel_mod=[(0.5, 0.15, 1.0)]
            )
            for _ in range(n_agents)
        ]
        
        self.logic = AgentLogic()
        self.step = 0
        
    def update(self):
        """One simulation step"""
        
        # === Phase 1: Parallel operations ===
        parallel_ops = []
        for agent in self.agents:
            local_energy = agent.perceive(self.field)
            op = self.logic.par_f(agent, local_energy)
            parallel_ops.append(op)
            
            # Execute parallel ops
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
        for i, agent in enumerate(self.agents):
            local_energy = agent.perceive(self.field)
            op = self.logic.excl_f(agent, local_energy)
            
            if op.spawn:
                # Spawn new agent (costs energy)
                agent.energy -= 1.0
                new_agents.append(Agent(
                    x=agent.x + np.random.randn(),
                    y=agent.y + np.random.randn(),
                    energy=0.5,
                    kernel_mod=agent.kernel_mod.copy()
                ))
        
        self.agents.extend(new_agents)
        
        # Remove dead agents
        self.agents = [a for a in self.agents if a.energy > 0]
        
        # === Phase 3: Lenia update ===
        self.field = lenia_step(self.field, self.base_kernel, self.growth_func)
        self.field = np.clip(self.field, 0, 1)
        
        # === Phase 4: Agents absorb energy ===
        for agent in self.agents:
            local_energy = agent.perceive(self.field, radius=3)
            # Absorb proportionally, but cap it
            absorb = min(0.02, local_energy * 0.05)
            agent.energy += absorb
            
        self.step += 1
    
    def visualize(self, save_path: str = None):
        """Visualize field and agents"""
        fig, ax = plt.subplots(1, 1, figsize=(8, 8))
        
        # Field
        ax.imshow(self.field, cmap='viridis', vmin=0, vmax=1)
        
        # Agents
        if self.agents:
            xs = [a.x for a in self.agents]
            ys = [a.y for a in self.agents]
            energies = [a.energy for a in self.agents]
            
            scatter = ax.scatter(xs, ys, c=energies, cmap='hot', 
                               s=100, edgecolors='white', linewidths=2)
            plt.colorbar(scatter, label='Agent Energy')
        
        ax.set_title(f'Step {self.step} | {len(self.agents)} agents')
        ax.axis('off')
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            plt.close()
        else:
            plt.show()

# ============ Experiment Runner ============

def run_experiment():
    """Run hybrid Lenia-Agent simulation"""
    
    print("[Experiment] Minimal Agent-Based Lenia")
    print("=" * 50)
    
    # Create system
    system = HybridLeniaAgentSystem(size=64, R=13, n_agents=10)
    
    # Run for 100 steps
    for i in range(100):
        system.update()
        
        if i % 20 == 0:
            print(f"Step {i}: {len(system.agents)} agents, "
                  f"field mean={system.field.mean():.3f}")
    
    # Save final visualization
    system.visualize('agent_lenia_minimal_result.png')
    
    # Report
    print("\n[Results]")
    print(f"Final agents: {len(system.agents)}")
    print(f"Field energy: mean={system.field.mean():.3f}, max={system.field.max():.3f}")
    
    if system.agents:
        energies = [a.energy for a in system.agents]
        print(f"Agent energy: mean={np.mean(energies):.3f}, max={max(energies):.3f}")
    
    return system

if __name__ == "__main__":
    system = run_experiment()
