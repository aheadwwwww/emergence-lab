# emergence-lab 使用指南

## 安装

```bash
git clone https://github.com/aheadwwwww/emergence-lab.git
cd emergence-lab
pip install -r requirements.txt
```

## 快速开始

### 1. Lenia — 连续细胞自动机

```python
from emergence_lab import Lenia

lenia = Lenia(R=20, mu=0.14, sigma=0.024)
lenia.init_grid(shape=(256, 256), mode='random')
result = lenia.run(steps=200, verbose=True)

print(f"State: {result['state']}")
print(f"Emergence Score: {result['emergence_score']:.3f}")
```

**参数说明**：
- `R`: 核半径（推荐 13-25）
- `mu`: 生长中心（推荐 0.12-0.16）
- `sigma`: 生长宽度（推荐 0.02-0.04）
- `fire_rate`: 异步更新比例（1.0=全同步）

### 2. NCA — 神经细胞自动机

```python
from emergence_lab import NCA

nca = NCA(channels=16, fire_rate=0.5)
nca.init_grid(shape=(128, 128), seed_size=8)
result = nca.run(steps=200, verbose=True)
```

**参数说明**：
- `channels`: 通道数（默认 16）
- `fire_rate`: 每步更新比例（默认 0.5）

### 3. PheromoneCA — 信息素耦合

```python
from emergence_lab import PheromoneCA

ca = PheromoneCA(channels=3, deposit_rate=0.1, decay_rate=0.01)
ca.init_grid(shape=(128, 128))
result = ca.run(steps=200, verbose=True)
```

**参数说明**：
- `channels`: 智能体通道数
- `deposit_rate`: 信息素沉积率
- `decay_rate`: 信息素衰减率

## 涌现度量

```python
from emergence_lab import EmergenceMetrics

metrics = EmergenceMetrics.full_report(grid)
# {
#   'alive': 0.85,           # 存活细胞比例
#   'entropy': 4.2,          # 状态熵
#   'edge_density': 0.12,    # 边缘密度
#   'stability': 0.95,       # 稳定性
#   'emergence_score': 0.63, # 综合涌现指数
#   'state': 'structure'     # 状态分类
# }
```

## 可视化

```python
from emergence_lab.core.visualization import Visualizer

# 时间线
Visualizer.plot_timeline(lenia.history, n_frames=5, save_path='timeline.png')

# 对比
Visualizer.plot_comparison([lenia, nca, ca], names=['Lenia', 'NCA', 'PheromoneCA'])
```

## 运行示例

```bash
cd examples
python example_lenia_basic.py
python example_parameter_sweep.py
python example_nca.py
python example_pheromone.py
python example_comparison.py
```

## 架构

```
emergence_lab/
├── core/
│   ├── metrics.py        # 涌现度量
│   └── visualization.py   # 可视化
├── models/
│   ├── lenia.py           # Lenia 实现
│   ├── nca.py             # NCA 实现
│   └── pheromone.py       # 信息素 CA
├── examples/              # 示例代码
├── docs/                  # 文档
└── experiments/           # 实验工具
```

## 常见问题

### Q: Lenia 不产生结构怎么办？
A: 调整参数。R=20, mu=0.14, sigma=0.024 是已验证的 sweet spot。

### Q: NCA 存活率太低？
A: 增大 seed_size 或降低 fire_rate。

### Q: 如何对比不同涌现模式？
A: 运行 `examples/example_comparison.py`。