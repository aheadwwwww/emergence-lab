"""
Hybrid Learnable Lenia: Combining V7 Evolved Parameters with Gradient-Based Kernel Refinement
Cycle 4 - Building on V8 GNN discoveries and V6 Pareto front
"""
import numpy as np
import sys
import json
from pathlib import Path
from datetime import datetime

# Import existing evolutionary Lenia infrastructure
sys.path.insert(0, str(Path(__file__).parent))
from evolutionary_lenia import (
    LeniaSystem, LeniaEvolver, EvolutionaryTrial,
    create_population_from_archetype, PARETO_ARCHETYPES
)

class LearnableKernelLayer:
    """Neural network-inspired learnable kernel component"""
    def __init__(self, base_mu, base_sigma, base_k=1, learning_rate=0.01):
        self.base_mu = base_mu
        self.base_sigma = base_sigma
        self.base_k = base_k
        
        # Learnable perturbations (small initial values)
        self.delta_mu = 0.0
        self.delta_sigma = 0.0
        self.delta_k = 0.0
        
        # Gradient accumulators
        self.grad_mu = 0.0
        self.grad_sigma = 0.0
        self.grad_k = 0.0
        
        self.learning_rate = learning_rate
        self.momentum = 0.9
        self.velocity_mu = 0.0
        self.velocity_sigma = 0.0
        
    def get_parameters(self):
        """Get current parameters with learnable perturbations"""
        return {
            'mu': np.clip(self.base_mu + self.delta_mu, 0.01, 0.5),
            'sigma': max(0.001, self.base_sigma + self.delta_sigma),
            'k': max(1, int(round(self.base_k + self.delta_k)))
        }
    
    def compute_gradients(self, fitness_score, survival_score, complexity_score):
        """
        Compute pseudo-gradients using finite differences approach
        Based on sensitivity analysis of Lenia dynamics
        """
        # Higher fitness → reinforce current direction
        # Lower fitness → explore alternatives
        
        # Survival gradient: stronger signal for stability
        survival_grad = (survival_score - 0.5) * 0.001
        
        # Complexity gradient: encourage pattern richness
        complexity_grad = (complexity_score - 1.0) * 0.0005
        
        # Combined gradient with momentum
        self.grad_mu = survival_grad + complexity_grad
        self.grad_sigma = -survival_grad * 0.5  # Negative: higher survival with lower sigma
        
        return self.grad_mu, self.grad_sigma
    
    def apply_gradients(self):
        """Apply gradients with momentum optimizer"""
        self.velocity_mu = self.momentum * self.velocity_mu + self.learning_rate * self.grad_mu
        self.velocity_sigma = self.momentum * self.velocity_sigma + self.learning_rate * self.grad_sigma
        
        self.delta_mu += self.velocity_mu
        self.delta_sigma += self.velocity_sigma
        
        # Clamp perturbations to reasonable range
        self.delta_mu = np.clip(self.delta_mu, -0.1, 0.1)
        self.delta_sigma = np.clip(self.delta_sigma, -0.05, 0.05)
        
        # Reset gradients
        self.grad_mu = 0.0
        self.grad_sigma = 0.0

class HybridEvolutionaryLearner:
    """
    Combines evolutionary search (V7) with gradient-based refinement
    Key insight from V8: Different architectures need different parameter ranges
    """
    def __init__(self, population_size=30, generations=20, learning_steps=5):
        self.population_size = population_size
        self.generations = generations
        self.learning_steps = learning_steps
        
        # V7 evolved parameters as base (from state file)
        self.v7_params = {
            'mu': 0.135,
            'sigma': 0.074,
            'R': 13,
            'T': 10,
            'k': 1
        }
        
        # V6 Pareto archetypes for diversity
        self.archetypes = PARETO_ARCHETYPES
        
        # Tracking
        self.learning_history = []
        self.best_hybrid = None
        
    def initialize_hybrid_population(self):
        """Create population mixing evolved and learnable components"""
        population = []
        
        # 1/3 from V7 parameters with learnable layer
        for i in range(self.population_size // 3):
            layer = LearnableKernelLayer(
                self.v7_params['mu'],
                self.v7_params['sigma'],
                self.v7_params['k']
            )
            # Add small random perturbation for diversity
            layer.delta_mu = np.random.uniform(-0.02, 0.02)
            layer.delta_sigma = np.random.uniform(-0.01, 0.01)
            population.append({
                'type': 'v7_learnable',
                'layer': layer,
                'params': layer.get_parameters(),
                'fitness': 0.0
            })
        
        # 1/3 from Pareto archetypes
        for i, (name, archetype) in enumerate(self.archetypes.items()):
            if i >= self.population_size // 3:
                break
            layer = LearnableKernelLayer(
                archetype['mu'],
                archetype['sigma'],
                archetype.get('k', 1)
            )
            population.append({
                'type': f'archetype_{name}',
                'layer': layer,
                'params': layer.get_parameters(),
                'fitness': 0.0
            })
        
        # 1/3 random exploration
        remaining = self.population_size - len(population)
        for i in range(remaining):
            # Sample from V8 insight: wider sigma for stability
            mu = np.random.uniform(0.1, 0.2)
            sigma = np.random.uniform(0.03, 0.1)  # V8 showed σ≥0.025 is critical
            layer = LearnableKernelLayer(mu, sigma, 1)
            population.append({
                'type': 'random_explore',
                'layer': layer,
                'params': layer.get_parameters(),
                'fitness': 0.0
            })
        
        return population
    
    def hybrid_evaluate(self, individual):
        """Evaluate individual using Lenia system"""
        params = individual['params']
        
        # Create Lenia system with these parameters
        ls = LeniaSystem(
            mu=params['mu'],
            sigma=params['sigma'],
            R=self.v7_params['R'],
            T=self.v7_params['T'],
            k=params['k']
        )
        
        # Run simulation
        trial = EvolutionaryTrial(ls, max_steps=200)
        results = trial.run()
        
        return results
    
    def hybrid_step(self, population):
        """One generation of hybrid evolution + learning"""
        # Phase 1: Evaluate all individuals
        for individual in population:
            results = self.hybrid_evaluate(individual)
            individual['fitness'] = results['fitness']
            individual['survival'] = results['survival']
            individual['complexity'] = results['complexity']
        
        # Phase 2: Learning step for learnable individuals
        for individual in population:
            if 'layer' in individual:
                layer = individual['layer']
                layer.compute_gradients(
                    individual['fitness'],
                    individual['survival'],
                    individual['complexity']
                )
                layer.apply_gradients()
                individual['params'] = layer.get_parameters()
        
        # Phase 3: Selection and variation (evolutionary)
        population.sort(key=lambda x: x['fitness'], reverse=True)
        
        # Track best
        if self.best_hybrid is None or population[0]['fitness'] > self.best_hybrid['fitness']:
            self.best_hybrid = population[0].copy()
        
        # Elitism + mutation
        elite_count = self.population_size // 4
        new_population = population[:elite_count]
        
        # Fill rest with mutations of top performers
        while len(new_population) < self.population_size:
            parent = population[np.random.randint(0, elite_count)]
            child_layer = LearnableKernelLayer(
                parent['params']['mu'],
                parent['params']['sigma'],
                parent['params'].get('k', 1)
            )
            # Mutation
            child_layer.delta_mu = parent['layer'].delta_mu + np.random.uniform(-0.02, 0.02)
            child_layer.delta_sigma = parent['layer'].delta_sigma + np.random.uniform(-0.01, 0.01)
            
            new_population.append({
                'type': parent['type'] + '_child',
                'layer': child_layer,
                'params': child_layer.get_parameters(),
                'fitness': 0.0
            })
        
        return new_population
    
    def run(self):
        """Run full hybrid evolutionary learning process"""
        print("="*80)
        print("HYBRID EVOLUTIONARY LEARNING - Cycle 4")
        print("Combining V7 evolved parameters with gradient-based refinement")
        print("="*80)
        
        population = self.initialize_hybrid_population()
        
        for gen in range(self.generations):
            population = self.hybrid_step(population)
            
            # Record history
            gen_stats = {
                'generation': gen,
                'best_fitness': population[0]['fitness'],
                'best_survival': population[0]['survival'],
                'best_complexity': population[0]['complexity'],
                'best_params': population[0]['params'],
                'best_type': population[0]['type']
            }
            self.learning_history.append(gen_stats)
            
            if gen % 5 == 0:
                print(f"\nGen {gen}: Best fitness={population[0]['fitness']:.3f}, "
                      f"survival={population[0]['survival']:.3f}, "
                      f"type={population[0]['type']}")
        
        # Final analysis
        final_best = population[0]
        
        results = {
            'method': 'hybrid_evolutionary_learning',
            'cycle': 4,
            'generations': self.generations,
            'final_best': {
                'fitness': final_best['fitness'],
                'survival': final_best['survival'],
                'complexity': final_best['complexity'],
                'params': final_best['params'],
                'type': final_best['type'],
                'learnable_deltas': {
                    'delta_mu': final_best['layer'].delta_mu,
                    'delta_sigma': final_best['layer'].delta_sigma
                }
            },
            'learning_history': self.learning_history,
            'convergence': self.analyze_convergence()
        }
        
        return results
    
    def analyze_convergence(self):
        """Analyze if learning converged to stable parameters"""
        if len(self.learning_history) < 5:
            return {'status': 'insufficient_data'}
        
        recent = self.learning_history[-5:]
        fitness_trend = [h['best_fitness'] for h in recent]
        
        # Check if fitness is improving
        improving = all(fitness_trend[i] <= fitness_trend[i+1] 
                       for i in range(len(fitness_trend)-1))
        
        # Check parameter stability
        param_variance = np.var([h['best_params']['mu'] for h in recent])
        
        return {
            'improving': improving,
            'param_variance': param_variance,
            'final_fitness': fitness_trend[-1],
            'fitness_gain': fitness_trend[-1] - fitness_trend[0]
        }

def main():
    """Run Cycle 4 hybrid experiment"""
    print("Starting Cycle 4: Hybrid Learnable Lenia")
    print("Building on V7 evolved parameters and V8 GNN insights")
    print()
    
    # Run hybrid learner
    learner = HybridEvolutionaryLearner(
        population_size=30,
        generations=20,
        learning_steps=5
    )
    
    results = learner.run()
    
    # Save results
    output_path = Path(__file__).parent / 'exploration' / 'cycle4_hybrid_results.json'
    output_path.parent.mkdir(exist_ok=True, parents=True)
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {output_path}")
    
    # Print summary
    print("\n" + "="*80)
    print("CYCLE 4 RESULTS SUMMARY")
    print("="*80)
    print(f"Best fitness: {results['final_best']['fitness']:.3f}")
    print(f"Best survival: {results['final_best']['survival']:.3f}")
    print(f"Best complexity: {results['final_best']['complexity']:.3f}")
    print(f"Best type: {results['final_best']['type']}")
    print(f"Final parameters: μ={results['final_best']['params']['mu']:.4f}, "
          f"σ={results['final_best']['params']['sigma']:.4f}")
    print(f"Learnable deltas: Δμ={results['final_best']['learnable_deltas']['delta_mu']:.4f}, "
          f"Δσ={results['final_best']['learnable_deltas']['delta_sigma']:.4f}")
    print()
    
    return results

if __name__ == '__main__':
    main()
