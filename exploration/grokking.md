# Grokking: 突然泛化现象

## 什么是 Grokking？

Grokking 是 2022 年 OpenAI 发现的现象：神经网络在长时间过拟合后，突然"顿悟"，从记忆数据转变为真正理解规律并泛化。

## 核心观察

1. **训练曲线三阶段**：
   - 初期：快速记忆训练集（训练准确率↑，测试准确率低）
   - 中期：长时间停滞（训练100%准确，测试随机）
   - Grokking：测试准确率突然飙升到100%

2. **关键因素**：
   - **训练步数**：需要远超传统early stopping的点
   - **权重衰减**：促进泛化的关键
   - **数据量**：小数据集更容易观察到
   - **模型结构**：Transformer比MLP更容易

## 数学直觉

- 训练初期找到"捷径解"（记忆），复杂度低
- 随着训练+权重衰减，找到"泛化解"（真正规律），虽然更复杂但泛化更好
- 权重衰减惩罚大权重，迫使网络寻找更简洁的表示

## 实验方向

### 实验1：算术运算
```python
# 任务：两个数字加法 a + b = c
# 数据：a, b ∈ [0, 100], 部分作为训练集
# 观察：训练集100%准确后，多久测试集开始泛化？
```

### 实验2：算法任务
```python
# 任务：奇偶判断、模运算、比较大小
# 观察：哪些任务更容易出现grokking？
```

### 实验3：电路形成
```python
# 分析：grokking前后，网络内部结构如何变化？
# 方法：probing classifier、attention pattern可视化
```

## 相关概念

- **顿悟（Insight）**：人类学习中也有类似的"啊哈！"时刻
- **相变（Phase Transition）**：物理系统突然改变状态
- **双下降（Double Descent）**：测试误差随模型容量先降后升再降

## 进一步阅读

- Power et al., "Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets" (2022)
- Nanda et al., "Progress Measures for Grokking via Mechanistic Interpretability" (2023)
- Liu et al., "Towards Understanding Grokking: An Effective Theory of Representation Learning" (2022)

## 待探索问题

1. Grokking 与模型规模的关系？
2. 是否存在"Grokking触发器"可以加速顿悟？
3. 不同优化器（Adam vs SGD）对grokking的影响？
4. 语言模型中是否存在类似现象？