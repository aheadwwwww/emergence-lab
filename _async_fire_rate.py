"""测试不同 fire_rate 对 Lenia 的影响"""
import json
import sys
sys.path.insert(0, 'experiments')
from lenia_async import run_async_lenia

results = []
for fire_rate in [0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0]:
    result = run_async_lenia(
        shape=(256, 256),
        R=20,
        mu=0.14,
        sigma=0.024,
        fire_rate=fire_rate,
        steps=200,
        record_every=200,
    )
    entry = {
        'fire_rate': fire_rate,
        'state': result['state'],
        **result['stats'],
    }
    results.append(entry)
    print(f"fire_rate={fire_rate:.2f} → {result['state']} | alive={result['stats']['alive']:.3f}")

# Save
with open('experiments/lenia_async_fire_rate_sweep.json', 'w') as f:
    json.dump(results, f, indent=2)

# Summary
from collections import Counter
states = Counter(r['state'] for r in results)
print(f"\nSummary: {dict(states)}")
print(f"Best alive: {max(results, key=lambda x: x['alive'])['fire_rate']}")