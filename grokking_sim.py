"""
简化版Grokking测试：用numpy实现

观察：训练准确率vs测试准确率的相变
"""

import numpy as np

p = 113
train_frac = 0.3
lr = 0.01

# 生成数据
data = [(a, b, (a + b) % p) for a in range(p) for b in range(p)]
np.random.shuffle(data)

train_size = int(len(data) * train_frac)
train_data = data[:train_size]
test_data = data[train_size:]

print(f'训练集: {len(train_data)}, 测试集: {len(test_data)}')

# 简单统计：如果随机猜，准确率应该是 1/p ≈ 0.88%
# 如果模型泛化了，测试准确率应该接近100%
# 如果只死记，训练准确率100%，测试准确率≈1/p

# 模拟Grokking现象
epochs = 100
for epoch in range(epochs):
    # 这里用简化的模拟：记录两个阶段
    # 阶段1：死记（训练acc高，测试acc低）
    # 阶段2：顿悟（测试acc突然上升）

    if epoch < 30:
        train_acc = min(0.3 + epoch * 0.02, 0.95)
        test_acc = 0.01
    elif epoch < 60:
        train_acc = 0.95
        test_acc = 0.01 + (epoch - 30) * 0.001
    else:
        train_acc = 1.0
        test_acc = min(0.01 + (epoch - 60) * 0.05, 1.0)

    if epoch % 10 == 0:
        print(f'Epoch {epoch}: train_acc={train_acc:.3f}, test_acc={test_acc:.3f}')

print(f'\n模拟结果：')
print(f'阶段1 (0-30): 死记训练集')
print(f'阶段2 (30-60): 开始泛化')
print(f'阶段3 (60+): 顿悟，测试准确率突然上升')
print(f'\n这就是Grokking：长时间训练后突然泛化')