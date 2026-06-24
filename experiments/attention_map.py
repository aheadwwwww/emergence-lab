"""
#013 Attention: 注意力模式涌现可视化

模拟不同配置下注意力模式从随机到结构化的"涌现"过程。
通过控制头数、序列长度、训练步数来观察临界规模效应。
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import os

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'experiments')
os.makedirs(OUTPUT, exist_ok=True)

# ============================================================
# 实验 1: 多头注意力的涌现散射图
# ============================================================
def exp1_head_emergence():
    """模拟 1 到 12 头注意力的"涌现"得分"""
    np.random.seed(42)
    n_heads = np.arange(1, 13)
    seq_len = 32
    
    # 模拟注意力分数: 每个头关注不同模式
    # 头越多, 多样化涌现越强
    emergence_score = []
    for h in n_heads:
        attn = np.zeros((h, seq_len, seq_len))
        for i in range(h):
            # 每个头随机关注一些模式
            pattern_type = i % 4
            if pattern_type == 0:
                # 对角线附近 (局部注意力)
                for j in range(seq_len):
                    start = max(0, j-2)
                    end = min(seq_len, j+3)
                    slen = end - start
                    attn[i, j, start:end] = np.random.dirichlet(np.ones(slen))
            elif pattern_type == 1:
                # 固定位置 (全局注意力)
                target = (i * 7) % seq_len
                attn[i, :, target] = np.eye(seq_len)[:, target]
            elif pattern_type == 2:
                # 块状注意力 (短语)
                block_size = max(2, 8 - i)
                for j in range(0, seq_len, block_size):
                    end = min(j + block_size, seq_len)
                    attn[i, j:end, j:end] = np.full((end-j, end-j), 1/(end-j))
            else:
                # 随机 (探索)
                attn[i] = np.random.dirichlet(np.ones(seq_len), size=seq_len)
        
        # 涌现得分: 头的熵多样性 + 模式区分度
        head_entropies = []
        for i in range(h):
            ent = -np.sum(attn[i] * np.log(attn[i] + 1e-10), axis=1).mean()
            head_entropies.append(ent)
        
        # 模式多样性 = head 间的平均距离
        diversity = 0
        count = 0
        for i in range(h):
            for j in range(i+1, h):
                diversity += np.abs(attn[i] - attn[j]).mean()
                count += 1
        diversity = diversity / count if count > 0 else 0
        
        # 涌现得分 = 多样性 + (4 - 平均熵的正则化)  # 熵越低表示模式越明确
        score = diversity * 8 + max(0, 3.5 - np.mean(head_entropies))
        emergence_score.append(score)
    
    fig, axes = plt.subplots(2, 6, figsize=(20, 7))
    axes = axes.flatten()
    
    for idx, (h, score) in enumerate(zip(n_heads, emergence_score)):
        ax = axes[idx]
        # 模拟注意力热图
        attn_demo = np.zeros((seq_len, seq_len))
        for i in range(h):
            pattern = i % 4
            if pattern == 0:
                for j in range(seq_len):
                    r = (j * 3 + i) % seq_len
                    attn_demo[j, r] += 0.3
            elif pattern == 1:
                target = ((i + 1) * 5) % seq_len
                attn_demo[np.arange(seq_len), (np.arange(seq_len) + 1) % seq_len] += 0.15
            elif pattern == 2:
                block = 16 // (i + 1)
                if block < 2: block = 2
                for b in range(0, seq_len, block):
                    attn_demo[b:b+block, b:b+block] += 0.25 / block
            else:
                attn_demo += np.random.rand(seq_len, seq_len) * 0.05
        
        ax.imshow(attn_demo, cmap='viridis', aspect='equal')
        ax.set_title(f'{h} Heads | Score: {score:.2f}', fontsize=10)
        ax.set_xticks([])
        ax.set_yticks([])
    
    fig.suptitle('#013 Attention: 多头注意力的涌现模式 — 从头数看临界规模', fontsize=14, fontweight='bold')
    plt.tight_layout()
    path = os.path.join(OUTPUT, 'attention_emergence_overview.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"[OK] 实验 1 完成: {path}")
    return emergence_score


# ============================================================
# 实验 2: 注意力到能力涌现 — 临界规模曲线
# ============================================================
def exp2_critical_scale():
    """模拟能力随注意力头数和层数的涌现"""
    np.random.seed(42)
    
    max_heads = 16
    n_layers = [1, 2, 4, 8]
    
    fig, axes = plt.subplots(1, 4, figsize=(20, 5))
    
    for li, layers in enumerate(n_layers):
        ax = axes[li]
        n_heads_range = np.arange(1, max_heads + 1)
        
        # 能力评分 (Sigmoid 曲线模拟涌现)
        def capacity(h, l):
            base = h * l  # 总头数
            x = base / 30.0  # 归一化
            # Sigmoid 带饱和度
            return 1.0 / (1.0 + np.exp(-4 * (x - 0.5)))
        
        scores = [capacity(h, layers) for h in n_heads_range]
        
        # 加一些模拟的"训练"噪声
        noise = np.random.normal(0, 0.02, len(scores))
        scores = np.clip(np.array(scores) + noise, 0, 1)
        
        ax.plot(n_heads_range, scores, 'b.-', linewidth=2, markersize=8)
        # 标记涌现门槛
        threshold_idx = np.argmax(scores > 0.6)
        if threshold_idx > 0:
            ax.axvline(x=n_heads_range[threshold_idx], color='r', linestyle='--', alpha=0.7, 
                      label=f'Threshold: {n_heads_range[threshold_idx]} heads')
        ax.axhline(y=0.6, color='gray', linestyle=':', alpha=0.5)
        
        ax.set_xlabel('Number of Heads')
        ax.set_ylabel('Emergent Capability')
        ax.set_title(f'{layers} Layer(s)', fontsize=12)
        ax.set_ylim(0, 1.1)
        ax.legend(fontsize=9)
        ax.grid(alpha=0.2)
    
    fig.suptitle('#013 Attention: 能力涌现的临界规模 — 头数 × 层数', fontsize=14, fontweight='bold')
    plt.tight_layout()
    path = os.path.join(OUTPUT, 'attention_critical_scale.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"[OK] 实验 2 完成: {path}")


# ============================================================
# 实验 3: 经典注意力模式汇编
# ============================================================
def exp3_attention_patterns():
    """展示典型的注意力模式"""
    seq_len = 24
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    axes = axes.flatten()
    
    patterns = [
        ("Diagonal\n(局部),", lambda: np.eye(seq_len)),
        ("Vertical\n(全局/特殊 token)", lambda: np.tile(np.eye(seq_len)[:, 0:1], (1, seq_len))),
        ("Block-Diagonal\n(短语/块)", lambda: np.kron(np.eye(seq_len // 4), np.ones((4, 4)) / 4)),
        ("Slanted\n(位移/语法)", lambda: np.eye(seq_len, k=1)),
        ("Uniform\n(平均注意力)", lambda: np.ones((seq_len, seq_len)) / seq_len),
        ("Dual Focus\n(双峰注意力)", lambda: (np.eye(seq_len) + np.fliplr(np.eye(seq_len))) / 2),
        ("Random\n(未训练)", lambda: np.random.dirichlet(np.ones(seq_len), size=seq_len)),
        ("Mixed\n(实际训练后)", lambda: (
            0.3 * np.eye(seq_len) + 
            0.2 * np.eye(seq_len, k=-1) + 
            0.3 * np.eye(seq_len, k=1) * 0.5 +
            0.2 * np.tile(np.eye(seq_len)[:, seq_len//2:seq_len//2+1], (1, seq_len))
        )),
    ]
    
    for idx, (name, gen_fn) in enumerate(patterns):
        ax = axes[idx]
        pattern = gen_fn()
        # 加 softmax
        pattern = np.exp(pattern * 3)
        pattern = pattern / pattern.sum(axis=1, keepdims=True)
        
        ax.imshow(pattern, cmap='YlOrRd', aspect='equal')
        ax.set_title(name, fontsize=10)
        ax.set_xticks([])
        ax.set_yticks([])
    
    fig.suptitle('#013 Attention: 典型的注意力模式类型 — 从局部到全局', fontsize=14, fontweight='bold')
    plt.tight_layout()
    path = os.path.join(OUTPUT, 'attention_pattern_types.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"[OK] 实验 3 完成: {path}")


# ============================================================
# 实验 4: 注意力 vs 涌现维度关系图
# ============================================================
def exp4_attention_emergence_web():
    """注意力与涌现理论各节点的关系网络"""
    nodes = [
        "Attention",
        "Emergence", "Self-Reference", "Scaling Laws",
        "Strange Loops", "Cognitive Gap", "Creativity",
        "Hallucination"
    ]
    
    # 连接矩阵: 关注度
    connections = np.array([
        [0,  0.9, 0.7, 0.8, 0.6, 0.7, 0.5, 0.4],  # Attention
        [0.9, 0,  0.5, 0.6, 0.4, 0.3, 0.3, 0.2],  # Emergence
        [0.7, 0.5, 0,  0.3, 0.8, 0.4, 0.3, 0.5],  # Self-Reference
        [0.8, 0.6, 0.3, 0,  0.2, 0.5, 0.4, 0.3],  # Scaling Laws
        [0.6, 0.4, 0.8, 0.2, 0,  0.3, 0.2, 0.4],  # Strange Loops
        [0.7, 0.3, 0.4, 0.5, 0.3, 0,  0.6, 0.7],  # Cognitive Gap
        [0.5, 0.3, 0.3, 0.4, 0.2, 0.6, 0,  0.5],  # Creativity
        [0.4, 0.2, 0.5, 0.3, 0.4, 0.7, 0.5, 0],  # Hallucination
    ])
    
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(connections, cmap='RdYlBu_r', vmin=0, vmax=1)
    
    ax.set_xticks(range(len(nodes)))
    ax.set_yticks(range(len(nodes)))
    ax.set_xticklabels(nodes, rotation=45, ha='right', fontsize=10)
    ax.set_yticklabels(nodes, fontsize=10)
    
    for i in range(len(nodes)):
        for j in range(len(nodes)):
            text = ax.text(j, i, f'{connections[i, j]:.1f}',
                          ha='center', va='center', color='black' if connections[i, j] < 0.5 else 'white',
                          fontsize=9)
    
    fig.suptitle('#013 Attention: 与涌现理论各节点的关联强度', fontsize=14, fontweight='bold')
    plt.tight_layout()
    path = os.path.join(OUTPUT, 'attention_connections.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"[OK] 实验 4 完成: {path}")


# ============================================================
# 主流程
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print("#013 Attention: 注意力机制涌现可视化实验")
    print("=" * 60)
    
    scores = exp1_head_emergence()
    print(f"\n各头数涌现得分: {', '.join(f'{s:.2f}' for s in scores)}")
    print(f"涌现门槛 (得分>2.0): 第 {next(i+1 for i,s in enumerate(scores) if s > 2.0)} 个头")
    
    exp2_critical_scale()
    exp3_attention_patterns()
    exp4_attention_emergence_web()
    
    print(f"\n所有输出已保存到: {OUTPUT}")
    print("[DONE]")
