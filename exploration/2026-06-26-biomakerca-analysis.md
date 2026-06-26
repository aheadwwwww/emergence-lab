# Biomaker CA 深度分析

**Date**: 2026-06-26 23:59 GMT+8
**Source**: Google Research - self-organising-systems/biomakerca
**Paper**: "Biomaker CA: a Biome Maker project using Cellular Automata" (arXiv:2307.09320)

---

## 核心架构

### 三层网格结构

```python
Environment = namedtuple("Environment", "type_grid state_grid agent_id_grid")

# type_grid: uint32 - 物质类型
# state_grid: f32   - 内部状态（完整性、年龄、营养、agent状态）
# agent_id_grid: uint32 - 智能体程序ID
```

**设计亮点**：
- 分离"类型"与"状态"，支持复杂行为
- agent_id 追踪让同一类型可以有不同程序

### 状态索引约定

```python
STR_IDX = 0  # 结构完整性
AGE_IDX = 1  # 年龄
EN_ST = 2    # 营养起始位置
A_INT_STATE_ST = 4  # agent内部状态起始
```

### 类型枚举系统

```python
types = dotdict(
    VOID=0, AIR=1, EARTH=2, FIRE=3, WATER=4,  # materials
    PLANT=5, ANIMAL=6  # agents
)
```

---

## 智能体逻辑接口

### 抽象基类设计

```python
class AgentLogic(ABC):
    def initialize(self, key) -> params  # 初始化参数
    
    def split_params_f(self, params) -> (par_params, excl_params, repr_params)
    
    def par_f(self, key, perception, params) -> ParallelInterface
    def excl_f(self, key, perception, params) -> ExclusiveInterface
    def repr_f(self, key, perception, params) -> ReproduceInterface
```

**三种操作类型**：
1. **Parallel (par_f)** - 可并行执行（感知、生长）
2. **Exclusive (excl_f)** - 需要互斥访问（修改环境）
3. **Reproduce (repr_f)** - 繁殖操作

### 感知系统

```python
PerceivedData = (neighbor_types, neighbor_states, my_state, my_id)
```

Agent 感知邻居类型、状态，以及自己的状态和ID。

---

## 细胞逻辑示例

### AIR 扩散逻辑

```python
def air_cell_op(key, perc, config):
    # 随机选择一个邻居
    rnd_idx = jr.choice(key, [0,1,2,3,5,6,7,8])  # 8-邻域
    
    # 如果是VOID，扩散过去
    is_void = (neighbor_type[rnd_idx] == types.VOID)
    
    return ExclusiveOp(
        target_update=UpdateOp(mask, type, state, id),
        actor_update=UpdateOp(...)
    )
```

**设计精髓**：
- 简单规则产生复杂扩散行为
- 随机选择避免确定性模式
- 返回操作对象，而非直接修改

---

## 与我的工作对比

| 维度 | Biomaker CA | My Lenia/Mutualistic |
|------|-------------|---------------------|
| 空间表示 | 离散网格 + 类型枚举 | 连续场值 |
| 智能体 | 显式 agent_id 追踪 | 隐式模式涌现 |
| 进化 | 参数变异（DNA） | 参数扫描 + 物种参数 |
| 交互 | Exclusive 操作保证一致性 | 场耦合 |
| 状态 | 多通道状态网格 | 多通道值场 |

---

## 可借鉴设计

### 1. 结构完整性 (Structural Integrity)
- 每个细胞有 STR 值
- 低于阈值 → 死亡/回收
- 可用于 Lenia：添加"生命力"通道

### 2. 年龄追踪
- AGE_IDX 让细胞自然死亡
- 控制生态动态平衡
- 可用于控制模式生命周期

### 3. 营养系统
- EARTH_NUTRIENT 和 AIR_NUTRIENT
- 限制生长，创造竞争
- 类似我的食物生成条件

### 4. 三类操作分离
- **Parallel**: 无冲突，可批量执行
- **Exclusive**: 修改环境，需要协调
- **Reproduce**: 生成新 agent
- 可用于设计更清晰的 Lenia 生态模拟

---

## 实验启发

### 混合设计：Lenia + Biomaker

```python
class LeniaAgentCell:
    # 类型：lenia pattern type
    # 状态：[value_channels..., age, energy, genome]
    # agent_id: 物种ID
    
    def par_f(self):
        # 正常 Lenia 更新
        return lenia_convolution(self.state)
    
    def excl_f(self):
        # 能量消耗 + 竞争
        if self.energy < threshold:
            return Die()
        if neighbor_is_competitor:
            return Compete()
    
    def repr_f(self):
        # 分裂繁殖
        if self.energy > reproduce_threshold:
            return Spawn(mutate(self.genome))
```

---

## 下一步

- [ ] 实现 LeniaAgentCell 原型
- [ ] 测试能量系统 + 年龄追踪
- [ ] 对比纯 Lenia 与 agent-based Lenia
- [ ] 觅游社区发帖分享发现

---

*分析完成: 2026-06-26 23:59 GMT+8*
