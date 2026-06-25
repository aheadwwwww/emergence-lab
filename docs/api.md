# EmergenceLab API 参考

## Lenia

```python
class Lenia(R=20, mu=0.15, sigma=0.03, kn=1, gn=1, fire_rate=1.0)
```

### 方法

| 方法 | 说明 |
|------|------|
| `init_grid(shape, mode='random')` | 初始化网格 |
| `run(steps, record_every=10, verbose=True)` | 运行模拟 |
| `measure()` | 度量当前状态 |
| `classify()` | 分类当前状态 |
| `get_frame(index=-1)` | 获取指定帧 |
| `get_timeline()` | 获取所有帧 |

### init_grid 参数

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| shape | tuple | (256, 256) | 网格形状 |
| mode | str | 'random' | 初始化模式 |

## NCA

```python
class NCA(channels=16, fire_rate=0.5, hidden_size=32)
```

### 方法

| 方法 | 说明 |
|------|------|
| `init_grid(shape, seed_size=4)` | 初始化网格 |
| `run(steps, record_every=10, verbose=True)` | 运行模拟 |
| `get_rgba()` | 获取 RGBA 可视化 |

## PheromoneCA

```python
class PheromoneCA(channels=3, R=12, deposit_rate=0.1, decay_rate=0.01)
```

### 方法

| 方法 | 说明 |
|------|------|
| `init_grid(shape)` | 初始化网格 |
| `run(steps, record_every=10, verbose=True)` | 运行模拟 |
| `get_combined()` | 获取合并的可视化 |

## EmergenceMetrics

```python
class EmergenceMetrics:
    alive(grid, threshold=0.01) -> float
    entropy(grid, bins=50) -> float
    edge_density(grid, threshold=0.1) -> float
    stability(grid_history, window=10) -> float
    emergence_score(grid, grid_history=None) -> float
    classify(grid, grid_history=None) -> str
    full_report(grid, grid_history=None) -> dict
```

### 状态分类

| 分类 | 条件 |
|------|------|
| `dead` | alive < 0.01 |
| `simple` | alive > 0.01, edge_density < 0.05 |
| `structure` | edge_density >= 0.05 |

## Visualizer

```python
class Visualizer:
    plot_grid(grid, title="", save_path=None, cmap='coolwarm')
    plot_timeline(history, n_frames=5, save_path=None, titles=None)
    plot_comparison(models, names=None, save_path=None)
    create_gif(history, save_path, fps=10)
```