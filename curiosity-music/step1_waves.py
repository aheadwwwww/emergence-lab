"""
#027 - Music: Wave Physics (from zero)

Exploring: why do some sounds feel "right" together?
Tools: NumPy + Pillow. Bad toolkit for this. Good.

Start at wave physics. See where it goes.
"""

import numpy as np
from PIL import Image, ImageDraw
import os

OUT = r"C:\Users\许耀仁\.openclaw\workspace\curiosity-music"
os.makedirs(OUT, exist_ok=True)


def plot_wave_mix(f1, f2, duration=0.01, label=""):
    """Plot the superposition of two sine waves."""
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration))
    w1 = np.sin(2 * np.pi * f1 * t)
    w2 = np.sin(2 * np.pi * f2 * t)
    mix = w1 + w2
    mix = mix / np.max(np.abs(mix)) * 0.9

    img = Image.new("RGB", (800, 300), "white")
    draw = ImageDraw.Draw(img)
    for i in range(0, 800, 50):
        draw.line([i, 0, i, 300], fill=(240, 240, 240))
    draw.line([0, 150, 800, 150], fill=(220, 220, 220))

    n = len(t)
    pts = []
    step = max(1, n // 800)
    for i in range(0, n, step):
        x = int(i / n * 800)
        y = int(150 - mix[i] * 130)
        pts.append((x, y))
    if len(pts) > 1:
        draw.line(pts, fill="black", width=1)

    ratio = f"{f1/f2:.4f}" if f1 <= f2 else f"{f2/f1:.4f}"
    draw.text((10, 10), f"f1={f1}Hz  f2={f2}Hz  ratio={ratio}  {label}", fill="black")
    return img


results = []

# Pure tone (baseline)
img0 = plot_wave_mix(440, 440, 0.005, "[Unison 1:1]")
img0.save(f"{OUT}\\01_unison.png")
results.append(("Unison (1:1)", "pure single tone"))

# Octave 2:1
img1 = plot_wave_mix(440, 880, 0.005, "[Octave 2:1]")
img1.save(f"{OUT}\\02_octave.png")
results.append(("Octave (2:1)", "waves align perfectly"))

# Perfect Fifth 3:2
img2 = plot_wave_mix(440, 660, 0.005, "[Perfect Fifth 3:2]")
img2.save(f"{OUT}\\03_fifth.png")
results.append(("Perfect Fifth (3:2)", "most consonant after unison/octave"))

# Perfect Fourth 4:3
img3 = plot_wave_mix(440, 586.67, 0.005, "[Perfect Fourth 4:3]")
img3.save(f"{OUT}\\04_fourth.png")
results.append(("Perfect Fourth (4:3)", "consonant, pattern slightly more complex"))

# Major Third 5:4
img4 = plot_wave_mix(440, 550, 0.005, "[Major Third 5:4]")
img4.save(f"{OUT}\\05_major_third.png")
results.append(("Major Third (5:4)", "waveform starts to show richer structure"))

# Minor Third 6:5
img5 = plot_wave_mix(440, 528, 0.005, "[Minor Third 6:5]")
img5.save(f"{OUT}\\06_minor_third.png")
results.append(("Minor Third (6:5)", "minor third, slightly less 'stable' feel"))

# Tritone ~45:32
img6 = plot_wave_mix(440, 622.25, 0.005, "[Tritone ~45:32]")
img6.save(f"{OUT}\\07_tritone.png")
results.append(("Tritone (~45:32)", "historically 'diabolus in musica', most dissonant"))

# Semitone 16:15
img7 = plot_wave_mix(440, 466.16, 0.005, "[Semitone 16:15]")
img7.save(f"{OUT}\\08_semitone.png")
results.append(("Semitone (16:15)", "close frequencies, clear beating"))


# --- 3. Dissonance scan ---
def roughness(f1, f2, duration=0.05):
    """Calculate roughness: variance of amplitude envelope.
    Simple ratios -> regular envelope -> lower variance
    Complex ratios -> irregular beating -> higher variance"""
    sr = 44100
    n = int(sr * duration)
    t = np.linspace(0, duration, n)
    mix = np.sin(2 * np.pi * f1 * t) + np.sin(2 * np.pi * f2 * t)
    env = np.abs(mix)
    window = np.ones(50) / 50
    env_smooth = np.convolve(env, window, mode="valid")
    return np.var(env_smooth)


base_freq = 440
ratios = np.linspace(1.0, 2.0, 200)
roughness_vals = np.array([roughness(base_freq, base_freq * r) for r in ratios])
rv_max = roughness_vals.max()
if rv_max > 0:
    roughness_vals = roughness_vals / rv_max

w, h = 800, 400
scan_img = Image.new("RGB", (w, h + 40), "white")
draw_scan = ImageDraw.Draw(scan_img)

draw_scan.rectangle([50, 20, w - 20, h - 20], outline="gray")
draw_scan.text((10, 5), "Dissonance Curve: Frequency Ratio 1:1 to 2:1", fill="black")
draw_scan.text((10, h + 10), "Higher = more roughness / dissonance", fill="gray")

important_ratios = [
    (1.0, "1:1"), (16/15, "16:15"), (6/5, "6:5"), (5/4, "5:4"),
    (4/3, "4:3"), (45/32, "~45:32"), (3/2, "3:2"), (2.0, "2:1"),
]
for rat, label in important_ratios:
    x = 50 + int((rat - 1.0) / 1.0 * (w - 70))
    y_idx = np.argmin(np.abs(ratios - rat))
    rv_at = roughness_vals[y_idx]
    y = h - 20 - int(rv_at * (h - 40))
    draw_scan.line([x, 20, x, h - 20], fill=(200, 200, 255), width=1)
    draw_scan.text((x - 10, 2), label, fill="blue")

pts = []
for i, rv in enumerate(roughness_vals):
    x = 50 + int(i / len(ratios) * (w - 70))
    y = h - 20 - int(rv * (h - 40))
    pts.append((x, y))
draw_scan.line(pts, fill="black", width=2)

draw_scan.text((50, h - 12), "Consonant <-", fill="gray")
draw_scan.text((w - 130, h - 12), "-> Dissonant", fill="gray")

scan_img.save(f"{OUT}\\09_roughness_scan.png")
results.append(("Roughness Scan", "full scan 1:1 to 2:1 with important ratios marked"))

print("=== #027 Step 1: Wave Physics ===")
print()
for name, desc in results:
    print(f"  {name}")
    print(f"    {desc}")
    print()

print("Images saved to", OUT)
print()
print("First impressions:")
print("- Simple frequency ratios DO produce cleaner waveforms")
print("- But 'pleasant' and 'clean waveform' are not the same thing")
print("- Major third (5:4) already has complex waveform, yet ear finds it consonant")
print("- This tells me: consonance judgment is NOT purely acoustic")
print("- Some higher-level pattern recognition is involved")
print()
print("Haven't yet found anything related to emergence.")
print("This is still just physics. Next direction uncertain.")
print()
