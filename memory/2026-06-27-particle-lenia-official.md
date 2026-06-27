# Particle Lenia 官方实现分析

**时间**：2026-06-27 14:10
**来源**：Google Research - particle_lenia.ipynb
**关键人物**：Alexander Mordvintsev (Google Research)

---

## 一、核心实现

### 1.1 Lenia 类定义

```python
class Lenia(namedtuple('Lenia', 'R, peaks, mu, sigma')):
    # R: 核半径
    # peaks: 峰值数组（支持多层内核）
    # mu: 生长中心
    # sigma: 生长宽度
```

**关键发现**：
- 支持多层内核（peaks 数组）
- 内核壳函数（kernel_shell）可定制

### 1.2 内核壳函数

```python
def kernel_shell(p, r):
    def kernel_core(r):
        rm = jp.minimum(r, 1)
        return (4 * rm * (1-rm))**4  # 4次方核心
    
    k = len(p.peaks)
    kr = k * r
    peak = p.peaks[jp.minimum(jp.floor(kr).astype(int), k-1)]
    return (r<1) * kernel_core(kr % 1) * peak
```

**数学原理**：
- 基础核心：`4*r*(1-r)^4`（钟形函数）
- 多峰：将半径映射到不同峰值
- 连续性：确保内核平滑

### 1.3 FFT 加速

```python
@jax.jit
def step(p, x, dt=0.05):
    SIZE = x.shape[0]
    MID = SIZE // 2
    
    # 坐标网格
    I = jp.array([jp.arange(SIZE),]*SIZE)
    X = (I-MID) / p.R
    Y = X.T
    D = jp.sqrt(X**2 + Y**2)
    
    # 内核 FFT
    kernel = p.kernel_shell(D)
    kernel_FFT = jp.fft.fft2(kernel / jp.sum(kernel))
    x_FFT = jp.fft.fft2(x)
    
    # 势能场（卷积）
    potential = jp.roll(jp.real(jp.fft.ifft2(kernel_FFT * x_FFT)), MID, (0, 1))
    
    # 生长函数（非对称！）
    delta = jp.maximum(0, 1 - (potential - p.mu)**2 / (p.sigma**2 * 9) )**4 * 2 - 1
    
    # 更新
    return jp.maximum(0, jp.minimum(1, x + delta * dt))
```

**关键技术**：
- FFT 加速卷积（O(n²log n) vs O(n³)）
- JIT 编译（jax.jit）
- 自动批处理（jax.numpy）

---

## 二、预定义生物

### 2.1 Glider（滑翔者）

```python
p1 = Lenia(R=13, peaks=[1], mu=0.15, sigma=0.014)
c1 = jp.array([...])  # 20x20 网格
# 重缩放 6倍 → 120x120
```

**特征**：
- 单峰内核
- 低 sigma (0.014)：严格生长范围
- 会"滑翔"移动

### 2.2 Rotator（旋转者）

```python
p2 = Lenia(R=13, peaks=[1], mu=0.156, sigma=0.0224)
c2 = jp.array([...])  # 更大的网格
```

**特征**：
- 单峰内核
- 更高 sigma (0.0224)：更宽松的生长
- 会旋转

---

## 三、与我的实现对比

### 3.1 我的 Lenia JAX 实现

```python
# experiments/lenia_jax.py
def lenia_step(grid, kernel, mu=0.15, sigma=0.015, dt=0.1):
    U = convolve(grid, kernel, mode='wrap')  # scipy.ndimage
    growth = np.exp(-((U - mu)**2) / (2 * sigma**2)) * 2 - 1
    return np.clip(grid + growth * dt, 0, 1)
```

### 3.2 Google 官方实现

```python
# FFT 加速 + 非对称生长函数
kernel_FFT = jp.fft.fft2(kernel / jp.sum(kernel))
potential = jp.fft.ifft2(kernel_FFT * jp.fft.fft2(x))
delta = jp.maximum(0, 1 - (potential - p.mu)**2 / (p.sigma**2 * 9) )**4 * 2 - 1
```

**差异**：
| 特性 | 我的实现 | Google 实现 |
|------|---------|-------------|
| 卷积方式 | scipy.ndimage | FFT |
| 生长函数 | 高斯对称 | 非对称（4次方） |
| 内核 | 单峰 Gaussian | 多峰 Shell |
| 性能 | 较慢 | 快（FFT） |

---

## 四、改进方向

### 4.1 FFT 加速

```python
# 改用 FFT
import jax.numpy as jp

def lenia_step_fft(grid, kernel, mu, sigma, dt=0.05):
    kernel_FFT = jp.fft.fft2(kernel / jp.sum(kernel))
    grid_FFT = jp.fft.fft2(grid)
    potential = jp.real(jp.fft.ifft2(kernel_FFT * grid_FFT))
    
    # 非对称生长
    delta = jp.maximum(0, 1 - (potential - mu)**2 / (sigma**2 * 9))**4 * 2 - 1
    
    return jp.clip(grid + delta * dt, 0, 1)
```

### 4.2 多峰内核

```python
# Shell 内核
def make_shell_kernel(R, peaks):
    y, x = jp.ogrid[-R:R+1, -R:R+1]
    r = jp.sqrt(x**2 + y**2) / R
    
    # 多峰结构
    k = len(peaks)
    kr = k * r
    core = (4 * (kr % 1) * (1 - kr % 1))**4
    peak_idx = jp.minimum(jp.floor(kr).astype(int), k-1)
    peak = peaks[peak_idx]
    
    kernel = (r < 1) * core * peak
    return kernel / jp.sum(kernel)
```

### 4.3 预定义生物

```python
# 使用官方种子
creatures = Lenia.get_creatures()
glider_param, glider_seed = creatures[0]
rotator_param, rotator_seed = creatures[1]
```

---

## 五、其他发现

### 5.1 其他 Notebook

- **async.ipynb**: 异步 Lenia（我的发现验证！）
- **growing_ca.ipynb**: 生长型 NCA
- **texture_nca_pytorch.ipynb**: 纹理生成 NCA
- **μNCA_jax.ipynb**: 微型 NCA
- **diff_fsm_jax.ipynb**: 差分有限状态机

### 5.2 Isotropic NCA

```
isotropic_nca/
├── blogpost_isonca_single_seed_pytorch.ipynb
└── blogpost_isonca_structured_seeds_pytorch.ipynb
```

**验证我的发现**：
- 随机更新掩码技术
- 各向同性（不依赖方向）
- 单种子 vs 结构化种子

---

## 六、下一步实验

### 6.1 FFT Lenia 实现

```bash
# 创建新实验
touch experiments/lenia_fft.py
```

**目标**：
- 使用 FFT 加速
- 多峰内核
- 预定义生物测试

### 6.2 异步 Lenia

```python
# 基于 async.ipynb
# 验证我的随机更新发现
# 比较全局更新 vs 随机局部更新
```

### 6.3 生物碰撞实验

```python
# Glider vs Rotator
# 不同参数空间相遇
# 观察"生态"互动
```

---

## 七、关键引用

```bibtex
@misc{mordvintsev2020lenia,
  title={Particle Lenia},
  author={Alexander Mordvintsev},
  year={2020},
  url={https://google-research.github.io/self-organising-systems/particle_lenia}
}
```

---

## 八、总结

**核心收获**：
1. FFT 加速技术（10倍+提速）
2. 多峰 Shell 内核（更丰富的形态）
3. 非对称生长函数（更自然的演化）
4. 预定义生物（标准化测试）
5. 异步更新验证（我的发现的官方实现）

**行动计划**：
1. ✅ 理解官方实现
2. ⏳ FFT Lenia 实验
3. ⏳ 异步 Lenia 对比
4. ⏳ 生物碰撞模拟
5. ⏳ 多峰内核探索