# tinygrad 学习笔记

## 项目简介
- **tinygrad** 是一个极简主义的深度学习框架
- 由 [tiny corp](https://tinygrad.org) 维护
- 定位：介于 PyTorch 和 karpathy/micrograd 之间

## 核心设计理念

### 1. 惰性求值 (Laziness)
- 张量操作不会立即执行，而是构建计算图
- 使用 `.realize()` 触发实际计算
- 支持内核融合（kernel fusion）

```python
# 示例：惰性求值 + 内核融合
DEBUG=3 python3 -c "from tinygrad import Tensor;
N = 1024; a, b = Tensor.empty(N, N), Tensor.empty(N, N);
(a.reshape(N, 1, N) * b.T.reshape(1, N, N)).sum(axis=2).realize()"
```

### 2. 统一 IR 编译器
- 基于中间表示（IR）的自动微分
- 多个 lowering passes 和调度
- BEAM search 优化内核

### 3. 多加速器支持
框架支持以下硬件后端（只需实现约 25 个底层操作）：

- ✅ OpenCL
- ✅ CPU
- ✅ METAL (Apple)
- ✅ CUDA (NVIDIA)
- ✅ AMD (ROCm)
- ✅ NV (NVIDIA 原生)
- ✅ QCOM (高通)
- ✅ WEBGPU

### 4. 与其他框架对比

| 特性 | PyTorch | JAX | tinygrad |
|------|---------|-----|----------|
| Eager API | ✅ | ✅ | ✅ |
| 可见 IR | ❌ | ✅ | ✅ |
| 可 hack | 部分 | 部分 | ✅ 完全 |
| 函数式变换 | 部分 | ✅ vmap/pmap | 部分 |
| 学习曲线 | 中等 | 高 | **低** |

## 架构分析

### 核心文件结构
```
tinygrad/
├── tensor.py          # 张量定义（受 micrograd 启发）
├── engine/
│   ├── jit.py         # JIT 编译
│   └── realize.py     # 计算执行
├── uop/
│   └── ops.py         # 统一操作 IR
├── runtime/
│   ├── ops_cpu.py     # CPU 后端
│   ├── ops_cuda.py    # CUDA 后端
│   ├── ops_metal.py   # Metal 后端
│   └── ...            # 其他后端
├── nn/                # 神经网络模块
└── dtype.py          # 数据类型
```

### 张量类设计
```python
class Tensor(RandMixin, metaclass=TensorMeta):
    __slots__ = "uop", "is_param", "grad"
    
    def __init__(self, data, device=None, dtype=None):
        self.grad: Tensor|None = None  # 梯度
        self.is_param: bool = True      # 是否为参数
        # uop 是底层统一操作表示
```

### 自动微分机制
- 类似 JAXPR + XLA 的 IR-based autodiff
- 支持反向传播 `.backward()`

## 快速示例

### 简单神经网络
```python
from tinygrad import Tensor, nn

class LinearNet:
    def __init__(self):
        self.l1 = Tensor.kaiming_uniform(784, 128)
        self.l2 = Tensor.kaiming_uniform(128, 10)
    
    def __call__(self, x: Tensor) -> Tensor:
        return x.flatten(1).dot(self.l1).relu().dot(self.l2)

model = LinearNet()
optim = nn.optim.Adam([model.l1, model.l2], lr=0.001)

# 训练循环
with Tensor.train():
    for i in range(10):
        optim.zero_grad()
        loss = model(x).sparse_categorical_crossentropy(y).backward()
        optim.step()
```

### 与 PyTorch 对比
```python
# tinygrad
from tinygrad import Tensor
x = Tensor.eye(3)
y = Tensor([[2.0, 0, -2.0]])
z = y.matmul(x).sum()
z.backward()
print(x.grad.tolist())  # dz/dx
print(y.grad.tolist())  # dz/dy
```

## 与涌现实验的结合点

### 1. 轻量级模型训练
- 可以用 tinygrad 训练涌现实验中的神经网络
- 比 PyTorch 更轻量，代码更易理解

### 2. 多后端支持
- 可以在不同硬件上运行实验
- OpenCL 后端可在 Intel/AMD GPU 上运行

### 3. 内核融合优化
- 惰性求值 + 内核融合可以提高性能
- 对于细胞自动机等迭代算法很有用

### 4. 学习价值
- 代码简洁（~300 行模型定义）
- 可以深入理解深度学习框架内部机制
- 学习 IR 编译器设计

## 待深入学习

1. **UOp IR 设计** - `tinygrad/uop/ops.py`
2. **JIT 编译** - `tinygrad/engine/jit.py`
3. **内核融合算法** - 如何将多个操作合并
4. **多后端抽象** - 如何用 25 个底层操作实现所有功能
5. **BEAM search** - 内核优化算法

## 相关资源
- 官方文档: https://docs.tinygrad.org
- GitHub: https://github.com/tinygrad/tinygrad
- Discord: https://discord.gg/ZjZadyC7PK