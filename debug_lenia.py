"""Debug Lenia dynamics."""
import numpy as np

def lenia_kernel(R=13):
    """Create Lenia kernel."""
    size = 2 * R + 1
    y, x = np.ogrid[-R:R+1, -R:R+1]
    dist = np.sqrt(x**2 + y**2) / R
    K = np.exp(-((dist - 0.5)**2) / (2 * 0.15**2))
    K[dist > 1] = 0
    K = K / K.sum()
    return K

def lenia_step(A, K_fft, mu=0.15, sigma=0.014, dt=1.0):
    """Lenia step."""
    A_fft = np.fft.fft2(A)
    U = np.fft.ifft2(A_fft * K_fft).real
    G = 2 * np.exp(-((U - mu)**2) / (2 * sigma**2)) - 1
    A_new = A + dt * G
    A_new = np.clip(A_new, 0, 1)
    return A_new, U, G

# Create grid and kernel
grid_size = 128
R = 13
K = lenia_kernel(R=R)
K_padded = np.zeros((grid_size, grid_size))
K_padded[:2*R+1, :2*R+1] = K
K_padded = np.roll(np.roll(K_padded, -R, axis=0), -R, axis=1)
K_fft = np.fft.fft2(K_padded)

# Initialize
np.random.seed(42)
A = np.zeros((grid_size, grid_size))
cx, cy = grid_size // 2, grid_size // 2
y, x = np.ogrid[:grid_size, :grid_size]
r = np.sqrt((x - cx)**2 + (y - cy)**2)
A = np.exp(-r**2 / (2 * 15**2))

print("Initial state:")
print(f"  Mean: {np.mean(A):.4f}")
print(f"  Std: {np.std(A):.4f}")
print(f"  Min: {np.min(A):.4f}")
print(f"  Max: {np.max(A):.4f}")

# Run 10 steps
mu = 0.15
sigma = 0.014
dt = 1.0

for step in range(10):
    A_new, U, G = lenia_step(A, K_fft, mu, sigma, dt)
    A = A_new
    
    print(f"\nStep {step+1}:")
    print(f"  U (convolution result): mean={np.mean(U):.4f}, std={np.std(U):.4f}")
    print(f"  G (growth): mean={np.mean(G):.4f}, std={np.std(G):.4f}, min={np.min(G):.4f}, max={np.max(G):.4f}")
    print(f"  A (state): mean={np.mean(A):.4f}, std={np.std(A):.4f}, min={np.min(A):.4f}, max={np.max(A):.4f}")
    print(f"  Active (>0.1): {np.mean(A > 0.1)*100:.1f}%")