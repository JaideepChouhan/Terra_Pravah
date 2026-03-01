# Chapter 6: Training Deep Networks -- Practical Guide

## Introduction

Knowing the theory of neural networks is one thing. Actually training them successfully is another. This chapter covers everything you need to know about the practical side of training: how to set up a training pipeline, how to debug common problems, how to monitor training, how to use GPUs, how to train on large datasets, and how to achieve the best possible performance.

---

## Table of Contents

1. The Complete Training Pipeline
2. GPU Computing with CUDA
3. Mixed Precision Training
4. Gradient Clipping
5. Learning Rate Scheduling in Practice
6. Data Parallelism and Distributed Training
7. Logging and Monitoring with TensorBoard and Weights & Biases
8. Debugging Neural Networks
9. Common Training Problems and Solutions
10. Transfer Learning and Fine-Tuning
11. Model Checkpointing
12. Reproducibility
13. Memory Management
14. Training Large Models
15. Summary

---

## 1. The Complete Training Pipeline

Here is a production-quality training pipeline that incorporates all best practices:

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import time
import os
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


class Trainer:
    """A complete training pipeline for any PyTorch model."""
    
    def __init__(
        self,
        model,
        train_loader,
        val_loader,
        criterion,
        optimizer,
        scheduler=None,
        device="cuda",
        save_dir="checkpoints",
        max_epochs=100,
        patience=10,
        gradient_clip_val=1.0,
        log_interval=100
    ):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.criterion = criterion
        self.optimizer = optimizer
        self.scheduler = scheduler
        self.device = device
        self.save_dir = save_dir
        self.max_epochs = max_epochs
        self.patience = patience
        self.gradient_clip_val = gradient_clip_val
        self.log_interval = log_interval
        
        os.makedirs(save_dir, exist_ok=True)
        
        self.best_val_loss = float("inf")
        self.patience_counter = 0
        self.history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": [], "lr": []}
    
    def train_one_epoch(self, epoch):
        """Train for one epoch."""
        self.model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        start_time = time.time()
        
        for batch_idx, (inputs, targets) in enumerate(self.train_loader):
            inputs = inputs.to(self.device, non_blocking=True)
            targets = targets.to(self.device, non_blocking=True)
            
            # Forward pass
            outputs = self.model(inputs)
            loss = self.criterion(outputs, targets)
            
            # Backward pass
            self.optimizer.zero_grad(set_to_none=True)  # Slightly faster than zero_grad()
            loss.backward()
            
            # Gradient clipping
            if self.gradient_clip_val > 0:
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(), self.gradient_clip_val
                )
            
            # Update
            self.optimizer.step()
            
            # Metrics
            total_loss += loss.item() * inputs.size(0)
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()
            
            # Log progress
            if (batch_idx + 1) % self.log_interval == 0:
                logger.info(
                    f"  Batch {batch_idx+1}/{len(self.train_loader)}, "
                    f"Loss: {loss.item():.4f}"
                )
        
        elapsed = time.time() - start_time
        avg_loss = total_loss / total
        accuracy = correct / total
        
        logger.info(
            f"Epoch {epoch}: Train Loss={avg_loss:.4f}, "
            f"Train Acc={accuracy:.4f}, Time={elapsed:.1f}s"
        )
        
        return avg_loss, accuracy
    
    @torch.no_grad()
    def validate(self, epoch):
        """Validate the model."""
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0
        
        for inputs, targets in self.val_loader:
            inputs = inputs.to(self.device, non_blocking=True)
            targets = targets.to(self.device, non_blocking=True)
            
            outputs = self.model(inputs)
            loss = self.criterion(outputs, targets)
            
            total_loss += loss.item() * inputs.size(0)
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()
        
        avg_loss = total_loss / total
        accuracy = correct / total
        
        logger.info(f"Epoch {epoch}: Val Loss={avg_loss:.4f}, Val Acc={accuracy:.4f}")
        
        return avg_loss, accuracy
    
    def save_checkpoint(self, epoch, is_best=False):
        """Save a training checkpoint."""
        checkpoint = {
            "epoch": epoch,
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "best_val_loss": self.best_val_loss,
            "history": self.history
        }
        if self.scheduler:
            checkpoint["scheduler_state_dict"] = self.scheduler.state_dict()
        
        path = os.path.join(self.save_dir, f"checkpoint_epoch_{epoch}.pt")
        torch.save(checkpoint, path)
        
        if is_best:
            best_path = os.path.join(self.save_dir, "best_model.pt")
            torch.save(checkpoint, best_path)
            logger.info(f"  Saved best model (Val Loss: {self.best_val_loss:.4f})")
    
    def load_checkpoint(self, path):
        """Resume training from a checkpoint."""
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        if self.scheduler and "scheduler_state_dict" in checkpoint:
            self.scheduler.load_state_dict(checkpoint["scheduler_state_dict"])
        self.best_val_loss = checkpoint["best_val_loss"]
        self.history = checkpoint["history"]
        return checkpoint["epoch"]
    
    def train(self):
        """Full training loop."""
        logger.info(f"Starting training for {self.max_epochs} epochs")
        logger.info(f"Model parameters: {sum(p.numel() for p in self.model.parameters()):,}")
        
        for epoch in range(1, self.max_epochs + 1):
            # Train
            train_loss, train_acc = self.train_one_epoch(epoch)
            
            # Validate
            val_loss, val_acc = self.validate(epoch)
            
            # Learning rate scheduling
            current_lr = self.optimizer.param_groups[0]["lr"]
            if self.scheduler:
                if isinstance(self.scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau):
                    self.scheduler.step(val_loss)
                else:
                    self.scheduler.step()
            
            # Record history
            self.history["train_loss"].append(train_loss)
            self.history["val_loss"].append(val_loss)
            self.history["train_acc"].append(train_acc)
            self.history["val_acc"].append(val_acc)
            self.history["lr"].append(current_lr)
            
            # Check for improvement
            if val_loss < self.best_val_loss:
                self.best_val_loss = val_loss
                self.patience_counter = 0
                self.save_checkpoint(epoch, is_best=True)
            else:
                self.patience_counter += 1
                if self.patience_counter >= self.patience:
                    logger.info(f"Early stopping at epoch {epoch}")
                    break
        
        # Save training history
        with open(os.path.join(self.save_dir, "history.json"), "w") as f:
            json.dump(self.history, f, indent=2)
        
        logger.info(f"Training complete. Best Val Loss: {self.best_val_loss:.4f}")
```

---

## 2. GPU Computing with CUDA

GPUs (Graphics Processing Units) are essential for training neural networks. A modern GPU can be 10-100x faster than a CPU for deep learning.

### Why GPUs?

Neural network training involves millions of matrix multiplications. GPUs have thousands of cores optimized for parallel math operations:

- CPU: 8-16 cores, optimized for sequential tasks with complex logic.
- GPU: 5,000-16,000 cores, optimized for parallel math (same operation on many data points).

### Using GPUs in PyTorch

```python
import torch

# Check GPU availability
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU count: {torch.cuda.device_count()}")
if torch.cuda.is_available():
    print(f"GPU name: {torch.cuda.get_device_name(0)}")
    print(f"GPU memory: {torch.cuda.get_device_properties(0).total_mem / 1e9:.1f} GB")

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Move model to GPU
model = model.to(device)

# Move data to GPU (do this in the training loop, per batch)
inputs = inputs.to(device)
targets = targets.to(device)

# Or use non_blocking for async transfers (slightly faster with pin_memory)
inputs = inputs.to(device, non_blocking=True)
```

### GPU Memory Management

GPU memory is limited (typically 8-80 GB). If you run out, you'll get a "CUDA out of memory" error.

```python
# Check GPU memory usage
print(f"Allocated: {torch.cuda.memory_allocated() / 1e9:.2f} GB")
print(f"Cached: {torch.cuda.memory_reserved() / 1e9:.2f} GB")

# Free unused cached memory
torch.cuda.empty_cache()

# Common fixes for out-of-memory:
# 1. Reduce batch size
# 2. Use mixed precision training (FP16 instead of FP32)
# 3. Use gradient accumulation
# 4. Use gradient checkpointing
# 5. Use a smaller model
# 6. Free intermediate tensors with del
```

---

## 3. Mixed Precision Training

Mixed precision uses both 16-bit (FP16) and 32-bit (FP32) floating-point numbers during training. This approximately halves GPU memory usage and can speed up training by 2-3x on modern GPUs.

### How It Works

- Forward pass: Use FP16 (faster, less memory).
- Loss scaling: Scale the loss up to prevent underflow in FP16 gradients.
- Backward pass: Use FP16 for most gradients.
- Parameter update: Use FP32 (to maintain precision).

```python
from torch.amp import autocast, GradScaler

# Create a gradient scaler
scaler = GradScaler("cuda")

for inputs, targets in train_loader:
    inputs = inputs.to(device)
    targets = targets.to(device)
    
    optimizer.zero_grad()
    
    # Forward pass in mixed precision
    with autocast("cuda"):
        outputs = model(inputs)
        loss = criterion(outputs, targets)
    
    # Backward pass with scaled gradients
    scaler.scale(loss).backward()
    
    # Unscale gradients for clipping
    scaler.unscale_(optimizer)
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    
    # Update parameters
    scaler.step(optimizer)
    scaler.update()
```

---

## 4. Gradient Clipping

During training, gradients can sometimes become extremely large ("exploding gradients"), causing the training to diverge. Gradient clipping limits the magnitude of gradients.

### Clip by Norm (Most Common)

Scales the gradient vector so its total norm does not exceed a threshold:

```python
# After loss.backward(), before optimizer.step():
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
```

### Clip by Value

Clips each individual gradient value to a range:

```python
torch.nn.utils.clip_grad_value_(model.parameters(), clip_value=0.5)
```

### When to Use

- Always use gradient clipping for RNNs and transformers.
- Use it when you see NaN losses or exploding loss values.
- A max_norm of 1.0 is a good default.

### Monitoring Gradient Health

```python
def log_gradient_stats(model):
    """Print gradient statistics to detect problems."""
    total_norm = 0
    for name, param in model.named_parameters():
        if param.grad is not None:
            param_norm = param.grad.data.norm(2).item()
            total_norm += param_norm ** 2
            
            if param_norm > 100:
                print(f"  WARNING: Large gradient in {name}: {param_norm:.4f}")
            if param_norm == 0:
                print(f"  WARNING: Zero gradient in {name}")
            if torch.isnan(param.grad).any():
                print(f"  ERROR: NaN gradient in {name}")
    
    total_norm = total_norm ** 0.5
    print(f"  Total gradient norm: {total_norm:.4f}")
```

---

## 5. Learning Rate Scheduling in Practice

### Warmup

Start with a very small learning rate and gradually increase it. This is critical for transformers and large models.

```python
def get_warmup_cosine_scheduler(optimizer, warmup_steps, total_steps):
    """Warmup then cosine decay -- the most common schedule for transformers."""
    
    def lr_lambda(current_step):
        if current_step < warmup_steps:
            # Linear warmup
            return current_step / warmup_steps
        else:
            # Cosine decay
            import math
            progress = (current_step - warmup_steps) / (total_steps - warmup_steps)
            return 0.5 * (1 + math.cos(math.pi * progress))
    
    return torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)

# Usage
total_steps = len(train_loader) * num_epochs
warmup_steps = int(0.1 * total_steps)  # 10% warmup
scheduler = get_warmup_cosine_scheduler(optimizer, warmup_steps, total_steps)

# Call scheduler.step() after EVERY batch, not every epoch
for epoch in range(num_epochs):
    for batch in train_loader:
        # ... training step ...
        scheduler.step()
```

### One Cycle Policy

Increase learning rate for the first half of training, then decrease it. Achieves excellent results quickly.

```python
scheduler = torch.optim.lr_scheduler.OneCycleLR(
    optimizer,
    max_lr=0.01,
    total_steps=len(train_loader) * num_epochs,
    pct_start=0.3,    # 30% of training for warmup
    anneal_strategy="cos"
)
```

### How to Choose a Learning Rate

The learning rate is the most important hyperparameter. Here is a systematic approach:

**Learning Rate Finder** (the Smith method):

```python
def find_learning_rate(model, train_loader, criterion, device, 
                       start_lr=1e-7, end_lr=10, num_steps=100):
    """
    Train for a few batches with exponentially increasing LR.
    Plot loss vs LR and pick the LR where loss decreases fastest.
    """
    import copy
    import matplotlib.pyplot as plt
    
    # Save original model state
    original_state = copy.deepcopy(model.state_dict())
    
    optimizer = torch.optim.SGD(model.parameters(), lr=start_lr)
    
    lr_mult = (end_lr / start_lr) ** (1 / num_steps)
    lrs = []
    losses = []
    
    data_iter = iter(train_loader)
    best_loss = float("inf")
    
    for step in range(num_steps):
        try:
            inputs, targets = next(data_iter)
        except StopIteration:
            data_iter = iter(train_loader)
            inputs, targets = next(data_iter)
        
        inputs, targets = inputs.to(device), targets.to(device)
        
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        
        # Stop if loss diverges
        if loss.item() > 10 * best_loss:
            break
        best_loss = min(best_loss, loss.item())
        
        lrs.append(optimizer.param_groups[0]["lr"])
        losses.append(loss.item())
        
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        
        # Increase LR for next step
        for param_group in optimizer.param_groups:
            param_group["lr"] *= lr_mult
    
    # Restore original model
    model.load_state_dict(original_state)
    
    # Plot
    plt.plot(lrs, losses)
    plt.xscale("log")
    plt.xlabel("Learning Rate")
    plt.ylabel("Loss")
    plt.title("Learning Rate Finder")
    plt.savefig("lr_finder.png")
    
    return lrs, losses
```

**Rules of thumb**:
- Adam optimizer: Start with 1e-3 or 3e-4.
- SGD with momentum: Start with 1e-2 or 1e-1.
- Fine-tuning a pre-trained model: Use 10-100x smaller LR than training from scratch (e.g., 1e-5 to 2e-5).

---

## 6. Data Parallelism and Distributed Training

### Single GPU (DataParallel)

For using multiple GPUs on one machine:

```python
if torch.cuda.device_count() > 1:
    print(f"Using {torch.cuda.device_count()} GPUs")
    model = nn.DataParallel(model)

model = model.to(device)
```

### DistributedDataParallel (DDP)

The preferred method for multi-GPU training. More efficient than DataParallel.

```python
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data.distributed import DistributedSampler

def setup_ddp(rank, world_size):
    """Initialize distributed training."""
    os.environ["MASTER_ADDR"] = "localhost"
    os.environ["MASTER_PORT"] = "12355"
    dist.init_process_group("nccl", rank=rank, world_size=world_size)

def cleanup_ddp():
    """Clean up distributed training."""
    dist.destroy_process_group()

def train_ddp(rank, world_size):
    setup_ddp(rank, world_size)
    
    # Each process gets its own GPU
    device = torch.device(f"cuda:{rank}")
    
    model = MyModel().to(device)
    model = DDP(model, device_ids=[rank])
    
    # Use DistributedSampler to split data across processes
    train_sampler = DistributedSampler(train_dataset, num_replicas=world_size, rank=rank)
    train_loader = DataLoader(train_dataset, batch_size=32, sampler=train_sampler)
    
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()
    
    for epoch in range(num_epochs):
        train_sampler.set_epoch(epoch)  # Important for proper shuffling
        
        for inputs, targets in train_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
    
    cleanup_ddp()

# Launch with:
# world_size = torch.cuda.device_count()
# torch.multiprocessing.spawn(train_ddp, args=(world_size,), nprocs=world_size)
```

### Gradient Accumulation

When your batch size is limited by GPU memory, you can simulate larger batch sizes by accumulating gradients over multiple forward passes:

```python
accumulation_steps = 4  # Effective batch_size = actual_batch_size * 4

optimizer.zero_grad()
for i, (inputs, targets) in enumerate(train_loader):
    inputs, targets = inputs.to(device), targets.to(device)
    
    outputs = model(inputs)
    loss = criterion(outputs, targets)
    loss = loss / accumulation_steps  # Scale loss
    loss.backward()
    
    if (i + 1) % accumulation_steps == 0:
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        optimizer.zero_grad()
```

---

## 7. Logging and Monitoring with TensorBoard and Weights & Biases

### TensorBoard

```python
from torch.utils.tensorboard import SummaryWriter

writer = SummaryWriter("runs/experiment_1")

for epoch in range(num_epochs):
    train_loss, train_acc = train_one_epoch(model, train_loader, ...)
    val_loss, val_acc = validate(model, val_loader, ...)
    
    # Log scalars
    writer.add_scalar("Loss/train", train_loss, epoch)
    writer.add_scalar("Loss/val", val_loss, epoch)
    writer.add_scalar("Accuracy/train", train_acc, epoch)
    writer.add_scalar("Accuracy/val", val_acc, epoch)
    writer.add_scalar("LR", optimizer.param_groups[0]["lr"], epoch)
    
    # Log histograms of weights and gradients
    for name, param in model.named_parameters():
        writer.add_histogram(f"weights/{name}", param, epoch)
        if param.grad is not None:
            writer.add_histogram(f"gradients/{name}", param.grad, epoch)

writer.close()

# View in browser: tensorboard --logdir=runs
```

### Weights & Biases (wandb)

```python
import wandb

# Initialize
wandb.init(
    project="my-ai-project",
    name="experiment-1",
    config={
        "learning_rate": 0.001,
        "batch_size": 32,
        "epochs": 100,
        "model": "ResNet-18",
        "optimizer": "AdamW"
    }
)

for epoch in range(num_epochs):
    train_loss, train_acc = train_one_epoch(...)
    val_loss, val_acc = validate(...)
    
    wandb.log({
        "train_loss": train_loss,
        "val_loss": val_loss,
        "train_acc": train_acc,
        "val_acc": val_acc,
        "lr": optimizer.param_groups[0]["lr"],
        "epoch": epoch
    })

# Log model
wandb.save("best_model.pt")
wandb.finish()
```

---

## 8. Debugging Neural Networks

### Systematic Debugging Checklist

When your model is not training well, work through this checklist:

**1. Verify data**:
```python
# Check a batch
batch = next(iter(train_loader))
inputs, targets = batch
print(f"Input shape: {inputs.shape}")
print(f"Input range: [{inputs.min():.4f}, {inputs.max():.4f}]")
print(f"Target shape: {targets.shape}")
print(f"Target values: {targets.unique()}")
print(f"Any NaN in inputs: {torch.isnan(inputs).any()}")
```

**2. Verify model output shape**:
```python
# Check output shape matches expectations
with torch.no_grad():
    output = model(inputs[:1].to(device))
    print(f"Output shape: {output.shape}")
    print(f"Output range: [{output.min():.4f}, {output.max():.4f}]")
    print(f"Any NaN in output: {torch.isnan(output).any()}")
```

**3. Overfit on a single batch**:
```python
# If the model cannot overfit 1 batch, there is a bug
model.train()
single_batch = next(iter(train_loader))
inputs, targets = single_batch[0].to(device), single_batch[1].to(device)

optimizer = optim.Adam(model.parameters(), lr=0.001)
for step in range(1000):
    outputs = model(inputs)
    loss = criterion(outputs, targets)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    
    if step % 100 == 0:
        _, pred = outputs.max(1)
        acc = pred.eq(targets).float().mean()
        print(f"Step {step}: Loss={loss.item():.4f}, Acc={acc.item():.4f}")

# Loss should go to ~0 and accuracy to ~1
# If not: model is too small, LR is wrong, or there is a bug
```

**4. Check gradient flow**:
```python
def check_gradient_flow(model):
    """Verify that gradients are flowing to all layers."""
    for name, param in model.named_parameters():
        if param.requires_grad:
            if param.grad is None:
                print(f"  NO GRADIENT: {name}")
            elif param.grad.abs().max() == 0:
                print(f"  ZERO GRADIENT: {name}")
            else:
                print(f"  OK: {name} (grad norm: {param.grad.norm():.6f})")
```

### Common Bugs

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Loss is NaN | Learning rate too high, or numerical overflow | Reduce LR, add gradient clipping, check for division by zero |
| Loss does not decrease | LR too low, model too small, or bug in data/labels | Increase LR, increase model size, verify data pipeline |
| Loss decreases then explodes | LR too high | Reduce LR, add LR scheduling |
| Training loss low, val loss high | Overfitting | Add dropout, data augmentation, reduce model size, add weight decay |
| Both losses high | Underfitting | Increase model size, train longer, increase LR, add features |
| Loss stays constant | Dead ReLUs, or optimizer not attached to model | Check activations, verify optimizer has model.parameters() |
| Accuracy stuck at random | Labels might be shuffled relative to inputs | Verify data pipeline, check a few samples manually |

---

## 9. Common Training Problems and Solutions

### Vanishing Gradients

**Problem**: Gradients become very small in early layers, so they barely learn.
**Solutions**:
- Use ReLU activation instead of sigmoid/tanh.
- Use batch normalization.
- Use skip connections (residual connections).
- Use proper weight initialization (He init for ReLU).

### Exploding Gradients

**Problem**: Gradients become very large, causing unstable updates.
**Solutions**:
- Gradient clipping.
- Lower learning rate.
- Batch normalization.
- Proper weight initialization.

### Dying ReLU

**Problem**: Some neurons always output 0 and never recover.
**Solutions**:
- Use Leaky ReLU, PReLU, or ELU instead.
- Lower learning rate.
- Use batch normalization before ReLU.

### Overfitting

**Problem**: Model memorizes training data, fails on new data.
**Solutions**:
- More training data.
- Data augmentation.
- Dropout.
- Weight decay (L2 regularization).
- Reduce model complexity.
- Early stopping.

### Underfitting

**Problem**: Model too simple to capture patterns.
**Solutions**:
- Larger model (more layers, more neurons).
- Train for more epochs.
- Higher learning rate (initially).
- Better features.
- Reduce regularization (less dropout, less weight decay).

---

## 10. Transfer Learning and Fine-Tuning

Transfer learning uses a model pre-trained on a large dataset as a starting point. This is one of the most powerful techniques in deep learning -- instead of starting from random weights, you start from weights that already understand general patterns.

### Why Transfer Learning Works

A model trained on ImageNet (14 million images) learns general visual features:
- Layer 1: Edges, corners, simple textures.
- Layer 2: More complex textures, patterns.
- Layer 3: Parts of objects.
- Layer 4+: Full objects and concepts.

These features are useful for nearly any vision task, even if your task is completely different from ImageNet.

### Feature Extraction

Freeze the pre-trained layers and only train a new output head:

```python
import torchvision.models as models

# Load a pre-trained model
model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)

# Freeze all layers
for param in model.parameters():
    param.requires_grad = False

# Replace the final classification layer
num_classes = 5  # Your number of classes
model.fc = nn.Linear(model.fc.in_features, num_classes)
# Only model.fc parameters will be trained

optimizer = optim.Adam(model.fc.parameters(), lr=0.001)
```

### Fine-Tuning

Unfreeze some or all pre-trained layers and train with a small learning rate:

```python
# Load pre-trained model
model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)

# Replace final layer
model.fc = nn.Linear(model.fc.in_features, num_classes)

# Use different learning rates for different parts
# Lower LR for pre-trained layers, higher LR for new layers
optimizer = optim.Adam([
    {"params": model.conv1.parameters(), "lr": 1e-5},
    {"params": model.bn1.parameters(), "lr": 1e-5},
    {"params": model.layer1.parameters(), "lr": 1e-5},
    {"params": model.layer2.parameters(), "lr": 1e-4},
    {"params": model.layer3.parameters(), "lr": 1e-4},
    {"params": model.layer4.parameters(), "lr": 1e-3},
    {"params": model.fc.parameters(), "lr": 1e-2}
])
```

### Gradual Unfreezing

Start by training only the new layers, then gradually unfreeze earlier layers:

```python
# Phase 1: Train only the new head (5 epochs)
for param in model.parameters():
    param.requires_grad = False
model.fc.requires_grad_(True)
train(model, epochs=5)

# Phase 2: Unfreeze last block (5 epochs)
model.layer4.requires_grad_(True)
train(model, epochs=5)

# Phase 3: Unfreeze everything (10 epochs with small LR)
model.requires_grad_(True)
train(model, epochs=10)
```

---

## 11. Model Checkpointing

Always save checkpoints during training. Training can crash, GPUs can fail, and experiments can take days or weeks.

```python
class CheckpointManager:
    """Manages model checkpoints with rotation."""
    
    def __init__(self, save_dir, max_checkpoints=5):
        self.save_dir = save_dir
        self.max_checkpoints = max_checkpoints
        self.checkpoints = []
        os.makedirs(save_dir, exist_ok=True)
    
    def save(self, model, optimizer, epoch, val_loss, scheduler=None):
        """Save a checkpoint and rotate old ones."""
        checkpoint = {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "val_loss": val_loss
        }
        if scheduler:
            checkpoint["scheduler_state_dict"] = scheduler.state_dict()
        
        path = os.path.join(self.save_dir, f"checkpoint_{epoch:04d}.pt")
        torch.save(checkpoint, path)
        self.checkpoints.append(path)
        
        # Remove old checkpoints
        while len(self.checkpoints) > self.max_checkpoints:
            old_path = self.checkpoints.pop(0)
            if os.path.exists(old_path):
                os.remove(old_path)
    
    def load_latest(self):
        """Load the most recent checkpoint."""
        checkpoints = sorted(
            [f for f in os.listdir(self.save_dir) if f.startswith("checkpoint_")],
            reverse=True
        )
        if checkpoints:
            path = os.path.join(self.save_dir, checkpoints[0])
            return torch.load(path)
        return None
```

---

## 12. Reproducibility

Making experiments reproducible is essential for scientific rigor and debugging.

```python
import torch
import numpy as np
import random

def set_seed(seed=42):
    """Set all random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)  # For multi-GPU
    
    # These improve reproducibility but may reduce performance
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

set_seed(42)

# Also set worker seeds for DataLoader
def worker_init_fn(worker_id):
    np.random.seed(42 + worker_id)

train_loader = DataLoader(
    dataset,
    batch_size=32,
    shuffle=True,
    num_workers=4,
    worker_init_fn=worker_init_fn,
    generator=torch.Generator().manual_seed(42)
)
```

---

## 13. Memory Management

### Reducing GPU Memory Usage

```python
# 1. Use mixed precision (halves memory for activations)
from torch.amp import autocast
with autocast("cuda"):
    output = model(input)

# 2. Use gradient checkpointing (trades compute for memory)
from torch.utils.checkpoint import checkpoint

class MemoryEfficientModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.blocks = nn.ModuleList([Block() for _ in range(50)])
    
    def forward(self, x):
        for block in self.blocks:
            # Instead of storing activations, recompute them during backward
            x = checkpoint(block, x, use_reentrant=False)
        return x

# 3. Clear cache
torch.cuda.empty_cache()

# 4. Delete intermediate tensors
del intermediate_tensor

# 5. Use torch.no_grad() for inference
with torch.no_grad():
    output = model(input)

# 6. Use smaller data types
# float32 (4 bytes) -> float16 (2 bytes) -> bfloat16 (2 bytes)
tensor_fp16 = tensor.half()
tensor_bf16 = tensor.bfloat16()
```

### Profiling Memory Usage

```python
# Profile memory usage
print(f"GPU memory allocated: {torch.cuda.memory_allocated() / 1e9:.2f} GB")
print(f"GPU memory reserved: {torch.cuda.memory_reserved() / 1e9:.2f} GB")

# Detailed memory snapshot
print(torch.cuda.memory_summary())
```

---

## 14. Training Large Models

For models that do not fit on a single GPU, you need specialized techniques.

### Model Parallelism

Split different layers of the model across different GPUs:

```python
class ModelParallel(nn.Module):
    """Split model across two GPUs."""
    
    def __init__(self):
        super().__init__()
        # First half on GPU 0
        self.layer1 = nn.Linear(1000, 500).to("cuda:0")
        self.layer2 = nn.Linear(500, 500).to("cuda:0")
        # Second half on GPU 1
        self.layer3 = nn.Linear(500, 500).to("cuda:1")
        self.layer4 = nn.Linear(500, 10).to("cuda:1")
    
    def forward(self, x):
        x = x.to("cuda:0")
        x = torch.relu(self.layer1(x))
        x = torch.relu(self.layer2(x))
        x = x.to("cuda:1")  # Transfer between GPUs
        x = torch.relu(self.layer3(x))
        x = self.layer4(x)
        return x
```

### FSDP (Fully Sharded Data Parallel)

Shards model parameters, gradients, and optimizer state across GPUs. Allows training models much larger than a single GPU's memory.

```python
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP

model = FSDP(model)
```

### DeepSpeed

A library from Microsoft for extremely large-scale training:

```python
import deepspeed

model_engine, optimizer, _, _ = deepspeed.initialize(
    model=model,
    model_parameters=model.parameters(),
    config={
        "train_batch_size": 256,
        "fp16": {"enabled": True},
        "zero_optimization": {"stage": 2}
    }
)

for inputs, targets in train_loader:
    outputs = model_engine(inputs)
    loss = criterion(outputs, targets)
    model_engine.backward(loss)
    model_engine.step()
```

---

## 15. Summary

You now know how to train neural networks effectively:

1. **Complete training pipeline**: Model, data, loss, optimizer, train loop, validation, checkpointing.
2. **GPU computing**: Moving models and data to GPU, managing memory.
3. **Mixed precision**: Using FP16 for faster, more memory-efficient training.
4. **Gradient clipping**: Preventing exploding gradients.
5. **Learning rate scheduling**: Warmup, cosine decay, one-cycle, LR finding.
6. **Distributed training**: DataParallel, DDP, gradient accumulation.
7. **Monitoring**: TensorBoard, Weights & Biases.
8. **Debugging**: Systematic checklist, overfit single batch, check gradients.
9. **Common problems**: Vanishing/exploding gradients, dying ReLU, over/underfitting.
10. **Transfer learning**: Feature extraction, fine-tuning, gradual unfreezing.
11. **Checkpointing**: Saving and resuming training.
12. **Reproducibility**: Setting random seeds.
13. **Memory management**: Mixed precision, gradient checkpointing, profiling.
14. **Large-scale training**: Model parallelism, FSDP, DeepSpeed.

---

[<< Previous: Chapter 5 - Neural Networks](./05_NEURAL_NETWORKS.md) | [Next: Chapter 7 - Convolutional Neural Networks >>](./07_CNN.md)
