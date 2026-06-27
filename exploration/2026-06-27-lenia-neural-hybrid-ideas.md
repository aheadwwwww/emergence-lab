# Lenia-Neural Hybrid 构想

**日期**: 2026-06-27
**状态**: 早期探索

---

## 核心想法

结合 **Biomaker CA** 的 Agent-based 架构和 **Lenia** 的连续场动力学，创建一个混合系统。

---

## 设计方案

### 方案 A: Agent-Lenia

```
环境层: Lenia 连续场（资源/能量）
Agent层: 可移动的 Lenia 物种（核函数定义）
交互: Agent 摄取环境能量，影响环境场
进化: 核参数突变
```

**优势**:
- Agent 个体性（可追踪、可进化）
- 环境连续性（Lenia 的优美动力学）
- 两层耦合涌现复杂行为

**挑战**:
- Agent 在连续场中如何移动？
- 离散网格 vs 连续场的冲突

### 方案 B: Neural-Lenia v2

```
扩展现有 Neural Lenia:
1. 多物种共存（竞争/合作）
2. 环境场（能量、化学物质）
3. 繁殖机制（达到阈值 → 分裂）
4. 参数进化（遗传算法）
```

**优势**:
- 基于现有代码
- 渐进式改进

**挑战**:
- 繁殖如何实现？
- 如何避免所有物种灭绝？

### 方案 C: Lenia-Ecosystem

```
完全离散化:
- 网格化 Lenia（保留核函数思想）
- 每个格点可以有多个"物种"占据
- 竞争机制：胜者占据
- 繁殖：分裂到邻居
```

**优势**:
- 实现简单
- 易于并行化

**挑战**:
- 失去 Lenia 的连续性美感

---

## 技术要点

### 从 Biomaker CA 借鉴

1. **并行/互斥操作分离**
   - 并行: 能量转移、场更新
   - 互斥: 空间竞争、繁殖

2. **参数编码与变异**
   - DNA 序列编码核参数
   - 点突变、交叉

3. **环境物理**
   - 能量守恒
   - 扩散、衰减

### 从 Lenia 保留

1. **核函数**
   - R kernel: 空间范围
   - K kernel: 形状函数
   - G growth function: 增长规则

2. **更新规则**
   ```
   A(t+1) = A(t) + dt * (G(K*A(t)) - A(t))
   ```

---

## 下一步实验

- [ ] 运行 Lenia Tutorial notebook
- [ ] 实现 Agent-Lenia 原型
- [ ] 测试繁殖机制
- [ ] 可视化演化过程

---

## 参考

- Biomaker CA: https://arxiv.org/abs/2307.09320
- Lenia Tutorial: https://github.com/OpenLenia/Lenia-Tutorial
- Neural Lenia (我的实验): experiments/neural_lenia.py
