"""
Example 4: PheromoneCA Multi-Agent Coordination

信息素耦合的多智能体涌现行为。
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from emergence_lab import PheromoneCA
from emergence_lab.core.visualization import Visualizer
import matplotlib.pyplot as plt
import numpy as np

# 创建 PheromoneCA 实例
ca = PheromoneCA(channels=3, deposit_rate=0.1, decay_rate=0.01)

# 初始化网格
ca.init_grid(shape=(128, 128))

# 运行 200 步
print("Running PheromoneCA simulation...")
result = ca.run(steps=200, record_every=40, verbose=True)

print(f"\n最终状态: {result['state']}")
print(f"涌现评分: {result['emergence_score']:.3f}")

# 可视化合并通道
combined = ca.get_combined()
fig, ax = plt.subplots(figsize=(6, 6))
ax.imshow(combined, cmap='coolwarm', vmin=0, vmax=1)
ax.set_title('PheromoneCA - Combined Channels')
ax.axis('off')
fig.savefig('examples/output/pheromone_final.png', dpi=100, bbox_inches='tight')
plt.close(fig)

print("保存可视化到 output/pheromone_final.png")