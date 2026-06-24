"""
#024 Predictive Processing — 感知即受控幻觉
===========================================
核心观点：大脑不是被动接收信息，而是主动生成预测，
然后用感官输入来修正预测。感知 = 先验 × 似然。

实验：
1. 层级预测编码 — 2层网络模拟
2. 模糊刺激 — 先验如何塑造感知
3. 预测误差动力学
4. 精确性加权 — 噪声如何改变学习
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.colors import LinearSegmentedColormap
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

# ============================================================
# 1. HIERARCHICAL PREDICTIVE CODING SIMULATION
# ============================================================

def run_predictive_coding(seq_length=100, noise_level=0.3, learning_rate=0.05):
    """
    简单的2层预测编码：
    - High level: 学习序列规律（正弦波频率）
    - Low level: 生成具体预测
    - Prediction error 从低层传到高层驱动学习
    """
    # 生成序列：具有模式但带噪声
    t = np.linspace(0, 4*np.pi, seq_length)
    clean = np.sin(t) + 0.3 * np.sin(3*t)
    noisy = clean + noise_level * np.random.randn(seq_length)
    
    # 高层模型：估计频率和相位
    freq_est = 1.0  # 初始猜测
    phase_est = 0.0
    amp_est = 1.0
    
    predictions = np.zeros(seq_length)
    pred_errors = np.zeros(seq_length)
    freq_history = [freq_est]
    error_history = []
    
    for i in range(seq_length):
        # 高层生成预测
        prediction = amp_est * np.sin(freq_est * t[i] + phase_est)
        predictions[i] = prediction
        
        # 计算预测误差
        error = noisy[i] - prediction
        pred_errors[i] = error
        
        # 高层更新（误差驱动学习）
        grad_freq = amp_est * t[i] * np.cos(freq_est * t[i] + phase_est)
        freq_est += learning_rate * error * grad_freq * 0.01
        
        # 简易相位和幅度调整
        phase_est += learning_rate * error * 0.1
        amp_est += learning_rate * error * np.sin(freq_est * t[i] + phase_est) * 0.05
        
        freq_history.append(freq_est)
        error_history.append(abs(error))
    
    return {
        'clean': clean, 'noisy': noisy,
        'predictions': predictions, 'pred_errors': pred_errors,
        'freq_history': freq_history, 'error_history': error_history
    }

# ============================================================
# 2. AMBIGUOUS STIMULI — PRIOR SHAPES PERCEPTION
# ============================================================

def run_ambiguous_perception(size=100, trials=10):
    """
    模拟模糊刺激感知：两可图像（如Necker cube）
    先验（prior）决定你看到什么
    """
    # 模糊输入：两个模式重叠
    pattern_a = np.zeros((size, size))
    pattern_b = np.zeros((size, size))
    
    cx, cy = size//2, size//2
    
    # Pattern A: 从左上到右下的对角线梯度
    for x in range(size):
        for y in range(size):
            pattern_a[y, x] = np.exp(-((x-cx)**2 + (y-cy)**2) / (2*(size/4)**2))
            pattern_a[y, x] *= (0.5 + 0.5 * np.sin(0.1 * (x + y)))
    
    # Pattern B: 从右上到左下的对角线梯度  
    for x in range(size):
        for y in range(size):
            pattern_b[y, x] = np.exp(-((x-cx)**2 + (y-cy)**2) / (2*(size/4)**2))
            pattern_b[y, x] *= (0.5 + 0.5 * np.sin(0.1 * (x - y + size)))
    
    # 模糊输入 = 混合
    blend = 0.5 * pattern_a + 0.5 * pattern_b
    
    # 不同先验下的感知：
    priors = np.linspace(-0.5, 0.5, trials)
    perceptions = []
    
    for prior_bias in priors:
        # 先验偏差影响感知权重
        w_a = 0.5 - prior_bias
        w_b = 0.5 + prior_bias
        w_a = np.clip(w_a, 0, 1)
        w_b = np.clip(w_b, 0, 1)
        
        # 感知 = 先验 * 输入（实际是预测更新后的结果）
        perceived = w_a * pattern_a + w_b * pattern_b
        perceptions.append(perceived)
    
    return pattern_a, pattern_b, blend, priors, perceptions


# ============================================================
# 3. PRECISION-WEIGHTED PREDICTION ERROR
# ============================================================

def run_precision_weighting(segments=4, points_per_segment=30):
    """
    精确性加权：不同噪声水平的信号段，
    大脑应该给予"可信"信号更高权重
    """
    total = segments * points_per_segment
    t = np.linspace(0, 2*np.pi*segments, total)
    
    # 干净的底层信号
    true_signal = np.sin(t)
    
    # 不同段的噪声水平不同
    noise_levels = [0.1, 0.8, 0.2, 1.2]  # 精确性 = 1/noise
    noisy_signal = np.copy(true_signal)
    
    for seg in range(segments):
        start = seg * points_per_segment
        end = (seg + 1) * points_per_segment
        noisy_signal[start:end] += noise_levels[seg] * np.random.randn(points_per_segment)
    
    # 贝叶斯更新：精确性越高，更新幅度越大
    precision = [1.0 / max(n, 0.01) for n in noise_levels]
    
    estimates = np.zeros(total)
    uncertainty = np.ones(total) * 2.0  # 初始高不确定性
    
    for i in range(total):
        seg = i // points_per_segment
        prior_est = estimates[i-1] if i > 0 else 0.0
        prior_uncertainty = uncertainty[i-1] if i > 0 else 2.0
        
        # 精确性加权的贝叶斯更新
        sensory_precision = 1.0 / max(noise_levels[seg], 0.01)
        posterior_precision = 1.0/prior_uncertainty + sensory_precision
        posterior_uncertainty = 1.0 / posterior_precision
        
        # 估计 = 先验 + (精确性比) × 预测误差
        kalman_gain = sensory_precision / posterior_precision
        estimates[i] = prior_est + kalman_gain * (noisy_signal[i] - prior_est)
        uncertainty[i] = posterior_uncertainty
    
    return t, true_signal, noisy_signal, estimates, uncertainty, noise_levels, precision


# ============================================================
# MAIN: GENERATE ALL VISUALIZATIONS
# ============================================================

def make_predictive_coding_fig(results):
    """Figure 1: Hierarchical predictive coding"""
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), facecolor='#f5f0e8')
    
    # 1. 信号 vs 预测
    ax = axes[0]
    x = np.arange(len(results['clean']))
    ax.plot(x, results['clean'], 'k-', alpha=0.3, label='True signal', linewidth=1)
    ax.plot(x, results['noisy'], 'o', color='#7a9cc6', markersize=2, alpha=0.5, label='Noisy input')
    ax.plot(x, results['predictions'], '-', color='#e07a5f', linewidth=2.5, label='Prediction')
    ax.set_ylabel('Amplitude', fontsize=11)
    ax.legend(fontsize=10, loc='upper right')
    ax.set_title('Predictive Coding: Perception Minimizes Prediction Error', 
                 fontsize=13, fontweight='bold', pad=10)
    ax.set_xlim(0, len(results['clean'])-1)
    ax.grid(True, alpha=0.2)
    
    # 2. 预测误差
    ax = axes[1]
    ax.fill_between(x, 0, np.abs(results['pred_errors']), 
                     color='#e07a5f', alpha=0.3)
    ax.plot(x, results['pred_errors'], '-', color='#e07a5f', linewidth=1.5)
    ax.axhline(y=0, color='k', linewidth=0.5, alpha=0.5)
    ax.set_ylabel('Prediction Error', fontsize=11)
    ax.set_xlim(0, len(results['clean'])-1)
    ax.grid(True, alpha=0.2)
    
    # 3. 频率估计演变
    ax = axes[2]
    true_freq = 1.0
    ax.axhline(y=true_freq, color='k', linestyle='--', alpha=0.5, label=f'True freq = {true_freq}')
    ax.plot(results['freq_history'], '-', color='#81b29a', linewidth=2, label='Estimated frequency')
    ax.fill_between(range(len(results['freq_history'])), 
                     results['freq_history'], true_freq,
                     alpha=0.2, color='#81b29a')
    ax.set_xlabel('Time step', fontsize=11)
    ax.set_ylabel('Frequency', fontsize=11)
    ax.legend(fontsize=10)
    ax.set_xlim(0, len(results['freq_history'])-1)
    ax.grid(True, alpha=0.2)
    
    plt.tight_layout()
    plt.savefig('experiments/predictive_encoding.png', dpi=120, bbox_inches='tight')
    plt.close()


def make_ambiguous_fig(pattern_a, pattern_b, blend, priors, perceptions):
    """Figure 2: Ambiguous stimuli — prior shapes perception"""
    fig, axes = plt.subplots(2, 6, figsize=(18, 7), facecolor='#f5f0e8')
    
    # 原始模式
    ax = axes[0, 0]
    im = ax.imshow(pattern_a, cmap='RdYlBu_r', aspect='equal')
    ax.set_title('Pattern A', fontsize=10, fontweight='bold')
    ax.axis('off')
    
    ax = axes[0, 1]
    im = ax.imshow(pattern_b, cmap='RdYlBu_r', aspect='equal')
    ax.set_title('Pattern B', fontsize=10, fontweight='bold')
    ax.axis('off')
    
    ax = axes[0, 2]
    im = ax.imshow(blend, cmap='RdYlBu_r', aspect='equal')
    ax.set_title('Ambiguous Input\n(50/50 blend)', fontsize=10, fontweight='bold')
    ax.axis('off')
    
    # "感知 = 受控幻觉"
    ax = axes[0, 3]
    for i, (prior, perc) in enumerate(zip(priors, perceptions)):
        row = (i // 6)
        col = (i % 6)
        ax_actual = axes[row, col]
        ax_actual.imshow(perc, cmap='RdYlBu_r', aspect='equal')
        bias_pct = int(prior * 100)
        ax_actual.set_title(f'Prior bias: {bias_pct:+d}%', fontsize=9)
        ax_actual.axis('off')
    
    # Hue: each prior produces a different "perception" of same input
    
    # 底部行：先验-感知映射
    ax = axes[1, 3]
    for i in range(6):
        if i < len(priors):
            ax_actual = axes[1, i]
            ax_actual.imshow(perceptions[i], cmap='RdYlBu_r', aspect='equal')
            bias_pct = int(priors[i] * 100)
            ax_actual.set_title(f'Bias: {bias_pct:+d}%', fontsize=9)
            ax_actual.axis('off')
    
    # 先验影响曲线
    ax = axes[1, 4]
    diff_measures = []
    for perc in perceptions:
        diff_a = np.mean(np.abs(perc - pattern_a))
        diff_b = np.mean(np.abs(perc - pattern_b))
        diff_measures.append(diff_a / (diff_a + diff_b + 1e-10))
    
    ax.plot(priors * 100, [1 - d for d in diff_measures], 'o-', color='#3d405b', 
            linewidth=2.5, markersize=8, markerfacecolor='#e07a5f')
    ax.axhline(y=0.5, color='k', linestyle='--', alpha=0.3)
    ax.set_xlabel('Prior Bias (%)', fontsize=11)
    ax.set_ylabel('Perceptual Dominance\n(Pattern A)', fontsize=11)
    ax.set_title('Prior → Perception Mapping', fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.2)
    ax.set_xlim(-55, 55)
    ax.set_ylim(0, 1)
    
    # 说明
    ax = axes[1, 5]
    ax.axis('off')
    msg = ("Ambiguous Stimuli\n\n"
           "Same input, different priors\n→ different perceptions\n\n"
           "The brain doesn't passively\nreceive. It actively predicts.\n\n"
           "\"Perception is controlled\n hallucination\"\n- R. Gregory")
    ax.text(0.1, 0.7, msg, fontsize=9, fontfamily='monospace',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#e8dcc4', alpha=0.8))
    
    plt.suptitle('Predictive Processing: Priors Shape Perception', 
                 fontsize=14, fontweight='bold', y=1.01)
    plt.tight_layout()
    plt.savefig('experiments/ambiguous_perception.png', dpi=120, bbox_inches='tight')
    plt.close()


def make_precision_fig(t, true_signal, noisy_signal, estimates, uncertainty, noise_levels, precision):
    """Figure 3: Precision-weighted prediction error"""
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), facecolor='#f5f0e8')
    
    # 颜色区分不同段
    colors = ['#3d405b', '#e07a5f', '#81b29a', '#f2cc8f']
    segments = len(noise_levels)
    points_per_segment = len(t) // segments
    
    # 1. 信号 + 噪声 + 估计
    ax = axes[0]
    for seg in range(segments):
        start = seg * points_per_segment
        end = (seg + 1) * points_per_segment if seg < segments - 1 else len(t)
        ax.axvspan(t[start], t[end-1], alpha=0.08, color=colors[seg])
        ax.plot(t[start:end], noisy_signal[start:end], 'o', color=colors[seg], 
                markersize=2, alpha=0.4)
        ax.plot(t[start:end], estimates[start:end], '-', color='#000000', 
                linewidth=2.5, alpha=0.9)
    
    ax.plot(t, true_signal, '--', color='#7a9cc6', linewidth=1.5, alpha=0.6, label='True signal')
    
    # 标注噪声水平
    for seg in range(segments):
        mid = (seg * points_per_segment + (seg+1) * points_per_segment) // 2
        ax.annotate(f'σ={noise_levels[seg]}', xy=(t[mid], max(noisy_signal)), 
                    fontsize=9, color=colors[seg], fontweight='bold',
                    ha='center', va='bottom')
    
    ax.set_ylabel('Signal', fontsize=11)
    ax.set_title('Precision-Weighted Bayesian Perception', 
                 fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.set_xlim(t[0], t[-1])
    ax.grid(True, alpha=0.2)
    
    # 2. 不确定性演变
    ax = axes[1]
    for seg in range(segments):
        start = seg * points_per_segment
        end = (seg + 1) * points_per_segment if seg < segments - 1 else len(t)
        ax.axvspan(t[start], t[end-1], alpha=0.08, color=colors[seg])
    
    ax.plot(t, uncertainty, '-', color='#e07a5f', linewidth=2.5)
    ax.fill_between(t, 0, uncertainty, color='#e07a5f', alpha=0.15)
    for seg in range(segments):
        mid = (seg * points_per_segment + (seg+1) * points_per_segment) // 2
        ax.annotate(f'Precision={precision[seg]:.1f}', xy=(t[mid], max(uncertainty)*0.9),
                    fontsize=9, color=colors[seg], fontweight='bold',
                    ha='center')
    ax.set_ylabel('Posterior Uncertainty', fontsize=11)
    ax.set_xlim(t[0], t[-1])
    ax.grid(True, alpha=0.2)
    
    # 3. Kalman gain (精确性比)
    ax = axes[2]
    kalman_gains = []
    for i in range(len(t)):
        seg = i // points_per_segment
        sensory_precision = 1.0 / max(noise_levels[seg], 0.01)
        prior_unc = uncertainty[i-1] if i > 0 else 2.0
        posterior_precision = 1.0/prior_unc + sensory_precision
        kg = sensory_precision / posterior_precision
        kalman_gains.append(kg)
    
    for seg in range(segments):
        start = seg * points_per_segment
        end = (seg + 1) * points_per_segment if seg < segments - 1 else len(t)
        ax.axvspan(t[start], t[end-1], alpha=0.08, color=colors[seg])
    
    ax.plot(t, kalman_gains, '-', color='#81b29a', linewidth=2.5)
    ax.fill_between(t, 0, kalman_gains, color='#81b29a', alpha=0.15)
    ax.set_xlabel('Time', fontsize=11)
    ax.set_ylabel('Kalman Gain\n(Learning Rate)', fontsize=11)
    ax.set_xlim(t[0], t[-1])
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.2)
    ax.set_title('High Precision → High Learning Rate', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('experiments/precision_weighting.png', dpi=120, bbox_inches='tight')
    plt.close()


def make_hierarchy_fig():
    """Figure 4: Hierarchical predictive processing architecture"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8), facecolor='#f5f0e8')
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # 层级架构
    levels = [
        {'y': 6.5, 'label': 'High-Level\nAbstraction', 'color': '#3d405b',
         'desc': 'Long-range patterns\nConcepts, Categories\n\nPredicts lower level'},
        {'y': 4.0, 'label': 'Mid-Level\nFeatures', 'color': '#81b29a',
         'desc': 'Objects, Shapes\nGestalt patterns\n\nCompares prediction\nvs input'},
        {'y': 1.5, 'label': 'Low-Level\nSensation', 'color': '#e07a5f',
         'desc': 'Raw sensory pixels\nLocal features\n\nSends prediction\nerror upward'}
    ]
    
    predictions = []
    errors = []
    
    for lv in levels:
        y = lv['y']
        box = FancyBboxPatch((1.5, y-0.6), 4, 1.2, 
                              boxstyle="round,pad=0.1",
                              facecolor=lv['color'], alpha=0.85, edgecolor='none')
        ax.add_patch(box)
        ax.text(3.5, y, lv['label'], fontsize=11, fontweight='bold', 
                color='white', ha='center', va='center')
        
        # 右侧描述
        ax.text(7.5, y, lv['desc'], fontsize=9, va='center', color='#3d405b',
                fontfamily='monospace')
    
    # 向下的预测箭头
    for i in range(len(levels)-1):
        y1 = levels[i]['y'] - 0.6
        y2 = levels[i+1]['y'] + 0.6
        ax.annotate('', xy=(2.5, y2), xytext=(2.5, y1),
                    arrowprops=dict(arrowstyle='->', color='#81b29a', lw=2.5))
    
    # 向上的误差箭头  
    for i in range(len(levels)-1):
        y1 = levels[i+1]['y'] + 0.6
        y2 = levels[i]['y'] - 0.6
        ax.annotate('', xy=(4.5, y2), xytext=(4.5, y1),
                    arrowprops=dict(arrowstyle='->', color='#e07a5f', lw=2.5))
    
    # 标注
    ax.text(2.5, 0.1, 'Predictions (top-down)', fontsize=9, color='#81b29a', 
            ha='center', fontweight='bold')
    ax.text(4.5, 0.1, 'Prediction Errors (bottom-up)', fontsize=9, color='#e07a5f', 
            ha='center', fontweight='bold')
    
    # 标题和核心公式
    ax.text(6, 7.5, 'Hierarchical Predictive Processing', fontsize=14, fontweight='bold',
            ha='center', color='#3d405b')
    
    formula = ("Perception = argmin(Prediction Error)\n\n"
               "            prediction error\n"
               "Prior ←─────────────── Posterior\n"
               "      ───────────────→\n"
               "           prediction")
    ax.text(9.5, 2.5, formula, fontsize=10, fontfamily='monospace', 
            color='#3d405b', ha='center',
            bbox=dict(boxstyle='round,pad=0.8', facecolor='white', 
                       edgecolor='#3d405b', alpha=0.9))
    
    plt.savefig('experiments/predictive_hierarchy.png', dpi=120, bbox_inches='tight')
    plt.close()


# ============================================================
# RUN ALL
# ============================================================

print("=== #024 Predictive Processing ===")

print("\n[1/4] Hierarchical predictive coding simulation...")
results = run_predictive_coding(seq_length=100, noise_level=0.3, learning_rate=0.05)
make_predictive_coding_fig(results)
print("  → predictive_encoding.png")

print("\n[2/4] Ambiguous stimuli (prior shapes perception)...")
pattern_a, pattern_b, blend, priors, perceptions = run_ambiguous_perception(size=80, trials=10)
make_ambiguous_fig(pattern_a, pattern_b, blend, priors, perceptions)
print("  → ambiguous_perception.png")

print("\n[3/4] Precision-weighted perception...")
t, true_signal, noisy_signal, estimates, uncertainty, noise_levels, precision = run_precision_weighting()
make_precision_fig(t, true_signal, noisy_signal, estimates, uncertainty, noise_levels, precision)
print("  → precision_weighting.png")

print("\n[4/4] Hierarchical architecture diagram...")
make_hierarchy_fig()
print("  → predictive_hierarchy.png")

print("\n=== Done ===")
