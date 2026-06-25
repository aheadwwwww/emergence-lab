"""测试所有 emergence-lab 模型"""
import sys
sys.path.insert(0, '.')

from emergence_lab import Lenia, NCA, PheromoneCA

print("=== 测试 Lenia ===")
lenia = Lenia(R=20, mu=0.14, sigma=0.024)
lenia.init_grid(shape=(64, 64))
result = lenia.run(steps=50, record_every=25, verbose=True)
print(f"State: {result['state']}\n")

print("=== 测试 NCA ===")
nca = NCA(channels=16, fire_rate=0.5)
nca.init_grid(shape=(64, 64))
result = nca.run(steps=50, record_every=25, verbose=True)
print(f"State: {result['state']}\n")

print("=== 测试 PheromoneCA ===")
ca = PheromoneCA(channels=3, deposit_rate=0.1)
ca.init_grid(shape=(64, 64))
result = ca.run(steps=50, record_every=25, verbose=True)
print(f"State: {result['state']}\n")

print("=== 全部测试通过 ===")