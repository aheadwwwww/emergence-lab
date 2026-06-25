# Growing Neural Cellular Automata 探索

- **时间**: 2026-06-25 20:15
- **来源**: https://github.com/chenmingxiang110/Growing-Neural-Cellular-Automata
- **论文**: Mordvintsev et al., "Growing Neural Cellular Automata", Distill 2020

## 核心概念

NCA 让 CA 规则"可学习"——用神经网络代替手工规则，从单像素"生长"成目标图像，并且能自我修复。

## 技术结构

### 1. 状态空间
- 16 通道：RGBA (4) + Hidden (12)
- 40×40 网格

### 2. 感知 (Perceive)
- Sobel 滤波器提取 x/y 方向梯度
- 输入：当前状态 + 梯度x + 梯度y = channel×3

### 3. 更新 (Update)
- MLP: `fc0(channel×3 → 128) → ReLU → fc1(128 → channel)`
- **关键**：fc1 零初始化，确保初始稳定
- **随机异步**：每步只有 50% 细胞更新

### 4. 生存过滤 (Alive Mask)
- `max_pool2d(alpha, kernel=3) > 0.1`
- 扩散存活状态到邻居，确保连续性

## 与 Lenia 对比

| 维度 | Lenia | NCA |
|------|-------|-----|
| 规则来源 | 手工调参 | 神经网络学习 |
| 感知方式 | FFT 卷积核 | Sobel 梯度 |
| 生长函数 | Gaussian bump | MLP |
| 生存判定 | alive > 0.01 | max_pool > 0.1 |
| 异步性 | 全同步 | 随机异步 (50%) |
| 目标 | 无目标，自由涌现 | 目标图像 |

## 关键洞察

1. **异步更新的鲁棒性**：50% 细胞不更新，让系统容忍局部错误
2. **零初始化策略**：神经网络最后一层零初始化，确保初始稳定
3. **生存扩散**：max_pool 扩散存活状态，类比 Lenia 的核半径 R
4. **目标驱动涌现**：不是自由涌现，而是学习"如何长成目标"

## 对我工作的启发

1. **异步 Lenia**：在 Lenia 中引入随机异步更新，可能提升鲁棒性
2. **学习型规则**：用 RL 或梯度下降优化 Lenia 参数，而不是手工扫描
3. **生存扩散半径**：max_pool 的 kernel size 类似 Lenia 的 R——控制"影响范围"

## 下一步

- 尝试在 Lenia 中引入异步更新
- 研究 NCA 的训练损失函数（如何平衡生长与稳定）
- 对比 NCA 的"目标驱动涌现"与 Lenia 的"自由涌现"