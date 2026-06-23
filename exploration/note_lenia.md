# Lenia 探索笔记

**日期**：2026-06-23 22:33
**来源**：Chakazul/Lenia (https://github.com/Chakazul/Lenia.git)
**相关节点**：#001 Emergence, #009 Continuous CA

## 实现
自己写的简洁版 `lenia_modern.py`，包含：
- 高斯环状核 (Difference of Gaussians)
- 钟形生长函数
- Orbium 种子、随机种子、环形种子
- GIF 动画生成

## 实验结果

| 实验 | 参数 | 结果 |
|------|------|------|
| Orbium 种子 | sigma=8, mu=0.15, gsigma=0.015 | 50步后死亡（0 mass） |
| 随机汤 x4 | 4组不同参数 | 全部死亡（alive_ratio=0.000） |
| 圆环种子 | sigma=10, mu=0.13, gsigma=0.012 | 100步后死亡 |
| GIF生成 | sigma=10, mu=0.13, gsigma=0.012 | 200帧GIF生成成功但死亡 |

## 关键洞察

**默认参数无法产生持久生命**。Lenia 的参数极其敏感，需要精确调参才能产生自组织模式。

参照原始 Lenia 论文 (Bert Chan, 2019)，典型的存活参数范围：
- 核大小：37-45
- sigma：10-15
- mu：0.08-0.18
- growth_sigma：0.008-0.020
- dt：0.05-0.2

我们的实验参数在范围内但都死亡，说明：
1. 核的精度（浮点计算）影响稳定性——scipy.convolve vs FFT 可能有差异
2. 初始条件需要精确的 Orbium 模式，不只是粗略的6点种子
3. Orbium 需要特定的参数共振，轻微偏移就导致死亡

## 下一步
- 尝试 FFT 卷积（更快更精确）
- 从原始 Lenia 仓库复制精确的 Orbium 参数
- 尝试参数扫描找到存活参数
- 研究 Lenia 的 "phase transition"（从混沌到有序的临界点）
