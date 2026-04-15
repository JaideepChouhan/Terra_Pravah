# Chapter 4: Machine Learning Fundamentals

## Introduction

Machine learning is the core idea behind modern AI: instead of writing explicit rules for how to solve a problem, you show a computer many examples and let it learn the rules on its own. This chapter covers the fundamental concepts, algorithms, and intuitions of machine learning -- everything you need to know before diving into neural networks and deep learning.

---

## Table of Contents

1. What Is Machine Learning?
2. Types of Machine Learning
3. The Machine Learning Workflow
4. Linear Regression -- Your First Model
5. Logistic Regression -- Classification
6. Decision Trees
7. Random Forests and Ensemble Methods
8. Support Vector Machines
9. K-Nearest Neighbors
10. Clustering (K-Means, DBSCAN)
11. Dimensionality Reduction (PCA, t-SNE)
12. Evaluation Metrics
13. Overfitting and Underfitting
14. Regularization
15. Hyperparameter Tuning
16. The Bias-Variance Tradeoff
17. Summary

---

## 1. What Is Machine Learning?

Traditional programming works like this:
- You write rules (code).
- You give the program data (input).
- The program produces output based on the rules.

Machine learning flips this:
- You give the program data (input) AND the desired output.
- The program learns the rules.

In other words: **Traditional programming is "rules + data = output." Machine learning is "data + output = rules."**

### A Concrete Example

Suppose you want to build a spam email filter.

**Traditional approach**: You manually write rules:
- If the email contains "Nigerian prince," mark it as spam.
- If the email contains "free money," mark it as spam.
- If the sender is in the contact list, mark it as not spam.
- ... hundreds more rules.

This is tedious, incomplete (you will never think of every rule), and brittle (spammers will change their wording).

**Machine learning approach**:
1. Collect 100,000 emails that humans have already labeled as "spam" or "not spam."
2. Feed those emails to a machine learning algorithm.
3. The algorithm examines the emails and discovers patterns on its own (certain words, certain sender patterns, certain formatting, etc.).
4. The algorithm produces a "model" -- a mathematical function that takes in a new email and predicts "spam" or "not spam."

The model will catch spam patterns you never would have thought of, and it can be updated simply by feeding it more labeled emails.

### The Key Vocabulary

- **Model**: A mathematical function that maps inputs to outputs. The "learned rules."
- **Training**: The process of feeding data to an algorithm so it can learn the model.
- **Parameters**: The internal values of the model that are adjusted during training. For example, in a linear model y = wx + b, the parameters are w (weight) and b (bias).
- **Hyperparameters**: Settings that you (the human) choose before training. For example, the learning rate, the number of training iterations, the model architecture. These are not learned from the data.
- **Features**: The input variables. For a house price prediction model, features might be square footage, number of bedrooms, location, etc.
- **Labels (or Targets)**: The output variable you want to predict. For house price prediction, the label is the price.
- **Training data**: The data used to train the model.
- **Test data**: Data the model has never seen, used to evaluate how well it generalizes.
- **Loss function (or cost function)**: A function that measures how wrong the model's predictions are. Training tries to minimize this.
- **Epoch**: One complete pass through all training data.
- **Batch**: A subset of training data processed at once.
- **Inference**: Using a trained model to make predictions on new data.

---

## 2. Types of Machine Learning

### Supervised Learning

You have labeled data -- both inputs and the correct outputs. The model learns to predict the output from the input.

**Regression**: The output is a continuous number.
- Predicting house prices (output: $350,000)
- Predicting temperature (output: 23.5 degrees)
- Predicting stock prices (output: $142.30)

**Classification**: The output is a category.
- Spam detection (output: spam or not spam)
- Image classification (output: cat, dog, bird, etc.)
- Sentiment analysis (output: positive, negative, neutral)

### Unsupervised Learning

You have data but no labels. The model finds patterns, structure, or groupings in the data on its own.

**Clustering**: Grouping similar items together.
- Grouping customers by purchasing behavior.
- Grouping documents by topic.
- Grouping genes by expression patterns.

**Dimensionality Reduction**: Finding a simpler representation of the data.
- Compressing 1000-dimensional data down to 2 dimensions for visualization.
- Removing redundant features.

**Anomaly Detection**: Finding unusual data points.
- Detecting fraudulent transactions.
- Detecting manufacturing defects.
- Detecting network intrusions.

### Semi-Supervised Learning

You have a small amount of labeled data and a large amount of unlabeled data. The model uses both to learn. This is very common in practice because labeled data is expensive to create.

### Self-Supervised Learning

The model creates its own labels from the data. For example:
- A language model is trained to predict the next word in a sentence. The "label" is just the next word, which comes from the text itself.
- A model is trained to predict a masked-out patch of an image from the surrounding pixels.

This is the technique behind GPT, BERT, and most modern large AI models.

### Reinforcement Learning

An "agent" learns by interacting with an "environment." It takes actions, receives rewards or penalties, and learns to maximize the total reward over time.

- A robot learning to walk (reward: forward movement, penalty: falling down).
- A game-playing AI learning to win chess (reward: winning, penalty: losing).
- A chatbot learning to give helpful responses (reward: positive human feedback).

---

## 3. The Machine Learning Workflow

Every machine learning project follows roughly the same steps:

```
1. Define the problem
   What are you trying to predict? What data do you have?
   
2. Collect and explore data
   Gather data, visualize it, understand its distribution.
   
3. Prepare data
   Clean, preprocess, split into train/val/test.
   
4. Choose a model
   Start simple (linear model, decision tree), then try more complex ones.
   
5. Train the model
   Fit the model to your training data.
   
6. Evaluate the model
   Check performance on the validation set. Look at metrics.*
   
7. Tune hyperparameters
   Adjust settings to improve performance.
   
8. Evaluate on test set
   Final, unbiased performance estimate.
   
9. Deploy the model
   Put it into production where it can make predictions on new data.
   
10. Monitor and maintain
    Check that the model continues to perform well over time.
```

---

## 4. Linear Regression -- Your First Model

Linear regression is the simplest machine learning model. It learns a straight line (or a hyperplane in higher dimensions) that best fits the data.

### The Idea

We want to predict a continuous output $y$ from an input $x$. We assume the relationship is approximately linear:

$$y = wx + b$$

Where:
- $w$ is the weight (slope) -- how much $y$ changes when $x$ changes by 1.
- $b$ is the bias (intercept) -- the value of $y$ when $x = 0$.

With multiple input features $x_1, x_2, ..., x_n$:

$$y = w_1 x_1 + w_2 x_2 + ... + w_n x_n + b$$

Or in vector form: $y = \mathbf{w} \cdot \mathbf{x} + b$

### How Training Works

**Step 1**: Start with random values for $w$ and $b$.

**Step 2**: For each training example, compute the prediction: $\hat{y} = wx + b$.

**Step 3**: Compute how wrong the prediction is using a loss function. For regression, the most common loss is **Mean Squared Error (MSE)**:

$$\text{MSE} = \frac{1}{N} \sum_{i=1}^{N} (y_i - \hat{y}_i)^2$$

This squares the errors (so positive and negative errors do not cancel out) and averages them.

**Step 4**: Compute the gradients -- how should we change $w$ and $b$ to reduce the loss?

$$\frac{\partial \text{MSE}}{\partial w} = \frac{-2}{N} \sum_{i=1}^{N} x_i (y_i - \hat{y}_i)$$

$$\frac{\partial \text{MSE}}{\partial b} = \frac{-2}{N} \sum_{i=1}^{N} (y_i - \hat{y}_i)$$

**Step 5**: Update the parameters:

$$w \leftarrow w - \alpha \cdot \frac{\partial \text{MSE}}{\partial w}$$

$$b \leftarrow b - \alpha \cdot \frac{\partial \text{MSE}}{\partial b}$$

Where $\alpha$ is the **learning rate** -- a small number (e.g., 0.01) that controls how big a step we take.

**Step 6**: Repeat steps 2-5 for many iterations until the loss stops decreasing.

### Implementation from Scratch

```python
import numpy as np

class LinearRegression:
    """Linear regression implemented from scratch using gradient descent."""
    
    def __init__(self, learning_rate=0.01, n_iterations=1000):
        self.learning_rate = learning_rate
        self.n_iterations = n_iterations
        self.weights = None
        self.bias = None
        self.loss_history = []
    
    def fit(self, X, y):
        """
        Train the model.
        
        Args:
            X: Training features, shape (n_samples, n_features)
            y: Target values, shape (n_samples,)
        """
        n_samples, n_features = X.shape
        
        # Initialize parameters to zeros
        self.weights = np.zeros(n_features)
        self.bias = 0
        
        # Gradient descent
        for i in range(self.n_iterations):
            # Forward pass: compute predictions
            y_pred = np.dot(X, self.weights) + self.bias
            
            # Compute loss (MSE)
            loss = np.mean((y - y_pred) ** 2)
            self.loss_history.append(loss)
            
            # Compute gradients
            dw = -(2 / n_samples) * np.dot(X.T, (y - y_pred))
            db = -(2 / n_samples) * np.sum(y - y_pred)
            
            # Update parameters
            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db
            
            # Print progress
            if (i + 1) % 100 == 0:
                print(f"Iteration {i+1}/{self.n_iterations}, Loss: {loss:.6f}")
    
    def predict(self, X):
        """Make predictions on new data."""
        return np.dot(X, self.weights) + self.bias


# Example usage
np.random.seed(42)

# Generate synthetic data: y = 3x1 + 5x2 + 7 + noise
n_samples = 1000
X = np.random.randn(n_samples, 2)
y = 3 * X[:, 0] + 5 * X[:, 1] + 7 + np.random.randn(n_samples) * 0.5

# Split
X_train, X_test = X[:800], X[800:]
y_train, y_test = y[:800], y[800:]

# Train
model = LinearRegression(learning_rate=0.01, n_iterations=1000)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
mse = np.mean((y_test - y_pred) ** 2)
print(f"\nTest MSE: {mse:.6f}")
print(f"Learned weights: {model.weights}")  # Should be close to [3, 5]
print(f"Learned bias: {model.bias:.4f}")     # Should be close to 7
```

### Using scikit-learn

```python
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Train
model = LinearRegression()
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)

# Evaluate
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"MSE: {mse:.6f}")
print(f"R-squared: {r2:.6f}")  # 1.0 = perfect, 0.0 = as good as predicting the mean
print(f"Coefficients: {model.coef_}")
print(f"Intercept: {model.intercept_:.4f}")
```

---

## 5. Logistic Regression -- Classification

Despite its name, logistic regression is used for **classification**, not regression. It predicts the probability that an input belongs to a particular class.

### The Idea

For binary classification (two classes: 0 or 1), we want to output a probability between 0 and 1. We use the **sigmoid function** to squash any number into this range:

$$\sigma(z) = \frac{1}{1 + e^{-z}}$$

The model computes: $z = \mathbf{w} \cdot \mathbf{x} + b$, then applies sigmoid: $p = \sigma(z)$.

If $p > 0.5$, predict class 1. Otherwise, predict class 0.

### Loss Function: Binary Cross-Entropy

For classification, MSE is a poor loss function. Instead, we use **binary cross-entropy** (also called log loss):

$$\text{BCE} = -\frac{1}{N} \sum_{i=1}^{N} \left[ y_i \log(\hat{p}_i) + (1 - y_i) \log(1 - \hat{p}_i) \right]$$

Intuition:
- If the true label $y_i = 1$ and the model predicts $\hat{p}_i = 0.99$, the loss is $-\log(0.99) = 0.01$ (very small -- good!).
- If the true label $y_i = 1$ and the model predicts $\hat{p}_i = 0.01$, the loss is $-\log(0.01) = 4.6$ (very large -- bad!).
- If the true label $y_i = 0$ and the model predicts $\hat{p}_i = 0.01$, the loss is $-\log(0.99) = 0.01$ (very small -- good!).

### Implementation from Scratch

```python
import numpy as np

class LogisticRegression:
    """Logistic regression implemented from scratch."""
    
    def __init__(self, learning_rate=0.01, n_iterations=1000):
        self.learning_rate = learning_rate
        self.n_iterations = n_iterations
        self.weights = None
        self.bias = None
    
    def sigmoid(self, z):
        """Sigmoid function with numerical stability."""
        return 1 / (1 + np.exp(-np.clip(z, -500, 500)))
    
    def fit(self, X, y):
        n_samples, n_features = X.shape
        self.weights = np.zeros(n_features)
        self.bias = 0
        
        for i in range(self.n_iterations):
            # Forward pass
            z = np.dot(X, self.weights) + self.bias
            predictions = self.sigmoid(z)
            
            # Compute loss (binary cross-entropy)
            epsilon = 1e-15  # Small value to avoid log(0)
            loss = -np.mean(
                y * np.log(predictions + epsilon) +
                (1 - y) * np.log(1 - predictions + epsilon)
            )
            
            # Compute gradients
            dw = (1 / n_samples) * np.dot(X.T, (predictions - y))
            db = (1 / n_samples) * np.sum(predictions - y)
            
            # Update parameters
            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db
            
            if (i + 1) % 100 == 0:
                print(f"Iteration {i+1}, Loss: {loss:.6f}")
    
    def predict_proba(self, X):
        """Predict probabilities."""
        z = np.dot(X, self.weights) + self.bias
        return self.sigmoid(z)
    
    def predict(self, X, threshold=0.5):
        """Predict class labels."""
        probabilities = self.predict_proba(X)
        return (probabilities >= threshold).astype(int)


# Example usage
from sklearn.datasets import make_classification

X, y = make_classification(n_samples=1000, n_features=2, n_redundant=0, 
                           n_informative=2, random_state=42, n_clusters_per_class=1)

X_train, X_test = X[:800], X[800:]
y_train, y_test = y[:800], y[800:]

model = LogisticRegression(learning_rate=0.1, n_iterations=1000)
model.fit(X_train, y_train)

predictions = model.predict(X_test)
accuracy = np.mean(predictions == y_test)
print(f"Accuracy: {accuracy:.4f}")
```

### Multiclass Classification: Softmax

For more than two classes, we extend logistic regression using the **softmax function**:

$$\text{softmax}(z_i) = \frac{e^{z_i}}{\sum_{j=1}^{K} e^{z_j}}$$

This converts K raw scores into K probabilities that sum to 1.

Example: If the raw scores for classes [cat, dog, bird] are [2.0, 1.0, 0.5]:

$$p_{\text{cat}} = \frac{e^{2.0}}{e^{2.0} + e^{1.0} + e^{0.5}} = \frac{7.39}{7.39 + 2.72 + 1.65} = 0.63$$

$$p_{\text{dog}} = \frac{e^{1.0}}{e^{2.0} + e^{1.0} + e^{0.5}} = \frac{2.72}{11.76} = 0.23$$

$$p_{\text{bird}} = \frac{e^{0.5}}{e^{2.0} + e^{1.0} + e^{0.5}} = \frac{1.65}{11.76} = 0.14$$

The loss function for multiclass is **categorical cross-entropy**:

$$\text{CCE} = -\frac{1}{N} \sum_{i=1}^{N} \sum_{k=1}^{K} y_{i,k} \log(\hat{p}_{i,k})$$

---

## 6. Decision Trees

Decision trees make predictions by asking a series of yes/no questions about the features, creating a tree-like structure of decisions.

### How It Works

Think of playing "20 Questions." The tree asks questions that maximally split the data into pure groups.

Example: Predicting whether someone will buy a product.

```
                Is age > 30?
               /            \
            Yes              No
           /                   \
    Is income > 50k?       Is student?
     /          \           /         \
   Yes          No        Yes         No
   |            |          |           |
 BUY         NO BUY      BUY       NO BUY
```

### Splitting Criteria

The tree needs to decide which question to ask at each step. It chooses the question that best separates the data.

**Gini Impurity** (for classification): Measures how "mixed" a set is.

$$\text{Gini}(S) = 1 - \sum_{k=1}^{K} p_k^2$$

Where $p_k$ is the proportion of class $k$ in the set.
- Gini = 0 means the set is pure (all one class).
- Gini = 0.5 means maximum impurity for two classes (50/50 split).

**Information Gain** (for classification): Based on entropy, measures how much information we gain by splitting.

$$\text{Entropy}(S) = -\sum_{k=1}^{K} p_k \log_2(p_k)$$

$$\text{Information Gain} = \text{Entropy}(S) - \sum_v \frac{|S_v|}{|S|} \text{Entropy}(S_v)$$

**Variance Reduction** (for regression): Chooses the split that minimizes the variance of the target in each subset.

### Implementation from Scratch

```python
import numpy as np
from collections import Counter

class DecisionTreeNode:
    """A node in the decision tree."""
    
    def __init__(self, feature_idx=None, threshold=None, left=None, right=None, value=None):
        self.feature_idx = feature_idx  # Which feature to split on
        self.threshold = threshold      # Threshold value for the split
        self.left = left                # Left child (feature <= threshold)
        self.right = right              # Right child (feature > threshold)
        self.value = value              # Prediction (for leaf nodes)


class DecisionTree:
    """Decision tree classifier implemented from scratch."""
    
    def __init__(self, max_depth=10, min_samples_split=2):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.root = None
    
    def gini_impurity(self, y):
        """Calculate Gini impurity of a set."""
        counter = Counter(y)
        total = len(y)
        impurity = 1.0
        for count in counter.values():
            p = count / total
            impurity -= p ** 2
        return impurity
    
    def find_best_split(self, X, y):
        """Find the best feature and threshold to split on."""
        best_gain = -1
        best_feature = None
        best_threshold = None
        
        current_gini = self.gini_impurity(y)
        n_samples, n_features = X.shape
        
        for feature_idx in range(n_features):
            thresholds = np.unique(X[:, feature_idx])
            
            for threshold in thresholds:
                left_mask = X[:, feature_idx] <= threshold
                right_mask = ~left_mask
                
                if left_mask.sum() == 0 or right_mask.sum() == 0:
                    continue
                
                # Weighted Gini of children
                left_gini = self.gini_impurity(y[left_mask])
                right_gini = self.gini_impurity(y[right_mask])
                
                weighted_gini = (
                    (left_mask.sum() / n_samples) * left_gini +
                    (right_mask.sum() / n_samples) * right_gini
                )
                
                gain = current_gini - weighted_gini
                
                if gain > best_gain:
                    best_gain = gain
                    best_feature = feature_idx
                    best_threshold = threshold
        
        return best_feature, best_threshold, best_gain
    
    def build_tree(self, X, y, depth=0):
        """Recursively build the tree."""
        n_samples = len(y)
        n_classes = len(set(y))
        
        # Stopping conditions
        if (depth >= self.max_depth or 
            n_classes == 1 or 
            n_samples < self.min_samples_split):
            # Create leaf node with the most common class
            most_common = Counter(y).most_common(1)[0][0]
            return DecisionTreeNode(value=most_common)
        
        # Find best split
        feature_idx, threshold, gain = self.find_best_split(X, y)
        
        if gain <= 0:
            most_common = Counter(y).most_common(1)[0][0]
            return DecisionTreeNode(value=most_common)
        
        # Split the data
        left_mask = X[:, feature_idx] <= threshold
        right_mask = ~left_mask
        
        left_child = self.build_tree(X[left_mask], y[left_mask], depth + 1)
        right_child = self.build_tree(X[right_mask], y[right_mask], depth + 1)
        
        return DecisionTreeNode(
            feature_idx=feature_idx,
            threshold=threshold,
            left=left_child,
            right=right_child
        )
    
    def fit(self, X, y):
        """Train the decision tree."""
        self.root = self.build_tree(X, y)
    
    def predict_single(self, x, node):
        """Predict for a single sample."""
        if node.value is not None:
            return node.value
        
        if x[node.feature_idx] <= node.threshold:
            return self.predict_single(x, node.left)
        else:
            return self.predict_single(x, node.right)
    
    def predict(self, X):
        """Predict for multiple samples."""
        return np.array([self.predict_single(x, self.root) for x in X])
```

---

## 7. Random Forests and Ensemble Methods

### The Problem with Single Trees

A single decision tree tends to overfit -- it memorizes the training data and performs poorly on new data. Ensemble methods combine multiple "weak" models into one "strong" model.

### Random Forests

A Random Forest is a collection of decision trees, each trained on a random subset of the data and a random subset of features. The final prediction is the majority vote (classification) or average (regression) of all trees.

**Why this works**: Each tree sees slightly different data and features, so they make different errors. When you average them, the errors tend to cancel out. This is called the "wisdom of the crowd" effect.

```python
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score

# Classification
clf = RandomForestClassifier(
    n_estimators=100,      # Number of trees
    max_depth=10,          # Maximum depth per tree
    min_samples_split=5,   # Minimum samples to split a node
    max_features="sqrt",   # Number of features to consider per split
    random_state=42,
    n_jobs=-1              # Use all CPU cores
)

clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")

# Feature importance
importances = clf.feature_importances_
for feature, importance in sorted(zip(feature_names, importances), 
                                   key=lambda x: -x[1]):
    print(f"  {feature}: {importance:.4f}")
```

### Gradient Boosting

Gradient Boosting builds trees sequentially, where each new tree tries to correct the errors of the previous trees.

```python
from sklearn.ensemble import GradientBoostingClassifier

# Using sklearn
gb = GradientBoostingClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=3,
    random_state=42
)
gb.fit(X_train, y_train)

# Using XGBoost (faster and more powerful)
import xgboost as xgb

xgb_model = xgb.XGBClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5,
    eval_metric="logloss",
    random_state=42
)
xgb_model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=10)
```

### Bagging vs. Boosting

**Bagging** (Bootstrap Aggregating): Train multiple models independently on random subsets of data, then average their predictions. Example: Random Forest.
- Reduces variance (overfitting).
- Models are trained in parallel.

**Boosting**: Train models sequentially, each one focusing on the errors of the previous ones. Example: XGBoost, LightGBM.
- Reduces bias (underfitting).
- Models are trained sequentially.

---

## 8. Support Vector Machines

SVMs find the hyperplane that maximally separates two classes. The "support vectors" are the data points closest to the decision boundary.

### The Idea

Imagine you have red and blue dots on a piece of paper and you want to draw a line separating them. There are many possible lines, but the SVM finds the one with the largest "margin" -- the greatest distance between the line and the nearest points of each class.

### The Kernel Trick

Real data is often not linearly separable. The kernel trick maps data into a higher-dimensional space where it becomes separable, without actually computing the high-dimensional coordinates.

```python
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# SVM with different kernels
svm_linear = Pipeline([
    ("scaler", StandardScaler()),
    ("svm", SVC(kernel="linear", C=1.0))
])

svm_rbf = Pipeline([
    ("scaler", StandardScaler()),
    ("svm", SVC(kernel="rbf", C=1.0, gamma="scale"))
])

svm_poly = Pipeline([
    ("scaler", StandardScaler()),
    ("svm", SVC(kernel="poly", degree=3, C=1.0))
])

# Train and evaluate
svm_rbf.fit(X_train, y_train)
accuracy = svm_rbf.score(X_test, y_test)
print(f"SVM Accuracy: {accuracy:.4f}")
```

**C parameter**: Controls the trade-off between a smooth decision boundary and classifying training points correctly. High C = less regularization (might overfit). Low C = more regularization (might underfit).

---

## 9. K-Nearest Neighbors

KNN is one of the simplest algorithms: to classify a new point, find the K nearest training points and take a majority vote.

### How It Works

1. Store all training data (no actual "training" step).
2. For a new point, calculate the distance to every training point.
3. Find the K closest training points (K is a hyperparameter, e.g., 5).
4. For classification: the predicted class is the most common class among those K neighbors.
5. For regression: the prediction is the average of those K neighbors' values.

```python
from sklearn.neighbors import KNeighborsClassifier

knn = KNeighborsClassifier(
    n_neighbors=5,           # K
    weights="distance",       # Closer neighbors have more influence
    metric="euclidean"        # Distance metric
)

knn.fit(X_train, y_train)
accuracy = knn.score(X_test, y_test)
print(f"KNN Accuracy: {accuracy:.4f}")
```

**Choosing K**:
- Small K (e.g., 1): Very sensitive to noise. Can overfit.
- Large K (e.g., 100): Very smooth predictions. Can underfit.
- Common practice: Try several values of K and pick the one with the best validation accuracy.
- Rule of thumb: Start with $K = \sqrt{N}$ where N is the number of training samples.

**Pros**: Simple, no training time, works well for small datasets.
**Cons**: Slow at prediction time for large datasets (must compute distance to every training point), does not work well in high dimensions ("curse of dimensionality").

---

## 10. Clustering (K-Means, DBSCAN)

Clustering is unsupervised learning -- finding groups in data without labels.

### K-Means

K-Means partitions data into K clusters by iteratively assigning points to the nearest cluster center and updating cluster centers.

**Algorithm**:
1. Choose K (number of clusters).
2. Randomly initialize K cluster centroids.
3. Assign each point to the nearest centroid.
4. Recompute each centroid as the mean of its assigned points.
5. Repeat steps 3-4 until centroids stop moving (or a maximum number of iterations).

```python
from sklearn.cluster import KMeans
import numpy as np

# Generate some clustered data
from sklearn.datasets import make_blobs
X, true_labels = make_blobs(n_samples=300, centers=4, random_state=42)

# K-Means clustering
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
kmeans.fit(X)

predicted_labels = kmeans.labels_
centroids = kmeans.cluster_centers_

print(f"Cluster sizes: {np.bincount(predicted_labels)}")
print(f"Inertia (sum of squared distances): {kmeans.inertia_:.2f}")
```

**Choosing K**: Use the "elbow method" -- plot inertia vs K and look for the "elbow" point where adding more clusters stops helping much.

```python
inertias = []
K_range = range(1, 11)
for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X)
    inertias.append(km.inertia_)

# Plot inertia vs K -- look for the "elbow"
import matplotlib.pyplot as plt
plt.plot(K_range, inertias, "bo-")
plt.xlabel("Number of Clusters (K)")
plt.ylabel("Inertia")
plt.title("Elbow Method")
plt.savefig("elbow.png")
```

### DBSCAN

DBSCAN (Density-Based Spatial Clustering of Applications with Noise) finds clusters of arbitrary shape based on density. It does not require you to specify K in advance.

```python
from sklearn.cluster import DBSCAN

dbscan = DBSCAN(
    eps=0.5,            # Maximum distance between two samples in the same neighborhood
    min_samples=5       # Minimum points to form a dense region (cluster)
)
dbscan.fit(X)

labels = dbscan.labels_
n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
n_noise = (labels == -1).sum()

print(f"Clusters found: {n_clusters}")
print(f"Noise points: {n_noise}")
```

---

## 11. Dimensionality Reduction (PCA, t-SNE)

### PCA (Principal Component Analysis)

PCA finds the directions (principal components) along which the data varies the most, and projects the data onto those directions. This reduces the number of features while preserving as much information as possible.

```python
from sklearn.decomposition import PCA
import numpy as np

# Reduce 100-dimensional data to 2 dimensions for visualization
pca = PCA(n_components=2)
X_reduced = pca.fit_transform(X_high_dimensional)

print(f"Original shape: {X_high_dimensional.shape}")   # (1000, 100)
print(f"Reduced shape: {X_reduced.shape}")              # (1000, 2)
print(f"Explained variance ratio: {pca.explained_variance_ratio_}")
print(f"Total variance retained: {sum(pca.explained_variance_ratio_):.4f}")

# Choose n_components to retain 95% of variance
pca_95 = PCA(n_components=0.95)
X_95 = pca_95.fit_transform(X_high_dimensional)
print(f"Components needed for 95% variance: {pca_95.n_components_}")
```

### t-SNE

t-SNE is a non-linear dimensionality reduction technique that is excellent for visualization. It preserves local structure -- points that are close in high dimensions stay close in low dimensions.

```python
from sklearn.manifold import TSNE

tsne = TSNE(
    n_components=2,
    perplexity=30,      # Roughly how many neighbors to consider
    random_state=42,
    n_iter=1000
)
X_tsne = tsne.fit_transform(X_high_dimensional)

# Visualize
import matplotlib.pyplot as plt
plt.scatter(X_tsne[:, 0], X_tsne[:, 1], c=labels, cmap="viridis", alpha=0.5, s=10)
plt.title("t-SNE Visualization")
plt.savefig("tsne.png")
```

**Important**: t-SNE is only for visualization. You cannot use it for feature engineering or apply it to new data (it does not have a `.transform()` method -- the mapping is not generalizable).

---

## 12. Evaluation Metrics

### Regression Metrics

```python
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np

# Mean Squared Error (MSE)
mse = mean_squared_error(y_true, y_pred)

# Root Mean Squared Error (RMSE) -- same units as the target
rmse = np.sqrt(mse)

# Mean Absolute Error (MAE) -- less sensitive to outliers than MSE
mae = mean_absolute_error(y_true, y_pred)

# R-squared -- proportion of variance explained (1.0 = perfect, 0.0 = baseline)
r2 = r2_score(y_true, y_pred)

print(f"MSE: {mse:.4f}")
print(f"RMSE: {rmse:.4f}")
print(f"MAE: {mae:.4f}")
print(f"R-squared: {r2:.4f}")
```

### Classification Metrics

```python
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                              f1_score, confusion_matrix, classification_report,
                              roc_auc_score)

# Accuracy: fraction of correct predictions
accuracy = accuracy_score(y_true, y_pred)

# Precision: of all positive predictions, how many were correct?
precision = precision_score(y_true, y_pred)

# Recall: of all actual positives, how many did we find?
recall = recall_score(y_true, y_pred)

# F1 Score: harmonic mean of precision and recall
f1 = f1_score(y_true, y_pred)

# Confusion Matrix
cm = confusion_matrix(y_true, y_pred)
# [[True Negatives, False Positives],
#  [False Negatives, True Positives]]

# Full classification report
print(classification_report(y_true, y_pred))

# AUC-ROC (requires probability predictions)
auc = roc_auc_score(y_true, y_pred_proba)
```

**When to use which**:
- **Accuracy**: When classes are balanced.
- **Precision**: When false positives are costly (e.g., spam filter -- do not want to miss real emails).
- **Recall**: When false negatives are costly (e.g., disease detection -- do not want to miss a sick patient).
- **F1**: When you need a balance between precision and recall.
- **AUC-ROC**: When you want to evaluate across all thresholds.

### Understanding Confusion Matrix

```
                    Predicted Positive    Predicted Negative
Actual Positive     True Positive (TP)    False Negative (FN)
Actual Negative     False Positive (FP)   True Negative (TN)

Precision = TP / (TP + FP)     "Of all I said were positive, how many actually were?"
Recall    = TP / (TP + FN)     "Of all actual positives, how many did I catch?"
Accuracy  = (TP + TN) / Total  "Overall, how often am I correct?"
```

---

## 13. Overfitting and Underfitting

### Overfitting

Overfitting is when the model memorizes the training data -- including its noise and quirks -- instead of learning the general pattern. It performs well on training data but poorly on new data.

**Signs of overfitting**:
- Training accuracy is very high, but validation accuracy is much lower.
- The model is very complex (many parameters, deep tree, high polynomial degree).
- The training loss keeps decreasing but validation loss starts increasing.

**Causes**:
- Too little training data.
- Too complex a model.
- Training for too many epochs.

### Underfitting

Underfitting is when the model is too simple to capture the patterns in the data. It performs poorly on both training and new data.

**Signs of underfitting**:
- Both training and validation accuracy are low.
- The model is very simple (linear model for a non-linear problem).

**Causes**:
- Model is not complex enough.
- Not enough training.
- Features are not informative.

### Visualizing the Trade-off

```
Model Complexity  ->  Low    |    Medium    |    High
                     --------|-------------|--------
Training Error       High    |    Low      |    Very Low
Validation Error     High    |    Low      |    High
                     --------|-------------|--------
Diagnosis            Under-  |    Good     |    Over-
                     fitting |    fit      |    fitting
```

---

## 14. Regularization

Regularization is a set of techniques to prevent overfitting by constraining the model.

### L1 Regularization (Lasso)

Adds the absolute value of weights to the loss function:

$$\text{Loss} = \text{MSE} + \lambda \sum_{i} |w_i|$$

Effect: Pushes some weights to exactly zero, effectively performing feature selection. Useful when you have many features and suspect most are irrelevant.

### L2 Regularization (Ridge)

Adds the squared value of weights to the loss function:

$$\text{Loss} = \text{MSE} + \lambda \sum_{i} w_i^2$$

Effect: Shrinks all weights toward zero but does not eliminate any completely. Prevents any single feature from having too much influence.

### Elastic Net

Combines L1 and L2:

$$\text{Loss} = \text{MSE} + \lambda_1 \sum_{i} |w_i| + \lambda_2 \sum_{i} w_i^2$$

```python
from sklearn.linear_model import Ridge, Lasso, ElasticNet

# Ridge (L2)
ridge = Ridge(alpha=1.0)  # alpha = lambda
ridge.fit(X_train, y_train)

# Lasso (L1)
lasso = Lasso(alpha=0.1)
lasso.fit(X_train, y_train)

# Elastic Net
elastic = ElasticNet(alpha=0.1, l1_ratio=0.5)  # l1_ratio controls L1 vs L2 balance
elastic.fit(X_train, y_train)
```

### Dropout (for Neural Networks)

During training, randomly set a fraction of neurons to zero. This prevents co-adaptation (neurons relying too much on each other). We cover this in detail in the neural network chapters.

### Early Stopping

Stop training when the validation loss starts increasing, even if the training loss is still decreasing.

```python
best_val_loss = float("inf")
patience = 10
patience_counter = 0

for epoch in range(max_epochs):
    train_loss = train_one_epoch(model, train_loader)
    val_loss = evaluate(model, val_loader)
    
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        patience_counter = 0
        # Save the best model
        save_model(model, "best_model.pt")
    else:
        patience_counter += 1
        if patience_counter >= patience:
            print(f"Early stopping at epoch {epoch}")
            break
```

---

## 15. Hyperparameter Tuning

### Grid Search

Try every combination of hyperparameters.

```python
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier

param_grid = {
    "n_estimators": [50, 100, 200],
    "max_depth": [5, 10, 20, None],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf": [1, 2, 4]
}

grid_search = GridSearchCV(
    RandomForestClassifier(random_state=42),
    param_grid,
    cv=5,
    scoring="accuracy",
    n_jobs=-1,
    verbose=1
)

grid_search.fit(X_train, y_train)

print(f"Best parameters: {grid_search.best_params_}")
print(f"Best CV accuracy: {grid_search.best_score_:.4f}")
```

### Random Search

Sample random combinations of hyperparameters. Often more efficient than grid search because it explores more of the parameter space.

```python
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import randint, uniform

param_distributions = {
    "n_estimators": randint(50, 500),
    "max_depth": randint(3, 30),
    "min_samples_split": randint(2, 20),
    "min_samples_leaf": randint(1, 10),
    "max_features": uniform(0.1, 0.9)
}

random_search = RandomizedSearchCV(
    RandomForestClassifier(random_state=42),
    param_distributions,
    n_iter=100,        # Number of random combinations to try
    cv=5,
    scoring="accuracy",
    n_jobs=-1,
    random_state=42
)

random_search.fit(X_train, y_train)

print(f"Best parameters: {random_search.best_params_}")
print(f"Best CV accuracy: {random_search.best_score_:.4f}")
```

---

## 16. The Bias-Variance Tradeoff

This is one of the most important concepts in machine learning.

**Bias**: The error introduced by approximating a complex real-world problem with a simple model. High bias means the model makes strong (wrong) assumptions. This is underfitting.

**Variance**: The error introduced by the model's sensitivity to the specific training data. High variance means the model changes drastically when trained on different data. This is overfitting.

**Total Error = Bias^2 + Variance + Irreducible Error**

- **Irreducible error** is the noise in the data itself. No model can eliminate it.
- As you make the model more complex, bias decreases but variance increases.
- The sweet spot is where their sum is minimized.

```
Error
  |    \                        /
  |     \  Total Error         /
  |      \      ___           /
  |       \   /    \         /
  |        \_/      \       /    Variance
  |         |        \     /
  |  Bias   |         \___/
  |         |
  |---------|----------------------> Model Complexity
           Sweet Spot
```

---

## 17. Summary

You now understand the core concepts of machine learning:

1. **What ML is**: Learning rules from data + desired outputs.
2. **Types of ML**: Supervised, unsupervised, semi-supervised, self-supervised, reinforcement learning.
3. **The ML workflow**: From problem definition to deployment.
4. **Linear regression**: Predicting continuous values with a linear model.
5. **Logistic regression**: Classification using sigmoid and cross-entropy.
6. **Decision trees**: Making predictions through a series of questions.
7. **Random forests**: Combining many trees for better predictions.
8. **SVMs**: Finding maximum-margin decision boundaries.
9. **KNN**: Predicting based on nearest neighbors.
10. **Clustering**: Finding groups in unlabeled data (K-Means, DBSCAN).
11. **Dimensionality reduction**: PCA for compression, t-SNE for visualization.
12. **Evaluation metrics**: MSE, RMSE, MAE, R-squared, accuracy, precision, recall, F1, AUC.
13. **Overfitting vs underfitting**: The fundamental tension in ML.
14. **Regularization**: L1, L2, dropout, early stopping.
15. **Hyperparameter tuning**: Grid search and random search.
16. **Bias-variance tradeoff**: The theoretical underpinning of the overfitting/underfitting trade-off.

---

[<< Previous: Chapter 3 - Data Fundamentals](./03_DATA_FUNDAMENTALS.md) | [Next: Chapter 5 - Neural Networks >>](./05_NEURAL_NETWORKS.md)
