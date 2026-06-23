# Equinox Exploration Note

**Date**: 2026-06-23
**Repository**: https://github.com/patrick-kidger/equinox

## What is Equinox?

Equinox is a neural network library for JAX with PyTorch-like syntax. It's not a framework - everything is compatible with the JAX ecosystem.

## Key Features

1. **PyTorch-like Model Definition**: Simple class-based syntax
2. **PyTree Integration**: Models are just PyTrees, work seamlessly with JAX transformations
3. **No Magic**: Transparent - `eqx.Module` just registers your class as a PyTree
4. **Advanced Features**: Runtime errors, filtered APIs, PyTree manipulation

## Why Interesting for Our Work?

- Could be used for neural network experiments in the emergence orchestrator
- Clean API for defining models
- Good for scientific computing (integrates with Diffrax, Optimistix, etc.)

## Quick Example

```python
import equinox as eqx
import jax

class Linear(eqx.Module):
    weight: jax.Array
    bias: jax.Array

    def __init__(self, in_size, out_size, key):
        wkey, bkey = jax.random.split(key)
        self.weight = jax.random.normal(wkey, (out_size, in_size))
        self.bias = jax.random.normal(bkey, (out_size,))

    def __call__(self, x):
        return self.weight @ x + self.bias
```

## Next Steps

- Try building a simple neural cellular automata with Equinox
- Explore integration with emergence experiments
- Check Diffrax for differential equation solvers

## Related Libraries

- **Diffrax**: Differential equation solvers
- **Optimistix**: Optimization
- **Lineax**: Linear solvers
- **BlackJAX**: Bayesian sampling
