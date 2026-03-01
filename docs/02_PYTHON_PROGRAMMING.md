# Chapter 2: Python Programming for AI -- A Complete Guide

## Introduction

This chapter teaches you Python from absolute zero to the level needed for AI development. Every concept is explained thoroughly with examples. By the end of this chapter, you will be comfortable writing Python code for data processing, model building, and experimentation.

---

## Table of Contents

1. Running Python Code
2. Variables and Data Types
3. Operators
4. Strings
5. Lists, Tuples, and Sets
6. Dictionaries
7. Control Flow (if/elif/else)
8. Loops (for, while)
9. Functions
10. Classes and Object-Oriented Programming
11. File I/O
12. Error Handling
13. Modules and Imports
14. List Comprehensions and Generators
15. Lambda Functions
16. Decorators
17. NumPy -- The Foundation of Scientific Python
18. Pandas -- Data Manipulation
19. Matplotlib -- Visualization
20. Working with Data Files (CSV, JSON, Images)
21. Python Best Practices for AI

---

## 1. Running Python Code

There are several ways to run Python code:

### Method 1: Python Interactive Shell

Open a terminal and type `python` (or `python3`). You will see a prompt (`>>>`). Type Python code and press Enter to run it immediately.

```
>>> print("Hello, World!")
Hello, World!
>>> 2 + 3
5
>>> exit()
```

### Method 2: Python Script Files

Create a file with a `.py` extension (e.g., `hello.py`), write your code in it, and run it from the terminal:

```python
# hello.py
print("Hello, World!")
print("This is my first Python script.")
```

Run it:
```bash
python hello.py
```

### Method 3: Jupyter Notebook

Jupyter notebooks let you run code in "cells" and see the output immediately. This is the most common way to do AI experimentation.

```bash
jupyter notebook
```

This opens a web interface. Create a new notebook and start writing code in cells. Press Shift+Enter to run a cell.

### Method 4: VS Code

Open a `.py` file in VS Code. Click the play button in the top-right corner, or press Ctrl+Shift+P and select "Python: Run Python File in Terminal."

---

## 2. Variables and Data Types

A variable is a name that refers to a value. In Python, you create a variable by assigning a value to a name using the `=` operator.

```python
# Integer (whole number)
age = 25
print(age)          # 25
print(type(age))    # <class 'int'>

# Float (decimal number)
height = 5.9
print(height)       # 5.9
print(type(height)) # <class 'float'>

# String (text)
name = "Alice"
print(name)         # Alice
print(type(name))   # <class 'str'>

# Boolean (True or False)
is_student = True
print(is_student)   # True
print(type(is_student))  # <class 'bool'>

# None (represents "no value" or "nothing")
result = None
print(result)       # None
print(type(result)) # <class 'NoneType'>
```

### Variable Naming Rules

- Must start with a letter or underscore: `my_var`, `_private`, `Count`
- Can contain letters, numbers, and underscores: `data_2`, `model_v3`
- Cannot start with a number: `2nd_try` is INVALID
- Cannot be a Python keyword: `if`, `for`, `class`, `return`, etc.
- Case-sensitive: `Name` and `name` are different variables

### Naming Conventions in Python (PEP 8)

- **Variables and functions**: Use `snake_case` (lowercase with underscores): `learning_rate`, `batch_size`, `process_data()`
- **Classes**: Use `PascalCase` (capitalize each word): `NeuralNetwork`, `DataLoader`, `TransformerModel`
- **Constants**: Use `UPPER_SNAKE_CASE`: `MAX_EPOCHS`, `LEARNING_RATE`, `BATCH_SIZE`

### Type Conversion

```python
# String to integer
x = int("42")       # 42

# String to float
y = float("3.14")   # 3.14

# Number to string
s = str(42)          # "42"

# Float to integer (truncates, does not round)
n = int(3.7)         # 3

# Integer to float
f = float(5)         # 5.0

# Integer to boolean
print(bool(0))       # False
print(bool(1))       # True
print(bool(-5))      # True (any non-zero number is True)

# String to boolean
print(bool(""))      # False (empty string is False)
print(bool("hello")) # True (non-empty string is True)
```

---

## 3. Operators

### Arithmetic Operators

```python
a = 10
b = 3

print(a + b)    # Addition: 13
print(a - b)    # Subtraction: 7
print(a * b)    # Multiplication: 30
print(a / b)    # Division: 3.333...
print(a // b)   # Floor division: 3
print(a % b)    # Modulus (remainder): 1
print(a ** b)   # Exponentiation: 1000
```

### Comparison Operators

```python
print(5 == 5)    # Equal: True
print(5 != 3)    # Not equal: True
print(5 > 3)     # Greater than: True
print(5 < 3)     # Less than: False
print(5 >= 5)    # Greater than or equal: True
print(5 <= 3)    # Less than or equal: False
```

### Logical Operators

```python
print(True and True)    # True
print(True and False)   # False
print(True or False)    # True
print(False or False)   # False
print(not True)         # False
print(not False)        # True

# Practical example
age = 25
has_id = True
if age >= 18 and has_id:
    print("Allowed entry")
```

### Assignment Operators

```python
x = 10
x += 5    # x = x + 5 => 15
x -= 3    # x = x - 3 => 12
x *= 2    # x = x * 2 => 24
x /= 4    # x = x / 4 => 6.0
x //= 2   # x = x // 2 => 3.0
x **= 3   # x = x ** 3 => 27.0
```

---

## 4. Strings

Strings are sequences of characters. They are used for text data, file paths, labels, and much more.

```python
# Creating strings
s1 = "Hello"          # Double quotes
s2 = 'World'          # Single quotes (same thing)
s3 = """This is a     # Triple quotes for multi-line strings
multi-line
string"""
s4 = f"Name: {name}"  # f-string (formatted string) -- inserts variable values

# String operations
greeting = "Hello" + " " + "World"  # Concatenation: "Hello World"
repeated = "Ha" * 3                  # Repetition: "HaHaHa"
length = len("Hello")               # Length: 5

# Accessing characters (0-indexed)
s = "Python"
print(s[0])     # 'P' (first character)
print(s[-1])    # 'n' (last character)
print(s[1:4])   # 'yth' (characters 1, 2, 3 -- "slicing")
print(s[:3])    # 'Pyt' (first 3 characters)
print(s[3:])    # 'hon' (from character 3 to the end)

# String methods
text = "  Hello, World!  "
print(text.strip())         # "Hello, World!" (remove whitespace)
print(text.lower())         # "  hello, world!  "
print(text.upper())         # "  HELLO, WORLD!  "
print(text.replace("World", "AI"))  # "  Hello, AI!  "
print(text.split(","))      # ['  Hello', ' World!  ']
print("Hello World".split())  # ['Hello', 'World']
print("-".join(["a", "b", "c"]))  # "a-b-c"
print("hello".startswith("he"))   # True
print("hello".endswith("lo"))     # True
print("hello world".title())      # "Hello World"
print("42".isdigit())             # True
print("hello".isalpha())          # True

# Formatted strings (f-strings) -- VERY important for AI logging
epoch = 5
loss = 0.0342
accuracy = 95.7
print(f"Epoch {epoch}: Loss = {loss:.4f}, Accuracy = {accuracy:.1f}%")
# Output: Epoch 5: Loss = 0.0342, Accuracy = 95.7%

# Format specifications
print(f"{3.14159:.2f}")     # "3.14" (2 decimal places)
print(f"{42:05d}")          # "00042" (pad with zeros to 5 digits)
print(f"{1000000:,}")       # "1,000,000" (comma separator)
print(f"{0.857:.1%}")       # "85.7%" (percentage format)
```

---

## 5. Lists, Tuples, and Sets

### Lists

Lists are ordered, mutable (changeable) collections of items. They are the most commonly used data structure in Python.

```python
# Creating lists
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", 3.14, True, None]
empty = []
nested = [[1, 2], [3, 4], [5, 6]]

# Accessing elements
print(numbers[0])     # 1 (first element)
print(numbers[-1])    # 5 (last element)
print(numbers[1:4])   # [2, 3, 4] (slicing)
print(numbers[:3])    # [1, 2, 3]
print(numbers[::2])   # [1, 3, 5] (every 2nd element)
print(numbers[::-1])  # [5, 4, 3, 2, 1] (reversed)

# Modifying lists
numbers[0] = 10       # Change first element
numbers.append(6)     # Add to end: [10, 2, 3, 4, 5, 6]
numbers.insert(0, 0)  # Insert at position 0: [0, 10, 2, 3, 4, 5, 6]
numbers.extend([7, 8])  # Add multiple: [0, 10, 2, 3, 4, 5, 6, 7, 8]
numbers.remove(10)    # Remove first occurrence of 10
popped = numbers.pop()  # Remove and return last element
popped_at = numbers.pop(2)  # Remove and return element at index 2

# List operations
a = [1, 2, 3]
b = [4, 5, 6]
print(a + b)          # [1, 2, 3, 4, 5, 6] (concatenation)
print(a * 3)          # [1, 2, 3, 1, 2, 3, 1, 2, 3] (repetition)
print(len(a))         # 3
print(3 in a)         # True (membership test)
print(7 in a)         # False

# Sorting
nums = [3, 1, 4, 1, 5, 9, 2, 6]
nums.sort()           # Sort in-place: [1, 1, 2, 3, 4, 5, 6, 9]
nums.sort(reverse=True)  # Sort descending: [9, 6, 5, 4, 3, 2, 1, 1]
sorted_nums = sorted(nums)  # Return new sorted list (does not modify original)

# Useful functions
print(min(nums))      # Minimum
print(max(nums))      # Maximum
print(sum(nums))      # Sum

# Nested list (2D array) -- common for representing matrices before using NumPy
matrix = [[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]]
print(matrix[0][0])   # 1 (row 0, column 0)
print(matrix[1][2])   # 6 (row 1, column 2)
```

### Tuples

Tuples are ordered, immutable (unchangeable) collections. They are like lists but cannot be modified after creation. They are used for fixed collections of values.

```python
# Creating tuples
point = (3, 4)
rgb = (255, 128, 0)
single = (42,)        # Note the comma -- needed for single-element tuples

# Accessing elements (same as lists)
print(point[0])       # 3
print(point[1])       # 4

# Tuples are immutable
# point[0] = 5        # ERROR: TypeError

# Tuple unpacking (very useful)
x, y = point          # x = 3, y = 4
r, g, b = rgb         # r = 255, g = 128, b = 0

# Commonly used for returning multiple values from functions
def get_dimensions():
    return 1920, 1080  # Returns a tuple

width, height = get_dimensions()

# Shape tuples in NumPy/PyTorch
# A tensor might have shape (32, 3, 224, 224) meaning:
# 32 images, 3 color channels, 224 pixels height, 224 pixels width
```

### Sets

Sets are unordered collections of unique elements. Useful for removing duplicates and testing membership efficiently.

```python
# Creating sets
s = {1, 2, 3, 4, 5}
from_list = set([1, 2, 2, 3, 3, 3])  # {1, 2, 3} -- duplicates removed

# Set operations
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}
print(a | b)          # Union: {1, 2, 3, 4, 5, 6}
print(a & b)          # Intersection: {3, 4}
print(a - b)          # Difference: {1, 2}
print(a ^ b)          # Symmetric difference: {1, 2, 5, 6}

# Adding and removing
s.add(6)
s.remove(1)           # Raises error if not found
s.discard(10)         # Does nothing if not found

# Membership test (very fast -- O(1))
print(3 in s)         # True
```

---

## 6. Dictionaries

Dictionaries store key-value pairs. They are extremely useful for configuration, storing results, and mapping between values.

```python
# Creating dictionaries
person = {
    "name": "Alice",
    "age": 30,
    "city": "New York"
}

# Accessing values
print(person["name"])          # "Alice"
print(person.get("name"))     # "Alice"
print(person.get("phone", "N/A"))  # "N/A" (default if key does not exist)

# Modifying
person["age"] = 31             # Update
person["email"] = "a@b.com"   # Add new key
del person["city"]             # Delete a key

# Dictionary methods
print(person.keys())           # dict_keys(['name', 'age', 'email'])
print(person.values())         # dict_values(['Alice', 31, 'a@b.com'])
print(person.items())          # dict_items([('name', 'Alice'), ('age', 31), ...])

# Iterating over a dictionary
for key, value in person.items():
    print(f"{key}: {value}")

# Checking if a key exists
if "name" in person:
    print("Name found")

# Nested dictionaries (common for configurations)
config = {
    "model": {
        "type": "transformer",
        "num_layers": 12,
        "hidden_size": 768,
        "num_attention_heads": 12
    },
    "training": {
        "learning_rate": 3e-4,
        "batch_size": 32,
        "num_epochs": 10,
        "optimizer": "adamw"
    },
    "data": {
        "train_path": "data/train.csv",
        "val_path": "data/val.csv",
        "max_length": 512
    }
}

print(config["model"]["hidden_size"])  # 768
```

---

## 7. Control Flow

### if / elif / else

```python
temperature = 35

if temperature > 30:
    print("It is hot")
elif temperature > 20:
    print("It is warm")
elif temperature > 10:
    print("It is cool")
else:
    print("It is cold")

# Ternary operator (one-line if/else)
status = "hot" if temperature > 30 else "not hot"

# Practical AI example: choosing a device
import torch
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")
```

---

## 8. Loops

### for Loops

```python
# Iterating over a list
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# Iterating with index
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")

# range()
for i in range(5):          # 0, 1, 2, 3, 4
    print(i)

for i in range(2, 8):       # 2, 3, 4, 5, 6, 7
    print(i)

for i in range(0, 10, 2):   # 0, 2, 4, 6, 8 (step of 2)
    print(i)

# Iterating over a dictionary
config = {"lr": 0.001, "batch_size": 32, "epochs": 10}
for key, value in config.items():
    print(f"{key} = {value}")

# Nested loops
for i in range(3):
    for j in range(3):
        print(f"({i}, {j})", end=" ")
    print()

# zip() -- iterate over multiple lists simultaneously
names = ["Alice", "Bob", "Charlie"]
scores = [95, 87, 92]
for name, score in zip(names, scores):
    print(f"{name}: {score}")
```

### while Loops

```python
# Basic while loop
count = 0
while count < 5:
    print(count)
    count += 1

# Practical example: training until convergence
loss = 10.0
tolerance = 0.01
epoch = 0
while loss > tolerance:
    loss *= 0.9  # Simulate loss decreasing
    epoch += 1
    if epoch % 10 == 0:
        print(f"Epoch {epoch}: loss = {loss:.4f}")
print(f"Converged after {epoch} epochs")
```

### break and continue

```python
# break: exit the loop early
for i in range(100):
    if i == 5:
        break
    print(i)
# Prints: 0 1 2 3 4

# continue: skip the current iteration
for i in range(10):
    if i % 2 == 0:
        continue        # Skip even numbers
    print(i)
# Prints: 1 3 5 7 9
```

---

## 9. Functions

Functions are reusable blocks of code. They take inputs (parameters), do something, and optionally return an output.

```python
# Defining a function
def greet(name):
    """This is a docstring -- it documents what the function does."""
    return f"Hello, {name}!"

# Calling a function
message = greet("Alice")
print(message)  # "Hello, Alice!"

# Multiple parameters
def add(a, b):
    return a + b

# Default parameter values
def create_model(input_size, hidden_size=128, num_layers=3, dropout=0.1):
    print(f"Model: input={input_size}, hidden={hidden_size}, "
          f"layers={num_layers}, dropout={dropout}")
    # ... model creation code ...

create_model(784)                           # Uses all defaults
create_model(784, hidden_size=256)          # Override hidden_size
create_model(784, 256, 6, 0.2)             # Override all
create_model(784, dropout=0.3, num_layers=4)  # Keyword arguments (any order)

# Returning multiple values
def compute_stats(data):
    mean = sum(data) / len(data)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    std = variance ** 0.5
    return mean, variance, std

mean, var, std = compute_stats([1, 2, 3, 4, 5])
print(f"Mean: {mean}, Variance: {var}, Std: {std}")

# *args and **kwargs (variable number of arguments)
def flexible_function(*args, **kwargs):
    print(f"Positional arguments: {args}")
    print(f"Keyword arguments: {kwargs}")

flexible_function(1, 2, 3, name="Alice", age=30)
# Positional arguments: (1, 2, 3)
# Keyword arguments: {'name': 'Alice', 'age': 30}

# Type hints (optional but recommended for clarity)
def train_model(
    model_name: str,
    learning_rate: float = 1e-3,
    num_epochs: int = 10,
    use_gpu: bool = True
) -> dict:
    """Train a model and return metrics."""
    # ... training code ...
    return {"loss": 0.05, "accuracy": 0.97}
```

### Scope

Variables defined inside a function are local to that function:

```python
def my_function():
    x = 10  # Local variable
    print(x)

my_function()   # Prints 10
# print(x)     # ERROR: x is not defined outside the function

# Global variables
total = 0

def add_to_total(value):
    global total    # Declare that we want to modify the global variable
    total += value

add_to_total(5)
add_to_total(3)
print(total)     # 8
```

---

## 10. Classes and Object-Oriented Programming

Classes let you create custom data types that bundle data and behavior together. In AI, classes are used to define models, datasets, training loops, and more.

```python
# Defining a class
class Dog:
    # Class attribute (shared by all instances)
    species = "Canis familiaris"
    
    # Constructor (__init__ is called when you create an instance)
    def __init__(self, name, age):
        # Instance attributes (unique to each instance)
        self.name = name
        self.age = age
    
    # Method (a function that belongs to the class)
    def bark(self):
        return f"{self.name} says Woof!"
    
    # Another method
    def birthday(self):
        self.age += 1
        return f"{self.name} is now {self.age}"
    
    # String representation
    def __repr__(self):
        return f"Dog(name='{self.name}', age={self.age})"

# Creating instances
dog1 = Dog("Rex", 5)
dog2 = Dog("Buddy", 3)

print(dog1.bark())       # "Rex says Woof!"
print(dog2.birthday())   # "Buddy is now 4"
print(dog1)              # Dog(name='Rex', age=5)
```

### Inheritance

Inheritance allows a class to inherit attributes and methods from another class:

```python
class Animal:
    def __init__(self, name, sound):
        self.name = name
        self.sound = sound
    
    def speak(self):
        return f"{self.name} says {self.sound}"

class Dog(Animal):
    def __init__(self, name):
        super().__init__(name, "Woof")  # Call parent constructor
    
    def fetch(self):
        return f"{self.name} fetches the ball!"

class Cat(Animal):
    def __init__(self, name):
        super().__init__(name, "Meow")
    
    def purr(self):
        return f"{self.name} purrs..."

dog = Dog("Rex")
cat = Cat("Whiskers")
print(dog.speak())    # "Rex says Woof"
print(cat.speak())    # "Whiskers says Meow"
print(dog.fetch())    # "Rex fetches the ball!"
```

### Practical AI Example: A Simple Neural Network Class

```python
import numpy as np

class SimpleNeuralNetwork:
    """A simple 2-layer neural network for classification."""
    
    def __init__(self, input_size, hidden_size, output_size):
        # Initialize weights randomly
        self.W1 = np.random.randn(input_size, hidden_size) * 0.01
        self.b1 = np.zeros((1, hidden_size))
        self.W2 = np.random.randn(hidden_size, output_size) * 0.01
        self.b2 = np.zeros((1, output_size))
    
    def relu(self, x):
        return np.maximum(0, x)
    
    def softmax(self, x):
        exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=1, keepdims=True)
    
    def forward(self, X):
        """Forward pass: compute predictions."""
        self.z1 = X @ self.W1 + self.b1
        self.a1 = self.relu(self.z1)
        self.z2 = self.a1 @ self.W2 + self.b2
        self.a2 = self.softmax(self.z2)
        return self.a2
    
    def predict(self, X):
        """Return predicted class indices."""
        probs = self.forward(X)
        return np.argmax(probs, axis=1)

# Usage
model = SimpleNeuralNetwork(input_size=784, hidden_size=128, output_size=10)
X_sample = np.random.randn(5, 784)  # 5 samples, 784 features (28x28 images)
predictions = model.predict(X_sample)
print(f"Predictions: {predictions}")  # Array of 5 predicted digits (0-9)
```

---

## 11. File I/O

Reading and writing files is essential for loading datasets, saving models, and logging results.

```python
# Writing to a text file
with open("output.txt", "w") as f:
    f.write("Hello, World!\n")
    f.write("This is line 2.\n")

# Reading from a text file
with open("output.txt", "r") as f:
    content = f.read()
    print(content)

# Reading line by line
with open("output.txt", "r") as f:
    for line in f:
        print(line.strip())

# Appending to a file
with open("output.txt", "a") as f:
    f.write("This is a new line.\n")

# Writing and reading JSON
import json

config = {
    "learning_rate": 0.001,
    "batch_size": 32,
    "model": "transformer"
}

# Write JSON
with open("config.json", "w") as f:
    json.dump(config, f, indent=2)

# Read JSON
with open("config.json", "r") as f:
    loaded_config = json.load(f)
print(loaded_config)

# Using pickle for saving Python objects (like trained models)
import pickle

data = {"weights": [1.0, 2.0, 3.0], "bias": 0.5}

# Save
with open("model.pkl", "wb") as f:
    pickle.dump(data, f)

# Load
with open("model.pkl", "rb") as f:
    loaded_data = pickle.load(f)
```

---

## 12. Error Handling

```python
# try/except blocks
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero!")

# Catching multiple exceptions
try:
    x = int("hello")
except ValueError:
    print("Invalid number!")
except TypeError:
    print("Wrong type!")

# Generic exception (catch everything)
try:
    risky_operation()
except Exception as e:
    print(f"Error: {e}")

# try/except/else/finally
try:
    result = 10 / 2
except ZeroDivisionError:
    print("Division error")
else:
    print(f"Success: {result}")  # Runs only if no exception
finally:
    print("This always runs")   # Runs no matter what

# Raising exceptions
def validate_batch_size(batch_size):
    if batch_size <= 0:
        raise ValueError(f"Batch size must be positive, got {batch_size}")
    if batch_size > 1024:
        raise ValueError(f"Batch size too large: {batch_size}")
    return batch_size

# Practical AI example: safe model loading
def load_model(path):
    try:
        model = torch.load(path)
        print(f"Model loaded from {path}")
        return model
    except FileNotFoundError:
        print(f"Model file not found: {path}")
        return None
    except RuntimeError as e:
        print(f"Error loading model: {e}")
        return None
```

---

## 13. Modules and Imports

Python's power comes from its vast ecosystem of modules (libraries). Here is how to use them:

```python
# Import an entire module
import math
print(math.pi)        # 3.14159...
print(math.sqrt(16))  # 4.0

# Import specific items
from math import pi, sqrt
print(pi)
print(sqrt(16))

# Import with an alias
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.optim as optim

# Common AI imports (you will see these at the top of almost every AI script)
import os
import sys
import time
import json
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
```

### Creating Your Own Modules

Create a file called `my_utils.py`:

```python
# my_utils.py

def normalize(data):
    """Normalize data to [0, 1] range."""
    min_val = min(data)
    max_val = max(data)
    return [(x - min_val) / (max_val - min_val) for x in data]

def accuracy(predictions, labels):
    """Compute accuracy."""
    correct = sum(p == l for p, l in zip(predictions, labels))
    return correct / len(labels)
```

Use it in another file:

```python
from my_utils import normalize, accuracy

data = [10, 20, 30, 40, 50]
print(normalize(data))  # [0.0, 0.25, 0.5, 0.75, 1.0]
```

---

## 14. List Comprehensions and Generators

### List Comprehensions

A concise way to create lists:

```python
# Traditional way
squares = []
for i in range(10):
    squares.append(i ** 2)

# List comprehension (same result, one line)
squares = [i ** 2 for i in range(10)]
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# With a condition
even_squares = [i ** 2 for i in range(10) if i % 2 == 0]
# [0, 4, 16, 36, 64]

# Nested comprehension
matrix = [[i * j for j in range(4)] for i in range(3)]
# [[0, 0, 0, 0], [0, 1, 2, 3], [0, 2, 4, 6]]

# Dictionary comprehension
word_lengths = {word: len(word) for word in ["hello", "world", "python"]}
# {'hello': 5, 'world': 5, 'python': 6}

# Set comprehension
unique_lengths = {len(word) for word in ["cat", "dog", "fish", "ant"]}
# {3, 4}
```

### Generators

Generators produce items one at a time instead of creating the entire list in memory. This is crucial for working with large datasets:

```python
# Generator expression (like list comprehension but with parentheses)
squares_gen = (i ** 2 for i in range(1000000))
# This does NOT create a list of 1 million items in memory

# Generator function (uses yield instead of return)
def data_generator(file_path, batch_size):
    """Generate batches of data from a file."""
    batch = []
    with open(file_path, "r") as f:
        for line in f:
            batch.append(line.strip())
            if len(batch) == batch_size:
                yield batch
                batch = []
    if batch:  # Yield remaining items
        yield batch

# Use it
for batch in data_generator("data.txt", batch_size=32):
    process(batch)
```

---

## 15. Lambda Functions

Lambda functions are small anonymous (nameless) functions:

```python
# Regular function
def add(a, b):
    return a + b

# Equivalent lambda
add = lambda a, b: a + b
print(add(3, 4))  # 7

# Common uses
# Sorting with a custom key
words = ["banana", "apple", "cherry", "date"]
words.sort(key=lambda w: len(w))
# ['date', 'apple', 'banana', 'cherry']

# Using with map, filter
numbers = [1, 2, 3, 4, 5]
doubled = list(map(lambda x: x * 2, numbers))     # [2, 4, 6, 8, 10]
evens = list(filter(lambda x: x % 2 == 0, numbers))  # [2, 4]
```

---

## 16. Decorators

Decorators modify the behavior of functions. They are used extensively in AI frameworks:

```python
# A simple decorator
def timer(func):
    """Measure execution time of a function."""
    import time
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f} seconds")
        return result
    return wrapper

@timer
def train_epoch(data):
    # Simulate training
    import time
    time.sleep(1)
    return {"loss": 0.05}

result = train_epoch(None)  # Prints: train_epoch took 1.00 seconds

# PyTorch uses decorators like:
# @torch.no_grad()      -- disable gradient computation (for inference)
# @torch.jit.script     -- compile a function for faster execution
```

---

## 17. NumPy -- The Foundation of Scientific Python

NumPy is the most important library for AI. It provides fast array operations that are the foundation of all deep learning frameworks.

```python
import numpy as np

# Creating arrays
a = np.array([1, 2, 3, 4, 5])              # From a list
b = np.zeros((3, 4))                         # 3x4 array of zeros
c = np.ones((2, 3))                          # 2x3 array of ones
d = np.full((3, 3), 7)                       # 3x3 array filled with 7
e = np.eye(4)                                # 4x4 identity matrix
f = np.arange(0, 10, 2)                      # [0, 2, 4, 6, 8]
g = np.linspace(0, 1, 5)                     # [0, 0.25, 0.5, 0.75, 1.0]
h = np.random.randn(3, 4)                    # 3x4 array of random normal values
i = np.random.rand(3, 4)                     # 3x4 array of random uniform [0,1)
j = np.random.randint(0, 10, size=(3, 4))    # 3x4 random integers [0, 10)

# Array properties
arr = np.random.randn(3, 4, 5)
print(arr.shape)      # (3, 4, 5) -- dimensions
print(arr.ndim)       # 3 -- number of dimensions
print(arr.size)       # 60 -- total number of elements
print(arr.dtype)      # float64 -- data type

# Reshaping
a = np.arange(12)                  # [0, 1, 2, ..., 11]
b = a.reshape(3, 4)               # 3x4 matrix
c = a.reshape(2, 2, 3)            # 2x2x3 tensor
d = a.reshape(-1, 4)              # -1 means "figure it out": 3x4
e = b.flatten()                    # Back to 1D
f = b.T                           # Transpose

# Indexing and slicing
arr = np.array([[1, 2, 3],
                [4, 5, 6],
                [7, 8, 9]])

print(arr[0, 0])          # 1
print(arr[1])             # [4, 5, 6] (second row)
print(arr[:, 1])          # [2, 5, 8] (second column)
print(arr[0:2, 1:3])      # [[2, 3], [5, 6]] (subarray)

# Boolean indexing (filtering)
data = np.array([1, -2, 3, -4, 5])
print(data[data > 0])     # [1, 3, 5] -- only positive values
print(data[data > 0].mean())  # 3.0

# Arithmetic (element-wise by default)
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
print(a + b)       # [5, 7, 9]
print(a * b)       # [4, 10, 18]
print(a ** 2)      # [1, 4, 9]
print(np.sqrt(a))  # [1.0, 1.414, 1.732]
print(np.exp(a))   # [2.718, 7.389, 20.086]
print(np.log(a))   # [0.0, 0.693, 1.099]

# Matrix operations
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])
print(A @ B)              # Matrix multiplication
print(np.dot(A, B))       # Same thing
print(A * B)              # Element-wise multiplication (NOT matrix multiplication)
print(np.linalg.inv(A))   # Inverse
print(np.linalg.det(A))   # Determinant
eigenvalues, eigenvectors = np.linalg.eig(A)

# Statistics
data = np.random.randn(1000)
print(np.mean(data))      # Mean
print(np.std(data))       # Standard deviation
print(np.var(data))       # Variance
print(np.median(data))    # Median
print(np.min(data))       # Minimum
print(np.max(data))       # Maximum
print(np.percentile(data, [25, 50, 75]))  # Quartiles

# Aggregation along axes
M = np.array([[1, 2, 3],
              [4, 5, 6]])
print(np.sum(M))            # 21 (sum of all elements)
print(np.sum(M, axis=0))    # [5, 7, 9] (sum of each column)
print(np.sum(M, axis=1))    # [6, 15] (sum of each row)
print(np.mean(M, axis=0))   # [2.5, 3.5, 4.5] (mean of each column)

# Random number generation (with seed for reproducibility)
np.random.seed(42)  # Set seed for reproducible results
print(np.random.randn(3))  # Always produces the same random numbers

# Using a Generator (modern approach)
rng = np.random.default_rng(42)
print(rng.normal(0, 1, size=(3,)))  # Normal distribution
print(rng.uniform(0, 1, size=(3,))) # Uniform distribution
print(rng.integers(0, 10, size=(3,)))  # Random integers
```

---

## 18. Pandas -- Data Manipulation

Pandas is used for working with tabular data (CSV files, databases, etc.):

```python
import pandas as pd

# Creating a DataFrame from a dictionary
df = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie", "Diana"],
    "age": [25, 30, 35, 28],
    "score": [95.5, 87.3, 92.1, 88.7],
    "passed": [True, True, True, True]
})

print(df)
#       name  age  score  passed
# 0    Alice   25   95.5    True
# 1      Bob   30   87.3    True
# 2  Charlie   35   92.1    True
# 3    Diana   28   88.7    True

# Reading CSV files
# df = pd.read_csv("data.csv")
# df = pd.read_csv("data.csv", sep="\t")  # Tab-separated

# Basic exploration
print(df.head())        # First 5 rows
print(df.tail())        # Last 5 rows
print(df.shape)         # (4, 4) -- 4 rows, 4 columns
print(df.columns)       # Column names
print(df.dtypes)        # Column data types
print(df.describe())    # Summary statistics
print(df.info())        # Data types and non-null counts

# Selecting data
print(df["name"])           # Single column (returns Series)
print(df[["name", "age"]])  # Multiple columns (returns DataFrame)
print(df.iloc[0])           # First row by index
print(df.iloc[0:2])         # First two rows
print(df.loc[df["age"] > 28])  # Filter rows

# Adding/modifying columns
df["grade"] = df["score"].apply(lambda s: "A" if s >= 90 else "B")
df["age_in_months"] = df["age"] * 12

# Sorting
df_sorted = df.sort_values("score", ascending=False)

# Grouping and aggregation
grouped = df.groupby("grade")["score"].mean()
print(grouped)

# Saving
# df.to_csv("output.csv", index=False)
```

---

## 19. Matplotlib -- Visualization

```python
import matplotlib.pyplot as plt
import numpy as np

# Line plot
x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(10, 6))
plt.plot(x, y, label="sin(x)", color="blue", linewidth=2)
plt.plot(x, np.cos(x), label="cos(x)", color="red", linewidth=2, linestyle="--")
plt.xlabel("x")
plt.ylabel("y")
plt.title("Trigonometric Functions")
plt.legend()
plt.grid(True)
plt.savefig("plot.png", dpi=150)
plt.show()

# Subplots (multiple plots in one figure)
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Training loss plot
epochs = range(1, 101)
train_loss = [1.0 / (1 + 0.05 * e) for e in epochs]
val_loss = [1.0 / (1 + 0.04 * e) + 0.05 * np.random.rand() for e in epochs]

axes[0, 0].plot(epochs, train_loss, label="Train")
axes[0, 0].plot(epochs, val_loss, label="Validation")
axes[0, 0].set_title("Loss")
axes[0, 0].legend()
axes[0, 0].grid(True)

# Scatter plot
x = np.random.randn(100)
y = 2 * x + 1 + np.random.randn(100) * 0.5
axes[0, 1].scatter(x, y, alpha=0.6)
axes[0, 1].set_title("Scatter Plot")
axes[0, 1].grid(True)

# Histogram
data = np.random.randn(1000)
axes[1, 0].hist(data, bins=30, color="skyblue", edgecolor="black")
axes[1, 0].set_title("Histogram")

# Bar chart
categories = ["Cat", "Dog", "Bird", "Fish"]
counts = [30, 45, 20, 15]
axes[1, 1].bar(categories, counts, color=["red", "blue", "green", "orange"])
axes[1, 1].set_title("Bar Chart")

plt.tight_layout()
plt.savefig("subplots.png", dpi=150)
plt.show()

# Heatmap (useful for confusion matrices)
confusion_matrix = np.array([[45, 5, 0],
                              [3, 42, 5],
                              [1, 4, 45]])

plt.figure(figsize=(8, 6))
plt.imshow(confusion_matrix, cmap="Blues")
plt.colorbar()
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
for i in range(3):
    for j in range(3):
        plt.text(j, i, str(confusion_matrix[i, j]),
                ha="center", va="center", fontsize=14)
plt.xticks([0, 1, 2], ["Cat", "Dog", "Bird"])
plt.yticks([0, 1, 2], ["Cat", "Dog", "Bird"])
plt.savefig("confusion_matrix.png", dpi=150)
plt.show()
```

---

## 20. Working with Data Files

### CSV Files

```python
import csv

# Reading CSV manually
with open("data.csv", "r") as f:
    reader = csv.reader(f)
    header = next(reader)       # First row is usually the header
    for row in reader:
        print(row)

# With pandas (much easier)
import pandas as pd
df = pd.read_csv("data.csv")
```

### JSON Files

```python
import json

# Reading JSON
with open("config.json", "r") as f:
    data = json.load(f)

# Writing JSON
with open("results.json", "w") as f:
    json.dump({"accuracy": 0.95, "loss": 0.05}, f, indent=2)
```

### Image Files

```python
from PIL import Image
import numpy as np

# Loading an image
img = Image.open("photo.jpg")
print(img.size)           # (width, height)
print(img.mode)           # 'RGB' for color, 'L' for grayscale

# Convert to NumPy array
arr = np.array(img)
print(arr.shape)          # (height, width, 3) for RGB
print(arr.dtype)          # uint8 (values 0-255)

# Resize
img_resized = img.resize((224, 224))

# Convert to grayscale
img_gray = img.convert("L")

# Save
img_resized.save("resized.jpg")
```

---

## 21. Python Best Practices for AI

### Use Virtual Environments

Always use a virtual environment for each project. This prevents dependency conflicts.

### Set Random Seeds for Reproducibility

```python
import random
import numpy as np
import torch

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

set_seed(42)
```

### Use Logging Instead of Print

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("training.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

logger.info("Starting training...")
logger.warning("GPU memory is low")
logger.error("Failed to load data")
```

### Use argparse for Command-Line Arguments

```python
import argparse

parser = argparse.ArgumentParser(description="Train a neural network")
parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
parser.add_argument("--epochs", type=int, default=10, help="Number of epochs")
parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
parser.add_argument("--model", type=str, default="resnet18", help="Model name")
parser.add_argument("--gpu", action="store_true", help="Use GPU")

args = parser.parse_args()
print(f"Training with lr={args.lr}, epochs={args.epochs}")
```

### Use tqdm for Progress Bars

```python
from tqdm import tqdm
import time

for i in tqdm(range(100), desc="Training"):
    time.sleep(0.05)  # Simulate work
# Training: 100%|##########| 100/100 [00:05<00:00, 19.82it/s]
```

### Use Type Hints

```python
from typing import List, Dict, Optional, Tuple

def train(
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    train_loader: DataLoader,
    num_epochs: int = 10,
    device: str = "cpu"
) -> Dict[str, List[float]]:
    """Train the model and return metrics history."""
    history = {"train_loss": [], "train_acc": []}
    # ... training code ...
    return history
```

---

## Summary

You now have a solid foundation in Python programming for AI. The key concepts are:

1. **Variables and data types**: int, float, str, bool, list, dict, tuple, set
2. **Control flow**: if/elif/else, for loops, while loops
3. **Functions**: Defining, calling, parameters, return values
4. **Classes**: Object-oriented programming, inheritance
5. **File I/O**: Reading and writing text, JSON, CSV, images
6. **NumPy**: Array operations, linear algebra, random numbers
7. **Pandas**: DataFrames, data manipulation, CSV handling
8. **Matplotlib**: Plotting, visualization
9. **Best practices**: Seeds, logging, argparse, tqdm, type hints

---

[<< Previous: Chapter 1 - Mathematics](./01_MATHEMATICS_FOUNDATION.md) | [Next: Chapter 3 - Machine Learning Fundamentals >>](./03_ML_FUNDAMENTALS.md)
