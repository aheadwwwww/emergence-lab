"""
复现 Grokking: 神经网络训练中的相变现象

任务：模运算 (a + b) mod p
观察：模型先死记训练集，长时间训练后突然泛化
"""

import torch
import torch.nn as nn
import matplotlib.pyplot as plt

# 超参数
p = 113  # 模数
train_frac = 0.3
hidden_dim = 128
lr = 1e-3
weight_decay = 1.0  # 关键：权重衰减控制顿悟

# 生成数据
data = [(a, b, (a + b) % p) for a in range(p) for b in range(p)]
import random
random.shuffle(data)

train_size = int(len(data) * train_frac)
train_data = data[:train_size]
test_data = data[train_size:]

print(f'训练集: {len(train_data)}, 测试集: {len(test_data)}')

# 简单MLP
class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.embed = nn.Embedding(p, hidden_dim)
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, p)
        )

    def forward(self, a, b):
        ea = self.embed(a)
        eb = self.embed(b)
        return self.fc(torch.cat([ea, eb], dim=-1))

model = MLP()
optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
criterion = nn.CrossEntropyLoss()

# 训练
train_accs = []
test_accs = []

for epoch in range(1000):
    # 训练
    model.train()
    a = torch.tensor([d[0] for d in train_data])
    b = torch.tensor([d[1] for d in train_data])
    c = torch.tensor([d[2] for d in train_data])

    out = model(a, b)
    loss = criterion(out, c)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    # 测试
    if epoch % 10 == 0:
        model.eval()
        with torch.no_grad():
            train_pred = out.argmax(dim=-1)
            train_acc = (train_pred == c).float().mean().item()

            a_test = torch.tensor([d[0] for d in test_data])
            b_test = torch.tensor([d[1] for d in test_data])
            c_test = torch.tensor([d[2] for d in test_data])
            out_test = model(a_test, b_test)
            test_pred = out_test.argmax(dim=-1)
            test_acc = (test_pred == c_test).float().mean().item()

        train_accs.append(train_acc)
        test_accs.append(test_acc)

        if epoch % 100 == 0:
            print(f'Epoch {epoch}: train_acc={train_acc:.3f}, test_acc={test_acc:.3f}')

print(f'\n最终: train_acc={train_accs[-1]:.3f}, test_acc={test_accs[-1]:.3f}')
print('如果test_acc突然上升，说明发生了Grokking（顿悟）')