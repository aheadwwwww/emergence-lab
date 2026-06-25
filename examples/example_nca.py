"""
Example 3: NCA Growth Simulation

运行 Neural Cellular Automata 观察目标驱动生长。
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from emergence_lab import NCA
from emergence_lab.core.visualization import Visualizer

# 创建 NCA 实例
nca = NCA(channels=16, fire_rate=0.5)

# 初始化网格（中心种子）
nca.init_grid(shape=(128, 128), seed_size=8)

# 运行 200 步
print("Running NCA simulation...")
result = nca.run(steps=200, record_every=40, verbose=True)

print(f"\n最终状态: {result['state']}")
print(f"存活比例: {result['alive']:.3f}")

# 保存 RGBA 可视化
rgba = nca.get_rgba()
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6, 6))
ax.imshow(rgba)
ax.set_title('NCA Final State')
ax.axis('off')
fig.savefig('examples/output/nca_final.png', dpi=100, bbox_inches='tight')
plt.close(fig)

print("保存可视化到 output/nca_final.png")