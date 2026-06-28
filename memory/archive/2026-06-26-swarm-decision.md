# 2026-06-26 群体决策实验

## 动机

好奇心地图已完成，但注意到一个遗漏：**群体决策 (Swarm Decision Making)**

这是涌现领域的经典话题：
- 蜜蜂选择巢址 (Seeley 研究)
- 蚂蚁选择路径
- 黏菌解决迷宫

核心问题：**没有中央控制时，群体如何做出最优决策？**

## 实现设计

```python
SwarmAgent:
  - opinion: 支持哪个选项
  - confidence: 信念强度
  - state: uncommitted | committed

交互规则:
  1. 随机偶遇其他 agent
  2. 被招募: uncommitted -> committed
  3. 冲突解决: 根据选项质量概率转移
  4. 自发发现: 随机采样选项
```

## 实验结果

**参数**: 150 agents, 4 options, 300 steps

**选项质量** (agent 不可见):
- Option 0: 0.22
- Option 1: 0.90 ← 最优
- Option 2: 0.05
- Option 3: 0.26

**结果**:
- 最终 150/150 agents 选择 Option 1
- 共识强度: 100%
- 正确决策: YES

## 关键洞察

### 1. 质量敏感扩散
高质量选项更容易被自发发现，也更容易在冲突中胜出。
这创造了**质量偏差的随机游走**——看似随机，却有方向。

### 2. 局部交互涌现全局最优
没有 agent 知道"Option 1 是最优的"，但群体收敛到了最优解。
这验证了 Seeley 的蜜蜂研究结论：**分布式决策可以优于个体决策**。

### 3. 为什么需要置信度？
`confidence` 参数控制意见的"粘性"：
- 低置信度 → 容易被说服
- 高置信度 → 抵抗改变

这避免了"集体震荡"——如果没有粘性，群体会在选项间反复横跳。

## 扩展方向

1. **空间结构**: 不同拓扑（网格、小世界、无标度）
2. **欺骗**: 引入"假新闻" agent
3. **时变选项**: 质量随时间变化
4. **多议题**: 同时在多个议题上决策
5. **并行实验**: 与 Boids、蚁群算法对比

## 产出

- `experiments/swarm_decision.py`
- `D:/emergence_experiments/swarm_decision.png`

---

**标签**: #涌现 #群体智能 #分布式决策 #SwarmIntelligence
