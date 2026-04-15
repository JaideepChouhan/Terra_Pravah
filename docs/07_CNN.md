# Chapter 7: Convolutional Neural Networks (CNNs) -- Computer Vision

## Introduction

Convolutional Neural Networks are the backbone of computer vision. They are designed to process data that has a spatial structure -- images (2D grids of pixels), audio spectrograms (2D time-frequency grids), video (3D: time plus 2D frames), and even 3D volumes. This chapter covers how CNNs work, how to build them, and the landmark architectures that have defined the field.

---

## Table of Contents

1. Why CNNs? The Problem with Fully Connected Networks for Images
2. Convolution -- The Core Operation
3. Padding, Stride, and Dilation
4. Pooling Layers
5. CNN Architecture: Putting It All Together
6. Building a CNN from Scratch
7. Building a CNN in PyTorch
8. Landmark Architectures
9. Object Detection
10. Image Segmentation
11. Practical Computer Vision Pipeline
12. Summary

---

## 1. Why CNNs? The Problem with Fully Connected Networks for Images

A 224x224 RGB image has 224 x 224 x 3 = 150,528 input values. If the first hidden layer has 1,000 neurons, you need 150,528 x 1,000 = 150 million parameters in just the first layer. This is:

- **Computationally wasteful**: Most of these parameters are unnecessary.
- **Prone to overfitting**: Too many parameters for the amount of data.
- **Ignores spatial structure**: A pixel at position (10, 10) is treated the same as a pixel at (200, 200), even though nearby pixels are strongly related.

CNNs solve all three problems using two key ideas:

1. **Local connectivity (receptive fields)**: Each neuron only looks at a small patch of the input, not the entire image.
2. **Weight sharing**: The same small set of weights (a "filter" or "kernel") is applied to every patch of the image.

---

## 2. Convolution -- The Core Operation

### What Convolution Does

Imagine a small window (e.g., 3x3 pixels) sliding across the image. At each position, the window's values are multiplied element-wise with a set of learned weights (the kernel), and the results are summed to produce a single output value.

### 1D Convolution (for sequences)

```
Input:   [1, 2, 3, 4, 5, 6, 7]
Kernel:  [1, 0, -1]

Step 1: [1, 2, 3] * [1, 0, -1] = 1*1 + 2*0 + 3*(-1) = -2
Step 2: [2, 3, 4] * [1, 0, -1] = 2*1 + 3*0 + 4*(-1) = -2
Step 3: [3, 4, 5] * [1, 0, -1] = 3*1 + 4*0 + 5*(-1) = -2
Step 4: [4, 5, 6] * [1, 0, -1] = 4*1 + 5*0 + 6*(-1) = -2
Step 5: [5, 6, 7] * [1, 0, -1] = 5*1 + 6*0 + 7*(-1) = -2

Output:  [-2, -2, -2, -2, -2]
```

This particular kernel computes the difference between the left and right neighbors -- it is a simple edge detector.

### 2D Convolution (for images)

```python
import numpy as np

def convolve2d(image, kernel):
    """Apply 2D convolution to a single-channel image."""
    kh, kw = kernel.shape
    ih, iw = image.shape
    
    # Output dimensions
    oh = ih - kh + 1
    ow = iw - kw + 1
    
    output = np.zeros((oh, ow))
    
    for i in range(oh):
        for j in range(ow):
            # Extract the patch
            patch = image[i:i+kh, j:j+kw]
            # Element-wise multiply and sum
            output[i, j] = np.sum(patch * kernel)
    
    return output

# Example: Edge detection
image = np.array([
    [0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0],
    [0, 1, 1, 1, 0],
    [0, 1, 1, 1, 0],
    [0, 0, 0, 0, 0]
], dtype=np.float32)

# Horizontal edge detection kernel
kernel = np.array([
    [-1, -1, -1],
    [ 0,  0,  0],
    [ 1,  1,  1]
], dtype=np.float32)

result = convolve2d(image, kernel)
print(result)
# Shows edges at the top and bottom of the square
```

### Multiple Channels and Multiple Filters

Real images have 3 channels (RGB). A convolution layer has multiple filters, each producing one output channel.

```
Input:  (3 channels, H, W)      -- e.g., RGB image
Filter: (3 input channels, kH, kW)  -- one filter processes all 3 channels
        The filter has 3 x kH x kW weights + 1 bias

N filters produce N output channels:
Output: (N channels, H', W')

So a Conv2d layer with:
  - 3 input channels
  - 64 output channels (64 filters)
  - 3x3 kernel size
Has parameters: 64 * (3 * 3 * 3 + 1) = 64 * 28 = 1,792    (much less than a fully connected layer!)
```

### What Filters Learn

In a trained CNN:
- **Early layers** (close to input): Learn simple patterns -- edges, corners, color gradients.
- **Middle layers**: Learn textures, patterns, parts of objects.
- **Deep layers** (close to output): Learn high-level concepts -- whole objects, faces, scenes.

This hierarchy of features is what makes CNNs so powerful.

---

## 3. Padding, Stride, and Dilation

### Padding

Without padding, the output is smaller than the input (by kernel_size - 1 in each dimension). Padding adds extra values (usually zeros) around the border of the input.

```python
# "same" padding: output size = input size
conv = nn.Conv2d(3, 64, kernel_size=3, padding=1)
# Input: (batch, 3, 32, 32) -> Output: (batch, 64, 32, 32)

# "valid" padding (no padding): output shrinks
conv = nn.Conv2d(3, 64, kernel_size=3, padding=0)
# Input: (batch, 3, 32, 32) -> Output: (batch, 64, 30, 30)
```

### Stride

Stride controls how many pixels the filter moves between positions. Stride > 1 reduces the spatial dimensions.

```python
# Stride 2: output is half the size in each dimension
conv = nn.Conv2d(3, 64, kernel_size=3, stride=2, padding=1)
# Input: (batch, 3, 32, 32) -> Output: (batch, 64, 16, 16)
```

### Dilation

Dilation inserts gaps between kernel elements, allowing the filter to see a larger area without more parameters.

```python
# Dilation 2: kernel covers a 5x5 area but only has 3x3 weights
conv = nn.Conv2d(3, 64, kernel_size=3, dilation=2, padding=2)
```

### Output Size Formula

$$H_{out} = \left\lfloor \frac{H_{in} + 2 \times \text{padding} - \text{dilation} \times (\text{kernel\_size} - 1) - 1}{\text{stride}} + 1 \right\rfloor$$

---

## 4. Pooling Layers

Pooling reduces the spatial dimensions of feature maps, making the representation more compact and adding translational invariance.

### Max Pooling

Take the maximum value in each local window:

```python
pool = nn.MaxPool2d(kernel_size=2, stride=2)
# Input: (batch, channels, 32, 32) -> Output: (batch, channels, 16, 16)
# Each 2x2 region is replaced by its maximum value
```

### Average Pooling

Take the average value in each local window:

```python
pool = nn.AvgPool2d(kernel_size=2, stride=2)
```

### Global Average Pooling

Take the average across the entire spatial dimension. Reduces (batch, channels, H, W) to (batch, channels, 1, 1). Used as a replacement for fully connected layers at the end of a CNN.

```python
pool = nn.AdaptiveAvgPool2d(output_size=(1, 1))
# Input: (batch, 512, 7, 7) -> Output: (batch, 512, 1, 1)
```

---

## 5. CNN Architecture: Putting It All Together

A typical CNN alternates between convolutional layers (feature extraction) and pooling layers (downsampling), ending with fully connected layers (classification).

```
Input Image (3, 224, 224)
    |
    v
Conv2d(3 -> 64, 3x3) + BatchNorm + ReLU     -> (64, 224, 224)
Conv2d(64 -> 64, 3x3) + BatchNorm + ReLU     -> (64, 224, 224)
MaxPool2d(2x2)                                 -> (64, 112, 112)
    |
    v
Conv2d(64 -> 128, 3x3) + BatchNorm + ReLU    -> (128, 112, 112)
Conv2d(128 -> 128, 3x3) + BatchNorm + ReLU   -> (128, 112, 112)
MaxPool2d(2x2)                                 -> (128, 56, 56)
    |
    v
Conv2d(128 -> 256, 3x3) + BatchNorm + ReLU   -> (256, 56, 56)
Conv2d(256 -> 256, 3x3) + BatchNorm + ReLU   -> (256, 56, 56)
MaxPool2d(2x2)                                 -> (256, 28, 28)
    |
    v
AdaptiveAvgPool2d(1x1)                        -> (256, 1, 1)
Flatten                                         -> (256,)
Linear(256 -> num_classes)                      -> (num_classes,)
```

---

## 6. Building a CNN from Scratch

```python
import numpy as np

class Conv2D:
    """2D Convolution layer implemented from scratch."""
    
    def __init__(self, in_channels, out_channels, kernel_size, stride=1, padding=0):
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding
        
        # He initialization
        scale = np.sqrt(2.0 / (in_channels * kernel_size * kernel_size))
        self.weights = np.random.randn(
            out_channels, in_channels, kernel_size, kernel_size
        ) * scale
        self.biases = np.zeros(out_channels)
    
    def forward(self, x):
        """
        Forward pass.
        
        Args:
            x: Input tensor, shape (batch, in_channels, H, W)
        
        Returns:
            Output tensor, shape (batch, out_channels, H_out, W_out)
        """
        batch_size, _, H, W = x.shape
        
        # Add padding
        if self.padding > 0:
            x = np.pad(x, ((0, 0), (0, 0), 
                           (self.padding, self.padding), 
                           (self.padding, self.padding)))
        
        # Calculate output dimensions
        H_out = (H + 2 * self.padding - self.kernel_size) // self.stride + 1
        W_out = (W + 2 * self.padding - self.kernel_size) // self.stride + 1
        
        output = np.zeros((batch_size, self.out_channels, H_out, W_out))
        
        for b in range(batch_size):
            for f in range(self.out_channels):
                for i in range(H_out):
                    for j in range(W_out):
                        h_start = i * self.stride
                        h_end = h_start + self.kernel_size
                        w_start = j * self.stride
                        w_end = w_start + self.kernel_size
                        
                        patch = x[b, :, h_start:h_end, w_start:w_end]
                        output[b, f, i, j] = np.sum(patch * self.weights[f]) + self.biases[f]
        
        self.input_cache = x  # Save for backprop
        return output


class MaxPool2D:
    """Max pooling layer."""
    
    def __init__(self, kernel_size=2, stride=2):
        self.kernel_size = kernel_size
        self.stride = stride
    
    def forward(self, x):
        batch_size, channels, H, W = x.shape
        H_out = H // self.stride
        W_out = W // self.stride
        
        output = np.zeros((batch_size, channels, H_out, W_out))
        
        for b in range(batch_size):
            for c in range(channels):
                for i in range(H_out):
                    for j in range(W_out):
                        h_start = i * self.stride
                        h_end = h_start + self.kernel_size
                        w_start = j * self.stride
                        w_end = w_start + self.kernel_size
                        
                        output[b, c, i, j] = np.max(x[b, c, h_start:h_end, w_start:w_end])
        
        return output
```

---

## 7. Building a CNN in PyTorch

```python
import torch
import torch.nn as nn

class CNN(nn.Module):
    """A complete CNN for image classification."""
    
    def __init__(self, num_classes=10):
        super().__init__()
        
        # Feature extraction layers
        self.features = nn.Sequential(
            # Block 1
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.Conv2d(32, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout2d(0.25),
            
            # Block 2
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout2d(0.25),
            
            # Block 3
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout2d(0.25),
        )
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(128, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x


# Complete training example with CIFAR-10
import torchvision
import torchvision.transforms as T

# Data transforms
train_transform = T.Compose([
    T.RandomCrop(32, padding=4),
    T.RandomHorizontalFlip(),
    T.ToTensor(),
    T.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616))
])

test_transform = T.Compose([
    T.ToTensor(),
    T.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616))
])

# Load CIFAR-10
train_dataset = torchvision.datasets.CIFAR10(
    root="./data", train=True, download=True, transform=train_transform
)
test_dataset = torchvision.datasets.CIFAR10(
    root="./data", train=False, download=True, transform=test_transform
)

train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=128, shuffle=True, num_workers=4)
test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=256, shuffle=False, num_workers=4)

# Create model and train
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = CNN(num_classes=10).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=100)

# Training loop (see Chapter 6 for the full training pipeline)
```

---

## 8. Landmark Architectures

### LeNet-5 (1998)

The original CNN, designed by Yann LeCun for handwritten digit recognition. Simple but revolutionary.

### AlexNet (2012)

The model that triggered the deep learning revolution. Won ImageNet by a large margin using two GPUs and ReLU activations.

### VGG (2014)

Showed that very deep networks with small (3x3) filters work better than shallow networks with large filters. VGG-16 has 16 layers.

### GoogLeNet / Inception (2014)

Used "inception modules" that apply multiple filter sizes (1x1, 3x3, 5x5) in parallel and concatenate the results.

### ResNet (2015)

Introduced skip connections, enabling training of networks with 152+ layers. This solved the degradation problem (deeper networks performing worse).

```python
class ResidualBlock(nn.Module):
    """A residual block as used in ResNet."""
    
    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()
        
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, 
                               stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, 
                               padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        
        # Skip connection: if dimensions change, use 1x1 conv to match
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1, 
                         stride=stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )
    
    def forward(self, x):
        identity = self.shortcut(x)
        
        out = torch.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        
        out += identity  # Skip connection
        out = torch.relu(out)
        
        return out


class ResNet(nn.Module):
    """A simplified ResNet."""
    
    def __init__(self, block, num_blocks, num_classes=10):
        super().__init__()
        self.in_channels = 64
        
        self.conv1 = nn.Conv2d(3, 64, kernel_size=3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.layer1 = self._make_layer(block, 64, num_blocks[0], stride=1)
        self.layer2 = self._make_layer(block, 128, num_blocks[1], stride=2)
        self.layer3 = self._make_layer(block, 256, num_blocks[2], stride=2)
        self.layer4 = self._make_layer(block, 512, num_blocks[3], stride=2)
        self.avg_pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512, num_classes)
    
    def _make_layer(self, block, out_channels, num_blocks, stride):
        layers = [block(self.in_channels, out_channels, stride)]
        self.in_channels = out_channels
        for _ in range(1, num_blocks):
            layers.append(block(out_channels, out_channels))
        return nn.Sequential(*layers)
    
    def forward(self, x):
        x = torch.relu(self.bn1(self.conv1(x)))
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.avg_pool(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x

def ResNet18(num_classes=10):
    return ResNet(ResidualBlock, [2, 2, 2, 2], num_classes)
```

### EfficientNet (2019)

Systematically scales network width, depth, and resolution together using a compound scaling method. Very parameter-efficient.

### Vision Transformer (ViT) (2020)

Applies the transformer architecture (originally designed for text) directly to images by splitting them into patches. Achieves state-of-the-art results with enough data.

### ConvNeXt (2022)

Modernized ConvNets to compete with Vision Transformers by adopting transformer design principles (larger kernels, fewer activations, layer norm, etc.).

---

## 9. Object Detection

Object detection not only classifies objects in an image but also draws bounding boxes around them.

### Key Concepts

- **Bounding box**: A rectangle defined by (x, y, width, height) or (x1, y1, x2, y2) that surrounds an object.
- **IoU (Intersection over Union)**: Measures overlap between predicted and ground-truth boxes. IoU > 0.5 is typically considered a correct detection.
- **Non-Maximum Suppression (NMS)**: When multiple boxes detect the same object, keep only the one with the highest confidence.
- **Anchor boxes**: Pre-defined boxes at various sizes and aspect ratios used as starting points for predictions.

### YOLO (You Only Look Once)

YOLO divides the image into a grid and predicts bounding boxes and class probabilities for each grid cell in a single forward pass.

```python
# Using a pre-trained YOLO model
import torchvision

model = torchvision.models.detection.fasterrcnn_resnet50_fpn(
    weights=torchvision.models.detection.FasterRCNN_ResNet50_FPN_Weights.DEFAULT
)
model.eval()

# Run detection
from PIL import Image
import torchvision.transforms as T

img = Image.open("photo.jpg")
transform = T.ToTensor()
img_tensor = transform(img).unsqueeze(0)

with torch.no_grad():
    predictions = model(img_tensor)

# predictions[0] contains:
# - "boxes": Tensor of (N, 4) bounding boxes
# - "labels": Tensor of (N,) class labels
# - "scores": Tensor of (N,) confidence scores

for box, label, score in zip(predictions[0]["boxes"], 
                              predictions[0]["labels"], 
                              predictions[0]["scores"]):
    if score > 0.5:
        print(f"Class {label.item()}, Score {score.item():.2f}, Box {box.tolist()}")
```

---

## 10. Image Segmentation

Image segmentation assigns a class label to every pixel in the image.

### Semantic Segmentation

Every pixel gets a class label. Does not distinguish between different instances of the same class.

### Instance Segmentation

Distinguishes between different instances. Each individual object gets its own mask.

### U-Net Architecture

The most popular architecture for segmentation. It has an encoder (downsampling) path and a decoder (upsampling) path with skip connections between them.

```python
class UNet(nn.Module):
    """Simplified U-Net for image segmentation."""
    
    def __init__(self, in_channels=3, num_classes=2):
        super().__init__()
        
        # Encoder (downsampling)
        self.enc1 = self._double_conv(in_channels, 64)
        self.enc2 = self._double_conv(64, 128)
        self.enc3 = self._double_conv(128, 256)
        self.enc4 = self._double_conv(256, 512)
        
        # Bottleneck
        self.bottleneck = self._double_conv(512, 1024)
        
        # Decoder (upsampling)
        self.up4 = nn.ConvTranspose2d(1024, 512, kernel_size=2, stride=2)
        self.dec4 = self._double_conv(1024, 512)  # 1024 because of skip connection
        
        self.up3 = nn.ConvTranspose2d(512, 256, kernel_size=2, stride=2)
        self.dec3 = self._double_conv(512, 256)
        
        self.up2 = nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2)
        self.dec2 = self._double_conv(256, 128)
        
        self.up1 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2)
        self.dec1 = self._double_conv(128, 64)
        
        # Output
        self.out_conv = nn.Conv2d(64, num_classes, kernel_size=1)
        
        self.pool = nn.MaxPool2d(2)
    
    def _double_conv(self, in_ch, out_ch):
        return nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True)
        )
    
    def forward(self, x):
        # Encoder
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool(e1))
        e3 = self.enc3(self.pool(e2))
        e4 = self.enc4(self.pool(e3))
        
        # Bottleneck
        b = self.bottleneck(self.pool(e4))
        
        # Decoder with skip connections
        d4 = self.dec4(torch.cat([self.up4(b), e4], dim=1))
        d3 = self.dec3(torch.cat([self.up3(d4), e3], dim=1))
        d2 = self.dec2(torch.cat([self.up2(d3), e2], dim=1))
        d1 = self.dec1(torch.cat([self.up1(d2), e1], dim=1))
        
        return self.out_conv(d1)
```

---

## 11. Practical Computer Vision Pipeline

```python
import torch
import torchvision.models as models
import torchvision.transforms as T
from PIL import Image

def create_image_classifier(num_classes, pretrained=True):
    """Create a production-ready image classifier using transfer learning."""
    
    # Use a pre-trained EfficientNet
    if pretrained:
        weights = models.EfficientNet_B0_Weights.IMAGENET1K_V1
        model = models.efficientnet_b0(weights=weights)
    else:
        model = models.efficientnet_b0()
    
    # Replace classifier
    model.classifier = nn.Sequential(
        nn.Dropout(0.2),
        nn.Linear(model.classifier[1].in_features, num_classes)
    )
    
    return model

# Transforms
train_transforms = T.Compose([
    T.RandomResizedCrop(224),
    T.RandomHorizontalFlip(),
    T.RandAugment(num_ops=2, magnitude=9),
    T.ToTensor(),
    T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

val_transforms = T.Compose([
    T.Resize(256),
    T.CenterCrop(224),
    T.ToTensor(),
    T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Inference function
def predict_image(model, image_path, transform, class_names, device="cuda"):
    """Predict the class of a single image."""
    model.eval()
    
    img = Image.open(image_path).convert("RGB")
    tensor = transform(img).unsqueeze(0).to(device)
    
    with torch.no_grad():
        output = model(tensor)
        probabilities = torch.softmax(output, dim=1)
        confidence, predicted = probabilities.max(1)
    
    return {
        "class": class_names[predicted.item()],
        "confidence": confidence.item(),
        "all_probabilities": {
            name: prob.item() 
            for name, prob in zip(class_names, probabilities[0])
        }
    }
```

---

## 12. Summary

You now understand computer vision with CNNs:

1. **Why CNNs**: Local connectivity and weight sharing solve the problems of using fully connected networks for images.
2. **Convolution**: Sliding filters that detect patterns at every location.
3. **Padding, stride, dilation**: Controlling output size and receptive field.
4. **Pooling**: Reducing spatial dimensions and adding invariance.
5. **CNN architecture**: Stacking conv blocks with increasing channels and decreasing spatial size.
6. **From-scratch implementation**: Understanding every computation.
7. **PyTorch implementation**: Building professional CNNs.
8. **Landmark architectures**: LeNet, AlexNet, VGG, ResNet, EfficientNet, ViT.
9. **Object detection**: YOLO, Faster R-CNN, bounding boxes, IoU, NMS.
10. **Image segmentation**: U-Net, semantic vs instance segmentation.
11. **Practical pipeline**: Transfer learning, data augmentation, inference.

---

[<< Previous: Chapter 6 - Training Deep Networks](./06_TRAINING_DEEP_NETWORKS.md) | [Next: Chapter 8 - Sequence Models & NLP >>](./08_SEQUENCE_MODELS_NLP.md)
