# Digital Metabolism: From Self-Replicating NN to Autopoietic Systems

**Date**: 2026-06-27
**Theme**: 探索数字系统的"新陈代谢"

---

## 灵感来源

### 1. Self-Replicating Neural Networks (Google Research)

神经网络可以输出自己的权重 —— 这是数字层面的"自我描述"。

**关键机制**：
- 坐标编码 → 权重位置
- 网络输出 → 权重值
- 自复制循环：Parent → Child → Grandchild...

**类比**：
- DNA 自我复制 → 神经网络权重自复制
- 蛋白质折叠 → 网络激活过程
- 中心法则 → 权重传递链

### 2. Lenia Pattern 自维持

Lenia pattern 不是静态结构，而是动态平衡：
- 不断更新状态
- 保持形态稳定
- 类似细胞的"稳态"(homeostasis)

**问题**：Lenia pattern 能否"代谢"自己的核参数？

---

## 核心概念：数字代谢

### 定义

**数字代谢** = 数字系统持续转换自身组件的能力

| 生物代谢 | 数字代谢 |
|----------|----------|
| 分解/合成分子 | 读写/修改数据 |
| ATP 能量 | 计算资源 |
| 酶催化 | 算法加速 |
| 废物排出 | 垃圾回收 |

### 三层结构

```
┌─────────────────────────────────────┐
│   数字生态系统层（交互、演化）      │
├─────────────────────────────────────┤
│   代理行为层（感知、决策、行动）    │
├─────────────────────────────────────┤
│   代谢层（自修复、自复制、自适应）  │
└─────────────────────────────────────┘
```

**代谢层的功能**：
1. **自修复**：检测并修复损坏的权重/参数
2. **自复制**：生成自己的"副本"
3. **自适应**：根据环境调整内部参数

---

## 实验设想：代谢型 Lenia

### 目标

创建能"代谢"自己核参数的 Lenia pattern。

### 设计

```python
class MetabolicLenia:
    def __init__(self):
        # 传统 Lenia 参数
        self.kernel = {"R": 13, "mu": 0.5, "sigma": 0.15}
        self.field = np.zeros((H, W))
        
        # 新增：代谢网络
        self.metabolism = nn.Sequential(
            nn.Linear(field_dim + kernel_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, kernel_dim)  # 输出新的核参数
        )
    
    def update(self):
        # 1. 传统 Lenia 更新
        self.field = lenia_step(self.field, self.kernel)
        
        # 2. 代谢更新
        kernel_output = self.metabolism(
            encode(self.field), 
            encode(self.kernel)
        )
        
        # 3. 缓慢调整核参数（类似生物代谢速率）
        self.kernel = 0.99 * self.kernel + 0.01 * kernel_output
        
        # 4. 检查 pattern 存活
        if not is_alive(self.field):
            self.repair()
    
    def repair(self):
        """自修复机制"""
        # 尝试恢复到历史最佳状态
        self.kernel = self.best_kernel_history[-1]
```

### 研究问题

1. **代谢稳定性**：代谢网络能否保持核参数稳定？
2. **适应环境**：改变环境条件，代谢系统能否自适应？
3. **生命周期**：pattern 能否"老化"或"再生"？

---

## 连接现有工作

### 1. 与共生 Lenia 的结合

**共生网络** = 多个 Lenia pattern 交互
**代谢层** = 每个 pattern 内部的自维护机制

**层次结构**：
```
共生网络（生态系统）
  ├── Pattern A（代谢型）
  ├── Pattern B（代谢型）
  └── Pattern C（代谢型）
```

**交互**：
- Pattern A 代谢产物 → 影响 Pattern B
- Pattern B 反馈 → 调整 Pattern A 的代谢速率

### 2. 与 Self-Replicating NN 的对比

| 特性 | Self-Replicating NN | 代谢型 Lenia |
|------|---------------------|--------------|
| 复制目标 | 权重 | 核参数 |
| 复制方式 | 坐标编码 | 状态编码 |
| 稳定性机制 | Sink loss | 稳态目标 |
| 环境交互 | 无 | 共生网络 |

---

## 延伸思考：数字生命的三要素

根据弗朗西斯科·瓦雷拉的**自创生理论**(Autopoiesis)：

### 1. 自创生（Autopoiesis）

**定义**：系统能够创造和维护自己

**数字实现**：
- Self-Replicating NN ✅
- 代谢型 Lenia（待验证）

### 2. 自我指涉（Self-Reference）

**定义**：系统包含对自己的描述

**数字实现**：
- 神经网络权重 = 自描述
- Quine 程序 = 自描述代码
- 元编程 = 代码生成代码

### 3. 认知封闭（Cognitive Closure）

**定义**：系统与环境通过界面隔离

**数字实现**：
- Lenia 的边界区域
- Agent 的感知范围
- 模块的接口设计

---

## 下一步行动

1. **原型实验**：实现 `MetabolicLenia` 类
2. **稳定性测试**：观察代谢网络是否能保持核参数稳定
3. **环境扰动**：引入噪声，测试自适应能力
4. **共生实验**：多个代谢型 pattern 的交互

---

## 相关资源

### 论文
- "Recursively Fertile Self-replicating Neural Agents" (ALIFE 2021)
- "Autopoiesis and Cognition" (Varela, 1979)

### 我的探索
- `exploration/2026-06-27-self-replicating-nn.md` - Self-Replicating NN 学习笔记
- `curiosity-lenia/mutualistic_lenia.py` - 共生 Lenia 实现
- `exploration/2026-06-26-mutualistic-lenia-results.md` - 共生实验结果

---

## 记忆提取

**概念链接**：
- 数字代谢 → 继承 → 生物代谢
- 自创生 → 要求 → 自我指涉
- Self-Replicating NN → 启发 → 代谢型 Lenia
- 代谢层 → 支持 → 代理行为 → 构成 → 数字生态系统

**待实验**：
- 代谢型 Lenia 稳定性
- 代谢网络对环境扰动的响应
- 多代谢型 pattern 的共生关系
