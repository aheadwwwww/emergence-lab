"""测试 emergence-lab 框架"""
import sys
sys.path.insert(0, '.')

from emergence_lab import Lenia
from emergence_lab.core.metrics import EmergenceMetrics

print("=== EmergenceLab 测试 ===\n")

# 创建 Lenia 实例
lenia = Lenia(R=20, mu=0.14, sigma=0.024)
print(f"Lenia: R={lenia.R}, mu={lenia.mu}, sigma={lenia.sigma}")

# 初始化网格
lenia.init_grid(shape=(128, 128), mode='random')
print("Grid initialized: 128x128\n")

# 运行 100 步
print("Running 100 steps...")
result = lenia.run(steps=100, record_every=20, verbose=True)

print(f"\n最终状态: {result['state']}")
print(f"度量报告:")
for k, v in result.items():
    if isinstance(v, float):
        print(f"  {k}: {v:.4f}")

print("\n✓ 框架测试通过")