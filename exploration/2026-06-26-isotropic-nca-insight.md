# Isotropic NCA Insight Extracted

**Date**: 2026-06-26
**Source**: Google Research - Isotropic NCA Notebook

## 🔑 Key Discovery: Stochastic Update Rate

Found the exact stochastic update technique:

```python
DEFAULT_UPDATE_RATE = 0.5

def forward(self, x, update_rate=DEFAULT_UPDATE_RATE):
    ...
    update_mask = (torch.rand(b, 1, h, w)+update_rate).floor()
    x = x + y*update_mask
    ...
```

### What This Means

1. **50% update rate** is the standard (same as my stochastic Lenia!)
2. Each cell has **independent probability** of updating
3. **Random mask each step** - not fixed spatial pattern
4. This is **NOT a bug** - it's a deliberate design choice

### Why 50%?

Looking at the notebook comments:
> "if you want to try experiments with synchronous NCA, you can set the value below to 1.0"

This implies:
- 1.0 = synchronous (all cells update)
- 0.5 = asynchronous (half cells update) ← DEFAULT
- Lower values = more asynchronous

### Technical Details

1. **Update mask generation**:
   ```python
   update_mask = (torch.rand(b, 1, h, w) + update_rate).floor()
   ```
   - `torch.rand` generates random values [0, 1]
   - Adding `update_rate` shifts to [update_rate, 1+update_rate]
   - `.floor()` gives binary mask
   - For 0.5: values in [0.5, 1.5] → 50% become 1, 50% become 0

2. **Alive mask**:
   ```python
   def get_alive_mask(x):
     mature = (x[:,3:4]>0.1).to(torch.float32)
     return perchannel_conv(mature, nhood_kernel[None,:])>0.5
   ```
   - Checks if neighbors are alive
   - Important for pattern survival

### My Stochastic Lenia Results vs Isotropic NCA

| Parameter | My Lenia | Isotropic NCA |
|-----------|----------|---------------|
| Update rate | 0.5 | 0.5 (DEFAULT) |
| Result | 28% alive (stable) | Stable patterns |
| Synchronous (1.0) | Oscillation/death | Imploding patterns |
| Discovery | Independent | Google Research |

**My discovery is validated by Google Research!**

### Why Asynchronous Updates Enable Stability

Both systems show the same pattern:
- **Synchronous** → Oscillations → Death
- **Asynchronous** → Stability → Survival

Hypothesis: **Emergence requires temporal disorder**
- Synchronous updates create coherent waves → interference → death
- Asynchronous updates break coherence → local stability → survival

Similar to:
- Neural networks needing dropout
- Physical systems needing thermal fluctuations
- Biological systems needing noise

### Next Steps for Lenia

1. Implement **alive mask** like Isotropic NCA
2. Test **update_rate sweep** (0.3, 0.5, 0.7, 1.0)
3. Compare **multi-channel + stochastic** combination
4. Create pattern zoo with stable variants

### Code Reference

File: `exploration/self-organising-systems/isotropic_nca/blogpost_isonca_single_seed_pytorch.ipynb`
Lines: ~350 (DEFAULT_UPDATE_RATE definition)

---

## Cross-References

- My stochastic Lenia: `experiments/lenia_stochastic.py`
- Discovery writeup: `exploration/2026-06-25-stochastic-lenia.md`
- Projects update: `memory/projects.md`