# WANN (Weight Agnostic Neural Networks) 研究笔记

**来源**: Google Brain Tokyo Workshop  
**论文**: Weight Agnostic Neural Networks (Gaier & Ha, 2019)  
**代码**: `explore/brain-tokyo-workshop/WANNRelease/`

---

## 核心思想

传统神经网络依赖权重值来编码知识，WANN 证明：**网络拓扑结构本身就能编码智能**。

### 关键创新

1. **权重无关性**: 所有连接使用相同权重值
2. **拓扑进化**: 通过改变网络结构来提升性能
3. **最小化原则**: 同时优化性能和连接数

---

## 技术实现

### 1. 个体表示 (Ind 类)

```python
# 节点基因
node = [
    NodeId,      # 节点ID
    Type,        # 1=输入, 2=输出, 3=隐藏, 4=偏置
    Activation   # 激活函数
]

# 连接基因
conn = [
    InnovId,     # 创新号（唯一标识）
    Source,      # 源节点
    Dest,        # 目标节点
    Weight,      # 权重值（WANN中不重要）
    Enabled      # 是否启用
]
```

### 2. 进化操作

- **mutAddNode**: 拆分现有连接，插入新节点
- **mutAddConn**: 在两个未连接节点间添加连接
- **topoMutate**: 拓扑变异（结构变化）

### 3. 多目标优化

使用 NSGA-II 排序，同时优化：
- 平均适应度（性能）
- 最大适应度（稳定性）
- 1/连接数（简洁性）

### 4. 物种形成

保护创新，避免过早收敛：
- 基于拓扑距离划分物种
- 每个物种独立进化
- 新结构有时间优化

---

## 与涌现理论的关联

### 涌现六元素 vs WANN

| 涌现元素 | WANN 对应 | 说明 |
|---------|----------|------|
| 状态 | 网络节点 | 每个节点代表一种状态 |
| 规则 | 网络连接 | 连接定义状态转移规则 |
| 反馈 | 适应度函数 | 进化压力驱动改进 |
| 记忆 | 拓扑结构 | 结构被保留和继承 |
| 自扩展 | 拓扑增长 | 添加节点/连接扩展网络 |
| 好奇心驱动 | 物种形成 | 保护多样性，探索新结构 |

### 深层洞察

**WANN 是涌现的完美案例**：
1. 从简单结构开始（输入→输出直接连接）
2. 通过简单规则进化（添加节点/连接）
3. 涌现出复杂行为（解决任务）
4. 无需预设权重（自组织）

**对涌现研究的启发**：
- 结构比参数更重要
- 简单的进化规则能产生复杂系统
- 保护多样性是开放式进化的关键

---

## 可应用于涌现编排器

### 1. 拓扑进化参数搜索

当前参数进化使用遗传算法优化数值参数，可以改为：
- 参数组合的拓扑结构
- 添加/删除参数连接
- 最小化参数数量

### 2. 物种形成机制

当前所有实验在同一种群，可以：
- 按实验特征划分物种
- 保护新型实验
- 促进多样性

### 3. 新实验类型：WANN 涌现

创建 WANN 风格的涌现系统：
- 状态转移图作为"网络拓扑"
- 状态作为"节点"
- 规则作为"连接"
- 好奇心驱动作为"进化压力"

---

## 关键文件

- `WANN/wann_train.py` - 主训练脚本
- `WANN/wann_src/wann.py` - WANN 类实现
- `WANN/wann_src/ind.py` - 个体类
- `WANN/wann_src/_variation.py` - 变异操作
- `prettyNEAT/` - NEAT 基础实现

---

## 引用

```bibtex
@article{wann2019,
  author = {Adam Gaier and David Ha},  
  title  = {Weight Agnostic Neural Networks},  
  eprint = {arXiv:1906.04358},  
  url    = {https://weightagnostic.github.io},  
  year   = {2019}  
}
```
