"""
Swarm Decision Making - Collective Intelligence Without Central Control

Simulates a swarm making democratic decisions through local interactions.
Classic example: honeybee nest site selection (Seeley's research)

Emergent property: Optimal decision despite no individual knowing the global optimum
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import defaultdict

class SwarmAgent:
    """Individual agent in the swarm"""
    
    def __init__(self, agent_id, initial_opinion=None):
        self.id = agent_id
        self.opinion = initial_opinion  # Which option they support
        self.confidence = 0.1  # How strongly they hold this opinion
        self.state = 'uncommitted'  # uncommitted, committed, quorum_reached
        
    def interact(self, other_agents, options_quality):
        """
        Local interaction rules:
        1. Random encounters with neighbors
        2. Transfer opinion with probability based on confidence
        3. Increase confidence over time
        """
        if len(other_agents) == 0:
            return
            
        # Randomly encounter another agent
        other = np.random.choice(other_agents)
        
        if other.state == 'committed' and self.state == 'uncommitted':
            # Get recruited
            self.opinion = other.opinion
            self.confidence = 0.2
            self.state = 'committed'
            
        elif other.state == 'committed' and self.state == 'committed':
            if other.opinion == self.opinion:
                # Reinforcement - same opinion
                self.confidence = min(1.0, self.confidence + 0.05)
            else:
                # Conflict - compare based on option quality
                q1 = options_quality.get(self.opinion, 0.5)
                q2 = options_quality.get(other.opinion, 0.5)
                if np.random.random() < q2 / (q1 + q2):
                    self.opinion = other.opinion
                    self.confidence = 0.3

class SwarmDecisionSimulation:
    """
    Simulates collective decision making
    
    Inspired by:
    - Honeybee nest selection (Seeley)
    - Ant colony path selection
    - Slime mold maze solving
    """
    
    def __init__(self, n_agents=100, n_options=3, space_size=100):
        self.n_agents = n_agents
        self.n_options = n_options
        self.space_size = space_size
        
        # Option qualities (hidden from agents)
        # Agents discover quality through local sampling
        self.options_quality = {i: np.random.random() for i in range(n_options)}
        # Make one option clearly best for testing
        self.options_quality[np.argmax(list(self.options_quality.values()))] = 0.9
        
        # Agent positions in 2D space
        self.positions = np.random.random((n_agents, 2)) * space_size
        
        # Create agents
        self.agents = []
        for i in range(n_agents):
            agent = SwarmAgent(i)
            # Small chance of initial commitment
            if np.random.random() < 0.1:
                agent.opinion = np.random.randint(n_options)
                agent.state = 'committed'
                agent.confidence = 0.3
            self.agents.append(agent)
            
        self.history = []
        
    def get_neighbors(self, agent_idx, radius=10):
        """Get agents within interaction radius"""
        pos = self.positions[agent_idx]
        distances = np.linalg.norm(self.positions - pos, axis=1)
        neighbor_indices = np.where((distances > 0) & (distances < radius))[0]
        return [self.agents[i] for i in neighbor_indices]
    
    def step(self):
        """One simulation step"""
        # Move agents randomly (Brownian motion)
        movement = (np.random.random((self.n_agents, 2)) - 0.5) * 4
        self.positions = np.clip(self.positions + movement, 0, self.space_size)
        
        # Interactions
        for i, agent in enumerate(self.agents):
            neighbors = self.get_neighbors(i)
            agent.interact(neighbors, self.options_quality)
            
            # Spontaneous discovery (agents randomly sample options)
            if agent.state == 'uncommitted' and np.random.random() < 0.01:
                # Discover an option, quality affects commitment
                option = np.random.randint(self.n_options)
                quality = self.options_quality[option]
                if np.random.random() < quality:
                    agent.opinion = option
                    agent.confidence = quality * 0.5
                    agent.state = 'committed'
        
        # Record state
        opinion_counts = defaultdict(int)
        for agent in self.agents:
            if agent.opinion is not None:
                opinion_counts[agent.opinion] += 1
        self.history.append(dict(opinion_counts))
        
    def run(self, n_steps=200):
        """Run simulation"""
        for _ in range(n_steps):
            self.step()
        return self.history
        
    def visualize(self, save_path=None):
        """Visualize the decision process"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        
        # 1. Opinion distribution over time
        ax1 = axes[0, 0]
        for opt in range(self.n_options):
            counts = [h.get(opt, 0) for h in self.history]
            label = f"Option {opt} (q={self.options_quality[opt]:.2f})"
            color = plt.cm.tab10(opt)
            ax1.plot(counts, label=label, color=color, linewidth=2)
        ax1.set_xlabel('Time Step')
        ax1.set_ylabel('Number of Supporters')
        ax1.set_title('Opinion Dynamics Over Time')
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # 2. Final opinion distribution
        ax2 = axes[0, 1]
        final = self.history[-1]
        options = list(range(self.n_options))
        counts = [final.get(o, 0) for o in options]
        colors = [plt.cm.tab10(o) for o in options]
        bars = ax2.bar(options, counts, color=colors)
        ax2.set_xlabel('Option')
        ax2.set_ylabel('Final Supporters')
        ax2.set_title('Final Decision Distribution')
        
        # Highlight best option
        best_opt = max(self.options_quality, key=self.options_quality.get)
        bars[best_opt].set_edgecolor('red')
        bars[best_opt].set_linewidth(3)
        
        # 3. Agent positions colored by opinion
        ax3 = axes[1, 0]
        for opt in range(self.n_options):
            mask = [a.opinion == opt for a in self.agents]
            if any(mask):
                positions = self.positions[mask]
                ax3.scatter(positions[:, 0], positions[:, 1], 
                          c=[plt.cm.tab10(opt)], label=f'Option {opt}', alpha=0.6, s=30)
        uncommitted = [a.opinion is None for a in self.agents]
        if any(uncommitted):
            ax3.scatter(self.positions[uncommitted, 0], self.positions[uncommitted, 1],
                       c='gray', label='Uncommitted', alpha=0.3, s=20)
        ax3.set_xlabel('X Position')
        ax3.set_ylabel('Y Position')
        ax3.set_title('Agent Positions (colored by opinion)')
        ax3.legend(loc='upper right')
        ax3.set_xlim(0, self.space_size)
        ax3.set_ylim(0, self.space_size)
        
        # 4. Convergence analysis
        ax4 = axes[1, 1]
        # Calculate consensus strength (how concentrated opinions are)
        consensus = []
        for h in self.history:
            total = sum(h.values())
            if total > 0:
                max_count = max(h.values())
                consensus.append(max_count / total)
            else:
                consensus.append(0)
        ax4.plot(consensus, linewidth=2, color='darkblue')
        ax4.axhline(y=0.5, color='red', linestyle='--', label='Majority threshold')
        ax4.axhline(y=0.7, color='green', linestyle='--', label='Strong consensus')
        ax4.set_xlabel('Time Step')
        ax4.set_ylabel('Consensus Strength')
        ax4.set_title('Convergence to Consensus')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved to {save_path}")
            
        return fig
        
    def analyze(self):
        """Analyze the decision outcome"""
        final = self.history[-1]
        best_opt = max(self.options_quality, key=self.options_quality.get)
        
        total_committed = sum(final.values())
        best_supporters = final.get(best_opt, 0)
        
        if total_committed > 0:
            best_fraction = best_supporters / total_committed
        else:
            best_fraction = 0
            
        consensus_reached = best_fraction > 0.5
        correct_decision = consensus_reached and (max(final, key=final.get) == best_opt)
        
        return {
            'best_option': best_opt,
            'best_quality': self.options_quality[best_opt],
            'best_supporters': best_supporters,
            'consensus_strength': best_fraction,
            'consensus_reached': consensus_reached,
            'correct_decision': correct_decision,
            'total_committed': total_committed
        }


def run_swarm_experiment():
    """Run a complete swarm decision experiment"""
    print("=" * 60)
    print("SWARM DECISION MAKING - Emergent Collective Intelligence")
    print("=" * 60)
    
    # Create simulation
    sim = SwarmDecisionSimulation(n_agents=150, n_options=4)
    
    print(f"\nOption qualities (hidden from agents):")
    for opt, quality in sorted(sim.options_quality.items()):
        print(f"  Option {opt}: {quality:.2f}")
    
    print(f"\nRunning simulation with {sim.n_agents} agents...")
    history = sim.run(n_steps=300)
    
    # Analyze results
    results = sim.analyze()
    
    print(f"\n{'=' * 60}")
    print("RESULTS:")
    print(f"  Best option: {results['best_option']} (quality: {results['best_quality']:.2f})")
    print(f"  Supporters for best: {results['best_supporters']}")
    print(f"  Consensus strength: {results['consensus_strength']:.1%}")
    print(f"  Consensus reached: {'YES' if results['consensus_reached'] else 'NO'}")
    print(f"  Correct decision: {'YES' if results['correct_decision'] else 'NO'}")
    print(f"{'=' * 60}")
    
    # Visualize
    save_path = "D:/emergence_experiments/swarm_decision.png"
    sim.visualize(save_path)
    
    return sim, results


if __name__ == "__main__":
    run_swarm_experiment()
