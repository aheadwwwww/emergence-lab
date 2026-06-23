"""Test all 10 orchestrator experiments, focusing on newly added ones."""
from registry import REGISTRY, OUTPUT_DIR
import os, time

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Test Phase Transitions
print('=== Testing PhaseTransitions ===')
pt = REGISTRY['phase_transitions']
params = pt.generate_params()
print(f'Params: {params}')
t0 = time.time()
result = pt.run(params)
t = time.time() - t0
print(f'Done in {t:.2f}s: mag={result["magnetization"]:.3f}, phase={result["phase"]}')
img = pt.visualize(result)
img.save(str(OUTPUT_DIR / 'test_phaseTransitions.png'))
print('OK - image saved')

# Test Lenia
print()
print('=== Testing Lenia ===')
lenia = REGISTRY['lenia']
params = lenia.generate_params()
print(f'Params: {params}')
t0 = time.time()
result = lenia.run(params)
t = time.time() - t0
print(f'Done in {t:.2f}s: state shape {result["state"].shape}')
img = lenia.visualize(result)
img.save(str(OUTPUT_DIR / 'test_lenia.png'))
print('OK - image saved')

# Quick test all 10
print()
print('=== Quick test all 10 experiments ===')
for name, exp in REGISTRY.items():
    try:
        params = exp.generate_params()
        t0 = time.time()
        result = exp.run(params)
        t = time.time() - t0
        img = exp.visualize(result)
        img.save(str(OUTPUT_DIR / f'test_{name}.png'))
        print(f'  [{t:6.3f}s] {name}: {exp.describe(params, result)}')
    except Exception as e:
        import traceback
        print(f'  [FAIL] {name}: {e}')
        traceback.print_exc()

print()
print('All tests complete. Images in:', OUTPUT_DIR)
