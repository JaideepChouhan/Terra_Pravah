# Chapter 0: Prerequisites, Environment Setup, and Foundational Concepts

## Who This Guide Is For

This guide is written for anyone -- literally anyone -- who wants to understand how artificial intelligence models work and how to build them from scratch. You do not need a computer science degree. You do not need to have ever written a line of code. You do not need to know calculus or linear algebra. Every single concept is explained from the ground up. If you can read and follow instructions, you can build an AI model by the end of this guide.

This is not a surface-level tutorial. This is a comprehensive, exhaustive reference that covers every layer of knowledge required to go from zero to building state-of-the-art AI systems. We cover text generation, image generation, 3D model generation, reinforcement learning, and everything in between.

---

## Table of Contents for This Chapter

1. What Is a Computer, Really?
2. How Computers Store and Process Information
3. What Is Software?
4. What Is a Programming Language?
5. Installing Your Operating System Tools
6. Installing Python
7. Understanding the Command Line / Terminal
8. Setting Up a Code Editor
9. Understanding File Systems
10. Installing Git and Version Control Basics
11. Setting Up a Virtual Environment
12. Installing Core Libraries
13. Understanding Hardware: CPU, GPU, RAM, Storage
14. Cloud Computing Options
15. What Is AI? A Bird's Eye View

---

## 1. What Is a Computer, Really?

A computer is a machine that processes information. At its core, it does exactly four things:

1. **Input**: It receives data (from a keyboard, mouse, file, network, sensor, camera, microphone, or any other source).
2. **Storage**: It stores data in memory (temporarily in RAM, or permanently on a hard drive or SSD).
3. **Processing**: It manipulates data according to a set of instructions (a program).
4. **Output**: It produces results (on a screen, to a file, over a network, to a speaker, etc.).

Every single thing a computer does -- from displaying a web page to training a neural network that generates human-like text -- is some combination of these four operations.

### The Central Processing Unit (CPU)

The CPU is the "brain" of the computer. It executes instructions one at a time (or a few at a time, in modern processors). Each instruction is extremely simple: add two numbers, compare two numbers, move a piece of data from one location to another. The power of a computer comes from the fact that it can execute billions of these simple instructions per second.

A modern CPU has multiple "cores," each of which can execute instructions independently. A quad-core CPU can do four things at once. An eight-core CPU can do eight things at once. This matters for AI because training models involves doing the same operation on millions of pieces of data, and having more cores means you can do more of these operations simultaneously.

### Random Access Memory (RAM)

RAM is the computer's short-term memory. When you open a program, its code and the data it needs are loaded from the hard drive into RAM so the CPU can access them quickly. RAM is fast but temporary -- when you turn off the computer, everything in RAM disappears.

For AI work, RAM matters because datasets and model parameters need to fit in memory during training. A typical laptop has 8-16 GB of RAM. For serious AI work, you often want 32 GB or more. For very large models, you might need hundreds of gigabytes, which is where specialized hardware and distributed computing come in.

### Storage (Hard Drives and SSDs)

Storage is the computer's long-term memory. Unlike RAM, data on a hard drive or SSD persists when the computer is turned off. There are two main types:

- **Hard Disk Drives (HDD)**: Use spinning magnetic platters. Slower but cheaper per gigabyte. Good for storing large datasets you do not access frequently.
- **Solid State Drives (SSD)**: Use flash memory chips. Much faster than HDDs. Programs load faster, files open faster. Preferred for your operating system and active projects.

For AI, you will often work with datasets that are tens or hundreds of gigabytes in size. Having enough storage and fast enough read speeds matters.

### The Graphics Processing Unit (GPU)

The GPU was originally designed to render graphics for video games. It turns out that the same kind of computation that makes video game graphics work -- performing the same mathematical operation on thousands of data points simultaneously -- is exactly what is needed for training neural networks.

A CPU might have 8-16 cores. A modern GPU has thousands of smaller cores. While each individual GPU core is simpler and slower than a CPU core, the sheer number of them means that for certain types of computation (called "parallel computation"), a GPU can be 10 to 100 times faster than a CPU.

For AI work, NVIDIA GPUs are the standard because of their CUDA platform, which is a software framework that lets you write programs that run on GPU cores. The most commonly used GPUs for AI are:

- **Consumer GPUs**: NVIDIA RTX 3060 (12 GB VRAM), RTX 3080 (10 GB), RTX 3090 (24 GB), RTX 4060 (8 GB), RTX 4070 (12 GB), RTX 4080 (16 GB), RTX 4090 (24 GB)
- **Professional/Data Center GPUs**: NVIDIA A100 (40/80 GB), H100 (80 GB), A6000 (48 GB)

The amount of VRAM (Video RAM, the GPU's own memory) is critical for AI. Larger models require more VRAM. A 7-billion parameter language model typically needs about 14-28 GB of VRAM depending on precision.

---

## 2. How Computers Store and Process Information

### Binary: The Language of Computers

Computers store all information as sequences of 0s and 1s. Each 0 or 1 is called a "bit" (binary digit). A group of 8 bits is called a "byte."

Why binary? Because the fundamental building blocks of a computer are transistors -- tiny electronic switches that can be either ON (1) or OFF (0). Everything a computer does is built on top of these simple switches.

Here is how numbers are represented in binary:

```
Decimal:  0    1    2    3    4    5    6    7    8    9    10
Binary:   0    1    10   11   100  101  110  111  1000 1001 1010
```

Each position in a binary number represents a power of 2 (just like each position in a decimal number represents a power of 10):

```
Binary: 1    0    1    1
        |    |    |    |
        2^3  2^2  2^1  2^0
        8    4    2    1

So 1011 in binary = 8 + 0 + 2 + 1 = 11 in decimal
```

### How Text Is Stored

Text is stored by assigning each character a number. The most common system is called ASCII (American Standard Code for Information Interchange), which assigns numbers 0-127 to characters:

```
'A' = 65
'B' = 66
'a' = 97
'b' = 98
'0' = 48
'1' = 49
' ' (space) = 32
```

Modern computers use Unicode, which extends this to cover every writing system in the world (including Chinese characters, Arabic script, Devanagari, and many more), assigning numbers up to over 1 million.

The most common encoding of Unicode is UTF-8, which uses 1-4 bytes per character. ASCII characters use 1 byte each.

### How Images Are Stored

A digital image is a grid of tiny colored dots called pixels. Each pixel has a color, typically represented as three numbers: one for Red, one for Green, and one for Blue (RGB). Each number ranges from 0 to 255 (one byte).

So a single pixel takes 3 bytes. A 1920x1080 image (Full HD) has 1920 * 1080 = 2,073,600 pixels, each taking 3 bytes, for a total of about 6.2 megabytes of raw data. In practice, images are compressed using formats like JPEG or PNG to take up less space.

### How Numbers Are Stored in AI

In AI, we work extensively with decimal numbers (called "floating-point numbers"). The most common formats are:

- **float32 (FP32)**: 32 bits (4 bytes) per number. This is the standard precision. Offers about 7 decimal digits of precision.
- **float16 (FP16)**: 16 bits (2 bytes) per number. Half precision. Less accurate but uses half the memory and can be computed twice as fast on modern GPUs. Adequate for most AI training.
- **bfloat16 (BF16)**: 16 bits, but with a different split between range and precision than FP16. Preferred by Google's TPUs and increasingly common.
- **float64 (FP64)**: 64 bits (8 bytes) per number. Double precision. Rarely needed for AI but used in scientific computing.
- **int8**: 8 bits (1 byte) per number. Only whole numbers from -128 to 127 (or 0 to 255 for unsigned). Used in "quantized" models that sacrifice a tiny bit of accuracy for huge memory savings.
- **int4**: 4 bits per number. Even more aggressive quantization. Used to run very large language models on consumer hardware.

Understanding these formats matters because: a model with 7 billion parameters stored in float32 takes 28 GB of memory (7 billion * 4 bytes). The same model in float16 takes 14 GB. In int8, it takes 7 GB. In int4, it takes 3.5 GB. This can be the difference between a model fitting on your GPU or not.

---

## 3. What Is Software?

Software is a set of instructions that tells the computer what to do. There are several layers:

### The Operating System (OS)

The operating system is the foundational software that manages the computer's hardware and provides services for other programs. The three main operating systems are:

- **Windows**: Made by Microsoft. The most common desktop OS. Versions include Windows 10 and Windows 11.
- **macOS**: Made by Apple. Runs only on Apple hardware. Known for its polished interface.
- **Linux**: Free and open-source. Comes in many "distributions" (distros) like Ubuntu, Fedora, Debian, Arch Linux. The preferred OS for AI development because most AI tools and servers run on Linux.

For AI development, Linux (especially Ubuntu) is the most common choice because:
1. Most AI frameworks are developed on and tested on Linux first.
2. GPU drivers and CUDA are most reliable on Linux.
3. Most cloud servers run Linux.
4. Docker containers (which we will discuss later) run natively on Linux.

If you are on Windows, you have several options:
- Use Windows Subsystem for Linux (WSL2), which lets you run a Linux environment inside Windows.
- Dual-boot with Linux.
- Use a cloud server running Linux.
- Many tools also work natively on Windows, though you may encounter occasional compatibility issues.

### Applications and Programs

An application is a program that performs a specific task. A web browser is an application. A text editor is an application. A Python script that trains a neural network is an application.

### Libraries and Frameworks

A library is a collection of pre-written code that you can use in your own programs. Instead of writing everything from scratch, you use libraries to handle common tasks. For AI, the key libraries include:

- **NumPy**: A library for working with arrays of numbers efficiently.
- **PyTorch**: A deep learning framework made by Facebook/Meta. Currently the most popular framework for AI research.
- **TensorFlow**: A deep learning framework made by Google. Very popular in production environments.
- **Hugging Face Transformers**: A library that provides pre-trained models and tools for natural language processing.
- **scikit-learn**: A library for classical machine learning algorithms.
- **Matplotlib**: A library for creating charts and graphs.
- **Pandas**: A library for working with tabular data.

---

## 4. What Is a Programming Language?

A programming language is a formal language that lets you write instructions for a computer. Just as human languages have grammar and vocabulary, programming languages have syntax (rules for how to write valid code) and semantics (what the code means).

### Why Python?

Python is the dominant language for AI and machine learning for several reasons:

1. **Readability**: Python code reads almost like English. There are no curly braces, no semicolons at the end of lines, and indentation is used to define code blocks.
2. **Ecosystem**: Python has the richest ecosystem of AI and machine learning libraries.
3. **Community**: The vast majority of AI tutorials, research code, and tools are written in Python.
4. **Flexibility**: Python is a general-purpose language, so you can use it for data processing, web development, automation, and more.
5. **Interoperability**: Python can call code written in C and C++ (which is how NumPy and PyTorch achieve their speed).

### Python Basics Preview

Here is what Python code looks like:

```python
# This is a comment. The computer ignores it.
# Comments are for humans reading the code.

# Variables: storing values
name = "Alice"          # A string (text)
age = 30                # An integer (whole number)
height = 5.6            # A float (decimal number)
is_student = True       # A boolean (True or False)

# Printing output
print("Hello, my name is", name)
print("I am", age, "years old")

# Arithmetic
x = 10
y = 3
print(x + y)    # Addition: 13
print(x - y)    # Subtraction: 7
print(x * y)    # Multiplication: 30
print(x / y)    # Division: 3.3333...
print(x ** y)   # Exponentiation (10^3): 1000
print(x % y)    # Modulus (remainder): 1
print(x // y)   # Floor division: 3

# Conditional statements
if age >= 18:
    print("You are an adult")
elif age >= 13:
    print("You are a teenager")
else:
    print("You are a child")

# Loops
for i in range(5):      # i goes from 0 to 4
    print(i)

# Lists (arrays)
numbers = [1, 2, 3, 4, 5]
print(numbers[0])       # First element: 1
print(numbers[-1])      # Last element: 5
numbers.append(6)       # Add to end
print(len(numbers))     # Length: 6

# Functions
def add(a, b):
    return a + b

result = add(3, 4)
print(result)           # 7

# Dictionaries (key-value pairs)
person = {
    "name": "Alice",
    "age": 30,
    "city": "New York"
}
print(person["name"])   # Alice
```

Do not worry about memorizing all of this now. We will use Python extensively throughout this guide, and you will learn by doing.

---

## 5. Installing Your Operating System Tools

### On Windows

#### Step 1: Update Windows

1. Click the Start button (the Windows icon in the bottom-left or bottom-center of the screen).
2. Click the gear icon (Settings).
3. Click "Update & Security" (or "Windows Update" on Windows 11).
4. Click "Check for updates."
5. Install any available updates and restart your computer if prompted.

#### Step 2: Install Windows Terminal (if you do not have it)

Windows Terminal is a modern terminal application that lets you use PowerShell, Command Prompt, and WSL.

1. Open the Microsoft Store (search for "Microsoft Store" in the Start menu).
2. Search for "Windows Terminal."
3. Click "Install."

#### Step 3: Install WSL2 (Windows Subsystem for Linux)

WSL2 lets you run a full Linux environment inside Windows. This is highly recommended for AI development.

1. Open Windows Terminal or PowerShell as Administrator:
   - Right-click the Start button.
   - Select "Terminal (Admin)" or "Windows PowerShell (Admin)."
2. Run this command:
   ```
   wsl --install
   ```
3. This will enable WSL2 and install Ubuntu by default.
4. Restart your computer when prompted.
5. After restart, Ubuntu will start automatically and ask you to create a username and password. Choose something you will remember.

### On macOS

#### Step 1: Update macOS

1. Click the Apple menu (top-left of the screen).
2. Click "System Preferences" (or "System Settings" on newer macOS).
3. Click "Software Update."
4. Install any available updates.

#### Step 2: Install Xcode Command Line Tools

Open Terminal (you can find it in Applications > Utilities > Terminal, or search for "Terminal" using Spotlight with Cmd+Space) and run:

```bash
xcode-select --install
```

Click "Install" when prompted.

#### Step 3: Install Homebrew

Homebrew is a package manager for macOS that makes it easy to install software. In Terminal, run:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow the on-screen instructions. After installation, you may need to add Homebrew to your PATH by running the commands it suggests.

### On Linux (Ubuntu/Debian)

#### Step 1: Update Your System

Open a terminal and run:

```bash
sudo apt update && sudo apt upgrade -y
```

This updates the package lists and upgrades all installed packages to their latest versions.

#### Step 2: Install Essential Tools

```bash
sudo apt install -y build-essential curl wget git software-properties-common
```

This installs:
- `build-essential`: The C/C++ compiler and related tools (needed for compiling some Python packages).
- `curl` and `wget`: Tools for downloading files from the internet.
- `git`: Version control system (explained later).
- `software-properties-common`: Tools for managing software repositories.

---

## 6. Installing Python

Python is the programming language we will use for all AI development in this guide.

### Checking if Python Is Already Installed

Open a terminal and run:

```bash
python --version
```

or

```bash
python3 --version
```

If you see something like "Python 3.10.12" or "Python 3.11.5", you already have Python installed. If you get an error or see Python 2.x, you need to install Python 3.

### Installing Python on Windows

#### Method 1: From the Official Website

1. Go to https://www.python.org/downloads/
2. Click the big yellow button that says "Download Python 3.x.x" (where x.x is the latest version).
3. Run the downloaded installer.
4. IMPORTANT: Check the box that says "Add Python to PATH" at the bottom of the installer window.
5. Click "Install Now."
6. Wait for the installation to complete.
7. Click "Close."
8. Open a new terminal and verify: `python --version`

#### Method 2: Using the Microsoft Store

1. Open the Microsoft Store.
2. Search for "Python 3.11" (or the latest version).
3. Click "Install."

### Installing Python on macOS

```bash
brew install python
```

### Installing Python on Linux (Ubuntu/Debian)

Python 3 usually comes pre-installed on Ubuntu. If not:

```bash
sudo apt install -y python3 python3-pip python3-venv
```

### Verifying the Installation

Open a terminal and run:

```bash
python3 --version
pip3 --version
```

You should see version numbers for both. `pip` is Python's package installer -- it lets you download and install libraries.

---

## 7. Understanding the Command Line / Terminal

The command line (also called the terminal, shell, or console) is a text-based interface for interacting with your computer. Instead of clicking icons and menus, you type commands.

### Why Use the Command Line?

For AI development, the command line is essential because:
1. Many AI tools do not have graphical interfaces.
2. You need to install packages, run scripts, manage files, and monitor training processes.
3. When you work on a remote server (which is common for training large models), the command line is often the only interface available.
4. It is faster and more precise than clicking through menus once you are familiar with it.

### Essential Commands

#### Navigating the File System

```bash
# Print the current directory (where you are)
pwd                             # Linux/macOS
cd                              # Windows (just "cd" by itself)

# List files and folders in the current directory
ls                              # Linux/macOS
dir                             # Windows
Get-ChildItem                   # PowerShell

# Change directory (move into a folder)
cd Documents                    # Move into the Documents folder
cd ..                           # Move up one level
cd /home/username               # Move to an absolute path (Linux)
cd ~                            # Move to your home directory (Linux/macOS)

# Create a new directory (folder)
mkdir my_project                # Create a folder called "my_project"
mkdir -p a/b/c                  # Create nested folders (Linux/macOS)

# Create a new file
touch myfile.txt                # Linux/macOS
New-Item myfile.txt             # PowerShell
```

#### Working with Files

```bash
# View the contents of a file
cat myfile.txt                  # Linux/macOS
type myfile.txt                 # Windows Command Prompt
Get-Content myfile.txt          # PowerShell

# Copy a file
cp source.txt destination.txt   # Linux/macOS
copy source.txt dest.txt        # Windows

# Move or rename a file
mv oldname.txt newname.txt      # Linux/macOS
move oldname.txt newname.txt    # Windows

# Delete a file
rm myfile.txt                   # Linux/macOS
del myfile.txt                  # Windows

# Delete a directory and its contents
rm -rf my_folder                # Linux/macOS (BE VERY CAREFUL with this)
Remove-Item my_folder -Recurse  # PowerShell
```

#### Installing Python Packages

```bash
# Install a package
pip install numpy

# Install a specific version
pip install numpy==1.24.0

# Install multiple packages from a requirements file
pip install -r requirements.txt

# List installed packages
pip list

# Uninstall a package
pip uninstall numpy
```

---

## 8. Setting Up a Code Editor

A code editor is a program designed for writing code. Unlike a plain text editor (like Notepad), a code editor provides features like syntax highlighting (coloring different parts of the code), auto-completion, error checking, and integrated terminal.

### Visual Studio Code (VS Code) -- Recommended

VS Code is free, open-source, and the most popular code editor for AI development.

#### Installing VS Code

1. Go to https://code.visualstudio.com/
2. Download the installer for your operating system.
3. Run the installer and follow the instructions.

#### Essential Extensions for AI Development

After installing VS Code, install these extensions:

1. **Python**: Provides Python language support (syntax highlighting, linting, debugging).
   - Click the Extensions icon in the left sidebar (it looks like four squares).
   - Search for "Python" by Microsoft.
   - Click "Install."

2. **Jupyter**: Lets you run Jupyter notebooks inside VS Code.
   - Search for "Jupyter" by Microsoft.
   - Click "Install."

3. **Pylance**: Advanced Python IntelliSense (code completion and type checking).
   - Search for "Pylance."
   - Click "Install."

4. **GitLens**: Enhanced Git integration.
   - Search for "GitLens."
   - Click "Install."

#### VS Code Basics

- **Opening a folder**: File > Open Folder (this is how you open a project).
- **Opening the terminal**: View > Terminal (or press Ctrl+`).
- **Creating a new file**: File > New File.
- **Saving a file**: Ctrl+S (Cmd+S on macOS).
- **Running Python code**: Open a .py file, then click the play button in the top-right corner, or right-click and select "Run Python File in Terminal."

### Jupyter Notebooks

Jupyter notebooks are a special kind of document that mixes code, text, and output. They are extremely popular in AI and data science because you can run code in small chunks (called "cells") and see the results immediately.

#### Installing Jupyter

```bash
pip install jupyter notebook
```

#### Running Jupyter

```bash
jupyter notebook
```

This opens a web interface in your browser where you can create and edit notebooks.

---

## 9. Understanding File Systems

A file system is how files and folders are organized on your computer. Understanding it is essential because you will be managing datasets, model files, code files, and configuration files.

### Directory Structure

Think of the file system as a tree:

```
/ (root)
|-- home/
|   |-- username/
|       |-- Documents/
|       |-- Downloads/
|       |-- projects/
|           |-- my_ai_project/
|               |-- data/
|               |   |-- train.csv
|               |   |-- test.csv
|               |-- models/
|               |   |-- model_v1.pt
|               |-- src/
|               |   |-- train.py
|               |   |-- model.py
|               |   |-- data_loader.py
|               |-- requirements.txt
|               |-- README.md
```

### Absolute vs. Relative Paths

- **Absolute path**: The full path from the root of the file system. Example: `/home/username/projects/my_ai_project/src/train.py`
- **Relative path**: The path relative to your current directory. If you are in `/home/username/projects/my_ai_project/`, then the relative path to train.py is `src/train.py`.

### Recommended Project Structure for AI Projects

```
my_ai_project/
|-- data/                   # Datasets
|   |-- raw/                # Original, unmodified data
|   |-- processed/          # Cleaned and preprocessed data
|-- models/                 # Saved model files
|-- notebooks/              # Jupyter notebooks for experimentation
|-- src/                    # Source code
|   |-- data/               # Data loading and preprocessing code
|   |-- models/             # Model architecture definitions
|   |-- training/           # Training loops and utilities
|   |-- evaluation/         # Evaluation and metrics code
|   |-- utils/              # Utility functions
|-- configs/                # Configuration files
|-- logs/                   # Training logs
|-- tests/                  # Unit tests
|-- requirements.txt        # Python dependencies
|-- README.md               # Project documentation
|-- .gitignore              # Files to exclude from version control
```

---

## 10. Installing Git and Version Control Basics

Git is a version control system. It tracks changes to your files over time, allowing you to:
- Go back to any previous version of your code.
- Work on new features without breaking existing code.
- Collaborate with others.
- Keep a history of what changed and why.

### Installing Git

#### Windows
1. Download from https://git-scm.com/download/windows
2. Run the installer. Accept the default settings.

#### macOS
```bash
brew install git
```

#### Linux
```bash
sudo apt install -y git
```

### Configuring Git

After installation, tell Git who you are:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Essential Git Commands

```bash
# Initialize a new Git repository in the current folder
git init

# Check the status of your files (which are modified, staged, etc.)
git status

# Add files to the staging area (preparing them to be committed)
git add filename.py         # Add a specific file
git add .                   # Add all changed files

# Commit (save a snapshot of the current state)
git commit -m "Describe what you changed"

# View the commit history
git log
git log --oneline           # Compact view

# Create a new branch (a parallel version of your code)
git branch my-feature

# Switch to a branch
git checkout my-feature
# or
git switch my-feature

# Merge a branch into the current branch
git merge my-feature

# Clone a repository (download it from GitHub or similar)
git clone https://github.com/username/repository.git

# Push changes to a remote repository
git push origin main

# Pull changes from a remote repository
git pull origin main
```

### GitHub

GitHub is a website that hosts Git repositories online. It is the standard place to share code, collaborate on projects, and find AI research code.

1. Go to https://github.com and create a free account.
2. You can create new repositories, fork (copy) other people's repositories, and contribute to open-source projects.

### .gitignore

A `.gitignore` file tells Git which files to ignore (not track). For AI projects, you typically want to ignore:

```
# .gitignore for AI projects
__pycache__/
*.pyc
.env
.venv/
venv/
data/
models/
*.pt
*.pth
*.h5
*.ckpt
wandb/
logs/
.ipynb_checkpoints/
```

---

## 11. Setting Up a Virtual Environment

A virtual environment is an isolated Python installation. It lets you install packages for one project without affecting other projects. This is important because different projects may need different versions of the same library.

### Creating a Virtual Environment

```bash
# Navigate to your project directory
cd my_ai_project

# Create a virtual environment called "venv"
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate

# You should see (venv) at the beginning of your terminal prompt
```

### Installing Packages in a Virtual Environment

With your virtual environment activated:

```bash
# Install packages
pip install numpy pandas matplotlib scikit-learn

# Save your installed packages to a file
pip freeze > requirements.txt

# Later, or on another machine, install all packages from the file
pip install -r requirements.txt
```

### Deactivating the Virtual Environment

```bash
deactivate
```

### Using conda (Alternative to pip/venv)

Conda is another package manager that is popular in the data science community. It comes with Anaconda or Miniconda.

#### Installing Miniconda

1. Go to https://docs.conda.io/en/latest/miniconda.html
2. Download the installer for your OS.
3. Run the installer.

#### Using Conda

```bash
# Create a new environment
conda create -n myenv python=3.11

# Activate the environment
conda activate myenv

# Install packages
conda install numpy pandas pytorch torchvision -c pytorch

# Deactivate
conda deactivate

# List environments
conda env list

# Remove an environment
conda env remove -n myenv
```

---

## 12. Installing Core Libraries

Here are all the core libraries you will need for AI development. Install them after activating your virtual environment.

### The Basic Stack

```bash
pip install numpy scipy matplotlib pandas scikit-learn jupyter notebook
```

What each does:
- **numpy**: Array operations, linear algebra, random numbers.
- **scipy**: Advanced scientific computing (optimization, statistics, signal processing).
- **matplotlib**: Plotting and visualization.
- **pandas**: Data manipulation (reading CSV files, filtering data, computing statistics).
- **scikit-learn**: Classical machine learning algorithms (linear regression, decision trees, SVMs, clustering).
- **jupyter**: Interactive notebooks.

### Deep Learning: PyTorch

PyTorch is the primary deep learning framework we will use. Install it from https://pytorch.org by selecting your OS, package manager, and CUDA version.

For a typical setup with NVIDIA GPU (CUDA 12.1):

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

For CPU-only (if you do not have an NVIDIA GPU):

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### Deep Learning: TensorFlow (Alternative)

```bash
pip install tensorflow
```

### Natural Language Processing

```bash
pip install transformers datasets tokenizers sentencepiece
```

### Computer Vision

```bash
pip install opencv-python Pillow albumentations
```

### Experiment Tracking

```bash
pip install tensorboard wandb
```

### Utilities

```bash
pip install tqdm pyyaml requests
```

---

## 13. Understanding Hardware: CPU, GPU, RAM, Storage in Detail

### How Much Hardware Do You Need?

This depends entirely on what you want to build:

#### Learning and Experimentation (Minimal)
- **CPU**: Any modern CPU (Intel i5 or AMD Ryzen 5 or better)
- **RAM**: 8 GB minimum, 16 GB recommended
- **GPU**: Not strictly necessary (you can train small models on CPU)
- **Storage**: 50 GB free
- **Estimated cost**: Most existing laptops from the last 5 years will work

#### Serious Individual Work
- **CPU**: Intel i7/i9 or AMD Ryzen 7/9
- **RAM**: 32 GB
- **GPU**: NVIDIA RTX 3060 (12 GB VRAM) or better
- **Storage**: 500 GB SSD + 1 TB HDD
- **Estimated cost**: $1,000-$2,000 for a desktop, or use cloud computing

#### Training Large Models
- **CPU**: High-end multi-core processor
- **RAM**: 64-128 GB
- **GPU**: NVIDIA A100 (80 GB) or multiple RTX 4090s (24 GB each)
- **Storage**: Several TB of fast NVMe SSD
- **Estimated cost**: $10,000+ for hardware, or $1-10 per hour in the cloud

### NVIDIA CUDA and cuDNN

CUDA is NVIDIA's parallel computing platform. cuDNN is a library of optimized routines for deep learning. Both are required for GPU-accelerated training.

#### Installing CUDA

1. Check your GPU model:
   - Windows: Open Device Manager > Display adapters
   - Linux: `nvidia-smi` (if drivers are installed) or `lspci | grep -i nvidia`

2. Download and install GPU drivers from https://www.nvidia.com/drivers

3. Download and install CUDA Toolkit from https://developer.nvidia.com/cuda-toolkit

4. Download cuDNN from https://developer.nvidia.com/cudnn (requires a free NVIDIA developer account)

5. Verify the installation:
   ```bash
   nvidia-smi           # Shows GPU info and CUDA version
   nvcc --version       # Shows CUDA compiler version
   ```

6. Verify in Python:
   ```python
   import torch
   print(torch.cuda.is_available())          # Should print True
   print(torch.cuda.get_device_name(0))      # Should print your GPU name
   print(torch.cuda.device_count())          # Number of GPUs
   ```

---

## 14. Cloud Computing Options

If you do not have a powerful GPU, cloud computing lets you rent one by the hour.

### Google Colab (Free Tier Available)

Google Colab provides free access to GPUs (usually NVIDIA T4 with 15 GB VRAM) through a web-based Jupyter notebook interface.

1. Go to https://colab.research.google.com
2. Sign in with a Google account.
3. Create a new notebook.
4. Go to Runtime > Change runtime type > select "GPU."
5. You now have access to a GPU.

Limitations of the free tier:
- Sessions time out after a period of inactivity.
- You might not always get a GPU if demand is high.
- Limited RAM (about 12 GB).
- Files are deleted when the session ends (save them to Google Drive).

### Other Cloud Options

- **AWS (Amazon Web Services)**: EC2 instances with GPUs. p3.2xlarge (V100) costs about $3/hour. p4d.24xlarge (8xA100) costs about $32/hour.
- **Google Cloud Platform (GCP)**: Compute Engine with GPUs. Similar pricing to AWS.
- **Microsoft Azure**: Virtual machines with GPUs.
- **Lambda Labs**: GPU cloud specifically for AI. Often cheaper than the big three.
- **RunPod**: On-demand GPU rentals. Very affordable.
- **Vast.ai**: Marketplace for GPU rentals. Often the cheapest option.
- **Kaggle**: Free GPUs similar to Colab, with access to many datasets.
- **Lightning AI**: Free GPU access with a nice development environment.

### Setting Up a Cloud Instance (General Steps)

1. Create an account on your chosen platform.
2. Select a GPU instance type (e.g., one with an NVIDIA A100).
3. Select an operating system (Ubuntu is recommended).
4. Select a pre-built AI image if available (these come with CUDA, Python, and common libraries pre-installed).
5. Launch the instance.
6. Connect to the instance via SSH:
   ```bash
   ssh -i your-key.pem ubuntu@your-instance-ip-address
   ```
7. Set up your environment (install packages, upload data, etc.).
8. Remember to stop or terminate the instance when you are done to avoid ongoing charges.

---

## 15. What Is AI? A Bird's Eye View

Before we dive into the technical details in the following chapters, let us establish a mental map of the entire field.

### Artificial Intelligence

Artificial Intelligence (AI) is the broad field of creating machines that can perform tasks that typically require human intelligence. This includes:
- Understanding and generating language
- Recognizing objects in images
- Making decisions
- Playing games
- Driving cars
- Creating art
- And much more

### Machine Learning

Machine Learning (ML) is a subset of AI. Instead of explicitly programming rules ("if the email contains the word 'viagra,' mark it as spam"), you give the computer examples and let it learn the rules on its own.

The three main types of machine learning:

1. **Supervised Learning**: You provide labeled examples. "Here are 10,000 emails, each labeled as 'spam' or 'not spam.' Learn to classify new emails."
2. **Unsupervised Learning**: You provide data without labels. "Here are 10,000 customer records. Find natural groupings among them."
3. **Reinforcement Learning**: An agent learns by interacting with an environment. "Play this game and learn to maximize your score."

### Deep Learning

Deep Learning is a subset of machine learning that uses neural networks with many layers (hence "deep"). It has been responsible for most of the recent breakthroughs in AI:
- GPT and other language models
- Image generation (Stable Diffusion, DALL-E, Midjourney)
- Voice synthesis
- Game-playing AI (AlphaGo, AlphaZero)
- Self-driving cars
- Protein structure prediction (AlphaFold)

### The AI Landscape (What You Can Build)

Here is a map of the major types of AI models you can build, all of which are covered in this guide:

1. **Text Classification**: Input text, output a category (spam detection, sentiment analysis).
2. **Text Generation**: Input a prompt, output continuation text (chatbots, story writing).
3. **Machine Translation**: Input text in one language, output text in another.
4. **Question Answering**: Input a question (and optionally a context), output an answer.
5. **Summarization**: Input a long text, output a shorter summary.
6. **Image Classification**: Input an image, output a category (cat vs. dog, cancer vs. healthy).
7. **Object Detection**: Input an image, output locations and categories of objects in the image.
8. **Image Segmentation**: Input an image, output a pixel-level map of which object each pixel belongs to.
9. **Image Generation**: Input a text description (or random noise), output an image.
10. **Image-to-Image Translation**: Input an image, output a modified image (style transfer, colorization).
11. **Video Generation**: Generate video from text or images.
12. **Audio Classification**: Input audio, output a category (speech vs. music, speaker identification).
13. **Speech Recognition**: Input audio, output text (transcription).
14. **Speech Synthesis (Text-to-Speech)**: Input text, output audio.
15. **Music Generation**: Generate music from text descriptions or other music.
16. **3D Object Generation**: Generate 3D models from text descriptions or 2D images.
17. **Reinforcement Learning Agents**: Train agents that learn to play games, control robots, or make decisions.
18. **Recommendation Systems**: Input user preferences, output recommended items.
19. **Anomaly Detection**: Input normal data, learn what is "normal," detect deviations.
20. **Time Series Forecasting**: Input historical data, predict future values (stock prices, weather).

Each of these is covered in detail in subsequent chapters, with complete code examples that you can run.

---

## Summary

At this point, you should have:

1. A basic understanding of how computers work (CPU, GPU, RAM, storage).
2. An understanding of binary and how data is stored.
3. Python installed on your computer.
4. A code editor (VS Code) installed and configured.
5. A command line / terminal you are comfortable opening.
6. Git installed and configured.
7. A virtual environment set up for your AI projects.
8. Core AI libraries installed (NumPy, PyTorch, etc.).
9. An understanding of cloud computing options if you need more powerful hardware.
10. A bird's-eye view of the entire AI landscape.

In the next chapter, we will cover the mathematical foundations you need for AI. Do not be intimidated -- we will start from the very basics and build up gradually.

---

[Next: Chapter 1 - Mathematics for AI >>](./01_MATHEMATICS_FOUNDATION.md)
