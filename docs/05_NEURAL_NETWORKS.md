# Chapter 5: Neural Networks -- The Foundation of Deep Learning

## Introduction

Neural networks are the engine of modern AI. Every system that generates text (like ChatGPT), creates images (like Stable Diffusion), recognizes speech (like Siri), translates languages, plays games at superhuman levels, or generates 3D models is powered by some form of neural network. This chapter explains everything about neural networks from the ground up -- what they are, why they work, how every component functions, and how to build them yourself.

---

## Table of Contents

1. What Is a Neural Network?
2. The Biological Inspiration
3. The Perceptron -- The Simplest Neural Network
4. Activation Functions
5. Multi-Layer Perceptrons (MLPs)
6. Forward Propagation -- How a Network Makes Predictions
7. Loss Functions -- Measuring How Wrong the Network Is
8. Backpropagation -- How a Network Learns
9. Gradient Descent Variants
10. Building a Neural Network from Scratch in NumPy
11. Building Neural Networks with PyTorch
12. Common Layer Types
13. Weight Initialization
14. Batch Normalization
15. Dropout
16. Skip Connections (Residual Connections)
17. Network Architecture Design
18. Universal Approximation Theorem
19. Summary

---

## 1. What Is a Neural Network?

A neural network is a mathematical function -- nothing more, nothing less. It takes in numbers and produces numbers. What makes it special is that it has many adjustable parameters (weights and biases) that can be tuned so the function maps inputs to desired outputs.

Here is the simplest way to think about it:

```
Input (numbers)  -->  [Neural Network (parameters)]  -->  Output (numbers)

Example:
[pixel values of an image]  -->  [Neural Network]  -->  [probabilities: 90% cat, 8% dog, 2% bird]
[words of a sentence]       -->  [Neural Network]  -->  [next word]
[3D coordinates]            -->  [Neural Network]  -->  [occupancy: inside or outside an object]
```

The "learning" part is adjusting the parameters so the network produces the correct outputs for as many inputs as possible.

A modern large language model like GPT-4 has hundreds of billions of parameters. But the fundamental principles are the same as a network with 10 parameters. We start small and build up.

---

## 2. The Biological Inspiration

Neural networks are loosely inspired by the brain. The brain is made of roughly 86 billion neurons. Each neuron:

1. Receives electrical signals from other neurons through **dendrites**.
2. Processes those signals in the **cell body**.
3. If the total signal exceeds a threshold, it fires an electrical signal through its **axon**.
4. The signal is transmitted to other neurons through **synapses** (connections).

A single biological neuron does something roughly like this:
- Take in many input signals.
- Multiply each signal by a weight (the "strength" of the connection).
- Sum all weighted signals.
- If the sum exceeds a threshold, fire (output 1). Otherwise, do not fire (output 0).

This is exactly what an artificial neuron (perceptron) does. But do not take the analogy too far -- artificial neural networks are very different from real brains in important ways. They are mathematical models, not biological simulations.

---

## 3. The Perceptron -- The Simplest Neural Network

A perceptron is a single artificial neuron. It is the building block of all neural networks.

### How It Works

A perceptron takes multiple inputs, multiplies each by a weight, sums them, adds a bias, and applies an activation function:

$$\text{output} = f\left(\sum_{i=1}^{n} w_i x_i + b\right) = f(\mathbf{w} \cdot \mathbf{x} + b)$$

Where:
- $x_1, x_2, ..., x_n$ are the inputs
- $w_1, w_2, ..., w_n$ are the weights (one per input)
- $b$ is the bias
- $f$ is the activation function
- The output is a single number

Visually:

```
x1 --w1--\
x2 --w2---\
x3 --w3--->[ Sum + bias ]--->[ Activation f ]--->  output
...       /
xn --wn--/
```

### Implementation

```python
import numpy as np

class Perceptron:
    """A single neuron (perceptron) with step activation."""
    
    def __init__(self, n_inputs, learning_rate=0.01):
        # Initialize weights randomly (small values)
        self.weights = np.random.randn(n_inputs) * 0.01
        self.bias = 0.0
        self.learning_rate = learning_rate
    
    def forward(self, x):
        """Compute the output of the perceptron."""
        z = np.dot(x, self.weights) + self.bias
        return 1 if z > 0 else 0  # Step activation
    
    def train(self, X, y, n_epochs=100):
        """Train the perceptron using the perceptron learning rule."""
        for epoch in range(n_epochs):
            errors = 0
            for xi, yi in zip(X, y):
                prediction = self.forward(xi)
                error = yi - prediction
                
                # Update weights: move toward correct answer
                self.weights += self.learning_rate * error * xi
                self.bias += self.learning_rate * error
                
                errors += int(error != 0)
            
            if errors == 0:
                print(f"Converged at epoch {epoch}")
                break


# Example: Learning the AND function
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([0, 0, 0, 1])  # AND: only 1 when both inputs are 1

perceptron = Perceptron(n_inputs=2)
perceptron.train(X, y)

for xi in X:
    print(f"{xi} -> {perceptron.forward(xi)}")
```

### The XOR Problem

A single perceptron can only learn linearly separable functions (AND, OR, NOT). It fails on XOR:

```
XOR truth table:
0 XOR 0 = 0
0 XOR 1 = 1
1 XOR 0 = 1
1 XOR 1 = 0
```

No single straight line can separate the 1s from the 0s in this case. This limitation was famously pointed out by Minsky and Papert in 1969 and nearly killed neural network research for a decade. The solution: stack multiple layers of neurons. A two-layer network can learn XOR.

---

## 4. Activation Functions

Activation functions introduce non-linearity. Without them, stacking many layers of linear operations would still just produce a linear function -- no better than a single layer. The activation function is what gives neural networks the power to learn complex, non-linear patterns.

### Sigmoid

$$\sigma(z) = \frac{1}{1 + e^{-z}}$$

- Output range: (0, 1)
- Historically popular but has problems:
  - **Vanishing gradient**: For very large or very small $z$, the derivative is nearly zero, so gradients barely flow and learning stalls.
  - **Not zero-centered**: Outputs are always positive, which can make optimization harder.
- Used mainly in output layers for binary classification.

```python
def sigmoid(z):
    return 1 / (1 + np.exp(-z))

def sigmoid_derivative(z):
    s = sigmoid(z)
    return s * (1 - s)
```

### Tanh (Hyperbolic Tangent)

$$\tanh(z) = \frac{e^{z} - e^{-z}}{e^{z} + e^{-z}}$$

- Output range: (-1, 1)
- Zero-centered (better than sigmoid for hidden layers).
- Still suffers from vanishing gradients.

```python
def tanh(z):
    return np.tanh(z)

def tanh_derivative(z):
    return 1 - np.tanh(z) ** 2
```

### ReLU (Rectified Linear Unit)

$$\text{ReLU}(z) = \max(0, z)$$

- Output range: [0, infinity)
- The most widely used activation function in modern networks.
- Computationally simple and fast.
- Does not saturate for positive values (no vanishing gradient for z > 0).
- **Problem: Dead neurons**. If a neuron's input is always negative, it always outputs 0 and its gradient is always 0. It effectively "dies" and never learns.

```python
def relu(z):
    return np.maximum(0, z)

def relu_derivative(z):
    return (z > 0).astype(float)
```

### Leaky ReLU

$$\text{LeakyReLU}(z) = \begin{cases} z & \text{if } z > 0 \\ \alpha z & \text{if } z \leq 0 \end{cases}$$

Where $\alpha$ is a small constant (e.g., 0.01).

- Fixes the dead neuron problem by allowing a small gradient for negative values.

```python
def leaky_relu(z, alpha=0.01):
    return np.where(z > 0, z, alpha * z)
```

### GELU (Gaussian Error Linear Unit)

$$\text{GELU}(z) = z \cdot \Phi(z)$$

Where $\Phi$ is the cumulative distribution function of the standard normal distribution.

- Used in modern transformers (BERT, GPT).
- Smoother than ReLU.
- Can be approximated as: $\text{GELU}(z) \approx 0.5z(1 + \tanh[\sqrt{2/\pi}(z + 0.044715z^3)])$

### SiLU / Swish

$$\text{SiLU}(z) = z \cdot \sigma(z)$$

- Smooth, non-monotonic.
- Used in many modern architectures (EfficientNet, etc.).

### Softmax (for output layer with multiple classes)

$$\text{softmax}(z_i) = \frac{e^{z_i}}{\sum_{j} e^{z_j}}$$

- Converts raw scores into probabilities that sum to 1.
- Used only in the output layer for multi-class classification.

### Summary of When to Use What

| Activation | Where to Use | When |
|-----------|-------------|------|
| ReLU | Hidden layers | Default choice |
| Leaky ReLU | Hidden layers | When you see dead neurons |
| GELU | Hidden layers | Transformer architectures |
| SiLU / Swish | Hidden layers | Modern CNNs |
| Sigmoid | Output layer | Binary classification |
| Softmax | Output layer | Multi-class classification |
| Tanh | Hidden layers | RNNs (historically) |
| Linear (none) | Output layer | Regression |

---

## 5. Multi-Layer Perceptrons (MLPs)

An MLP (also called a "feed-forward neural network" or "fully connected network") is made of multiple layers of neurons, where each neuron in one layer is connected to every neuron in the next layer.

### Architecture

```
Input Layer          Hidden Layer 1        Hidden Layer 2        Output Layer
(n features)         (h1 neurons)          (h2 neurons)          (k outputs)

  x1 ----\          /---h1_1---\          /---h2_1---\          /--- o1
  x2 -----\--------/---h1_2----\--------/---h2_2----\--------/--- o2
  x3 -----/--------\---h1_3----/--------\---h2_3----/--------\--- o3
  x4 ----/          \---h1_4---/          \---h2_4---/
                                           
         Fully Connected      Fully Connected      Fully Connected
```

**Input layer**: One "neuron" per feature. These do not do any computation; they just pass the input values through.

**Hidden layers**: The layers between input and output. These are where the learning happens. Each neuron computes a weighted sum of its inputs, adds a bias, and applies an activation function.

**Output layer**: Produces the final prediction. The number of neurons depends on the task:
- Regression (predict one number): 1 neuron, no activation (or linear activation).
- Binary classification: 1 neuron with sigmoid activation.
- Multi-class classification (K classes): K neurons with softmax activation.

### The Math

For a network with one hidden layer:

**Layer 1 (input to hidden)**:
$$\mathbf{h} = f_1(\mathbf{W}_1 \mathbf{x} + \mathbf{b}_1)$$

**Layer 2 (hidden to output)**:
$$\mathbf{y} = f_2(\mathbf{W}_2 \mathbf{h} + \mathbf{b}_2)$$

Where:
- $\mathbf{x}$ is the input vector (shape: $n$)
- $\mathbf{W}_1$ is the weight matrix connecting input to hidden (shape: $h \times n$)
- $\mathbf{b}_1$ is the bias vector for the hidden layer (shape: $h$)
- $f_1$ is the activation function for the hidden layer (e.g., ReLU)
- $\mathbf{h}$ is the hidden layer output (shape: $h$)
- $\mathbf{W}_2$ is the weight matrix connecting hidden to output (shape: $k \times h$)
- $\mathbf{b}_2$ is the bias vector for the output layer (shape: $k$)
- $f_2$ is the activation function for the output layer (e.g., softmax)
- $\mathbf{y}$ is the output (shape: $k$)

---

## 6. Forward Propagation -- How a Network Makes Predictions

Forward propagation is the process of passing an input through the network to get an output. It is called "forward" because data flows forward from input to output.

### Step-by-Step Example

Consider a network with:
- 2 input features
- 1 hidden layer with 3 neurons (ReLU activation)
- 1 output neuron (sigmoid activation)

```python
import numpy as np

# Input
x = np.array([0.5, 0.8])  # 2 features

# Layer 1 weights and bias (2 inputs -> 3 hidden neurons)
W1 = np.array([
    [0.1, 0.4],    # Weights for hidden neuron 1
    [0.3, -0.2],   # Weights for hidden neuron 2
    [-0.5, 0.6]    # Weights for hidden neuron 3
])
b1 = np.array([0.1, -0.1, 0.2])

# Layer 2 weights and bias (3 hidden neurons -> 1 output)
W2 = np.array([[0.7, -0.3, 0.5]])
b2 = np.array([0.1])

# Forward pass
# Step 1: Hidden layer pre-activation
z1 = W1 @ x + b1  # Matrix multiplication + bias
# z1 = [0.1*0.5 + 0.4*0.8 + 0.1, 0.3*0.5 + (-0.2)*0.8 + (-0.1), (-0.5)*0.5 + 0.6*0.8 + 0.2]
# z1 = [0.47, -0.01, 0.43]

# Step 2: Hidden layer activation (ReLU)
h = np.maximum(0, z1)
# h = [0.47, 0.0, 0.43]  (the -0.01 becomes 0 due to ReLU)

# Step 3: Output layer pre-activation
z2 = W2 @ h + b2
# z2 = [0.7*0.47 + (-0.3)*0.0 + 0.5*0.43 + 0.1]
# z2 = [0.644]

# Step 4: Output layer activation (sigmoid)
output = 1 / (1 + np.exp(-z2))
# output = [0.656]

print(f"Prediction: {output[0]:.4f}")  # 65.6% probability of class 1
```

---

## 7. Loss Functions -- Measuring How Wrong the Network Is

The loss function tells us how far the network's predictions are from the correct answers. Training a neural network means finding the parameters that minimize this loss.

### Mean Squared Error (MSE) -- for Regression

$$\text{MSE} = \frac{1}{N} \sum_{i=1}^{N} (y_i - \hat{y}_i)^2$$

```python
import torch.nn as nn

criterion = nn.MSELoss()
loss = criterion(predictions, targets)
```

### Binary Cross-Entropy -- for Binary Classification

$$\text{BCE} = -\frac{1}{N} \sum_{i=1}^{N} [y_i \log(\hat{p}_i) + (1-y_i)\log(1-\hat{p}_i)]$$

```python
criterion = nn.BCELoss()           # Inputs must be probabilities (after sigmoid)
criterion = nn.BCEWithLogitsLoss() # Inputs are raw logits (sigmoid applied internally)
```

### Categorical Cross-Entropy -- for Multi-class Classification

$$\text{CCE} = -\frac{1}{N} \sum_{i=1}^{N} \sum_{k=1}^{K} y_{i,k} \log(\hat{p}_{i,k})$$

```python
criterion = nn.CrossEntropyLoss()  # Inputs are raw logits (softmax applied internally)
# Target should be class indices (not one-hot), e.g., [0, 2, 1, 5]
```

### Huber Loss -- Robust Regression

A combination of MSE and MAE. Behaves like MSE for small errors and like MAE for large errors. Less sensitive to outliers than MSE.

$$L_\delta(y, \hat{y}) = \begin{cases} \frac{1}{2}(y - \hat{y})^2 & \text{if } |y - \hat{y}| \leq \delta \\ \delta |y - \hat{y}| - \frac{1}{2}\delta^2 & \text{otherwise} \end{cases}$$

```python
criterion = nn.HuberLoss(delta=1.0)
```

---

## 8. Backpropagation -- How a Network Learns

Backpropagation is the algorithm that computes how much each parameter contributed to the loss, so we can adjust each parameter to reduce the loss. It is the core learning algorithm for neural networks.

### The Key Idea: The Chain Rule

Backpropagation is just the chain rule of calculus applied repeatedly.

If the output depends on the hidden layer, which depends on the weights:
$$\text{loss} = f(g(w))$$

Then by the chain rule:
$$\frac{\partial \text{loss}}{\partial w} = \frac{\partial \text{loss}}{\partial g} \cdot \frac{\partial g}{\partial w}$$

### Step-by-Step Example

Consider the same network from the forward propagation example. We will compute gradients for all parameters.

Given:
- Input: $x = [0.5, 0.8]$
- True label: $y = 1$
- Network produced: $\hat{y} = 0.656$
- Loss (BCE): $L = -[1 \cdot \log(0.656) + 0 \cdot \log(1 - 0.656)] = 0.422$

**Step 1: Gradient of loss with respect to output (before sigmoid)**

$$\frac{\partial L}{\partial z_2} = \hat{y} - y = 0.656 - 1 = -0.344$$

**Step 2: Gradient with respect to W2 and b2**

$$\frac{\partial L}{\partial W_2} = \frac{\partial L}{\partial z_2} \cdot h^T = -0.344 \times [0.47, 0.0, 0.43]$$

$$\frac{\partial L}{\partial b_2} = \frac{\partial L}{\partial z_2} = -0.344$$

**Step 3: Gradient flowing back to hidden layer**

$$\frac{\partial L}{\partial h} = W_2^T \cdot \frac{\partial L}{\partial z_2}$$

**Step 4: Gradient through ReLU activation**

$$\frac{\partial L}{\partial z_1} = \frac{\partial L}{\partial h} \odot \text{ReLU}'(z_1)$$

Where $\odot$ is element-wise multiplication and $\text{ReLU}'(z) = 1$ if $z > 0$, else $0$.

**Step 5: Gradient with respect to W1 and b1**

$$\frac{\partial L}{\partial W_1} = \frac{\partial L}{\partial z_1} \cdot x^T$$

$$\frac{\partial L}{\partial b_1} = \frac{\partial L}{\partial z_1}$$

**Step 6: Update all parameters**

$$W_1 \leftarrow W_1 - \alpha \cdot \frac{\partial L}{\partial W_1}$$
$$b_1 \leftarrow b_1 - \alpha \cdot \frac{\partial L}{\partial b_1}$$
$$W_2 \leftarrow W_2 - \alpha \cdot \frac{\partial L}{\partial W_2}$$
$$b_2 \leftarrow b_2 - \alpha \cdot \frac{\partial L}{\partial b_2}$$

### Why It Is Called "Back" Propagation

The gradients are computed backwards through the network:
1. First, compute the gradient at the output layer.
2. Then propagate it back to the last hidden layer.
3. Then propagate it back to the second-to-last hidden layer.
4. Continue until you reach the input layer.

This backward flow is what gives the algorithm its name.

### Automatic Differentiation in PyTorch

In practice, you never compute backpropagation by hand. PyTorch does it automatically:

```python
import torch
import torch.nn as nn

# Define a simple model
model = nn.Sequential(
    nn.Linear(2, 3),    # 2 inputs, 3 hidden neurons
    nn.ReLU(),
    nn.Linear(3, 1),    # 3 hidden, 1 output
    nn.Sigmoid()
)

# Forward pass
x = torch.tensor([[0.5, 0.8]], dtype=torch.float32)
y = torch.tensor([[1.0]], dtype=torch.float32)

prediction = model(x)

# Compute loss
criterion = nn.BCELoss()
loss = criterion(prediction, y)

# Backpropagation -- compute all gradients automatically
loss.backward()

# Now every parameter has a .grad attribute containing its gradient
for name, param in model.named_parameters():
    print(f"{name}: value={param.data}, gradient={param.grad}")
```

---

## 9. Gradient Descent Variants

### Batch Gradient Descent

Compute the gradient using the ENTIRE training set, then update parameters once.

```python
for epoch in range(n_epochs):
    predictions = model(X_train_all)
    loss = criterion(predictions, y_train_all)
    loss.backward()
    optimizer.step()
    optimizer.zero_grad()
```

- Pros: Stable gradient, guaranteed convergence direction.
- Cons: Very slow for large datasets (must process all data before one update).

### Stochastic Gradient Descent (SGD)

Compute the gradient using a SINGLE training example, then update parameters.

- Pros: Very fast updates, can escape local minima due to noise.
- Cons: Noisy gradients, unstable training.

### Mini-Batch Gradient Descent

Compute the gradient using a BATCH of training examples (e.g., 32 or 64).

This is what everyone uses in practice. It combines the stability of batch gradient descent with the speed of SGD.

```python
for epoch in range(n_epochs):
    for batch_X, batch_y in data_loader:  # data_loader yields batches
        predictions = model(batch_X)
        loss = criterion(predictions, batch_y)
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
```

### SGD with Momentum

Momentum accelerates SGD by remembering previous gradients. Think of a ball rolling down a hill -- it picks up speed.

$$v_t = \beta v_{t-1} + (1 - \beta) \nabla L$$
$$w_t = w_{t-1} - \alpha v_t$$

Where $\beta$ is the momentum coefficient (typically 0.9).

```python
optimizer = torch.optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
```

### Adam (Adaptive Moment Estimation)

Adam combines momentum with adaptive learning rates for each parameter. It is the most popular optimizer.

$$m_t = \beta_1 m_{t-1} + (1 - \beta_1) g_t$$
$$v_t = \beta_2 v_{t-1} + (1 - \beta_2) g_t^2$$
$$\hat{m}_t = \frac{m_t}{1 - \beta_1^t}, \quad \hat{v}_t = \frac{v_t}{1 - \beta_2^t}$$
$$w_t = w_{t-1} - \alpha \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon}$$

```python
optimizer = torch.optim.Adam(model.parameters(), lr=0.001, betas=(0.9, 0.999))
```

### AdamW (Adam with Weight Decay)

AdamW decouples weight decay from the gradient update, which leads to better generalization.

```python
optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)
```

### Learning Rate Schedulers

The learning rate often needs to change during training. Start high (fast learning) and decrease over time (fine-tuning).

```python
# Step decay: reduce LR by factor 0.1 every 30 epochs
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=30, gamma=0.1)

# Cosine annealing: smoothly decrease LR following a cosine curve
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=100)

# Reduce on plateau: reduce LR when validation loss stops improving
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode="min", factor=0.1, patience=10
)

# Warmup + cosine (commonly used in transformers)
from torch.optim.lr_scheduler import LambdaLR
import math

def warmup_cosine_schedule(step, warmup_steps=1000, total_steps=10000):
    if step < warmup_steps:
        return step / warmup_steps
    progress = (step - warmup_steps) / (total_steps - warmup_steps)
    return 0.5 * (1 + math.cos(math.pi * progress))

scheduler = LambdaLR(optimizer, lr_lambda=warmup_cosine_schedule)
```

---

## 10. Building a Neural Network from Scratch in NumPy

This is the most instructive exercise in all of deep learning. By implementing everything yourself, you'll understand every detail.

```python
import numpy as np

class NeuralNetwork:
    """
    A fully-connected neural network implemented entirely in NumPy.
    Supports arbitrary number of layers, ReLU/Sigmoid activations,
    and trains with mini-batch gradient descent.
    """
    
    def __init__(self, layer_sizes, learning_rate=0.01):
        """
        Initialize the network.
        
        Args:
            layer_sizes: List of integers defining the network architecture.
                         E.g., [784, 128, 64, 10] = 784 inputs, two hidden layers
                         of 128 and 64 neurons, and 10 outputs.
            learning_rate: Step size for gradient descent.
        """
        self.layer_sizes = layer_sizes
        self.learning_rate = learning_rate
        self.n_layers = len(layer_sizes) - 1
        
        # Initialize weights and biases using He initialization
        self.weights = []
        self.biases = []
        for i in range(self.n_layers):
            # He initialization: scale by sqrt(2 / fan_in)
            scale = np.sqrt(2.0 / layer_sizes[i])
            W = np.random.randn(layer_sizes[i + 1], layer_sizes[i]) * scale
            b = np.zeros((layer_sizes[i + 1], 1))
            self.weights.append(W)
            self.biases.append(b)
    
    def relu(self, z):
        """ReLU activation function."""
        return np.maximum(0, z)
    
    def relu_derivative(self, z):
        """Derivative of ReLU."""
        return (z > 0).astype(float)
    
    def softmax(self, z):
        """Softmax activation function (numerically stable)."""
        exp_z = np.exp(z - np.max(z, axis=0, keepdims=True))
        return exp_z / np.sum(exp_z, axis=0, keepdims=True)
    
    def forward(self, X):
        """
        Forward propagation.
        
        Args:
            X: Input data, shape (n_features, n_samples).
               Note: columns are samples (for easier matrix math).
        
        Returns:
            Output predictions, shape (n_outputs, n_samples).
        """
        self.activations = [X]  # Store for backpropagation
        self.pre_activations = []
        
        current = X
        for i in range(self.n_layers):
            z = self.weights[i] @ current + self.biases[i]
            self.pre_activations.append(z)
            
            if i == self.n_layers - 1:
                # Output layer: softmax
                current = self.softmax(z)
            else:
                # Hidden layers: ReLU
                current = self.relu(z)
            
            self.activations.append(current)
        
        return current
    
    def compute_loss(self, predictions, targets):
        """
        Compute cross-entropy loss.
        
        Args:
            predictions: Shape (n_classes, n_samples)
            targets: Shape (n_classes, n_samples) -- one-hot encoded
        """
        n_samples = targets.shape[1]
        epsilon = 1e-15
        loss = -np.sum(targets * np.log(predictions + epsilon)) / n_samples
        return loss
    
    def backward(self, targets):
        """
        Backpropagation: compute gradients for all weights and biases.
        
        Args:
            targets: One-hot encoded targets, shape (n_classes, n_samples).
        """
        n_samples = targets.shape[1]
        self.weight_gradients = []
        self.bias_gradients = []
        
        # Output layer gradient (softmax + cross-entropy combined)
        dz = self.activations[-1] - targets
        
        for i in range(self.n_layers - 1, -1, -1):
            # Gradient for weights and biases of this layer
            dW = (1 / n_samples) * dz @ self.activations[i].T
            db = (1 / n_samples) * np.sum(dz, axis=1, keepdims=True)
            
            self.weight_gradients.insert(0, dW)
            self.bias_gradients.insert(0, db)
            
            if i > 0:
                # Propagate gradient to previous layer
                dz = (self.weights[i].T @ dz) * self.relu_derivative(self.pre_activations[i - 1])
    
    def update_parameters(self):
        """Update weights and biases using gradient descent."""
        for i in range(self.n_layers):
            self.weights[i] -= self.learning_rate * self.weight_gradients[i]
            self.biases[i] -= self.learning_rate * self.bias_gradients[i]
    
    def train(self, X, y, n_epochs=100, batch_size=32, verbose=True):
        """
        Train the network.
        
        Args:
            X: Training data, shape (n_samples, n_features).
            y: Training labels, shape (n_samples,) -- integer class labels.
            n_epochs: Number of training epochs.
            batch_size: Number of samples per mini-batch.
            verbose: Whether to print progress.
        """
        n_samples = X.shape[0]
        n_classes = self.layer_sizes[-1]
        
        # Convert to one-hot
        y_onehot = np.zeros((n_samples, n_classes))
        y_onehot[np.arange(n_samples), y] = 1
        
        # Transpose for our column-vector convention
        X_T = X.T  # Shape: (n_features, n_samples)
        y_T = y_onehot.T  # Shape: (n_classes, n_samples)
        
        for epoch in range(n_epochs):
            # Shuffle data
            indices = np.random.permutation(n_samples)
            X_shuffled = X_T[:, indices]
            y_shuffled = y_T[:, indices]
            
            epoch_loss = 0
            n_batches = 0
            
            for start in range(0, n_samples, batch_size):
                end = min(start + batch_size, n_samples)
                X_batch = X_shuffled[:, start:end]
                y_batch = y_shuffled[:, start:end]
                
                # Forward pass
                predictions = self.forward(X_batch)
                
                # Compute loss
                loss = self.compute_loss(predictions, y_batch)
                epoch_loss += loss
                n_batches += 1
                
                # Backward pass
                self.backward(y_batch)
                
                # Update parameters
                self.update_parameters()
            
            if verbose and (epoch + 1) % 10 == 0:
                avg_loss = epoch_loss / n_batches
                accuracy = self.evaluate(X, y)
                print(f"Epoch {epoch+1}/{n_epochs}, Loss: {avg_loss:.4f}, Accuracy: {accuracy:.4f}")
    
    def predict(self, X):
        """Predict class labels for input data."""
        predictions = self.forward(X.T)
        return np.argmax(predictions, axis=0)
    
    def evaluate(self, X, y):
        """Compute accuracy on given data."""
        predictions = self.predict(X)
        return np.mean(predictions == y)


# Example: Train on MNIST-like data
from sklearn.datasets import load_digits

digits = load_digits()
X = digits.data / 16.0  # Normalize to [0, 1]
y = digits.target

# Split
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and train the network
# Architecture: 64 inputs -> 128 hidden -> 64 hidden -> 10 outputs
net = NeuralNetwork(layer_sizes=[64, 128, 64, 10], learning_rate=0.1)
net.train(X_train, y_train, n_epochs=100, batch_size=32)

# Evaluate
test_accuracy = net.evaluate(X_test, y_test)
print(f"\nTest Accuracy: {test_accuracy:.4f}")
```

---

## 11. Building Neural Networks with PyTorch

PyTorch is the most popular framework for building neural networks. It provides automatic differentiation, GPU support, and a huge library of pre-built layers.

### The Basics

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

# Check for GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Define a model using nn.Module
class SimpleClassifier(nn.Module):
    """A simple feed-forward classifier."""
    
    def __init__(self, input_size, hidden_size, num_classes):
        super().__init__()
        
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, num_classes)
        )
    
    def forward(self, x):
        return self.network(x)

# Create model, loss function, and optimizer
model = SimpleClassifier(input_size=784, hidden_size=256, num_classes=10).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Print model summary
print(model)
total_params = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"Total parameters: {total_params:,}")
print(f"Trainable parameters: {trainable_params:,}")
```

### The Training Loop

```python
def train_epoch(model, data_loader, criterion, optimizer, device):
    """Train for one epoch."""
    model.train()  # Set model to training mode (enables dropout, batch norm training behavior)
    
    total_loss = 0
    correct = 0
    total = 0
    
    for batch_idx, (inputs, targets) in enumerate(data_loader):
        inputs, targets = inputs.to(device), targets.to(device)
        
        # 1. Forward pass
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        
        # 2. Backward pass
        optimizer.zero_grad()  # Clear previous gradients
        loss.backward()        # Compute gradients
        
        # 3. Update parameters
        optimizer.step()
        
        # Track metrics
        total_loss += loss.item() * inputs.size(0)
        _, predicted = outputs.max(1)
        total += targets.size(0)
        correct += predicted.eq(targets).sum().item()
    
    avg_loss = total_loss / total
    accuracy = correct / total
    return avg_loss, accuracy


def evaluate(model, data_loader, criterion, device):
    """Evaluate the model on a dataset."""
    model.eval()  # Set to evaluation mode (disables dropout, uses running batch norm stats)
    
    total_loss = 0
    correct = 0
    total = 0
    
    with torch.no_grad():  # Disable gradient computation (saves memory and time)
        for inputs, targets in data_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            
            total_loss += loss.item() * inputs.size(0)
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()
    
    avg_loss = total_loss / total
    accuracy = correct / total
    return avg_loss, accuracy


# Full training loop
n_epochs = 50
best_val_accuracy = 0

for epoch in range(n_epochs):
    train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
    val_loss, val_acc = evaluate(model, val_loader, criterion, device)
    
    print(f"Epoch {epoch+1}/{n_epochs}")
    print(f"  Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}")
    print(f"  Val Loss:   {val_loss:.4f}, Val Acc:   {val_acc:.4f}")
    
    # Save best model
    if val_acc > best_val_accuracy:
        best_val_accuracy = val_acc
        torch.save(model.state_dict(), "best_model.pt")
        print(f"  Saved best model (Val Acc: {val_acc:.4f})")

# Load best model and evaluate on test set
model.load_state_dict(torch.load("best_model.pt"))
test_loss, test_acc = evaluate(model, test_loader, criterion, device)
print(f"\nFinal Test Accuracy: {test_acc:.4f}")
```

### Saving and Loading Models

```python
# Save entire model (architecture + weights)
torch.save(model, "full_model.pt")

# Save only weights (recommended -- more flexible)
torch.save(model.state_dict(), "model_weights.pt")

# Load weights
model = SimpleClassifier(input_size=784, hidden_size=256, num_classes=10)
model.load_state_dict(torch.load("model_weights.pt"))
model.eval()  # Set to evaluation mode

# Save a training checkpoint (weights, optimizer, epoch, loss)
checkpoint = {
    "epoch": epoch,
    "model_state_dict": model.state_dict(),
    "optimizer_state_dict": optimizer.state_dict(),
    "train_loss": train_loss,
    "val_loss": val_loss
}
torch.save(checkpoint, "checkpoint.pt")

# Load checkpoint
checkpoint = torch.load("checkpoint.pt")
model.load_state_dict(checkpoint["model_state_dict"])
optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
start_epoch = checkpoint["epoch"] + 1
```

---

## 12. Common Layer Types

### Linear (Fully Connected) Layer

Computes $y = Wx + b$. Connects every input to every output.

```python
layer = nn.Linear(in_features=256, out_features=128)
# Parameters: 256 * 128 + 128 = 32,896
```

### Convolutional Layers (for images, audio, sequences)

Covered in detail in Chapter 8 (Computer Vision). Briefly: they slide a small filter over the input, detecting local patterns (edges, textures, etc.).

```python
conv = nn.Conv2d(in_channels=3, out_channels=64, kernel_size=3, padding=1)
# Input: (batch, 3, H, W) -> Output: (batch, 64, H, W)
```

### Recurrent Layers (for sequences)

Covered in detail in Chapter 7 (NLP). Briefly: they process sequences one step at a time, maintaining a hidden state that carries information from previous steps.

```python
rnn = nn.LSTM(input_size=256, hidden_size=512, num_layers=2, batch_first=True)
# Input: (batch, seq_len, 256) -> Output: (batch, seq_len, 512)
```

### Embedding Layer

Maps integer indices to dense vectors. Used for words, categories, etc.

```python
embedding = nn.Embedding(num_embeddings=50000, embedding_dim=256)
# Input: (batch, seq_len) of integers -> Output: (batch, seq_len, 256) of floats
```

### Pooling Layers

Reduce spatial dimensions by taking the maximum or average within local windows.

```python
max_pool = nn.MaxPool2d(kernel_size=2, stride=2)
# Input: (batch, channels, H, W) -> Output: (batch, channels, H/2, W/2)

avg_pool = nn.AdaptiveAvgPool2d(output_size=(1, 1))
# Input: (batch, channels, H, W) -> Output: (batch, channels, 1, 1)  -- global average
```

---

## 13. Weight Initialization

How you initialize the weights before training matters a lot. Poor initialization can make training very slow or cause it to fail entirely.

### Why It Matters

If weights are too large, activations will explode (become huge numbers). If weights are too small, activations will vanish (become nearly zero). Either way, gradients become unhelpful and the network cannot learn.

### Xavier/Glorot Initialization

Designed for sigmoid and tanh activations. Sets weights to maintain the variance of activations across layers.

$$W \sim \text{Uniform}\left(-\sqrt{\frac{6}{n_{\text{in}} + n_{\text{out}}}}, \sqrt{\frac{6}{n_{\text{in}} + n_{\text{out}}}}\right)$$

or

$$W \sim \mathcal{N}\left(0, \frac{2}{n_{\text{in}} + n_{\text{out}}}\right)$$

```python
nn.init.xavier_uniform_(layer.weight)
nn.init.xavier_normal_(layer.weight)
```

### He/Kaiming Initialization

Designed for ReLU activations. Accounts for the fact that ReLU zeros out half the values.

$$W \sim \mathcal{N}\left(0, \frac{2}{n_{\text{in}}}\right)$$

```python
nn.init.kaiming_uniform_(layer.weight, nonlinearity="relu")
nn.init.kaiming_normal_(layer.weight, nonlinearity="relu")
```

### Default in PyTorch

PyTorch's `nn.Linear` uses Kaiming Uniform initialization by default, which works well for ReLU networks. You usually do not need to change it unless using a different activation function.

---

## 14. Batch Normalization

Batch normalization normalizes the inputs to each layer to have zero mean and unit variance. This stabilizes training and allows higher learning rates.

### How It Works

For each mini-batch, for each feature:

$$\hat{x} = \frac{x - \mu_{\text{batch}}}{\sqrt{\sigma_{\text{batch}}^2 + \epsilon}}$$

$$y = \gamma \hat{x} + \beta$$

Where $\gamma$ (scale) and $\beta$ (shift) are learnable parameters that allow the network to undo the normalization if that is beneficial.

### When to Use It

```python
class ModelWithBatchNorm(nn.Module):
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(784, 256),
            nn.BatchNorm1d(256),   # Batch norm AFTER linear, BEFORE activation
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Linear(128, 10)
        )
    
    def forward(self, x):
        return self.network(x)
```

### Layer Normalization

Layer normalization normalizes across features instead of across the batch. It is preferred in transformer architectures because it works regardless of batch size.

```python
# Layer norm normalizes each sample independently
layer_norm = nn.LayerNorm(256)
# Input: (batch, 256) -> Output: (batch, 256) -- each sample is normalized
```

---

## 15. Dropout

Dropout randomly sets a fraction of neuron outputs to zero during training. This prevents the network from relying too heavily on any single neuron and acts as regularization.

### How It Works

During training: each neuron output has probability $p$ of being set to zero. The remaining outputs are scaled up by $\frac{1}{1-p}$ to maintain the expected value.

During evaluation: dropout is disabled (all neurons are active). This is why you must call `model.train()` before training and `model.eval()` before evaluation.

```python
class ModelWithDropout(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 512)
        self.dropout1 = nn.Dropout(p=0.5)  # 50% of neurons dropped
        self.fc2 = nn.Linear(512, 256)
        self.dropout2 = nn.Dropout(p=0.3)  # 30% of neurons dropped
        self.fc3 = nn.Linear(256, 10)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.dropout1(x)   # Dropout after activation
        x = torch.relu(self.fc2(x))
        x = self.dropout2(x)
        x = self.fc3(x)        # No dropout on the output layer
        return x
```

**Typical dropout rates**:
- 0.1 to 0.3: Light regularization. Good for small models or when you have lots of data.
- 0.5: Standard. Good default for most situations.
- 0.7 to 0.9: Heavy regularization. Use when overfitting is severe.

---

## 16. Skip Connections (Residual Connections)

Skip connections (also called residual connections) allow the input to a block to be added to its output. This was introduced in the ResNet paper and is critical for training very deep networks (100+ layers).

### The Problem with Deep Networks

As networks get deeper, gradients must flow through more and more layers during backpropagation. This can cause:
- **Vanishing gradients**: Gradients shrink to nearly zero, so early layers barely learn.
- **Degradation**: Adding more layers makes the model worse, not better.

### The Solution

Instead of learning $H(x)$, learn $F(x) = H(x) - x$ and compute $H(x) = F(x) + x$.

```
x ---> [Layer] ---> [Layer] ---> F(x)
|                                 |
+--- skip connection ----------->+---> F(x) + x
```

If the optimal transformation is close to the identity (do nothing), the network just needs to learn $F(x) \approx 0$, which is much easier.

```python
class ResidualBlock(nn.Module):
    """A residual block with a skip connection."""
    
    def __init__(self, dim):
        super().__init__()
        self.block = nn.Sequential(
            nn.Linear(dim, dim),
            nn.BatchNorm1d(dim),
            nn.ReLU(),
            nn.Linear(dim, dim),
            nn.BatchNorm1d(dim)
        )
        self.relu = nn.ReLU()
    
    def forward(self, x):
        residual = x                # Save the input
        out = self.block(x)         # Transform
        out = out + residual        # Add skip connection
        out = self.relu(out)        # Final activation
        return out


class DeepResidualNetwork(nn.Module):
    """A deep network using residual blocks."""
    
    def __init__(self, input_dim, hidden_dim, num_classes, num_blocks=10):
        super().__init__()
        
        self.input_layer = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU()
        )
        
        self.blocks = nn.Sequential(
            *[ResidualBlock(hidden_dim) for _ in range(num_blocks)]
        )
        
        self.output_layer = nn.Linear(hidden_dim, num_classes)
    
    def forward(self, x):
        x = self.input_layer(x)
        x = self.blocks(x)
        x = self.output_layer(x)
        return x
```

---

## 17. Network Architecture Design

### Rules of Thumb

1. **Start simple**: Begin with a small network and increase complexity only if needed.
2. **Powers of 2**: Use hidden sizes that are powers of 2 (64, 128, 256, 512, 1024). GPUs are optimized for these.
3. **Funnel shape**: Gradually reduce the hidden size from input to output (e.g., 512 -> 256 -> 128 -> 10).
4. **Skip connections**: Use them when the network has more than about 5 layers.
5. **Batch normalization**: Use it by default. It almost always helps.
6. **Dropout**: Start with 0.1-0.3 and increase if overfitting.
7. **Activation**: ReLU for most cases. GELU for transformers.

### How to Choose Architecture for Your Task

| Task | Architecture |
|------|-------------|
| Tabular data | MLP (2-4 layers, 64-512 neurons) |
| Image classification | CNN (ResNet, EfficientNet) |
| Object detection | CNN + detection head (YOLO, Faster R-CNN) |
| Text classification | Transformer encoder (BERT) |
| Text generation | Transformer decoder (GPT) |
| Translation | Transformer encoder-decoder (T5) |
| Speech recognition | Transformer or CNN + RNN (Whisper) |
| 3D generation | Diffusion models, NeRF, or transformer |
| Time series | Transformer, LSTM, or 1D CNN |

---

## 18. Universal Approximation Theorem

The Universal Approximation Theorem states that a neural network with just one hidden layer and a sufficient number of neurons can approximate any continuous function to arbitrary accuracy.

What this means: Neural networks are incredibly flexible. Given enough neurons and training data, they can learn virtually any input-output mapping.

What this does NOT mean:
- It does not tell you how many neurons you need.
- It does not tell you how to find the right weights (training might be hard).
- It does not guarantee that gradient descent will find a good solution.
- In practice, deeper networks with fewer neurons per layer are more efficient than a single wide layer.

---

## 19. Summary

You now understand neural networks at a deep level:

1. **What they are**: Mathematical functions with learnable parameters.
2. **Perceptrons**: The building block -- weighted sum, bias, activation.
3. **Activation functions**: ReLU, sigmoid, tanh, GELU, softmax -- introducing non-linearity.
4. **MLPs**: Multiple layers of fully connected neurons.
5. **Forward propagation**: Input flows through layers to produce output.
6. **Loss functions**: MSE, cross-entropy, Huber -- measuring prediction quality.
7. **Backpropagation**: Computing gradients using the chain rule.
8. **Optimizers**: SGD, Adam, AdamW -- updating parameters to reduce loss.
9. **From-scratch implementation**: Building and training a network in pure NumPy.
10. **PyTorch**: The professional framework for building neural networks.
11. **Common layers**: Linear, Conv, RNN, Embedding, Pooling.
12. **Weight initialization**: Xavier, He -- starting the network well.
13. **Batch normalization**: Stabilizing training.
14. **Dropout**: Preventing overfitting.
15. **Skip connections**: Training very deep networks.
16. **Architecture design**: Choosing the right structure for your task.
17. **Universal approximation**: The theoretical power of neural networks.

---

[<< Previous: Chapter 4 - ML Fundamentals](./04_ML_FUNDAMENTALS.md) | [Next: Chapter 6 - Training Deep Networks >>](./06_TRAINING_DEEP_NETWORKS.md)
