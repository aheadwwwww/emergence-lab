"""
#027 Step 2: Harmonic Series and the Emergence of Scales

The most beautiful claim in music acoustics:
  Every natural sound has overtones (integer multiples of fundamental).
  The intervals between those overtones ARE the consonant intervals.
  So musical scales emerged from physics.

This is suspiciously neat. Let me test it visually and audibly.
"""

import numpy as np
from PIL import Image, ImageDraw
import struct, os

OUT = r"C:\Users\许耀仁\.openclaw\workspace\curiosity-music"
os.makedirs(OUT, exist_ok=True)

sr = 44100
dur = 1.5
t = np.linspace(0, dur, int(sr * dur), endpoint=False)


def draw_harmonic_series(fundamental=110, n_harmonics=16):
    """Draw the harmonic overtone series on a keyboard-like display."""
    img = Image.new("RGB", (900, 500), "white")
    draw = ImageDraw.Draw(img)
    draw.text((20, 10), f"Harmonic Series of {fundamental}Hz (A2)", fill="black")

    harmonics = [fundamental * i for i in range(1, n_harmonics + 1)]
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    def freq_to_note(f):
        if f <= 0:
            return "?", 999
        semitones = 12 * np.log2(f / 440.0)
        nearest = int(round(semitones))
        cents = int((semitones - nearest) * 100)
        octave = 4 + (nearest + 9) // 12
        note_idx = (nearest + 9) % 12
        return f"{note_names[note_idx]}{octave}", cents

    y_start = 60
    bar_h = 25
    max_width = 800

    for i, h in enumerate(harmonics):
        ratio_str = f"{i+1}:1"
        note_name, cents_dev = freq_to_note(h)
        deviation = f"{cents_dev:+d}ct" if abs(cents_dev) < 50 else f"{cents_dev:+d}ct"
        bar_w = min(max_width, int(h / harmonics[-1] * max_width))
        y = y_start + i * (bar_h + 4)
        green = max(100, 255 - abs(cents_dev) * 3)
        red = min(255, abs(cents_dev) * 3)
        fill = (red, green, 180)
        draw.rectangle([50, y, 50 + bar_w, y + bar_h], fill=fill, outline="black")
        draw.text((55, y + 4), f"h{i+1}  {h:.1f}Hz  ({ratio_str})", fill="black")
        draw.text((max_width + 60, y + 4), f"~{note_name} ({deviation})", fill="black")

    # Scale emergence box
    scale_y = y_start + n_harmonics * (bar_h + 4) + 20
    draw.rectangle([20, scale_y, 880, scale_y + 160], outline="gray")
    draw.text((30, scale_y + 5), "Intervals in the Harmonic Series:", fill="black")

    interval_y = scale_y + 30
    for idx in range(1, min(n_harmonics, 16)):
        h_low, h_high = idx, idx + 1
        ratio_val = h_high / h_low
        x = 30 + ((idx - 1) % 4) * 210
        y = interval_y + ((idx - 1) // 4) * 25
        interval_name = {
            2/1: "Octave", 3/2: "Fifth", 4/3: "Fourth",
            5/4: "Maj 3rd", 6/5: "Min 3rd",
            7/6: "7th (flat)", 8/7: "Maj 2nd (wide)",
            9/8: "Maj 2nd", 10/9: "Min 2nd",
            16/15: "Semitone",
        }.get(ratio_val, f"{ratio_val:.4f}")
        draw.text((x, y),
                  f"h{h_low}->h{h_high}: {ratio_str}={interval_name}",
                  fill="black")

    draw.text((30, interval_y + 70),
              "All consonant intervals appear naturally in the overtone series.",
              fill="gray")
    draw.text((30, interval_y + 90),
              "h4/h5/h6/h7/h8/h9 = C/E/G/Bb/C/D = entire major scale built in.",
              fill="gray")
    draw.text((30, interval_y + 115),
              "This is the strongest argument for 'music emerges from physics'.",
              fill="gray")

    return img


img_harm = draw_harmonic_series(110, 16)
img_harm.save(f"{OUT}\\10_harmonic_series.png")
img_harm2 = draw_harmonic_series(220, 12)
img_harm2.save(f"{OUT}\\11_harmonic_series_a3.png")


def save_wav(filename, samples, sample_rate=44100):
    samples = samples / np.max(np.abs(samples)) * 0.9
    samples_int = np.int16(samples * 32767)
    n = len(samples_int)
    with open(filename, "wb") as f:
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36 + n * 2))
        f.write(b"WAVE")
        f.write(b"fmt ")
        f.write(struct.pack("<I", 16))
        f.write(struct.pack("<H", 1))
        f.write(struct.pack("<H", 1))
        f.write(struct.pack("<I", sample_rate))
        f.write(struct.pack("<I", sample_rate * 2))
        f.write(struct.pack("<H", 2))
        f.write(struct.pack("<H", 16))
        f.write(b"data")
        f.write(struct.pack("<I", n * 2))
        samples_int.tofile(f)


def tone(freq, harmonics=[1.0, 0.5, 0.25, 0.125, 0.0625]):
    result = np.zeros_like(t)
    for i, amp in enumerate(harmonics):
        if amp > 0:
            result += amp * np.sin(2 * np.pi * freq * (i + 1) * t)
    return result * 0.3


base = 262  # C4
intervals = [
    ("01_unison", base, base),
    ("02_octave", base, base * 2),
    ("03_fifth", base, base * 3/2),
    ("04_fourth", base, base * 4/3),
    ("05_major_third", base, base * 5/4),
    ("06_minor_third", base, base * 6/5),
    ("07_tritone", base, base * 45/32),
    ("08_semitone", base, base * 16/15),
]

print("=== Generated WAV files ===")
for name, f1, f2 in intervals:
    silence = np.zeros(int(sr * 0.2))
    wav = np.concatenate([
        tone(f1) * 0.5, silence,
        (tone(f1) + tone(f2)) * 0.5, silence,
        tone(f2) * 0.5,
    ])
    path = f"{OUT}\\wav_{name}.wav"
    save_wav(path, wav)
    print(f"  wav_{name}.wav  ({f1:.1f}Hz + {f2:.1f}Hz)")

chord_notes = [
    ("major_triad", [base, base * 5/4, base * 3/2]),
    ("minor_triad", [base, base * 6/5, base * 3/2]),
    ("diminished", [base, base * 6/5, base * 45/32]),
]
for name, freqs in chord_notes:
    wav = np.zeros(len(t))
    for f in freqs:
        wav += tone(f)
    wav = wav / np.max(np.abs(wav)) * 0.5
    path = f"{OUT}\\wav_chord_{name}.wav"
    save_wav(path, wav)
    print(f"  wav_chord_{name}.wav  ({','.join(f'{f:.1f}' for f in freqs)})")

print()
print("All WAV files saved.")


def draw_tuning_comparison():
    img = Image.new("RGB", (900, 480), "white")
    draw = ImageDraw.Draw(img)
    draw.text((20, 10), "Equal Temperament vs Just Intonation: C Major Scale", fill="black")
    draw.text((20, 30),
              "Just = pure ratios from harmonic series. ET = 12-TET compromise.",
              fill="gray")

    et_ratios = {0: 1.0, 2: 2**(2/12), 4: 2**(4/12), 5: 2**(5/12),
                 7: 2**(7/12), 9: 2**(9/12), 11: 2**(11/12), 12: 2.0}
    just_ratios = {0: 1/1, 2: 9/8, 4: 5/4, 5: 4/3,
                   7: 3/2, 9: 5/3, 11: 15/8, 12: 2/1}
    note_labels = {0: "C", 2: "D", 4: "E", 5: "F",
                   7: "G", 9: "A", 11: "B", 12: "C'"}

    base_freq = 262
    bar_h = 30
    y0 = 60

    draw.text((50, y0), "Note", fill="black")
    draw.text((150, y0), "Ratio", fill="black")
    draw.text((300, y0), "Just (Hz)", fill="black")
    draw.text((450, y0), "ET (Hz)", fill="black")
    draw.text((600, y0), "Diff", fill="black")
    draw.text((750, y0), "Cents", fill="black")

    for i, semi in enumerate([0, 2, 4, 5, 7, 9, 11, 12]):
        y = y0 + 30 + i * (bar_h + 5)
        j_freq = base_freq * just_ratios[semi]
        e_freq = base_freq * et_ratios[semi]
        cents = 1200 * np.log2(j_freq / e_freq)
        color = "green" if abs(cents) < 2 else ("orange" if abs(cents) < 10 else "red")
        draw.text((50, y), note_labels[semi], fill="black")
        draw.text((150, y), f"{just_ratios[semi]:.4f}", fill="black")
        draw.text((300, y), f"{j_freq:.2f}", fill=color)
        draw.text((450, y), f"{e_freq:.2f}", fill=color)
        draw.text((600, y), f"{j_freq - e_freq:+.2f}", fill=color)
        draw.text((750, y), f"{cents:+.1f}", fill=color)

    note_y = y0 + 30 + 8 * (bar_h + 5) + 15
    draw.text((20, note_y),
              "ET is a system-wide compromise. Every interval slightly off from pure.",
              fill="black")
    draw.text((20, note_y + 20),
              "But ET allows key modulation. Just intonation only perfect in ONE key.",
              fill="black")
    draw.text((20, note_y + 40),
              "This trade-off is the first genuinely 'emergent' structure I see here:",
              fill="black")
    draw.text((20, note_y + 60),
              "a system-level solution that nobody designed, discovered independently",
              fill="black")
    draw.text((20, note_y + 80),
              "across cultures, from the need for flexible harmony.",
              fill="black")

    return img


img_tune = draw_tuning_comparison()
img_tune.save(f"{OUT}\\12_tuning_comparison.png")

print()
print("=== Step 2 Summary ===")
print()
print("What I found:")
print("- Harmonic series produces ALL consonant intervals naturally")
print("- The major scale (h4 through h9) falls out of it")
print("- But our ears accept equal temperament, which tunes away from pure ratios")
print("- This means 'consonant' is NOT purely physical")
print("- It's a negotiation between physics and system-level requirements")
print()
print("First emergent structure: equal temperament")
print("  Not designed. Emerged as a compromise between multiple constraints.")
print("  A system-level solution to a system-level problem.")
print()
