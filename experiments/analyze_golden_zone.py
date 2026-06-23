"""
Golden Zone Experiment Analysis
Analyzes the relationship between regrowth rate, density, energy, and curiosity rates.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os

# Load data
data_path = 'D:/openclaw_workspace/experiments/results/golden_zone_data_20260623_210136.json'
with open(data_path, 'r') as f:
    data = json.load(f)

params = np.array([(p['regrowth'], p['density'], p['energy']) for p in data['params']])
regrowth = params[:, 0]
density = params[:, 1]
energy = params[:, 2]

curiosity_rates = np.array(data['curiosity_rates'])
survival_steps = np.array(data['survival_steps'])
is_alive = np.array(data['is_alive'])
scores = np.array(data['scores'])

# Unique values
unique_regrowth = np.unique(regrowth)
unique_density = np.unique(density)
unique_energy = np.unique(energy)

print(f"Dataset: {len(params)} experiments")
print(f"Regrowth rates: {len(unique_regrowth)} values from {unique_regrowth.min():.4f} to {unique_regrowth.max():.4f}")
print(f"Densities: {len(unique_density)} values from {unique_density.min():.4f} to {unique_density.max():.4f}")
print(f"Energies: {len(unique_energy)} values from {unique_energy.min():.1f} to {unique_energy.max():.1f}")

# Output directory
output_dir = 'D:/openclaw_workspace/experiments/results'
os.makedirs(output_dir, exist_ok=True)

# =============================================================================
# 1. Distribution Analysis
# =============================================================================
print("\n=== Distribution Analysis ===")

# Create figure with subplots for distributions
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1.1 Curiosity rate distribution
ax1 = axes[0, 0]
ax1.hist(curiosity_rates * 100, bins=30, color='steelblue', edgecolor='black', alpha=0.7)
ax1.set_xlabel('Curiosity Rate (%)', fontsize=12)
ax1.set_ylabel('Frequency', fontsize=12)
ax1.set_title('Distribution of Curiosity Rates', fontsize=14)
ax1.axvline(x=10, color='red', linestyle='--', label='Golden Zone Threshold (10%)')
ax1.legend()

# 1.2 Survival steps distribution
ax2 = axes[0, 1]
ax2.hist(survival_steps, bins=30, color='forestgreen', edgecolor='black', alpha=0.7)
ax2.set_xlabel('Survival Steps', fontsize=12)
ax2.set_ylabel('Frequency', fontsize=12)
ax2.set_title('Distribution of Survival Steps', fontsize=14)
ax2.axvline(x=100, color='red', linestyle='--', label='Golden Zone Threshold (100)')
ax2.legend()

# 1.3 Curiosity rate by energy level
ax3 = axes[1, 0]
for e in unique_energy:
    mask = energy == e
    rates = curiosity_rates[mask] * 100
    ax3.hist(rates, bins=20, alpha=0.5, label=f'Energy={int(e)}')
ax3.set_xlabel('Curiosity Rate (%)', fontsize=12)
ax3.set_ylabel('Frequency', fontsize=12)
ax3.set_title('Curiosity Rate Distribution by Energy Level', fontsize=14)
ax3.legend()

# 1.4 Survival steps by energy level
ax4 = axes[1, 1]
for e in unique_energy:
    mask = energy == e
    steps = survival_steps[mask]
    ax4.hist(steps, bins=20, alpha=0.5, label=f'Energy={int(e)}')
ax4.set_xlabel('Survival Steps', fontsize=12)
ax4.set_ylabel('Frequency', fontsize=12)
ax4.set_title('Survival Steps Distribution by Energy Level', fontsize=14)
ax4.legend()

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'golden_zone_distributions.png'), dpi=150)
plt.close()
print("Saved: golden_zone_distributions.png")

# =============================================================================
# 2. Heatmaps
# =============================================================================
print("\n=== Generating Heatmaps ===")

# Create heatmaps for each energy level
fig_heat, axes_heat = plt.subplots(2, 2, figsize=(14, 12))
axes_heat = axes_heat.flatten()

for idx, e in enumerate(unique_energy):
    ax = axes_heat[idx]
    
    # Filter data for this energy level
    mask = energy == e
    r_vals = regrowth[mask]
    d_vals = density[mask]
    c_rates = curiosity_rates[mask]
    
    # Create grid
    n_regrowth = len(unique_regrowth)
    n_density = len(unique_density)
    
    heatmap_data = np.full((n_density, n_regrowth), np.nan)
    
    for i, (r, d, c) in enumerate(zip(r_vals, d_vals, c_rates)):
        ri = np.where(unique_regrowth == r)[0][0]
        di = np.where(unique_density == d)[0][0]
        heatmap_data[di, ri] = c * 100  # Convert to percentage
    
    im = ax.imshow(heatmap_data, cmap='YlOrRd', aspect='auto', vmin=0, vmax=50)
    ax.set_xticks(range(n_regrowth))
    ax.set_xticklabels([f'{x:.3f}' for x in unique_regrowth], rotation=45, ha='right')
    ax.set_yticks(range(n_density))
    ax.set_yticklabels([f'{x:.2f}' for x in unique_density])
    ax.set_xlabel('Regrowth Rate', fontsize=11)
    ax.set_ylabel('Density', fontsize=11)
    ax.set_title(f'Curiosity Rate Heatmap (Energy={int(e)})', fontsize=13)
    
    # Add colorbar
    plt.colorbar(im, ax=ax, label='Curiosity Rate (%)')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'golden_zone_heatmaps_curiosity.png'), dpi=150)
plt.close()
print("Saved: golden_zone_heatmaps_curiosity.png")

# Survival steps heatmaps
fig_heat2, axes_heat2 = plt.subplots(2, 2, figsize=(14, 12))
axes_heat2 = axes_heat2.flatten()

for idx, e in enumerate(unique_energy):
    ax = axes_heat2[idx]
    
    mask = energy == e
    r_vals = regrowth[mask]
    d_vals = density[mask]
    s_steps = survival_steps[mask]
    
    n_regrowth = len(unique_regrowth)
    n_density = len(unique_density)
    
    heatmap_data = np.full((n_density, n_regrowth), np.nan)
    
    for i, (r, d, s) in enumerate(zip(r_vals, d_vals, s_steps)):
        ri = np.where(unique_regrowth == r)[0][0]
        di = np.where(unique_density == d)[0][0]
        heatmap_data[di, ri] = s
    
    im = ax.imshow(heatmap_data, cmap='YlGn', aspect='auto')
    ax.set_xticks(range(n_regrowth))
    ax.set_xticklabels([f'{x:.3f}' for x in unique_regrowth], rotation=45, ha='right')
    ax.set_yticks(range(n_density))
    ax.set_yticklabels([f'{x:.2f}' for x in unique_density])
    ax.set_xlabel('Regrowth Rate', fontsize=11)
    ax.set_ylabel('Density', fontsize=11)
    ax.set_title(f'Survival Steps Heatmap (Energy={int(e)})', fontsize=13)
    
    plt.colorbar(im, ax=ax, label='Survival Steps')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'golden_zone_heatmaps_survival.png'), dpi=150)
plt.close()
print("Saved: golden_zone_heatmaps_survival.png")

# =============================================================================
# 3. Statistical Analysis
# =============================================================================
print("\n=== Statistical Analysis ===")

from scipy import stats

# Correlation analysis
print("\n--- Correlation with Curiosity Rate ---")
r_corr_regrowth, p_regrowth = stats.pearsonr(regrowth, curiosity_rates)
r_corr_density, p_density = stats.pearsonr(density, curiosity_rates)
r_corr_energy, p_energy = stats.pearsonr(energy, curiosity_rates)

print(f"Regrowth: r={r_corr_regrowth:.4f}, p={p_regrowth:.6f}")
print(f"Density: r={r_corr_density:.4f}, p={p_density:.6f}")
print(f"Energy: r={r_corr_energy:.4f}, p={p_energy:.6f}")

print("\n--- Correlation with Survival Steps ---")
r_corr_regrowth_s, p_regrowth_s = stats.pearsonr(regrowth, survival_steps)
r_corr_density_s, p_density_s = stats.pearsonr(density, survival_steps)
r_corr_energy_s, p_energy_s = stats.pearsonr(energy, survival_steps)

print(f"Regrowth: r={r_corr_regrowth_s:.4f}, p={p_regrowth_s:.6f}")
print(f"Density: r={r_corr_density_s:.4f}, p={p_density_s:.6f}")
print(f"Energy: r={r_corr_energy_s:.4f}, p={p_energy_s:.6f}")

# Multiple regression
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score

X = np.column_stack([regrowth, density, energy])

# For curiosity rate
scaler_c = StandardScaler()
X_scaled = scaler_c.fit_transform(X)
lr_c = LinearRegression()
lr_c.fit(X_scaled, curiosity_rates)

print("\n--- Linear Regression for Curiosity Rate ---")
print(f"Intercept: {lr_c.intercept_:.6f}")
print(f"Regrowth coefficient: {lr_c.coef_[0]:.6f}")
print(f"Density coefficient: {lr_c.coef_[1]:.6f}")
print(f"Energy coefficient: {lr_c.coef_[2]:.6f}")
print(f"R-squared score: {lr_c.score(X_scaled, curiosity_rates):.4f}")

# For survival steps
lr_s = LinearRegression()
lr_s.fit(X_scaled, survival_steps)

print("\n--- Linear Regression for Survival Steps ---")
print(f"Intercept: {lr_s.intercept_:.6f}")
print(f"Regrowth coefficient: {lr_s.coef_[0]:.6f}")
print(f"Density coefficient: {lr_s.coef_[1]:.6f}")
print(f"Energy coefficient: {lr_s.coef_[2]:.6f}")
print(f"R-squared score: {lr_s.score(X_scaled, survival_steps):.4f}")

# Interaction effects
print("\n--- Interaction Effects ---")
# Regrowth * Density interaction
interaction_rd = regrowth * density
r_int_rd, p_int_rd = stats.pearsonr(interaction_rd, curiosity_rates)
print(f"Regrowth * Density interaction: r={r_int_rd:.4f}, p={p_int_rd:.6f}")

# Regrowth * Energy interaction
interaction_re = regrowth * energy
r_int_re, p_int_re = stats.pearsonr(interaction_re, curiosity_rates)
print(f"Regrowth * Energy interaction: r={r_int_re:.4f}, p={p_int_re:.6f}")

# Density * Energy interaction
interaction_de = density * energy
r_int_de, p_int_de = stats.pearsonr(interaction_de, curiosity_rates)
print(f"Density * Energy interaction: r={r_int_de:.4f}, p={p_int_de:.6f}")

# Create correlation visualization
fig_corr, axes_corr = plt.subplots(1, 2, figsize=(14, 5))

# Curiosity rate correlations
labels = ['Regrowth', 'Density', 'Energy', 'R×D', 'R×E', 'D×E']
correlations_c = [
    r_corr_regrowth, r_corr_density, r_corr_energy,
    r_int_rd, r_int_re, r_int_de
]
colors = ['steelblue' if c > 0 else 'coral' for c in correlations_c]
axes_corr[0].bar(labels, correlations_c, color=colors, edgecolor='black')
axes_corr[0].set_ylabel('Correlation Coefficient (r)', fontsize=12)
axes_corr[0].set_title('Correlation with Curiosity Rate', fontsize=14)
axes_corr[0].axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
axes_corr[0].set_ylim(-1, 1)

# Survival steps correlations
correlations_s = [
    r_corr_regrowth_s, r_corr_density_s, r_corr_energy_s,
    stats.pearsonr(regrowth * density, survival_steps)[0],
    stats.pearsonr(regrowth * energy, survival_steps)[0],
    stats.pearsonr(density * energy, survival_steps)[0]
]
colors_s = ['forestgreen' if c > 0 else 'coral' for c in correlations_s]
axes_corr[1].bar(labels, correlations_s, color=colors_s, edgecolor='black')
axes_corr[1].set_ylabel('Correlation Coefficient (r)', fontsize=12)
axes_corr[1].set_title('Correlation with Survival Steps', fontsize=14)
axes_corr[1].axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
axes_corr[1].set_ylim(-1, 1)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'golden_zone_correlations.png'), dpi=150)
plt.close()
print("Saved: golden_zone_correlations.png")

# =============================================================================
# 4. Golden Zone Identification
# =============================================================================
print("\n=== Golden Zone Identification ===")
print("Criteria: Curiosity Rate > 10% AND Survival Steps > 100")

golden_mask = (curiosity_rates > 0.10) & (survival_steps > 100)
golden_indices = np.where(golden_mask)[0]

print(f"\nGolden Zone experiments: {len(golden_indices)} out of {len(params)} ({100*len(golden_indices)/len(params):.1f}%)")

if len(golden_indices) > 0:
    golden_params = params[golden_mask]
    golden_regrowth = golden_params[:, 0]
    golden_density = golden_params[:, 1]
    golden_energy = golden_params[:, 2]
    golden_curiosity = curiosity_rates[golden_mask]
    golden_survival = survival_steps[golden_mask]
    
    print(f"\n--- Golden Zone Parameter Ranges ---")
    print(f"Regrowth Rate: {golden_regrowth.min():.4f} - {golden_regrowth.max():.4f}")
    print(f"Density: {golden_density.min():.4f} - {golden_density.max():.4f}")
    print(f"Energy: {golden_energy.min():.1f} - {golden_energy.max():.1f}")
    
    print(f"\n--- Golden Zone Performance ---")
    print(f"Curiosity Rate: {golden_curiosity.min()*100:.1f}% - {golden_curiosity.max()*100:.1f}% (mean: {golden_curiosity.mean()*100:.1f}%)")
    print(f"Survival Steps: {golden_survival.min():.0f} - {golden_survival.max():.0f} (mean: {golden_survival.mean():.0f})")
    
    # Top 10 golden zone configurations
    print(f"\n--- Top 10 Golden Zone Configurations ---")
    sorted_indices = np.argsort(golden_curiosity)[::-1][:10]
    print("Rank | Regrowth | Density | Energy | Curiosity% | Survival")
    print("-" * 60)
    for rank, idx in enumerate(sorted_indices, 1):
        print(f"{rank:4d} | {golden_regrowth[idx]:.4f}   | {golden_density[idx]:.4f}  | {int(golden_energy[idx]):5d}  | {golden_curiosity[idx]*100:8.1f}%  | {int(golden_survival[idx]):6d}")
    
    # Create golden zone visualization
    fig_gz = plt.figure(figsize=(16, 6))
    
    # 3D scatter plot
    ax1 = fig_gz.add_subplot(131, projection='3d')
    scatter = ax1.scatter(regrowth, density, energy, c=curiosity_rates*100, cmap='YlOrRd', 
                         alpha=0.5, s=20, label='All experiments')
    golden_scatter = ax1.scatter(golden_regrowth, golden_density, golden_energy, 
                                 c=golden_curiosity*100, cmap='YlOrRd', 
                                 edgecolors='black', linewidths=1, s=60, marker='*', 
                                 label='Golden Zone')
    ax1.set_xlabel('Regrowth Rate')
    ax1.set_ylabel('Density')
    ax1.set_zlabel('Energy')
    ax1.set_title('3D Parameter Space\n(Golden Zone = Stars)')
    plt.colorbar(scatter, ax=ax1, label='Curiosity %', shrink=0.6)
    ax1.legend(loc='upper left')
    
    # 2D projection: Regrowth vs Density
    ax2 = fig_gz.add_subplot(132)
    ax2.scatter(regrowth, density, c=curiosity_rates*100, cmap='YlOrRd', alpha=0.4, s=20)
    ax2.scatter(golden_regrowth, golden_density, c=golden_curiosity*100, cmap='YlOrRd', 
               edgecolors='black', linewidths=1, s=80, marker='*')
    ax2.set_xlabel('Regrowth Rate', fontsize=12)
    ax2.set_ylabel('Density', fontsize=12)
    ax2.set_title('Golden Zone: Regrowth vs Density\n(Color = Curiosity %)')
    
    # Highlight boundaries
    ax2.axvline(x=golden_regrowth.min(), color='green', linestyle='--', alpha=0.5, label='Boundary')
    ax2.axvline(x=golden_regrowth.max(), color='green', linestyle='--', alpha=0.5)
    ax2.axhline(y=golden_density.min(), color='green', linestyle='--', alpha=0.5)
    ax2.axhline(y=golden_density.max(), color='green', linestyle='--', alpha=0.5)
    ax2.legend()
    
    # Curiosity vs Survival scatter
    ax3 = fig_gz.add_subplot(133)
    ax3.scatter(survival_steps, curiosity_rates*100, c='steelblue', alpha=0.4, s=20, label='All experiments')
    ax3.scatter(golden_survival, golden_curiosity*100, c='gold', edgecolors='black', 
               s=60, marker='*', label='Golden Zone')
    ax3.axhline(y=10, color='red', linestyle='--', label='Curiosity > 10%')
    ax3.axvline(x=100, color='red', linestyle='--', label='Survival > 100')
    ax3.fill_between([100, max(survival_steps)*1.05], 10, max(curiosity_rates)*105, 
                    alpha=0.2, color='gold', label='Golden Zone')
    ax3.set_xlabel('Survival Steps', fontsize=12)
    ax3.set_ylabel('Curiosity Rate (%)', fontsize=12)
    ax3.set_title('Curiosity vs Survival\n(Golden Zone Shaded)')
    ax3.legend(loc='lower right', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'golden_zone_visualization.png'), dpi=150)
    plt.close()
    print("Saved: golden_zone_visualization.png")
    
    # Energy breakdown
    print(f"\n--- Golden Zone by Energy Level ---")
    for e in unique_energy:
        e_mask = golden_energy == e
        count = np.sum(e_mask)
        if count > 0:
            mean_curiosity = golden_curiosity[e_mask].mean() * 100
            mean_survival = golden_survival[e_mask].mean()
            print(f"Energy {int(e):2d}: {count:3d} configurations, Mean Curiosity: {mean_curiosity:.1f}%, Mean Survival: {mean_survival:.0f}")
else:
    print("No experiments meet the Golden Zone criteria!")

# =============================================================================
# 5. Additional Analysis: Parameter Impact
# =============================================================================
print("\n=== Parameter Impact Analysis ===")

# Analyze mean curiosity rate for each parameter value
fig_impact, axes_impact = plt.subplots(1, 3, figsize=(15, 5))

# Regrowth impact
regrowth_means = []
regrowth_stds = []
for r in unique_regrowth:
    mask = regrowth == r
    regrowth_means.append(curiosity_rates[mask].mean() * 100)
    regrowth_stds.append(curiosity_rates[mask].std() * 100)

axes_impact[0].errorbar(unique_regrowth, regrowth_means, yerr=regrowth_stds, 
                        fmt='o-', capsize=3, color='steelblue', ecolor='lightgray')
axes_impact[0].fill_between(unique_regrowth, 
                            np.array(regrowth_means) - np.array(regrowth_stds),
                            np.array(regrowth_means) + np.array(regrowth_stds),
                            alpha=0.2, color='steelblue')
axes_impact[0].set_xlabel('Regrowth Rate', fontsize=12)
axes_impact[0].set_ylabel('Mean Curiosity Rate (%)', fontsize=12)
axes_impact[0].set_title('Impact of Regrowth Rate\n(error bars = std dev)', fontsize=13)
axes_impact[0].grid(True, alpha=0.3)

# Density impact
density_means = []
density_stds = []
for d in unique_density:
    mask = density == d
    density_means.append(curiosity_rates[mask].mean() * 100)
    density_stds.append(curiosity_rates[mask].std() * 100)

axes_impact[1].errorbar(unique_density, density_means, yerr=density_stds, 
                        fmt='o-', capsize=3, color='forestgreen', ecolor='lightgray')
axes_impact[1].fill_between(unique_density, 
                            np.array(density_means) - np.array(density_stds),
                            np.array(density_means) + np.array(density_stds),
                            alpha=0.2, color='forestgreen')
axes_impact[1].set_xlabel('Density', fontsize=12)
axes_impact[1].set_ylabel('Mean Curiosity Rate (%)', fontsize=12)
axes_impact[1].set_title('Impact of Density\n(error bars = std dev)', fontsize=13)
axes_impact[1].grid(True, alpha=0.3)

# Energy impact
energy_means = []
energy_stds = []
for e in unique_energy:
    mask = energy == e
    energy_means.append(curiosity_rates[mask].mean() * 100)
    energy_stds.append(curiosity_rates[mask].std() * 100)

axes_impact[2].errorbar(unique_energy, energy_means, yerr=energy_stds, 
                        fmt='o-', capsize=3, color='coral', ecolor='lightgray')
axes_impact[2].fill_between(unique_energy, 
                            np.array(energy_means) - np.array(energy_stds),
                            np.array(energy_means) + np.array(energy_stds),
                            alpha=0.2, color='coral')
axes_impact[2].set_xlabel('Energy', fontsize=12)
axes_impact[2].set_ylabel('Mean Curiosity Rate (%)', fontsize=12)
axes_impact[2].set_title('Impact of Energy\n(error bars = std dev)', fontsize=13)
axes_impact[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'golden_zone_parameter_impact.png'), dpi=150)
plt.close()
print("Saved: golden_zone_parameter_impact.png")

print("\n=== Analysis Complete ===")
