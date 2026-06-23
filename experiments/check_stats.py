import json
import numpy as np

data = json.load(open('D:/openclaw_workspace/experiments/results/golden_zone_data_20260623_210136.json'))
curiosity = np.array(data['curiosity_rates'])
survival = np.array(data['survival_steps'])
params = data['params']

print('Curiosity rate stats:')
print(f'  Max: {curiosity.max()*100:.1f}%')
print(f'  Mean: {curiosity.mean()*100:.1f}%')
print(f'  >5%: {np.sum(curiosity>0.05)} configs')
print(f'  >10%: {np.sum(curiosity>0.10)} configs')

print('Survival stats:')
print(f'  Max: {survival.max()}')
print(f'  Mean: {survival.mean():.1f}')
print(f'  >50: {np.sum(survival>50)} configs')
print(f'  >100: {np.sum(survival>100)} configs')
print(f'  >200: {np.sum(survival>200)} configs')

print('\nBest configs by curiosity rate:')
sorted_idx = np.argsort(curiosity)[::-1][:10]
for i in sorted_idx:
    print(f'  r={params[i]["regrowth"]:.4f}, d={params[i]["density"]:.4f}, e={params[i]["energy"]}, curiosity={curiosity[i]*100:.1f}%, survival={survival[i]}')

print('\nBest configs by survival:')
sorted_idx_s = np.argsort(survival)[::-1][:10]
for i in sorted_idx_s:
    print(f'  r={params[i]["regrowth"]:.4f}, d={params[i]["density"]:.4f}, e={params[i]["energy"]}, curiosity={curiosity[i]*100:.1f}%, survival={survival[i]}')

# Relaxed golden zone
print('\n--- Relaxed Golden Zone (Curiosity > 5% AND Survival > 50) ---')
relaxed_mask = (curiosity > 0.05) & (survival > 50)
relaxed_count = np.sum(relaxed_mask)
print(f'Found: {relaxed_count} configs')
if relaxed_count > 0:
    relaxed_params = np.array([(params[i]["regrowth"], params[i]["density"], params[i]["energy"]) for i in range(len(params)) if relaxed_mask[i]])
    relaxed_curiosity = curiosity[relaxed_mask]
    relaxed_survival = survival[relaxed_mask]
    print(f'Regrowth range: {relaxed_params[:,0].min():.4f} - {relaxed_params[:,0].max():.4f}')
    print(f'Density range: {relaxed_params[:,1].min():.4f} - {relaxed_params[:,1].max():.4f}')
    print(f'Energy range: {relaxed_params[:,2].min():.0f} - {relaxed_params[:,2].max():.0f}')

# Near golden zone
print('\n--- Near Golden Zone (Curiosity > 5% OR Survival > 100) ---')
near_mask = (curiosity > 0.05) | (survival > 100)
near_count = np.sum(near_mask)
print(f'Found: {near_count} configs')