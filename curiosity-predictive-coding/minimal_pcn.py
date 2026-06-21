"""
minimal_pcn.py — Minimal Predictive Coding Network from scratch (NumPy)

Shows the core idea:
  1. Each layer predicts the activity of the layer below
  2. Prediction error drives updates to layer activities (inference)
  3. After inference converges, weights update to predict better (learning)

Architecture: input → hidden → top (generative, predictions flow downward)
No PyTorch, no backpropagation — just iterative inference + Hebbian-like weight updates.

Ref: Rao & Ballard (1999), Friston (2005), Bogacz (2017)
"""

import numpy as np


class MinimalPCN:
    """A 2-layer predictive coding network.

    Layers: 0 (input, observed), 1 (hidden, inferred), 2 (top, prior/prediction)

    During inference:
      - Top generates prediction for hidden
      - Hidden generates prediction for input
      - Prediction errors at both levels drive activity updates
    """

    def __init__(self, n_input, n_hidden, n_top=16, dt=0.1, activation="tanh"):
        self.n_input = n_input
        self.n_hidden = n_hidden
        self.n_top = n_top
        self.dt = dt  # integration step for inference

        # Weight matrices (top → hidden, hidden → input)
        rng = np.random.RandomState(42)
        scale_h = np.sqrt(2.0 / n_top)
        scale_i = np.sqrt(2.0 / n_hidden)
        self.W_th = rng.randn(n_hidden, n_top) * scale_h  # top→hidden
        self.W_hi = rng.randn(n_input, n_hidden) * scale_i  # hidden→input

        # Biases
        self.b_h = np.zeros(n_hidden)
        self.b_i = np.zeros(n_input)

        # Precision (inverse variance) — how much we trust predictions vs data
        self.pi_h = 1.0  # precision of hidden prediction error
        self.pi_i = 1.0  # precision of input prediction error

        # State
        self.x_input = np.zeros(n_input)
        self.x_hidden = np.zeros(n_hidden)
        self.x_top = np.zeros(n_top)

        self.activation = activation

    def _act(self, x):
        if self.activation == "tanh":
            return np.tanh(x)
        elif self.activation == "relu":
            return np.maximum(0, x)
        elif self.activation == "sigmoid":
            return 1.0 / (1.0 + np.exp(-x))
        return x

    def _act_prime(self, x):
        """Derivative of activation."""
        if self.activation == "tanh":
            t = np.tanh(x)
            return 1.0 - t ** 2
        elif self.activation == "relu":
            return (x > 0).astype(float)
        elif self.activation == "sigmoid":
            s = 1.0 / (1.0 + np.exp(-x))
            return s * (1.0 - s)
        return np.ones_like(x)

    def infer(self, input_data, n_steps=50, top_prior=None):
        """Run inference to find hidden activities that explain the input.

        Args:
          input_data: observed input (n_input,)
          n_steps: number of inference steps
          top_prior: optional prior for top layer activities

        Returns:
          free_energy_history: list of free energy values over time
        """
        self.x_input = input_data.copy()
        self.x_hidden = np.random.randn(self.n_hidden) * 0.1

        if top_prior is not None:
            self.x_top = top_prior.copy()
        else:
            self.x_top = np.zeros(self.n_top)

        fe_history = []

        for step in range(n_steps):
            # --- Prediction errors ---
            # Hidden layer reconstructs input
            pred_input = self.W_hi @ self._act(self.x_hidden) + self.b_i
            err_input = self.x_input - pred_input  # ε_i

            # Top layer predicts hidden
            pred_hidden = self.W_th @ self._act(self.x_top) + self.b_h
            err_hidden = self._act(self.x_hidden) - pred_hidden  # ε_h

            # --- Update hidden activities (inference) ---
            # Gradient of free energy w.r.t. hidden activities
            # dF/dx_h = -W_hi^T * ε_i * pi_i * act'(x_h) + ε_h * pi_h * act'(x_h)
            dF_dxh = (
                -self.W_hi.T @ (err_input * self.pi_i) * self._act_prime(self.x_hidden)
                + err_hidden * self.pi_h * self._act_prime(self.x_hidden)
            )

            self.x_hidden -= self.dt * dF_dxh

            # --- Free energy (for monitoring) ---
            fe = 0.5 * self.pi_i * np.sum(err_input ** 2) + 0.5 * self.pi_h * np.sum(
                err_hidden ** 2
            )
            fe_history.append(fe)

        return fe_history

    def learn(self, lr=0.01):
        """Update weights to minimize free energy (after inference converges)."""
        # Recompute errors at equilibrium
        pred_input = self.W_hi @ self._act(self.x_hidden) + self.b_i
        err_input = self.x_input - pred_input

        pred_hidden = self.W_th @ self._act(self.x_top) + self.b_h
        err_hidden = self._act(self.x_hidden) - pred_hidden

        # Weight updates (negative gradient of F)
        # dF/dW_hi = -ε_i * act(x_h)^T (outer product)
        # dF/dW_th = -ε_h * act(x_top)^T
        dW_hi = -np.outer(err_input, self._act(self.x_hidden))
        dW_th = -np.outer(err_hidden, self._act(self.x_top))

        self.W_hi -= lr * dW_hi
        self.W_th -= lr * dW_th

        # Bias updates
        self.b_i -= lr * (-err_input)
        self.b_h -= lr * (-err_hidden)

    def generate(self, n_steps=20):
        """Generate a pattern by running inference from top-down prediction."""
        self.x_top = np.random.randn(self.n_top) * 0.5
        self.x_hidden = np.zeros(self.n_hidden)

        # Settle hidden and input
        for _ in range(n_steps):
            pred_hidden = self.W_th @ self._act(self.x_top) + self.b_h
            err_hidden = self._act(self.x_hidden) - pred_hidden
            self.x_hidden -= self.dt * err_hidden * self._act_prime(self.x_hidden)

        pred_input = self.W_hi @ self._act(self.x_hidden) + self.b_i
        return self._act(pred_input)


def demo():
    """Train MinimalPCN to reconstruct synthetic patterns."""
    np.random.seed(42)
    n_input = 20
    n_hidden = 8
    n_top = 4

    pcn = MinimalPCN(n_input, n_hidden, n_top, dt=0.1)
    n_patterns = 12
    n_epochs = 200

    # Create synthetic patterns: sparse binary vectors
    patterns = np.zeros((n_patterns, n_input))
    for i in range(n_patterns):
        active_idx = np.random.choice(n_input, size=5, replace=False)
        patterns[i, active_idx] = 1.0

    print(f"Training on {n_patterns} patterns x {n_epochs} epochs")
    print(f"Architecture: {n_input}→{n_hidden}→{n_top}")

    total_fes = []
    for epoch in range(n_epochs):
        epoch_fe = 0
        for p in range(n_patterns):
            fe_hist = pcn.infer(patterns[p], n_steps=30)
            pcn.learn(lr=0.02)
            epoch_fe += fe_hist[-1]
        total_fes.append(epoch_fe / n_patterns)

        if epoch % 40 == 0 or epoch == n_epochs - 1:
            print(f"  Epoch {epoch:3d}  avg free energy: {total_fes[-1]:.4f}")

    # Test: reconstruct a held-out pattern
    test_idx = np.random.randint(n_patterns)
    test_pattern = patterns[test_idx]
    pcn.infer(test_pattern, n_steps=50)
    reconstruction = pcn.generate(n_steps=30)

    # Visualize with Pillow
    try:
        from PIL import Image, ImageDraw, ImageFont

        W, H = 720, 480
        img = Image.new("RGB", (W, H), "white")
        draw = ImageDraw.Draw(img)

        # Title
        draw.text((20, 10), "Minimal Predictive Coding Network", fill="black")

        # Training curve
        draw.text((20, 40), f"Training {n_patterns} patterns, {n_epochs} epochs", fill="black")

        # Draw free energy curve
        draw.text((20, 70), "Free energy over training:", fill="black")
        margin = 20
        plot_w, plot_h = 320, 160
        px, py = 20, 100
        draw.rectangle([px, py, px + plot_w, py + plot_h], outline="gray")

        fe_array = np.array(total_fes)
        fe_min, fe_max = fe_array.min(), fe_array.max()
        fe_range = fe_max - fe_min if fe_max > fe_min else 1

        n_pts = len(fe_array)
        for i in range(n_pts - 1):
            x1 = px + int(i / n_pts * plot_w)
            y1 = py + plot_h - int((fe_array[i] - fe_min) / fe_range * (plot_h - 4)) - 2
            x2 = px + int((i + 1) / n_pts * plot_w)
            y2 = py + plot_h - int((fe_array[i + 1] - fe_min) / fe_range * (plot_h - 4)) - 2
            draw.line([x1, y1, x2, y2], fill="blue", width=2)

        draw.text((px + 5, py + plot_h + 5), f"Epochs", fill="black")
        draw.text((px + plot_w - 80, py - 15), f"FE: {fe_min:.2f}→{fe_max:.2f}", fill="gray")

        # Pattern vs reconstruction
        draw.text((400, 70), "Test pattern vs reconstruction:", fill="black")

        # Draw original pattern
        bar_w, bar_h = 12, 180
        x0, y0 = 400, 100
        for i in range(n_input):
            val = test_pattern[i]
            color = "blue" if val > 0.5 else "lightgray"
            draw.rectangle(
                [x0 + i * (bar_w + 2), y0 + (1 - val) * bar_h,
                 x0 + i * (bar_w + 2) + bar_w, y0 + bar_h],
                fill=color, outline="black",
            )
        draw.text((x0, y0 + bar_h + 8), "Original", fill="black")

        # Draw reconstruction
        y1 = y0 + bar_h + 30
        recolor = "red" if np.max(reconstruction) > 0 else "gray"
        for i in range(n_input):
            val = min(1.0, max(0, reconstruction[i]))
            color_h = int(200 - val * 200)
            color_r = "black"
            if val > 0.5:
                fill_c = (int(255 * val), 50, 50)
            else:
                fill_c = (200, 200, 200)
            draw.rectangle(
                [x0 + i * (bar_w + 2), y1 + (1 - val) * bar_h,
                 x0 + i * (bar_w + 2) + bar_w, y1 + bar_h],
                fill=fill_c, outline="black",
            )
        draw.text((x0, y1 + bar_h + 8), "Reconstruction", fill="black")

        # Algorithm explanation
        draw.text((20, 320), "How it works:", fill="black", font=None)
        draw.text((20, 345), "1. Input clamped at bottom layer", fill="gray")
        draw.text((20, 365), "2. Hidden activities iterate to minimize prediction error", fill="gray")
        draw.text((20, 385), "3. Top-down predictions generate expectations", fill="gray")
        draw.text((20, 405), "4. Bottom-up errors drive activity updates", fill="gray")
        draw.text((20, 425), "5. Weights learn to predict better over time", fill="gray")

        draw.text((40, 450), "No backpropagation — just inference + Hebbian-like learning", fill="gray")

        img.save("C:\\Users\\许耀仁\\.openclaw\\workspace\\curiosity-predictive-coding\\pcn_demo.png")
        print("Saved pcn_demo.png")
    except ImportError:
        print("Pillow not available for visualization")

    print("\nDone! PCN learned to reconstruct patterns through iterative inference.")
    print(f"Final avg free energy: {total_fes[-1]:.4f}")


if __name__ == "__main__":
    demo()
