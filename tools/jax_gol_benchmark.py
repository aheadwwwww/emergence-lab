"""
JAX-accelerated Game of Life — Benchmark vs NumPy
Phase 2: Acceleration — port key emergence experiments to JAX

Compare pure NumPy vs JAX (JIT + vmap) for Conway's Game of Life
"""

import numpy as np
import jax
import jax.numpy as jnp
import time
import sys

# ─── NumPy implementation ───────────────────────────────────────────

def gol_step_numpy(grid):
    """One step of Game of Life using NumPy (rolled convolutions)."""
    neighbors = (
        np.roll(grid, 1, axis=0) + np.roll(grid, -1, axis=0) +
        np.roll(grid, 1, axis=1) + np.roll(grid, -1, axis=1) +
        np.roll(np.roll(grid, 1, axis=0), 1, axis=1) +
        np.roll(np.roll(grid, 1, axis=0), -1, axis=1) +
        np.roll(np.roll(grid, -1, axis=0), 1, axis=1) +
        np.roll(np.roll(grid, -1, axis=0), -1, axis=1)
    )
    return (neighbors == 3) | ((grid == 1) & (neighbors == 2))

def simulate_numpy(initial, steps):
    grid = initial.copy()
    for _ in range(steps):
        grid = gol_step_numpy(grid)
    return grid


# ─── JAX implementation ─────────────────────────────────────────────

def gol_step_jax(grid):
    """One step of Game of Life using JAX (JIT-compilable roll)."""
    neighbors = (
        jnp.roll(grid, 1, axis=0) + jnp.roll(grid, -1, axis=0) +
        jnp.roll(grid, 1, axis=1) + jnp.roll(grid, -1, axis=1) +
        jnp.roll(jnp.roll(grid, 1, axis=0), 1, axis=1) +
        jnp.roll(jnp.roll(grid, 1, axis=0), -1, axis=1) +
        jnp.roll(jnp.roll(grid, -1, axis=0), 1, axis=1) +
        jnp.roll(jnp.roll(grid, -1, axis=0), -1, axis=1)
    )
    return (neighbors == 3) | ((grid == 1) & (neighbors == 2))

def simulate_jax_scan(grid, steps):
    """Use jax.lax.fori_loop for fully JIT-compiled multi-step simulation."""
    def step_fn(i, g):
        return gol_step_jax(g).astype(jnp.int32)
    return jax.lax.fori_loop(0, steps, step_fn, grid)

# Also a version that runs step-by-step (like numpy) for fair comparison
def simulate_jax_loop(initial, steps):
    grid = jnp.array(initial)
    for _ in range(steps):
        grid = gol_step_jax(grid)
    return grid

# Warm-up JIT
_ = jax.jit(simulate_jax_scan)(jnp.zeros((32, 32), dtype=jnp.int32), 5).block_until_ready()


# ─── Benchmark ──────────────────────────────────────────────────────

def make_glider_gun(size):
    """Gosper glider gun in a size×size grid."""
    grid = np.zeros((size, size), dtype=np.int32)
    gun = [
        (5, 1), (5, 2), (6, 1), (6, 2),
        (3, 35), (3, 36), (4, 34), (4, 37), (5, 34), (5, 37),
        (6, 34), (6, 37), (7, 35), (7, 36), (8, 34), (8, 35), (8, 36), (8, 37),
        (7, 1), (7, 2), (8, 1), (8, 2),
        (3, 13), (3, 14), (4, 12), (4, 16), (5, 11), (5, 17),
        (6, 11), (6, 15), (6, 17), (6, 18),
        (7, 11), (7, 17), (8, 12), (8, 16), (9, 13), (9, 14),
        (1, 25), (2, 23), (2, 25), (3, 21), (3, 22), (4, 21), (4, 22),
        (5, 21), (5, 22), (6, 23), (6, 25), (7, 25),
    ]
    for r, c in gun:
        if 0 <= r < size and 0 <= c < size:
            grid[r, c] = 1
    return grid


def run_benchmark(sizes, steps, trials=3):
    print(f"{'Size':>10} {'Steps':>8} {'NumPy (s)':>12} {'JAX-loop (s)':>14} {'JAX-scan (s)':>14} {'Scan/np':>10} {'Grids/s':>10}")
    print("-" * 80)
    
    for size in sizes:
        glider = make_glider_gun(size)
        jax_glider = jnp.array(glider)
        
        # NumPy
        np_times = []
        for _ in range(trials):
            t0 = time.perf_counter()
            simulate_numpy(glider, steps)
            np_times.append(time.perf_counter() - t0)
        np_time = min(np_times)
        
        # JAX loop (step-by-step)
        jax_loop_times = []
        for _ in range(trials):
            t0 = time.perf_counter()
            _ = simulate_jax_loop(jax_glider, steps).block_until_ready()
            jax_loop_times.append(time.perf_counter() - t0)
        jax_loop_time = min(jax_loop_times)
        
        # JAX scan (fully compiled via fori_loop)
        simulate_jax_scan_jit = jax.jit(simulate_jax_scan, static_argnums=(1,))
        jax_scan_times = []
        for _ in range(trials):
            t0 = time.perf_counter()
            _ = simulate_jax_scan_jit(jax_glider, steps).block_until_ready()
            jax_scan_times.append(time.perf_counter() - t0)
        jax_scan_time = min(jax_scan_times)
        
        scan_speedup = np_time / jax_scan_time if jax_scan_time > 0 else float('inf')
        grids_per_sec = (size * size) / jax_scan_time if jax_scan_time > 0 else float('inf')
        
        print(f"{size:>10} {steps:>8} {np_time:>12.4f} {jax_loop_time:>14.4f} {jax_scan_time:>14.4f} {scan_speedup:>9.2f}x {grids_per_sec:>10.1f}")


if __name__ == "__main__":
    print("=" * 80)
    print("Game of Life: NumPy vs JAX Benchmark")
    print(f"JAX version: {jax.__version__}")
    print(f"Devices: {jax.devices()}")
    print("=" * 80)
    print()
    
    # Warm-up
    _ = jax.jit(simulate_jax_scan)(jnp.zeros((256, 256), dtype=jnp.int32), 50).block_until_ready()
    
    # Benchmark
    run_benchmark([64, 128, 256, 512, 1024], steps=200, trials=3)
    
    print()
    print("All benchmarks complete.")
