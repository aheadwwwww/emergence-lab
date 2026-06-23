"""
#027 音乐与涌现 — Emergent Music

从涌现系统生成音乐：
- 用 1D 元胞自动机（Wolfram CA）驱动旋律生成
- 用 2D 反应扩散（Gray-Scott）驱动和声/节奏
- 输出 MIDI 文件

核心思想：简单规则 → 复杂音序 → 涌现式音乐
"""

import numpy as np
from midiutil import MIDIFile
import random

# ============================================================
# 1D Cellular Automata → Melody
# ============================================================

def wolfram_step(state, rule):
    """Wolfram 1D CA 单步演化"""
    n = len(state)
    new_state = np.zeros(n, dtype=int)
    for i in range(n):
        left = state[(i - 1) % n]
        center = state[i]
        right = state[(i + 1) % n]
        pattern = (left << 2) | (center << 1) | right
        new_state[i] = (rule >> pattern) & 1
    return new_state

def ca_to_melody(state, scale, octave_base=4):
    """
    将 CA 状态映射为音符。
    活跃cell → 音高，非活跃 → 休止
    """
    notes = []
    for i, cell in enumerate(state):
        if cell == 1:
            note_idx = i % len(scale)
            octave = octave_base + (i // len(scale))
            notes.append((scale[note_idx], octave))
        else:
            notes.append(None)  # 休止
    return notes

# ============================================================
# 2D Gray-Scott → Harmony / Rhythm
# ============================================================

def gray_scott_step(U, V, Du, Dv, f, k, dt=0.04):
    """Gray-Scott 反应扩散单步"""
    # Laplacian (5-point stencil)
    def laplacian(X):
        return (np.roll(X, 1, 0) + np.roll(X, -1, 0) +
                np.roll(X, 1, 1) + np.roll(X, -1, 1) - 4 * X)
    
    Lu = laplacian(U)
    Lv = laplacian(V)
    
    uvv = U * V * V
    
    U_new = U + (Du * Lu - uvv + f * (1 - U)) * dt
    V_new = V + (Dv * Lv + uvv - (f + k) * V) * dt
    
    return np.clip(U_new, 0, 1), np.clip(V_new, 0, 1)

def gs_to_chord(V_field, chord_voicings, n_voices=3):
    """
    从 Gray-Scott V 场生成和弦。
    取 V 场中活性最高的区域，映射为和弦。
    """
    h, w = V_field.shape
    # 将 V 场分块，每块的平均活性决定该声部的音高
    block_h = h // n_voices
    chord = []
    for v in range(n_voices):
        block = V_field[v * block_h:(v + 1) * block_h, :]
        activity = np.mean(block)
        # 活性映射到和弦音
        voicing_idx = int(activity * (len(chord_voicings) - 1))
        chord.append(chord_voicings[voicing_idx])
    return chord

# ============================================================
# MIDI Generation
# ============================================================

def create_midi(notes_sequence, tempo=120, output_path='emergent_music.mid'):
    """
    从音符序列创建 MIDI 文件。
    notes_sequence: list of list of (pitch, duration_beats) or None
    """
    midi = MIDIFile(2)  # 2 tracks: melody + harmony
    
    # Track 0: Melody (from CA)
    track = 0
    midi.addTrackName(track, 0, "Emergent Melody (CA)")
    midi.addTempo(track, 0, tempo)
    
    time = 0
    beat_duration = 0.25  # 16分音符
    
    for step_notes in notes_sequence:
        for note_info in step_notes:
            if note_info is not None:
                note_name, octave = note_info
                pitch = note_to_midi(note_name, octave)
                midi.addNote(track, 0, pitch, time, beat_duration * 0.9, 80)
        time += beat_duration
    
    # Track 1: Harmony (from Gray-Scott)
    track = 1
    midi.addTrackName(track, 0, "Emergent Harmony (GS)")
    
    return midi

def note_to_midi(note_name, octave):
    """将音名转为 MIDI 编号"""
    note_map = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
                'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
    return note_map[note_name] + (octave + 1) * 12

# ============================================================
# Scale & Chord Definitions
# ============================================================

PENTATONIC = ['C', 'D', 'E', 'G', 'A']  # 五声音阶（好听）
MAJOR_SCALE = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
MINOR_SCALE = ['C', 'D', 'Eb', 'F', 'G', 'Ab', 'Bb']
DORIAN = ['C', 'D', 'Eb', 'F', 'G', 'A', 'Bb']
PHRYGIAN = ['C', 'Db', 'Eb', 'F', 'G', 'Ab', 'Bb']

CHORD_VOICINGS = [
    [0, 4, 7],      # Major triad
    [0, 3, 7],      # Minor triad
    [0, 4, 7, 11],  # Maj7
    [0, 3, 7, 10],  # Min7
    [0, 4, 7, 10],  # Dom7
    [0, 5, 7],      # Sus4
    [0, 3, 6],      # Dim
]

# ============================================================
# Main Experiment
# ============================================================

def run_experiment():
    print("=== #027 音乐与涌现 ===")
    print("从涌现系统生成音乐\n")
    
    # --- CA Melody ---
    print("[1/3] 运行 Wolfram CA 生成旋律...")
    ca_width = 32
    ca_steps = 128
    
    # 尝试多个规则，找有趣的
    interesting_rules = [30, 45, 54, 60, 90, 105, 110, 150, 184]
    
    for rule in interesting_rules:
        # 初始化
        state = np.zeros(ca_width, dtype=int)
        state[ca_width // 2] = 1  # 单点初始
        
        print(f"  Rule {rule}: ", end="")
        
        melody = []
        for step in range(ca_steps):
            notes = ca_to_melody(state, PENTATONIC, octave_base=3)
            melody.append(notes)
            state = wolfram_step(state, rule)
        
        # 统计活跃音符
        active_count = sum(1 for step in melody for n in step if n is not None)
        density = active_count / (ca_steps * ca_width)
        print(f"note density = {density:.3f}")
    
    # --- Gray-Scott Harmony ---
    print("\n[2/3] 运行 Gray-Scott 生成和声...")
    size = 64
    U = np.ones((size, size))
    V = np.zeros((size, size))
    
    # 在中心初始化斑点
    center = size // 2
    r = 5
    for i in range(size):
        for j in range(size):
            if (i - center)**2 + (j - center)**2 < r**2:
                V[i, j] = 0.25
                U[i, j] = 0.5
    
    # 有趣参数组合
    params = [
        (0.16, 0.08, 0.035, 0.065),   # 斑点
        (0.14, 0.06, 0.039, 0.058),   # 条纹+斑点
        (0.12, 0.08, 0.020, 0.050),   # 移动斑点
        (0.16, 0.08, 0.030, 0.062),   # 混沌
    ]
    
    for Du, Dv, f, k in params:
        U_cur, V_cur = U.copy(), V.copy()
        
        # 运行到稳定
        for _ in range(500):
            U_cur, V_cur = gray_scott_step(U_cur, V_cur, Du, Dv, f, k)
        
        mean_v = np.mean(V_cur)
        max_v = np.max(V_cur)
        print(f"  GS(Du={Du},Dv={Dv},f={f},k={k}): V_mean={mean_v:.4f}, V_max={max_v:.4f}")
    
    # --- Generate MIDI ---
    print("\n[3/3] 生成 MIDI 文件...")
    
    # 选择最佳参数：Rule 30 (混沌但有趣) + PENTATONIC
    best_rule = 30
    state = np.zeros(ca_width, dtype=int)
    state[ca_width // 2] = 1
    
    midi = MIDIFile(2)
    track_melody = 0
    track_harmony = 1
    
    tempo = 140
    midi.addTrackName(track_melody, 0, "CA Emergent Melody")
    midi.addTrackName(track_harmony, 0, "GS Harmony Pad")
    midi.addTempo(track_melody, 0, tempo)
    midi.addTempo(track_harmony, 0, tempo)
    
    # Gray-Scott 准备
    gs_size = 32
    U_gs = np.ones((gs_size, gs_size))
    V_gs = np.zeros((gs_size, gs_size))
    for i in range(gs_size):
        for j in range(gs_size):
            if (i - gs_size//2)**2 + (j - gs_size//2)**2 < 4**2:
                V_gs[i, j] = 0.25
                U_gs[i, j] = 0.5
    
    Du, Dv, f, k = 0.14, 0.06, 0.035, 0.065
    
    beat_dur = 0.25  # 16分音符
    time = 0
    
    # 和弦根音序列
    chord_roots = [0, 5, 7, 3, 0, 5, 9, 7]  # I-V-vi-iii-I-V-ii-V (C大调)
    
    for step in range(ca_steps):
        # CA melody
        notes = ca_to_melody(state, PENTATONIC, octave_base=4)
        for note_info in notes:
            if note_info is not None:
                note_name, octave = note_info
                pitch = note_to_midi(note_name, octave)
                velocity = random.randint(60, 90)
                midi.addNote(track_melody, 0, pitch, time, beat_dur * 0.85, velocity)
            time += beat_dur
        
        # Gray-Scott harmony (每4拍更新)
        if step % 4 == 0:
            U_gs, V_gs = gray_scott_step(U_gs, V_gs, Du, Dv, f, k)
            
            # 从 V 场提取和声
            chord_idx = step // 4
            root = chord_roots[chord_idx % len(chord_roots)]
            
            # 用 V 场活性选择 voicing
            mean_v = np.mean(V_gs)
            voicing_idx = int(mean_v * 6)  # 0-6
            voicing = CHORD_VOICINGS[min(voicing_idx, len(CHORD_VOICINGS)-1)]
            
            chord_time = (step // 4) * 4 * beat_dur
            for interval in voicing:
                pitch = note_to_midi('C', 3) + root + interval
                midi.addNote(track_harmony, 0, pitch, chord_time, 1.0, 50)
        
        state = wolfram_step(state, best_rule)
    
    output_path = 'D:\\openclaw_workspace\\experiments\\emergent_music.mid'
    with open(output_path, 'wb') as f:
        midi.writeFile(f)
    
    print(f"  MIDI saved: {output_path}")
    print(f"  Duration: {time:.1f} beats = {time/tempo*60:.1f}s at {tempo} BPM")
    print(f"  Rule: {best_rule}, Scale: Pentatonic")
    
    # --- Analysis ---
    print("\n=== 分析 ===")
    print("涌现音乐的核心洞察：")
    print("  1. CA 的局部规则产生全局旋律结构")
    print("  2. 五声音阶确保即使随机也'好听'")
    print("  3. Gray-Scott 斑图驱动和声密度变化")
    print("  4. 音乐是时间上的涌现 — 音符序列从简单规则中生长")
    print()
    print("好奇心地图节点: #027 音乐与涌现 ✓")
    
    return output_path

if __name__ == '__main__':
    run_experiment()
