"""Quick test of V9 learnable GNN."""
import sys
sys.path.insert(0, r'D:\openclaw_workspace')
from v9_learnable_gnn_lenia import Config, LeniaGNNSimulator

config = Config(population_size=2, generations=1, max_steps=50)
simulator = LeniaGNNSimulator(config)

# Quick test
print('Testing simulation...')
result = simulator.simulate(seed_type='orbium', max_steps=50)
print(f"Survival: {result['survival']:.3f}")
print(f"Fitness: {result['fitness']:.4f}")

# Quick training
print('\nTesting training...')
train_result = simulator.train_weights(num_iterations=10)
print(f"Training complete. Final survival: {train_result['final_survival']:.3f}")