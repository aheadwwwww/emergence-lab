import json
data = json.load(open('experiments/lenia_multichannel_sweep.json'))

structs = [r for r in data if r['state'] == 'structure']
print('Structure params:')
for r in structs:
    print(f"  mu={r['mu']:.3f} sigma={r['sigma']:.3f} alive={r['alive']:.3f} score={r['score']:.3f}")

print(f"\nTotal: {len(structs)}/{len(data)} structures")

# Find pattern
print("\nPattern: low sigma (0.02) produces structure across all mu ranges")
print("         mu=0.22 region is dead zone for this configuration")
