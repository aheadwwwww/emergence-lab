# micrograd 学习笔记

> 学习时间：2026-06-26 22:05
> 来源：https://github.com/karpathy/micrograd

---

## 一、什么是 micrograd

micrograd 是 Andrej Karpathy 写的一个**极简自动微分引擎**，只有约100行代码，却实现了：
- 反向传播（reverse-mode autodiff）
- 动态构建计算图（DAG）
- PyTorch 风格的 API

**核心理念**：用标量（scalar）运算构建整个深度神经网络。

---

## 二、核心代码解析

### 2.1 Value 类

```python
class Value:
    def __init__(self, data, _children=(), _op=''):
        self.data = data      # 存储标量值
        self.grad = 0         # 存储梯度
        self._backward = lambda: None  # 反向传播函数
        self._prev = set(_children)    # 父节点
        self._op = _op                 # 操作类型（用于可视化）
```

**关键点**：
- `data`：节点存储的标量值
- `grad`：梯度（∂loss/∂data）
- `_backward`：该节点的反向传播函数
- `_prev`：父节点集合（计算图的边）

### 2.2 加法操作

```python
def __add__(self, other):
    other = other if isinstance(other, Value) else Value(other)
    out = Value(self.data + other.data, (self, other), '+')

    def _backward():
        self.grad += out.grad   # 链式法则：d(a+b)/da = 1
        other.grad += out.grad  # d(a+b)/db = 1
    out._backward = _backward

    return out
```

**为什么是 `+=` 而不是 `=`**？
- 因为一个变量可能在计算图中出现多次（如 `a + a`）
- 需要累加来自不同路径的梯度

### 2.3 乘法操作

```python
def __mul__(self, other):
    other = other if isinstance(other, Value) else Value(other)
    out = Value(self.data * other.data, (self, other), '*')

    def _backward():
        self.grad += other.data * out.grad   # d(ab)/da = b
        other.grad += self.data * out.grad   # d(ab)/db = a
    out._backward = _backward

    return out
```

### 2.4 ReLU 激活函数

```python
def relu(self):
    out = Value(0 if self.data < 0 else self.data, (self,), 'ReLU')

    def _backward():
        self.grad += (out.data > 0) * out.grad  # x>0时梯度为1，否则为0
    out._backward = _backward

    return out
```

### 2.5 反向传播（核心！）

```python
def backward(self):
    # 拓扑排序
    topo = []
    visited = set()
    def build_topo(v):
        if v not in visited:
            visited.add(v)
            for child in v._prev:
                build_topo(child)
            topo.append(v)
    build_topo(self)

    # 初始化梯度为1
    self.grad = 1
    
    # 从后往前应用链式法则
    for v in reversed(topo):
        v._backward()
```

**关键步骤**：
1. **拓扑排序**：确保反向传播顺序正确
2. **初始化梯度**：损失函数对自己的梯度为1
3. **逐节点反向传播**：按拓扑序逆序调用每个节点的 `_backward()`

---

## 三、为什么这么简洁？

### 3.1 标量而非张量

- PyTorch/TensorFlow 操作的是张量（矩阵）
- micrograd 只操作标量
- **代价**：效率低（每个加法、乘法都是一个节点）
- **好处**：概念清晰，易于理解

### 3.2 动态图

- 计算图在**前向传播时构建**
- 不需要预先定义图结构
- 与 PyTorch 的动态图理念一致

### 3.3 闭包保存梯度函数

- 每个操作都定义一个闭包 `_backward()`
- 闭包捕获了 `self` 和 `other`
- 反向传播时直接调用

---

## 四、示例：手动推导

```python
a = Value(-4.0)
b = Value(2.0)
c = a + b        # c = -2
d = a * b + b**3 # d = -8 + 8 = 0
c += c + 1       # c = -2 + (-2) + 1 = -3
c += 1 + c + (-a) # c = -3 + 1 + (-3) + 4 = -1
d += d * 2 + (b + a).relu() # d = 0 + 0 + 0 = 0
d += 3 * d + (b - a).relu() # d = 0 + 0 + 6 = 6
e = c - d        # e = -1 - 6 = -7
f = e**2         # f = 49
g = f / 2.0      # g = 24.5
g += 10.0 / f    # g = 24.5 + 0.204 = 24.704
```

反向传播后：
- `a.grad = 138.8338`（∂g/∂a）
- `b.grad = 645.5773`（∂g/∂b）

---

## 五、与 PyTorch 对比

| 特性 | micrograd | PyTorch |
|------|----------|---------|
| 操作对象 | 标量 | 张量 |
| 计算图 | 动态 | 动态 |
| 反向传播 | 手写 | 自动微分引擎 |
| 代码量 | ~100行 | 数万行 |
| 性能 | 慢 | 快（CUDA加速） |
| 用途 | 教学 | 生产 |

---

## 六、学习收获

### 6.1 自动微分的本质

**不是符号微分，也不是数值微分**
- 符号微分：推导数学公式
- 数值微分：用 (f(x+h) - f(x))/h 近似
- **自动微分**：分解为基本操作，逐节点应用链式法则

### 6.2 反向传播的简洁实现

关键在于：
1. 前向传播时**保存计算图**
2. 每个操作定义其**反向函数**
3. 拓扑排序保证**计算顺序**

### 6.3 为什么深度学习框架都是动态图？

- 动态图更灵活（条件、循环）
- 调试更方便
- PyTorch 的成功证明了动态图的价值

---

## 七、可以扩展的方向

1. **支持张量**：从标量扩展到矩阵
2. **GPU 加速**：使用 CUDA
3. **更多操作**：sigmoid、tanh、卷积等
4. **优化器**：Adam、RMSprop 等
5. **可视化**：GraphViz 集成

---

## 八、一句话总结

**micrograd 用100行代码展示了自动微分的本质：前向构建图，反向应用链式法则。**

---

**学习时间：2026-06-26 22:05**
**代码仓库**：repos/micrograd