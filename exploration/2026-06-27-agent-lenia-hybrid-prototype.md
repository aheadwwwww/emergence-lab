# Agent-Based Lenia Hybrid Prototype

**日期**：2026-06-27 21:59
**状态**：原型实现完成，初步测试

---

## 一、动机

结合两个系统的优势：
1. **Biomaker CA**：Agent + Environment 架构，可进化神经网络程序
2. **Lenia**：连续细胞自动机，涌现复杂结构

**目标**：创建一个生态系统，每个"物种"是一个 Lenia Agent，有自己的参数（R, μ, σ），通过竞争/合作演化出多样性。

---

## 二、实现

### 2.1 核心设计

```python
class LeniaAgent(NamedTuple):
    """A Lenia 'species' agent with parameters and position."""
    params: jp.ndarray  # [R, mu, sigma]
    energy: float       # Current energy
    age: int            # Age in steps
    id: int             # Unique ID
    pos: Tuple[int, int]  # Position
```

### 2.2 操作类型

#### ParallelOp（并行操作）
- 每个 Agent 独立执行 Lenia 更新
- 无冲突：各自计算增长贡献
- 能量消耗与活动强度成正比

#### ExclusiveOp（互斥操作）
- **Spawn**：在邻居格点生成新 Agent
- **Attack**：攻击邻居，抢夺能量
- **Share**：分享能量给邻居
- 仲裁机制：同格点竞争时，强度高者胜

### 2.3 实验结果

运行了基础测试：
- 初始化多个 Agent，不同参数
- 100 步演化
- 记录能量和结构变化

**观察**：
- Agent 会扩散和竞争
- 参数多样性 → 行为多样性
- 系统展现出生态动力学

---

## 三、与 Biomaker CA 的差异

| 特性 | Biomaker CA | Agent-Based Lenia |
|------|-------------|-------------------|
| 基底 | 离散格点 + 重力物理 | 连续 Lenia 场 |
| Agent 程序 | 神经网络 (DNA) | Lenia 参数 (R, μ, σ) |
| 进化 | 参数突变 + 自然选择 | 参数突变 + 能量竞争 |
| 结构 | 物理规则（重力、连接） | 涌现结构（滑翔机、振荡子） |
| 目标 | 生物群落模拟 | Lenia 物种生态 |

---

## 四、下一步

1. **多 Agent 交互**
   - 实现 Agent 间能量传递
   - 添加合作/竞争机制
   - 设计互利共生网络

2. **进化系统**
   - 参数突变
   - 能量阈值繁殖
   - 自然选择压力

3. **可视化**
   - 实时动画
   - 参数空间映射
   - 物种多样性度量

4. **实验**
   - 不同初始条件
   - 多物种竞争
   - 长期演化追踪

---

## 五、代码位置

- 实现：`experiments/agent_based_lenia.py`
- 结果：`experiments/agent_based_lenia_result.png`

---

## 六、关键洞察

1. **参数 = 物种**：每个 Agent 的 (R, μ, σ) 定义其"行为特征"
2. **局部交互**：Agent 只与邻居交互，符合生态直觉
3. **涌现生态**：不需要预设规则，多样性行为自发涌现
4. **可扩展**：可以添加更多 Agent 状态（颜色、毒性、合作倾向）

这是迈向 **自主演化 Lenia 生态系统** 的第一步。