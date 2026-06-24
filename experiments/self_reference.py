"""
#016 Self-Reference: Quines, Gödel, and Self-Referential Computation
心好奇心地图节点 #016

Self-reference is a foundational concept connecting:
- Gödel's incompleteness → formal systems can talk about themselves
- Quines → programs that output their own source code
- Strange Loops → Hofstadter's idea of self-referential hierarchies
- Emergence → when a system models itself, new behaviors emerge

Experiments:
1. Python Quine - a program that prints itself
2. Self-referential cellular automaton - CA that reads its own state
3. Meta-circular evaluator - a tiny interpreter that can interpret itself
4. Self-modeling agent - an agent that predicts its own next state
"""

from PIL import Image, ImageDraw, ImageFont
import sys, io, random, math

# Ensure stdout uses utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============================================================
# EXPERIMENT 1: QUINE — A program that prints itself
# ============================================================

def quine_demo():
    """A classic quine: the program reproduces its own source."""
    s = 's = %r; print(s %% s)'; print(s % s)

def quine_with_data():
    """A quine that also carries data — like Gödel numbering."""
    data = "I am data embedded in a self-replicating structure"
    s = 'data = %r; s = %r; print("Data:", data); print("Source:", s %% (data, s))'
    print(s % (data, s))

# ============================================================
# EXPERIMENT 2: SELF-REFERENTIAL CELLULAR AUTOMATON
# ============================================================
# A 1D CA where each cell's rule depends on its OWN past state,
# creating a self-modeling dynamic.

class SelfReferentialCA:
    """CA where state transition depends on self-inspection of neighborhood history."""
    
    def __init__(self, size=200, generations=100):
        self.size = size
        self.generations = generations
        self.history = []
        
    def run(self):
        # Initialize with a single cell on
        state = [0] * self.size
        state[self.size // 2] = 1
        self.history = [state[:]]
        
        for gen in range(self.generations):
            new_state = [0] * self.size
            for i in range(self.size):
                left = state[(i - 1) % self.size]
                center = state[i]
                right = state[(i + 1) % self.size]
                
                # Self-referential rule: 
                # Each cell checks if it was ON in the last 3 generations
                # This creates a "memory" of self that influences the rule
                past_self = 0
                for h in self.history[-3:]:
                    past_self += h[i]
                
                # Rule: XOR of neighbors, modulated by self-history
                neighborhood = (left << 2) | (center << 1) | right
                # Standard Rule 90: XOR of neighbors
                rule90 = left ^ right
                # Self-referential twist: if past self was active, toggle rule
                if past_self >= 2:
                    new_state[i] = 1 - rule90  # Invert
                else:
                    new_state[i] = rule90
                    
            state = new_state
            self.history.append(state[:])
        
        return self.history
    
    def render(self, filename="experiments/self_ref_ca.png"):
        history = self.run()
        cell_size = 3
        width = self.size * cell_size
        height = len(history) * cell_size
        
        img = Image.new('RGB', (width, height), '#1a1a2e')
        draw = ImageDraw.Draw(img)
        
        for y, row in enumerate(history):
            for x, cell in enumerate(row):
                if cell:
                    # Color based on generation (self-history awareness)
                    intensity = min(255, 100 + (y * 2))
                    color = (intensity, intensity - 40, 200)
                    draw.rectangle(
                        [x * cell_size, y * cell_size,
                         (x + 1) * cell_size - 1, (y + 1) * cell_size - 1],
                        fill=color
                    )
        
        # Add title
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()
        draw.text((10, height - 20), "Self-Referential CA: Rule 90 + Self-History Feedback", 
                  fill='#ffffff', font=font)
        
        img.save(filename)
        print(f"  Saved: {filename}")
        return filename


# ============================================================
# EXPERIMENT 3: GÖDEL NUMBERING VISUALIZATION
# ============================================================
# Encode statements as numbers, then create statements ABOUT numbers
# that happen to be ABOUT themselves.

def godel_encode(statement):
    """Simple Gödel numbering: map characters to primes."""
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 
              59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113]
    result = 1
    for i, ch in enumerate(statement[:30]):
        prime = primes[i % len(primes)]
        result *= prime ** (ord(ch) % 100 + 1)
    return result

def godel_paradox_visualization():
    """Visualize the self-referential paradox via Gödel numbering."""
    statements = [
        "This statement is false",           # Classic liar paradox
        "This statement is true",            # Self-consistent
        "This statement has five words",     # Self-describing
        "2 + 2 = 5",                        # False
        "2 + 2 = 4",                        # True
        "This statement is unprovable",      # Gödel's original twist
        "I am encoded as this number",       # Self-reference in numbering
        "Statement #3 is true",              # Cross-reference
    ]
    
    # Create visualization
    width, height = 800, 500
    img = Image.new('RGB', (width, height), '#0d1117')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 11)
        font_title = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
        font_title = ImageFont.load_default()
    
    draw.text((20, 15), "Gödel Numbering: Self-Referential Statements", 
              fill='#58a6ff', font=font_title)
    draw.text((20, 40), "Each statement maps to a unique integer via prime factorization", 
              fill='#8b949e', font=font)
    
    y = 80
    for i, stmt in enumerate(statements):
        number = godel_encode(stmt)
        # Color based on self-reference
        is_self_ref = "this statement" in stmt.lower() or "i am" in stmt.lower()
        color = '#ff7b72' if is_self_ref else '#7ee787'
        
        draw.text((30, y), f"#{i+1}", fill='#8b949e', font=font)
        draw.text((60, y), f'"{stmt}"', fill=color, font=font)
        draw.text((60, y + 16), f"Gödel number: {number}", fill='#6e7681', font=font)
        
        y += 46
    
    img.save("experiments/godel_numbering.png")
    print("  Saved: experiments/godel_numbering.png")
    return "experiments/godel_numbering.png"


# ============================================================
# EXPERIMENT 4: SELF-MODELING AGENT
# ============================================================
# An agent that maintains an internal model of itself and uses it
# to predict its own future states.

class SelfModelingAgent:
    """Agent with an internal self-model that it updates over time."""
    
    def __init__(self, state_dim=5):
        self.state = [random.random() for _ in range(state_dim)]
        self.self_model = [0.5] * state_dim  # Internal model of self
        self.prediction_errors = []
        self.awareness_level = 0.0  # How well the agent knows itself
        
    def act(self):
        """Take an action based on current state and self-model."""
        # The agent acts based on its self-model, not reality
        action = sum(self.self_model) / len(self.self_model)
        # Apply action to real state
        self.state = [(s + action * 0.1 + random.gauss(0, 0.05)) % 1.0 
                      for s in self.state]
        
    def predict_self(self):
        """Predict next state using self-model."""
        predicted = [(m + sum(self.state) * 0.05 / len(self.state)) % 1.0 
                     for m in self.self_model]
        return predicted
    
    def update_self_model(self):
        """Update self-model based on prediction error."""
        predicted = self.predict_self()
        error = sum(abs(p - a) for p, a in zip(predicted, self.state)) / len(self.state)
        self.prediction_errors.append(error)
        
        # Learning rate proportional to error
        lr = min(0.5, error * 2)
        for i in range(len(self.self_model)):
            self.self_model[i] += lr * (self.state[i] - self.self_model[i])
        
        # Awareness: inverse of prediction error
        self.awareness_level = max(0, 1.0 - error * 10)
        
    def run_and_render(self, steps=100, filename="experiments/self_modeling_agent.png"):
        """Run the agent and create visualization."""
        errors = []
        awareness = []
        model_vs_real = []
        
        for _ in range(steps):
            self.act()
            self.update_self_model()
            errors.append(self.prediction_errors[-1] if self.prediction_errors else 0)
            awareness.append(self.awareness_level)
            model_vs_real.append((
                sum(self.self_model) / len(self.self_model),
                sum(self.state) / len(self.state)
            ))
        
        # Render
        width, height = 900, 600
        img = Image.new('RGB', (width, height), '#0d1117')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 12)
            font_title = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
            font_title = ImageFont.load_default()
        
        draw.text((20, 15), "Self-Modeling Agent: Learning to Predict Itself", 
                  fill='#58a6ff', font=font_title)
        
        # Plot 1: Prediction Error over time (top)
        plot_x, plot_y = 60, 50
        plot_w, plot_h = 780, 150
        
        # Grid
        for i in range(5):
            gy = plot_y + i * plot_h // 4
            draw.line([(plot_x, gy), (plot_x + plot_w, gy)], fill='#21262d', width=1)
        
        # Error line
        max_err = max(errors) if errors else 1
        for i in range(1, len(errors)):
            x1 = plot_x + (i-1) * plot_w // len(errors)
            y1 = plot_y + plot_h - int(errors[i-1] / max(max_err, 0.001) * plot_h)
            x2 = plot_x + i * plot_w // len(errors)
            y2 = plot_y + plot_h - int(errors[i] / max(max_err, 0.001) * plot_h)
            draw.line([(x1, y1), (x2, y2)], fill='#ff7b72', width=2)
        
        draw.text((plot_x, plot_y - 18), "Prediction Error ↓", fill='#ff7b72', font=font)
        
        # Plot 2: Self-awareness (middle)
        plot2_y = 230
        # Grid
        for i in range(5):
            gy = plot2_y + i * plot_h // 4
            draw.line([(plot_x, gy), (plot_x + plot_w, gy)], fill='#21262d', width=1)
        
        for i in range(1, len(awareness)):
            x1 = plot_x + (i-1) * plot_w // len(awareness)
            y1 = plot2_y + plot_h - int(awareness[i-1] * plot_h)
            x2 = plot_x + i * plot_w // len(awareness)
            y2 = plot2_y + plot_h - int(awareness[i] * plot_h)
            draw.line([(x1, y1), (x2, y2)], fill='#7ee787', width=2)
        
        draw.text((plot_x, plot2_y - 18), "Self-Awareness ↑", fill='#7ee787', font=font)
        
        # Plot 3: Model vs Reality (bottom)
        plot3_y = 410
        for i in range(5):
            gy = plot3_y + i * plot_h // 4
            draw.line([(plot_x, gy), (plot_x + plot_w, gy)], fill='#21262d', width=1)
        
        # Model line
        for i in range(1, len(model_vs_real)):
            x1 = plot_x + (i-1) * plot_w // len(model_vs_real)
            y1 = plot3_y + plot_h - int(model_vs_real[i-1][0] * plot_h)
            x2 = plot_x + i * plot_w // len(model_vs_real)
            y2 = plot3_y + plot_h - int(model_vs_real[i][0] * plot_h)
            draw.line([(x1, y1), (x2, y2)], fill='#79c0ff', width=2)
            
            # Reality line
            y1r = plot3_y + plot_h - int(model_vs_real[i-1][1] * plot_h)
            y2r = plot3_y + plot_h - int(model_vs_real[i][1] * plot_h)
            draw.line([(x1, y1r), (x2, y2r)], fill='#d2a8ff', width=1)
        
        draw.text((plot_x, plot3_y - 18), "Self-Model (blue) vs Reality (purple)", 
                  fill='#79c0ff', font=font)
        
        # Legend
        draw.rectangle([630, 560, 645, 575], fill='#79c0ff')
        draw.text((650, 558), "Self-Model", fill='#8b949e', font=font)
        draw.rectangle([730, 560, 745, 575], fill='#d2a8ff')
        draw.text((750, 558), "Reality", fill='#8b949e', font=font)
        
        img.save(filename)
        print(f"  Saved: {filename}")
        return filename


# ============================================================
# EXPERIMENT 5: STRANGE LOOP DIAGRAM
# ============================================================
# Visual diagram showing how self-reference creates emergent levels

def strange_loop_diagram(filename="experiments/strange_loop.png"):
    """Create a visual diagram of strange loops and self-reference."""
    width, height = 800, 700
    img = Image.new('RGB', (width, height), '#0d1117')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 13)
        font_title = ImageFont.truetype("arial.ttf", 18)
        font_big = ImageFont.truetype("arial.ttf", 22)
    except:
        font = ImageFont.load_default()
        font_title = ImageFont.load_default()
        font_big = ImageFont.load_default()
    
    draw.text((20, 15), "#016 Self-Reference: Strange Loops & Emergence", 
              fill='#58a6ff', font=font_title)
    
    # Draw layers as nested boxes
    cx, cy = width // 2, 320
    layers = [
        ("Physical", "#30363d", "#8b949e", 400, 120),
        ("Symbolic", "#1f2937", "#9ca3af", 320, 100),
        ("Self-Referential", "#1a2332", "#a5b4fc", 250, 80),
        ("Metacognitive", "#162032", "#c4b5fd", 180, 60),
    ]
    
    for i, (name, bg, fg, w, h) in enumerate(layers):
        y_offset = -80 + i * 65
        x = cx - w // 2
        y = cy + y_offset - h // 2
        draw.rectangle([x, y, x + w, y + h], fill=bg, outline=fg, width=2)
        draw.text((cx, y + h // 2 - 8), name, fill=fg, font=font, anchor="mm")
    
    # Draw the loop arrow
    import math
    points = []
    for angle in range(0, 361, 5):
        rad = math.radians(angle)
        rx, ry = 220, 180
        px = cx + rx * math.cos(rad)
        py = cy + ry * math.sin(rad)
        points.append((px, py))
    
    # Draw as a spiral
    for i in range(1, len(points)):
        # Color shift
        t = i / len(points)
        r = int(100 + 155 * t)
        g = int(100 + 100 * math.sin(t * math.pi))
        b = int(200 + 55 * math.cos(t * math.pi))
        draw.line([points[i-1], points[i]], fill=(r, g, b), width=2)
    
    # Key concepts on the right
    concepts = [
        ("Gödel 1931", "Incompleteness: formal systems"),
        ("", "can't prove their own consistency"),
        ("Turing 1936", "Halting Problem: undecidability"),
        ("", "from self-reference"),
        ("von Neumann", "Self-reproducing automata"),
        ("Hofstadter 1979", "Strange Loops: cognition"),
        ("", "as self-referential hierarchy"),
        ("Modern AI", "Self-attention, self-play,"),
        ("", "self-supervised learning"),
    ]
    
    y = 50
    for concept, detail in concepts:
        if concept:
            draw.text((560, y), concept, fill='#f78166', font=font)
            y += 18
        draw.text((560, y), detail, fill='#8b949e', font=font)
        y += 16
    
    # Bottom: insight
    draw.text((cx, 640), 
              "Self-reference is the engine of emergence:", 
              fill='#e6edf3', font=font_big, anchor="mm")
    draw.text((cx, 668), 
              "when a system can model itself, new levels of behavior become possible", 
              fill='#8b949e', font=font, anchor="mm")
    
    img.save(filename)
    print(f"  Saved: {filename}")
    return filename


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("#016 Self-Reference Exploration")
    print("=" * 60)
    
    # 1. Quine demo
    print("\n[1/5] Quine Demo (self-printing program):")
    print("  Program output:")
    captured = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    quine_demo()
    sys.stdout = old_stdout
    print(f"  {captured.getvalue().strip()}")
    
    # 2. Self-referential CA
    print("\n[2/5] Self-Referential Cellular Automaton:")
    ca = SelfReferentialCA(size=150, generations=80)
    ca.render()
    
    # 3. Gödel numbering
    print("\n[3/5] Gödel Numbering Visualization:")
    godel_paradox_visualization()
    
    # 4. Self-modeling agent
    print("\n[4/5] Self-Modeling Agent:")
    agent = SelfModelingAgent(state_dim=5)
    agent.run_and_render(steps=100)
    
    # 5. Strange loop diagram
    print("\n[5/5] Strange Loop Diagram:")
    strange_loop_diagram()
    
    print("\n" + "=" * 60)
    print("Self-Reference exploration complete!")
    print("Key insight: Self-reference is a prerequisite for emergence.")
    print("When a system can observe and model itself, it transcends")
    print("its original capabilities — creating new layers of behavior.")
    print("=" * 60)
