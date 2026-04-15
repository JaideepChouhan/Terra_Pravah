# Chapter 1: Mathematics for Artificial Intelligence

## Introduction

Mathematics is the language of AI. Every neural network, every training algorithm, every optimization technique is built on mathematical foundations. But do not let that scare you. The math you need for AI is not abstract or obscure -- it is practical, visual, and once you understand it, everything else clicks into place.

This chapter covers everything from basic arithmetic through calculus, linear algebra, probability, and statistics -- all explained from scratch with concrete examples and Python code.

---

## Table of Contents

1. Numbers and Arithmetic
2. Algebra Fundamentals
3. Functions and Graphs
4. Linear Algebra
   - Scalars, Vectors, Matrices, and Tensors
   - Vector Operations
   - Matrix Operations
   - Matrix Multiplication
   - Transpose
   - Determinant and Inverse
   - Eigenvalues and Eigenvectors
   - Norms
5. Calculus
   - Limits
   - Derivatives
   - Partial Derivatives
   - The Chain Rule
   - Gradients
   - Integrals
6. Probability and Statistics
   - Basic Probability
   - Conditional Probability and Bayes' Theorem
   - Probability Distributions
   - Expected Value, Variance, Standard Deviation
   - Maximum Likelihood Estimation
7. Information Theory
   - Entropy
   - Cross-Entropy
   - KL Divergence
8. Optimization
   - Gradient Descent
   - Stochastic Gradient Descent
   - Learning Rate
   - Convex vs Non-Convex Optimization
9. Putting It All Together

---

## 1. Numbers and Arithmetic

### Types of Numbers

- **Natural numbers**: 0, 1, 2, 3, 4, ... (counting numbers)
- **Integers**: ..., -3, -2, -1, 0, 1, 2, 3, ... (natural numbers plus negatives)
- **Rational numbers**: Numbers that can be expressed as a fraction (e.g., 1/2, 3/4, -7/3)
- **Real numbers**: All numbers on the number line, including irrational numbers like pi (3.14159...) and sqrt(2) (1.41421...)
- **Complex numbers**: Numbers with a real part and an imaginary part (e.g., 3 + 2i). Rarely used in basic AI, but appear in some signal processing and advanced architectures.

In AI, we primarily work with real numbers, represented as floating-point numbers in the computer.

### Arithmetic Operations

```
Addition:        3 + 5 = 8
Subtraction:     10 - 4 = 6
Multiplication:  6 * 7 = 42
Division:        15 / 4 = 3.75
Integer Division: 15 // 4 = 3  (discard the remainder)
Modulus:         15 % 4 = 3    (the remainder)
Exponentiation:  2^10 = 1024   (2 multiplied by itself 10 times)
Square Root:     sqrt(16) = 4  (what number times itself gives 16?)
```

### Order of Operations (PEMDAS/BODMAS)

1. Parentheses / Brackets
2. Exponents / Orders
3. Multiplication and Division (left to right)
4. Addition and Subtraction (left to right)

Example: 3 + 4 * 2 = 3 + 8 = 11 (not 14, because multiplication comes before addition)

### Summation Notation

In AI papers and textbooks, you will frequently see summation notation:

The sum of values x_1, x_2, ..., x_n is written as:

$$\sum_{i=1}^{n} x_i = x_1 + x_2 + x_3 + \cdots + x_n$$

For example, if x = [2, 5, 3, 8], then:

$$\sum_{i=1}^{4} x_i = 2 + 5 + 3 + 8 = 18$$

In Python:

```python
x = [2, 5, 3, 8]
total = sum(x)  # 18
```

### Product Notation

Similarly, the product of values is written as:

$$\prod_{i=1}^{n} x_i = x_1 \times x_2 \times x_3 \times \cdots \times x_n$$

For example:

$$\prod_{i=1}^{4} x_i = 2 \times 5 \times 3 \times 8 = 240$$

In Python:

```python
import math
x = [2, 5, 3, 8]
product = math.prod(x)  # 240
```

---

## 2. Algebra Fundamentals

### Variables

A variable is a symbol that represents a number. Just like in algebra class, we use letters like x, y, z to represent unknown or changing values.

In AI:
- **x** often represents input data
- **y** often represents the output or target value
- **w** (or theta) represents the weights (parameters) of a model
- **b** represents bias terms

### Equations

An equation states that two expressions are equal:

$$y = 2x + 3$$

This means: for any value of x, y is twice that value plus 3.

- When x = 0: y = 2(0) + 3 = 3
- When x = 1: y = 2(1) + 3 = 5
- When x = 5: y = 2(5) + 3 = 13

This is actually the equation of a straight line, and it is the simplest possible AI model (linear regression).

### Solving Equations

To solve an equation means to find the value of the unknown variable. The key principle is: you can do the same thing to both sides of an equation.

Example: Solve 3x + 7 = 22

```
3x + 7 = 22
3x = 22 - 7        (subtract 7 from both sides)
3x = 15
x = 15 / 3          (divide both sides by 3)
x = 5
```

### Exponents and Logarithms

Exponents:
$$a^n = \underbrace{a \times a \times \cdots \times a}_{n \text{ times}}$$

Important rules:
- $a^0 = 1$ (any number to the power 0 is 1)
- $a^1 = a$
- $a^m \times a^n = a^{m+n}$
- $(a^m)^n = a^{mn}$
- $a^{-n} = \frac{1}{a^n}$

The natural exponential function $e^x$ (where $e \approx 2.71828$) is extremely important in AI. It appears in:
- The softmax function (converts numbers to probabilities)
- The sigmoid function (squashes numbers to the range 0-1)
- Normal distributions
- Many loss functions

Logarithms are the inverse of exponents. If $a^b = c$, then $\log_a(c) = b$.

The natural logarithm (written as $\ln$ or $\log$) is the logarithm with base $e$:
- If $e^x = y$, then $\ln(y) = x$
- $\ln(1) = 0$
- $\ln(e) = 1$
- $\ln(ab) = \ln(a) + \ln(b)$
- $\ln(a/b) = \ln(a) - \ln(b)$
- $\ln(a^n) = n \cdot \ln(a)$

Logarithms are critical in AI because:
- We often use log-probabilities instead of probabilities (to avoid numerical underflow when multiplying many small numbers)
- Cross-entropy loss (the most common loss function) uses logarithms
- Information theory is built on logarithms

In Python:

```python
import math
import numpy as np

# Exponents
print(2 ** 10)          # 1024
print(math.e)           # 2.718281828...
print(np.exp(1))        # e^1 = 2.718281828...
print(np.exp(0))        # e^0 = 1.0

# Logarithms
print(np.log(1))        # ln(1) = 0.0
print(np.log(math.e))   # ln(e) = 1.0
print(np.log(100))      # ln(100) = 4.605...
print(np.log10(100))    # log10(100) = 2.0
print(np.log2(1024))    # log2(1024) = 10.0
```

---

## 3. Functions and Graphs

A function takes an input and produces an output. Written as $f(x)$, where $x$ is the input and $f(x)$ is the output.

### Linear Functions

$$f(x) = mx + b$$

Where $m$ is the slope (how steep the line is) and $b$ is the y-intercept (where the line crosses the y-axis).

This is the foundation of linear regression, the simplest AI model.

### Common Functions in AI

#### Sigmoid Function

$$\sigma(x) = \frac{1}{1 + e^{-x}}$$

The sigmoid function takes any real number and outputs a value between 0 and 1. This makes it perfect for representing probabilities.

- $\sigma(0) = 0.5$
- $\sigma(\text{large positive}) \approx 1$
- $\sigma(\text{large negative}) \approx 0$

```python
import numpy as np

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

# Test it
print(sigmoid(0))      # 0.5
print(sigmoid(5))      # 0.9933...
print(sigmoid(-5))     # 0.0067...
print(sigmoid(100))    # 1.0 (essentially)
print(sigmoid(-100))   # 0.0 (essentially)
```

#### ReLU (Rectified Linear Unit)

$$\text{ReLU}(x) = \max(0, x)$$

ReLU is the most widely used activation function in neural networks. It outputs 0 for negative inputs and passes through positive inputs unchanged.

- ReLU(-3) = 0
- ReLU(0) = 0
- ReLU(5) = 5

```python
def relu(x):
    return np.maximum(0, x)
```

#### Tanh (Hyperbolic Tangent)

$$\tanh(x) = \frac{e^x - e^{-x}}{e^x + e^{-x}}$$

Outputs values between -1 and 1. Used in some neural network architectures.

#### Softmax

The softmax function converts a vector of numbers into a probability distribution (all values between 0 and 1, summing to 1):

$$\text{softmax}(x_i) = \frac{e^{x_i}}{\sum_{j=1}^{n} e^{x_j}}$$

```python
def softmax(x):
    exp_x = np.exp(x - np.max(x))  # subtract max for numerical stability
    return exp_x / np.sum(exp_x)

scores = np.array([2.0, 1.0, 0.1])
print(softmax(scores))  # [0.659, 0.242, 0.099] -- sums to 1.0
```

Softmax is used at the output of classification models and is a core component of the attention mechanism in transformers.

### Visualizing Functions

```python
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(-5, 5, 100)

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Sigmoid
axes[0, 0].plot(x, 1 / (1 + np.exp(-x)))
axes[0, 0].set_title('Sigmoid')
axes[0, 0].grid(True)

# ReLU
axes[0, 1].plot(x, np.maximum(0, x))
axes[0, 1].set_title('ReLU')
axes[0, 1].grid(True)

# Tanh
axes[1, 0].plot(x, np.tanh(x))
axes[1, 0].set_title('Tanh')
axes[1, 0].grid(True)

# Linear
axes[1, 1].plot(x, 2*x + 1)
axes[1, 1].set_title('Linear: y = 2x + 1')
axes[1, 1].grid(True)

plt.tight_layout()
plt.savefig('activation_functions.png')
plt.show()
```

---

## 4. Linear Algebra

Linear algebra is the single most important area of mathematics for AI. Neural networks are fundamentally machines that perform linear algebra operations (matrix multiplications) interspersed with nonlinear functions.

### Scalars, Vectors, Matrices, and Tensors

#### Scalars

A scalar is a single number. Examples: 5, -3.14, 0, 42.7

In Python:
```python
x = 5.0
```

#### Vectors

A vector is an ordered list of numbers. Think of it as an arrow in space, or a point in a multi-dimensional space.

$$\mathbf{v} = \begin{bmatrix} 1 \\ 3 \\ 5 \end{bmatrix}$$

This is a 3-dimensional vector. It has three components (or elements).

In AI, vectors are used to represent:
- A single data point (a 784-dimensional vector for a 28x28 pixel grayscale image)
- A word (word embeddings are typically 100-768 dimensional vectors)
- The weights of a single neuron
- Gradients

In Python (using NumPy):
```python
import numpy as np

# Creating vectors
v = np.array([1, 3, 5])
print(v)            # [1 3 5]
print(v.shape)      # (3,) -- a 3-element vector
print(v[0])         # 1 (first element, 0-indexed)
print(v[2])         # 5 (third element)
print(len(v))       # 3
```

#### Matrices

A matrix is a 2-dimensional array of numbers. Think of it as a spreadsheet or a grid.

$$\mathbf{M} = \begin{bmatrix} 1 & 2 & 3 \\ 4 & 5 & 6 \end{bmatrix}$$

This is a 2x3 matrix (2 rows, 3 columns).

In AI, matrices are used to represent:
- A batch of data points (each row is a data point, each column is a feature)
- The weight matrix of a neural network layer
- An image (rows and columns of pixel values)
- Attention scores in transformers

In Python:
```python
M = np.array([[1, 2, 3],
              [4, 5, 6]])
print(M)
print(M.shape)      # (2, 3) -- 2 rows, 3 columns
print(M[0, 0])      # 1 (first row, first column)
print(M[1, 2])      # 6 (second row, third column)
print(M[0])         # [1 2 3] (first row)
print(M[:, 1])      # [2 5] (second column)
```

#### Tensors

A tensor is a generalization of scalars, vectors, and matrices to any number of dimensions:

- A scalar is a 0-dimensional tensor
- A vector is a 1-dimensional tensor
- A matrix is a 2-dimensional tensor
- A 3D tensor is like a stack of matrices (e.g., a color image: height x width x 3 channels)
- A 4D tensor is a batch of 3D tensors (e.g., a batch of images: batch_size x height x width x channels)

In deep learning frameworks like PyTorch, all data is represented as tensors:

```python
import torch

# Scalar (0D tensor)
s = torch.tensor(5.0)
print(s.shape)          # torch.Size([])

# Vector (1D tensor)
v = torch.tensor([1.0, 2.0, 3.0])
print(v.shape)          # torch.Size([3])

# Matrix (2D tensor)
m = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
print(m.shape)          # torch.Size([2, 2])

# 3D Tensor (e.g., a single color image: 3 channels x 224 pixels x 224 pixels)
img = torch.randn(3, 224, 224)
print(img.shape)        # torch.Size([3, 224, 224])

# 4D Tensor (e.g., a batch of 32 images)
batch = torch.randn(32, 3, 224, 224)
print(batch.shape)      # torch.Size([32, 3, 224, 224])
```

### Vector Operations

#### Addition

Two vectors of the same size can be added element-by-element:

$$\begin{bmatrix} 1 \\ 2 \\ 3 \end{bmatrix} + \begin{bmatrix} 4 \\ 5 \\ 6 \end{bmatrix} = \begin{bmatrix} 5 \\ 7 \\ 9 \end{bmatrix}$$

```python
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
print(a + b)  # [5 7 9]
```

#### Scalar Multiplication

Multiplying a vector by a scalar multiplies each element:

$$3 \times \begin{bmatrix} 1 \\ 2 \\ 3 \end{bmatrix} = \begin{bmatrix} 3 \\ 6 \\ 9 \end{bmatrix}$$

```python
print(3 * a)  # [3 6 9]
```

#### Dot Product

The dot product of two vectors is the sum of the products of corresponding elements:

$$\mathbf{a} \cdot \mathbf{b} = \sum_{i=1}^{n} a_i b_i$$

$$\begin{bmatrix} 1 \\ 2 \\ 3 \end{bmatrix} \cdot \begin{bmatrix} 4 \\ 5 \\ 6 \end{bmatrix} = 1 \times 4 + 2 \times 5 + 3 \times 6 = 4 + 10 + 18 = 32$$

```python
print(np.dot(a, b))  # 32
```

The dot product is fundamental to AI. Every single neuron in a neural network computes a dot product between its input and its weights. Every attention score in a transformer is a dot product.

#### Element-wise (Hadamard) Product

Multiplying two vectors element by element (not the same as the dot product):

$$\begin{bmatrix} 1 \\ 2 \\ 3 \end{bmatrix} \odot \begin{bmatrix} 4 \\ 5 \\ 6 \end{bmatrix} = \begin{bmatrix} 4 \\ 10 \\ 18 \end{bmatrix}$$

```python
print(a * b)  # [ 4 10 18]
```

### Norms (Measuring the Size of a Vector)

A norm is a function that measures the "length" or "size" of a vector.

#### L1 Norm (Manhattan Distance)

$$\|\mathbf{v}\|_1 = \sum_{i=1}^{n} |v_i|$$

The sum of the absolute values of all elements.

$$\left\|\begin{bmatrix} 3 \\ -4 \\ 5 \end{bmatrix}\right\|_1 = |3| + |-4| + |5| = 3 + 4 + 5 = 12$$

#### L2 Norm (Euclidean Distance)

$$\|\mathbf{v}\|_2 = \sqrt{\sum_{i=1}^{n} v_i^2}$$

The square root of the sum of squares. This is the usual notion of "distance."

$$\left\|\begin{bmatrix} 3 \\ 4 \end{bmatrix}\right\|_2 = \sqrt{3^2 + 4^2} = \sqrt{9 + 16} = \sqrt{25} = 5$$

```python
v = np.array([3, -4, 5])
print(np.linalg.norm(v, ord=1))  # L1 norm: 12.0
print(np.linalg.norm(v, ord=2))  # L2 norm: 7.071...
print(np.linalg.norm(v))         # Default is L2: 7.071...
```

Norms are used in:
- Regularization (L1 and L2 regularization add norm-based penalties to prevent overfitting)
- Normalization (scaling vectors to have unit length)
- Measuring distances between vectors

### Matrix Operations

#### Matrix Addition

Element-wise, same as vectors but in 2D:

```python
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])
print(A + B)
# [[ 6  8]
#  [10 12]]
```

#### Matrix Multiplication

This is the most important operation in all of AI. Matrix multiplication is NOT element-wise. It follows a specific rule:

To multiply matrix A (shape m x n) by matrix B (shape n x p), the number of columns of A must equal the number of rows of B. The result has shape m x p.

Each element of the result is computed as the dot product of a row of A with a column of B:

$$(\mathbf{AB})_{ij} = \sum_{k=1}^{n} A_{ik} B_{kj}$$

Example:

$$\begin{bmatrix} 1 & 2 \\ 3 & 4 \end{bmatrix} \times \begin{bmatrix} 5 & 6 \\ 7 & 8 \end{bmatrix}$$

Row 1 of A dot Column 1 of B: 1*5 + 2*7 = 5 + 14 = 19
Row 1 of A dot Column 2 of B: 1*6 + 2*8 = 6 + 16 = 22
Row 2 of A dot Column 1 of B: 3*5 + 4*7 = 15 + 28 = 43
Row 2 of A dot Column 2 of B: 3*6 + 4*8 = 18 + 32 = 50

$$= \begin{bmatrix} 19 & 22 \\ 43 & 50 \end{bmatrix}$$

```python
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])
print(np.matmul(A, B))   # or A @ B
# [[19 22]
#  [43 50]]
```

Why does matrix multiplication matter for AI? A neural network layer is essentially: output = activation(input @ weights + bias). The @ is matrix multiplication. When you have a batch of 64 data points, each with 100 features, and a layer with 50 neurons:
- Input shape: (64, 100)
- Weight shape: (100, 50)
- Output shape: (64, 50)

One matrix multiplication computes all 64 * 50 = 3,200 neuron outputs simultaneously. This is why GPUs (which are designed for matrix multiplication) are so important for AI.

#### Transpose

The transpose of a matrix flips it over its diagonal (rows become columns, columns become rows):

$$\mathbf{A} = \begin{bmatrix} 1 & 2 & 3 \\ 4 & 5 & 6 \end{bmatrix} \quad \Rightarrow \quad \mathbf{A}^T = \begin{bmatrix} 1 & 4 \\ 2 & 5 \\ 3 & 6 \end{bmatrix}$$

```python
A = np.array([[1, 2, 3], [4, 5, 6]])
print(A.T)
# [[1 4]
#  [2 5]
#  [3 6]]
```

#### Identity Matrix

The identity matrix is the matrix equivalent of the number 1. Multiplying any matrix by the identity matrix gives the same matrix:

$$\mathbf{I} = \begin{bmatrix} 1 & 0 & 0 \\ 0 & 1 & 0 \\ 0 & 0 & 1 \end{bmatrix}$$

```python
I = np.eye(3)  # 3x3 identity matrix
```

#### Matrix Inverse

The inverse of a matrix A, written $A^{-1}$, is the matrix such that $A \times A^{-1} = I$ (the identity matrix). Not all matrices have inverses (just as you cannot divide by zero).

```python
A = np.array([[1, 2], [3, 4]])
A_inv = np.linalg.inv(A)
print(A_inv)
# [[-2.   1. ]
#  [ 1.5 -0.5]]

# Verify: A @ A_inv should be the identity matrix
print(A @ A_inv)
# [[1. 0.]
#  [0. 1.]]
```

#### Determinant

The determinant of a square matrix is a single number that tells you whether the matrix is invertible (determinant is not zero) and how it scales volume.

For a 2x2 matrix:
$$\det\begin{bmatrix} a & b \\ c & d \end{bmatrix} = ad - bc$$

```python
A = np.array([[1, 2], [3, 4]])
print(np.linalg.det(A))  # -2.0
```

#### Eigenvalues and Eigenvectors

An eigenvector of a matrix A is a vector that, when multiplied by A, only gets scaled (not rotated):

$$A\mathbf{v} = \lambda\mathbf{v}$$

Where $\mathbf{v}$ is the eigenvector and $\lambda$ is the eigenvalue (the scaling factor).

Eigenvalues and eigenvectors are used in:
- Principal Component Analysis (PCA) for dimensionality reduction
- Understanding the behavior of neural networks
- Spectral methods in graph neural networks

```python
A = np.array([[4, -2], [1, 1]])
eigenvalues, eigenvectors = np.linalg.eig(A)
print("Eigenvalues:", eigenvalues)    # [3. 2.]
print("Eigenvectors:\n", eigenvectors)
```

### Broadcasting

Broadcasting is a NumPy feature that allows operations between arrays of different shapes. Understanding it is essential for writing efficient AI code.

Rules of broadcasting:
1. If the arrays have different numbers of dimensions, the shape of the smaller array is padded with 1s on the left.
2. Arrays with a size of 1 in a particular dimension act as if they had the size of the largest shape in that dimension.

```python
# Add a scalar to a matrix (scalar is broadcast to every element)
M = np.array([[1, 2, 3], [4, 5, 6]])
print(M + 10)
# [[11 12 13]
#  [14 15 16]]

# Add a vector to each row of a matrix
v = np.array([10, 20, 30])
print(M + v)
# [[11 22 33]
#  [14 25 36]]

# Add a column vector to each column of a matrix
c = np.array([[100], [200]])
print(M + c)
# [[101 102 103]
#  [204 205 206]]
```

---

## 5. Calculus

Calculus is the mathematics of change. In AI, calculus is used to:
- Compute how changing a model's parameters affects its error (derivatives)
- Update parameters to reduce the error (gradient descent)
- Understand optimization landscapes

### Limits

A limit describes the value a function approaches as the input approaches some value:

$$\lim_{x \to a} f(x) = L$$

This means: as $x$ gets closer and closer to $a$, $f(x)$ gets closer and closer to $L$.

Example:
$$\lim_{x \to 2} (x^2 + 1) = 4 + 1 = 5$$

### Derivatives

The derivative of a function at a point is the slope of the function at that point -- it tells you how fast the function is changing.

$$f'(x) = \frac{df}{dx} = \lim_{h \to 0} \frac{f(x + h) - f(x)}{h}$$

Think of it as: if I wiggle $x$ by a tiny amount, how much does $f(x)$ change?

#### Common Derivatives

| Function | Derivative |
|----------|-----------|
| $f(x) = c$ (constant) | $f'(x) = 0$ |
| $f(x) = x$ | $f'(x) = 1$ |
| $f(x) = x^2$ | $f'(x) = 2x$ |
| $f(x) = x^n$ | $f'(x) = nx^{n-1}$ |
| $f(x) = e^x$ | $f'(x) = e^x$ |
| $f(x) = \ln(x)$ | $f'(x) = 1/x$ |
| $f(x) = \sin(x)$ | $f'(x) = \cos(x)$ |
| $f(x) = \cos(x)$ | $f'(x) = -\sin(x)$ |

#### Derivative Rules

**Sum Rule**: $(f + g)' = f' + g'$

**Product Rule**: $(fg)' = f'g + fg'$

**Quotient Rule**: $(f/g)' = (f'g - fg') / g^2$

**Chain Rule** (the most important one for AI):

$(f(g(x)))' = f'(g(x)) \cdot g'(x)$

The chain rule says: the derivative of a composition of functions is the derivative of the outer function (evaluated at the inner function) times the derivative of the inner function.

Example: If $h(x) = (3x + 2)^5$, let $g(x) = 3x + 2$ and $f(u) = u^5$:
- $f'(u) = 5u^4$
- $g'(x) = 3$
- $h'(x) = 5(3x + 2)^4 \cdot 3 = 15(3x + 2)^4$

The chain rule is the mathematical foundation of backpropagation, which is how neural networks learn. The entire training process is based on applying the chain rule through the layers of the network.

#### Computing Derivatives Numerically

You can approximate derivatives numerically using the definition:

```python
def numerical_derivative(f, x, h=1e-7):
    return (f(x + h) - f(x - h)) / (2 * h)

# Derivative of x^2 at x = 3
def f(x):
    return x ** 2

print(numerical_derivative(f, 3))  # Very close to 6.0 (since d/dx x^2 = 2x, and 2*3 = 6)
```

### Partial Derivatives

When a function has multiple inputs, the partial derivative tells you how the output changes when you change one input while keeping the others fixed.

$$f(x, y) = x^2 + 3xy + y^2$$

Partial derivative with respect to $x$ (treat $y$ as a constant):
$$\frac{\partial f}{\partial x} = 2x + 3y$$

Partial derivative with respect to $y$ (treat $x$ as a constant):
$$\frac{\partial f}{\partial y} = 3x + 2y$$

### Gradients

The gradient of a function is a vector of all its partial derivatives. It points in the direction of steepest increase.

$$\nabla f(x, y) = \begin{bmatrix} \frac{\partial f}{\partial x} \\ \frac{\partial f}{\partial y} \end{bmatrix}$$

For our example:
$$\nabla f(x, y) = \begin{bmatrix} 2x + 3y \\ 3x + 2y \end{bmatrix}$$

In AI, the gradient tells you which direction to change the model's parameters to reduce the error. You then move in the opposite direction (gradient descent).

### The Jacobian and Hessian

The **Jacobian** is a matrix of all first-order partial derivatives for a vector-valued function. If $\mathbf{f}: \mathbb{R}^n \to \mathbb{R}^m$, the Jacobian is an $m \times n$ matrix.

The **Hessian** is a matrix of all second-order partial derivatives for a scalar-valued function. If $f: \mathbb{R}^n \to \mathbb{R}$, the Hessian is an $n \times n$ matrix. It tells you about the curvature of the function. Second-order optimization methods (like Newton's method) use the Hessian, but they are rarely used in deep learning because computing the full Hessian is too expensive for large models.

### Integrals

Integration is the inverse of differentiation. While derivatives measure rates of change, integrals measure accumulation (area under a curve).

$$\int_a^b f(x) \, dx$$

This computes the area under the curve $f(x)$ from $x = a$ to $x = b$.

Common integrals:
- $\int x^n \, dx = \frac{x^{n+1}}{n+1} + C$ (for $n \neq -1$)
- $\int e^x \, dx = e^x + C$
- $\int \frac{1}{x} \, dx = \ln|x| + C$

Integrals are used in probability theory (the probability of an event is the integral of the probability density function over the relevant range) and in some loss functions.

---

## 6. Probability and Statistics

Probability and statistics are essential for AI because:
- Models learn probability distributions from data.
- Loss functions are often derived from probability theory.
- Evaluation metrics are statistical in nature.
- Generative models explicitly model probability distributions.

### Basic Probability

The probability of an event is a number between 0 and 1:
- $P(\text{event}) = 0$ means the event is impossible
- $P(\text{event}) = 1$ means the event is certain
- $P(\text{event}) = 0.5$ means the event is equally likely or unlikely

#### Rules

**Complement**: $P(\text{not } A) = 1 - P(A)$

**Union (OR)**: $P(A \text{ or } B) = P(A) + P(B) - P(A \text{ and } B)$

**Intersection (AND)**: $P(A \text{ and } B) = P(A) \times P(B|A)$ where $P(B|A)$ is the probability of B given A.

**Independence**: If A and B are independent (one does not affect the other): $P(A \text{ and } B) = P(A) \times P(B)$

### Conditional Probability and Bayes' Theorem

Conditional probability is the probability of an event given that another event has occurred:

$$P(A|B) = \frac{P(A \text{ and } B)}{P(B)}$$

**Bayes' Theorem** is one of the most important results in all of probability theory:

$$P(A|B) = \frac{P(B|A) \times P(A)}{P(B)}$$

In AI terms:
- $P(A)$ is the **prior** (what you believe before seeing data)
- $P(B|A)$ is the **likelihood** (how likely the data is if A is true)
- $P(A|B)$ is the **posterior** (what you believe after seeing data)
- $P(B)$ is the **evidence** (how likely the data is overall)

Example: A medical test for a disease:
- P(disease) = 0.01 (1% of people have the disease)
- P(positive test | disease) = 0.99 (if you have the disease, the test catches it 99% of the time)
- P(positive test | no disease) = 0.05 (false positive rate is 5%)

If you test positive, what is the probability you actually have the disease?

$$P(\text{disease}|\text{positive}) = \frac{P(\text{positive}|\text{disease}) \times P(\text{disease})}{P(\text{positive})}$$

$$P(\text{positive}) = P(\text{positive}|\text{disease}) \times P(\text{disease}) + P(\text{positive}|\text{no disease}) \times P(\text{no disease})$$
$$= 0.99 \times 0.01 + 0.05 \times 0.99 = 0.0099 + 0.0495 = 0.0594$$

$$P(\text{disease}|\text{positive}) = \frac{0.99 \times 0.01}{0.0594} = \frac{0.0099}{0.0594} \approx 0.167$$

Only about 16.7%, not 99%. This is surprising and shows why understanding probability is important.

### Probability Distributions

A probability distribution describes the likelihood of different outcomes.

#### Discrete Distributions

**Bernoulli Distribution**: A single coin flip. Outcome is 0 or 1.
- $P(X = 1) = p$
- $P(X = 0) = 1 - p$

**Categorical Distribution**: Like a die roll. Multiple possible outcomes, each with its own probability.

**Binomial Distribution**: Number of successes in $n$ independent Bernoulli trials.

#### Continuous Distributions

**Uniform Distribution**: All values in a range are equally likely.

**Gaussian (Normal) Distribution**: The famous bell curve. Defined by mean ($\mu$) and standard deviation ($\sigma$):

$$f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{(x-\mu)^2}{2\sigma^2}}$$

The normal distribution is central to AI because:
- Noise in data is often approximately normal.
- Weight initialization in neural networks usually uses normal distributions.
- Variational autoencoders use normal distributions as their latent space.
- Diffusion models add and remove Gaussian noise.

```python
import numpy as np
import matplotlib.pyplot as plt

# Generate samples from a normal distribution
mu = 0      # mean
sigma = 1   # standard deviation
samples = np.random.normal(mu, sigma, 10000)

plt.hist(samples, bins=50, density=True, alpha=0.7)
plt.title('Gaussian Distribution (mu=0, sigma=1)')
plt.xlabel('Value')
plt.ylabel('Density')
plt.show()
```

### Expected Value, Variance, and Standard Deviation

**Expected Value (Mean)**: The average value you would get if you sampled infinitely many times.

$$E[X] = \mu = \sum_{i} x_i \cdot P(x_i) \quad \text{(discrete)}$$
$$E[X] = \mu = \int x \cdot f(x) \, dx \quad \text{(continuous)}$$

In practice:
$$\bar{x} = \frac{1}{n} \sum_{i=1}^{n} x_i$$

**Variance**: How spread out the values are from the mean.

$$\text{Var}(X) = \sigma^2 = E[(X - \mu)^2] = \frac{1}{n} \sum_{i=1}^{n} (x_i - \bar{x})^2$$

**Standard Deviation**: The square root of the variance.

$$\sigma = \sqrt{\text{Var}(X)}$$

```python
data = np.array([4, 8, 6, 5, 3, 7, 9, 2])
print("Mean:", np.mean(data))        # 5.5
print("Variance:", np.var(data))     # 4.75
print("Std Dev:", np.std(data))      # 2.179...
```

### Covariance and Correlation

**Covariance** measures how two variables change together:

$$\text{Cov}(X, Y) = E[(X - \mu_X)(Y - \mu_Y)]$$

- Positive covariance: when X is high, Y tends to be high
- Negative covariance: when X is high, Y tends to be low
- Zero covariance: no linear relationship

**Correlation** is covariance normalized to the range [-1, 1]:

$$\rho_{XY} = \frac{\text{Cov}(X, Y)}{\sigma_X \sigma_Y}$$

### Maximum Likelihood Estimation (MLE)

MLE is a method for estimating the parameters of a probability distribution. The idea: find the parameters that make the observed data most likely.

Given data $x_1, x_2, \ldots, x_n$ and a model with parameters $\theta$:

$$\hat{\theta}_{MLE} = \arg\max_\theta \prod_{i=1}^{n} P(x_i | \theta)$$

In practice, we maximize the log-likelihood (which is easier to work with because products become sums):

$$\hat{\theta}_{MLE} = \arg\max_\theta \sum_{i=1}^{n} \log P(x_i | \theta)$$

MLE is the foundation of training neural networks. When you train a classification model by minimizing cross-entropy loss, you are doing MLE.

---

## 7. Information Theory

Information theory, developed by Claude Shannon, provides the mathematical foundation for understanding information, compression, and communication. It is deeply connected to machine learning.

### Entropy

Entropy measures the uncertainty or "surprise" in a probability distribution:

$$H(X) = -\sum_{i} P(x_i) \log_2 P(x_i)$$

- A fair coin has entropy 1 bit (maximum uncertainty for two outcomes).
- A biased coin that always lands heads has entropy 0 bits (no uncertainty).
- A fair six-sided die has entropy $\log_2(6) \approx 2.585$ bits.

In AI, we typically use the natural logarithm (base $e$) instead of base 2, and the unit is called "nats":

$$H(X) = -\sum_{i} P(x_i) \ln P(x_i)$$

```python
def entropy(probs):
    probs = np.array(probs)
    # Avoid log(0) by filtering out zero probabilities
    probs = probs[probs > 0]
    return -np.sum(probs * np.log(probs))

# Fair coin
print(entropy([0.5, 0.5]))       # 0.693 nats

# Biased coin (90% heads)
print(entropy([0.9, 0.1]))       # 0.325 nats

# Certain outcome
print(entropy([1.0, 0.0]))       # 0.0 nats
```

### Cross-Entropy

Cross-entropy measures the average number of bits needed to encode data from distribution $P$ using a code optimized for distribution $Q$:

$$H(P, Q) = -\sum_{i} P(x_i) \log Q(x_i)$$

Cross-entropy is the most common loss function in classification tasks. If $P$ is the true distribution (one-hot label) and $Q$ is the model's predicted distribution:

$$\text{Loss} = -\sum_{i} y_i \log(\hat{y}_i)$$

Where $y_i$ is the true label (0 or 1) and $\hat{y}_i$ is the predicted probability.

For binary classification, this simplifies to:

$$\text{Loss} = -(y \log(\hat{y}) + (1-y) \log(1-\hat{y}))$$

```python
def cross_entropy(true_probs, predicted_probs):
    true_probs = np.array(true_probs)
    predicted_probs = np.array(predicted_probs)
    return -np.sum(true_probs * np.log(predicted_probs + 1e-10))

# True label: class 2 (out of 3 classes)
true = [0, 0, 1]

# Good prediction
good_pred = [0.05, 0.05, 0.9]
print("Good prediction loss:", cross_entropy(true, good_pred))  # 0.105

# Bad prediction
bad_pred = [0.7, 0.2, 0.1]
print("Bad prediction loss:", cross_entropy(true, bad_pred))    # 2.303
```

### KL Divergence (Kullback-Leibler Divergence)

KL divergence measures how different one probability distribution is from another:

$$D_{KL}(P \| Q) = \sum_{i} P(x_i) \log \frac{P(x_i)}{Q(x_i)}$$

Properties:
- $D_{KL}(P \| Q) \geq 0$ (always non-negative)
- $D_{KL}(P \| Q) = 0$ if and only if $P = Q$
- It is NOT symmetric: $D_{KL}(P \| Q) \neq D_{KL}(Q \| P)$

KL divergence is used in:
- Variational Autoencoders (VAEs)
- Policy optimization in reinforcement learning
- Knowledge distillation
- Measuring how far a model's distribution is from the true distribution

Note: Cross-entropy = Entropy + KL Divergence

$$H(P, Q) = H(P) + D_{KL}(P \| Q)$$

---

## 8. Optimization

Optimization is the process of finding the best parameters for a model. In AI, "best" usually means the parameters that minimize a loss function (a measure of how wrong the model's predictions are).

### Gradient Descent

Gradient descent is the fundamental optimization algorithm used in AI. The idea is simple:

1. Compute the gradient (the direction of steepest increase) of the loss function with respect to the parameters.
2. Move the parameters a small step in the opposite direction (to decrease the loss).
3. Repeat.

Mathematically:

$$\theta_{t+1} = \theta_t - \alpha \nabla L(\theta_t)$$

Where:
- $\theta$ are the parameters
- $\alpha$ is the learning rate (how big each step is)
- $\nabla L(\theta)$ is the gradient of the loss function
- $t$ is the step number

```python
# Gradient descent to find the minimum of f(x) = (x - 3)^2
# The minimum is at x = 3

def f(x):
    return (x - 3) ** 2

def df(x):
    return 2 * (x - 3)

x = 0.0             # Starting point
learning_rate = 0.1  # Step size

for step in range(50):
    gradient = df(x)
    x = x - learning_rate * gradient
    if step % 10 == 0:
        print(f"Step {step}: x = {x:.4f}, f(x) = {f(x):.6f}")

# Output:
# Step 0: x = 0.6000, f(x) = 5.760000
# Step 10: x = 2.8926, f(x) = 0.011529
# Step 20: x = 2.9988, f(x) = 0.000001
# Step 30: x = 3.0000, f(x) = 0.000000
# Step 40: x = 3.0000, f(x) = 0.000000
```

### Stochastic Gradient Descent (SGD)

Computing the gradient over the entire dataset is expensive. Stochastic Gradient Descent (SGD) computes the gradient over a small random subset of the data (a "mini-batch") and updates the parameters. This is faster and often works just as well.

Types of gradient descent:
- **Batch gradient descent**: Use the entire dataset for each update. Most accurate gradient but slowest.
- **Stochastic gradient descent**: Use one data point for each update. Very noisy but very fast.
- **Mini-batch gradient descent**: Use a small batch (e.g., 32, 64, 128 data points) for each update. The standard approach in practice.

### Learning Rate

The learning rate ($\alpha$) controls how big each parameter update is:
- **Too high**: The model overshoots the minimum and may diverge (the loss increases instead of decreasing).
- **Too low**: The model converges very slowly and may get stuck in a local minimum.
- **Just right**: The model converges smoothly to a good solution.

Common learning rates: 1e-3 (0.001), 1e-4 (0.0001), 3e-4 (0.0003)

**Learning rate scheduling**: Instead of using a fixed learning rate, it is common to start with a higher learning rate and gradually decrease it during training:
- **Step decay**: Multiply the learning rate by a factor (e.g., 0.1) every N epochs.
- **Cosine annealing**: Decrease the learning rate following a cosine curve.
- **Warmup**: Start with a very low learning rate and gradually increase it for the first few thousand steps, then decrease.

### Advanced Optimizers

In practice, plain SGD is rarely used. Modern optimizers add momentum and adaptive learning rates:

**SGD with Momentum**: Instead of just using the current gradient, also consider the direction of previous gradients. This helps the optimizer move smoothly through ravines in the loss landscape.

$$v_t = \beta v_{t-1} + \nabla L(\theta_t)$$
$$\theta_{t+1} = \theta_t - \alpha v_t$$

**Adam (Adaptive Moment Estimation)**: The most popular optimizer. It maintains running averages of both the gradient (first moment) and the squared gradient (second moment) and uses them to adapt the learning rate for each parameter.

$$m_t = \beta_1 m_{t-1} + (1 - \beta_1) \nabla L(\theta_t)$$
$$v_t = \beta_2 v_{t-1} + (1 - \beta_2) (\nabla L(\theta_t))^2$$
$$\hat{m}_t = \frac{m_t}{1 - \beta_1^t}$$
$$\hat{v}_t = \frac{v_t}{1 - \beta_2^t}$$
$$\theta_{t+1} = \theta_t - \alpha \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon}$$

Default hyperparameters: $\beta_1 = 0.9$, $\beta_2 = 0.999$, $\epsilon = 10^{-8}$

**AdamW**: A variant of Adam that handles weight decay (L2 regularization) differently and often works better for training large models.

### Convex vs. Non-Convex Optimization

A convex function has a single minimum (like a bowl). Gradient descent is guaranteed to find it.

A non-convex function has multiple minima, maxima, and saddle points (like a mountain range). Neural network loss functions are almost always non-convex. This means:
- Gradient descent is NOT guaranteed to find the global minimum.
- It may find a local minimum or a saddle point.
- In practice, for large neural networks, most local minima are "good enough" and the difference between them is small.

---

## 9. Putting It All Together

Let us see how all this math comes together in a concrete example: training a simple linear regression model from scratch.

```python
import numpy as np
import matplotlib.pyplot as plt

# Generate synthetic data: y = 2x + 1 + noise
np.random.seed(42)
X = np.random.randn(100, 1)  # 100 data points, 1 feature
y = 2 * X + 1 + 0.3 * np.random.randn(100, 1)  # True relationship: y = 2x + 1

# Initialize parameters randomly
w = np.random.randn(1, 1)  # Weight
b = np.zeros((1, 1))       # Bias

learning_rate = 0.1
n_epochs = 100

losses = []

for epoch in range(n_epochs):
    # Forward pass: compute predictions (LINEAR ALGEBRA: matrix multiplication)
    y_pred = X @ w + b  # X is (100,1), w is (1,1), result is (100,1)
    
    # Compute loss: Mean Squared Error (STATISTICS)
    loss = np.mean((y_pred - y) ** 2)
    losses.append(loss)
    
    # Compute gradients (CALCULUS: partial derivatives)
    dw = (2 / len(X)) * X.T @ (y_pred - y)  # Derivative of loss w.r.t. w
    db = (2 / len(X)) * np.sum(y_pred - y)   # Derivative of loss w.r.t. b
    
    # Update parameters (OPTIMIZATION: gradient descent)
    w = w - learning_rate * dw
    b = b - learning_rate * db
    
    if epoch % 20 == 0:
        print(f"Epoch {epoch}: Loss = {loss:.4f}, w = {w[0,0]:.4f}, b = {b[0,0]:.4f}")

print(f"\nFinal: w = {w[0,0]:.4f} (true: 2.0), b = {b[0,0]:.4f} (true: 1.0)")

# Plot the results
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Data and fitted line
axes[0].scatter(X, y, alpha=0.6, label='Data')
x_line = np.linspace(-3, 3, 100).reshape(-1, 1)
y_line = x_line @ w + b
axes[0].plot(x_line, y_line, 'r-', linewidth=2, label=f'Fitted: y = {w[0,0]:.2f}x + {b[0,0]:.2f}')
axes[0].set_xlabel('x')
axes[0].set_ylabel('y')
axes[0].set_title('Linear Regression')
axes[0].legend()
axes[0].grid(True)

# Plot 2: Loss over time
axes[1].plot(losses)
axes[1].set_xlabel('Epoch')
axes[1].set_ylabel('MSE Loss')
axes[1].set_title('Training Loss')
axes[1].grid(True)

plt.tight_layout()
plt.savefig('linear_regression.png')
plt.show()
```

This simple example demonstrates ALL the mathematical concepts in action:
- **Linear algebra**: Matrix multiplication (X @ w)
- **Calculus**: Computing gradients (derivatives of the loss function)
- **Statistics**: Mean squared error as the loss function
- **Optimization**: Gradient descent to find the best parameters
- **Probability**: The noise in the data follows a normal distribution

Every neural network training loop follows this same pattern, just with more complex models and loss functions.

---

## Summary

You now have the mathematical foundation for AI:

1. **Numbers and Arithmetic**: The basic building blocks
2. **Algebra**: Variables, equations, exponents, logarithms
3. **Functions**: Sigmoid, ReLU, softmax -- the building blocks of neural networks
4. **Linear Algebra**: Vectors, matrices, tensors, matrix multiplication -- the fundamental computations
5. **Calculus**: Derivatives, gradients, the chain rule -- how we compute how to improve
6. **Probability and Statistics**: Distributions, expected values, MLE -- the framework for learning from data
7. **Information Theory**: Entropy, cross-entropy, KL divergence -- measuring information and defining loss functions
8. **Optimization**: Gradient descent and its variants -- how we actually improve the model

Do not worry if you do not feel like you have mastered everything in this chapter. You will see these concepts applied repeatedly throughout the guide, and with each application, your understanding will deepen.

---

[<< Previous: Chapter 0 - Prerequisites](./00_PREREQUISITES_AND_SETUP.md) | [Next: Chapter 2 - Python Programming for AI >>](./02_PYTHON_PROGRAMMING.md)
