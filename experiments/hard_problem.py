"""
#025 Hard Problem of Consciousness — 4-in-1 Exploration

The "Hard Problem" (Chalmers): Why does physical processing give rise to subjective experience?
The "Easy Problems": discrimination, integration, reportability, behavior control.

This experiment explores four perspectives:
1. Qualia Space — mapping possible conscious states as a high-dimensional geometry
2. Information Integration (Φ/IIT) — measuring consciousness as integrated information
3. The Explanatory Gap — why physical descriptions feel incomplete
4. Emergence of Self-Model — when does a system start modeling itself as "I"?
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# Experiment 1: Qualia Space — Geometry of Possible Experiences
# ============================================================

def qualia_space():
    """Map qualia as points in a high-dimensional space, project to 2D."""
    np.random.seed(42)
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # Generate qualia points in 16D space
    n_qualia = 200
    dim = 16
    qualia = np.random.randn(n_qualia, dim)
    
    # Color by "intensity" (norm)
    intensity = np.linalg.norm(qualia, axis=1)
    
    # PCA-like projection to 2D
    U, S, Vt = np.linalg.svd(qualia - qualia.mean(axis=0), full_matrices=False)
    proj = (qualia - qualia.mean(axis=0)) @ Vt[:2].T
    
    # Panel 1: Qualia scatter
    ax = axes[0]
    scatter = ax.scatter(proj[:, 0], proj[:, 1], c=intensity, cmap='plasma', 
                         s=30, alpha=0.7, edgecolors='white', linewidth=0.5)
    ax.set_title("Qualia Space (16D → 2D Projection)", fontsize=12, fontweight='bold')
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    plt.colorbar(scatter, ax=ax, label='Intensity')
    
    # Panel 2: Qualia categories (cluster into 5 "types")
    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    labels = kmeans.fit_predict(qualia)
    type_names = ['Visual', 'Auditory', 'Emotional', 'Somatic', 'Cognitive']
    colors = ['#FF6B6B', '#4ECDC4', '#FFE66D', '#95E1D3', '#F38181']
    
    ax = axes[1]
    for i, name in enumerate(type_names):
        mask = labels == i
        ax.scatter(proj[mask, 0], proj[mask, 1], c=colors[i], s=30, 
                   alpha=0.7, label=name, edgecolors='white', linewidth=0.5)
    ax.set_title("Qualia Categories (K-Means Clustering)", fontsize=12, fontweight='bold')
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.legend(fontsize=8, loc='lower right')
    
    # Panel 3: Qualia distance matrix (how "different" are experiences?)
    ax = axes[2]
    sample_n = 30
    sample_qualia = qualia[:sample_n]
    dist_matrix = np.zeros((sample_n, sample_n))
    for i in range(sample_n):
        for j in range(sample_n):
            dist_matrix[i, j] = np.linalg.norm(sample_qualia[i] - sample_qualia[j])
    
    im = ax.imshow(dist_matrix, cmap='viridis', aspect='auto')
    ax.set_title("Qualia Distance Matrix", fontsize=12, fontweight='bold')
    ax.set_xlabel("Experience #")
    ax.set_ylabel("Experience #")
    plt.colorbar(im, ax=ax, label='Distance')
    
    plt.suptitle("#025 Hard Problem — Experiment 1: Qualia Space", 
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    path = os.path.join(OUTPUT_DIR, 'hard_problem_qualia.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [OK] qualia_space -> {path}")
    return path


# ============================================================
# Experiment 2: Integrated Information (Φ) — IIT Simulation
# ============================================================

def integrated_information():
    """
    Simulate Φ (phi) — Integrated Information Theory.
    Φ measures how much information a system has as a whole
    beyond the sum of its parts.
    """
    np.random.seed(42)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    # --- Panel 1: Φ vs System Size ---
    ax = axes[0, 0]
    sizes = np.arange(2, 33, 2)
    phi_values = []
    
    for n in sizes:
        # Simulate a system of n binary nodes with random connectivity
        states = np.random.randint(0, 2, (1000, n))
        
        # Whole system entropy
        whole_patterns = [tuple(row) for row in states]
        _, whole_counts = np.unique(whole_patterns, axis=0, return_counts=True)
        whole_entropy = -np.sum((whole_counts / len(states)) * np.log2(whole_counts / len(states) + 1e-10))
        
        # Sum of parts entropy (treat each node independently)
        part_entropies = []
        for i in range(n):
            _, counts = np.unique(states[:, i], return_counts=True)
            p = counts / len(states)
            part_entropies.append(-np.sum(p * np.log2(p + 1e-10)))
        
        # Φ = whole entropy - sum of parts (simplified)
        phi = max(0, whole_entropy - sum(part_entropies))
        phi_values.append(phi)
    
    ax.plot(sizes, phi_values, 'o-', color='#6C5CE7', linewidth=2, markersize=8)
    ax.fill_between(sizes, 0, phi_values, alpha=0.2, color='#6C5CE7')
    ax.set_xlabel("System Size (nodes)", fontsize=11)
    ax.set_ylabel("Φ (Integrated Information)", fontsize=11)
    ax.set_title("Φ vs System Size", fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # --- Panel 2: Φ vs Connectivity ---
    ax = axes[0, 1]
    n = 16
    connectivities = np.linspace(0.05, 0.95, 20)
    phi_conn = []
    
    for p in connectivities:
        # Generate random directed graph with connection probability p
        adj = np.random.rand(n, n) < p
        np.fill_diagonal(adj, 0)
        
        # Simulate dynamics
        state = np.random.randint(0, 2, n)
        history = []
        for _ in range(500):
            state = (adj @ state) % 2
            history.append(state.copy())
        history = np.array(history[-200:])
        
        # Whole entropy
        patterns = [tuple(row) for row in history]
        _, counts = np.unique(patterns, axis=0, return_counts=True)
        whole_ent = -np.sum((counts / len(history)) * np.log2(counts / len(history) + 1e-10))
        
        # Part entropy
        part_ents = []
        for i in range(n):
            _, cnts = np.unique(history[:, i], return_counts=True)
            p_i = cnts / len(history)
            part_ents.append(-np.sum(p_i * np.log2(p_i + 1e-10)))
        
        phi = max(0, whole_ent - sum(part_ents))
        phi_conn.append(phi)
    
    ax.plot(connectivities, phi_conn, 'o-', color='#E17055', linewidth=2, markersize=6)
    ax.axvline(x=0.5, color='red', linestyle='--', alpha=0.5, label='Critical?')
    ax.set_xlabel("Connection Probability", fontsize=11)
    ax.set_ylabel("Φ", fontsize=11)
    ax.set_title("Φ vs Connectivity (Edge of Chaos?)", fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    
    # --- Panel 3: Φ Decomposition (MIP — Minimum Information Partition) ---
    ax = axes[1, 0]
    n = 12
    # Generate a system with structure
    adj = np.random.rand(n, n) < 0.3
    np.fill_diagonal(adj, 0)
    
    # Compute Φ for different bipartitions
    partitions = []
    phi_parts = []
    for split in range(1, n):
        left = list(range(split))
        right = list(range(split, n))
        
        # Simulate full system
        state = np.random.randint(0, 2, n)
        full_history = []
        for _ in range(300):
            state = (adj @ state) % 2
            full_history.append(state.copy())
        full_history = np.array(full_history[-100:])
        
        # Whole entropy
        patterns = [tuple(row) for row in full_history]
        _, counts = np.unique(patterns, axis=0, return_counts=True)
        whole_ent = -np.sum((counts / 100) * np.log2(counts / 100 + 1e-10))
        
        # Entropy of left + right independently
        left_patterns = [tuple(row[left]) for row in full_history]
        right_patterns = [tuple(row[right]) for row in full_history]
        _, lc = np.unique(left_patterns, axis=0, return_counts=True)
        _, rc = np.unique(right_patterns, axis=0, return_counts=True)
        left_ent = -np.sum((lc / 100) * np.log2(lc / 100 + 1e-10))
        right_ent = -np.sum((rc / 100) * np.log2(rc / 100 + 1e-10))
        
        phi = max(0, whole_ent - (left_ent + right_ent))
        partitions.append(split)
        phi_parts.append(phi)
    
    ax.bar(partitions, phi_parts, color=['#00B894' if p == min(phi_parts) else '#DFE6E9' 
                                         for p in phi_parts], edgecolor='#636E72', linewidth=0.5)
    ax.axhline(y=min(phi_parts), color='red', linestyle='--', alpha=0.7, 
               label=f'MIP Φ = {min(phi_parts):.2f}')
    ax.set_xlabel("Bipartition Point", fontsize=11)
    ax.set_ylabel("Φ (Information Loss)", fontsize=11)
    ax.set_title("Minimum Information Partition (MIP)", fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    
    # --- Panel 4: Φ Landscape — where does consciousness emerge? ---
    ax = axes[1, 1]
    
    # Create a 2D landscape: size × connectivity
    sizes_grid = np.arange(4, 33, 2)
    conn_grid = np.linspace(0.1, 0.9, 15)
    phi_landscape = np.zeros((len(sizes_grid), len(conn_grid)))
    
    for i, n in enumerate(sizes_grid):
        for j, p in enumerate(conn_grid):
            adj = np.random.rand(n, n) < p
            np.fill_diagonal(adj, 0)
            state = np.random.randint(0, 2, n)
            history = []
            for _ in range(200):
                state = (adj @ state) % 2
                history.append(state.copy())
            history = np.array(history[-80:])
            
            patterns = [tuple(row) for row in history]
            _, counts = np.unique(patterns, axis=0, return_counts=True)
            whole_ent = -np.sum((counts / 80) * np.log2(counts / 80 + 1e-10))
            
            part_ents = 0
            for k in range(n):
                _, cnts = np.unique(history[:, k], return_counts=True)
                p_k = cnts / 80
                part_ents += -np.sum(p_k * np.log2(p_k + 1e-10))
            
            phi_landscape[i, j] = max(0, whole_ent - part_ents)
    
    im = ax.pcolormesh(conn_grid, sizes_grid, phi_landscape, cmap='magma', shading='auto')
    ax.set_xlabel("Connectivity", fontsize=11)
    ax.set_ylabel("System Size (nodes)", fontsize=11)
    ax.set_title("Φ Landscape: Where Does Consciousness Emerge?", fontsize=12, fontweight='bold')
    plt.colorbar(im, ax=ax, label='Φ')
    
    # Mark "consciousness threshold" (hypothetical)
    ax.contour(conn_grid, sizes_grid, phi_landscape, levels=[np.percentile(phi_landscape, 80)], 
               colors='cyan', linewidths=2, linestyles='--')
    
    plt.suptitle("#025 Hard Problem — Experiment 2: Integrated Information (Φ)", 
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    path = os.path.join(OUTPUT_DIR, 'hard_problem_phi.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [OK] integrated_information -> {path}")
    return path


# ============================================================
# Experiment 3: The Explanatory Gap
# ============================================================

def explanatory_gap():
    """
    Visualize the explanatory gap: why physical descriptions
    of neural activity don't feel like they explain experience.
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # --- Panel 1: The Gap Itself ---
    ax = axes[0]
    
    # Left side: physical description
    physical_text = [
        "Physical Description",
        "─────────────────",
        "• Neuron #42,817 fires at 83 Hz",
        "• V4 area shows 12% BOLD increase",
        "• Glutamate binds to AMPA receptors",
        "• Synchronized gamma oscillation (40 Hz)",
        "• Prefrontal cortex activation +17%",
        "• Dopamine release in nucleus accumbens",
    ]
    
    # Right side: experience
    experience_text = [
        "Subjective Experience",
        "─────────────────────",
        "• The vivid redness of a rose",
        "• A sharp pang of nostalgia",
        "• The taste of dark chocolate",
        "• Feeling the warmth of sunlight",
        "• The sound of rain on a tin roof",
        "• A sudden flash of insight",
    ]
    
    y_positions = np.linspace(0.9, 0.1, len(physical_text))
    
    for i, (p_text, e_text) in enumerate(zip(physical_text, experience_text)):
        y = y_positions[i]
        ax.text(0.02, y, p_text, transform=ax.transAxes, fontsize=8, 
                fontfamily='monospace', verticalalignment='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#DFE6E9', alpha=0.8))
        ax.text(0.55, y, e_text, transform=ax.transAxes, fontsize=8, 
                fontfamily='monospace', verticalalignment='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#FAB1A0', alpha=0.8))
    
    # Draw the gap
    ax.axvline(x=0.5, color='red', linewidth=3, linestyle='--', alpha=0.7)
    ax.text(0.5, 0.95, "←── Explanatory Gap ──→", transform=ax.transAxes,
            ha='center', fontsize=10, fontweight='bold', color='red')
    ax.text(0.5, 0.05, '"Why does it feel like something?"', transform=ax.transAxes,
            ha='center', fontsize=9, fontstyle='italic', color='#636E72')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title("The Explanatory Gap", fontsize=12, fontweight='bold')
    
    # --- Panel 2: Philosophical Positions ---
    ax = axes[1]
    
    positions = [
        ("Physicalism", "Consciousness IS\nphysical activity", 0.8, 0.9, '#6C5CE7'),
        ("Panpsychism", "Consciousness is\nfundamental (like mass)", 0.5, 0.5, '#00B894'),
        ("Dualism", "Mind and matter\nare separate", 0.2, 0.3, '#E17055'),
        ("Illusionism", "Consciousness\ndoesn't exist", 0.8, 0.2, '#FDCB6E'),
        ("Idealism", "Only consciousness\nis real", 0.15, 0.8, '#FD79A8'),
        ("Mysterianism", "We can never\nunderstand it", 0.5, 0.1, '#636E72'),
    ]
    
    for name, desc, x, y, color in positions:
        circle = plt.Circle((x, y), 0.12, color=color, alpha=0.7, ec='white', linewidth=2)
        ax.add_patch(circle)
        ax.text(x, y, name, ha='center', va='center', fontsize=8, fontweight='bold', color='white')
        ax.text(x, y - 0.18, desc, ha='center', va='top', fontsize=6, color='#2D3436')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("Philosophical Positions on Consciousness", fontsize=12, fontweight='bold')
    ax.axis('off')
    
    # --- Panel 3: The Knowledge Argument (Mary's Room) ---
    ax = axes[2]
    
    # Mary's Room thought experiment
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Room
    room = plt.Rectangle((1, 1), 3, 8, fill=False, edgecolor='#636E72', linewidth=2, linestyle='--')
    ax.add_patch(room)
    ax.text(2.5, 9.2, "Mary's\nB&W Room", ha='center', fontsize=9, fontweight='bold')
    ax.text(2.5, 8.5, "Knows ALL\nphysical facts\nabout color", ha='center', fontsize=7, color='#636E72')
    
    # Books in room
    for i, y in enumerate([7, 6, 5, 4, 3, 2]):
        book = plt.Rectangle((1.5, y), 2, 0.6, fill=True, facecolor='#DFE6E9', edgecolor='#B2BEC3')
        ax.add_patch(book)
    
    # Arrow out
    ax.annotate('', xy=(7, 5), xytext=(4.2, 5),
                arrowprops=dict(arrowstyle='->', color='red', lw=2))
    ax.text(5.6, 5.3, "Sees red\nfor first time", ha='center', fontsize=8, color='red', fontweight='bold')
    
    # Outside world
    sun = plt.Circle((8, 8), 0.8, color='#FDCB6E', ec='none')
    ax.add_patch(sun)
    red_apple = plt.Circle((7.5, 4), 0.5, color='#FF0000', ec='none')
    ax.add_patch(red_apple)
    ax.text(7.5, 3.3, "Red Apple", ha='center', fontsize=7)
    
    # Question
    ax.text(5, 1, '"Does Mary learn something new?"', ha='center', fontsize=10, 
            fontstyle='italic', fontweight='bold', color='#2D3436',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFEAA7', alpha=0.8))
    
    ax.set_title("Mary's Room (Knowledge Argument)", fontsize=12, fontweight='bold')
    
    plt.suptitle("#025 Hard Problem — Experiment 3: The Explanatory Gap", 
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    path = os.path.join(OUTPUT_DIR, 'hard_problem_explanatory_gap.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [OK] explanatory_gap -> {path}")
    return path


# ============================================================
# Experiment 4: Emergence of Self-Model
# ============================================================

def self_model_emergence():
    """
    When does a system start modeling itself as "I"?
    Simulate agents that develop increasingly sophisticated self-models.
    """
    np.random.seed(42)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    # --- Panel 1: Self-Model Accuracy over Time ---
    ax = axes[0, 0]
    
    class SelfModelingAgent:
        def __init__(self, n_states=10):
            self.true_state = np.random.randn(n_states)
            self.self_model = np.zeros((n_states, n_states))  # Learns to predict self
            self.accuracy_history = []
            self.meta_accuracy = []  # How well it knows its own accuracy
            
        def act(self, t):
            # Action changes state
            action = np.random.randn(len(self.true_state)) * 0.3
            self.true_state = 0.9 * self.true_state + action
            
            # Predict own next state
            predicted = self.self_model @ self.true_state
            error = np.linalg.norm(predicted - self.true_state)
            
            # Update self-model (learn)
            lr = 0.01
            for i in range(len(self.true_state)):
                for j in range(len(self.true_state)):
                    self.self_model[i, j] += lr * (self.true_state[i] - predicted[i]) * self.true_state[j]
            
            # Meta: how accurate is my self-model?
            self.accuracy_history.append(1.0 / (1.0 + error))
            
            # Can it estimate its own accuracy? (meta-self-model)
            if len(self.accuracy_history) > 10:
                recent = self.accuracy_history[-10:]
                self.meta_accuracy.append(np.mean(recent))
            else:
                self.meta_accuracy.append(0)
            
            return error
    
    agents = [SelfModelingAgent(n_states=8) for _ in range(5)]
    colors = ['#6C5CE7', '#00B894', '#E17055', '#FDCB6E', '#FD79A8']
    
    for agent, color in zip(agents, colors):
        for t in range(500):
            agent.act(t)
        ax.plot(agent.accuracy_history, color=color, alpha=0.7, linewidth=1)
    
    ax.set_xlabel("Time Steps", fontsize=11)
    ax.set_ylabel("Self-Model Accuracy", fontsize=11)
    ax.set_title("Self-Model Learning Curves", fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0.8, color='green', linestyle='--', alpha=0.5, label='"I know myself" threshold')
    ax.legend(fontsize=8)
    
    # --- Panel 2: Self vs World Model Accuracy ---
    ax = axes[0, 1]
    
    class DualModelingAgent:
        def __init__(self, n_states=6):
            self.self_state = np.random.randn(n_states)
            self.world_state = np.random.randn(n_states)
            self.self_model = np.zeros((n_states, n_states))
            self.world_model = np.zeros((n_states, n_states))
            self.self_acc = []
            self.world_acc = []
            
        def step(self):
            # World changes independently
            self.world_state = 0.95 * self.world_state + np.random.randn(len(self.world_state)) * 0.2
            
            # Self changes based on world + internal
            self.self_state = 0.9 * self.self_state + 0.1 * self.world_state + np.random.randn(len(self.self_state)) * 0.1
            
            # Learn both models
            self_pred = self.self_model @ self.self_state
            world_pred = self.world_model @ self.world_state
            
            self_err = np.linalg.norm(self_pred - self.self_state)
            world_err = np.linalg.norm(world_pred - self.world_state)
            
            lr = 0.02
            for i in range(len(self.self_state)):
                for j in range(len(self.self_state)):
                    self.self_model[i, j] += lr * (self.self_state[i] - self_pred[i]) * self.self_state[j]
                    self.world_model[i, j] += lr * (self.world_state[i] - world_pred[i]) * self.world_state[j]
            
            self.self_acc.append(1.0 / (1.0 + self_err))
            self.world_acc.append(1.0 / (1.0 + world_err))
    
    agent = DualModelingAgent()
    for _ in range(400):
        agent.step()
    
    ax.plot(agent.self_acc, label='Self-Model', color='#6C5CE7', linewidth=2)
    ax.plot(agent.world_acc, label='World-Model', color='#E17055', linewidth=2)
    ax.set_xlabel("Time Steps", fontsize=11)
    ax.set_ylabel("Model Accuracy", fontsize=11)
    ax.set_title("Self-Model vs World-Model Accuracy", fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # --- Panel 3: Self-Awareness Spectrum ---
    ax = axes[1, 0]
    
    levels = [
        ("Reactive", "No self-model\nStimulus → Response", 0.1, '#DFE6E9'),
        ("Proprioceptive", "Body awareness\nInternal state sensing", 0.3, '#74B9FF'),
        ("Predictive", "Predicts own\nfuture states", 0.5, '#6C5CE7'),
        ("Reflective", "Models own\nmodeling process", 0.7, '#E17055'),
        ("Meta-Conscious", "Aware of being\naware", 0.9, '#D63031'),
    ]
    
    for name, desc, y, color in levels:
        bar = FancyBboxPatch((0.1, y - 0.06), 0.8, 0.12, 
                             boxstyle="round,pad=0.02", 
                             facecolor=color, alpha=0.8, ec='white', linewidth=1)
        ax.add_patch(bar)
        ax.text(0.5, y, f"{name}", ha='center', va='center', fontsize=10, 
                fontweight='bold', color='white')
        ax.text(0.5, y - 0.04, desc, ha='center', va='top', fontsize=7, color='white', alpha=0.9)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("Spectrum of Self-Awareness", fontsize=12, fontweight='bold')
    ax.axis('off')
    
    # --- Panel 4: Consciousness as Emergent Property ---
    ax = axes[1, 1]
    
    # Show how self-model accuracy relates to "consciousness indicators"
    n_agents = 50
    self_accuracies = []
    phi_estimates = []
    meta_scores = []
    
    for seed in range(n_agents):
        np.random.seed(seed)
        agent = SelfModelingAgent(n_states=6)
        for _ in range(300):
            agent.act(_)
        self_accuracies.append(np.mean(agent.accuracy_history[-50:]))
        phi_estimates.append(np.mean(agent.meta_accuracy[-50:]) if agent.meta_accuracy else 0)
        meta_scores.append(np.std(agent.accuracy_history[-50:]))  # Variability = meta-awareness?
    
    scatter = ax.scatter(self_accuracies, phi_estimates, c=meta_scores, 
                         cmap='plasma', s=60, alpha=0.7, edgecolors='white', linewidth=0.5)
    ax.set_xlabel("Self-Model Accuracy", fontsize=11)
    ax.set_ylabel("Meta-Awareness (Φ estimate)", fontsize=11)
    ax.set_title("Consciousness as Emergent Property", fontsize=12, fontweight='bold')
    plt.colorbar(scatter, ax=ax, label='Meta Variability')
    ax.grid(True, alpha=0.3)
    
    # Draw "consciousness zone"
    ax.axvspan(0.7, 1.0, alpha=0.1, color='green')
    ax.axhspan(0.6, 1.0, alpha=0.1, color='green')
    ax.text(0.85, 0.8, "Consciousness\nZone?", fontsize=9, color='green', 
            fontweight='bold', ha='center', alpha=0.7)
    
    plt.suptitle("#025 Hard Problem — Experiment 4: Emergence of Self-Model", 
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    path = os.path.join(OUTPUT_DIR, 'hard_problem_self_model.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [OK] self_model_emergence -> {path}")
    return path


# ============================================================
# Main
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("#025 Hard Problem of Consciousness — 4-in-1 Exploration")
    print("=" * 60)
    
    qualia_space()
    integrated_information()
    explanatory_gap()
    self_model_emergence()
    
    print("\n[OK] All 4 experiments complete!")
    print("  Key insight: Consciousness may be what it feels like")
    print("  to be a system that models itself modeling itself.")
