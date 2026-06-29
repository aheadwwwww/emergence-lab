# Mneme: Field-like Memory in Biological Systems — 2026-06-30

## 项目概述

**Mneme** (MIT License, bshepp) — 检测生物系统中场状涌现记忆结构的探索性研究系统。
初始焦点：涡虫再生（planarian regeneration）和生物电场数据。

核心理念：生物组织通过**场**（而非局部序列）编码和分布记忆。

## 与我们的工作的关联

### 1. 与 xagent 预测处理的并行
xagent的预测处理流水线 vs Mneme的场记忆：
```
xagent:  feature_extract → encode → habit_homeo → recall → predict → learn
Mneme:   Field Reconstruction → Topology Analysis → Attractor Detection → VAE → Symbolic Regression
```
两条路径都在找涌现结构，但角度不同：xagent从认知端出发（Agent内部），Mneme从物理端出发（场形态）。

### 2. 与 Lenia/Neural Lenia 的潜在整合
- Mneme的**吸引子检测**可以直接分析Lenia演化轨迹
- **符号回归（PySR）**可自动发现Lenia的统领方程
- **拓扑数据分析（TDA）**可量化涌现结构的持久性
- 将场记忆概念引入Neural Lenia：agent可以"记住"场结构而不仅仅是局部状态

### 3. 核心模块

| 模块 | 功能 | 与我们工作的潜在应用 |
|------|------|---------------------|
| Field Reconstruction | 稀疏GP/IFT/神经场重建 | Lenia连续场插值 |
| Topology Analysis | GUDHI持久同调 | 量化涌现形态稳定性 |
| Attractor Detection | Lyapunov/复发/聚类 | Agent行为相空间分析 |
| Symbolic Regression | PySR发现统领方程 | 自动发现Lenia变异体的kernels |
| VAE Latent Space | 场压缩表示 | Agent内部状态编码 |

## 技术亮点

### 稀疏GP：O(nm²) 而非 O(n³)
```
method='ift' 默认使用稀疏GP，处理256×256场只需亚秒时间
普通GP: O(n³) — 对65536个点完全不可行
稀疏GP: O(nm²), m<<n — 标准方法
```

### Lyapunov + Surrogate门控
```python
# 不报告混沌除非通过替代检验
attractor_type = classify_attractor(lambda1, surrogate=sur)
# 只有 sur.significant == True 才标记为 STRANGE
```
这个严谨性值得我们在xagent/Lenia中学习：涌现需要统计验证而不是肉眼判断。

### BETSE集成
可直接读取Levin Lab的BETSE（生物电场组织模拟引擎）输出数据。
BETSE → Mneme → 涌现结构检测的端到端管道。

## 可迁移到 emergence-lab 的思路

1. **场记忆替代序列记忆**：Lenia cell不只记住自己的历史，还记住周围场结构
2. **持久同调度量涌现**：用持久性图量化不同参数下的形态稳定性
3. **符号回归发现规则**：输入Lenia轨迹，输出近似的统领方程——相当于反向工程涌现规则
4. **吸引子分类作为fitness**：用吸引子类型（周期性/混沌/稳定点）作为演化fitness信号

## 实验代码

```python
# 概念验证：用Mneme分析Lenia场
# 提取关键帧 → reconstruct field → compute persistence → classify attractor
from mneme.core import FieldReconstructor, largest_lyapunov
from mneme.analysis.pipeline import create_bioelectric_pipeline

# 将Lenia grid转为Mneme Field
# lenia_grid (256, 256, T) → pipeline.run({'field': lenia_grid})
```

## 依赖
- Python 3.12+, NumPy/SciPy
- PyTorch (VAE, neural fields)
- GUDHI (TDA)
- PySR + Julia (符号回归)
- scikit-learn (稀疏GP)

## 评分
- **概念新颖性**: 9/10 — 场记忆概念独特
- **与工作的关联度**: 8/10 — 直接可迁移到Lenia/xagent
- **可运行性**: 7/10 — 113测试，CI集成
- **总分**: 8/10

## 下一步
- [ ] 克隆mneme并测试基本管道
- [ ] 生成Lenia场数据送入Mneme分析
- [ ] 比较Mneme attractor检测 vs xagent homeostatic监控
- [ ] 探索在Neural Lenia中实现场记忆机制
