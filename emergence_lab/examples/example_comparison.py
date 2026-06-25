"""
Example 5: Emergence Comparison

对比三种涌现模式的差异。
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from emergence_lab import Lenia, NCA, PheromoneCA
from emergence_lab.core.visualization import Visualizer
import matplotlib.pyplot as plt
import numpy as np

print("Comparing three emergence modes...\n")

models = {
    'Lenia': None,
    'NCA': None,
    'PheromoneCA': None,
}

# Lenia
print("Running Lenia...")
lenia = Lenia(R=20, mu=0.14, sigma=0.024)
lenia.init_grid(shape=(128, 128), mode='random')
result = lenia.run(steps=150, record_every=150, verbose=False)
models['Lenia'] = lenia.get_frame(-1)
print(f"  Lenia: {result['state']}, score={result['emergence_score']:.3f}")

# NCA
print("Running NCA...")
nca = NCA(channels=16, fire_rate=0.5)
nca.init_grid(shape=(128, 128), seed_size=8)
result = nca.run(steps=150, record_every=150, verbose=False)
models['NCA'] = nca.get_rgba()[:, :, 3]  # Alpha channel
print(f"  NCA: alive={result['alive']:.3f}")

# PheromoneCA
print("Running PheromoneCA...")
ca = PheromoneCA(channels=3, deposit_rate=0.1)
ca.init_grid(shape=(128, 128))
result = ca.run(steps=150, record_every=150, verbose=False)
models['PheromoneCA'] = ca.get_combined()
print(f"  PheromoneCA: {result['state']}, score={result['emergence_score']:.3f}")

# 可视化对比
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for i, (name, grid) in enumerate(models.items()):
    axes[i].imshow(grid, cmap='coolwarm', vmin=0, vmax=1)
    axes[i].set_title(name)
    axes[i].axis('off')

plt.suptitle('Emergence Mode Comparison')
plt.tight_layout()
fig.savefig('examples/output/emergence_comparison.png', dpi=150, bbox_inches='tight')
plt.close(fig)

print("\n保存对比图到 output/emergence_comparison.png")