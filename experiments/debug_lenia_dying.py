"""Debug why patterns are dying even with good parameters."""

import numpy as np
import jax.numpy as jnp
import sys
sys.path.insert(0, 'D:/openclaw_workspace/experiments')

from lenia_jax import run_lenia, load_seed, make_kernel_fft

# Load the real Orbium seed
seed = np.load('D:/openclaw_workspace/experiments/lenia_seed_O2u.npy')
print(f"Orbium seed: shape={seed.shape}, mass={seed.sum():.2f}")

# Test 1: Use the exact best parameters from param search v2
print("\n" + "=" * 60)
print("TEST 1: Best params from search (R=10, mu=0.1622, sigma=0.0257)")
print("=" * 60)

result = run_lenia(
    shape=(128, 128),
    R=10,
    mu=0.1622,
    sigma=0.0257,
    kn=1,  # bump4
    gn=1,  # gaussian
    steps=300,
    init='seed',
    seed_path='D:/openclaw_workspace/experiments/lenia_seed_O2u.npy',
    verbose=True
)
print(f"State: {result['state']}, Stats: {result['stats']}")

# Test 2: Try with quad4 kernel instead
print("\n" + "=" * 60)
print("TEST 2: quad4 kernel (kn=0)")
print("=" * 60)

result = run_lenia(
    shape=(128, 128),
    R=10,
    mu=0.1622,
    sigma=0.0257,
    kn=0,  # quad4
    gn=1,
    steps=300,
    init='seed',
    seed_path='D:/openclaw_workspace/experiments/lenia_seed_O2u.npy',
    verbose=True
)
print(f"State: {result['state']}, Stats: {result['stats']}")

# Test 3: Try with R=13 (Orbium's R)
print("\n" + "=" * 60)
print("TEST 3: R=13 (Orbium's radius)")
print("=" * 60)

result = run_lenia(
    shape=(128, 128),
    R=13,
    mu=0.1622,
    sigma=0.0257,
    kn=1,
    gn=1,
    steps=300,
    init='seed',
    seed_path='D:/openclaw_workspace/experiments/lenia_seed_O2u.npy',
    verbose=True
)
print(f"State: {result['state']}, Stats: {result['stats']}")

# Test 4: Try with larger R and adjusted params
print("\n" + "=" * 60)
print("TEST 4: R=20 with wider sigma")
print("=" * 60)

result = run_lenia(
    shape=(128, 128),
    R=20,
    mu=0.15,
    sigma=0.03,
    kn=1,
    gn=1,
    steps=300,
    init='seed',
    seed_path='D:/openclaw_workspace/experiments/lenia_seed_O2u.npy',
    verbose=True
)
print(f"State: {result['state']}, Stats: {result['stats']}")

# Test 5: Random seed with best params
print("\n" + "=" * 60)
print("TEST 5: Random seed with best params")
print("=" * 60)

result = run_lenia(
    shape=(128, 128),
    R=10,
    mu=0.1622,
    sigma=0.0257,
    kn=1,
    gn=1,
    steps=300,
    init='random',
    verbose=True
)
print(f"State: {result['state']}, Stats: {result['stats']}")

# Test 6: Check if the seed is being loaded correctly
print("\n" + "=" * 60)
print("TEST 6: Check seed loading")
print("=" * 60)

from pathlib import Path
seed_path = Path('D:/openclaw_workspace/experiments/lenia_seed_O2u.npy')
grid = load_seed(str(seed_path), (128, 128), 10)
print(f"Loaded grid shape: {grid.shape}")
print(f"Loaded grid mass: {grid.sum():.2f}")
print(f"Non-zero cells: {(grid > 0).sum()}")
print(f"Max value: {grid.max():.4f}")
