"""
Debug Lenia kernel and growth function to find working parameters
"""
import numpy as np

# Test kernel
R = 13
xs = np.linspace(-R, R, 2 * R + 1)
ys = np.linspace(-R, R, 2 * R + 1)
X, Y = np.meshgrid(xs, ys)
D = np.sqrt(X**2 + Y**2)
r = D / R

# Kernel
kernel = np.zeros_like(D)
mask = (r > 0) & (r < 1)
alpha = 4.0
kernel[mask] = np.exp(alpha - alpha / (4 * r[mask] * (1 - r[mask])))
kernel = kernel / kernel.sum()

print(f"Kernel shape: {kernel.shape}")
print(f"Kernel sum: {kernel.sum():.6f}")
print(f"Kernel max: {kernel.max():.6f} at r={r[kernel == kernel.max()][0]:.3f}")
print(f"Kernel non-zero: {(kernel > 0).sum()} cells")
print()

# Test with a single active cell
test_world = np.zeros((200, 200))
test_world[100, 100] = 0.8

from scipy.ndimage import convolve
U = convolve(test_world, kernel, mode='wrap')
print(f"Single cell (0.8): U max={U.max():.6f}, U at center={U[100,100]:.6f}")

# Test with cell-like blobs
test_world2 = np.zeros((200, 200))
xs2 = np.arange(200)
ys2 = np.arange(200)
X2, Y2 = np.meshgrid(xs2, ys2)
for cy in range(20, 200, 30):
    for cx in range(20, 200, 30):
        D2 = np.sqrt((X2 - cx)**2 + (Y2 - cy)**2)
        test_world2 += 0.8 * np.exp(-D2**2 / 30)
test_world2 = np.clip(test_world2, 0, 1)

U2 = convolve(test_world2, kernel, mode='wrap')
print(f"\nCell blobs: U mean={U2.mean():.6f}, U max={U2.max():.6f}, U min={U2.min():.6f}")
print(f"U histogram (10 bins):")
hist, edges = np.histogram(U2.flatten(), bins=10)
for i, (h, lo, hi) in enumerate(zip(hist, edges[:-1], edges[1:])):
    print(f"  [{lo:.4f}, {hi:.4f}): {h}")

# Growth function
mu = 0.15
sigma = 0.022
def G(u):
    return 2 * np.exp(-(u - mu)**2 / (2 * sigma**2)) - 1

# Test growth function at key U values
test_us = np.linspace(0, 0.3, 31)
print(f"\nGrowth function G(u) with mu={mu}, sigma={sigma}:")
for u in test_us:
    g = G(u)
    marker = " <-- SWEET SPOT" if g > 0 else ""
    print(f"  u={u:.3f}: G={g:+.4f}{marker}")

# Find where G > 0
print(f"\nG > 0 when u in [{mu - sigma*np.sqrt(2*np.log(2)):.4f}, {mu + sigma*np.sqrt(2*np.log(2)):.4f}]")
