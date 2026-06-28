"""Test Orbium parameters directly to verify they work."""

import numpy as np
import jax.numpy as jnp
import sys
sys.path.insert(0, 'D:/openclaw_workspace/experiments')

from lenia_jax import make_orbium, _make_disk_kernel_np, run_lenia

# Test 1: Run with official Orbium parameters
print("=" * 60)
print("TEST 1: Official Orbium Parameters")
print("=" * 60)

# Orbium params from literature
R = 13
mu = 0.15
sigma = 0.014

# Create seed
grid = make_orbium((128, 128), R)
print(f"Seed mass: {float(grid.sum()):.2f}")

# Create kernel (bump4 = kn=1)
kernel = _make_disk_kernel_np(R, kn=1)
print(f"Kernel shape: {kernel.shape}")
print(f"Kernel sum: {kernel.sum():.6f}")
print(f"Kernel max: {kernel.max():.6f}")

# Run simulation
result = run_lenia(
    shape=(128, 128),
    R=R,
    mu=mu,
    sigma=sigma,
    kn=1,  # bump4
    gn=1,  # gaussian growth
    steps=200,
    init='orbium',
    verbose=True
)

print(f"\nFinal mass: {float(result['final'].sum()):.2f}")
print(f"Stats: {result['stats']}")

# Test 2: Try with different R values
print("\n" + "=" * 60)
print("TEST 2: Different R values with Orbium params")
print("=" * 60)

for R_test in [13, 15, 20]:
    result = run_lenia(
        shape=(128, 128),
        R=R_test,
        mu=0.15,
        sigma=0.014,
        kn=1,
        gn=1,
        steps=200,
        init='orbium',
        verbose=False
    )
    final_mass = float(result['final'].sum())
    alive = result['stats']['alive'] if result['stats'] else 0
    print(f"R={R_test:2d}: final_mass={final_mass:8.2f}, alive={alive:.4f}, state={result.get('state', 'unknown')}")

# Test 3: Try with growth function variations
print("\n" + "=" * 60)
print("TEST 3: Growth function variations")
print("=" * 60)

for gn_type in [0, 1, 2]:
    gn_names = ['quad4', 'gaus', 'step']
    result = run_lenia(
        shape=(128, 128),
        R=13,
        mu=0.15,
        sigma=0.014,
        kn=1,
        gn=gn_type,
        steps=200,
        init='orbium',
        verbose=False
    )
    final_mass = float(result['final'].sum())
    alive = result['stats']['alive'] if result['stats'] else 0
    print(f"gn={gn_type} ({gn_names[gn_type]:5s}): final_mass={final_mass:8.2f}, alive={alive:.4f}")

# Test 4: Try with kernel variations
print("\n" + "=" * 60)
print("TEST 4: Kernel type variations")
print("=" * 60)

for kn_type in [0, 1, 2]:
    kn_names = ['quad4', 'bump4', 'step']
    result = run_lenia(
        shape=(128, 128),
        R=13,
        mu=0.15,
        sigma=0.014,
        kn=kn_type,
        gn=1,
        steps=200,
        init='orbium',
        verbose=False
    )
    final_mass = float(result['final'].sum())
    alive = result['stats']['alive'] if result['stats'] else 0
    print(f"kn={kn_type} ({kn_names[kn_type]:5s}): final_mass={final_mass:8.2f}, alive={alive:.4f}")
