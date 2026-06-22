"""
Grokking实验：观察神经网络的顿悟现象

Grokking是指在长时间过拟合后，模型突然实现泛化的现象。
本实验使用模运算任务来观察这一现象。
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import json
from pathlib import Path

# 设置随机种子
torch.manual_seed(42)
np.random.seed(42)

# 实验参数
P = 97  # 模数
TRAIN_FRAC = 0.3  # 训练集比例（小训练集更容易观察到grokking）
HIDDEN_DIM = 128
NUM_LAYERS = 2
LEARNING_RATE = 1e-3
WEIGHT_DECAY = 1.0
NUM_EPOCHS = 10000
BATCH_SIZE = 512

class ModularArithmeticNet(nn.Module):
    """用于学习模运算的神经网络"""
    def __init__(self, p, hidden_dim, num_layers):
        super().__init__()
        self.p = p
        self.embed = nn.Embedding(p, hidden_dim)
        
        layers = []
        for _ in range(num_layers):
            layers.extend([
                nn.Linear(hidden_dim, hidden_dim),
                nn.ReLU(),
            ])
        self.mlp = nn.Sequential(*layers)
        self.unembed = nn.Linear(hidden_dim, p)
        
    def forward(self, x):
        # x shape: (batch, 2) - 两个操作数
        a, b = x[:, 0], x[:, 1]
        embed_a = self.embed(a)  # (batch, hidden)
        embed_b = self.embed(b)  # (batch, hidden)
        # 组合两个嵌入
        h = embed_a * embed_b  # 元素乘积（有助于学习乘法类运算）
        h = self.mlp(h)
        logits = self.unembed(h)
        return logits

def create_dataset(p, operation='add'):
    """创建模运算数据集"""
    data = []
    for a in range(p):
        for b in range(p):
            if operation == 'add':
                result = (a + b) % p
            elif operation == 'subtract':
                result = (a - b) % p
            elif operation == 'multiply':
                result = (a * b) % p
            else:
                raise ValueError(f"Unknown operation: {operation}")
            data.append((a, b, result))
    return data

def train_model(p, operation, train_frac, hidden_dim, num_layers, 
                learning_rate, weight_decay, num_epochs, batch_size):
    """训练模型并记录训练过程"""
    
    # 创建数据集
    data = create_dataset(p, operation)
    np.random.shuffle(data)
    
    # 划分训练集和测试集
    n_train = int(len(data) * train_frac)
    train_data = data[:n_train]
    test_data = data[n_train:]
    
    print(f"训练集大小: {len(train_data)}, 测试集大小: {len(test_data)}")
    
    # 转换为tensor
    train_inputs = torch.tensor([[a, b] for a, b, _ in train_data])
    train_labels = torch.tensor([r for _, _, r in train_data])
    test_inputs = torch.tensor([[a, b] for a, b, _ in test_data])
    test_labels = torch.tensor([r for _, _, r in test_data])
    
    # 创建模型
    model = ModularArithmeticNet(p, hidden_dim, num_layers)
    optimizer = optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
    criterion = nn.CrossEntropyLoss()
    
    # 记录训练过程
    history = {
        'train_loss': [],
        'test_loss': [],
        'train_acc': [],
        'test_acc': [],
        'epochs': []
    }
    
    best_test_acc = 0
    grokking_epoch = None
    
    # 训练循环
    for epoch in tqdm(range(num_epochs)):
        model.train()
        
        # 随机采样batch
        indices = torch.randperm(len(train_inputs))[:batch_size]
        batch_inputs = train_inputs[indices]
        batch_labels = train_labels[indices]
        
        optimizer.zero_grad()
        logits = model(batch_inputs)
        loss = criterion(logits, batch_labels)
        loss.backward()
        optimizer.step()
        
        # 每100个epoch评估一次
        if epoch % 100 == 0:
            model.eval()
            with torch.no_grad():
                # 训练集评估
                train_logits = model(train_inputs)
                train_loss = criterion(train_logits, train_labels).item()
                train_pred = train_logits.argmax(dim=1)
                train_acc = (train_pred == train_labels).float().mean().item()
                
                # 测试集评估
                test_logits = model(test_inputs)
                test_loss = criterion(test_logits, test_labels).item()
                test_pred = test_logits.argmax(dim=1)
                test_acc = (test_pred == test_labels).float().mean().item()
                
                history['epochs'].append(epoch)
                history['train_loss'].append(train_loss)
                history['test_loss'].append(test_loss)
                history['train_acc'].append(train_acc)
                history['test_acc'].append(test_acc)
                
                # 检测grokking现象
                if test_acc > 0.9 and grokking_epoch is None:
                    grokking_epoch = epoch
                    print(f"\n[!] Grokking detected at epoch {epoch}! Test accuracy: {test_acc:.2%}")
                
                if test_acc > best_test_acc:
                    best_test_acc = test_acc
                    
                if epoch % 1000 == 0:
                    print(f"Epoch {epoch}: Train Loss={train_loss:.4f}, Train Acc={train_acc:.2%}, "
                          f"Test Loss={test_loss:.4f}, Test Acc={test_acc:.2%}")
    
    return model, history, grokking_epoch, best_test_acc

def visualize_results(history, grokking_epoch, operation, save_path='grokking_results.png'):
    """可视化训练过程"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    epochs = history['epochs']
    
    # Loss曲线
    axes[0].plot(epochs, history['train_loss'], label='Train Loss', alpha=0.7)
    axes[0].plot(epochs, history['test_loss'], label='Test Loss', alpha=0.7)
    if grokking_epoch:
        axes[0].axvline(x=grokking_epoch, color='red', linestyle='--', label=f'Grokking (epoch {grokking_epoch})')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].set_title(f'Training Loss - {operation.capitalize()} Operation')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    axes[0].set_yscale('log')
    
    # Accuracy曲线
    axes[1].plot(epochs, history['train_acc'], label='Train Accuracy', alpha=0.7)
    axes[1].plot(epochs, history['test_acc'], label='Test Accuracy', alpha=0.7)
    if grokking_epoch:
        axes[1].axvline(x=grokking_epoch, color='red', linestyle='--', label=f'Grokking')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Accuracy')
    axes[1].set_title(f'Training Accuracy - {operation.capitalize()} Operation')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"结果已保存到: {save_path}")

def test_generalization(model, p, operation):
    """测试模型的泛化能力"""
    model.eval()
    correct = 0
    total = p * p
    
    with torch.no_grad():
        for a in range(p):
            for b in range(p):
                if operation == 'add':
                    expected = (a + b) % p
                elif operation == 'subtract':
                    expected = (a - b) % p
                elif operation == 'multiply':
                    expected = (a * b) % p
                
                inputs = torch.tensor([[a, b]])
                logits = model(inputs)
                pred = logits.argmax(dim=1).item()
                
                if pred == expected:
                    correct += 1
    
    accuracy = correct / total
    print(f"\n完整测试集准确率: {accuracy:.2%} ({correct}/{total})")
    return accuracy

def demonstrate_predictions(model, p, operation, num_examples=10):
    """展示一些预测示例"""
    model.eval()
    print(f"\n预测示例 ({operation} mod {p}):")
    print("-" * 50)
    
    with torch.no_grad():
        for _ in range(num_examples):
            a = np.random.randint(0, p)
            b = np.random.randint(0, p)
            
            if operation == 'add':
                expected = (a + b) % p
                op_str = f"{a} + {b}"
            elif operation == 'subtract':
                expected = (a - b) % p
                op_str = f"{a} - {b}"
            elif operation == 'multiply':
                expected = (a * b) % p
                op_str = f"{a} × {b}"
            
            inputs = torch.tensor([[a, b]])
            logits = model(inputs)
            pred = logits.argmax(dim=1).item()
            
            status = "OK" if pred == expected else "X"
            print(f"{op_str} mod {p} = {expected}, 预测: {pred} {status}")

if __name__ == "__main__":
    print("=" * 60)
    print("Grokking实验：观察神经网络的顿悟现象")
    print("=" * 60)
    
    # 运行多个操作
    operations = ['add', 'multiply']  # 加法和乘法更容易观察到grokking
    
    results = {}
    
    for operation in operations:
        print(f"\n{'=' * 60}")
        print(f"训练任务: 模{P}{operation}运算")
        print(f"{'=' * 60}")
        
        model, history, grokking_epoch, best_acc = train_model(
            p=P,
            operation=operation,
            train_frac=TRAIN_FRAC,
            hidden_dim=HIDDEN_DIM,
            num_layers=NUM_LAYERS,
            learning_rate=LEARNING_RATE,
            weight_decay=WEIGHT_DECAY,
            num_epochs=NUM_EPOCHS,
            batch_size=BATCH_SIZE
        )
        
        # 可视化
        save_path = f'grokking_{operation}.png'
        visualize_results(history, grokking_epoch, operation, save_path)
        
        # 测试泛化能力
        full_acc = test_generalization(model, P, operation)
        
        # 展示预测示例
        demonstrate_predictions(model, P, operation)
        
        # 保存结果
        results[operation] = {
            'grokking_epoch': grokking_epoch,
            'best_test_acc': best_acc,
            'full_test_acc': full_acc,
            'final_train_acc': history['train_acc'][-1],
            'final_test_acc': history['test_acc'][-1]
        }
        
        # 保存训练历史
        with open(f'history_{operation}.json', 'w') as f:
            json.dump(history, f)
    
    # 保存汇总结果
    print("\n" + "=" * 60)
    print("实验汇总")
    print("=" * 60)
    for op, res in results.items():
        print(f"\n{op.upper()}运算:")
        print(f"  Grokking出现epoch: {res['grokking_epoch']}")
        print(f"  最佳测试准确率: {res['best_test_acc']:.2%}")
        print(f"  完整测试集准确率: {res['full_test_acc']:.2%}")
    
    with open('grokking_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n实验完成！")
