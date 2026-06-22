# micrograd 学习笔记

## 是什么
Andrej Karpathy 的极简自动微分引擎，约 100 行代码实现反向传播。核心思想：每个神经元拆成无数个标量运算，用动态构建的 DAG（有向无环图）追踪计算过程。

## 核心架构

### Value 类 — 标量值 + 梯度

```python
class Value:
    def __init__(self, data, _children=(), _op=''):
        self.data = data        # 前向值
        self.grad = 0           # 反向梯度
        self._backward = lambda: None  # 反向传播函数
        self._prev = set(_children)    # 父节点（构建 DAG）
        self._op = _op                 # 操作符（可视化用）
```

**关键设计**：
1. **`_prev` 集合**：存储产生当前值的子节点 → 形成计算图
2. **`_backward` 函数**：每个操作定义自己的反向传播逻辑
3. **惰性计算梯度**：只有在调用 `backward()` 时才计算

### 操作实现

**加法 (`__add__`)**：
```python
def __add__(self, other):
    out = Value(self.data + other.data, (self, other), '+')
    
    def _backward():
        self.grad += out.grad    # d(a+b)/da = 1
        other.grad += out.grad   # d(a+b)/db = 1
    
    out._backward = _backward
    return out
```

**乘法 (`__mul__`)**：
```python
def __mul__(self, other):
    out = Value(self.data * other.data, (self, other), '*')
    
    def _backward():
        self.grad += other.data * out.grad  # d(a*b)/da = b
        other.grad += self.data * out.grad  # d(a*b)/db = a
    
    out._backward = _backward
    return out
```

**幂运算 (`__pow__`)**：
```python
def __pow__(self, other):
    out = Value(self.data**other, (self,), f'**{other}')
    
    def _backward():
        self.grad += (other * self.data**(other-1)) * out.grad  # d(a^n)/da = n*a^(n-1)
    
    out._backward = _backward
    return out
```

**ReLU (`relu`)**：
```python
def relu(self):
    out = Value(0 if self.data < 0 else self.data, (self,), 'ReLU')
    
    def _backward():
        self.grad += (out.data > 0) * out.grad  # d(ReLU(x))/dx = 1 if x>0 else 0
    
    out._backward = _backward
    return out
```

### 反向传播 (`backward`)

**拓扑排序 + 链式法则**：

```python
def backward(self):
    # 1. 构建拓扑序（从叶子到根）
    topo = []
    visited = set()
    def build_topo(v):
        if v not in visited:
            visited.add(v)
            for child in v._prev:
                build_topo(child)
            topo.append(v)
    build_topo(self)
    
    # 2. 初始化根节点梯度为 1
    self.grad = 1
    
    # 3. 反向遍历，应用链式法则
    for v in reversed(topo):
        v._backward()
```

**为什么需要拓扑排序？**
- 每个节点的梯度依赖于其后继节点的梯度
- 必须从输出到输入逐层计算
- 拓扑序保证了：计算当前节点时，所有后继节点梯度已知

## 神经网络模块 (`nn.py`)

### 三层结构

**Neuron（神经元）**：
```python
class Neuron(Module):
    def __init__(self, nin, nonlin=True):
        self.w = [Value(random.uniform(-1,1)) for _ in range(nin)]
        self.b = Value(0)
        self.nonlin = nonlin
    
    def __call__(self, x):
        act = sum((wi*xi for wi,xi in zip(self.w, x)), self.b)
        return act.relu() if self.nonlin else act
```

**Layer（层）**：
```python
class Layer(Module):
    def __init__(self, nin, nout, **kwargs):
        self.neurons = [Neuron(nin, **kwargs) for _ in range(nout)]
    
    def __call__(self, x):
        out = [n(x) for n in self.neurons]
        return out[0] if len(out) == 1 else out
```

**MLP（多层感知机）**：
```python
class MLP(Module):
    def __init__(self, nin, nouts):
        sz = [nin] + nouts
        self.layers = [Layer(sz[i], sz[i+1], nonlin=i!=len(nouts)-1) 
                       for i in range(len(nouts))]
    
    def __call__(self, x):
        for layer in self.layers:
            x = layer(x)
        return x
```

**注意**：最后一层默认 `nonlin=False`（线性输出层）

### Module 基类

```python
class Module:
    def zero_grad(self):
        for p in self.parameters():
            p.grad = 0
    
    def parameters(self):
        return []
```

**递归收集参数**：
- `Neuron.parameters()` → `[w1, w2, ..., wn, b]`
- `Layer.parameters()` → `[p for n in neurons for p in n.parameters()]`
- `MLP.parameters()` → `[p for layer in layers for p in layer.parameters()]`

## 关键设计模式

### 1. 动态图构建
- 每次 `+`, `*` 操作创建新的 `Value` 节点
- `_prev` 指向父节点，形成 DAG
- 不需要预先定义计算图

### 2. 闭包捕获反向传播
```python
def __add__(self, other):
    out = Value(...)
    
    def _backward():  # 闭包捕获 self, other, out
        self.grad += out.grad
        other.grad += out.grad
    
    out._backward = _backward
    return out
```

**为什么用闭包？**
- 每个操作的反向传播逻辑不同
- 需要访问操作时的上下文（self, other）
- 函数对象可以存储在 Value 实例中

### 3. 梯度累加 (`+=` 而非 `=`)
```python
self.grad += out.grad
```

**为什么累加？**
- 同一个变量可能被多次使用
- 例：`y = x + x`，`x` 出现两次
- `dy/dx = 1 + 1 = 2`，需要累加

### 4. Python 魔术方法
```python
__radd__  # other + self
__rmul__  # other * self
__neg__   # -self
__sub__   # self - other
__truediv__  # self / other
```

**目的**：支持自然语法 `a + 2`，`2 * a` 等

## 与 PyTorch 的对比

| 特性 | micrograd | PyTorch |
|------|-----------|---------|
| 数据类型 | 标量 | 张量（多维数组） |
| 计算图 | 动态 DAG | 动态 DAG |
| 反向传播 | 手动拓扑排序 | 自动优化 |
| GPU 支持 | ❌ | ✅ |
| 性能 | 极慢（教学用） | 生产级 |

**micrograd 的价值**：
- 理解自动微分的本质
- 反向传播的直观实现
- PyTorch 的最小化原型

## 学到的技巧

1. **动态 DAG**：每个操作创建节点，用 `_prev` 指向父节点
2. **闭包反向传播**：每个操作定义自己的 `_backward`，捕获操作上下文
3. **拓扑排序**：从输出到输入的反向传播顺序
4. **梯度累加**：处理变量复用的情况
5. **递归参数收集**：Module 基类的 `parameters()` 方法
6. **魔术方法重载**：让 API 更自然

## 与好奇心地图的关联

- **#011 Grokking**：梯度下降是理解（泛化）的机制
- **#013 Attention Mechanism**：深度学习的基础是自动微分
- **#014 Computational Universe**：计算图是一种计算过程
- **#016 Self-Reference**：`_backward` 函数是自指的（指向自己定义的反向逻辑）

## 扩展思考

### 为什么 micrograd 用标量？
- **教学目的**：标量最直观，容易理解
- **避免复杂性**：张量需要广播、形状匹配等
- **概念清晰**：每个节点对应一个数学运算

### 如何扩展到张量？
```python
class Tensor:
    def __init__(self, data, _children=(), _op=''):
        self.data = np.array(data)  # 改用 numpy
        self.grad = np.zeros_like(self.data)
        ...
```

- 需要处理广播规则
- 矩阵乘法的反向传播更复杂
- 这就是 PyTorch/TensorFlow 做的事

### 实际应用
- 用 micrograd 训练小型神经网络
- 理解反向传播的每一步
- 可视化计算图（用 graphviz）

---

## 清理
- 保留 micrograd 克隆供后续参考
