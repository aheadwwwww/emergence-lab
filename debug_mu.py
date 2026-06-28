"""Debug Lenia with corrected parameters."""
import numpy as np

def lenia_kernel(R=13, mu_k=0.5, sigma_k=0.15):
    """Create Lenia kernel."""
    y, x = np.ogrid[-R:R+1, -R:R+1]
    dist = np.sqrt(x**2 + y**2) / R
    K = np.exp(-((dist - mu_k)**2) / (2 * sigma_k**2))
    K[dist > 1] = 0
    K = K / K.sum()
    return K

# Create grid and kernel
grid_size = 128
R = 13
K = lenia_kernel(R=R)

# Pad kernel
K_padded = np.zeros((grid_size, grid_size))
K_padded[:2*R+1, :2*R+1] = K
K_padded = np.roll(np.roll(K_padded, -R, axis=0), -R, axis=1)
K_fft = np.fft.fft2(K_padded)

# Initialize with pattern matching mu=0.3
np.random.seed(42)
cx, cy = grid_size // 2, grid_size // 2
y, x = np.ogrid[:grid_size, :grid_size]
r = np.sqrt((x - cx)**2 + (y - cy)**2)
A = 0.4 * np.exp(-r**2 / (2 * 20**2))

print("Initial state:")
print(f"  Mean: {np.mean(A):.4f}")
print(f"  Max: {np.max(A):.4f}")

# Test different mu values
for mu in [0.15, 0.2, 0.25, 0.3, 0.35, 0.4]:
    sigma = 0.05
    A_test = A.copy()
    
    # Run 50 steps
    for step in range(50):
        A_fft = np.fft.fft2(A_test)
        U = np.fft.ifft2(A_fft * K_fft).real
        G = 2 * np.exp(-((U - mu)**2) / (2 * sigma**2)) - 1
        A_test = np.clip(A_test + G, 0, 1)
    
    survival = np.mean(A_test > 0.1)
    complexity = np.var(A_test) + np.std(A_test)
    
    print(f"\nmu={mu:.2f}: Mean={np.mean(A_test):.4f}, Survival={survival*100:.1f}%, Complexity={complexity:.4f}")

print("\n--- Key insight ---")
print("When mu is too high, the growth function gives negative values for low U.")
print("This causes patterns to collapse.")
print("Solution: Use mu that matches initial activation level OR use smaller dt.")