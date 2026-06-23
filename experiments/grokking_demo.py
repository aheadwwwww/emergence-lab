"""
Grokking Demo: 突然泛化现象演示

展示神经网络如何从"记忆"转变为"理解"
"""

import numpy as np
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
from pathlib import Path

# 设置
torch.manual_seed(42)
np.random.seed(42)

# ==================== 任务：模运算 ====================
# 给定 a, b，预测 (a + b) % p

class ModuloTask:
    def __init__(self, p=113, train_frac=0.3):
        self.p = p
        self.train_frac = train_frac
        
        # 生成所有可能的 (a, b) 组合
        self.data = []
        for a in range(p):
            for b in range(p):
                self.data.append((a, b, (a + b) % p))
        
        self.data = np.array(self.data)
        np.random.shuffle(self.data)
        
        # 分割训练/测试
        n_train = int(len(self.data) * train_frac)
        self.train_data = self.data[:n_train]
        self.test_data = self.data[n_train:]
        
        print(f"数据集大小: {len(self.data)}")
        print(f"训练集: {len(self.train_data)}, 测试集: {len(self.test_data)}")
    
    def get_batch(self, data, batch_size=512):
        idx = np.random.randint(0, len(data), batch_size)
        batch = data[idx]
        return batch[:, :2], batch[:, 2]

# ==================== 模型：Transformer ====================

class SimpleTransformer(nn.Module):
    def __init__(self, vocab_size, d_model=128, n_heads=4, n_layers=2):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, 
            nhead=n_heads,
            dim_feedforward=4*d_model,
            dropout=0.1,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
        self.fc_out = nn.Linear(d_model, vocab_size)
    
    def forward(self, x):
        # x: [batch, 2] (a, b)
        x = self.embedding(x)  # [batch, 2, d_model]
        x = self.transformer(x)  # [batch, 2, d_model]
        x = x.mean(dim=1)  # [batch, d_model]
        return self.fc_out(x)  # [batch, vocab_size]

# ==================== 训练 ====================

def train_grokking(task, model, n_steps=50000, lr=1e-3, weight_decay=1.0, log_every=100):
    """
    训练并记录训练/测试准确率
    """
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    criterion = nn.CrossEntropyLoss()
    
    train_accs = []
    test_accs = []
    losses = []
    
    # 准备测试数据
    test_x, test_y = task.get_batch(task.test_data, batch_size=len(task.test_data))
    test_x = torch.LongTensor(test_x)
    test_y = torch.LongTensor(test_y)
    
    for step in range(n_steps):
        # 训练步
        model.train()
        train_x, train_y = task.get_batch(task.train_data)
        train_x = torch.LongTensor(train_x)
        train_y = torch.LongTensor(train_y)
        
        logits = model(train_x)
        loss = criterion(logits, train_y)
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        # 记录
        losses.append(loss.item())
        
        # 评估
        if step % log_every == 0:
            model.eval()
            with torch.no_grad():
                # 训练准确率
                train_pred = model(train_x).argmax(dim=1)
                train_acc = (train_pred == train_y).float().mean().item()
                
                # 测试准确率
                test_pred = model(test_x).argmax(dim=1)
                test_acc = (test_pred == test_y).float().mean().item()
            
            train_accs.append(train_acc)
            test_accs.append(test_acc)
            
            if step % 1000 == 0:
                print(f"Step {step}: loss={loss.item():.4f}, train_acc={train_acc:.2%}, test_acc={test_acc:.2%}")
    
    return {
        'train_acc': train_accs,
        'test_acc': test_accs,
        'loss': losses
    }

# ==================== 可视化 ====================

def plot_grokking(history, save_path=None):
    """绘制 grokking 曲线"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 准确率曲线
    ax = axes[0]
    steps = np.arange(0, len(history['train_acc'])) * 100
    ax.plot(steps, history['train_acc'], label='Train Acc', linewidth=2)
    ax.plot(steps, history['test_acc'], label='Test Acc', linewidth=2)
    ax.set_xlabel('Training Steps')
    ax.set_ylabel('Accuracy')
    ax.set_title('Grokking: Train vs Test Accuracy')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 1.05])
    
    # 标注 grokking 点
    test_acc = np.array(history['test_acc'])
    grokking_idx = np.where(test_acc > 0.9)[0]
    if len(grokking_idx) > 0:
        grokking_step = grokking_idx[0] * 100
        ax.axvline(grokking_step, color='red', linestyle='--', alpha=0.5, label=f'Grokking (~{grokking_step} steps)')
        ax.legend()
    
    # 损失曲线
    ax = axes[1]
    ax.plot(history['loss'], alpha=0.7)
    ax.set_xlabel('Training Steps')
    ax.set_ylabel('Loss')
    ax.set_title('Training Loss')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved to {save_path}")
    
    plt.close()

# ==================== 主程序 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("Grokking Demo: 突然泛化现象")
    print("=" * 60)
    print()
    
    # 创建任务
    print("创建模运算任务...")
    task = ModuloTask(p=113, train_frac=0.3)
    
    # 创建模型
    model = SimpleTransformer(vocab_size=113, d_model=128, n_heads=4, n_layers=2)
    print(f"\n模型参数量: {sum(p.numel() for p in model.parameters()):,}")
    
    # 训练
    print("\n开始训练...")
    print("观察：训练集会先达到100%，但测试集会长时间停滞在随机水平")
    print("然后突然在某个时刻，测试集准确率飙升到100%\n")
    
    history = train_grokking(
        task, 
        model,
        n_steps=50000,
        lr=1e-3,
        weight_decay=1.0,  # 关键：权重衰减促进泛化
        log_every=100
    )
    
    # 可视化
    save_dir = Path("output")
    save_dir.mkdir(exist_ok=True)
    plot_grokking(history, save_path=save_dir / "grokking_demo.png")
    
    print("\n实验完成！")
    print(f"最终训练准确率: {history['train_acc'][-1]:.2%}")
    print(f"最终测试准确率: {history['test_acc'][-1]:.2%}")
