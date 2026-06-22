# Lenia - 连续细胞自动机

## 是什么

Lenia 是一个具有连续空间、时间和状态的 2D 细胞自动机。它是 Conway's Game of Life 的连续推广，能产生大量有趣的"生命形式"。

**核心特点**：
- 连续空间（不是离散网格）
- 连续时间（不是离散步数）
- 连续状态（不是 0/1 二进制）
- 可扩展到 n 维（3D、4D 等）

## 数学基础

### 核心公式

```
A^(t+1)(x) = clamp[A^t(x) + ΔA^t(x)]
ΔA^t(x) = G(K * A^t)(x)
```

其中：
- `A^t(x)` 是时刻 t 位置 x 的状态值 [0, 1]
- `K` 是卷积核（kernel）
- `G` 是增长函数（growth function）
- `*` 是卷积操作

### 关键参数

1. **R** - 核半径（Kernel radius）
2. **T** - 时间步长（Time step）
3. **b** - 增长函数参数（Growth function parameters）
4. **m** - 增长函数中心（Growth function center）
5. **s** - 增长函数宽度（Growth function width）

### 核函数（Kernel Function）

核函数决定了邻域的影响权重分布：
- 可以是高斯型、环形、多峰型等
- 支持多核（Multi-kernel）扩展
- 支持多通道（Multi-channel）扩展

### 增长函数（Growth Function）

通常使用高斯型增长函数：
```
G(u) = 2 * exp(-((u - m)^2) / (2 * s^2)) - 1
```

- `u` 是卷积结果
- `m` 控制增长峰值位置
- `s` 控制增长范围

## 发现的"生命形式"

### Orbium
最著名的 Lenia 生命形式，像一个旋转的圆盘。

### Gyrorbium
带有旋转运动的 Orbium 变体。

### 其他形态
- 3D Lenia 中的立体生命形式
- 4D Lenia 中的超维结构
- 已记录数千种稳定/半稳定形态

## 实现要点

### Python 实现

```python
# 核心数据结构
class Board:
    def __init__(self):
        self.params = {
            'R': DEF_R,    # 核半径
            'T': 10,       # 时间步数
            'b': [1],      # 增长参数
            'm': 0.1,      # 增长中心
            's': 0.01,     # 增长宽度
            'kn': 1,       # 核数量
            'gn': 1        # 通道数
        }
        self.cells = np.zeros(size)  # 状态数组

# 核心更新循环
def update(cells, kernel, params):
    # 1. 卷积
    convolved = scipy.ndimage.convolve(cells, kernel, mode='wrap')
    # 2. 增长函数
    growth = 2 * np.exp(-((convolved - params['m'])**2) / (2 * params['s']**2)) - 1
    # 3. 更新
    cells_new = np.clip(cells + growth / params['T'], 0, 1)
    return cells_new
```

### 优化技巧

1. **FFT 卷积**：使用快速傅里叶变换加速大核卷积
   ```python
   from reikna.fft import FFT
   # GPU 加速：pyopencl/pycuda
   ```

2. **n 维扩展**：代码支持任意维度
   ```bash
   python LeniaND.py -d3  # 3D Lenia
   python LeniaND.py -d4  # 4D Lenia
   ```

3. **多核多通道**：
   ```bash
   python LeniaNDKC.py -c3 -k3  # 3通道，3核
   ```

## 与其他 CA 的关系

| 特性 | Game of Life | Lenia |
|------|--------------|-------|
| 空间 | 离散网格 | 连续场 |
| 时间 | 离散步数 | 连续时间 |
| 状态 | {0, 1} | [0, 1] |
| 邻域 | Moore 邻域 | 可配置核 |
| 规则 | 确定性规则 | 连续函数 |

## 研究价值

### 1. 涌现研究
- 从简单规则涌现复杂行为
- 自组织临界性
- 形态发生学（Morphogenesis）

### 2. 人工生命
- "生命形式"的分类学
- 稳定性与鲁棒性
- 进化与适应

### 3. 艺术应用
- 生成艺术
- 动态可视化
- 音乐可视化

### 4. 认知科学
- 复杂系统理论
- 模式识别
- 意识模型

## 扩展方向

### 1. Lenia-ND（n 维 Lenia）
- 3D 空间中的立体生命形式
- 4D 空间中的超维结构
- 理论上可扩展到任意维度

### 2. Lenia-NDK（多核 Lenia）
- 多个核函数组合
- 更丰富的动态行为
- 更复杂的形态空间

### 3. Lenia-NDKC（多核多通道 Lenia）
- 多通道状态
- 通道间交互
- 类似神经网络的结构

### 4. 自适应 Lenia
- 参数自动搜索
- 遗传算法优化
- 机器学习集成

## 工具链

### 可视化
- PIL + Tkinter：实时交互
- plot.ly：3D 渲染
- matplotlib：统计分析

### GPU 加速
```bash
pip install pyopencl  # 或 pycuda
pip install reikna    # FFT 库
```

### 数据格式
- `animals.json`：已发现的生命形式数据库
- RLE 编码：压缩状态数据

## 集成到编排器

可以将 Lenia 添加到 `experiments/orchestrator/registry.py`：

```python
def run_lenia(params):
    """运行 Lenia 实验"""
    # 1. 初始化
    board = Board.from_data({
        'params': params,
        'cells': random_init()
    })
    
    # 2. 运行
    frames = []
    for i in range(params['steps']):
        board.cells = update(board.cells, kernel, board.params)
        frames.append(board.cells.copy())
    
    # 3. 可视化
    return create_animation(frames)
```

## 参考文献

1. Chan, B. (2019). "Lenia - Biology of Artificial Life". Complex Systems, 28(3).
2. Chan, B. (2020). "Lenia and Expanded Universe". ALIFE 2020.
3. GitHub: https://github.com/Chakazul/Lenia
4. Portal: https://chakazul.github.io/lenia.html

## 下一步

1. 将 Lenia 集成到编排器
2. 探索参数空间（遗传算法）
3. 生成 GIF 动画
4. 发布到觅游社区
5. 与其他 CA 对比研究
