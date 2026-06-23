"""Test the PhaseTransitions fix."""
from registry import REGISTRY, OUTPUT_DIR
import os
os.makedirs(str(OUTPUT_DIR), exist_ok=True)

pt = REGISTRY['phase_transitions']
params = pt.generate_params()
result = pt.run(params)
desc = pt.describe(params, result)
print(f'Describe output: {repr(desc)}')
print(f'Phase: {result["phase"]}, Mag: {result["magnetization"]:.3f}')
img = pt.visualize(result)
img.save(str(OUTPUT_DIR / 'test_pt_fixed.png'))
print('OK - fix works!')
