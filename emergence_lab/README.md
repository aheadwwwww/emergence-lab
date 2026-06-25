# emergence-lab — 可编程涌现实验框架

> 让涌现可观察、可干预、可引导

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 核心理念

涌现不是魔法，是参数空间里的窗口。`emergence-lab` 提供统一的实验平台，让研究者能：
- **观察**：实时可视化涌现过程
- **干预**：调整参数影响涌现方向
- **引导**：引入外部信号引导涌现

## 支持的涌现模式

| 模式 | 协调机制 | 异步性 | 典型应用 |
|------|---------|--------|---------|
| Lenia | 匿名场 (FFT) | 同步 | 人工生命形态 |
| NCA | 学习规则 (MLP) | 异步 | 目标驱动生长 |
| PheromoneCA | 信息素场 | 混合 | 多智能体协作 |

## Quick Start

```python
from emergence_lab import Lenia, NCA, PheromoneCA

# Lenia 实验
lenia = Lenia(R=20, mu=0.15, sigma=0.03)
lenia.init_grid(shape=(256, 256))
result = lenia.run(steps=300, verbose=True)
print(f"State: {result['state']}, Score: {result['emergence_score']:.3f}")

# NCA 实验
nca = NCA(channels=16, fire_rate=0.5)
nca.init_grid(shape=(128, 128))
result = nca.run(steps=200)

# 信息素耦合
ca = PheromoneCA(channels=3, deposit_rate=0.1)
ca.init_grid(shape=(128, 128))
result = ca.run(steps=200)
```

## 安装

```bash
git clone https://github.com/YOUR_USERNAME/emergence-lab.git
cd emergence-lab
pip install -r requirements.txt
```

## 核心功能

### 1. 统一接口
所有 CA 模式共享 `run()`, `measure()`, `classify()` 方法。

### 2. 涌现度量
```python
from emergence_lab import EmergenceMetrics

metrics = EmergenceMetrics.full_report(grid)
# {'alive': 0.85, 'entropy': 4.2, 'edge_density': 0.12, 'emergence_score': 0.63}
```

### 3. 可视化
```python
from emergence_lab.core.visualization import Visualizer

Visualizer.plot_timeline(lenia.history, n_frames=5, save_path='timeline.png')
Visualizer.create_gif(lenia.history, 'animation.gif', fps=10)
```

## 架构

```
emergence_lab/
├── core/
│   ├── metrics.py       # 涌现度量
│   └── visualization.py  # 可视化
├── models/
│   ├── lenia.py          # Lenia 实现
│   ├── nca.py            # NCA 实现
│   └── pheromone.py      # 信息素 CA
└── experiments/
    └── sweep.py          # 参数扫描
```

## 与现有工作的关系

- **Lenia**: 基于 Bert Chan 的官方实现，用 JAX 加速
- **NCA**: 基于 Distill 的 Growing Neural Cellular Automata
- **创新点**: 统一接口 + 涌现度量 + 可编程涌现

## License

MIT

---

**状态**: v0.1.0 — 基础功能可用
**起源**: 2026-06-25 探索笔记