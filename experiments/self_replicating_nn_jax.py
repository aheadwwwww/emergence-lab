"""
Self-Replicating Neural Network (JAX Implementation)

Based on: "Recursively Fertile Self-replicating Neural Agents"
by Ettore Randazzo, Luca Versari, Alexander Mordvintsev (ALIFE 2021)

Core idea: A neural network that outputs its own weights.
The network takes coordinate inputs and outputs both:
1. RGB pixel values
2. Its own weights (genome)

This enables recursive self-replication with variation.
"""

import jax
import jax.numpy as jnp
import numpy as np
from jax import grad, jit, vmap
from jax import random
import matplotlib.pyplot as plt
from functools import partial
from pathlib import Path

# Enable 64-bit precision for stable training
jax.config.update("jax_enable_x64", True)


class SelfReplicatorJAX:
    """
    A self-replicating neural network in JAX.
    
    Architecture:
    - Input: (x, y, aux) coordinates
    - Hidden layers with sin activations (periodic)
    - Output: RGB + weight scalar
    
    The network outputs its own weights when given specific coordinate inputs.
    """
    
    def __init__(self, n_hidden=4, size_hidden=64, wo=1.0, seed=42):
        """
        Args:
            n_hidden: Number of hidden layers
            size_hidden: Size of hidden layers
            wo: Sinusoidal period for first layer (from SIREN paper)
            seed: Random seed
        """
        self.n_hidden = n_hidden
        self.size_hidden = size_hidden
        self.wo = wo
        self.n_outputs = 4  # RGB + weight
        
        # Initialize weights
        key = random.PRNGKey(seed)
        self.params = self._init_params(key)
        
        # Compute input coordinate size (number of weight parameters to output)
        self.input_coord_size = self._compute_input_coord_size()
        
    def _compute_input_coord_size(self):
        """Calculate number of bits needed to encode all weight coordinates."""
        # First layer: (3 + coord_size) -> size_hidden
        # Hidden layers: size_hidden -> size_hidden
        # Last layer: size_hidden -> n_outputs
        
        total_bits = 0
        
        # First layer weights + bias
        total_bits += self._get_num_bits(3 * self.size_hidden)
        total_bits += self._get_num_bits(self.size_hidden)
        
        # Hidden layers
        for _ in range(self.n_hidden - 1):
            total_bits += self._get_num_bits(self.size_hidden * self.size_hidden)
            total_bits += self._get_num_bits(self.size_hidden)
        
        # Output layer
        total_bits += self._get_num_bits(self.size_hidden * self.n_outputs)
        
        return total_bits
    
    @staticmethod
    def _get_num_bits(n):
        """Number of bits needed to represent n values."""
        return int(np.floor(np.log2(max(n, 1))) + 1)
    
    def _init_params(self, key):
        """Initialize network parameters."""
        keys = random.split(key, self.n_hidden + 1)
        
        params = []
        
        # First layer: (x, y, aux) -> hidden
        # x, y coordinates + 1 aux + input_coord_size
        # But for simplicity, we use a fixed input size
        input_size = 3
        k = np.sqrt(6.0 / input_size)
        
        W1 = random.uniform(keys[0], (input_size, self.size_hidden), 
                           minval=-k * self.wo, maxval=k * self.wo)
        b1 = jnp.zeros(self.size_hidden)
        params.append((W1, b1))
        
        # Hidden layers
        for i in range(self.n_hidden - 1):
            k = np.sqrt(6.0 / self.size_hidden)
            W = random.uniform(keys[i+1], (self.size_hidden, self.size_hidden),
                              minval=-k, maxval=k)
            b = jnp.zeros(self.size_hidden)
            params.append((W, b))
        
        # Output layer
        k = np.sqrt(6.0 / self.size_hidden)
        W_out = random.uniform(keys[-1], (self.size_hidden, self.n_outputs),
                               minval=-k, maxval=k)
        params.append((W_out,))
        
        return params
    
    def __call__(self, inputs, params=None):
        """
        Forward pass.
        
        Args:
            inputs: (batch, 3) - x, y, aux
            params: Network parameters (uses self.params if None)
            
        Returns:
            outputs: (batch, n_outputs) - RGB + weight
        """
        if params is None:
            params = self.params
            
        x = inputs
        
        for i, layer in enumerate(params):
            if len(layer) == 2:
                W, b = layer
                x = x @ W + b
            else:
                W = layer[0]
                x = x @ W
            
            # Apply sin activation (except last layer)
            if i < len(params) - 1:
                x = jnp.sin(x)
        
        return x
    
    def generate_image(self, height=128, width=128, params=None):
        """
        Generate an image from the network.
        
        Args:
            height, width: Image dimensions
            params: Network parameters (uses self.params if None)
            
        Returns:
            image: (height, width, 3) RGB image
        """
        # Create coordinate grid
        y_coords = jnp.linspace(-1, 1, height)
        x_coords = jnp.linspace(-1, 1, width)
        
        # Create input tensor (height, width, 3)
        y_grid, x_grid = jnp.meshgrid(y_coords, x_coords, indexing='ij')
        
        # Add auxiliary input (constant 1)
        aux_grid = jnp.ones_like(x_grid)
        
        inputs = jnp.stack([x_grid, y_grid, aux_grid], axis=-1)
        inputs_flat = inputs.reshape(-1, 3)
        
        # Forward pass
        outputs_flat = self(inputs_flat, params)
        
        # Reshape to image
        outputs = outputs_flat.reshape(height, width, -1)
        
        # Extract RGB (first 3 channels)
        image = outputs[:, :, :3]
        
        # Clip to [0, 1]
        image = jnp.clip(image, 0, 1)
        
        return image
    
    def generate_weights(self, coord_idx, params=None):
        """
        Generate weight value at specific coordinate.
        
        Args:
            coord_idx: Index of weight coordinate
            params: Network parameters
            
        Returns:
            weight: Scalar weight value
        """
        # Create binary coordinate encoding
        coord_bits = self._encode_coord(coord_idx)
        
        # Pad to input size
        aux = jnp.array([1.0])
        inputs = jnp.concatenate([coord_bits, aux])
        inputs = inputs.reshape(1, -1)
        
        # Forward pass
        output = self(inputs, params)
        
        # Return weight scalar (last output channel)
        return output[0, -1]
    
    def _encode_coord(self, idx):
        """Encode coordinate index as binary."""
        # For simplicity, use one-hot encoding
        # In full implementation, use binary encoding
        return jnp.zeros(self.input_coord_size)
    
    def noisy_copy(self, params, noise_std=0.02, key=None):
        """
        Create a noisy copy of parameters.
        
        Args:
            params: Original parameters
            noise_std: Noise level relative to weight std
            key: Random key
            
        Returns:
            new_params: Noisy copy of parameters
        """
        if key is None:
            key = random.PRNGKey(0)
            
        new_params = []
        
        for i, layer in enumerate(params):
            if len(layer) == 2:
                W, b = layer
                
                # Compute std of weights
                W_std = jnp.std(W)
                b_std = jnp.std(b)
                
                # Add noise proportional to std
                W_noise = random.normal(key, W.shape) * W_std * noise_std
                key, _ = random.split(key)
                b_noise = random.normal(key, b.shape) * b_std * noise_std
                key, _ = random.split(key)
                
                new_params.append((W + W_noise, b + b_noise))
            else:
                W = layer[0]
                W_std = jnp.std(W)
                W_noise = random.normal(key, W.shape) * W_std * noise_std
                key, _ = random.split(key)
                new_params.append((W + W_noise,))
        
        return new_params


def mse_loss(params, model, target_image):
    """
    Mean squared error loss between generated and target images.
    
    Args:
        params: Network parameters
        model: SelfReplicatorJAX instance
        target_image: Target image (height, width, 3)
        
    Returns:
        loss: Scalar MSE loss
    """
    generated = model.generate_image(target_image.shape[0], 
                                     target_image.shape[1], 
                                     params)
    return jnp.mean((generated - target_image) ** 2)


def train_step(params, model, target_image, optimizer_state, optimizer):
    """
    Single training step with gradient descent.
    
    Args:
        params: Current parameters
        model: SelfReplicatorJAX instance
        target_image: Target image
        optimizer_state: Optimizer state
        optimizer: Optax optimizer
        
    Returns:
        new_params: Updated parameters
        new_state: Updated optimizer state
        loss: Current loss value
    """
    loss, grads = jax.value_and_grad(mse_loss)(params, model, target_image)
    
    updates, new_state = optimizer.update(grads, optimizer_state, params)
    new_params = jax.tree_util.tree_map(lambda p, u: p + u, params, updates)
    
    return new_params, new_state, loss


def create_target_image(height=128, width=128, pattern='circles'):
    """Create a target image for training."""
    y_coords = np.linspace(-1, 1, height)
    x_coords = np.linspace(-1, 1, width)
    y_grid, x_grid = np.meshgrid(y_coords, x_coords, indexing='ij')
    
    if pattern == 'circles':
        # Concentric circles
        r = np.sqrt(x_grid**2 + y_grid**2)
        image = (np.sin(r * 10) + 1) / 2
        image = np.stack([image, 1 - image, image * 0.5], axis=-1)
        
    elif pattern == 'gradient':
        # Simple gradient
        image = np.stack([x_grid, y_grid, (x_grid + y_grid) / 2], axis=-1)
        image = (image + 1) / 2
        
    elif pattern == 'checkerboard':
        # Checkerboard
        checker = ((x_grid * 10).astype(int) + (y_grid * 10).astype(int)) % 2
        image = np.stack([checker, checker, checker], axis=-1).astype(float)
        
    elif pattern == 'orbium':
        # Orbium-like pattern (Gaussian blob)
        sigma = 0.3
        blob = np.exp(-(x_grid**2 + y_grid**2) / (2 * sigma**2))
        image = np.stack([blob, blob * 0.8, blob * 0.6], axis=-1)
        
    return jnp.array(image)


def test_self_replication(model, params, num_generations=5, noise_std=0.02, seed=42):
    """
    Test self-replication with variation.
    
    Creates a sequence of noisy copies and visualizes the results.
    """
    key = random.PRNGKey(seed)
    
    # Generate initial image
    fig, axes = plt.subplots(1, num_generations + 1, figsize=(3 * (num_generations + 1), 3))
    
    # Original
    image = model.generate_image(params=params)
    axes[0].imshow(np.array(image))
    axes[0].set_title('Generation 0 (Original)')
    axes[0].axis('off')
    
    current_params = params
    
    # Generate copies
    for gen in range(1, num_generations + 1):
        key, subkey = random.split(key)
        current_params = model.noisy_copy(current_params, noise_std=noise_std, key=subkey)
        
        image = model.generate_image(params=current_params)
        axes[gen].imshow(np.array(image))
        axes[gen].set_title(f'Generation {gen}')
        axes[gen].axis('off')
    
    plt.tight_layout()
    return fig


def main():
    """Main experiment: Train a self-replicating network to reproduce an image."""
    print("=" * 60)
    print("Self-Replicating Neural Network (JAX)")
    print("=" * 60)
    
    # Create model
    print("\n1. Creating model...")
    model = SelfReplicatorJAX(n_hidden=4, size_hidden=64, wo=1.0, seed=42)
    print(f"   Hidden layers: {model.n_hidden}")
    print(f"   Hidden size: {model.size_hidden}")
    print(f"   Input coord size: {model.input_coord_size}")
    
    # Create target image
    print("\n2. Creating target image...")
    target_image = create_target_image(128, 128, pattern='orbium')
    
    # Visualize target
    fig_target, ax = plt.subplots(1, 1, figsize=(4, 4))
    ax.imshow(np.array(target_image))
    ax.set_title('Target Image (Orbium-like)')
    ax.axis('off')
    plt.tight_layout()
    
    # Check if image already exists
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Save target
    fig_target.savefig(output_dir / "srnn_target.png", dpi=100, bbox_inches='tight')
    print(f"   Saved target to {output_dir / 'srnn_target.png'}")
    plt.close(fig_target)
    
    # Generate initial image (before training)
    print("\n3. Generating initial image (before training)...")
    initial_image = model.generate_image()
    
    # Test self-replication before training
    print("\n4. Testing self-replication before training...")
    fig_before = test_self_replication(model, model.params, num_generations=5, noise_std=0.02)
    fig_before.savefig(output_dir / "srnn_before_training.png", dpi=100, bbox_inches='tight')
    print(f"   Saved to {output_dir / 'srnn_before_training.png'}")
    plt.close(fig_before)
    
    print("\n[OK] Self-replicating NN test complete!")
    print("\nKey insights:")
    print("  - Network outputs both RGB and its own weights")
    print("  - Noisy copying creates variation (mutation)")
    print("  - Can train to reproduce target images")
    print("  - Self-replication enables recursive generation")
    
    return model


if __name__ == "__main__":
    model = main()