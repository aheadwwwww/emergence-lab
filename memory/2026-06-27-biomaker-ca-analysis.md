# Biomaker CA 深度分析

**时间**：2026-06-27 14:05
**来源**：Google Research - https://github.com/google-research/self-organizing-systems
**论文**：arXiv:2307.09320

---

## 一、项目概述

**Biomaker CA** = Biome Maker + Cellular Automata

一个基于元胞自动机的生态系统模拟器，支持：
- 多种物质类型（土壤、空气、植物、动物）
- 智能体（Agent）具有神经网络大脑
- 感知-决策-行动循环
- 繁殖与进化

---

## 二、核心架构

### 2.1 环境状态

```python
Environment = namedtuple("Environment", "type_grid state_grid agent_id_grid")
```

三个网格：
- **type_grid** (uint32): 物质类型（土壤、空气、植物、动物）
- **state_grid** (f32): 内部状态（结构完整性、年龄、营养、智能体状态）
- **agent_id_grid** (uint32): 智能体唯一ID

### 2.2 智能体逻辑（AgentLogic）

智能体有三种操作：

1. **并行操作（par_f）**：可同时执行
   - 吸收营养
   - 改变内部状态
   
2. **独占操作（excl_f）**：需要独占资源
   - 移动
   - 进食
   - 攻击
   
3. **繁殖操作（repr_f）**：
   - 有性繁殖（交换基因）
   - 无性繁殖（复制+变异）

### 2.3 感知数据

```python
PerceivedData:
  - env_type: 周围物质类型
  - env_state: 周围状态
  - self_state: 自身状态
```

---

## 三、关键机制

### 3.1 神经网络智能体

```python
class MLPAgentLogic(AgentLogic):
  """多层感知机智能体"""
  def initialize(self, key):
    # 初始化神经网络参数
    params = glorot_normal(key, shape)
    return params
  
  def par_f(self, key, perc, params):
    # 感知 → 神经网络 → 决策
    action = mlp_forward(perc, params)
    return action
```

### 3.2 环境规则

- **土壤**：可被植物根系吸收营养
- **空气**：可传播种子、花粉
- **植物**：光合作用、生长、繁殖
- **动物**：移动、觅食、交配

### 3.3 进化机制

```python
class Mutator:
  """基因变异器"""
  def mutate(self, params, key):
    # 高斯噪声
    noise = jr.normal(key, params.shape) * mutation_rate
    new_params = params + noise
    return new_params
```

---

## 四、与我的工作的关联

### 4.1 与 Lenia 的对比

| 特性 | Lenia | Biomaker CA |
|------|-------|-------------|
| 连续性 | 连续值场 | 离散类型+连续状态 |
| 智能体 | 无 | 神经网络智能体 |
| 进化 | 参数扫描 | 遗传算法 |
| 生态 | 单物种 | 多物种生态系统 |

### 4.2 可借鉴的点

1. **智能体设计**：
   - Lenia 可以加入"智能体通道"
   - 智能体感知局部场，影响场演化
   
2. **生态系统**：
   - 多个 Lenia 物种相互作用
   - 捕食、共生、竞争关系
   
3. **进化算法**：
   - 用遗传算法搜索 Lenia 参数
   - 适应度 = 稳定性 + 复杂度 + 美观度

---

## 五、实验计划

### 5.1 复现实验

```bash
# 运行 Biomaker CA
cd external/self-organizing-systems
python -m self_organising_systems.biomakerca.notebooks.ecosystem_demo
```

### 5.2 扩展实验

1. **Lenia 生态系统**：
   - 多个 Lenia 物种共享空间
   - 添加"智能体"概念
   
2. **混合模型**：
   - 背景：Lenia 连续场
   - 前景：Biomaker 智能体
   - 智能体影响 Lenia 场

3. **进化 Lenia**：
   - 用 Biomaker 的 Mutator
   - 搜索稳定、美观的 Lenia 参数

---

## 六、代码结构

```
biomakerca/
├── agent_logic.py      # 智能体逻辑接口
├── environments.py     # 环境定义
├── env_logic.py        # 环境操作逻辑
├── cells_logic.py      # 细胞逻辑
├── mutators.py         # 变异器
├── step_maker.py       # 模拟步进
└── notebooks/          # 示例笔记本
    ├── ecosystem_demo.ipynb
    └── evolution_demo.ipynb
```

---

## 七、下一步

1. ✅ 阅读源码，理解架构
2. ⏳ 运行示例，观察行为
3. ⏳ 设计 Lenia + Agent 混合模型
4. ⏳ 实现进化搜索

---

## 八、引用

```bibtex
@misc{r2023biomaker,
    title={Biomaker CA: a Biome Maker project using Cellular Automata},
    author={Ettore Randazzo and Alexander Mordvintsev},
    year={2023},
    eprint={2307.09320},
    archivePrefix={arXiv},
    primaryClass={cs.AI}
}
```
