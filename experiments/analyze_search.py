"""分析Lenia参数搜索结果并生成可视化"""
import json, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Load results
with open('D:\\openclaw_workspace\\experiments\\output\\lenia_search_v2\\all_results.json', 'r', encoding='utf-8') as f:
    all_results = json.load(f)

print(f"Total results: {len(all_results)}")

# Top analysis
print("\n=== TOP 5 PARAMETER COMBINATIONS ===")
for i, r in enumerate(all_results[:5], 1):
    print(f"{i}. R={r['R']}, mu={r['mu']:.4f}, sigma={r['sigma']:.4f}, p={r['p_update']} → score={r['combined_score']:.4f}")
    print(f"   random: surv={r['random']['survival']:.2f} stab={r['random']['stability']:.2f} ent={r['random']['entropy']:.2f} div={r['random']['diversity']:.2f}")
    print(f"   orbium: surv={r['orbium']['survival']:.2f} stab={r['orbium']['stability']:.2f} ent={r['orbium']['entropy']:.2f} div={r['orbium']['diversity']:.2f}")

# R vs score
sync = [r for r in all_results if r['p_update'] == 1.0]
async_ = [r for r in all_results if r['p_update'] == 0.5]

print(f"\n=== SYNC vs ASYNC ===")
print(f"Synchronous (n={len(sync)}): max={max(r['combined_score'] for r in sync):.4f}, mean={np.mean([r['combined_score'] for r in sync]):.4f}")
async_max = max(r['combined_score'] for r in async_)
async_mean = np.mean([r['combined_score'] for r in async_])
print(f"Stochastic  (n={len(async_)}): max={async_max:.4f}, mean={async_mean:.4f}")

# R analysis
for R in sorted(set(r['R'] for r in all_results)):
    group = [r for r in all_results if r['R'] == R]
    top = max(r['combined_score'] for r in group)
    avg = np.mean([r['combined_score'] for r in group])
    print(f"R={R:2d}: top={top:.4f}, mean={avg:.4f}, count={len(group)}")

# Visualization
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# 1. R vs score
ax = axes[0]
for R in sorted(set(r['R'] for r in sync)):
    group = [r for r in sync if r['R'] == R]
    scores = [r['combined_score'] for r in group]
    ax.boxplot(scores, positions=[R], widths=1.5)
ax.set_xlabel('R (kernel radius)')
ax.set_ylabel('Combined Score')
ax.set_title('R vs Score (Synchronous)')

# 2. mu vs sigma heatmap for best R
ax = axes[1]
best_R = 20  # based on analysis
group = [r for r in sync if r['R'] == best_R]
mu_vals = sorted(set(r['mu'] for r in group))
sigma_vals = sorted(set(r['sigma'] for r in group))
heatmap = np.zeros((len(mu_vals), len(sigma_vals)))
for r in group:
    mi = mu_vals.index(r['mu'])
    si = sigma_vals.index(r['sigma'])
    heatmap[mi, si] = r['combined_score']

im = ax.imshow(heatmap, aspect='auto', origin='lower', cmap='viridis')
ax.set_xticks(range(len(sigma_vals)))
ax.set_xticklabels([f'{s:.3f}' for s in sigma_vals], rotation=45)
ax.set_yticks(range(len(mu_vals)))
ax.set_yticklabels([f'{m:.3f}' for m in mu_vals])
ax.set_xlabel('sigma')
ax.set_ylabel('mu')
ax.set_title(f'Score heatmap (R={best_R})')
plt.colorbar(im, ax=ax)

# 3. Sync vs Async comparison
ax = axes[2]
sync_scores = [r['combined_score'] for r in sync]
async_scores = [r['combined_score'] for r in async_]
ax.hist(sync_scores, bins=30, alpha=0.5, label=f'Sync (n={len(sync)})')
ax.hist(async_scores, bins=30, alpha=0.5, label=f'Async 0.5 (n={len(async_)})')
ax.set_xlabel('Score')
ax.set_ylabel('Count')
ax.set_title('Score Distribution: Sync vs Async')
ax.legend()

plt.suptitle('Lenia Parameter Search Results', fontsize=14)
plt.tight_layout()
plt.savefig('D:\\openclaw_workspace\\experiments\\output\\lenia_search_v2\\analysis.png', dpi=150)
print("\nSaved analysis plot to output/lenia_search_v2/analysis.png")

# Best params summary
best = all_results[0]
print(f"\n=== BEST OVERALL ===")
print(f"R={best['R']}, mu={best['mu']:.4f}, sigma={best['sigma']:.4f}, p_update={best['p_update']}")
print(f"Score: {best['combined_score']:.4f}")
