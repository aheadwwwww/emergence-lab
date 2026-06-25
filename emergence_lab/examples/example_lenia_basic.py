"""
Example 1: Basic Lenia Simulation

运行 Lenia 并观察涌现行为。
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from emergence_lab import Lenia
from emergence_lab.core.visualization import Visualizer

# 创建 Lenia 实例
lenia = Lenia(R=20, mu=0.14, sigma=0.024)

# 初始化网格
lenia.init_grid(shape=(256, 256), mode='random')

# 运行 200 步
print("Running Lenia simulation...")
result = lenia.run(steps=200, record_every=40, verbose=True)

print(f"\n最终状态: {result['state']}")
print(f"涌现评分: {result['emergence_score']:.3f}")

# 保存时间线可视化
Visualizer.plot_timeline(
    lenia.history, 
    n_frames=5, 
    save_path='examples/output/lenia_timeline.png',
    titles=['Step 0', 'Step 40', 'Step 80', 'Step 120', 'Step 200']
)

print("\n保存可视化到 output/lenia_timeline.png")