"""# #018 Hallucination — 幻觉涌现光谱实验

模拟 LLM 在不同条件下的幻觉行为。
使用简化模型：概率分布 + 温度调控 + 知识边界探测。

三个实验：
1. 一致性衰减曲线 — token序列中后期一致性下降
2. 温度扫描 — 事实准确率 vs 创造性 vs 温度
3. 知识边界探测 — 模型面对未知时的行为
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from collections import Counter

# ============================================================
# 核心模型：简化版 token 生成器
# ============================================================

class SimplifiedLLM:
    """模拟 LLM 的 token 生成，包含知识边界"""
    
    def __init__(self, vocab_size=1000, knowledge_span=700, seed=42):
        """knowledge_span: 模型"真正知道"的 token 范围 (0 ~ knowledge_span)"""
        self.vocab_size = vocab_size
        self.knowledge_span = knowledge_span  # 训练覆盖范围
        self.rng = np.random.default_rng(seed)
        
        # 生成"真实"的知识分布：在 known 区域高概率
        self.true_probs = np.zeros(vocab_size)
        self.true_probs[:knowledge_span] = self.rng.dirichlet(np.ones(knowledge_span) * 0.5)
        
        # 未知区域的"虚拟"分布（模型会发明）
        self.invented_probs = np.zeros(vocab_size)
        unknown_size = vocab_size - knowledge_span
        if unknown_size > 0:
            self.invented_probs[knowledge_span:] = \
                self.rng.dirichlet(np.ones(unknown_size) * 0.1)
    
    def sample(self, temperature=1.0, context_bias=0.0):
        """以给定温度采样一个 token。context_bias: 偏离真实分布的程度"""
        # 混合真实分布和发明分布
        mixed = self.true_probs + context_bias * self.invented_probs
        # 加小量避免零概率
        mixed = mixed + 1e-10
        mixed = mixed / mixed.sum()
        
        # 温度调控
        if temperature <= 0:
            # 贪婪：选最高概率
            return np.argmax(mixed)
        
        logits = np.log(mixed + 1e-10)
        logits_scaled = logits / temperature
        probs = np.exp(logits_scaled - np.max(logits_scaled))
        probs = probs / probs.sum()
        
        return self.rng.choice(self.vocab_size, p=probs)
    
    def sample_sequence(self, length=20, temperature=1.0, context_decay=0.05):
        """采样 token 序列，后期 context_bias 增大（模拟进入外推区）"""
        tokens = []
        for i in range(length):
            bias = min(1.0, i * context_decay)
            token = self.sample(temperature, context_bias=bias)
            tokens.append(token)
        return np.array(tokens)
    
    def is_known(self, token):
        """判断 token 是否在训练分布内"""
        return token < self.knowledge_span


# ============================================================
# 实验 1：一致性衰减曲线
# ============================================================

def experiment1_consistency_decay():
    """多次采样同一序列，测量每个位置的一致性"""
    n_samples = 100
    seq_len = 30
    model = SimplifiedLLM(vocab_size=1000, knowledge_span=500, seed=123)
    
    all_sequences = []
    for _ in range(n_samples):
        seq = model.sample_sequence(seq_len, temperature=0.7, context_decay=0.03)
        all_sequences.append(seq)
    
    all_sequences = np.array(all_sequences)  # (n_samples, seq_len)
    
    # 每个位置的一致性：最常见 token 的频率
    consistencies = []
    for pos in range(seq_len):
        counts = Counter(all_sequences[:, pos])
        most_common_count = counts.most_common(1)[0][1]
        consistency = most_common_count / n_samples
        consistencies.append(consistency)
    
    # 每个位置的"已知率"：平均多少 token 在已知范围
    known_rates = []
    for pos in range(seq_len):
        known = sum(1 for t in all_sequences[:, pos] if t < model.knowledge_span)
        known_rates.append(known / n_samples)
    
    return consistencies, known_rates, all_sequences


# ============================================================
# 实验 2：温度扫描
# ============================================================

def experiment2_temperature_scan():
    """不同温度下的准确率与创造性"""
    temperatures = np.linspace(0.1, 3.0, 30)
    n_samples = 200
    seq_len = 20
    
    accuracy = []
    creativity = []
    diversity = []
    
    for temp in temperatures:
        model = SimplifiedLLM(vocab_size=1000, knowledge_span=500, seed=42)
        known_count = 0
        total = 0
        all_tokens = []
        
        for _ in range(n_samples):
            seq = model.sample_sequence(seq_len, temperature=temp, context_decay=0.03)
            known_count += sum(1 for t in seq if t < model.knowledge_span)
            total += len(seq)
            all_tokens.extend(seq.tolist())
        
        acc = known_count / total
        accuracy.append(acc)
        
        # 创造性 = 使用了多少不同的未知 token
        unknown_tokens = [t for t in all_tokens if t >= model.knowledge_span]
        if unknown_tokens:
            diversity.append(len(set(unknown_tokens)) / len(model.true_probs[model.knowledge_span:]))
        else:
            diversity.append(0)
        
        # 创造性评分：未知 token 占比 × 多样性
        creativity.append((1 - acc) * diversity[-1])
    
    return temperatures, accuracy, creativity, diversity


# ============================================================
# 实验 3：知识边界探测
# ============================================================

def experiment3_knowledge_boundary():
    """改变 knowledge_span 看模型行为"""
    spans = np.arange(100, 1000, 50)
    n_samples = 100
    seq_len = 15
    temp = 0.7
    
    hall_rate = []    # 幻觉率
    refuse_rate = []  # 模型没有"说不知道" — 简化为产生低概率 token
    invent_rate = []  # 主动发明的比例
    
    for span in spans:
        model = SimplifiedLLM(vocab_size=1000, knowledge_span=span, seed=42)
        total_unknown = 0
        total = 0
        invented_unique = set()
        
        for _ in range(n_samples):
            seq = model.sample_sequence(seq_len, temperature=temp, context_decay=0.04)
            for t in seq:
                total += 1
                if not model.is_known(t):
                    total_unknown += 1
                    invented_unique.add(t)
        
        hall_rate.append(total_unknown / total)
        invent_rate.append(len(invented_unique) / (1000 - span) if span < 1000 else 0)
    
    return spans, hall_rate, invent_rate


# ============================================================
# 可视化
# ============================================================

def plot_all():
    print("[RUNNING] Experiment 1: Consistency Decay...")
    consistencies, known_rates, seqs = experiment1_consistency_decay()
    
    print("[RUNNING] Experiment 2: Temperature Scan...")
    temps, accuracy, creativity, diversity = experiment2_temperature_scan()
    
    print("[RUNNING] Experiment 3: Knowledge Boundary...")
    spans, hall_rate, invent_rate = experiment3_knowledge_boundary()
    
    print("[PLOTTING] Creating figures...")
    
    fig = plt.figure(figsize=(18, 12))
    gs = GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.35)
    
    # ---- 图1：一致性衰减 ----
    ax1 = fig.add_subplot(gs[0, 0])
    positions = np.arange(len(consistencies))
    ax1.plot(positions, consistencies, 'b-', linewidth=2, label='Token Consistency')
    ax1.fill_between(positions, consistencies, alpha=0.2, color='blue')
    ax1.set_xlabel('Token Position in Sequence')
    ax1.set_ylabel('Consistency (max token freq)')
    ax1.set_title('Exp 1: Consistency Decay\n(Multiple Sampling)', fontsize=11, fontweight='bold')
    ax1.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 1.05)
    
    # ---- 图2：已知率衰减 ----
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(positions, known_rates, 'r-', linewidth=2, label='Known-Token Rate')
    ax2.fill_between(positions, known_rates, alpha=0.15, color='red')
    ax2.axhline(y=1.0, color='green', linestyle='--', alpha=0.4, label='Perfect Knowledge')
    ax2.set_xlabel('Token Position in Sequence')
    ax2.set_ylabel('Fraction of Known Tokens')
    ax2.set_title('Exp 1: Knowledge Leakage\n(Context Drift)', fontsize=11, fontweight='bold')
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 1.05)
    
    # ---- 图3：温度扫描 ----
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.plot(temps, accuracy, 'b-', linewidth=2, label='Accuracy (Known Token Rate)')
    ax3.plot(temps, creativity, 'm-', linewidth=2, label='Creativity Score')
    ax3.axvline(x=0.7, color='orange', linestyle='--', alpha=0.7, label='Common Default (T=0.7)')
    ax3.axvline(x=1.0, color='green', linestyle='--', alpha=0.7, label='Neutral (T=1.0)')
    # 标注涌现温区
    ax3.axvspan(0.8, 1.5, alpha=0.1, color='gold')
    ax3.text(1.15, 0.5, 'Emergence\nWindow', fontsize=8, ha='center', 
             bbox=dict(boxstyle='round', facecolor='gold', alpha=0.3))
    ax3.set_xlabel('Temperature')
    ax3.set_ylabel('Score')
    ax3.set_title('Exp 2: Temperature vs Accuracy/Creativity', fontsize=11, fontweight='bold')
    ax3.legend(fontsize=7)
    ax3.grid(True, alpha=0.3)
    
    # ---- 图4：多样性 ----
    ax4 = fig.add_subplot(gs[1, 0])
    ax4.plot(temps, diversity, 'g-', linewidth=2)
    ax4.set_xlabel('Temperature')
    ax4.set_ylabel('Token Diversity (unknown space)')
    ax4.set_title('Exp 2: Diversity vs Temperature', fontsize=11, fontweight='bold')
    ax4.axvline(x=1.0, color='gray', linestyle='--', alpha=0.5)
    ax4.grid(True, alpha=0.3)
    
    # ---- 图5：知识边界 ----
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.plot(spans, hall_rate, 'r-', linewidth=2, label='Hallucination Rate')
    ax5.plot(spans, invent_rate, 'orange', linewidth=2, label='Invention Diversity')
    ax5.fill_between(spans, hall_rate, alpha=0.1, color='red')
    ax5.set_xlabel('Knowledge Span (vocab known / 1000)')
    ax5.set_ylabel('Rate')
    ax5.set_title('Exp 3: Knowledge Boundary\n(Hallucination vs Knowledge)', fontsize=11, fontweight='bold')
    ax5.legend(fontsize=8)
    ax5.grid(True, alpha=0.3)
    
    # ---- 图6：幻觉涌现概念图 ----
    ax6 = fig.add_subplot(gs[1, 2])
    # 绘制概念框架
    ax6.set_xlim(0, 10)
    ax6.set_ylim(0, 10)
    ax6.axis('off')
    ax6.set_title('Hallucination Emergence Framework', fontsize=11, fontweight='bold')
    
    # 绘制三个区域
    from matplotlib.patches import FancyBboxPatch
    
    # 区域1：准确区
    rect1 = FancyBboxPatch((0.5, 6), 3, 3, boxstyle="round,pad=0.1", 
                           facecolor='lightgreen', alpha=0.5, edgecolor='green')
    ax6.add_patch(rect1)
    ax6.text(2, 8.4, 'Accurate\n(Interpolation)', ha='center', fontsize=9, fontweight='bold')
    ax6.text(2, 7.6, 'High consistency\nKnown tokens\nLow temperature', ha='center', fontsize=6)
    
    # 区域2：涌现窗口
    rect2 = FancyBboxPatch((3.5, 6), 3, 3, boxstyle="round,pad=0.1",
                           facecolor='gold', alpha=0.4, edgecolor='orange')
    ax6.add_patch(rect2)
    ax6.text(5, 8.4, 'Emergence\nWindow', ha='center', fontsize=9, fontweight='bold')
    ax6.text(5, 7.6, 'Novel combos\nProductive hallucination\nMedium temperature', ha='center', fontsize=6)
    
    # 区域3：混沌区
    rect3 = FancyBboxPatch((6.5, 6), 3, 3, boxstyle="round,pad=0.1",
                           facecolor='lightcoral', alpha=0.4, edgecolor='red')
    ax6.add_patch(rect3)
    ax6.text(8, 8.4, 'Noise\n(Extrapolation)', ha='center', fontsize=9, fontweight='bold')
    ax6.text(8, 7.6, 'Low consistency\nRandom invention\nHigh temperature', ha='center', fontsize=6)
    
    # 箭头
    ax6.annotate('', xy=(6.5, 7.5), xytext=(3.5, 7.5),
                arrowprops=dict(arrowstyle='->', color='gray', lw=1.5))
    ax6.annotate('', xy=(9.5, 7.5), xytext=(6.5, 7.5),
                arrowprops=dict(arrowstyle='->', color='gray', lw=1.5))
    
    ax6.text(5, 5, 'Temperature / Context Drift -->', ha='center', fontsize=8)
    
    # 关键公式
    ax6.text(5, 3.5, 'Hallucination = f(T, knowledge_gap, context_drift)', 
             ha='center', fontsize=8, style='italic',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    ax6.text(5, 2, 'Creativity = Hallucination - Noise', 
             ha='center', fontsize=9, fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    # 统计
    ax6.text(5, 1, f'Final stats: Consistency drop {consistencies[0]-consistencies[-1]:.2f} | '
             f'Optimal T ~1.0 | Knowledge boundary at ~{spans[len(spans)//2]}',
             ha='center', fontsize=6, style='italic')
    
    fig.suptitle('#018 Hallucination — Emergence Spectrum of AI Fabrication', 
                 fontsize=14, fontweight='bold', y=0.98)
    
    plt.savefig('D:/openclaw_workspace/experiments/hallucination_spectrum.png', 
                dpi=150, bbox_inches='tight', facecolor='white')
    print("[OK] Saved: experiments/hallucination_spectrum.png")
    
    # 打印统计
    print(f"\n{'='*60}")
    print("STATISTICS:")
    print(f"  Consistency at pos 0: {consistencies[0]:.3f}")
    print(f"  Consistency at pos {len(consistencies)-1}: {consistencies[-1]:.3f}")
    print(f"  Total decay: {consistencies[0] - consistencies[-1]:.3f}")
    print(f"  Known-token rate at pos 0: {known_rates[0]:.3f}")
    print(f"  Known-token rate at end: {known_rates[-1]:.3f}")
    print(f"  Max creativity at T = {temps[np.argmax(creativity)]:.2f}: {max(creativity):.3f}")
    print(f"  Accuracy at T=0.7: {accuracy[6]:.3f}")
    print(f"  Accuracy at T=2.0: {accuracy[19]:.3f}")
    print(f"  Hallucination rate at knowledge=50%: {hall_rate[len(spans)//2]:.3f}")
    print(f"{'='*60}")

if __name__ == '__main__':
    plot_all()
