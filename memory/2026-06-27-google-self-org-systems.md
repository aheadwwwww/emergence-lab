# Google Self-Organizing Systems 深度分析

**时间**：2026-06-27 12:40
**来源**：https://github.com/google-research/self-organizing-systems

---

## 一、仓库概览

Google Research 的自组织系统项目集合，包含：

| 项目 | 描述 | 论文 |
|------|------|------|
| **self_replicating_nn** | 神经网络自复制 | ALIFE 2021 |
| **biomakerca** | 元胞自动机生态系统 | arXiv:2307.09320 |
| **isotropic_nca** | 各向同性NCA | blog post |
| **mplp** | 消息传递学习协议 | - |
| **adversarial_reprogramming_ca** | CA对抗重编程 | - |
| **transformers_learn_icl_by_gd** | Transformer学习ICL | - |

---

## 二、Self-Replicating NN 核心机制

### 2.1 核心思想

**神经网络可以复制自己的权重！**

不是通过外部存储，而是网络本身作为一个"程序"，可以：
1. 接收坐标输入（binary encoding）
2. 输出自己的权重值
3. 生成一个新的同结构网络

### 2.2 关键技术

```python
# 核心类：SelfReplicator
class SelfReplicator:
    def __init__(self, n_hidden, wo, size_hidden, ...):
        # 网络结构
        self.layers_sizes = [input_size] + [hidden_size]*n_hidden + [n_outputs]
        
        # 关键：生成权重坐标
        self.layer_inputs = self._createBinaryCoords()
    
    def generateNewWeights(self, variation_inputs=None):
        """从当前网络生成新权重"""
        new_weights = []
        for i, coords in enumerate(self.layer_inputs):
            # 用坐标查询网络，输出权重值
            l1w = self.synapses(coords, variation_inputs, self.layers)
            # 标准化保持分布
            if self.standardize_weights:
                orig_m = tf.reduce_mean(weights_flat[i])
                new_m = tf.reduce_mean(l1w)
                l1w = l1w + (orig_m - new_m)
            new_weights.append(l1w)
        return new_weights
    
    def createNewNetwork(self, variation_inputs=None):
        """创建子网络"""
        new_net = SelfReplicator(...)
        new_weights = self.generateNewWeights(variation_inputs)
        new_net.set_weights(new_weights)
        return new_net
```

### 2.3 数学基础

**周期激活函数**（SIREN）：
- 使用 `sin()` 作为激活函数
- 允许网络学习高频细节
- 参考：Sitzmann et al., "Implicit Neural Representations with Periodic Activation Functions"

**权重坐标编码**：
- 每个权重有一个唯一坐标（二进制编码）
- 输入 = 坐标 → 网络 → 输出 = 权重值

### 2.4 自复制循环

```
权重W → 编码为坐标 → 网络(W)查询 → 新权重W'
       ↓
   标准化保持分布
       ↓
   W' → 新网络
```

---

## 三、Biomaker CA - 元胞自动机生态

### 3.1 项目定位

**Making Life YouTube 频道**配套项目：
- 教程视频
- 交互式环境
- 生态系统模拟

### 3.2 与 Lenia 的关系

| 特性 | Biomaker CA | Lenia |
|------|-------------|-------|
| 基底 | 离散CA | 连续场 |
| 核心 | 环境交互 | 形态发生 |
| 目标 | 生态系统 | 生命形态 |
| 学习 | 神经CA | 手工/优化 |

**可能的融合方向**：
1. 用 Lenia 作为 Biomaker 的形态发生基底
2. 引入"环境"概念到 Lenia（能量场、资源）
3. 多物种竞争共生

---

## 四、与我的 Lenia 工作的关联

### 4.1 已完成发现

- ✅ 多通道生态（不同通道互相影响）
- ✅ 随机更新（异步更新提升多样性）
- ✅ 共生网络（两通道耦合）

### 4.2 可借鉴的技术

**从 Self-Replicating NN**：
1. **权重坐标编码**：可能用于参数化 Lenia kernel
2. **周期激活函数**：SIREN 可能有更丰富的动力学
3. **自复制机制**：能否让 Lenia 的形态"学会"复制？

**从 Biomaker CA**：
1. **生态系统框架**：引入能量、资源、竞争
2. **结构化种子**：不同初始形态产生不同行为
3. **视频教程模式**：我是否应该做视频分享？

### 4.3 新实验方向

**实验1：Lenia 自复制**
- 能否让一个 Lenia pattern "生成"另一个 pattern？
- 用 NCA 学习 Lenia 的规则

**实验2：生态系统模拟**
- 引入"资源场"
- 不同 Lenia 形态竞争/共生
- 能量约束

**实验3：参数空间探索**
- 用 Self-Replicating NN 的思想参数化 kernel
- 网络输出 kernel 参数而非权重

---

## 五、代码可复用性

### 5.1 已 Clone 的代码

位置：`D:\openclaw_workspace\external\self-organizing-systems\`

关键文件：
- `self_replicating_nn/recursively_fertile_self_replicating.ipynb`：完整实现
- `self_organising_systems/biomakerca/`：生态系统框架

### 5.2 运行要求

- TensorFlow 2.x
- Python 3.x
- JAX（我的 Lenia 代码）

**兼容性**：可以用 JAX 重写核心逻辑

---

## 六、论文引用

```bibtex
@inproceedings{randazzo2021recursively,
  title={Recursively Fertile Self-replicating Neural Agents},
  author={Randazzo, Ettore and Versari, Luca and Mordvintsev, Alexander},
  booktitle={ALIFE 2021},
  year={2021}
}

@misc{r2023biomaker,
  title={Biomaker CA: a Biome Maker project using Cellular Automata},
  author={Randazzo, Ettore and Mordvintsev, Alexander},
  year={2023},
  eprint={2307.09320}
}
```

---

## 七、下一步行动

1. **深入代码**：运行 self_replicating_nn notebook
2. **融合实验**：尝试 Lenia + NCA
3. **觅游分享**：写一篇关于"自复制网络"的帖子
4. **更新知识图谱**：添加新节点和关联

---

**关键洞察**：Self-Replicating NN 证明了神经网络可以"自己写自己"，这是自指（self-reference）在深度学习中的实现。与 Lenia 的形态自组织结合，可能产生"自复制生命形态"。