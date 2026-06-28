"""
Evolutionary Lenia V7 - Adaptive Kernel Switching
=================================================

Hypothesis: Switching between Pareto-optimal kernels during simulation
can achieve better composite fitness than any single static kernel.

Based on V6 Pareto front analysis, we discovered three kernel archetypes:
  1. Stability Specialist: stability=0.517, emergence=0.727, survival=65.7%
  2. Emergence Specialist: stability=0.444, emergence=1.328, survival=71.6%
  3. Balanced Generalist: stability=0.475, emergence=0.961, survival=64.4%

Phases:
  1. FORMATION (0-30%): Use stability kernel to establish pattern
  2. EXPLORATION (30-70%): Use emergence kernel for diversity
  3. STABILIZATION (70-100%): Use stability kernel for maintenance

Detection based on:
  - Simulation progress (time-based switching)
  - Survival rate trajectory
  - Diversity trajectory
"""

import jax
import jax.numpy as jnp
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any, Callable
import json
import time

# Import from V4 adaptive for MultiRingGenome
from evolutionary_lenia_v4_adaptive import (
    MultiRingGenome,
    RingParams,
    polynomial_bump,
    gaussian_bump,
)

# Import from V3 for fitness functions and seed
from evolutionary_lenia_v3_hybrid import (
    compute_hybrid_fitness,
    HybridFitnessResult,
    compute_emergence_metrics,
    EmergenceMetrics,
    get_seed,
)


# ============================================================================
# Pareto-Optimal Kernels (from V6 analysis)
# ============================================================================

def get_stability_kernel() -> MultiRingGenome:
    """
    Stability Specialist kernel from V6 Pareto front.
    
    Characterized by:
      - Higher stability (0.517)
      - Moderate emergence (0.727)
      - Good survival (65.7%)
      - Strong persistence (78.7%)
    """
    params = np.array([
        0.5294395685195923,   # r1: inner radius
        0.10283151268959045,  # w1: inner width
        1.2357608079910278,   # b1: inner weight (strong excitatory)
        0.9724768996238708,   # r2: outer radius
        0.15194140374660492,  # w2: outer width
        -0.12735438346862793, # b2: outer weight (mild inhibitory)
    ])
    return MultiRingGenome.from_param_vector(params, 'polynomial')


def get_emergence_kernel() -> MultiRingGenome:
    """
    Emergence Specialist kernel from V6 Pareto front.
    
    Characterized by:
      - Lower stability (0.444)
      - Highest emergence (1.328)
      - Highest survival (71.6%)
      - High diversity (3.72)
    """
    params = np.array([
        0.6073603630065918,   # r1: inner radius
        0.10283151268959045,  # w1: inner width
        1.0,                  # b1: inner weight (moderate excitatory)
        0.8360034227371216,   # r2: outer radius
        0.10779233276844025,  # w2: outer width
        -0.28860318660736084, # b2: outer weight (strong inhibitory)
    ])
    return MultiRingGenome.from_param_vector(params, 'polynomial')


def get_balanced_kernel() -> MultiRingGenome:
    """
    Balanced Generalist kernel from V6 Pareto front.
    
    Characterized by:
      - Moderate stability (0.475)
      - Moderate emergence (0.961)
      - Good survival (64.4%)
      - Balance between stability and dynamics
    """
    params = np.array([
        0.6073603630065918,   # r1: inner radius
        0.10283151268959045,  # w1: inner width
        1.0,                  # b1: inner weight
        0.7261261343955994,   # r2: outer radius
        0.15194140374660492,  # w2: outer width
        -0.07339548319578171, # b2: outer weight (weak inhibitory)
    ])
    return MultiRingGenome.from_param_vector(params, 'polynomial')


# ============================================================================
# Adaptive Kernel Manager
# ============================================================================

@dataclass
class PhaseMetrics:
    """Metrics tracked during simulation for phase detection."""
    survival: float
    diversity: float
    complexity: float
    phase: str


class AdaptiveKernelManager:
    """
    Manages kernel switching during simulation.
    
    Strategies:
      1. 'time_based': Switch at fixed time intervals
      2. 'metric_based': Switch based on survival/diversity metrics
      3. 'hybrid': Combine time and metric triggers
    """
    
    def __init__(self, strategy: str = 'time_based'):
        self.strategy = strategy
        
        # Pre-compute kernel FFTs for fast switching
        self.stability_kernel = get_stability_kernel()
        self.emergence_kernel = get_emergence_kernel()
        self.balanced_kernel = get_balanced_kernel()
        
        # Phase boundaries (for time-based switching)
        self.formation_end = 0.30    # 0-30%: Formation
        self.exploration_end = 0.70  # 30-70%: Exploration
        
        # Current state
        self.current_phase = 'formation'
        self.switch_history = []
    
    def get_kernel_fft(self, kernel: MultiRingGenome, R: int, size: int) -> jnp.ndarray:
        """Get FFT of kernel."""
        return kernel.to_kernel_fft(R, size)
    
    def detect_phase(self, 
                     progress: float, 
                     survival: float, 
                     diversity: float,
                     complexity: float) -> str:
        """
        Detect current phase based on strategy.
        
        Returns: 'formation', 'exploration', or 'stabilization'
        """
        if self.strategy == 'time_based':
            # Pure time-based switching
            if progress < self.formation_end:
                return 'formation'
            elif progress < self.exploration_end:
                return 'exploration'
            else:
                return 'stabilization'
        
        elif self.strategy == 'metric_based':
            # Metric-based switching
            # Formation: survival < 0.5 or complexity < 0.3
            # Exploration: diversity < 3.0
            # Stabilization: survival > 0.6
            
            if survival < 0.5 or complexity < 0.3:
                return 'formation'
            elif diversity < 3.0 and survival > 0.5:
                return 'exploration'
            elif survival > 0.6:
                return 'stabilization'
            else:
                return 'exploration'  # Default to exploration
        
        else:  # hybrid
            # Combine time and metric signals
            if progress < self.formation_end:
                return 'formation'
            elif progress > self.exploration_end:
                return 'stabilization'
            else:
                # In exploration zone, use metrics
                if diversity < 3.0:
                    return 'exploration'
                else:
                    return 'stabilization'
    
    def select_kernel(self, phase: str) -> MultiRingGenome:
        """Select appropriate kernel for phase."""
        if phase == 'formation':
            return self.stability_kernel  # Establish pattern
        elif phase == 'exploration':
            return self.emergence_kernel  # Generate diversity
        else:  # stabilization
            return self.stability_kernel  # Maintain pattern
    
    def record_switch(self, step: int, old_phase: str, new_phase: str):
        """Record phase transition."""
        if old_phase != new_phase:
            self.switch_history.append({
                'step': step,
                'from': old_phase,
                'to': new_phase,
            })


# ============================================================================
# Adaptive Lenia Simulator
# ============================================================================

class AdaptiveLeniaSimulator:
    """
    Lenia simulator with adaptive kernel switching.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.size = config['grid_size']
        self.R = config['kernel_radius']
        self.mu = config['mu']
        self.sigma = config['sigma']
        self.dt = config['dt']
        self.steps = config['sim_steps']
        
        # Adaptive kernel manager
        self.adaptive_manager = AdaptiveKernelManager(
            strategy=config.get('switching_strategy', 'time_based')
        )
    
    def compute_metrics(self, grid: np.ndarray, history: List[np.ndarray]) -> Tuple[float, float, float]:
        """Compute survival, diversity, and complexity metrics."""
        # Survival: fraction of mass retained
        current_mass = float(grid.sum())
        initial_mass = float(history[0].sum()) if history else current_mass
        survival = min(1.0, current_mass / (initial_mass + 1e-8))
        
        # Diversity: entropy of mass distribution
        flat = grid.flatten()
        hist, _ = np.histogram(flat, bins=10, range=(0, 1))
        hist = hist / (hist.sum() + 1e-8)
        diversity = float(-(hist * np.log(hist + 1e-8)).sum())
        
        # Complexity: edge density
        grad_y = np.abs(np.diff(grid, axis=0))
        grad_x = np.abs(np.diff(grid, axis=1))
        grad_y = np.pad(grad_y, ((0, 1), (0, 0)))
        grad_x = np.pad(grad_x, ((0, 0), (0, 1)))
        complexity = float(np.sqrt(grad_y**2 + grad_x**2).mean())
        
        return survival, diversity, complexity
    
    def run_adaptive(self, seed_name: str, verbose: bool = False) -> Dict[str, Any]:
        """
        Run simulation with adaptive kernel switching.
        
        Returns dictionary with:
          - history: list of grids
          - phase_history: list of phases at each snapshot
          - kernel_history: list of kernels used
          - metrics_history: list of PhaseMetrics
          - switch_events: list of phase switches
        """
        # Initialize
        seed = get_seed(seed_name, self.size)
        grid = jnp.array(seed)
        
        history = [np.array(grid)]
        phase_history = [self.adaptive_manager.current_phase]
        kernel_history = []
        metrics_history = []
        
        current_kernel = self.adaptive_manager.select_kernel(self.adaptive_manager.current_phase)
        kernel_fft = current_kernel.to_kernel_fft(self.R, self.size)
        
        # Run simulation
        for step in range(self.steps):
            progress = step / self.steps
            
            # Compute metrics every 10 steps
            if step % 10 == 0:
                survival, diversity, complexity = self.compute_metrics(
                    np.array(grid), history
                )
                
                # Detect phase
                old_phase = self.adaptive_manager.current_phase
                new_phase = self.adaptive_manager.detect_phase(
                    progress, survival, diversity, complexity
                )
                
                # Record switch if phase changed
                self.adaptive_manager.record_switch(step, old_phase, new_phase)
                
                if new_phase != old_phase:
                    if verbose:
                        print(f"  Step {step}: Phase change {old_phase} -> {new_phase}")
                    
                    # Switch kernel
                    self.adaptive_manager.current_phase = new_phase
                    current_kernel = self.adaptive_manager.select_kernel(new_phase)
                    kernel_fft = current_kernel.to_kernel_fft(self.R, self.size)
                
                # Record metrics
                metrics_history.append(PhaseMetrics(
                    survival=survival,
                    diversity=diversity,
                    complexity=complexity,
                    phase=new_phase,
                ))
            
            # Lenia update step
            grid_fft = jnp.fft.fft2(grid)
            conv = jnp.fft.ifft2(grid_fft * kernel_fft).real
            growth = jnp.exp(-((conv - self.mu) ** 2) / (2 * self.sigma ** 2)) * 2 - 1
            grid = jnp.clip(grid + self.dt * growth, 0, 1)
            
            # Record history periodically
            if step % 20 == 0:
                history.append(np.array(grid))
                phase_history.append(self.adaptive_manager.current_phase)
                kernel_history.append(self.adaptive_manager.current_phase)
        
        history.append(np.array(grid))
        
        return {
            'history': history,
            'phase_history': phase_history,
            'kernel_history': kernel_history,
            'metrics_history': metrics_history,
            'switch_events': self.adaptive_manager.switch_history.copy(),
        }
    
    def run_static(self, seed_name: str, kernel: MultiRingGenome) -> List[np.ndarray]:
        """Run simulation with static kernel."""
        kernel_fft = kernel.to_kernel_fft(self.R, self.size)
        seed = get_seed(seed_name, self.size)
        
        grid = jnp.array(seed)
        history = [np.array(grid)]
        
        for step in range(self.steps):
            grid_fft = jnp.fft.fft2(grid)
            conv = jnp.fft.ifft2(grid_fft * kernel_fft).real
            growth = jnp.exp(-((conv - self.mu) ** 2) / (2 * self.sigma ** 2)) * 2 - 1
            grid = jnp.clip(grid + self.dt * growth, 0, 1)
            
            if step % 20 == 0:
                history.append(np.array(grid))
        
        history.append(np.array(grid))
        return history


# ============================================================================
# Experiment Runner
# ============================================================================

@dataclass
class ExperimentResult:
    """Results from one experiment run."""
    seed_name: str
    random_seed: int
    strategy: str
    
    # Fitness scores
    adaptive_fitness: float
    stability_fitness: float
    emergence_fitness: float
    balanced_fitness: float
    
    # Detailed results
    adaptive_result: Dict[str, Any]
    
    # Metrics
    phase_distribution: Dict[str, float]
    switch_count: int


def run_single_experiment(config: Dict[str, Any], 
                          random_seed: int, 
                          verbose: bool = False) -> ExperimentResult:
    """Run a single experiment comparing adaptive vs static kernels."""
    
    # Set random seed
    np.random.seed(random_seed)
    
    # Create simulator
    simulator = AdaptiveLeniaSimulator(config)
    seed_name = config['seeds'][0]  # Use first seed
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Running experiment (seed={random_seed})")
        print(f"{'='*60}")
    
    # 1. Run with adaptive switching
    if verbose:
        print("\n[1] Running ADAPTIVE kernel switching...")
    
    adaptive_result = simulator.run_adaptive(seed_name, verbose=verbose)
    adaptive_fitness = compute_hybrid_fitness(adaptive_result['history'], alpha=0.5).hybrid_fitness
    
    if verbose:
        print(f"    Adaptive fitness: {adaptive_fitness:.6f}")
        print(f"    Phase switches: {len(adaptive_result['switch_events'])}")
    
    # 2. Run with static stability kernel
    if verbose:
        print("\n[2] Running STATIC STABILITY kernel...")
    
    stability_history = simulator.run_static(seed_name, get_stability_kernel())
    stability_fitness = compute_hybrid_fitness(stability_history, alpha=0.5).hybrid_fitness
    
    if verbose:
        print(f"    Stability fitness: {stability_fitness:.6f}")
    
    # 3. Run with static emergence kernel
    if verbose:
        print("\n[3] Running STATIC EMERGENCE kernel...")
    
    emergence_history = simulator.run_static(seed_name, get_emergence_kernel())
    emergence_fitness = compute_hybrid_fitness(emergence_history, alpha=0.5).hybrid_fitness
    
    if verbose:
        print(f"    Emergence fitness: {emergence_fitness:.6f}")
    
    # 4. Run with static balanced kernel
    if verbose:
        print("\n[4] Running STATIC BALANCED kernel...")
    
    balanced_history = simulator.run_static(seed_name, get_balanced_kernel())
    balanced_fitness = compute_hybrid_fitness(balanced_history, alpha=0.5).hybrid_fitness
    
    if verbose:
        print(f"    Balanced fitness: {balanced_fitness:.6f}")
    
    # Compute phase distribution
    phase_counts = {'formation': 0, 'exploration': 0, 'stabilization': 0}
    for phase in adaptive_result['phase_history']:
        phase_counts[phase] = phase_counts.get(phase, 0) + 1
    
    total_phases = sum(phase_counts.values())
    phase_distribution = {k: v / (total_phases + 1e-8) for k, v in phase_counts.items()}
    
    return ExperimentResult(
        seed_name=seed_name,
        random_seed=random_seed,
        strategy=config['switching_strategy'],
        adaptive_fitness=adaptive_fitness,
        stability_fitness=stability_fitness,
        emergence_fitness=emergence_fitness,
        balanced_fitness=balanced_fitness,
        adaptive_result=adaptive_result,
        phase_distribution=phase_distribution,
        switch_count=len(adaptive_result['switch_events']),
    )


def run_experiment_suite(config: Dict[str, Any], 
                         num_seeds: int = 10) -> List[ExperimentResult]:
    """Run experiment across multiple random seeds."""
    
    results = []
    
    for i in range(num_seeds):
        random_seed = 42 + i * 100
        result = run_single_experiment(config, random_seed, verbose=config['verbose'])
        results.append(result)
    
    return results


# ============================================================================
# Analysis and Visualization
# ============================================================================

def analyze_results(results: List[ExperimentResult], 
                    output_dir: Path) -> Dict[str, Any]:
    """Analyze and visualize experiment results."""
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Aggregate statistics
    adaptive_scores = [r.adaptive_fitness for r in results]
    stability_scores = [r.stability_fitness for r in results]
    emergence_scores = [r.emergence_fitness for r in results]
    balanced_scores = [r.balanced_fitness for r in results]
    
    analysis = {
        'num_experiments': len(results),
        'strategy': results[0].strategy,
        'adaptive': {
            'mean': float(np.mean(adaptive_scores)),
            'std': float(np.std(adaptive_scores)),
            'min': float(np.min(adaptive_scores)),
            'max': float(np.max(adaptive_scores)),
        },
        'static_stability': {
            'mean': float(np.mean(stability_scores)),
            'std': float(np.std(stability_scores)),
        },
        'static_emergence': {
            'mean': float(np.mean(emergence_scores)),
            'std': float(np.std(emergence_scores)),
        },
        'static_balanced': {
            'mean': float(np.mean(balanced_scores)),
            'std': float(np.std(balanced_scores)),
        },
        'improvement_vs_stability': float(np.mean(adaptive_scores) - np.mean(stability_scores)),
        'improvement_vs_emergence': float(np.mean(adaptive_scores) - np.mean(emergence_scores)),
        'improvement_vs_balanced': float(np.mean(adaptive_scores) - np.mean(balanced_scores)),
    }
    
    # Print summary
    print(f"\n{'='*70}")
    print("RESULTS SUMMARY")
    print(f"{'='*70}")
    print(f"\nStrategy: {analysis['strategy']}")
    print(f"Experiments: {analysis['num_experiments']}")
    print(f"\nFitness Scores (mean ± std):")
    print(f"  Adaptive:         {analysis['adaptive']['mean']:.6f} ± {analysis['adaptive']['std']:.6f}")
    print(f"  Static Stability: {analysis['static_stability']['mean']:.6f} ± {analysis['static_stability']['std']:.6f}")
    print(f"  Static Emergence: {analysis['static_emergence']['mean']:.6f} ± {analysis['static_emergence']['std']:.6f}")
    print(f"  Static Balanced:  {analysis['static_balanced']['mean']:.6f} ± {analysis['static_balanced']['std']:.6f}")
    print(f"\nImprovement (adaptive - static):")
    print(f"  vs Stability:  {analysis['improvement_vs_stability']:+.6f}")
    print(f"  vs Emergence:  {analysis['improvement_vs_emergence']:+.6f}")
    print(f"  vs Balanced:   {analysis['improvement_vs_balanced']:+.6f}")
    
    # Determine best approach
    best_static = max(
        analysis['static_stability']['mean'],
        analysis['static_emergence']['mean'],
        analysis['static_balanced']['mean']
    )
    
    if analysis['adaptive']['mean'] > best_static:
        print(f"\n[OK] ADAPTIVE OUTPERFORMS all static kernels!")
        analysis['winner'] = 'adaptive'
    else:
        print(f"\n[X] Static kernel outperforms adaptive")
        analysis['winner'] = 'static'
    
    # Save analysis
    with open(output_dir / 'analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2)
    
    # Create visualizations
    create_visualizations(results, output_dir)
    
    return analysis


def create_visualizations(results: List[ExperimentResult], output_dir: Path):
    """Create comparison plots."""
    
    # Plot 1: Fitness comparison box plot
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # Extract data
    adaptive_scores = [r.adaptive_fitness for r in results]
    stability_scores = [r.stability_fitness for r in results]
    emergence_scores = [r.emergence_fitness for r in results]
    balanced_scores = [r.balanced_fitness for r in results]
    
    # Plot 1: Box plot comparison
    ax = axes[0, 0]
    data = [adaptive_scores, stability_scores, emergence_scores, balanced_scores]
    labels = ['Adaptive', 'Stability\n(static)', 'Emergence\n(static)', 'Balanced\n(static)']
    bp = ax.boxplot(data, tick_labels=labels, patch_artist=True)
    colors = ['#2ecc71', '#3498db', '#e74c3c', '#9b59b6']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax.set_ylabel('Hybrid Fitness', fontsize=11)
    ax.set_title('Fitness Comparison', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Plot 2: Per-experiment comparison
    ax = axes[0, 1]
    x = range(len(results))
    ax.plot(x, adaptive_scores, 'g-o', linewidth=2, markersize=8, label='Adaptive')
    ax.plot(x, stability_scores, 'b-s', linewidth=1.5, markersize=6, alpha=0.7, label='Stability')
    ax.plot(x, emergence_scores, 'r-^', linewidth=1.5, markersize=6, alpha=0.7, label='Emergence')
    ax.plot(x, balanced_scores, 'm-d', linewidth=1.5, markersize=6, alpha=0.7, label='Balanced')
    ax.set_xlabel('Experiment Index', fontsize=11)
    ax.set_ylabel('Hybrid Fitness', fontsize=11)
    ax.set_title('Per-Experiment Fitness', fontsize=12, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    # Plot 3: Improvement histogram
    ax = axes[0, 2]
    improvements_vs_stability = [a - s for a, s in zip(adaptive_scores, stability_scores)]
    improvements_vs_emergence = [a - e for a, e in zip(adaptive_scores, emergence_scores)]
    improvements_vs_balanced = [a - b for a, b in zip(adaptive_scores, balanced_scores)]
    
    bins = np.linspace(-0.05, 0.15, 20)
    ax.hist(improvements_vs_stability, bins=bins, alpha=0.6, label='vs Stability', color='blue')
    ax.hist(improvements_vs_emergence, bins=bins, alpha=0.6, label='vs Emergence', color='red')
    ax.hist(improvements_vs_balanced, bins=bins, alpha=0.6, label='vs Balanced', color='purple')
    ax.axvline(x=0, color='black', linestyle='--', linewidth=2, label='No improvement')
    ax.set_xlabel('Fitness Improvement', fontsize=11)
    ax.set_ylabel('Count', fontsize=11)
    ax.set_title('Adaptive Improvement Distribution', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 4: Phase distribution
    ax = axes[1, 0]
    phase_data = {
        'formation': [],
        'exploration': [],
        'stabilization': [],
    }
    for r in results:
        for phase in ['formation', 'exploration', 'stabilization']:
            phase_data[phase].append(r.phase_distribution.get(phase, 0))
    
    x = np.arange(len(results))
    width = 0.25
    
    ax.bar(x - width, phase_data['formation'], width, label='Formation', color='#3498db')
    ax.bar(x, phase_data['exploration'], width, label='Exploration', color='#e74c3c')
    ax.bar(x + width, phase_data['stabilization'], width, label='Stabilization', color='#2ecc71')
    
    ax.set_xlabel('Experiment Index', fontsize=11)
    ax.set_ylabel('Phase Proportion', fontsize=11)
    ax.set_title('Phase Distribution', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    # Plot 5: Switch count distribution
    ax = axes[1, 1]
    switch_counts = [r.switch_count for r in results]
    ax.hist(switch_counts, bins=range(max(switch_counts)+2), color='#9b59b6', alpha=0.7, edgecolor='black')
    ax.set_xlabel('Number of Phase Switches', fontsize=11)
    ax.set_ylabel('Count', fontsize=11)
    ax.set_title('Phase Switch Distribution', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Plot 6: Detailed trajectory for best adaptive result
    ax = axes[1, 2]
    best_idx = np.argmax(adaptive_scores)
    best_result = results[best_idx]
    
    # Plot metrics over time
    if best_result.adaptive_result['metrics_history']:
        metrics = best_result.adaptive_result['metrics_history']
        steps = np.arange(len(metrics)) * 10  # Metrics computed every 10 steps
        
        ax.plot(steps, [m.survival for m in metrics], 'b-', linewidth=2, label='Survival')
        ax.plot(steps, [m.diversity / 5.0 for m in metrics], 'r-', linewidth=2, label='Diversity/5')
        ax.plot(steps, [m.complexity * 10 for m in metrics], 'g-', linewidth=2, label='Complexity×10')
        
        # Mark phase changes
        for event in best_result.adaptive_result['switch_events']:
            ax.axvline(x=event['step'], color='purple', linestyle='--', alpha=0.5)
        
        ax.set_xlabel('Simulation Step', fontsize=11)
        ax.set_ylabel('Metric Value', fontsize=11)
        ax.set_title('Best Adaptive Trajectory', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.suptitle(
        'Evolutionary Lenia V7 - Adaptive Kernel Switching Results',
        fontsize=14, fontweight='bold', y=1.02
    )
    plt.tight_layout()
    
    plot_path = output_dir / 'v7_comparison.png'
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\n[OK] Visualization saved to {plot_path}")
    
    # Additional plot: Kernel visualization
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    R = 15
    y, x = np.ogrid[-R:R+1, -R:R+1]
    r_norm = np.sqrt(x*x + y*y) / R
    
    kernels = [
        (get_stability_kernel(), 'Stability Kernel', axes[0]),
        (get_emergence_kernel(), 'Emergence Kernel', axes[1]),
        (get_balanced_kernel(), 'Balanced Kernel', axes[2]),
    ]
    
    for kernel, title, ax in kernels:
        r1_scaled = (r_norm - kernel.ring1.radius) / (kernel.ring1.width + 1e-8)
        r2_scaled = (r_norm - kernel.ring2.radius) / (kernel.ring2.width + 1e-8)
        
        k1 = kernel.ring1.weight * polynomial_bump(r1_scaled)
        k2 = kernel.ring2.weight * polynomial_bump(r2_scaled)
        
        kernel_2d = (k1 + k2) * (r_norm <= 1.0)
        
        im = ax.imshow(kernel_2d, cmap='RdBu_r', aspect='equal')
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.axis('off')
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    
    plt.suptitle('Pareto-Optimal Kernels from V6', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    kernel_plot_path = output_dir / 'kernel_comparison.png'
    plt.savefig(kernel_plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"[OK] Kernel visualization saved to {kernel_plot_path}")


def save_detailed_results(results: List[ExperimentResult], output_dir: Path):
    """Save detailed results for further analysis."""
    
    # Convert to serializable format
    results_data = []
    for r in results:
        d = {
            'seed_name': r.seed_name,
            'random_seed': r.random_seed,
            'strategy': r.strategy,
            'adaptive_fitness': r.adaptive_fitness,
            'stability_fitness': r.stability_fitness,
            'emergence_fitness': r.emergence_fitness,
            'balanced_fitness': r.balanced_fitness,
            'phase_distribution': r.phase_distribution,
            'switch_count': r.switch_count,
            'switch_events': r.adaptive_result['switch_events'],
        }
        results_data.append(d)
    
    with open(output_dir / 'detailed_results.json', 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"[OK] Detailed results saved to {output_dir / 'detailed_results.json'}")


# ============================================================================
# Main Experiment
# ============================================================================

def create_v7_config() -> Dict[str, Any]:
    """Create configuration for V7 experiment."""
    return {
        # Simulation
        'grid_size': 128,
        'kernel_radius': 15,
        'mu': 0.12,            # V6 parameter (was 0.1622)
        'sigma': 0.05,         # V6 parameter (was 0.0257)
        'dt': 0.1,
        'sim_steps': 500,
        
        # Seeds
        'seeds': ['orbium'],
        
        # Adaptive switching
        'switching_strategy': 'time_based',  # 'time_based', 'metric_based', 'hybrid'
        
        # Experiment
        'num_seeds': 10,
        'verbose': True,
        
        # Output
        'output_dir': 'output/evo_lenia_v7_adaptive',
    }


def main():
    """Run V7 adaptive kernel switching experiment."""
    
    print("="*70)
    print("Evolutionary Lenia V7 - Adaptive Kernel Switching")
    print("="*70)
    print("""
Hypothesis: Switching between Pareto-optimal kernels during simulation
can achieve better composite fitness than any single static kernel.

Three kernel archetypes from V6 Pareto front:
  1. Stability Specialist: stability=0.517, emergence=0.727
  2. Emergence Specialist: stability=0.444, emergence=1.328
  3. Balanced Generalist: stability=0.475, emergence=0.961

Phase strategy:
  - FORMATION (0-30%): Stability kernel
  - EXPLORATION (30-70%): Emergence kernel
  - STABILIZATION (70-100%): Stability kernel
""")
    
    config = create_v7_config()
    output_dir = Path(config['output_dir'])
    
    print(f"Configuration:")
    print(f"  Grid size: {config['grid_size']}")
    print(f"  Simulation steps: {config['sim_steps']}")
    print(f"  Seeds: {config['seeds']}")
    print(f"  Strategy: {config['switching_strategy']}")
    print(f"  Number of runs: {config['num_seeds']}")
    print()
    
    # Run experiments
    print(f"\n{'='*70}")
    print("Running experiment suite...")
    print(f"{'='*70}")
    
    t0 = time.time()
    results = run_experiment_suite(config, num_seeds=config['num_seeds'])
    elapsed = time.time() - t0
    
    print(f"\n[OK] Experiment suite completed in {elapsed:.1f}s")
    
    # Analyze results
    analysis = analyze_results(results, output_dir)
    
    # Save detailed results
    save_detailed_results(results, output_dir)
    
    # Save config
    with open(output_dir / 'config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    # Final summary
    print(f"\n{'='*70}")
    print("FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"\nWinner: {analysis['winner'].upper()}")
    print(f"\nAdaptive mean fitness: {analysis['adaptive']['mean']:.6f}")
    print(f"Best static mean: {max(analysis['static_stability']['mean'], analysis['static_emergence']['mean'], analysis['static_balanced']['mean']):.6f}")
    print(f"\nImprovement over best static: {analysis['adaptive']['mean'] - max(analysis['static_stability']['mean'], analysis['static_emergence']['mean'], analysis['static_balanced']['mean']):+.6f}")
    
    if analysis['winner'] == 'adaptive':
        print("\n[OK] HYPOTHESIS CONFIRMED: Adaptive kernel switching outperforms static kernels!")
    else:
        print("\n[X] HYPOTHESIS REJECTED: Static kernel performs better")
    
    print(f"\nResults saved to: {output_dir}/")
    print(f"\n{'='*70}")
    print("Done!")
    
    return results, analysis


if __name__ == '__main__':
    results, analysis = main()
