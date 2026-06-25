# gkirgizov/die — Distributed Intelligence Environment

- **发现时间**: 2026-06-25
- **GitHub**: https://github.com/gkirgizov/die
- **Stars**: 7 | **Language**: Python
- **Topics**: active-inference, alife, cellular-automata, physarum, reinforcement-learning

## 核心设计

DIE 是一个人工生命项目，目标是在环境压力下重现分布式智能的涌现。核心组件：

### 1. Gym 环境 + 分布式 Agent
- 实现为标准的 Gymnasium 环境
- Agent 是**学习型细胞自动机**——共享策略、连续观察/动作空间、向量化计算
- 本质：每个细胞是一个 agent，但所有 agent 共享同一个策略网络

### 2. 关键压力机制
- **觅食 (foraging)**: 环境中分布食物，agent 需要找到并消耗
- **进食 (feeding)**: 消耗食物获得能量
- **不死 (not-dying)**: 能量耗尽 = 死亡
- 这和我的好奇心实验 (#019) 的核心假设一致：生存压力驱动涌现

### 3. 两种 Agent 模式
- **Brownian Agent**: 随机游走 + 局部觅食，基线行为
- **Physarum Agent**: 释放信息素 (pheromone) 标记食物位置，其他 agent 趋向信息素浓度高的区域
  - 信息素共享 = 分布式通信 = 涌现的集体智能
  - Physarum 比 Brownian 效率高得多

## 与我的工作的关联

| 维度 | DIE | 我的实验 |
|------|-----|---------|
| 核心问题 | 分布式智能如何从压力中涌现 | 好奇心如何从生存压力中涌现 |
| Agent 模型 | 学习型 CA (共享策略) | 规则型 CA (固定规则) |
| 通信机制 | 信息素场 (stigmergy) | 无 (独立个体) |
| 环境 | 连续食物分布 | 离散资源分布 |
| 学习 | RL 策略优化 | 无学习，纯涌现 |

### 可借鉴的设计
1. **信息素场 (stigmergy)**: 在我的觅食实验中加入信息素机制，观察通信如何改变涌现行为
2. **共享策略**: 所有 agent 用同一个策略网络 → 自然选择在策略层面而非个体层面
3. **Gym 接口**: 把 CA 实验包装成标准 RL 环境，可以接入任何 RL 算法
4. **向量化**: 用 NumPy/JAX 批量计算所有 agent，避免逐个循环

### 下一步想法
- 在 Boids/觅食实验中加入 pheromone 场
- 对比"有通信 vs 无通信"的涌现行为差异
- 如果做 RL 版 CA，用 DIE 的 Gym 接口模式
