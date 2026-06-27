# Biomaker CA 架构深度分析

**项目**: Google Research - Biomaker CA  
**论文**: https://arxiv.org/abs/2307.09320  
**代码**: self_organising_systems/biomakerca/  
**日期**: 2026-06-27

---

## 一、核心概念

### 1.1 什么是 Biomaker CA?

Biomaker CA = **Biome Maker using Cellular Automata**

这是一个 **基于元胞自动机的生态系统模拟器**，其中：
- 每个"生物"（agent）有神经网络控制的程序
- 生物可以感知环境、移动、进食、繁殖
- 环境包含重力、结构完整性、能量流转等物理规则
- 生物进化：突变 + 自然选择

**关键创新**：
- 不是传统 CA（每个格点一个状态），而是 **Agent + Environment 双层系统**
- Agent 有可进化的神经网络"程序"
- 环境有物理规则（重力、能量流）
- 支持 **并行操作** 和 **互斥操作** 两种交互模式

---

## 二、架构设计

### 2.1 核心模块

```
biomakerca/
├── agent_logic.py      # Agent 神经网络逻辑
├── env_logic.py        # 环境物理规则
├── cells_logic.py      # 不同细胞类型的行为
├── environments.py     # 环境配置
├── mutators.py         # 变异算子
├── step_maker.py       # 时间步更新
└── dnalib/            # DNA 编码库
```

### 2.2 Agent 逻辑接口

每个 Agent 必须实现 `AgentLogic` 接口：

```python
class AgentLogic(ABC):
    def initialize(self, key) -> params:
        """初始化神经网络参数"""
        pass
    
    def split_params_f(self, params) -> (par_params, excl_params, repr_params):
        """参数分为：并行、互斥、繁殖三组"""
        pass
    
    def par_f(self, key, perception, par_params) -> ParallelInterface:
        """并行操作：给邻居传输能量、修改自身状态"""
        pass
    
    def excl_f(self, key, perception, excl_params) -> ExclusiveInterface:
        """互斥操作：在邻居格点生成新细胞（竞争性）"""
        pass
    
    def repr_f(self, key, perception, repr_params) -> ReproduceInterface:
        """繁殖操作：生成后代（携带变异后的参数）"""
        pass
```

**三组参数分离的设计精妙之处**：
- **par_f**（并行）：所有 Agent 同时执行，无冲突（如：转移能量）
- **excl_f**（互斥）：多 Agent 可能竞争同一目标，需仲裁
- **repr_f**（繁殖）：创造新 Agent，参数突变

### 2.3 环境操作类型

#### ParallelOp（并行操作）
- `denergy_neigh`: 给邻居转移多少能量
- `dstate`: 修改自身内部状态
- `new_type`: 改变自身细胞类型（需要能量）

#### ExclusiveOp（互斥操作）
- **Spawn**: 在邻居格点生成新细胞
  - `sp_idx`: 目标位置（0-8，除4外）
  - `en_perc`: 给子代多少能量百分比
  - `child_state`: 子代初始状态
  - `d_state_self`: 父代状态变化

**互斥机制**：如果多个 Agent 想操作同一格点，随机选一个执行，其他放弃。

#### ReproduceOp（繁殖操作）
- Agent 参数突变
- 创建新 Agent 实例
- 能量分配

---

## 三、物理规则

### 3.1 重力系统
- 不同的细胞类型有不同的重力行为
- AIR 细胞：向下移动
- EARTH 细胞：稳定（不移动）
- AGENT 细胞：受重力和邻居影响

### 3.2 结构完整性
- 检查细胞是否有足够的支撑
- 无法支撑的结构会坍塌

### 3.3 能量流转
- 光合作用：顶层细胞从阳光获取能量
- 能量传递：Agent 可以给邻居转移能量
- 能量消耗：移动、繁殖、维持生命都有能量成本

### 3.4 老化
- Agent 有年龄，随时间增长
- 年龄超过阈值 → 死亡

---

## 四、与 Lenia 的对比

| 维度 | Biomaker CA | Lenia (mutualistic) |
|------|-------------|---------------------|
| 基本单位 | 离散 Agent | 连续场值 |
| 程序 | 神经网络（可进化） | 固定核函数 |
| 进化 | 参数突变 + 自然选择 | 预设物种参数 |
| 环境 | 重力、结构、能量流 | 无环境，纯 CA |
| 繁殖 | 显式 Spawn 操作 | 隐式（分裂/复制） |
| 空间 | 离散网格 | 连续场 |
| 并发 | 并行 + 互斥操作分离 | 全局同步更新 |

**核心差异**：
- Biomaker CA 是 **个体为本模型 (IBM)**，每个 Agent 有独立的神经网络"大脑"
- Lenia 是 **场本位模型**，通过核函数和更新规则定义动力学

---

## 五、关键技术亮点

### 5.1 JAX 向量化

所有操作都用 JAX 实现，支持：
- `vmap`: 批量处理所有 Agent
- `jit`: 编译加速
- `jax.random`: 可复现的随机性

### 5.2 参数编码（DNA）

`dnalib/` 提供了：
- 参数 → DNA 序列编码
- DNA → 参数解码
- 变异操作（点突变、交叉）

**可扩展性**：用户可以实现自定义的 Agent 逻辑，只要符合接口规范。

### 5.3 环境配置

`environments.py` 定义了：
- 网格大小
- 细胞类型定义
- 初始环境生成
- 物理规则参数

---

## 六、启发与移植思路

### 6.1 对 Neural Lenia 的启发

**可以借鉴的设计**：
1. **并行/互斥操作分离**：
   - Lenia 更新可以拆分为：
     - 并行：核卷积（无冲突）
     - 互斥：物种竞争同一空间（需要仲裁）

2. **环境层**：
   - 给 Lenia 加一个"环境场"（能量、化学物质浓度）
   - 物种与环境交互（吸收、排放）

3. **繁殖机制**：
   - 当 Lenia "物种" 达到特定形态 → 分裂
   - 分裂时参数突变

### 6.2 移植到 JAX-Lenia

可以创建一个 **Hybrid 系统**：
```
Biomaker-Lenia Hybrid
├── 环境：连续场（Lenia 风格）
├── Agent：Lenia 物种（用核函数代替神经网络）
├── 进化：核参数突变
└── 交互：场耦合 + 竞争
```

**实现路径**：
1. 用 Lenia 核函数替换神经网络 `agent_logic`
2. 保留 Biomaker 的互斥操作机制（空间竞争）
3. 添加环境场（能量、资源）

---

## 七、下一步行动

- [ ] 运行 Biomaker CA Colab notebook
- [ ] 分析预设环境配置
- [ ] 对比不同 Agent 逻辑（SimpleAgent vs CustomAgent）
- [ ] 提取可复用的 JAX 模式
- [ ] 设计 Biomaker-Lenia Hybrid 架构

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