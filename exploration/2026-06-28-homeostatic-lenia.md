# Homeostatic Lenia - 基于预测处理的涌现

**日期**: 2026-06-28
**灵感来源**: xagent (free energy principle)

## 核心思想

传统Lenia优化外部奖励（存活率），Homeostatic Lenia让模式通过最小化内部惊奇自组织。

基于 Karl Friston 的自由能量原理：
- 生物体不优化"奖励"，而是最小化"惊奇"
- 预测与现实之间的误差驱动行为
- 稳态维持是唯一的评价标准

## 实现机制

```python
# 1. 跟踪"期望状态"（过去状态的滚动平均）
expected_state = alpha * new_state + (1-alpha) * expected_state

# 2. 计算惊奇
surprise = ||new_state - expected_state||^2

# 3. 稳态压力
homeostatic_correction = 0.01 * (expected_state - new_state)

# 4. 混合更新
corrected_state = new_state + homeostatic_correction
```

## 实验结果

### 参数组测试 (R=15, 500步)

| 参数 | 最终惊奇 | 最终存活率 | 观察 |
|------|----------|------------|------|
| mu=0.15, sigma=0.015 | 0.01 | 0% | 快速死亡，稳态失效 |
| mu=0.22, sigma=0.04 | 86.88 | 30.7% | 惊奇先升后降，存活稳定 |
| mu=0.30, sigma=0.06 | 41.95 | 40.8% | 惊奇峰值最高，存活率最高 |

### 关键发现

1. **稳态压力帮助稳定**：高mu参数组通过稳态校正维持了40%存活率
2. **惊奇曲线非单调**：先上升（模式扩张），后下降（稳态收敛）
3. **死亡模式**：低mu参数无法维持活性，稳态压力不足以挽救

## 与标准Lenia对比

| 维度 | 标准Lenia | Homeostatic Lenia |
|------|-----------|-------------------|
| 评价信号 | 外部（存活率） | 内部（惊奇） |
| 驱动力 | 规则+初始条件 | 规则+稳态压力 |
| 自适应性 | 固定参数 | 滚动期望 |
| 理论基础 | 连续CA | 自由能量原理 |

## 与xagent的联系

xagent的7阶段预测处理流水线：
```
feature_extract → encode → habituate_homeo → recall_score → recall_topk → predict_and_act → learn_and_store
```

Homeostatic Lenia简化版：
```
state → kernel_convolution → growth → homeostatic_correction → new_state
```

xagent使用多尺度稳态监控器（快速/中速/慢速），Homeostatic Lenia只用单一时间尺度（alpha参数）。

## 下一步方向

1. **多尺度稳态**：引入快/中/慢三个alpha参数
2. **预测性稳态**：不只是跟随期望，而是预测期望变化
3. **物种竞争**：多个Homeostatic Lenia模式竞争资源
4. **元学习**：让alpha参数自己通过稳态压力调整

## 代码位置

`experiments/homeostatic_lenia.py`

## 参考

- xagent: https://github.com/koraytaylan/xagent
- Friston, K. (2010). The free-energy principle: a unified brain theory?
- Chan, B. (2019). Lenia - Biology of Artificial Life
