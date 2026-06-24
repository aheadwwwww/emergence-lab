"""
#019 Strange Loops: Tangled Hierarchies & Self-Reference in Action

Hofstadter's Strange Loops — systems where moving up through levels
inevitably leads back to the starting level, creating a self-referential
cycle that generates meaning, consciousness, and paradox.

Experiments:
1. Recursive Pattern Generator — Escher-style infinite nesting
2. Self-Modifying Grammar — rules that rewrite themselves
3. Strange Loop Truth Teller — logical paradox visualization
4. Meta-Circular Evaluator — interpreter that can evaluate itself
5. Strange Loop Emergence — multi-level system that loops back
"""

import random, math, sys, io
from PIL import Image, ImageDraw

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

OUTPUT_DIR = "experiments"


# ============================================================
# EXPERIMENT 1: Recursive Pattern Generator (Escher-style)
# ============================================================
# Like Escher's "Drawing Hands" — each level contains the previous,
# and the highest level references back to the lowest.

def recursive_escher_pattern(filename=f"{OUTPUT_DIR}/strange_loop_recursive.png"):
    """Generate an Escher-style recursive nesting pattern.
    
    Each level 'contains' the level above, creating a visual
    strange loop where inside becomes outside."""
    
    size = 800
    img = Image.new('RGB', (size, size), '#0d1117')
    draw = ImageDraw.Draw(img)
    
    def draw_nested_squares(cx, cy, side, depth, max_depth=7):
        if depth > max_depth or side < 8:
            return
        
        # Color shifts with depth — creates rainbow strange loop
        t = depth / max_depth
        r = int(80 + 175 * math.sin(t * math.pi * 2))
        g = int(80 + 175 * math.sin(t * math.pi * 2 + 2.09))
        b = int(80 + 175 * math.sin(t * math.pi * 2 + 4.19))
        
        # Draw square rotated slightly
        angle = depth * 0.15
        half = side // 2
        corners = []
        for deg in [45, 135, 225, 315]:
            rad = math.radians(deg + angle * 180 / math.pi)
            px = cx + half * math.cos(rad)
            py = cy + half * math.sin(rad)
            corners.append((px, py))
        
        # Draw the square
        for i in range(4):
            draw.line([corners[i], corners[(i+1) % 4]], 
                      fill=(r, g, b), width=2)
        
        # Recurse with smaller square, slightly shifted
        shift = side * 0.08
        new_cx = cx + shift * math.cos(angle * 2)
        new_cy = cy + shift * math.sin(angle * 2)
        new_side = side * 0.85
        
        draw_nested_squares(new_cx, new_cy, new_side, depth + 1, max_depth)
        
        # The STRANGE LOOP: from the deepest level, draw back to outer
        if depth == max_depth - 1:
            # Draw a feedback line from innermost to outermost
            for i in range(0, 360, 3):
                rad = math.radians(i)
                px = cx + size * 0.35 * math.cos(rad)
                py = cy + size * 0.35 * math.sin(rad)
                draw.point((px, py), fill=(255, 200, 100))
    
    cx, cy = size // 2, size // 2
    draw_nested_squares(cx, cy, 500, 0, 8)
    
    # Title
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("arial.ttf", 14)
        font_title = ImageFont.truetype("arial.ttf", 18)
    except:
        font = ImageFont.load_default()
        font_title = ImageFont.load_default()
    
    draw.text((20, 15), "#019 Strange Loops: Recursive Nesting", 
              fill='#58a6ff', font=font_title)
    draw.text((20, 40), "Each level 'contains' the next — and the deepest loops back", 
              fill='#8b949e', font=font)
    
    img.save(filename)
    print(f"  Saved: {filename}")
    return filename


# ============================================================
# EXPERIMENT 2: Self-Modifying Grammar (L-System with Strange Loop)
# ============================================================
# A grammar where rules can reference themselves, creating
# tangled hierarchies — like Hofstadter's "Strange Loop" in language.

def self_modifying_grammar(filename=f"{OUTPUT_DIR}/strange_loop_grammar.png"):
    """L-System with self-referential rules that create tangled hierarchies.
    
    Standard L-System: A → AB, B → A (Fibonacci)
    Strange Loop L-System: A → A[B], B → [A] where brackets mean "contains"
    """
    
    def generate_strange(axiom, rules, iterations):
        current = axiom
        history = []
        for i in range(iterations):
            next_str = ""
            for ch in current:
                next_str += rules.get(ch, ch)
            current = next_str
            if len(current) > 2000:
                break
            history.append((i, current[:100]))
        return history
    
    # Standard Fibonacci word (for comparison)
    fib_rules = {'A': 'AB', 'B': 'A'}
    fib = generate_strange('A', fib_rules, 10)
    
    # Strange loop grammar: self-referential containment
    # 'S' creates nested loops, 'L' links back
    strange_rules = {
        'S': 'S[L]S',
        'L': '<S>',
        '[': '[',
        ']': ']',
        '<': '<',
        '>': '>'
    }
    
    # Actually let's do something more interesting
    # A grammar where rules rewrite themselves
    class SelfModifyingGrammar:
        def __init__(self):
            self.rules = {'A': 'AB', 'B': 'A'}
            self.rule_history = []
        
        def step(self):
            """The grammar can modify its own rules based on its output."""
            # Current axiom
            axiom = 'A'
            result = axiom
            for _ in range(3):  # Apply current rules
                result = "".join(self.rules.get(c, c) for c in result)
            
            # Self-modification: if result contains 'AB', add new rule
            if 'AB' in result:
                self.rules['C'] = 'ABC'
            if 'ABCABC' in result:
                self.rules['B'] = 'CAB'  # Rule changes!
            
            self.rule_history.append(dict(self.rules))
            return result
    
    # Visualize the rule evolution
    width, height = 800, 600
    img = Image.new('RGB', (width, height), '#0d1117')
    draw = ImageDraw.Draw(img)
    
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("arial.ttf", 11)
        font_title = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
        font_title = ImageFont.load_default()
    
    draw.text((20, 15), "Self-Modifying Grammar: Rules That Rewrite Themselves", 
              fill='#58a6ff', font=font_title)
    
    # Run the self-modifying grammar
    smg = SelfModifyingGrammar()
    outputs = []
    for i in range(10):
        out = smg.step()
        outputs.append(out)
    
    # Display rule evolution
    y = 50
    for i, (rules, out) in enumerate(zip(smg.rule_history, outputs)):
        rule_str = ", ".join(f"{k}→{v}" for k, v in rules.items())
        draw.text((20, y), f"t={i+1}: {{{rule_str}}}", 
                  fill='#f78166', font=font)
        draw.text((20, y + 14), f"   Output: {out[:60]}", 
                  fill='#8b949e', font=font)
        y += 32
    
    # Show Fibonacci word for comparison
    draw.text((20, y + 10), "Fibonacci Word (no self-modification):", 
              fill='#79c0ff', font=font)
    for i, (gen, word) in enumerate(fib[:5]):
        draw.text((20, y + 28 + i * 16), f"  gen {gen+1}: {word[:60]}", 
                  fill='#8b949e', font=font)
    
    # Key insight at bottom
    draw.text((width // 2, height - 30), 
              "Self-modifying rules create a strange loop: the system's output changes the system itself",
              fill='#e6edf3', font=font, anchor="mm")
    
    img.save(filename)
    print(f"  Saved: {filename}")
    return filename


# ============================================================
# EXPERIMENT 3: Strange Loop Truth Teller (Logical Paradox)
# ============================================================
# Visualizing the classic strange loops in logic:
# "This statement is false" → the simplest strange loop

def logical_strange_loop(filename=f"{OUTPUT_DIR}/strange_loop_logic.png"):
    """Map the truth space of self-referential statements."""
    
    width, height = 900, 700
    img = Image.new('RGB', (width, height), '#0d1117')
    draw = ImageDraw.Draw(img)
    
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("arial.ttf", 12)
        font_title = ImageFont.truetype("arial.ttf", 16)
        font_big = ImageFont.truetype("arial.ttf", 18)
    except:
        font = ImageFont.load_default()
        font_title = ImageFont.load_default()
        font_big = ImageFont.load_default()
    
    draw.text((20, 15), "Strange Loops in Logic: Self-Referential Truth", 
              fill='#58a6ff', font=font_title)
    
    # Build a table of self-referential statements
    statements = [
        ("S₁", "This statement is false", "Liar Paradox", "↺ Oscillates"),
        ("S₂", "This statement is true", "Trivial Truth", "✓ Always True"),
        ("S₃", "S₅ is true", "Cross-ref #1", "Depends on S₅"),
        ("S₄", "S₃ is false", "Cross-ref #2", "Depends on S₃"),
        ("S₅", "S₄ is false", "Cross-ref #3", "→ S₃=True → S₄=False → S₅=True ✓"),
        ("S₆", "S₁ is true and S₁ is false", "Contradiction", "✗ Always False"),
        ("G", "G is not provable in system F", "Gödel Sentence", "⊢ G ↔ ¬Provable(G)"),
        ("T", "T is not provably true", "Truth Predicate", "⊢ T ↔ ¬True(T)"),
    ]
    
    y = 50
    # Header
    for w, text in [(20, "ID"), (50, "Statement"), (360, "Type"), (560, "Behavior")]:
        draw.text((w, y), text, fill='#79c0ff', font=font)
    
    draw.line([(20, y + 16), (880, y + 16)], fill='#21262d', width=1)
    y += 24
    
    for sid, stmt, stype, behavior in statements:
        is_loop = "Oscillates" in behavior or "Gödel" in stype or "Truth" in stype
        color = '#ff7b72' if is_loop else '#7ee787'
        
        draw.text((20, y), sid, fill='#8b949e', font=font)
        draw.text((50, y), f'"{stmt}"', fill=color, font=font)
        draw.text((360, y), stype, fill='#d2a8ff', font=font)
        draw.text((560, y), behavior, fill=color if is_loop else '#8b949e', font=font)
        y += 20
    
    # Draw the loop diagram
    y += 20
    draw.text((20, y), "The Gödelian Strange Loop:", fill='#f78166', font=font_title)
    y += 25
    
    # Visual: System F → Gödel Sentence G → G says "G not provable in F"
    # → If G is provable → contradiction → G is not provable
    # → Therefore G is true but unprovable → System F is incomplete
    
    loop_nodes = [
        (200, y,     "System F", "Formal system"),
        (400, y,     "Gödel Sentence G", "G = 'G is not provable in F'"),
        (600, y,     "Prove G?", ""),
        (600, y+50,  "YES → Contradiction", "G says it's unprovable"),
        (400, y+50,  "NO → G is true", "but unprovable"),
        (200, y+50,  "F is incomplete", "Some truths lie outside"),
    ]
    
    for nx, ny, label, desc in loop_nodes:
        draw.rectangle([nx-10, ny-12, nx + len(label)*7 + 10, ny+4], 
                      fill='#161b22', outline='#30363d', width=1)
        draw.text((nx, ny-8), label, fill='#58a6ff', font=font)
        if desc:
            draw.text((nx, ny+10), desc, fill='#8b949e', font=font)
    
    # Arrow: System F → Gödel sentence
    draw.line([(290, y-4), (390, y-4)], fill='#8b949e', width=1)
    # Arrow down from Prove G
    draw.line([(610, y+4), (610, y+46)], fill='#8b949e', width=1)
    # Arrow: YES → Contradiction
    draw.line([(680, y+54), (580, y+54)], fill='#ff7b72', width=1)
    # Arrow: NO → G is true 
    draw.line([(610, y+54), (490, y+54)], fill='#7ee787', width=1)
    # Arrow back to F is incomplete
    draw.line([(410, y+54), (290, y+54)], fill='#d2a8ff', width=1)
    
    # Key insight
    y += 90
    draw.text((width // 2, y), 
              "Gödel's Incompleteness: every sufficiently powerful system", 
              fill='#e6edf3', font=font_big, anchor="mm")
    draw.text((width // 2, y + 25), 
              "can create a statement about itself — and that statement", 
              fill='#e6edf3', font=font_big, anchor="mm")
    draw.text((width // 2, y + 50), 
              "creates a strange loop that escapes the system.", 
              fill='#f78166', font=font_big, anchor="mm")
    
    img.save(filename)
    print(f"  Saved: {filename}")
    return filename


# ============================================================
# EXPERIMENT 4: Strange Loop Emergence — Multi-Level Simulation
# ============================================================
# A system where micro-rules create macro-behaviors that 
# feedback and modify the micro-rules — the essence of a 
# strange loop between levels.

def strange_loop_emergence(filename=f"{OUTPUT_DIR}/strange_loop_emergence.png"):
    """Simulate a multi-level system with top-down causation.
    
    Level 1: Individual agents follow simple rules
    Level 2: Collective patterns emerge from agent interactions
    Level 3: These patterns modify the rules at Level 1
    
    This is a computational strange loop."""
    
    class StrangeLoopWorld:
        def __init__(self):
            self.size = 50
            self.agents = [(random.randint(0, self.size-1), 
                           random.randint(0, self.size-1)) 
                          for _ in range(30)]
            self.rule_bias = 0.5  # Level 1 rule parameter
            self.macro_state = 0.5  # Level 2 emergent state
            self.feedback_strength = 0.0  # Level 3: how much macro affects micro
            self.history = {
                'macro': [],
                'bias': [],
                'feedback': [],
                'entropy': []
            }
        
        def step(self, t):
            # Level 1: Agent movement
            new_agents = []
            for x, y in self.agents:
                # Rule affected by current bias
                if random.random() < self.rule_bias:
                    # Explore — move randomly
                    dx = random.choice([-1, 0, 1])
                    dy = random.choice([-1, 0, 1])
                else:
                    # Exploit — move toward nearest neighbor
                    nearest = min([(ax, ay) for ax, ay in self.agents 
                                  if (ax, ay) != (x, y)], 
                                 key=lambda p: (p[0]-x)**2 + (p[1]-y)**2,
                                 default=(x, y))
                    dx = 1 if nearest[0] > x else -1 if nearest[0] < x else 0
                    dy = 1 if nearest[1] > y else -1 if nearest[1] < y else 0
                
                nx = max(0, min(self.size-1, x + dx))
                ny = max(0, min(self.size-1, y + dy))
                new_agents.append((nx, ny))
            
            self.agents = new_agents
            
            # Level 2: Compute macro state (clustering)
            if len(new_agents) > 1:
                distances = []
                for i in range(min(50, len(new_agents))):
                    for j in range(i+1, min(50, len(new_agents))):
                        d = math.sqrt((new_agents[i][0]-new_agents[j][0])**2 +
                                     (new_agents[i][1]-new_agents[j][1])**2)
                        distances.append(d)
                avg_dist = sum(distances) / len(distances) if distances else self.size
                self.macro_state = 1.0 - (avg_dist / (self.size * math.sqrt(2)))
            else:
                self.macro_state = 0.0
            
            # Level 3: Strange loop — macro state feeds back to micro rule
            # When clustering is high → bias toward exploration (break clusters)
            # When clustering is low → bias toward exploitation (form clusters)
            target_bias = 0.5 + 0.3 * math.sin(self.macro_state * math.pi * 2 + t * 0.1)
            self.rule_bias += 0.05 * (target_bias - self.rule_bias)
            self.rule_bias = max(0.1, min(0.9, self.rule_bias))
            
            # Feedback strength increases over time (the loop tightens)
            self.feedback_strength = min(0.9, self.feedback_strength + 0.005)
            
            # Record
            self.history['macro'].append(self.macro_state)
            self.history['bias'].append(self.rule_bias)
            self.history['feedback'].append(self.feedback_strength)
            
            # Entropy: measure of agent dispersion
            cell_occupancy = {}
            for x, y in new_agents:
                cx, cy = x // 5, y // 5
                cell_occupancy[(cx, cy)] = cell_occupancy.get((cx, cy), 0) + 1
            total_cells = (self.size // 5) ** 2
            occupied = len(cell_occupancy)
            self.history['entropy'].append(occupied / total_cells if total_cells > 0 else 0)
    
    # Run simulation
    world = StrangeLoopWorld()
    for t in range(120):
        world.step(t)
    
    # Visualize
    width, height = 900, 700
    img = Image.new('RGB', (width, height), '#0d1117')
    draw = ImageDraw.Draw(img)
    
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("arial.ttf", 11)
        font_title = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
        font_title = ImageFont.load_default()
    
    draw.text((20, 15), "Strange Loop Emergence: Top-Down Causation", 
              fill='#58a6ff', font=font_title)
    draw.text((20, 38), "Micro-rules → Macro-patterns → Rule modification (the strange loop)", 
              fill='#8b949e', font=font)
    
    # Helper: plot a line
    def add_plot(data, x0, y0, w, h, color, label):
        max_val = max(data) if data else 1
        min_val = min(data) if data else 0
        rng = max_val - min_val if max_val > min_val else 1
        for i in range(1, len(data)):
            x1 = x0 + (i-1) * w // len(data)
            y1 = y0 + h - int((data[i-1] - min_val) / rng * h)
            x2 = x0 + i * w // len(data)
            y2 = y0 + h - int((data[i] - min_val) / rng * h)
            draw.line([(x1, y1), (x2, y2)], fill=color, width=2)
        draw.text((x0, y0 - 14), label, fill=color, font=font)
    
    # Plot 1: Macro state (clustering)
    add_plot(world.history['macro'], 50, 70, 350, 100, '#79c0ff', "Macro Clustering ↑")
    
    # Plot 2: Rule bias (micro-level)
    add_plot(world.history['bias'], 50, 220, 350, 100, '#f78166', "Rule Bias (explore vs exploit)")
    
    # Plot 3: Feedback strength
    add_plot(world.history['feedback'], 50, 370, 350, 100, '#d2a8ff', "Strange Loop Feedback ↑")
    
    # Plot 4: Entropy / dispersion
    add_plot(world.history['entropy'], 50, 520, 350, 100, '#7ee787', "Spatial Entropy")
    
    # Right side: Diagram of the strange loop
    cx, cy = 700, 350
    levels = [
        ("Micro Level", "Agents follow rules", "#1f2937", 300, 60, -120),
        ("Macro Level", "Clustering emerges", "#1a2332", 280, 60, -40),
        ("Feedback Loop", "Macro modifies micro rules", "#162032", 280, 60, 40),
        ("Strange Loop", "System self-regulates", "#0d1117", 280, 60, 120),
    ]
    
    for name, desc, bg, w, h, y_off in levels:
        x = cx - w // 2
        draw.rectangle([x, cy + y_off, x + w, cy + y_off + h], 
                      fill=bg, outline='#30363d', width=1)
        draw.text((cx, cy + y_off + 10), name, fill='#58a6ff', font=font, anchor="mm")
        draw.text((cx, cy + y_off + 26), desc, fill='#8b949e', font=font, anchor="mm")
    
    # Arrows going up (feedback is the strange loop!)
    for i, (y1, y2) in enumerate([(-60, 10), (20, 70), (100, 130)]):
        # Arrow going up-right
        draw.line([(cx + 10, cy + y1), (cx + 10, cy + y2)], 
                  fill='#f78166' if i == 2 else '#8b949e', width=2)
    
    # Bottom arrow from Feedback back to Micro (THE STRANGE LOOP)
    # Draw curved arrow
    arc_points = []
    for a in range(0, 181, 5):
        rad = math.radians(a - 90)
        px = cx + 160 * math.cos(rad)
        py = cy + 100 * math.sin(rad)
        arc_points.append((px, py))
    
    for i in range(1, len(arc_points)):
        draw.line([arc_points[i-1], arc_points[i]], fill='#f78166', width=3)
    
    draw.text((cx + 180, cy - 10), "↺", fill='#ff7b72', font=font_title)
    
    # Legend at bottom
    legend_items = [
        ("Macro Clustering", '#79c0ff'),
        ("Rule Bias", '#f78166'),
        ("Feedback", '#d2a8ff'),
        ("Entropy", '#7ee787'),
    ]
    
    lx = 450
    for i, (name, color) in enumerate(legend_items):
        draw.rectangle([lx + i * 110, 630, lx + i * 110 + 10, 640], fill=color)
        draw.text((lx + i * 110 + 14, 628), name, fill='#8b949e', font=font)
    
    # Insight
    draw.text((width // 2, 668), 
              "A strange loop: agents → clusters → rule change → new agent behavior → ...",
              fill='#e6edf3', font=font, anchor="mm")
    
    img.save(filename)
    print(f"  Saved: {filename}")
    return filename


# ============================================================
# EXPERIMENT 5: Strange Loop Audio Visualization
# ============================================================
# Musical strange loops: canons that end where they begin,
# like Bach's "Crab Canon" or Shepard tones.

def strange_loop_shepard(filename=f"{OUTPUT_DIR}/strange_loop_shepard.png"):
    """Visualize the Shepard tone — an auditory strange loop
    that seems to rise infinitely but actually cycles."""
    
    width, height = 800, 600
    img = Image.new('RGB', (width, height), '#0d1117')
    draw = ImageDraw.Draw(img)
    
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("arial.ttf", 12)
        font_title = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
        font_title = ImageFont.load_default()
    
    draw.text((20, 15), "Auditory Strange Loop: The Shepard Tone", 
              fill='#58a6ff', font=font_title)
    draw.text((20, 38), "A tone that seems to rise forever but actually cycles — Bach's infinite canon", 
              fill='#8b949e', font=font)
    
    # Draw the Shepard tone as overlapping sine waves
    # Each octave starts soft, grows loud, then fades
    # As one octave fades out, the next octave up appears
    # Creating the illusion of infinite ascent
    
    cx, cy = 400, 300
    
    # Draw multiple octaves with phase shifts
    octaves = 4
    for octave in range(octaves):
        base_freq = 220 * (2 ** octave)
        for x in range(0, 800, 2):
            t = x / 800
            # Each octave follows an amplitude envelope
            # that shifts in time — creating the illusion
            phase = t + octave * 0.25
            amplitude = max(0, math.sin(phase * math.pi * 2) ** 2)
            # Remove low amplitudes for clarity
            if amplitude < 0.05:
                continue
            y = cy + int(amplitude * 80 * math.sin(t * base_freq * 0.1))
            y = max(50, min(height - 50, y))
            
            # Color by octave
            hue = (octave / octaves) * 360
            r = int(100 + 155 * math.sin(hue * math.pi / 180 + octave))
            g = int(100 + 155 * math.sin(hue * math.pi / 180 + 2.09 + octave))
            b = int(100 + 155 * math.sin(hue * math.pi / 180 + 4.19 + octave))
            
            img.putpixel((x, y), (min(255, r), min(255, g), min(255, b)))
    
    # Show the amplitude envelopes
    draw.text((20, 100), "Amplitude envelopes (each octave rises and falls):", 
              fill='#d2a8ff', font=font)
    
    for octave in range(octaves):
        y_base = 120 + octave * 25
        for x in range(0, 780, 5):
            t = x / 780
            phase = t + octave * 0.25
            amp = max(0, math.sin(phase * math.pi * 2) ** 2)
            y = y_base - int(amp * 15)
            px = 20 + x
            color = ['#ff7b72', '#79c0ff', '#7ee787', '#d2a8ff'][octave]
            draw.point((px, y), fill=color)
        
        draw.text((20, y_base + 5), f"Octave {octave+1} ({220*2**octave:.0f}Hz)", 
                  fill=['#ff7b72', '#79c0ff', '#7ee787', '#d2a8ff'][octave], font=font)
    
    # Explanation
    explanations = [
        "How the auditory strange loop works:",
        "",
        "1. Multiple octaves play simultaneously",
        "2. Each octave's volume follows a rising-then-falling envelope",
        "3. As octave 1 fades, octave 2 is at its loudest",
        "4. As octave 2 fades, octave 3 is at its loudest",
        "5. When octave N fades, octave 1 reappears — the loop completes",
        "",
        "→ The brain perceives a continuously rising pitch",
        "→ But the system never actually goes anywhere",
        "→ This IS a strange loop: upward motion that returns to its origin"
    ]
    
    y = 260
    for line in explanations:
        if "→" in line:
            draw.text((20, y), line, fill='#f78166', font=font)
        elif line.startswith("How"):
            draw.text((20, y), line, fill='#79c0ff', font=font)
        else:
            draw.text((20, y), line, fill='#8b949e', font=font)
        y += 18
    
    # Connection to consciousness
    draw.text((width // 2, 540), 
              "Hofstadter: Consciousness is a strange loop —", 
              fill='#e6edf3', font=font_title, anchor="mm")
    draw.text((width // 2, 565), 
              "a self-referential hierarchy that loops back on itself to create 'I'", 
              fill='#8b949e', font=font, anchor="mm")
    
    img.save(filename)
    print(f"  Saved: {filename}")
    return filename


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("#019 Strange Loops Exploration")
    print("=" * 60)
    
    print("\n[1/5] Escher-style Recursive Nesting:")
    recursive_escher_pattern()
    
    print("\n[2/5] Self-Modifying Grammar:")
    self_modifying_grammar()
    
    print("\n[3/5] Logical Strange Loops (Gödel):")
    logical_strange_loop()
    
    print("\n[4/5] Strange Loop Emergence (Top-Down Causation):")
    strange_loop_emergence()
    
    print("\n[5/5] Shepard Tone / Auditory Strange Loop:")
    strange_loop_shepard()
    
    print("\n" + "=" * 60)
    print("#019 Strange Loops exploration complete!")
    print()
    print("Key Ideas:")
    print("1. A strange loop is a hierarchy where moving upward")
    print("   inevitably leads back to the starting level")
    print("2. Gödel: formal systems create strange loops via self-reference")
    print("3. Escher: visual art creates strange loops via impossible figures")
    print("4. Bach: music creates strange loops via canons that modulate")
    print("5. Consciousness: the ultimate strange loop")
    print("=" * 60)
