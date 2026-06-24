# JAX Acceleration — Game of Life Benchmark

**日期**: 2026-06-24
**状态**: Phase 2 — 加速关键涌现实验

## 背景

好奇心地图 26/26 节点完成 → 进入 Phase 2：用 JAX 加速涌现实验，实现更大规模参数扫描。

## 基准测试

### 方法

- **实现**: Conway's Game of Life (Gosper Glider Gun)
- **对比**: Pure NumPy vs JAX (`jax.lax.fori_loop` JIT-compiled)
- **环境**: CPU only (JAX v0.10.2, no GPU)

### 结果

| Grid Size | Steps | NumPy (s) | JAX (s) | Speedup |
|-----------|-------|-----------|---------|---------|
| 64×64     | 200   | 0.0186    | 0.0015  | **12.11x** |
| 128×128   | 200   | 0.0243    | 0.0074  | **3.31x** |
| 256×256   | 200   | 0.0502    | 0.0371  | 1.35x |
| 512×512   | 200   | 0.2052    | 0.3074  | 0.67x* |
| 1024×1024 | 200   | 2.3779    | 2.0464  | 1.16x |

*JAX loop-step on CPU slower due to Python overhead; JIT scan recovers

### 洞察

1. **小网格 (≤128)**: JAX 优势显著 (3-12x) — 编译开销被多次迭代摊薄
2. **中网格 (256)**: 平手 — NumPy 的 BLAS 在 CPU 上表现优秀
3. **大网格 (512+)**: JAX 略慢 — XLA CPU 后端对 roll 操作的优化不如预期
4. **结论**: 对 CPU-only 环境，JAX 对小规模涌现实验有用；大规模需 GPU

## 下一步

- [ ] 尝试 GPU 加速（如果可用）
- [ ] 用 JAX 重写 Lenia（连续 CA，更受益于 JIT）
- [ ] 用 JAX 重写 Embodiment 实验（多 agent 并行模拟）
- [ ] 探索其他加速方案：PyPy, Cython, Numba

## 代码

- `tools/jax_gol_benchmark.py` — 基准测试脚本

## 关联

- #001 Emergence — GoL 是最基础的涌现演示
- #012 Scaling Laws — 加速后可以跑更大规模的 scaling 实验
