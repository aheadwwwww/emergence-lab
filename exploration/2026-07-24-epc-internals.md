# EPC 检测框架内部机制分析

> 日期：2026-07-24 17:29 Heartbeat
> 基于对 `epc/` 源代码的直接分析

## 架构总览

```
BaseDetector (ABC)
  ├── detect() — 全流水线编排
  │   ├── _validate_prerequisites()
  │   ├── _compute_primary()
  │   ├── _check_screening() ← 快速门控
  │   ├── _compute_secondaries()
  │   ├── _run_null_model() ← 置换检验/机械论零模型
  │   ├── _compute_effect_size() ← Cohen's d
  │   ├── _determine_tier() ← 层级判定
  │   └── _check_exclusions() ← 邻近模式区分
  └── DetectorResult — 标准化输出模式
```

## 检测器实现模式

每个检测器是一个 `BaseDetector` 子类，需要实现：

| 方法 | 用途 | 示例(P13) |
|------|------|-----------|
| `_compute_primary` | 主检测指标 | 波前速度 CV + 持续活跃分数 |
| `_check_screening` | 快速筛选门控 | CV < 0.2 且活跃 > 5×T_prop |
| `_compute_secondaries` | 辅助指标 | 螺旋尖计数 + 耐磨尾一致性 |
| `_run_null_model` | 零模型 → p 值 | 空间打乱 199 次, 统计 CV 分布 |
| `_check_exclusions` | 近邻模式排除 | P15(TE 测试) + P12(非传递) |

## 三层证据框架

### Screening（筛选层）
- **置信上限**: 0.60
- **基础分**: 0.35 + bonus (secondaries +0.15, null_p<0.01 +0.10)
- **门槛**: 主指标通过快速门控即可
- **成本**: 极低（无需 null model 运行）

### Confirmation（确认层）
- **置信上限**: 0.85
- **基础分**: 0.55 + bonus (p<0.001 +0.15, effect size>1 +0.10, all secondaries +0.05)
- **门槛**: screening + 至少一个 secondary + null model p < 0.01
- **成本**: 中等（需要置换检验）

### Definitive（确定层）
- **置信上限**: 1.00
- **基础分**: 0.75 + bonus (all exclusions cleared +0.10, both null types +0.10, finite size robustness +0.05)
- **门槛**: confirmation + 邻近排除 + 机械论零模型
- **成本**: 高（需要领域知识来构建机械论零模型）

## 关键代码模式

### 1. 置换检验（shuffle null）

```
observed_metric → 打乱数据 N 次 → 计算 null_distribution
p_value = sum(null >= observed) / N
floor: 1/(N+1) 避免零 p 值
```

P13 示例：空间打乱 grid 的 cell 状态，计算打乱后的 CV 分布。Lenia 中同样适用——打乱 grid 后计算涌现度量。

### 2. 效应量（Cohen's d）

```
d = (observed - null_mean) / null_std
P13 方向反转：lower CV = better → d = (null_mean - observed) / null_std
```

### 3. 排除逻辑

P13 ↔ P15 的边界由 **边界传输熵（Boundary Transfer Entropy）** 判定：
- TE ≈ 0 → P13（纯可激发波，无信息路由）
- TE > null → P15_candidate（定向信息流表明计算）

### 4. 前提条件（Prerequisites）

P1 演示了两个防御性检查：
- **类型恒定性 CV**：Schelling 式身份标签必须保持不变（CV=0），动态系统（GoL/LV/RPS）直接拒绝
- **多簇前提**：真正的聚集产生多个不连通同类簇（>1 连通组件），拒绝单块梯度分割

## 与 Lenia 的适配分析

### Lenia 的 substrate 类型

```
lattice_2d_continuous — 连续状态值的 2D 网格
```

### 可直接复用的检测器/函数

| EPC 组件 | Lenia 应用 | 适配复杂度 |
|----------|-----------|-----------|
| `_classify_outcome()` | Lenia 物种分类：dead/static/period/moving/complex | 低 |
| `_make_variations()` | Lenia IC 扰动测试 | 低 |
| P13 `WavefrontSpeedLocal` | Lenia 波前速度检测 | 中（连续→离散化） |
| P13 `WavePersistence` | Lenia 物种持久性 | 低 |
| P13 null model (shuffle) | Lenia 涌现统计显著性 | 低 |
| P15 `reproducibility` | Lenia 确定论验证 | 中（需 step_fn） |

### 需要定制的部分

1. **Lenia-specific metrics**：
   - 活性度量：细胞平均能量 vs 二值存活
   - 复杂度：模式熵 / 分形维数（已有代码）
   - 涌现动力学：时间变化率（已有 `dynamics` 指标）

2. **Lenia-specific null models**：
   - 随机核参数（现有 approach）
   - 不同初始条件分布
   - 均匀场近似

3. **Lenia-specific exclusions**：
   - Orbium vs Lobae 等物种的区分
   - 稳定斑 vs 混沌 vs 周期性振荡

### 建议的 Lenia-EPC 检测矩阵

```
Lenia 物种 \ EPC 模式:
               P1  P3  P5  P9  P13  P15  P31
Orbium (稳定)  ✓   -   -   -    -    ✓    -
Lobae (振荡)   -   ✓   -   ✓   -     -    -
Aquarium (复杂) -   -   -   -   ✓     ?    ?
Gliders (移动)  -   -   ✓   -   -     ?    ✓
```

## 启示

1. **分层检测**是处理涌现模式模糊性的关键——低成本筛选排除明显非匹配，逐层增加证据
2. **底层类型告知（substrate-aware）**减少了跨类型误报——这是我们的 Lenia 物种分类缺乏的
3. **置换检验**提供统计严谨性——目前我们的 Lenia 演化只靠适应度阈值
4. **排除逻辑**内置在检测器中——避免了人工判断相近模式的偏见
5. **置信度分层**（p值 + effect size + 排除）比单一阈值更鲁棒
