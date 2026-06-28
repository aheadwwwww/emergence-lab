# Lenia V10 - JAX-MD Inspired Differentiable Simulation

**Date**: 2026-06-28 22:35
**Status**: Prototype complete, optimization shows flat gradient landscape

---

## Concept

Apply JAX-MD's differentiable simulation approach to Lenia:
- End-to-end gradients through simulation
- Autodiff to optimize emergence metrics
- Bridge between V7 (evolutionary) and V9 (learnable GNN)

## Implementation

**File**: `experiments/lenia_v10_jax_md_prototype.py`

Key components:
1. **Pre-computed kernel template** - Fixed distance matrix R
2. **Differentiable kernel creation** - JAX ops for Gaussian
3. **JIT-compiled simulation** - lax.scan for efficiency
4. **Gradient descent** - optax Adam optimizer

## Results

**Initial Test** (100 iterations, 50 sim steps):
- Emergence: 0.2632 (constant)
- Parameters: No change from initial
- **Finding**: Gradient is zero at Orbium-like parameters

## Interpretation

The flat gradient landscape suggests:

1. **Local optimum**: Orbium parameters may be at a local optimum
2. **Vanishing gradients**: Long simulation chain causes gradient decay
3. **Discontinuous dynamics**: Lenia state transitions may not be smooth
4. **Metric sensitivity**: Emergence metrics may not capture local improvements

## Comparison with Prior Methods

| Method | Gradient Type | Convergence | Best Emergence |
|--------|---------------|-------------|----------------|
| V7 (Evolutionary) | Indirect (population) | Slow but global | ~1.0 |
| V9 (Learnable GNN) | Local (attention) | Medium | 1.985 |
| V10 (JAX-MD) | Direct (autodiff) | Flat landscape | 0.263 |

## Next Steps

1. **Gradient analysis**: Check gradient magnitudes at each step
2. **Different seed patterns**: Test away from Orbium
3. **Shorter simulations**: Reduce gradient decay
4. **Alternative metrics**: Use smoother loss functions
5. **Hybrid approach**: Combine V7 (global search) + V10 (local refinement)

## Technical Lessons

### JAX JIT Compilation Challenges

1. **Static arguments**: Cannot pass numpy arrays as static
2. **Concrete values**: jnp.arange needs concrete bounds
3. **Tracer conflicts**: Mixing numpy and JAX ops causes errors

### Solution Pattern

```python
# Pre-compute template with numpy
r_template_np = create_kernel_template(R)
r_template = jax.device_put(r_template_np)

# Use JAX ops in loss function
kernel = jnp.exp(-((r_template - mu)**2) / (2 * sigma**2))
```

## Reference

- JAX-MD: https://github.com/jax-md/jax-md
- Schoenholz & Cubuk, "JAX M.D. A Framework for Differentiable Physics"
- Optax: https://github.com/google-deepmind/optax

---

**Conclusion**: V10 demonstrates the feasibility of end-to-end differentiable Lenia, but reveals that naive gradient descent struggles with the complex emergence landscape. Future work should focus on hybrid approaches combining global evolutionary search with local gradient refinement.
