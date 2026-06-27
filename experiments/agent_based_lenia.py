"""
Agent-Based Lenia: Hybrid of Biomaker CA and Lenia

Key idea: Each "species" is an agent with its own Lenia parameters.
Agents compete for space using exclusive operations.
Inspired by Biomaker CA's parallel/exclusive operation split.

Date: 2026-06-27
"""

import jax
import jax.numpy as jp
from jax import jit, vmap
import jax.random as jr
from functools import partial
from typing import NamedTuple, Tuple, Optional
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter


# ============================================
# Core Types
# ============================================

class LeniaAgent(NamedTuple):
    """A Lenia 'species' agent with parameters and position."""
    params: jp.ndarray  # [R, mu, sigma] or [kernel_params]
    energy: float       # Current energy
    age: int            # Age in steps
    id: int             # Unique ID
    pos: Tuple[int, int]  # Position (for localized agents)


class ExclusiveOp(NamedTuple):
    """Exclusive operation: compete for space."""
    target_pos: Tuple[int, int]
    action_type: int  # 0=spawn, 1=attack, 2=share_energy
    intensity: float


class ParallelOp(NamedTuple):
    """Parallel operation: local Lenia update."""
    field_contribution: jp.ndarray
    energy_delta: float
    state_delta: jp.ndarray


# ============================================
# Lenia Core Functions (from previous experiments)
# ============================================

def lenia_kernel(R: int, mu: float, sigma: float) -> jp.ndarray:
    """Generate Lenia kernel with parameters."""
    kernel_1d = jp.zeros(R * 2 + 1)
    
    def fill_ring(i, val):
        dist = jp.abs(i - R)
        # Gaussian ring at distance mu*R
        ring_val = jp.exp(-((dist - mu * R) ** 2) / (2 * sigma ** 2))
        return val.at[i].set(ring_val)
    
    kernel_1d = jax.lax.fori_loop(0, R * 2 + 1, fill_ring, kernel_1d)
    
    # Normalize
    total = jp.sum(kernel_1d) + 1e-8
    kernel_1d = kernel_1d / total
    
    return kernel_1d


def lenia_step(field: jp.ndarray, kernel_1d: jp.ndarray, T: float = 0.1) -> jp.ndarray:
    """Single Lenia update step with 1D kernel (row/col convolution)."""
    # Apply along rows
    growth_rows = jax.scipy.signal.convolve(field, kernel_1d[None, :], mode='same')
    # Apply along cols
    growth_cols = jax.scipy.signal.convolve(field, kernel_1d[:, None], mode='same')
    # Average
    growth = (growth_rows + growth_cols) / 2
    
    # Growth function
    growth = T * (2 * growth - 1)
    
    # Update
    new_field = field + growth
    new_field = jp.clip(new_field, 0, 1)
    
    return new_field


# ============================================
# Agent-Based System
# ============================================

def spawn_agent(
    key: jr.PRNGKey,
    parent_params: jp.ndarray,
    mutation_rate: float = 0.1
) -> LeniaAgent:
    """Spawn a new agent with mutated parameters."""
    k1, k2, k3, k4 = jr.split(key, 4)
    
    # Mutate parameters
    noise = jr.normal(k1, parent_params.shape) * mutation_rate
    new_params = parent_params + noise
    
    # Ensure valid ranges
    # R: integer, positive (let's say 5-20)
    # mu: 0-1
    # sigma: 0-1
    new_params = jp.array([
        jp.clip(new_params[0], 5.0, 20.0),  # R
        jp.clip(new_params[1], 0.1, 0.9),  # mu
        jp.clip(new_params[2], 0.05, 0.5),  # sigma
    ])
    
    return LeniaAgent(
        params=new_params,
        energy=1.0,
        age=0,
        id=int(jr.randint(k2, (), 0, 1000000)),
        pos=(int(jr.randint(k3, (), 0, 64)), int(jr.randint(k4, (), 0, 64)))
    )


def agent_parallel_op(
    agent: LeniaAgent,
    local_field: jp.ndarray
) -> ParallelOp:
    """Compute parallel operation: Lenia update contribution."""
    # Generate kernel from parameters
    R = int(agent.params[0])
    mu = agent.params[1]
    sigma = agent.params[2]
    
    kernel_1d = lenia_kernel(R, mu, sigma)
    
    # Compute growth contribution
    growth_rows = jax.scipy.signal.convolve(local_field, kernel_1d[None, :], mode='same')
    growth_cols = jax.scipy.signal.convolve(local_field, kernel_1d[:, None], mode='same')
    growth = (growth_rows + growth_cols) / 2
    
    # Energy cost proportional to activity
    energy_delta = -0.01 * jp.mean(jp.abs(growth))
    
    return ParallelOp(
        field_contribution=growth,
        energy_delta=energy_delta,
        state_delta=jp.zeros(3)  # No state change for now
    )


def resolve_exclusive_ops(
    ops: list[ExclusiveOp],
    agents: list[LeniaAgent]
) -> list[int]:
    """Resolve conflicts in exclusive operations.
    
    Returns list of winning agent indices for each target.
    """
    if not ops:
        return []
    
    # Group by target position
    targets = {}
    for i, op in enumerate(ops):
        target = op.target_pos
        if target not in targets:
            targets[target] = []
        targets[target].append((i, op.intensity))
    
    # Winner for each target: highest intensity wins
    winners = {}
    for target, candidates in targets.items():
        winner_idx, _ = max(candidates, key=lambda x: x[1])
        winners[target] = winner_idx
    
    return [winners.get(op.target_pos, -1) for op in ops]


# ============================================
# Simulation
# ============================================

class AgentBasedLeniaSimulation:
    """Simulation of agent-based Lenia system."""
    
    def __init__(
        self,
        field_size: int = 64,
        n_initial_agents: int = 5,
        seed: int = 42
    ):
        self.field_size = field_size
        self.key = jr.PRNGKey(seed)
        
        # Initialize field
        self.key, k1 = jr.split(self.key)
        self.field = jr.uniform(k1, (field_size, field_size))
        
        # Initialize agents
        self.agents = []
        for i in range(n_initial_agents):
            self.key, k1, k2, k3, k4 = jr.split(self.key, 5)
            agent = LeniaAgent(
                params=jp.array([
                    jr.randint(k1, (), 8, 15).astype(float),  # R
                    jr.uniform(k2, (), minval=0.2, maxval=0.8),            # mu
                    jr.uniform(k3, (), minval=0.1, maxval=0.3),            # sigma
                ]),
                energy=1.0,
                age=0,
                id=i,
                pos=(
                    int(jr.randint(k4, (), 0, field_size)),
                    int(jr.randint(k4, (), 0, field_size))
                )
            )
            self.agents.append(agent)
        
        self.history = []
        self.step_count = 0
    
    def step(self):
        """Execute one simulation step."""
        self.step_count += 1
        
        # Phase 1: Parallel operations (all agents contribute to field)
        total_contribution = jp.zeros_like(self.field)
        for agent in self.agents:
            # Extract local field around agent
            x, y = agent.pos
            R = int(agent.params[0])
            
            # Pad field for boundary
            padded = jp.pad(self.field, R, mode='wrap')
            local_field = padded[x:x+2*R+1, y:y+2*R+1]
            
            # Get parallel operation
            op = agent_parallel_op(agent, local_field)
            
            # Add contribution to global field
            # (simplified: agent affects local region)
            # In a full implementation, we'd handle boundary conditions
            total_contribution = total_contribution.at[
                max(0, x-R):min(self.field_size, x+R+1),
                max(0, y-R):min(self.field_size, y+R+1)
            ].add(op.field_contribution[:min(2*R+1, self.field_size), :min(2*R+1, self.field_size)])
            
            # Update agent energy
            agent = agent._replace(energy=agent.energy + op.energy_delta)
        
        # Apply field update
        self.field = self.field + 0.1 * total_contribution
        self.field = jp.clip(self.field, 0, 1)
        
        # Phase 2: Exclusive operations (spawn, compete)
        exclusive_ops = []
        for agent in self.agents:
            if agent.energy > 0.8 and agent.age > 10:
                # High energy agent can spawn
                self.key, k1 = jr.split(self.key)
                dx = int(jr.randint(k1, (), -3, 4))
                dy = int(jr.randint(k1, (), -3, 4))
                target_pos = (
                    (agent.pos[0] + dx) % self.field_size,
                    (agent.pos[1] + dy) % self.field_size
                )
                exclusive_ops.append(ExclusiveOp(
                    target_pos=target_pos,
                    action_type=0,  # spawn
                    intensity=agent.energy
                ))
        
        # Resolve conflicts
        winners = resolve_exclusive_ops(exclusive_ops, self.agents)
        
        # Spawn new agents
        for i, winner in enumerate(winners):
            if winner >= 0 and winner < len(self.agents):
                parent = self.agents[winner]
                self.key, k1 = jr.split(self.key)
                child = spawn_agent(k1, parent.params, mutation_rate=0.1)
                child = child._replace(
                    pos=exclusive_ops[i].target_pos,
                    energy=0.5  # Child gets half parent's energy
                )
                parent = parent._replace(energy=parent.energy - 0.5)
                self.agents[winner] = parent
                self.agents.append(child)
        
        # Phase 3: Aging and death
        surviving_agents = []
        for agent in self.agents:
            agent = agent._replace(age=agent.age + 1)
            # Death conditions
            if agent.energy > 0 and agent.age < 100:
                surviving_agents.append(agent)
        
        self.agents = surviving_agents
        
        # Record history
        self.history.append({
            'field': self.field,
            'n_agents': len(self.agents),
            'step': self.step_count
        })
    
    def run(self, n_steps: int = 100):
        """Run simulation for n steps."""
        for _ in range(n_steps):
            self.step()
    
    def visualize(self, save_path: Optional[str] = None):
        """Visualize simulation history."""
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        # Final field
        ax1 = axes[0]
        im1 = ax1.imshow(self.field, cmap='viridis', interpolation='bilinear')
        ax1.set_title(f'Final Field (Step {self.step_count})')
        plt.colorbar(im1, ax=ax1)
        
        # Agent positions
        ax2 = axes[1]
        ax2.imshow(self.field, cmap='viridis', alpha=0.5, interpolation='bilinear')
        if self.agents:
            positions = jp.array([agent.pos for agent in self.agents])
            energies = jp.array([agent.energy for agent in self.agents])
            ax2.scatter(positions[:, 1], positions[:, 0], c=energies, cmap='hot', s=50, edgecolors='white')
        ax2.set_title(f'Agents (n={len(self.agents)})')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved to {save_path}")
        else:
            plt.show()
        
        plt.close()


# ============================================
# Main
# ============================================

if __name__ == "__main__":
    print("Agent-Based Lenia Simulation")
    print("=" * 50)
    print("\nThis is a hybrid of Biomaker CA and Lenia concepts:")
    print("  - Agents have Lenia parameters as their 'genome'")
    print("  - Parallel ops: field contributions (Lenia updates)")
    print("  - Exclusive ops: spawning (compete for space)")
    print("  - Agents die when energy < 0 or age > 100")
    print("\n" + "=" * 50)
    
    # Run simulation
    sim = AgentBasedLeniaSimulation(
        field_size=64,
        n_initial_agents=5,
        seed=42
    )
    
    print("\nRunning 50 steps...")
    sim.run(n_steps=50)
    
    print(f"\nFinal state:")
    print(f"  - Agents alive: {len(sim.agents)}")
    print(f"  - Total steps: {sim.step_count}")
    
    if sim.agents:
        print(f"\nAgent sample:")
        for i, agent in enumerate(sim.agents[:3]):
            print(f"  Agent {i}: params={agent.params}, energy={agent.energy:.2f}, age={agent.age}")
    
    # Visualize
    sim.visualize(save_path="agent_based_lenia_result.png")
    
    print("\n✓ Done!")