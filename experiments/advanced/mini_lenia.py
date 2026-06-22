"""
Minimal Lenia — continuous CA from random noise
Core algorithm derived from Bert Chan's LeniaND
"""
import numpy as np
from PIL import Image
import os

W, H = 256, 256          # grid size
R = 18                   # kernel radius
T = 14                   # time steps per generation
DT = 1 / T
M = 0.14                 # growth center
S = 0.025                # growth width
STEPS = 400              # total iterations
SAVE_EVERY = 50          # save image every N steps
OUT = "C:\\Users\\许耀仁\\.openclaw\\workspace\\lenia_run"

os.makedirs(OUT, exist_ok=True)

# Growth function: Gaussian
def growth(U, m=M, s=S):
    return np.exp(-((U - m) ** 2) / (2 * s ** 2)) * 2 - 1

# Kernel: polynomial bump
def make_kernel(w, h, r):
    Y, X = np.ogrid[:h, :w]
    cx, cy = w // 2, h // 2
    dist = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2) / r
    kernel = (4 * dist * (1 - dist)) ** 4
    kernel[dist >= 1] = 0
    kernel /= kernel.sum()  # normalize
    return kernel

# Initialize
A = np.random.rand(H, W).astype(np.float64) * 0.2 + 0.05
kernel = make_kernel(W, H, R)

# FFT kernel (precompute)
K_FFT = np.fft.fft2(np.fft.ifftshift(kernel))

print(f"Grid: {W}x{H}, Kernel radius: {R}, Steps: {STEPS}")
print("Initial mass:", A.sum())

for step in range(STEPS):
    # Convolution via FFT
    U = np.real(np.fft.ifft2(np.fft.fft2(A) * K_FFT))
    U = np.clip(U, 0, 1)
    
    # Growth
    G = growth(U)
    
    # Euler step
    A_new = A + DT * G
    A_new = np.clip(A_new, 0, 1)
    A = A_new
    
    if step % SAVE_EVERY == 0 or step == STEPS - 1:
        img = (A * 255).astype(np.uint8)
        Image.fromarray(img, 'L').save(f"{OUT}\\step_{step:04d}.png")
        mass = A.sum()
        print(f"  Step {step:4d}: mass={mass:.1f}, max={A.max():.3f}")

# Collage
images = []
for step in range(0, STEPS, SAVE_EVERY):
    im = Image.open(f"{OUT}\\step_{step:04d}.png")
    images.append(im)
images.append(Image.open(f"{OUT}\\step_{STEPS-1:04d}.png"))

collage = Image.new('L', (256 * len(images), 256))
for i, im in enumerate(images):
    collage.paste(im, (i * 256, 0))
collage.save(f"{OUT}\\collage.png")
print(f"\nDone. {len(images)} frames saved, collage at {OUT}\\collage.png")
