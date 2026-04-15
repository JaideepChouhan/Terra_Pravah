# Chapter 3: Data -- The Fuel of AI

## Introduction

Every AI model, without exception, learns from data. A text generation model learns from text. An image generation model learns from images. A 3D model generator learns from 3D shapes. A music generator learns from music. The quality, quantity, and preparation of your data determines more about the success of your model than any architectural decision you will ever make.

This chapter covers everything about data: what it is at the lowest level, how to collect it, how to clean it, how to transform it, how to store it, how to load it efficiently, and how to avoid the many traps that can sabotage your model before training even begins.

---

## Table of Contents

1. What Is Data?
2. Types of Data
3. Data Formats and Storage
4. Collecting Data
5. Data Cleaning
6. Data Preprocessing
7. Feature Engineering
8. Data Splitting: Train, Validation, Test
9. Data Augmentation
10. Handling Imbalanced Data
11. Data Pipelines and DataLoaders
12. Working with Text Data
13. Working with Image Data
14. Working with Audio Data
15. Working with 3D Data
16. Working with Tabular Data
17. Data Ethics and Bias
18. Summary

---

## 1. What Is Data?

Data is information stored in a format that a computer can process. That is it. Every email you have ever sent is data. Every photo on your phone is data. Every song in your playlist is data. Every 3D model in a video game is data. Every stock price ever recorded is data.

At the lowest level, all data on a computer is stored as sequences of 0s and 1s (binary). Different types of data are just different conventions for interpreting those 0s and 1s:

- A text file stores characters where each character maps to a number (e.g., 'A' = 65 in ASCII).
- An image stores pixel values where each pixel has color channel values (e.g., RGB: three numbers from 0-255).
- An audio file stores amplitude samples taken many times per second (e.g., 44,100 samples per second for CD quality).
- A 3D model stores vertex coordinates, face definitions, and material properties.

For AI, we ultimately convert all data into numbers -- specifically into tensors (multi-dimensional arrays of numbers) -- because that is what neural networks operate on.

### A Concrete Example

Suppose you have the sentence: "The cat sat."

To feed this to a neural network, you might:

1. Split it into words: ["The", "cat", "sat", "."]
2. Map each word to a number: {"The": 1, "cat": 2, "sat": 3, ".": 4}
3. Create a tensor: [1, 2, 3, 4]

That tensor [1, 2, 3, 4] is what the neural network actually sees. The network never sees the letters or words directly -- it only sees numbers.

---

## 2. Types of Data

### Structured Data (Tabular Data)

Structured data is organized in rows and columns, like a spreadsheet. Each row is one "example" or "record," and each column is one "feature" or "attribute."

Example -- a dataset of houses:

| Bedrooms | Bathrooms | Square Feet | Price     |
|----------|-----------|-------------|-----------|
| 3        | 2         | 1500        | 300,000   |
| 4        | 3         | 2200        | 450,000   |
| 2        | 1         | 900         | 180,000   |

Here, each row is one house. The columns Bedrooms, Bathrooms, and Square Feet are "input features" (what we know about the house), and Price is the "target" (what we want to predict).

### Unstructured Data

Unstructured data does not fit neatly into rows and columns. Examples include:

- **Text**: Articles, books, tweets, chat messages, code, emails.
- **Images**: Photographs, drawings, medical scans, satellite imagery.
- **Audio**: Speech recordings, music, environmental sounds.
- **Video**: Sequences of images with optional audio tracks.
- **3D data**: Point clouds, meshes, voxel grids, CAD models.

Unstructured data requires special preprocessing to convert it into numerical tensors.

### Semi-Structured Data

Data that has some organization but is not tabular. Examples:

- **JSON**: Nested key-value pairs. Used everywhere on the web.
- **XML**: Hierarchical tagged data.
- **HTML**: Web page content with tags and attributes.

```json
{
    "name": "Alice",
    "age": 30,
    "skills": ["Python", "Machine Learning", "Data Analysis"],
    "education": {
        "degree": "M.S.",
        "field": "Computer Science"
    }
}
```

### Time Series Data

Data collected over time, where the order matters:

- Stock prices every minute
- Temperature readings every hour
- Heart rate measurements every second
- Website traffic counts every day

```
Timestamp,          Temperature
2026-01-01 00:00,   3.2
2026-01-01 01:00,   2.8
2026-01-01 02:00,   2.5
2026-01-01 03:00,   2.1
```

---

## 3. Data Formats and Storage

### Common File Formats

**CSV (Comma-Separated Values)**: The simplest format for tabular data. Each line is a row, and columns are separated by commas.

```csv
name,age,city
Alice,30,New York
Bob,25,San Francisco
Charlie,35,Chicago
```

Reading a CSV in Python:

```python
import pandas as pd

df = pd.read_csv("data.csv")
print(df.head())
#       name  age           city
# 0    Alice   30       New York
# 1      Bob   25  San Francisco
# 2  Charlie   35        Chicago
```

**JSON (JavaScript Object Notation)**: Great for nested, hierarchical data. Commonly used for API responses and configuration files.

```python
import json

# Reading JSON
with open("data.json", "r") as f:
    data = json.load(f)

# Writing JSON
with open("output.json", "w") as f:
    json.dump(data, f, indent=2)
```

**Parquet**: A columnar storage format that is much faster than CSV for large datasets. It compresses data efficiently and preserves data types.

```python
import pandas as pd

# Write to parquet
df.to_parquet("data.parquet")

# Read from parquet (much faster than CSV for large files)
df = pd.read_parquet("data.parquet")
```

**HDF5**: Hierarchical Data Format version 5. Excellent for storing large arrays of numbers. Used heavily in scientific computing and AI.

```python
import h5py
import numpy as np

# Writing
with h5py.File("data.h5", "w") as f:
    f.create_dataset("images", data=np.random.rand(1000, 224, 224, 3))
    f.create_dataset("labels", data=np.random.randint(0, 10, size=1000))

# Reading
with h5py.File("data.h5", "r") as f:
    images = f["images"][:]
    labels = f["labels"][:]
```

**Image Formats**: JPEG (lossy compression, smaller files), PNG (lossless compression, supports transparency), TIFF (high quality, used in medical/satellite imaging), BMP (uncompressed, large files).

```python
from PIL import Image
import numpy as np

# Load an image
img = Image.open("photo.jpg")

# Convert to numpy array
img_array = np.array(img)
print(img_array.shape)  # e.g., (480, 640, 3) which is height x width x RGB channels

# Each value is 0-255 representing intensity
print(img_array[0, 0])  # RGB values of top-left pixel, e.g., [128, 64, 200]
```

**Audio Formats**: WAV (uncompressed waveform), MP3 (compressed), FLAC (lossless compressed).

```python
import librosa
import numpy as np

# Load an audio file
waveform, sample_rate = librosa.load("audio.wav", sr=16000)
# waveform is a 1D numpy array of float values
# sample_rate is 16000 (samples per second)

print(f"Duration: {len(waveform) / sample_rate:.2f} seconds")
print(f"Shape: {waveform.shape}")  # e.g., (160000,) for 10 seconds
```

**3D Formats**: OBJ (simple text-based), STL (for 3D printing), PLY (with color), GLTF (web-optimized), FBX (animation).

```python
import trimesh

# Load a 3D mesh
mesh = trimesh.load("model.obj")
print(f"Vertices: {len(mesh.vertices)}")   # e.g., 5000 3D points
print(f"Faces: {len(mesh.faces)}")         # e.g., 10000 triangles
print(f"Vertex shape: {mesh.vertices.shape}")  # (5000, 3) -- x, y, z for each vertex
```

### Storage Options

**Local Storage**: Your computer's hard drive or SSD. Fastest for small-to-medium datasets.

**Cloud Storage**: Amazon S3, Google Cloud Storage, Azure Blob Storage. Essentially unlimited storage. Pay per GB stored and per GB transferred.

**Database**: PostgreSQL, MySQL for structured data. MongoDB for semi-structured. Redis for fast key-value storage.

---

## 4. Collecting Data

### Public Datasets

There are thousands of freely available datasets for AI research:

**General Repositories**:
- Hugging Face Datasets (https://huggingface.co/datasets) -- the largest collection, covering text, images, audio, and more.
- Kaggle (https://www.kaggle.com/datasets) -- competitions and datasets.
- UCI Machine Learning Repository -- classic ML datasets.
- Google Dataset Search -- a search engine for datasets.

**Text Datasets**:
- Common Crawl: Petabytes of web crawl data (raw text from the internet).
- Wikipedia: Full dumps of Wikipedia in all languages.
- The Pile: 800 GB of diverse English text curated for language model training.
- BookCorpus: 11,000 books.
- OpenWebText: Recreation of the WebText dataset used to train GPT-2.
- RedPajama: Open-source recreation of LLaMA training data.

**Image Datasets**:
- ImageNet: 14 million images in 20,000+ categories.
- COCO (Common Objects in Context): 330,000 images with object detection labels.
- CIFAR-10 / CIFAR-100: 60,000 tiny (32x32) images in 10 or 100 classes.
- MNIST: 70,000 handwritten digit images (28x28, grayscale).
- CelebA: 200,000 celebrity face images with 40 attribute labels.
- LAION-5B: 5 billion image-text pairs (used to train Stable Diffusion).

**3D Datasets**:
- ShapeNet: 51,000 3D models in 55 categories.
- ModelNet: 12,000 CAD models in 40 categories.
- Objaverse: 800,000+ 3D objects.
- ABC Dataset: 1 million CAD models.
- ScanNet: 1,500 3D scans of real-world indoor scenes.

**Audio Datasets**:
- LibriSpeech: 1,000 hours of English speech.
- Common Voice (Mozilla): Thousands of hours of speech in 100+ languages.
- AudioSet: 2 million 10-second YouTube clips labeled with 632 audio event classes.
- MUSDB18: Music source separation dataset.

### Web Scraping

When no existing dataset fits your needs, you can collect data from the web. This involves writing code that automatically visits web pages and extracts information.

```python
import requests
from bs4 import BeautifulSoup
import time

def scrape_articles(urls):
    """Scrape article text from a list of URLs."""
    articles = []
    
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Find the main content (varies by site)
            # This example looks for <article> tags or <p> tags
            article_tag = soup.find("article")
            if article_tag:
                text = article_tag.get_text(separator="\n", strip=True)
            else:
                paragraphs = soup.find_all("p")
                text = "\n".join(p.get_text(strip=True) for p in paragraphs)
            
            articles.append({
                "url": url,
                "text": text,
                "length": len(text)
            })
            
            # Be polite: wait between requests
            time.sleep(1)
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
    
    return articles
```

**Legal and ethical considerations**:
- Always check the website's robots.txt file (e.g., example.com/robots.txt) to see what they allow bots to access.
- Respect rate limits. Do not send hundreds of requests per second.
- Check the website's terms of service.
- Be aware of copyright. Scraping content does not give you the right to use it for any purpose.
- Consider privacy implications if the data contains personal information.

### APIs

Many services provide structured APIs for data access:

```python
import requests

# Example: fetching data from a public API
response = requests.get("https://api.example.com/data", params={
    "category": "science",
    "limit": 100,
    "format": "json"
})

data = response.json()
```

### Synthetic Data Generation

Sometimes you create your own data. This is called "synthetic data."

```python
import numpy as np

def generate_linear_data(n_samples=1000, noise_level=0.1):
    """Generate synthetic data for linear regression."""
    # True relationship: y = 3x + 7 + noise
    x = np.random.uniform(-10, 10, size=(n_samples, 1))
    noise = np.random.normal(0, noise_level, size=(n_samples, 1))
    y = 3 * x + 7 + noise
    return x, y

def generate_classification_data(n_samples=1000, n_features=2):
    """Generate synthetic data for classification."""
    # Two clusters
    class_0 = np.random.randn(n_samples // 2, n_features) + np.array([2, 2])
    class_1 = np.random.randn(n_samples // 2, n_features) + np.array([-2, -2])
    
    X = np.vstack([class_0, class_1])
    y = np.array([0] * (n_samples // 2) + [1] * (n_samples // 2))
    
    # Shuffle
    indices = np.random.permutation(n_samples)
    return X[indices], y[indices]
```

---

## 5. Data Cleaning

Real-world data is messy. Before you can train a model, you need to clean it. Here are the most common issues and how to fix them.

### Missing Values

Data often has missing entries. A sensor might have failed, a survey respondent skipped a question, or a web scrape missed a field.

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "name": ["Alice", "Bob", None, "David"],
    "age": [30, None, 25, 35],
    "salary": [70000, 80000, 55000, None]
})

# Check for missing values
print(df.isnull().sum())
# name      1
# age       1
# salary    1

# Strategy 1: Drop rows with any missing values
df_dropped = df.dropna()

# Strategy 2: Fill with a specific value
df_filled = df.fillna({"name": "Unknown", "age": df["age"].mean(), "salary": 0})

# Strategy 3: Forward fill (use the previous row's value)
df_ffill = df.fillna(method="ffill")

# Strategy 4: Interpolate (for numerical columns with ordered data)
df_interp = df.interpolate()
```

**When to use each strategy**:
- Drop rows if you have lots of data and few missing values (less than 5%).
- Fill with mean/median for numerical features when missing values are random.
- Forward/backward fill for time series data.
- Fill with a special category (e.g., "Unknown") for categorical features.
- Never drop rows blindly -- you might be removing an important pattern.

### Duplicate Data

Duplicate rows can bias your model by giving certain examples more weight.

```python
# Check for duplicates
print(f"Duplicates: {df.duplicated().sum()}")

# Remove duplicates
df_unique = df.drop_duplicates()

# Remove duplicates based on specific columns
df_unique = df.drop_duplicates(subset=["name", "age"])
```

### Inconsistent Data

Data from different sources might use different conventions:

```python
# Inconsistent text formatting
df["city"] = df["city"].str.strip()           # Remove leading/trailing whitespace
df["city"] = df["city"].str.lower()            # Standardize to lowercase
df["city"] = df["city"].str.replace("  ", " ") # Remove double spaces

# Inconsistent date formats
df["date"] = pd.to_datetime(df["date"], format="mixed")

# Inconsistent categories
mapping = {
    "ny": "New York",
    "nyc": "New York",
    "new york": "New York",
    "new york city": "New York",
    "sf": "San Francisco",
    "san fran": "San Francisco",
}
df["city"] = df["city"].map(mapping).fillna(df["city"])
```

### Outliers

Outliers are data points that are dramatically different from the rest. They can throw off your model.

```python
import numpy as np

def detect_outliers_iqr(data, column):
    """Detect outliers using the IQR method."""
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = data[(data[column] < lower_bound) | (data[column] > upper_bound)]
    return outliers

def detect_outliers_zscore(data, column, threshold=3):
    """Detect outliers using z-scores."""
    mean = data[column].mean()
    std = data[column].std()
    z_scores = (data[column] - mean) / std
    
    outliers = data[z_scores.abs() > threshold]
    return outliers

# Remove outliers (or cap them)
def cap_outliers(data, column, lower_percentile=0.01, upper_percentile=0.99):
    """Cap outliers at given percentiles instead of removing them."""
    lower = data[column].quantile(lower_percentile)
    upper = data[column].quantile(upper_percentile)
    data[column] = data[column].clip(lower, upper)
    return data
```

### Data Type Errors

Sometimes numbers are stored as strings, dates as numbers, etc.

```python
# Convert string numbers to actual numbers
df["price"] = pd.to_numeric(df["price"], errors="coerce")
# "coerce" turns unparseable values into NaN instead of raising an error

# Convert to appropriate types
df["category"] = df["category"].astype("category")
df["count"] = df["count"].astype(int)
df["is_valid"] = df["is_valid"].astype(bool)
```

---

## 6. Data Preprocessing

Preprocessing transforms raw data into a format suitable for model training.

### Normalization and Standardization

Neural networks work best when input values are in a consistent range.

**Min-Max Normalization** scales values to [0, 1]:

$$x_{normalized} = \frac{x - x_{min}}{x_{max} - x_{min}}$$

```python
def min_max_normalize(data):
    """Scale data to [0, 1] range."""
    min_val = data.min()
    max_val = data.max()
    return (data - min_val) / (max_val - min_val)

# Using sklearn
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()
X_normalized = scaler.fit_transform(X_train)

# IMPORTANT: Use the SAME scaler for test data
X_test_normalized = scaler.transform(X_test)  # transform, NOT fit_transform
```

**Standardization (Z-score normalization)** scales values to mean=0, std=1:

$$x_{standardized} = \frac{x - \mu}{\sigma}$$

```python
def standardize(data):
    """Scale data to mean=0, std=1."""
    return (data - data.mean()) / data.std()

# Using sklearn
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_standardized = scaler.fit_transform(X_train)
X_test_standardized = scaler.transform(X_test)
```

**When to use which**:
- Min-Max: When you need values in a specific range (e.g., pixel values for images).
- Standardization: When data might have outliers (z-score is more robust). Generally preferred for most neural network inputs.

### Encoding Categorical Variables

Neural networks only understand numbers. Categorical variables (like "color" = "red", "blue", "green") must be converted.

**Label Encoding**: Assign a number to each category.

```python
from sklearn.preprocessing import LabelEncoder

encoder = LabelEncoder()
df["color_encoded"] = encoder.fit_transform(df["color"])
# "blue" -> 0, "green" -> 1, "red" -> 2
```

Problem: The model might interpret "red" (2) as being "more" than "blue" (0), which is meaningless.

**One-Hot Encoding**: Create a binary column for each category.

```python
# Using pandas
df_encoded = pd.get_dummies(df, columns=["color"])
# Creates columns: color_blue, color_green, color_red
# Each is 0 or 1

# Using sklearn
from sklearn.preprocessing import OneHotEncoder

encoder = OneHotEncoder(sparse_output=False)
encoded = encoder.fit_transform(df[["color"]])
```

**When to use which**:
- Label encoding: For ordinal categories where order matters (e.g., "low" < "medium" < "high").
- One-hot encoding: For nominal categories where no order exists (e.g., colors, countries).
- For high-cardinality categories (thousands of unique values), consider embedding layers (covered in neural network chapters).

### Text Preprocessing

Text requires extensive preprocessing before it can be fed to a model.

```python
import re
import string

def preprocess_text(text):
    """Basic text preprocessing pipeline."""
    # 1. Lowercase
    text = text.lower()
    
    # 2. Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    
    # 3. Remove URLs
    text = re.sub(r"http\S+|www\.\S+", "", text)
    
    # 4. Remove email addresses
    text = re.sub(r"\S+@\S+", "", text)
    
    # 5. Remove special characters (keep letters, numbers, spaces)
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    
    # 6. Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()
    
    return text

# Example
raw = "<p>Check out https://example.com! Email me at bob@test.com for MORE info!!!</p>"
clean = preprocess_text(raw)
print(clean)  # "check out email me at for more info"
```

### Tokenization

Tokenization splits text into smaller units (tokens) that a model can process.

```python
# Simple word tokenization (splitting on spaces)
text = "The cat sat on the mat."
tokens = text.split()
# ["The", "cat", "sat", "on", "the", "mat."]

# Better: using a proper tokenizer that handles punctuation
import re
tokens = re.findall(r"\b\w+\b", text.lower())
# ["the", "cat", "sat", "on", "the", "mat"]

# Professional tokenization with Hugging Face
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
tokens = tokenizer.tokenize("The cat sat on the mat.")
# ["the", "cat", "sat", "on", "the", "mat", "."]

# Convert tokens to numerical IDs
token_ids = tokenizer.encode("The cat sat on the mat.")
# [101, 1996, 4937, 2938, 2006, 1996, 13523, 1012, 102]
# 101 = [CLS] token, 102 = [SEP] token (special tokens)
```

**Subword Tokenization**: Modern models do not tokenize by words. They use subword tokenization, which breaks words into smaller pieces. This handles rare words and typos gracefully.

```python
# BPE (Byte-Pair Encoding) -- used by GPT models
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("gpt2")

text = "unbelievably"
tokens = tokenizer.tokenize(text)
# ["un", "believ", "ably"]  -- broken into meaningful subwords

text = "supercalifragilisticexpialidocious"
tokens = tokenizer.tokenize(text)
# Broken into many subword pieces since this word is rare
```

### Image Preprocessing

```python
import torchvision.transforms as transforms
from PIL import Image

# Define a preprocessing pipeline for images
transform = transforms.Compose([
    transforms.Resize((224, 224)),          # Resize to fixed size
    transforms.RandomHorizontalFlip(p=0.5), # Random horizontal flip (augmentation)
    transforms.RandomRotation(10),           # Random rotation up to 10 degrees
    transforms.ColorJitter(                  # Random color changes
        brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1
    ),
    transforms.ToTensor(),                   # Convert to tensor [0, 1]
    transforms.Normalize(                    # Normalize with ImageNet stats
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# Apply to an image
img = Image.open("photo.jpg")
tensor = transform(img)
print(tensor.shape)  # torch.Size([3, 224, 224]) -- channels x height x width
```

---

## 7. Feature Engineering

Feature engineering is the art of creating new, informative features from raw data. Good features can make a simple model perform better than a complex model with poor features.

### Numerical Features

```python
import pandas as pd
import numpy as np

# Original features
df["total_rooms"] = 100
df["total_bedrooms"] = 20
df["population"] = 500
df["households"] = 200

# Engineered features (ratios, interactions)
df["rooms_per_household"] = df["total_rooms"] / df["households"]
df["bedrooms_ratio"] = df["total_bedrooms"] / df["total_rooms"]
df["people_per_household"] = df["population"] / df["households"]

# Polynomial features
df["rooms_squared"] = df["total_rooms"] ** 2
df["rooms_times_bedrooms"] = df["total_rooms"] * df["total_bedrooms"]

# Log transformation (for skewed distributions)
df["log_population"] = np.log1p(df["population"])  # log(1 + x) to handle zeros

# Binning (converting continuous to categorical)
df["rooms_category"] = pd.cut(df["total_rooms"], 
                               bins=[0, 3, 6, 10, float("inf")],
                               labels=["small", "medium", "large", "very_large"])
```

### Date/Time Features

```python
df["date"] = pd.to_datetime(df["date_string"])

# Extract components
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["day"] = df["date"].dt.day
df["day_of_week"] = df["date"].dt.dayofweek  # 0=Monday, 6=Sunday
df["hour"] = df["date"].dt.hour
df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
df["quarter"] = df["date"].dt.quarter

# Cyclical encoding (so December and January are "close")
df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
```

### Text Features

```python
# Length-based features
df["text_length"] = df["text"].str.len()
df["word_count"] = df["text"].str.split().str.len()
df["avg_word_length"] = df["text_length"] / df["word_count"]
df["sentence_count"] = df["text"].str.count(r"[.!?]+")

# Content-based features
df["has_question_mark"] = df["text"].str.contains(r"\?").astype(int)
df["exclamation_count"] = df["text"].str.count("!")
df["capital_ratio"] = df["text"].apply(
    lambda x: sum(1 for c in x if c.isupper()) / len(x) if len(x) > 0 else 0
)
```

---

## 8. Data Splitting: Train, Validation, Test

This is one of the most important concepts in machine learning, and getting it wrong will lead to models that seem to work but fail in practice.

### Why Three Splits?

- **Training set** (typically 70-80%): The model learns from this data. It sees these examples during training and adjusts its parameters to fit them.
- **Validation set** (typically 10-15%): Used during training to monitor performance on unseen data. Helps you tune hyperparameters (learning rate, model size, etc.) and detect overfitting.
- **Test set** (typically 10-15%): Used ONLY once, at the very end, to get a final, unbiased estimate of how well the model will perform on truly unseen data.

### The Cardinal Rule

**Never, ever let information from the test set influence any decision about your model.** If you look at the test set and then adjust your model, the test set is no longer "unseen" and your evaluation is biased. This is called "data leakage."

### How to Split

```python
from sklearn.model_selection import train_test_split

# Step 1: Split into train+val and test
X_trainval, X_test, y_trainval, y_test = train_test_split(
    X, y, test_size=0.15, random_state=42, stratify=y  # stratify for classification
)

# Step 2: Split train+val into train and val
X_train, X_val, y_train, y_val = train_test_split(
    X_trainval, y_trainval, test_size=0.176, random_state=42, stratify=y_trainval
    # 0.176 of 85% is approximately 15% of total
)

print(f"Train: {len(X_train)} ({len(X_train)/len(X)*100:.1f}%)")
print(f"Val:   {len(X_val)} ({len(X_val)/len(X)*100:.1f}%)")
print(f"Test:  {len(X_test)} ({len(X_test)/len(X)*100:.1f}%)")
```

### Cross-Validation

When you have limited data, cross-validation gives you a more reliable estimate of model performance.

```python
from sklearn.model_selection import KFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier

# K-Fold Cross-Validation
kf = KFold(n_splits=5, shuffle=True, random_state=42)

model = RandomForestClassifier()
scores = cross_val_score(model, X, y, cv=kf, scoring="accuracy")

print(f"Fold scores: {scores}")
print(f"Mean accuracy: {scores.mean():.4f} +/- {scores.std():.4f}")
```

How K-Fold works (with K=5):
1. Split data into 5 equal parts (folds).
2. Train on folds 1-4, validate on fold 5. Record score.
3. Train on folds 1-3 and 5, validate on fold 4. Record score.
4. Train on folds 1-2, 4-5, validate on fold 3. Record score.
5. Train on folds 1, 3-5, validate on fold 2. Record score.
6. Train on folds 2-5, validate on fold 1. Record score.
7. Average all 5 scores to get the final estimate.

---

## 9. Data Augmentation

Data augmentation creates new training examples by applying transformations to existing ones. This is a powerful technique to increase the effective size of your dataset and make your model more robust.

### Image Augmentation

```python
import torchvision.transforms as T

# Training transforms (with augmentation)
train_transform = T.Compose([
    T.RandomResizedCrop(224, scale=(0.8, 1.0)),
    T.RandomHorizontalFlip(p=0.5),
    T.RandomVerticalFlip(p=0.1),
    T.RandomRotation(degrees=15),
    T.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.1),
    T.RandomAffine(degrees=0, translate=(0.1, 0.1)),
    T.RandomPerspective(distortion_scale=0.2, p=0.5),
    T.RandomGrayscale(p=0.1),
    T.GaussianBlur(kernel_size=3, sigma=(0.1, 2.0)),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    T.RandomErasing(p=0.2),  # Randomly erase a rectangle
])

# Validation/Test transforms (NO augmentation, only resize and normalize)
val_transform = T.Compose([
    T.Resize(256),
    T.CenterCrop(224),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])
```

### Text Augmentation

```python
import random
import re

def text_augment_synonym(text, p=0.1):
    """Replace random words with simple alternatives."""
    # In practice, use a library like nlpaug or textattack
    simple_synonyms = {
        "good": ["great", "excellent", "fine", "nice"],
        "bad": ["poor", "terrible", "awful", "lousy"],
        "big": ["large", "huge", "enormous", "massive"],
        "small": ["tiny", "little", "miniature", "compact"],
    }
    
    words = text.split()
    new_words = []
    for word in words:
        lower = word.lower()
        if lower in simple_synonyms and random.random() < p:
            new_words.append(random.choice(simple_synonyms[lower]))
        else:
            new_words.append(word)
    return " ".join(new_words)

def text_augment_deletion(text, p=0.1):
    """Randomly delete words."""
    words = text.split()
    if len(words) <= 1:
        return text
    new_words = [w for w in words if random.random() > p]
    if len(new_words) == 0:
        return random.choice(words)
    return " ".join(new_words)

def text_augment_swap(text, p=0.1):
    """Randomly swap adjacent words."""
    words = text.split()
    for i in range(len(words) - 1):
        if random.random() < p:
            words[i], words[i + 1] = words[i + 1], words[i]
    return " ".join(words)
```

### Audio Augmentation

```python
import numpy as np

def add_noise(waveform, noise_level=0.005):
    """Add random noise to audio."""
    noise = np.random.randn(*waveform.shape) * noise_level
    return waveform + noise

def time_stretch(waveform, rate=1.0):
    """Speed up or slow down audio without changing pitch."""
    import librosa
    return librosa.effects.time_stretch(waveform, rate=rate)

def pitch_shift(waveform, sr, n_steps=0):
    """Shift pitch up or down."""
    import librosa
    return librosa.effects.pitch_shift(waveform, sr=sr, n_steps=n_steps)

def random_crop(waveform, crop_length):
    """Randomly crop a segment from audio."""
    if len(waveform) <= crop_length:
        return waveform
    start = np.random.randint(0, len(waveform) - crop_length)
    return waveform[start:start + crop_length]
```

---

## 10. Handling Imbalanced Data

In many real-world problems, some classes are much rarer than others. For example, in fraud detection, 99.9% of transactions are legitimate and only 0.1% are fraudulent. If your model simply predicts "not fraud" every time, it will be 99.9% accurate but completely useless.

### Techniques for Imbalanced Data

**1. Oversampling the minority class**:

```python
from sklearn.utils import resample

# Separate classes
minority = df[df["label"] == 1]
majority = df[df["label"] == 0]

# Oversample minority to match majority
minority_upsampled = resample(
    minority,
    replace=True,              # Sample with replacement
    n_samples=len(majority),   # Match number of majority samples
    random_state=42
)

# Combine
df_balanced = pd.concat([majority, minority_upsampled])
```

**2. Undersampling the majority class**:

```python
majority_downsampled = resample(
    majority,
    replace=False,
    n_samples=len(minority),
    random_state=42
)

df_balanced = pd.concat([majority_downsampled, minority])
```

**3. SMOTE (Synthetic Minority Over-sampling Technique)**:

```python
from imblearn.over_sampling import SMOTE

smote = SMOTE(random_state=42)
X_balanced, y_balanced = smote.fit_resample(X_train, y_train)
```

**4. Class weights in the loss function**:

```python
import torch
import torch.nn as nn

# If class 0 has 900 samples and class 1 has 100 samples
# Weight inversely proportional to frequency
weights = torch.tensor([100/1000, 900/1000])  # [0.1, 0.9]
# Or simply: inverse frequency
weights = torch.tensor([1.0/900, 1.0/100])
weights = weights / weights.sum()  # Normalize

criterion = nn.CrossEntropyLoss(weight=weights)
```

---

## 11. Data Pipelines and DataLoaders

For training neural networks, you need to efficiently feed data to the model in batches. PyTorch provides `Dataset` and `DataLoader` classes for this.

### PyTorch Dataset

```python
import torch
from torch.utils.data import Dataset, DataLoader

class CustomDataset(Dataset):
    """A custom dataset that loads data from files or arrays."""
    
    def __init__(self, data, labels, transform=None):
        """
        Args:
            data: Input features (numpy array or list of file paths).
            labels: Target values.
            transform: Optional transform to apply to the data.
        """
        self.data = data
        self.labels = labels
        self.transform = transform
    
    def __len__(self):
        """Return the total number of samples."""
        return len(self.data)
    
    def __getitem__(self, idx):
        """
        Return one sample. This is called by the DataLoader.
        
        Args:
            idx: Index of the sample to return.
            
        Returns:
            Tuple of (input, label).
        """
        sample = self.data[idx]
        label = self.labels[idx]
        
        if self.transform:
            sample = self.transform(sample)
        
        return torch.tensor(sample, dtype=torch.float32), torch.tensor(label, dtype=torch.long)


# Create datasets
train_dataset = CustomDataset(X_train, y_train)
val_dataset = CustomDataset(X_val, y_val)
test_dataset = CustomDataset(X_test, y_test)
```

### PyTorch DataLoader

```python
# Create DataLoaders
train_loader = DataLoader(
    train_dataset,
    batch_size=32,        # Number of samples per batch
    shuffle=True,         # Shuffle training data each epoch
    num_workers=4,        # Number of parallel data loading processes
    pin_memory=True,      # Speed up data transfer to GPU
    drop_last=True        # Drop the last incomplete batch
)

val_loader = DataLoader(
    val_dataset,
    batch_size=64,        # Can use larger batch size for validation (no gradients)
    shuffle=False,        # Do NOT shuffle validation data
    num_workers=4,
    pin_memory=True
)

# Iterating over batches
for batch_idx, (inputs, labels) in enumerate(train_loader):
    # inputs shape: (32, num_features)
    # labels shape: (32,)
    
    # Move to GPU if available
    inputs = inputs.to("cuda")
    labels = labels.to("cuda")
    
    # Forward pass, compute loss, backpropagate, update weights
    # (covered in training chapters)
    
    if batch_idx % 100 == 0:
        print(f"Batch {batch_idx}/{len(train_loader)}")
```

### Image Dataset Example

```python
import os
from PIL import Image
from torch.utils.data import Dataset
import torchvision.transforms as T

class ImageDataset(Dataset):
    """Dataset for loading images from a directory structure like:
    data/
        train/
            cats/
                cat001.jpg
                cat002.jpg
            dogs/
                dog001.jpg
                dog002.jpg
    """
    
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.samples = []
        self.class_to_idx = {}
        
        # Walk the directory tree
        classes = sorted(os.listdir(root_dir))
        for idx, class_name in enumerate(classes):
            class_dir = os.path.join(root_dir, class_name)
            if not os.path.isdir(class_dir):
                continue
            self.class_to_idx[class_name] = idx
            
            for filename in os.listdir(class_dir):
                if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
                    filepath = os.path.join(class_dir, filename)
                    self.samples.append((filepath, idx))
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        filepath, label = self.samples[idx]
        image = Image.open(filepath).convert("RGB")
        
        if self.transform:
            image = self.transform(image)
        
        return image, label
```

### Text Dataset Example

```python
class TextDataset(Dataset):
    """Dataset for text classification."""
    
    def __init__(self, texts, labels, tokenizer, max_length=512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]
        
        # Tokenize
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "label": torch.tensor(label, dtype=torch.long)
        }
```

---

## 12. Working with Text Data

### Building a Vocabulary

A vocabulary maps words (or tokens) to unique integer IDs.

```python
from collections import Counter

def build_vocabulary(texts, min_freq=2, max_size=50000):
    """
    Build a vocabulary from a list of texts.
    
    Args:
        texts: List of strings.
        min_freq: Minimum frequency for a word to be included.
        max_size: Maximum vocabulary size.
    
    Returns:
        word_to_idx: Dict mapping words to indices.
        idx_to_word: Dict mapping indices to words.
    """
    # Count all words
    word_counts = Counter()
    for text in texts:
        words = text.lower().split()
        word_counts.update(words)
    
    # Special tokens
    special_tokens = ["<PAD>", "<UNK>", "<BOS>", "<EOS>"]
    # <PAD> = padding (to make all sequences the same length)
    # <UNK> = unknown word (not in vocabulary)
    # <BOS> = beginning of sequence
    # <EOS> = end of sequence
    
    # Filter by frequency and take top N
    filtered_words = [
        word for word, count in word_counts.most_common(max_size)
        if count >= min_freq
    ]
    
    # Build mappings
    all_tokens = special_tokens + filtered_words
    word_to_idx = {word: idx for idx, word in enumerate(all_tokens)}
    idx_to_word = {idx: word for word, idx in word_to_idx.items()}
    
    return word_to_idx, idx_to_word

def text_to_indices(text, word_to_idx, max_length=100):
    """Convert text to a list of integer indices."""
    words = text.lower().split()
    indices = [word_to_idx.get(w, word_to_idx["<UNK>"]) for w in words]
    
    # Truncate or pad
    if len(indices) > max_length:
        indices = indices[:max_length]
    else:
        indices += [word_to_idx["<PAD>"]] * (max_length - len(indices))
    
    return indices
```

### Word Embeddings

Instead of representing words as single integers, we represent them as dense vectors. This is called "word embedding." Words with similar meanings will have similar vectors.

```python
import torch
import torch.nn as nn

# Create an embedding layer
vocab_size = 50000
embedding_dim = 300  # Each word is represented by a 300-dimensional vector

embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
# padding_idx=0 means the vector for index 0 (<PAD>) is always all zeros

# Look up embeddings for a batch of token IDs
token_ids = torch.tensor([[1, 5, 23, 0, 0], [7, 2, 45, 12, 0]])
# Shape: (batch_size=2, seq_length=5)

embedded = embedding(token_ids)
# Shape: (2, 5, 300) -- each token is now a 300-dim vector
```

### Pre-trained Word Embeddings

You do not have to train embeddings from scratch. Pre-trained embeddings capture semantic relationships learned from huge text corpora.

```python
import numpy as np

def load_glove_embeddings(glove_path, word_to_idx, embedding_dim=300):
    """
    Load pre-trained GloVe embeddings and create an embedding matrix.
    
    Downloaded from: https://nlp.stanford.edu/projects/glove/
    """
    embeddings = np.random.randn(len(word_to_idx), embedding_dim) * 0.01
    
    found = 0
    with open(glove_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            word = parts[0]
            if word in word_to_idx:
                idx = word_to_idx[word]
                vector = np.array(parts[1:], dtype=np.float32)
                embeddings[idx] = vector
                found += 1
    
    print(f"Found {found}/{len(word_to_idx)} words in GloVe")
    return torch.tensor(embeddings, dtype=torch.float32)

# Use pre-trained embeddings in your model
embedding_matrix = load_glove_embeddings("glove.6B.300d.txt", word_to_idx)
embedding = nn.Embedding.from_pretrained(embedding_matrix, freeze=False)
# freeze=False means the embeddings will be fine-tuned during training
```

---

## 13. Working with Image Data

### Loading and Inspecting Images

```python
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

# Load image
img = Image.open("photo.jpg")
print(f"Size: {img.size}")          # (width, height)
print(f"Mode: {img.mode}")          # RGB, L (grayscale), RGBA, etc.

# Convert to numpy array
arr = np.array(img)
print(f"Shape: {arr.shape}")        # (height, width, channels)
print(f"Dtype: {arr.dtype}")        # uint8 (0-255)
print(f"Min: {arr.min()}, Max: {arr.max()}")

# Display
plt.imshow(arr)
plt.axis("off")
plt.title("Original Image")
plt.savefig("display.png")
```

### Common Image Operations

```python
from PIL import Image, ImageFilter, ImageEnhance

img = Image.open("photo.jpg")

# Resize
img_resized = img.resize((224, 224))               # Exact size
img_thumbnail = img.copy()
img_thumbnail.thumbnail((224, 224))                  # Maintain aspect ratio

# Crop
img_cropped = img.crop((left, top, right, bottom))  # (x1, y1, x2, y2)

# Rotate
img_rotated = img.rotate(45)                         # 45 degrees

# Flip
img_flipped = img.transpose(Image.FLIP_LEFT_RIGHT)

# Color conversion
img_gray = img.convert("L")                          # Grayscale

# Filters
img_blurred = img.filter(ImageFilter.GaussianBlur(radius=3))
img_edges = img.filter(ImageFilter.FIND_EDGES)

# Enhance
enhancer = ImageEnhance.Brightness(img)
img_bright = enhancer.enhance(1.5)                   # 1.5x brighter
```

### Channel Operations

```python
import numpy as np

arr = np.array(img)  # Shape: (H, W, 3) for RGB

# Split channels
red = arr[:, :, 0]
green = arr[:, :, 1]
blue = arr[:, :, 2]

# Convert RGB to grayscale (weighted sum)
gray = 0.299 * red + 0.587 * green + 0.114 * blue

# Normalize to [0, 1]
arr_normalized = arr.astype(np.float32) / 255.0

# Standardize (ImageNet statistics)
mean = np.array([0.485, 0.456, 0.406])
std = np.array([0.229, 0.224, 0.225])
arr_standardized = (arr_normalized - mean) / std

# Convert from HWC (height, width, channels) to CHW (channels, height, width)
# PyTorch expects CHW
arr_chw = np.transpose(arr_normalized, (2, 0, 1))
print(arr_chw.shape)  # (3, H, W)
```

---

## 14. Working with Audio Data

### Loading Audio

```python
import librosa
import numpy as np
import soundfile as sf

# Load audio file
waveform, sample_rate = librosa.load("audio.wav", sr=16000)
# sr=16000 forces resampling to 16kHz
# waveform: 1D numpy array of float values in [-1, 1]

print(f"Sample rate: {sample_rate}")
print(f"Duration: {len(waveform) / sample_rate:.2f} seconds")
print(f"Shape: {waveform.shape}")

# Save audio
sf.write("output.wav", waveform, sample_rate)
```

### Spectrograms

A spectrogram converts audio from the time domain to the frequency domain, showing how the frequency content changes over time. This is the most common representation for feeding audio to neural networks.

```python
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt

# Compute mel spectrogram
mel_spec = librosa.feature.melspectrogram(
    y=waveform,
    sr=sample_rate,
    n_mels=128,        # Number of mel bands (frequency bins)
    n_fft=2048,        # FFT window size
    hop_length=512     # Step size between windows
)

# Convert to log scale (decibels)
mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)

print(f"Mel spectrogram shape: {mel_spec_db.shape}")
# (n_mels, time_steps) e.g., (128, 313) for a 10-second clip

# Visualize
plt.figure(figsize=(10, 4))
librosa.display.specshow(mel_spec_db, sr=sample_rate, hop_length=512,
                          x_axis="time", y_axis="mel")
plt.colorbar(format="%+2.0f dB")
plt.title("Mel Spectrogram")
plt.savefig("mel_spectrogram.png")
```

### MFCCs (Mel-Frequency Cepstral Coefficients)

MFCCs are a compact representation of audio often used for speech processing.

```python
mfccs = librosa.feature.mfcc(
    y=waveform,
    sr=sample_rate,
    n_mfcc=13         # Number of coefficients
)

print(f"MFCC shape: {mfccs.shape}")  # (13, time_steps)
```

---

## 15. Working with 3D Data

### Types of 3D Representations

**Point Clouds**: A collection of 3D points. Each point is (x, y, z) and may include color or normal vectors.

```python
import numpy as np

# A point cloud is simply an (N, 3) array
point_cloud = np.random.randn(10000, 3)  # 10,000 random 3D points
print(f"Point cloud shape: {point_cloud.shape}")  # (10000, 3)

# Normalize point cloud to unit sphere
centroid = point_cloud.mean(axis=0)
point_cloud -= centroid
max_dist = np.linalg.norm(point_cloud, axis=1).max()
point_cloud /= max_dist
```

**Meshes**: Vertices (3D points) connected by faces (usually triangles). More memory-efficient than point clouds for representing surfaces.

```python
import trimesh

# Load a mesh
mesh = trimesh.load("model.obj")
vertices = mesh.vertices   # (N, 3) array of 3D points
faces = mesh.faces         # (M, 3) array of triangle indices

print(f"Vertices: {vertices.shape}")
print(f"Faces: {faces.shape}")

# Sample points from the surface
points, face_indices = trimesh.sample.sample_surface(mesh, count=10000)
print(f"Sampled points: {points.shape}")  # (10000, 3)
```

**Voxel Grids**: 3D occupancy grids, like a 3D version of pixels. Each cell (voxel) is either occupied or empty.

```python
import numpy as np

# A voxel grid is a 3D binary array
resolution = 64
voxel_grid = np.zeros((resolution, resolution, resolution), dtype=np.float32)

# Mark some voxels as occupied (creating a simple cube)
voxel_grid[20:40, 20:40, 20:40] = 1.0

print(f"Voxel grid shape: {voxel_grid.shape}")  # (64, 64, 64)
print(f"Occupied voxels: {voxel_grid.sum()}")    # 8000
```

**Signed Distance Fields (SDF)**: For each point in 3D space, store the distance to the nearest surface. Negative inside the object, positive outside.

```python
import numpy as np

# Create a grid of query points
grid_points = np.mgrid[-1:1:64j, -1:1:64j, -1:1:64j].reshape(3, -1).T
# Shape: (262144, 3) -- 64^3 = 262,144 points

# For a sphere of radius 0.5 at origin, the SDF is simple
def sphere_sdf(points, center=np.array([0, 0, 0]), radius=0.5):
    """Signed distance to a sphere. Negative inside, positive outside."""
    distances = np.linalg.norm(points - center, axis=1) - radius
    return distances

sdf_values = sphere_sdf(grid_points)
print(f"SDF shape: {sdf_values.shape}")  # (262144,)
print(f"Inside: {(sdf_values < 0).sum()}")
print(f"Outside: {(sdf_values >= 0).sum()}")
```

---

## 16. Working with Tabular Data

### End-to-End Tabular Data Pipeline

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder

def prepare_tabular_data(csv_path, target_column, test_size=0.2):
    """Complete pipeline for preparing tabular data for ML."""
    
    # 1. Load data
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    
    # 2. Basic info
    print(f"\nColumn types:\n{df.dtypes}")
    print(f"\nMissing values:\n{df.isnull().sum()}")
    
    # 3. Separate features and target
    X = df.drop(columns=[target_column])
    y = df[target_column]
    
    # 4. Handle missing values
    numeric_cols = X.select_dtypes(include=[np.number]).columns
    categorical_cols = X.select_dtypes(include=["object", "category"]).columns
    
    X[numeric_cols] = X[numeric_cols].fillna(X[numeric_cols].median())
    X[categorical_cols] = X[categorical_cols].fillna("Unknown")
    
    # 5. Encode categorical variables
    label_encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        label_encoders[col] = le
    
    # 6. Encode target if it's categorical
    target_encoder = None
    if y.dtype == "object":
        target_encoder = LabelEncoder()
        y = target_encoder.fit_transform(y)
    
    # 7. Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )
    
    # 8. Scale features
    scaler = StandardScaler()
    X_train[numeric_cols] = scaler.fit_transform(X_train[numeric_cols])
    X_test[numeric_cols] = scaler.transform(X_test[numeric_cols])
    
    return X_train, X_test, y_train, y_test, scaler, label_encoders, target_encoder
```

---

## 17. Data Ethics and Bias

### Types of Bias

**Selection Bias**: Your dataset does not represent the real world. For example, if you train a face recognition model only on photos of light-skinned people, it will perform poorly on dark-skinned people.

**Measurement Bias**: The way data is collected introduces systematic errors. For example, using arrest records as a proxy for crime rates introduces biases from policing practices.

**Historical Bias**: The data reflects past injustices. For example, if you train a resume screening model on historical hiring data, it may learn to discriminate against women if the company historically hired fewer women.

**Label Bias**: The labels themselves are biased. For example, if medical images are labeled by doctors who are more likely to miss diagnoses in certain demographic groups.

### Mitigating Bias

1. **Audit your data**: Check demographic breakdowns. Are all groups represented?
2. **Measure performance across groups**: Does the model work equally well for all demographics?
3. **Use diverse data sources**: Do not rely on a single source.
4. **Consider fairness metrics**: Equal opportunity, demographic parity, calibration.
5. **Document your dataset**: Create a "datasheet" describing how the data was collected, what it contains, known limitations, and intended use.
6. **Get diverse perspectives**: Include people from different backgrounds in the data collection and evaluation process.

---

## 18. Summary

You now understand:

1. **What data is** and how different types (text, images, audio, 3D, tabular) are represented as numbers.
2. **Data formats**: CSV, JSON, Parquet, HDF5, and specialized formats for images, audio, and 3D models.
3. **Data collection**: Public datasets, web scraping, APIs, and synthetic data generation.
4. **Data cleaning**: Handling missing values, duplicates, inconsistencies, outliers, and type errors.
5. **Preprocessing**: Normalization, standardization, encoding categorical variables, tokenization.
6. **Feature engineering**: Creating informative features from raw data.
7. **Data splitting**: Train/validation/test splits and cross-validation.
8. **Data augmentation**: Creating more training data through transformations.
9. **Imbalanced data**: Oversampling, undersampling, SMOTE, class weights.
10. **Data pipelines**: PyTorch Dataset and DataLoader for efficient batch processing.
11. **Working with specific data types**: Text (vocabularies, embeddings), images (channels, transforms), audio (spectrograms, MFCCs), 3D (point clouds, meshes, voxels, SDFs).
12. **Data ethics**: Understanding and mitigating bias in datasets.

---

[<< Previous: Chapter 2 - Python Programming](./02_PYTHON_PROGRAMMING.md) | [Next: Chapter 4 - Machine Learning Fundamentals >>](./04_ML_FUNDAMENTALS.md)
