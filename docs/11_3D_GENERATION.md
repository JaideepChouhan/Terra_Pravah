# Chapter 11: 3D Generation and Neural Rendering

## Table of Contents

1. [What is 3D Generation?](#1-what-is-3d-generation)
2. [3D Representations](#2-3d-representations)
3. [Classical 3D Reconstruction](#3-classical-3d-reconstruction)
4. [Neural Radiance Fields (NeRF)](#4-neural-radiance-fields-nerf)
5. [3D Gaussian Splatting](#5-3d-gaussian-splatting)
6. [Mesh Generation with Neural Networks](#6-mesh-generation-with-neural-networks)
7. [Point Cloud Processing](#7-point-cloud-processing)
8. [Text-to-3D Generation](#8-text-to-3d-generation)
9. [Image-to-3D Generation](#9-image-to-3d-generation)
10. [3D-Aware Image Synthesis](#10-3d-aware-image-synthesis)
11. [Physics-Based Simulation with ML](#11-physics-based-simulation-with-ml)
12. [Texture and Material Generation](#12-texture-and-material-generation)
13. [Animation and Motion Generation](#13-animation-and-motion-generation)
14. [Practical Projects](#14-practical-projects)
15. [Summary and Key Takeaways](#15-summary-and-key-takeaways)

---

## 1. What is 3D Generation?

3D generation refers to the task of creating three-dimensional content -- shapes, scenes, textures, animations -- using computational methods. This chapter covers the intersection of deep learning and 3D content creation, which has become one of the most rapidly advancing areas in AI.

### Why 3D Generation Matters

- **Gaming**: Procedural generation of 3D assets (characters, environments, props)
- **Film and VFX**: Rapid prototyping, virtual sets, digital doubles
- **Architecture**: Generating building designs, interior layouts
- **Manufacturing**: Product design, rapid prototyping
- **AR/VR**: Real-time 3D content for immersive experiences
- **Robotics**: Understanding and simulating 3D environments
- **Medical imaging**: 3D reconstruction from CT/MRI scans

### The Core Challenge

The fundamental difficulty of 3D generation is that our training data usually comes in 2D form (photographs, renders) but we need to produce 3D outputs. This means the model must somehow learn 3D structure from 2D observations. This is sometimes called the "inverse rendering" problem: given images, recover the 3D scene that produced them.

---

## 2. 3D Representations

Before building any 3D model, you must understand how 3D data is represented in a computer. Each representation has different strengths and weaknesses.

### 2.1 Meshes

A mesh is the most common representation in computer graphics. It consists of:

- **Vertices**: 3D points (x, y, z coordinates)
- **Edges**: Lines connecting pairs of vertices
- **Faces**: Polygons (usually triangles) defined by edges

```python
import numpy as np
import trimesh

# A mesh is fundamentally just vertices and faces
# Vertices: N x 3 array of (x, y, z) positions
vertices = np.array([
    [0, 0, 0],    # vertex 0
    [1, 0, 0],    # vertex 1
    [0.5, 1, 0],  # vertex 2
    [0.5, 0.5, 1] # vertex 3
], dtype=np.float32)

# Faces: M x 3 array of vertex indices (for triangle meshes)
# Each row defines a triangle by referencing 3 vertex indices
faces = np.array([
    [0, 1, 2],  # triangle 0: bottom face
    [0, 1, 3],  # triangle 1: front face
    [1, 2, 3],  # triangle 2: right face
    [0, 2, 3],  # triangle 3: left face
], dtype=np.int64)

# Create a mesh object
mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

# Mesh properties
print(f"Number of vertices: {len(mesh.vertices)}")  # 4
print(f"Number of faces: {len(mesh.faces)}")          # 4
print(f"Is watertight: {mesh.is_watertight}")
print(f"Volume: {mesh.volume}")
print(f"Surface area: {mesh.area}")
print(f"Bounding box: {mesh.bounds}")

# Export to common formats
mesh.export("tetrahedron.obj")   # Wavefront OBJ
mesh.export("tetrahedron.stl")   # STL (3D printing)
mesh.export("tetrahedron.ply")   # PLY (point cloud + mesh)
mesh.export("tetrahedron.glb")   # glTF binary (web/AR)
```

**Mesh file formats explained:**

| Format | Description | Use Case |
|--------|-------------|----------|
| OBJ | Text-based, stores vertices, normals, UVs, materials | General purpose, widely supported |
| STL | Triangle-only, no color/texture | 3D printing |
| PLY | Supports per-vertex colors, flexible | Point clouds, scanned data |
| FBX | Binary, supports animation, materials | Game engines, animation |
| glTF/GLB | JSON + binary, web-optimized | Web, AR/VR |
| USD | Universal Scene Description (Pixar) | Film production, complex scenes |

**Advantages of meshes:**
- Efficient rendering (GPU-optimized)
- Explicit surface representation
- Industry-standard format
- Easy to edit in modeling software

**Disadvantages of meshes:**
- Fixed topology (changing the number of vertices/faces is hard)
- Not differentiable by default (hard to optimize with gradient descent)
- Difficult to represent complex topologies (holes, branching structures)

### 2.2 Point Clouds

A point cloud is a set of 3D points with optional attributes (color, normal, intensity).

```python
import numpy as np
import open3d as o3d

# A point cloud is simply an N x 3 array of (x, y, z) coordinates
points = np.random.randn(10000, 3).astype(np.float32)

# Optional: colors (N x 3, values 0-1)
colors = np.random.rand(10000, 3).astype(np.float32)

# Optional: normals (N x 3, unit vectors)
normals = np.random.randn(10000, 3).astype(np.float32)
normals = normals / np.linalg.norm(normals, axis=1, keepdims=True)

# Create an Open3D point cloud
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)
pcd.colors = o3d.utility.Vector3dVector(colors)
pcd.normals = o3d.utility.Vector3dVector(normals)

# Estimate normals if not available
pcd.estimate_normals(
    search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30)
)

# Statistical outlier removal
cleaned_pcd, indices = pcd.remove_statistical_outlier(
    nb_neighbors=20,    # Number of neighbors to consider
    std_ratio=2.0       # Standard deviation threshold
)

# Downsample using voxel grid
downsampled = pcd.voxel_down_sample(voxel_size=0.05)

# Save and load
o3d.io.write_point_cloud("cloud.ply", pcd)
loaded = o3d.io.read_point_cloud("cloud.ply")

# Convert point cloud to mesh using Poisson reconstruction
mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
    pcd, depth=9
)
```

**Advantages of point clouds:**
- Easy to capture (LiDAR, depth cameras, photogrammetry)
- No topology constraints
- Memory-efficient for sparse representations

**Disadvantages:**
- No surface connectivity information
- Rendering is less efficient than meshes
- Unstructured -- cannot directly use standard convolutions

### 2.3 Voxels

Voxels are 3D pixels -- a regular grid of cells in 3D space, each either occupied or empty (binary), or containing a continuous value (density, color, etc.).

```python
import numpy as np

# A voxel grid is a 3D array
# Binary occupancy: 1 = occupied, 0 = empty
resolution = 64
voxel_grid = np.zeros((resolution, resolution, resolution), dtype=np.float32)

# Create a sphere in voxel space
center = resolution // 2
radius = resolution // 4
for x in range(resolution):
    for y in range(resolution):
        for z in range(resolution):
            dist = np.sqrt((x - center)**2 + (y - center)**2 + (z - center)**2)
            if dist <= radius:
                voxel_grid[x, y, z] = 1.0

# Voxels can be processed with 3D convolutions
import torch
import torch.nn as nn

# Batch x Channels x Depth x Height x Width
voxel_tensor = torch.from_numpy(voxel_grid).unsqueeze(0).unsqueeze(0)
# Shape: (1, 1, 64, 64, 64)

# 3D convolution
conv3d = nn.Conv3d(
    in_channels=1,
    out_channels=32,
    kernel_size=3,
    padding=1
)
output = conv3d(voxel_tensor)
# Shape: (1, 32, 64, 64, 64)
```

**Advantages of voxels:**
- Regular structure -- directly compatible with 3D CNNs
- Simple to implement
- Easy boolean operations (union, intersection, difference)

**Disadvantages:**
- Memory grows cubically with resolution: 64^3 = 262K, 256^3 = 16.7M, 512^3 = 134M cells
- Most cells are empty (wasteful)
- Blocky appearance unless very high resolution

### 2.4 Signed Distance Functions (SDF)

An SDF assigns a signed distance value to every point in 3D space:
- **Negative** values: inside the object
- **Zero**: on the surface
- **Positive** values: outside the object

```python
import numpy as np

def sphere_sdf(points, center, radius):
    """
    Signed distance function for a sphere.
    Negative inside, zero on surface, positive outside.
    
    points: (N, 3) array of query positions
    center: (3,) center of sphere
    radius: float
    """
    distances = np.linalg.norm(points - center, axis=1)
    return distances - radius

def box_sdf(points, center, half_extents):
    """SDF for an axis-aligned box."""
    q = np.abs(points - center) - half_extents
    outside = np.linalg.norm(np.maximum(q, 0), axis=1)
    inside = np.minimum(np.max(q, axis=1), 0)
    return outside + inside

# Boolean operations with SDFs are trivially easy:
def union_sdf(sdf_a, sdf_b):
    """Union of two shapes = minimum of their SDFs."""
    return np.minimum(sdf_a, sdf_b)

def intersection_sdf(sdf_a, sdf_b):
    """Intersection = maximum of SDFs."""
    return np.maximum(sdf_a, sdf_b)

def difference_sdf(sdf_a, sdf_b):
    """Subtraction: A minus B = max(sdf_a, -sdf_b)."""
    return np.maximum(sdf_a, -sdf_b)

# Extract a mesh from an SDF using Marching Cubes
from skimage.measure import marching_cubes

# Evaluate SDF on a 3D grid
resolution = 128
x = np.linspace(-2, 2, resolution)
y = np.linspace(-2, 2, resolution)
z = np.linspace(-2, 2, resolution)
xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
grid_points = np.stack([xx, yy, zz], axis=-1).reshape(-1, 3)

# Compute SDF values
sdf_values = sphere_sdf(grid_points, center=np.array([0, 0, 0]), radius=1.0)
sdf_grid = sdf_values.reshape(resolution, resolution, resolution)

# Marching Cubes extracts the zero-level-set (the surface)
vertices, faces, normals, values = marching_cubes(sdf_grid, level=0.0)

# Scale vertices back to world coordinates
vertices = vertices / resolution * 4 - 2  # Map from [0, res] to [-2, 2]
```

**Why SDFs are important for deep learning:**
- Continuous representation -- can be evaluated at any point
- Easy to extract meshes (Marching Cubes)
- Neural networks can learn to predict SDF values (DeepSDF)
- Boolean operations are trivial

### 2.5 Neural Implicit Representations

Instead of storing explicit geometry, use a neural network to represent the 3D shape. The network takes a 3D coordinate (x, y, z) as input and outputs some property (occupancy, signed distance, color, density).

```python
import torch
import torch.nn as nn

class NeuralImplicitSurface(nn.Module):
    """
    A neural network that represents a 3D shape.
    Input: (x, y, z) coordinate
    Output: signed distance to the surface
    """
    def __init__(self, hidden_dim=256, num_layers=8):
        super().__init__()
        
        layers = []
        # First layer: 3D input
        layers.append(nn.Linear(3, hidden_dim))
        layers.append(nn.ReLU())
        
        # Hidden layers with skip connection at layer 4 (like DeepSDF)
        for i in range(1, num_layers):
            if i == 4:
                # Skip connection: concatenate input to features
                layers.append(nn.Linear(hidden_dim + 3, hidden_dim))
            else:
                layers.append(nn.Linear(hidden_dim, hidden_dim))
            layers.append(nn.ReLU())
        
        # Output: single SDF value
        layers.append(nn.Linear(hidden_dim, 1))
        
        self.layers = nn.ModuleList(layers)
        self.skip_layer_index = 4
    
    def forward(self, coords):
        """
        coords: (batch_size, 3) -- x, y, z positions
        returns: (batch_size, 1) -- signed distance values
        """
        x = coords
        h = x
        layer_idx = 0
        for i, layer in enumerate(self.layers):
            if isinstance(layer, nn.Linear):
                if layer_idx == self.skip_layer_index:
                    h = torch.cat([h, x], dim=-1)
                h = layer(h)
                layer_idx += 1
            else:
                h = layer(h)
        return h

# Usage
model = NeuralImplicitSurface()
query_points = torch.randn(1000, 3)  # 1000 random 3D points
sdf_predictions = model(query_points)  # (1000, 1) SDF values
```

### 2.6 Comparison of Representations

| Representation | Memory | Resolution | Topology | GPU Friendly | Learning |
|---------------|--------|-----------|----------|------------|---------|
| Mesh | Low | Fixed vertices | Fixed | Yes (rendering) | Hard |
| Point Cloud | Low | N points | Free | Moderate | Moderate |
| Voxel | High (O(n^3)) | Fixed grid | Free | Yes (3D CNN) | Easy |
| SDF (grid) | High (O(n^3)) | Fixed grid | Free | Yes | Easy |
| Neural Implicit | Model params | Continuous | Free | Yes | Yes |

---

## 3. Classical 3D Reconstruction

Before diving into neural methods, it is important to understand classical 3D reconstruction techniques, as they form the foundation and are still used in practice.

### 3.1 Stereo Vision

The basic idea: two cameras viewing the same scene from slightly different positions. By finding corresponding points between the two images, you can triangulate their 3D position.

**The Math:**

Given a point P in 3D space visible in two cameras:
- Camera 1 sees P at pixel (u1, v1)
- Camera 2 sees P at pixel (u2, v2)
- The horizontal difference (u1 - u2) is called the **disparity**
- Depth is inversely proportional to disparity: Z = (f * B) / d
  - f = focal length
  - B = baseline (distance between cameras)
  - d = disparity

```python
import cv2
import numpy as np

# Load stereo pair (left and right images)
left = cv2.imread("left.png", cv2.IMREAD_GRAYSCALE)
right = cv2.imread("right.png", cv2.IMREAD_GRAYSCALE)

# Semi-Global Block Matching (SGBM) stereo matcher
stereo = cv2.StereoSGBM_create(
    minDisparity=0,
    numDisparities=128,    # Must be divisible by 16
    blockSize=5,
    P1=8 * 3 * 5**2,      # Penalty for disparity changes of 1
    P2=32 * 3 * 5**2,     # Penalty for larger disparity changes
    disp12MaxDiff=1,
    uniquenessRatio=10,
    speckleWindowSize=100,
    speckleRange=32
)

# Compute disparity map
disparity = stereo.compute(left, right).astype(np.float32) / 16.0

# Convert disparity to depth
focal_length = 700.0   # pixels
baseline = 0.1         # meters
depth = (focal_length * baseline) / (disparity + 1e-6)
```

### 3.2 Structure from Motion (SfM)

SfM recovers 3D structure from a set of 2D images taken from different viewpoints. It simultaneously estimates:
- **Camera poses** (position and orientation for each image)
- **3D point cloud** (sparse set of 3D points)

The pipeline:
1. **Feature detection**: Find distinctive points in each image (SIFT, ORB, SuperPoint)
2. **Feature matching**: Find corresponding features between image pairs
3. **Geometric verification**: Use RANSAC to filter out incorrect matches
4. **Triangulation**: Compute 3D positions of matched points
5. **Bundle adjustment**: Jointly optimize all camera poses and 3D points to minimize reprojection error

```python
# Using COLMAP (the industry standard SfM tool, called from Python)
import subprocess
import os

def run_colmap_sfm(image_dir, output_dir):
    """Run COLMAP Structure-from-Motion pipeline."""
    os.makedirs(output_dir, exist_ok=True)
    database_path = os.path.join(output_dir, "database.db")
    sparse_dir = os.path.join(output_dir, "sparse")
    os.makedirs(sparse_dir, exist_ok=True)
    
    # Step 1: Feature extraction
    subprocess.run([
        "colmap", "feature_extractor",
        "--database_path", database_path,
        "--image_path", image_dir,
        "--ImageReader.single_camera", "1",
        "--SiftExtraction.use_gpu", "1"
    ], check=True)
    
    # Step 2: Feature matching
    subprocess.run([
        "colmap", "exhaustive_matcher",
        "--database_path", database_path,
        "--SiftMatching.use_gpu", "1"
    ], check=True)
    
    # Step 3: Sparse reconstruction (SfM)
    subprocess.run([
        "colmap", "mapper",
        "--database_path", database_path,
        "--image_path", image_dir,
        "--output_path", sparse_dir
    ], check=True)
    
    return sparse_dir

# After SfM, you have sparse point cloud + camera poses
# This is the starting point for NeRF, Gaussian Splatting, etc.
```

### 3.3 Multi-View Stereo (MVS)

MVS takes the sparse SfM output and produces a dense 3D reconstruction:

```python
def run_colmap_mvs(image_dir, sparse_dir, output_dir):
    """Run COLMAP dense reconstruction pipeline."""
    dense_dir = os.path.join(output_dir, "dense")
    os.makedirs(dense_dir, exist_ok=True)
    
    # Step 1: Undistort images
    subprocess.run([
        "colmap", "image_undistorter",
        "--image_path", image_dir,
        "--input_path", os.path.join(sparse_dir, "0"),
        "--output_path", dense_dir,
        "--output_type", "COLMAP"
    ], check=True)
    
    # Step 2: Dense stereo (depth map estimation)
    subprocess.run([
        "colmap", "patch_match_stereo",
        "--workspace_path", dense_dir,
        "--PatchMatchStereo.geom_consistency", "true"
    ], check=True)
    
    # Step 3: Depth map fusion into dense point cloud
    subprocess.run([
        "colmap", "stereo_fusion",
        "--workspace_path", dense_dir,
        "--output_path", os.path.join(dense_dir, "fused.ply")
    ], check=True)
    
    return os.path.join(dense_dir, "fused.ply")
```

---

## 4. Neural Radiance Fields (NeRF)

NeRF, introduced by Mildenhall et al. in 2020, was a breakthrough in neural 3D reconstruction and novel view synthesis. It represents a scene as a continuous volumetric function using a neural network.

### 4.1 The Core Idea

NeRF trains a neural network to map a 5D input (3D position + 2D viewing direction) to a color and density:

```
F(x, y, z, theta, phi) -> (r, g, b, sigma)
```

Where:
- (x, y, z) = 3D position in space
- (theta, phi) = viewing direction (spherical coordinates)
- (r, g, b) = color at that point from that direction
- sigma = volume density (how opaque the point is)

The viewing direction input allows the model to capture view-dependent effects like specular reflections (shiny surfaces look different from different angles).

### 4.2 Volume Rendering

To render a pixel, NeRF casts a ray from the camera through that pixel into the scene and evaluates the network at many points along the ray. The final pixel color is computed using volume rendering:

```
C(r) = integral from t_near to t_far of T(t) * sigma(t) * c(t) dt

where T(t) = exp(-integral from t_near to t of sigma(s) ds)
```

T(t) is the accumulated transmittance -- the probability that the ray has not hit anything yet by distance t.

In practice, this integral is approximated with numerical quadrature (sampling points along the ray):

```python
def volume_render(colors, densities, deltas):
    """
    Volume rendering along a ray.
    
    colors: (N_samples, 3) -- RGB color at each sample point
    densities: (N_samples, 1) -- volume density at each sample
    deltas: (N_samples, 1) -- distance between consecutive samples
    
    Returns:
        rgb: (3,) -- final rendered pixel color
        depth: scalar -- expected depth
        weights: (N_samples,) -- contribution of each sample
    """
    import torch
    
    # Alpha compositing
    # alpha_i = 1 - exp(-sigma_i * delta_i)
    alpha = 1.0 - torch.exp(-densities * deltas)  # (N_samples, 1)
    
    # Transmittance: product of (1 - alpha) for all previous samples
    # T_i = prod_{j=1}^{i-1} (1 - alpha_j)
    transmittance = torch.cumprod(
        torch.cat([torch.ones(1, 1), 1.0 - alpha[:-1]], dim=0),
        dim=0
    )  # (N_samples, 1)
    
    # Weights for each sample
    weights = transmittance * alpha  # (N_samples, 1)
    
    # Final color: weighted sum
    rgb = (weights * colors).sum(dim=0)  # (3,)
    
    # Expected depth
    t_values = torch.linspace(0, 1, len(densities))
    depth = (weights.squeeze() * t_values).sum()
    
    return rgb, depth, weights.squeeze()
```

### 4.3 Positional Encoding

A critical insight: neural networks (MLPs) struggle to learn high-frequency functions. The raw (x, y, z) coordinates produce blurry results. The solution is positional encoding, which maps the input to a higher-dimensional space using sinusoidal functions:

```python
import torch
import torch.nn as nn

class PositionalEncoding(nn.Module):
    """
    Maps a scalar x to a higher-dimensional vector:
    gamma(x) = [sin(2^0 * pi * x), cos(2^0 * pi * x),
                sin(2^1 * pi * x), cos(2^1 * pi * x),
                ...,
                sin(2^(L-1) * pi * x), cos(2^(L-1) * pi * x)]
    
    This allows the network to learn high-frequency details.
    """
    def __init__(self, num_frequencies=10, include_input=True):
        super().__init__()
        self.num_frequencies = num_frequencies
        self.include_input = include_input
        
        # Frequency bands: 2^0, 2^1, ..., 2^(L-1)
        self.frequency_bands = 2.0 ** torch.linspace(
            0.0, num_frequencies - 1, num_frequencies
        )
    
    def forward(self, x):
        """
        x: (..., D) input coordinates
        Returns: (..., D * (2L + 1)) if include_input, else (..., D * 2L)
        """
        encodings = []
        
        if self.include_input:
            encodings.append(x)
        
        for freq in self.frequency_bands:
            encodings.append(torch.sin(freq * torch.pi * x))
            encodings.append(torch.cos(freq * torch.pi * x))
        
        return torch.cat(encodings, dim=-1)
    
    def output_dim(self, input_dim):
        """Calculate output dimensionality."""
        mult = 2 * self.num_frequencies
        if self.include_input:
            mult += 1
        return input_dim * mult

# For 3D coordinates with L=10 frequencies:
pos_enc = PositionalEncoding(num_frequencies=10)
# Input dim=3, output dim = 3 * (2*10 + 1) = 63

# For viewing direction with L=4 frequencies:
dir_enc = PositionalEncoding(num_frequencies=4)
# Input dim=3 (direction as unit vector), output dim = 3 * (2*4 + 1) = 27
```

### 4.4 Full NeRF Implementation

```python
import torch
import torch.nn as nn

class NeRF(nn.Module):
    """
    Complete Neural Radiance Field network.
    
    Architecture:
    - 8-layer MLP for density and feature extraction
    - Skip connection at layer 4
    - Additional head for color (conditioned on view direction)
    """
    def __init__(self, pos_enc_dim=63, dir_enc_dim=27, hidden_dim=256):
        super().__init__()
        
        # Positional encoding layers
        self.pos_encoding = PositionalEncoding(num_frequencies=10)
        self.dir_encoding = PositionalEncoding(num_frequencies=4)
        
        # Density network: 8 layers with skip connection at layer 4
        self.density_layers = nn.ModuleList()
        self.density_layers.append(nn.Linear(pos_enc_dim, hidden_dim))
        for i in range(1, 8):
            if i == 4:
                # Skip connection: input is concatenated with features
                self.density_layers.append(nn.Linear(hidden_dim + pos_enc_dim, hidden_dim))
            else:
                self.density_layers.append(nn.Linear(hidden_dim, hidden_dim))
        
        # Density output (single scalar)
        self.density_out = nn.Linear(hidden_dim, 1)
        
        # Feature output (input to color network)
        self.feature_out = nn.Linear(hidden_dim, hidden_dim)
        
        # Color network: takes features + view direction
        self.color_layers = nn.Sequential(
            nn.Linear(hidden_dim + dir_enc_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 3),
            nn.Sigmoid()  # Colors in [0, 1]
        )
    
    def forward(self, positions, directions):
        """
        positions: (batch, 3) -- 3D positions
        directions: (batch, 3) -- viewing directions (unit vectors)
        
        Returns:
            colors: (batch, 3) -- RGB
            density: (batch, 1) -- volume density (non-negative)
        """
        # Positional encoding
        pos_encoded = self.pos_encoding(positions)   # (batch, 63)
        dir_encoded = self.dir_encoding(directions)  # (batch, 27)
        
        # Density network with skip connection
        h = pos_encoded
        for i, layer in enumerate(self.density_layers):
            if i == 4:
                h = torch.cat([h, pos_encoded], dim=-1)
            h = torch.relu(layer(h))
        
        # Density (using softplus to ensure non-negative)
        density = torch.nn.functional.softplus(self.density_out(h))  # (batch, 1)
        
        # Feature vector
        features = self.feature_out(h)  # (batch, 256)
        
        # Color network
        color_input = torch.cat([features, dir_encoded], dim=-1)
        colors = self.color_layers(color_input)  # (batch, 3)
        
        return colors, density


class NeRFRenderer:
    """
    Renders images from a NeRF model.
    """
    def __init__(self, model, near=2.0, far=6.0, n_samples=64, n_fine=128):
        self.model = model
        self.near = near
        self.far = far
        self.n_samples = n_samples
        self.n_fine = n_fine
    
    def get_rays(self, height, width, focal, c2w):
        """
        Generate rays for each pixel.
        
        height, width: image dimensions
        focal: focal length in pixels
        c2w: (4, 4) camera-to-world transformation matrix
        
        Returns:
            ray_origins: (H*W, 3)
            ray_directions: (H*W, 3)
        """
        # Create pixel coordinates
        i, j = torch.meshgrid(
            torch.arange(width, dtype=torch.float32),
            torch.arange(height, dtype=torch.float32),
            indexing='xy'
        )
        
        # Convert pixel to camera coordinates
        # Camera looks down -Z axis, X is right, Y is down
        directions = torch.stack([
            (i - width * 0.5) / focal,
            -(j - height * 0.5) / focal,
            -torch.ones_like(i)
        ], dim=-1)  # (H, W, 3)
        
        # Rotate ray directions from camera to world frame
        ray_dirs = (c2w[:3, :3] @ directions.reshape(-1, 3).T).T  # (H*W, 3)
        ray_dirs = ray_dirs / ray_dirs.norm(dim=-1, keepdim=True)
        
        # Ray origins are the camera position (translation part of c2w)
        ray_origins = c2w[:3, 3].expand_as(ray_dirs)  # (H*W, 3)
        
        return ray_origins, ray_dirs
    
    def sample_along_rays(self, ray_origins, ray_dirs, n_samples):
        """
        Sample points along each ray between near and far planes.
        Uses stratified sampling for better coverage.
        """
        t_vals = torch.linspace(self.near, self.far, n_samples)
        
        # Stratified sampling: add noise within each bin
        mids = 0.5 * (t_vals[:-1] + t_vals[1:])
        upper = torch.cat([mids, t_vals[-1:]])
        lower = torch.cat([t_vals[:1], mids])
        t_rand = torch.rand(n_samples)
        t_vals = lower + (upper - lower) * t_rand
        
        # Compute 3D positions along rays
        # points = origin + t * direction
        points = ray_origins.unsqueeze(1) + t_vals.unsqueeze(0).unsqueeze(-1) * ray_dirs.unsqueeze(1)
        # Shape: (n_rays, n_samples, 3)
        
        return points, t_vals
    
    def render_rays(self, ray_origins, ray_dirs):
        """Render a batch of rays."""
        # Coarse sampling
        points, t_vals = self.sample_along_rays(ray_origins, ray_dirs, self.n_samples)
        n_rays = ray_origins.shape[0]
        
        # Expand directions to match points
        dirs_expanded = ray_dirs.unsqueeze(1).expand_as(points)
        
        # Query the network
        flat_points = points.reshape(-1, 3)
        flat_dirs = dirs_expanded.reshape(-1, 3)
        
        with torch.no_grad():
            colors, densities = self.model(flat_points, flat_dirs)
        
        colors = colors.reshape(n_rays, self.n_samples, 3)
        densities = densities.reshape(n_rays, self.n_samples, 1)
        
        # Compute distances between samples
        deltas = t_vals[1:] - t_vals[:-1]
        deltas = torch.cat([deltas, torch.tensor([1e10])])  # Infinite last delta
        deltas = deltas.unsqueeze(0).unsqueeze(-1).expand(n_rays, -1, 1)
        
        # Volume rendering
        alpha = 1.0 - torch.exp(-densities * deltas)
        transmittance = torch.cumprod(
            torch.cat([torch.ones(n_rays, 1, 1), 1.0 - alpha[:, :-1]], dim=1),
            dim=1
        )
        weights = transmittance * alpha
        
        # Final pixel colors
        rgb = (weights * colors).sum(dim=1)  # (n_rays, 3)
        
        return rgb


def train_nerf(images, poses, focal_length, n_iterations=100000):
    """
    Train a NeRF model from a set of images with known camera poses.
    
    images: (N, H, W, 3) -- training images, values in [0, 1]
    poses: (N, 4, 4) -- camera-to-world matrices for each image
    focal_length: float -- focal length in pixels
    n_iterations: int -- number of training iterations
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    model = NeRF().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=5e-4)
    scheduler = torch.optim.lr_scheduler.ExponentialLR(optimizer, gamma=0.9999)
    
    renderer = NeRFRenderer(model)
    
    n_images, height, width, _ = images.shape
    
    for iteration in range(n_iterations):
        # Randomly select an image
        img_idx = torch.randint(0, n_images, (1,)).item()
        target_image = images[img_idx].to(device)
        pose = poses[img_idx].to(device)
        
        # Generate rays for this image
        ray_origins, ray_dirs = renderer.get_rays(height, width, focal_length, pose)
        
        # Randomly sample a batch of rays (not all -- too expensive)
        n_rand = 1024  # batch size
        select_indices = torch.randint(0, height * width, (n_rand,))
        ray_origins = ray_origins[select_indices].to(device)
        ray_dirs = ray_dirs[select_indices].to(device)
        target_pixels = target_image.reshape(-1, 3)[select_indices]
        
        # Render
        predicted_rgb = renderer.render_rays(ray_origins, ray_dirs)
        
        # Loss: MSE between predicted and actual pixel colors
        loss = torch.nn.functional.mse_loss(predicted_rgb, target_pixels)
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        scheduler.step()
        
        if iteration % 1000 == 0:
            psnr = -10.0 * torch.log10(loss)
            print(f"Iteration {iteration}, Loss: {loss.item():.6f}, PSNR: {psnr.item():.2f}")
    
    return model
```

### 4.5 Instant-NGP and Hash Encoding

The original NeRF is slow (hours to train, seconds per frame to render). Instant-NGP (Mueller et al., 2022) replaced the deep MLP with a multi-resolution hash table, reducing training to seconds and enabling real-time rendering.

**Key idea**: Instead of positional encoding with sinusoids, use a learned hash table at multiple resolutions:

```python
import torch
import torch.nn as nn

class HashEncoding(nn.Module):
    """
    Simplified multi-resolution hash encoding (Instant-NGP style).
    
    Idea: maintain hash tables at multiple resolutions.
    For each resolution, hash the grid cell index to look up a learned feature vector.
    Interpolate features within each grid cell, then concatenate across resolutions.
    """
    def __init__(
        self,
        n_levels=16,          # Number of resolution levels
        n_features_per_level=2,  # Features stored per hash entry
        log2_hashmap_size=19,    # Hash table size = 2^19
        base_resolution=16,      # Coarsest grid resolution
        finest_resolution=2048   # Finest grid resolution
    ):
        super().__init__()
        self.n_levels = n_levels
        self.n_features = n_features_per_level
        self.hashmap_size = 2 ** log2_hashmap_size
        
        # Compute resolution at each level (geometric progression)
        growth_factor = (finest_resolution / base_resolution) ** (1.0 / (n_levels - 1))
        self.resolutions = [int(base_resolution * growth_factor ** i) for i in range(n_levels)]
        
        # Hash tables: one per level, each with hashmap_size entries of n_features dimensions
        self.hash_tables = nn.ParameterList([
            nn.Parameter(torch.randn(self.hashmap_size, n_features_per_level) * 0.01)
            for _ in range(n_levels)
        ])
    
    def hash_function(self, coords):
        """
        Spatial hash function mapping integer 3D coordinates to hash table indices.
        Uses XOR of coordinates multiplied by large primes.
        """
        primes = [1, 2654435761, 805459861]
        result = torch.zeros(coords.shape[0], dtype=torch.long, device=coords.device)
        for i in range(3):
            result ^= coords[:, i].long() * primes[i]
        return result % self.hashmap_size
    
    def forward(self, positions):
        """
        positions: (batch, 3) -- normalized to [0, 1]
        Returns: (batch, n_levels * n_features_per_level)
        """
        outputs = []
        
        for level, resolution in enumerate(self.resolutions):
            # Scale positions to grid resolution
            scaled = positions * resolution
            
            # Get grid cell indices (floor)
            floor_coords = torch.floor(scaled).int()
            
            # Get interpolation weights
            weights = scaled - floor_coords.float()
            
            # Trilinear interpolation: query 8 corners of the cell
            features = torch.zeros(
                positions.shape[0], self.n_features,
                device=positions.device
            )
            
            for dx in [0, 1]:
                for dy in [0, 1]:
                    for dz in [0, 1]:
                        corner = floor_coords + torch.tensor([dx, dy, dz], device=positions.device)
                        idx = self.hash_function(corner)
                        
                        # Trilinear interpolation weight
                        wx = (1 - weights[:, 0]) if dx == 0 else weights[:, 0]
                        wy = (1 - weights[:, 1]) if dy == 0 else weights[:, 1]
                        wz = (1 - weights[:, 2]) if dz == 0 else weights[:, 2]
                        w = (wx * wy * wz).unsqueeze(-1)
                        
                        features += w * self.hash_tables[level][idx]
            
            outputs.append(features)
        
        return torch.cat(outputs, dim=-1)  # (batch, n_levels * n_features)

    def output_dim(self):
        return self.n_levels * self.n_features
```

### 4.6 Using Nerfstudio (Practical NeRF)

In practice, you do not implement NeRF from scratch. Use nerfstudio, the most popular NeRF framework:

```bash
# Install nerfstudio
pip install nerfstudio

# Process your images (estimates camera poses using COLMAP)
ns-process-data images --data ./my_photos/ --output-dir ./processed/

# Train a NeRF model (nerfacto is a good default)
ns-train nerfacto --data ./processed/

# Train with Instant-NGP (fastest)
ns-train instant-ngp --data ./processed/

# View the training in real-time
# Open the URL printed in the terminal in your browser

# Export a mesh after training
ns-export poisson --load-config outputs/my_scene/nerfacto/config.yml \
    --output-dir exports/mesh/

# Export a point cloud
ns-export pointcloud --load-config outputs/my_scene/nerfacto/config.yml \
    --output-dir exports/pointcloud/

# Render a video along a camera path
ns-render camera-path --load-config outputs/my_scene/nerfacto/config.yml \
    --camera-path-filename camera_path.json \
    --output-path renders/video.mp4
```

---

## 5. 3D Gaussian Splatting

3D Gaussian Splatting (3DGS), introduced by Kerbl et al. in 2023, represents a scene as a collection of 3D Gaussian primitives. It achieves real-time rendering at high quality and trains in minutes.

### 5.1 Core Concept

Instead of representing the scene as a continuous volume (NeRF) or a mesh, represent it as millions of small 3D Gaussians. Each Gaussian has:

- **Position** (mean): (x, y, z) -- where it is in 3D space
- **Covariance matrix**: 3x3 matrix defining its shape (size and orientation)
- **Opacity**: alpha value (how transparent/opaque it is)
- **Color**: represented as spherical harmonics coefficients (for view-dependent color)

```python
import torch
import torch.nn as nn

class GaussianModel:
    """
    A set of 3D Gaussians representing a scene.
    All properties are learnable parameters.
    """
    def __init__(self, num_gaussians=100000):
        # Position: (N, 3) -- center of each Gaussian
        self.positions = nn.Parameter(torch.randn(num_gaussians, 3))
        
        # Scale: (N, 3) -- size along each axis (log scale for positivity)
        self.log_scales = nn.Parameter(torch.zeros(num_gaussians, 3) - 3.0)
        
        # Rotation: (N, 4) -- quaternion representing orientation
        self.rotations = nn.Parameter(torch.zeros(num_gaussians, 4))
        self.rotations.data[:, 0] = 1.0  # Initialize to identity quaternion
        
        # Opacity: (N, 1) -- logit (sigmoid applied during rendering)
        self.opacity_logits = nn.Parameter(torch.zeros(num_gaussians, 1))
        
        # Color: (N, 3) or (N, K, 3) if using spherical harmonics
        # Degree 0 = diffuse color only, degree 3 = view-dependent
        self.sh_coefficients = nn.Parameter(torch.randn(num_gaussians, 16, 3) * 0.01)
    
    @property
    def scales(self):
        return torch.exp(self.log_scales)
    
    @property
    def opacities(self):
        return torch.sigmoid(self.opacity_logits)
    
    def build_covariance_matrix(self, idx):
        """
        Build the 3D covariance matrix for Gaussian idx.
        Covariance = R * S * S^T * R^T
        where R is rotation matrix, S is diagonal scale matrix.
        """
        scale = self.scales[idx]  # (3,)
        rotation = self.rotations[idx]  # (4,) quaternion
        
        # Quaternion to rotation matrix
        R = quaternion_to_rotation_matrix(rotation)  # (3, 3)
        
        # Scale matrix
        S = torch.diag(scale)  # (3, 3)
        
        # Covariance
        covariance = R @ S @ S.T @ R.T  # (3, 3)
        return covariance


def quaternion_to_rotation_matrix(q):
    """Convert quaternion (w, x, y, z) to 3x3 rotation matrix."""
    w, x, y, z = q[0], q[1], q[2], q[3]
    
    R = torch.stack([
        1 - 2*y*y - 2*z*z,     2*x*y - 2*w*z,     2*x*z + 2*w*y,
        2*x*y + 2*w*z,     1 - 2*x*x - 2*z*z,     2*y*z - 2*w*x,
        2*x*z - 2*w*y,         2*y*z + 2*w*x, 1 - 2*x*x - 2*y*y
    ]).reshape(3, 3)
    
    return R
```

### 5.2 Rendering Process (Splatting)

Rendering is done by "splatting" each 3D Gaussian onto the 2D image plane:

1. **Project** each 3D Gaussian to 2D using the camera parameters
2. **Sort** all 2D Gaussians by depth (front to back)
3. **Blend** them using alpha compositing

```python
def project_gaussian_to_2d(mean_3d, covariance_3d, view_matrix, projection_matrix):
    """
    Project a 3D Gaussian to a 2D Gaussian on the image plane.
    
    The 3D covariance transforms to 2D via the Jacobian of the projection:
    Sigma_2d = J @ W @ Sigma_3d @ W^T @ J^T
    
    where W is the view matrix and J is the Jacobian of the perspective projection.
    """
    # Transform mean to camera space
    mean_cam = (view_matrix[:3, :3] @ mean_3d + view_matrix[:3, 3])
    
    # Jacobian of perspective projection
    fx, fy = projection_matrix[0, 0], projection_matrix[1, 1]
    z = mean_cam[2]
    
    J = torch.tensor([
        [fx / z, 0, -fx * mean_cam[0] / (z * z)],
        [0, fy / z, -fy * mean_cam[1] / (z * z)],
    ])
    
    # Project covariance
    W = view_matrix[:3, :3]
    cov_cam = W @ covariance_3d @ W.T
    cov_2d = J @ cov_cam @ J.T  # (2, 2)
    
    # Project mean to screen
    mean_2d = torch.tensor([
        fx * mean_cam[0] / z + projection_matrix[0, 2],
        fy * mean_cam[1] / z + projection_matrix[1, 2]
    ])
    
    return mean_2d, cov_2d


def rasterize_gaussians(means_2d, covs_2d, colors, opacities, image_size):
    """
    Simplified differentiable rasterization of 2D Gaussians.
    In practice, this is implemented in CUDA for performance.
    """
    H, W = image_size
    image = torch.zeros(H, W, 3)
    
    # Sort by depth (front to back)
    # (In practice, tile-based sorting is used for efficiency)
    
    for pixel_y in range(H):
        for pixel_x in range(W):
            pixel = torch.tensor([pixel_x + 0.5, pixel_y + 0.5])
            
            accumulated_color = torch.zeros(3)
            accumulated_alpha = 0.0
            
            for i in range(len(means_2d)):
                # Evaluate 2D Gaussian at this pixel
                diff = pixel - means_2d[i]
                cov_inv = torch.inverse(covs_2d[i])
                
                # Mahalanobis distance
                power = -0.5 * (diff @ cov_inv @ diff)
                
                if power > -4.0:  # Skip negligible contributions
                    gaussian_value = torch.exp(power)
                    alpha = opacities[i] * gaussian_value
                    
                    # Alpha compositing (front-to-back)
                    remaining = 1.0 - accumulated_alpha
                    accumulated_color += remaining * alpha * colors[i]
                    accumulated_alpha += remaining * alpha
                    
                    if accumulated_alpha > 0.999:
                        break
            
            image[pixel_y, pixel_x] = accumulated_color
    
    return image
```

### 5.3 Training 3D Gaussian Splatting

Training involves optimizing all Gaussian parameters to minimize the rendering loss, plus adaptive density control (adding/removing Gaussians):

```python
def train_gaussian_splatting(images, cameras, n_iterations=30000):
    """
    Training pipeline for 3D Gaussian Splatting.
    
    Key elements:
    1. Start from SfM point cloud (COLMAP output)
    2. Optimize position, scale, rotation, opacity, color
    3. Periodically densify (split/clone) and prune Gaussians
    """
    # Initialize Gaussians from SfM point cloud
    # (In practice, use COLMAP output)
    initial_points = get_sfm_points()  # (N, 3)
    model = GaussianModel(num_gaussians=len(initial_points))
    model.positions.data = initial_points
    
    optimizer = torch.optim.Adam([
        {'params': [model.positions], 'lr': 0.00016},
        {'params': [model.log_scales], 'lr': 0.005},
        {'params': [model.rotations], 'lr': 0.001},
        {'params': [model.opacity_logits], 'lr': 0.05},
        {'params': [model.sh_coefficients], 'lr': 0.0025},
    ])
    
    for iteration in range(n_iterations):
        # Random camera view
        cam_idx = torch.randint(0, len(cameras), (1,)).item()
        camera = cameras[cam_idx]
        target = images[cam_idx]
        
        # Render from this viewpoint
        rendered = render(model, camera)
        
        # Loss: L1 + SSIM
        l1_loss = torch.abs(rendered - target).mean()
        ssim_loss = 1.0 - compute_ssim(rendered, target)
        loss = 0.8 * l1_loss + 0.2 * ssim_loss
        
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        
        # Adaptive density control (every 100 iterations)
        if iteration % 100 == 0 and iteration < 15000:
            # Densification: split large Gaussians, clone small ones
            with torch.no_grad():
                # Compute gradient magnitude for positions
                grad_magnitude = model.positions.grad.norm(dim=-1)
                
                # Clone: small Gaussians with large gradients
                clone_mask = (grad_magnitude > 0.0002) & (model.scales.max(dim=-1).values < 0.01)
                
                # Split: large Gaussians with large gradients
                split_mask = (grad_magnitude > 0.0002) & (model.scales.max(dim=-1).values >= 0.01)
                
                # Prune: nearly transparent Gaussians
                prune_mask = model.opacities.squeeze() < 0.005
                
                # Apply densification
                densify_and_clone(model, clone_mask)
                densify_and_split(model, split_mask)
                prune_gaussians(model, prune_mask)
        
        if iteration % 1000 == 0:
            print(f"Iteration {iteration}, Loss: {loss.item():.4f}, "
                  f"Num Gaussians: {len(model.positions)}")
    
    return model
```

### 5.4 Using Gaussian Splatting in Practice

```bash
# Clone the official implementation
git clone https://github.com/graphdeco-inria/gaussian-splatting.git
cd gaussian-splatting

# Install dependencies
pip install -r requirements.txt
pip install submodules/diff-gaussian-rasterization
pip install submodules/simple-knn

# Prepare data (needs COLMAP)
python convert.py -s /path/to/your/images

# Train
python train.py -s /path/to/your/images -m output/my_scene

# Render
python render.py -m output/my_scene

# Evaluate quality
python metrics.py -m output/my_scene

# Interactive viewer (real-time)
# Use the SIBR viewer included in the repo
SIBR_viewers/install/bin/SIBR_gaussianViewer_app -m output/my_scene
```

### 5.5 NeRF vs Gaussian Splatting Comparison

| Aspect | NeRF | 3D Gaussian Splatting |
|--------|------|----------------------|
| Representation | Neural network (implicit) | Explicit Gaussians |
| Training time | Hours | Minutes |
| Rendering speed | Seconds per frame | Real-time (100+ FPS) |
| Quality | Excellent | Excellent |
| Memory | Network weights (~few MB) | Gaussians (~100s MB) |
| Editability | Difficult | Easy (move/delete Gaussians) |
| Mesh export | Via Marching Cubes | Via Poisson reconstruction |
| Dynamic scenes | Extensions exist | Extensions exist |

---

## 6. Mesh Generation with Neural Networks

### 6.1 DeepSDF (Learning Signed Distance Functions)

DeepSDF trains a neural network to predict the signed distance value for any point in space, given a latent code that specifies which shape to generate.

```python
import torch
import torch.nn as nn

class DeepSDF(nn.Module):
    """
    Auto-decoder architecture for learning shape SDFs.
    
    Instead of an encoder, each shape gets a learned latent code.
    The decoder maps (latent_code, xyz) -> sdf_value.
    """
    def __init__(self, latent_dim=256, hidden_dim=512, num_layers=8):
        super().__init__()
        
        self.latent_dim = latent_dim
        
        layers = []
        input_dim = latent_dim + 3  # latent code + xyz
        
        for i in range(num_layers):
            if i == 4:
                # Skip connection
                layers.append(nn.Linear(hidden_dim + latent_dim + 3, hidden_dim))
            else:
                layers.append(nn.Linear(input_dim if i == 0 else hidden_dim, hidden_dim))
            layers.append(nn.ReLU())
        
        layers.append(nn.Linear(hidden_dim, 1))  # SDF output
        
        self.network = nn.ModuleList(layers)
        self.skip_idx = 4
    
    def forward(self, latent_code, points):
        """
        latent_code: (batch, latent_dim)
        points: (batch, N_points, 3)
        Returns: (batch, N_points, 1) SDF values
        """
        batch_size, n_points, _ = points.shape
        
        # Expand latent code to match points
        latent = latent_code.unsqueeze(1).expand(-1, n_points, -1)  # (B, N, latent_dim)
        
        # Concatenate
        x = torch.cat([latent, points], dim=-1)  # (B, N, latent_dim + 3)
        input_x = x
        
        h = x
        layer_idx = 0
        for module in self.network:
            if isinstance(module, nn.Linear):
                if layer_idx == self.skip_idx:
                    h = torch.cat([h, input_x], dim=-1)
                h = module(h)
                layer_idx += 1
            else:
                h = module(h)
        
        return h  # (batch, N_points, 1)


def train_deepsdf(shapes_data, n_epochs=1000, latent_dim=256):
    """
    Train DeepSDF on a dataset of 3D shapes.
    
    shapes_data: list of (points, sdf_values) pairs
                 Each: points (N, 3), sdf (N, 1)
    """
    device = torch.device("cuda")
    n_shapes = len(shapes_data)
    
    model = DeepSDF(latent_dim=latent_dim).to(device)
    
    # Learnable latent codes (one per shape)
    latent_codes = nn.Embedding(n_shapes, latent_dim).to(device)
    nn.init.normal_(latent_codes.weight, 0.0, 0.01)
    
    optimizer = torch.optim.Adam([
        {'params': model.parameters(), 'lr': 1e-4},
        {'params': latent_codes.parameters(), 'lr': 1e-3}
    ])
    
    for epoch in range(n_epochs):
        total_loss = 0
        
        for shape_idx in range(n_shapes):
            points, gt_sdf = shapes_data[shape_idx]
            points = points.to(device).unsqueeze(0)    # (1, N, 3)
            gt_sdf = gt_sdf.to(device).unsqueeze(0)    # (1, N, 1)
            
            latent = latent_codes(torch.tensor([shape_idx], device=device))  # (1, latent_dim)
            
            pred_sdf = model(latent, points)
            
            # SDF loss: clamped L1
            clamp_val = 0.1
            pred_clamped = torch.clamp(pred_sdf, -clamp_val, clamp_val)
            gt_clamped = torch.clamp(gt_sdf, -clamp_val, clamp_val)
            sdf_loss = torch.abs(pred_clamped - gt_clamped).mean()
            
            # Latent code regularization
            reg_loss = 1e-4 * latent.norm(dim=-1).mean()
            
            loss = sdf_loss + reg_loss
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        if epoch % 100 == 0:
            print(f"Epoch {epoch}, Loss: {total_loss / n_shapes:.6f}")
    
    return model, latent_codes


def extract_mesh_from_sdf(model, latent_code, resolution=256, threshold=0.0):
    """
    Extract a mesh from a trained DeepSDF model using Marching Cubes.
    """
    from skimage.measure import marching_cubes
    
    device = latent_code.device
    
    # Create a 3D grid of query points
    x = torch.linspace(-1, 1, resolution)
    y = torch.linspace(-1, 1, resolution)
    z = torch.linspace(-1, 1, resolution)
    xx, yy, zz = torch.meshgrid(x, y, z, indexing='ij')
    grid_points = torch.stack([xx, yy, zz], dim=-1).reshape(-1, 3).to(device)
    
    # Query SDF in batches
    batch_size = 100000
    sdf_values = []
    
    with torch.no_grad():
        for i in range(0, len(grid_points), batch_size):
            batch = grid_points[i:i+batch_size].unsqueeze(0)  # (1, B, 3)
            sdf = model(latent_code.unsqueeze(0), batch)       # (1, B, 1)
            sdf_values.append(sdf.squeeze(0).squeeze(-1).cpu())
    
    sdf_grid = torch.cat(sdf_values).reshape(resolution, resolution, resolution).numpy()
    
    # Marching Cubes
    vertices, faces, normals, _ = marching_cubes(sdf_grid, level=threshold)
    
    # Scale to [-1, 1]
    vertices = vertices / resolution * 2 - 1
    
    return vertices, faces
```

### 6.2 Differentiable Rendering for Mesh Optimization

To optimize a mesh using gradient descent, you need differentiable rendering -- the ability to compute gradients of image pixels with respect to mesh vertices, textures, and materials.

```python
import torch
import pytorch3d
from pytorch3d.structures import Meshes
from pytorch3d.renderer import (
    FoVPerspectiveCameras,
    RasterizationSettings,
    MeshRenderer,
    MeshRasterizer,
    SoftPhongShader,
    TexturesVertex,
    PointLights,
)

def create_differentiable_renderer(image_size=256, device="cuda"):
    """Create a differentiable mesh renderer using PyTorch3D."""
    
    cameras = FoVPerspectiveCameras(device=device)
    
    raster_settings = RasterizationSettings(
        image_size=image_size,
        blur_radius=0.0,
        faces_per_pixel=1,
    )
    
    lights = PointLights(
        device=device,
        location=[[0.0, 0.0, -3.0]]
    )
    
    renderer = MeshRenderer(
        rasterizer=MeshRasterizer(
            cameras=cameras,
            raster_settings=raster_settings
        ),
        shader=SoftPhongShader(
            device=device,
            cameras=cameras,
            lights=lights
        )
    )
    
    return renderer


def optimize_mesh_to_target(initial_verts, faces, target_image, n_iterations=500):
    """
    Optimize mesh vertices to match a target image using differentiable rendering.
    """
    device = torch.device("cuda")
    
    # Make vertices learnable
    verts = initial_verts.clone().to(device).requires_grad_(True)
    faces = faces.to(device)
    
    # Vertex colors (also learnable)
    colors = torch.ones_like(verts).to(device).requires_grad_(True)
    
    renderer = create_differentiable_renderer(device=device)
    
    optimizer = torch.optim.Adam([verts, colors], lr=0.01)
    
    target = target_image.to(device)
    
    for i in range(n_iterations):
        # Create mesh with current vertices
        textures = TexturesVertex(verts_features=[colors])
        mesh = Meshes(verts=[verts], faces=[faces], textures=textures)
        
        # Render
        rendered = renderer(mesh)  # (1, H, W, 4) -- RGBA
        rendered_rgb = rendered[0, :, :, :3]
        
        # Loss
        loss = torch.nn.functional.mse_loss(rendered_rgb, target)
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if i % 50 == 0:
            print(f"Iteration {i}, Loss: {loss.item():.6f}")
    
    return verts.detach(), colors.detach()
```

### 6.3 Mesh Deformation Networks

Instead of directly optimizing vertices, predict deformations from a template mesh:

```python
class MeshDeformationNet(nn.Module):
    """
    Predict vertex offsets from a template mesh.
    Input: image (or latent code)
    Output: per-vertex displacement vectors
    """
    def __init__(self, n_vertices, latent_dim=512):
        super().__init__()
        
        # Image encoder (ResNet backbone)
        import torchvision.models as models
        resnet = models.resnet18(pretrained=True)
        self.encoder = nn.Sequential(*list(resnet.children())[:-1])
        
        # Deformation decoder
        self.decoder = nn.Sequential(
            nn.Linear(512, 1024),
            nn.ReLU(),
            nn.Linear(1024, 1024),
            nn.ReLU(),
            nn.Linear(1024, n_vertices * 3),  # 3D offset per vertex
        )
        
        self.n_vertices = n_vertices
    
    def forward(self, image):
        """
        image: (batch, 3, H, W)
        Returns: (batch, n_vertices, 3) vertex offsets
        """
        features = self.encoder(image).flatten(1)  # (batch, 512)
        offsets = self.decoder(features)              # (batch, n_vertices * 3)
        offsets = offsets.reshape(-1, self.n_vertices, 3)
        return offsets
```

---

## 7. Point Cloud Processing

### 7.1 PointNet: The Foundation

PointNet (Qi et al., 2017) was the first deep learning architecture designed specifically for point clouds. The key insight: process each point independently, then aggregate with a symmetric function (max pooling) to achieve permutation invariance.

```python
import torch
import torch.nn as nn

class PointNet(nn.Module):
    """
    PointNet for classification.
    
    Key ideas:
    1. Process each point independently with shared MLPs
    2. Use max pooling to get a global feature (permutation invariant)
    3. Classify from the global feature
    """
    def __init__(self, num_classes=40, num_points=1024):
        super().__init__()
        
        # Per-point feature extraction (shared MLP)
        self.mlp1 = nn.Sequential(
            nn.Linear(3, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Linear(128, 1024),
            nn.BatchNorm1d(1024),
            nn.ReLU()
        )
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(1024, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        """
        x: (batch, num_points, 3) -- point cloud
        Returns: (batch, num_classes) -- classification logits
        """
        batch_size, num_points, _ = x.shape
        
        # Process each point
        # Reshape for BatchNorm: (batch * num_points, 3)
        x = x.reshape(-1, 3)
        x = self.mlp1(x)  # (batch * num_points, 1024)
        x = x.reshape(batch_size, num_points, 1024)
        
        # Symmetric aggregation: max pooling over points
        x = x.max(dim=1)[0]  # (batch, 1024) -- global feature
        
        # Classify
        logits = self.classifier(x)
        return logits


class PointNetSegmentation(nn.Module):
    """
    PointNet for per-point segmentation.
    Each point gets a label by combining local and global features.
    """
    def __init__(self, num_classes=50):
        super().__init__()
        
        # Local features
        self.local_mlp = nn.Sequential(
            nn.Linear(3, 64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU()
        )
        
        # Global features
        self.global_mlp = nn.Sequential(
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Linear(256, 1024),
            nn.ReLU()
        )
        
        # Segmentation head (local + global concatenated)
        self.seg_head = nn.Sequential(
            nn.Linear(128 + 1024, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        """
        x: (batch, N, 3)
        Returns: (batch, N, num_classes) per-point logits
        """
        batch_size, num_points, _ = x.shape
        
        # Local features per point
        local_feats = self.local_mlp(x)  # (batch, N, 128)
        
        # Global feature
        global_input = local_feats.reshape(-1, 128)
        global_feats = self.global_mlp(global_input)  # (batch*N, 1024)
        global_feats = global_feats.reshape(batch_size, num_points, 1024)
        global_feats = global_feats.max(dim=1, keepdim=True)[0]  # (batch, 1, 1024)
        global_feats = global_feats.expand(-1, num_points, -1)   # (batch, N, 1024)
        
        # Concatenate local + global
        combined = torch.cat([local_feats, global_feats], dim=-1)  # (batch, N, 128+1024)
        
        # Per-point classification
        logits = self.seg_head(combined)  # (batch, N, num_classes)
        return logits
```

### 7.2 PointNet++ (Hierarchical Point Set Learning)

PointNet++ improves on PointNet by capturing local structure at multiple scales:

```python
class PointNetPlusPlus(nn.Module):
    """
    PointNet++ with set abstraction layers.
    Captures local geometric structures at progressively larger scales.
    """
    def __init__(self, num_classes=40):
        super().__init__()
        
        # Set Abstraction Level 1: 1024 -> 512 points
        self.sa1 = SetAbstractionLayer(
            n_points=512,    # Number of centroids
            radius=0.2,     # Ball query radius
            n_samples=32,   # Points per local region
            in_channels=3,
            mlp_channels=[64, 64, 128]
        )
        
        # Set Abstraction Level 2: 512 -> 128 points
        self.sa2 = SetAbstractionLayer(
            n_points=128,
            radius=0.4,
            n_samples=64,
            in_channels=128 + 3,
            mlp_channels=[128, 128, 256]
        )
        
        # Set Abstraction Level 3: 128 -> 1 point (global)
        self.sa3 = SetAbstractionLayer(
            n_points=1,
            radius=1.0,
            n_samples=128,
            in_channels=256 + 3,
            mlp_channels=[256, 512, 1024]
        )
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, xyz):
        """xyz: (batch, N, 3) point cloud"""
        # Progressively downsample and extract features
        xyz1, feat1 = self.sa1(xyz, None)    # (B, 512, 3), (B, 512, 128)
        xyz2, feat2 = self.sa2(xyz1, feat1)  # (B, 128, 3), (B, 128, 256)
        xyz3, feat3 = self.sa3(xyz2, feat2)  # (B, 1, 3),   (B, 1, 1024)
        
        global_feat = feat3.squeeze(1)  # (B, 1024)
        return self.classifier(global_feat)


class SetAbstractionLayer(nn.Module):
    """One level of PointNet++ hierarchy."""
    
    def __init__(self, n_points, radius, n_samples, in_channels, mlp_channels):
        super().__init__()
        self.n_points = n_points
        self.radius = radius
        self.n_samples = n_samples
        
        layers = []
        for out_ch in mlp_channels:
            layers.append(nn.Linear(in_channels, out_ch))
            layers.append(nn.ReLU())
            in_channels = out_ch
        self.mlp = nn.Sequential(*layers)
    
    def forward(self, xyz, features):
        """
        xyz: (B, N, 3) -- point positions
        features: (B, N, C) or None -- point features
        
        Returns:
            new_xyz: (B, n_points, 3) -- sampled centroids
            new_features: (B, n_points, mlp_channels[-1])
        """
        batch_size = xyz.shape[0]
        
        # Step 1: Farthest Point Sampling (select n_points centroids)
        centroid_indices = farthest_point_sample(xyz, self.n_points)
        new_xyz = gather_points(xyz, centroid_indices)  # (B, n_points, 3)
        
        # Step 2: Ball Query (find n_samples neighbors within radius)
        group_indices = ball_query(xyz, new_xyz, self.radius, self.n_samples)
        grouped_xyz = gather_points(xyz, group_indices)  # (B, n_points, n_samples, 3)
        
        # Normalize to local coordinates
        grouped_xyz = grouped_xyz - new_xyz.unsqueeze(2)
        
        # Concatenate with features if available
        if features is not None:
            grouped_features = gather_points(features, group_indices)
            grouped = torch.cat([grouped_xyz, grouped_features], dim=-1)
        else:
            grouped = grouped_xyz
        
        # Step 3: PointNet on each local region
        grouped = self.mlp(grouped)  # (B, n_points, n_samples, C_out)
        
        # Step 4: Max pool over neighbors
        new_features = grouped.max(dim=2)[0]  # (B, n_points, C_out)
        
        return new_xyz, new_features


def farthest_point_sample(xyz, n_points):
    """
    Farthest Point Sampling: iteratively select the point
    that is farthest from all previously selected points.
    Produces a well-distributed subset.
    """
    B, N, _ = xyz.shape
    centroids = torch.zeros(B, n_points, dtype=torch.long, device=xyz.device)
    distances = torch.ones(B, N, device=xyz.device) * 1e10
    
    # Start from a random point
    farthest = torch.randint(0, N, (B,), device=xyz.device)
    
    for i in range(n_points):
        centroids[:, i] = farthest
        
        # Distance from each point to the newly selected centroid
        centroid_pos = xyz[torch.arange(B), farthest].unsqueeze(1)  # (B, 1, 3)
        dist = torch.sum((xyz - centroid_pos) ** 2, dim=-1)          # (B, N)
        
        # Update minimum distances
        distances = torch.min(distances, dist)
        
        # Select the point with the largest minimum distance
        farthest = distances.argmax(dim=-1)
    
    return centroids
```

---

## 8. Text-to-3D Generation

### 8.1 Score Distillation Sampling (SDS)

DreamFusion (Poole et al., 2022) introduced Score Distillation Sampling, which enables text-to-3D generation using a pre-trained 2D text-to-image diffusion model (like Stable Diffusion) as a critic.

**The key insight**: You do not need 3D training data. Instead:
1. Maintain a 3D representation (NeRF or mesh)
2. Render it from random viewpoints
3. Use a pre-trained diffusion model to ask: "Does this rendering look like [text prompt]?"
4. Backpropagate the diffusion model's gradient through the differentiable renderer to update the 3D representation

```python
import torch
import torch.nn as nn
from diffusers import StableDiffusionPipeline

class ScoreDistillationSampling:
    """
    SDS loss for text-to-3D generation.
    Uses a frozen diffusion model to supervise 3D generation.
    """
    def __init__(self, prompt, guidance_scale=100.0, device="cuda"):
        self.device = device
        self.guidance_scale = guidance_scale
        
        # Load pre-trained diffusion model
        pipe = StableDiffusionPipeline.from_pretrained(
            "stabilityai/stable-diffusion-2-1-base",
            torch_dtype=torch.float16
        ).to(device)
        
        self.vae = pipe.vae
        self.unet = pipe.unet
        self.text_encoder = pipe.text_encoder
        self.tokenizer = pipe.tokenizer
        self.scheduler = pipe.scheduler
        
        # Freeze all diffusion model parameters
        for p in self.vae.parameters():
            p.requires_grad = False
        for p in self.unet.parameters():
            p.requires_grad = False
        for p in self.text_encoder.parameters():
            p.requires_grad = False
        
        # Encode the text prompt
        self.text_embeddings = self._encode_text(prompt)
        
        # Unconditional embeddings (for classifier-free guidance)
        self.uncond_embeddings = self._encode_text("")
    
    def _encode_text(self, prompt):
        tokens = self.tokenizer(
            prompt,
            padding="max_length",
            max_length=self.tokenizer.model_max_length,
            return_tensors="pt"
        ).input_ids.to(self.device)
        
        with torch.no_grad():
            embeddings = self.text_encoder(tokens)[0]
        return embeddings
    
    def compute_sds_loss(self, rendered_image):
        """
        Compute the SDS gradient for a rendered image.
        
        rendered_image: (1, 3, H, W) in [0, 1]
        Returns: scalar loss whose gradient updates the 3D model
        """
        # Encode image to latent space
        with torch.no_grad():
            latents = self.vae.encode(
                rendered_image * 2 - 1  # Scale to [-1, 1]
            ).latent_dist.sample() * 0.18215
        
        # Add noise at random timestep
        t = torch.randint(20, 980, (1,), device=self.device)
        noise = torch.randn_like(latents)
        noisy_latents = self.scheduler.add_noise(latents, noise, t)
        
        # Predict noise with classifier-free guidance
        with torch.no_grad():
            # Conditional prediction
            noise_pred_cond = self.unet(
                noisy_latents,
                t,
                encoder_hidden_states=self.text_embeddings
            ).sample
            
            # Unconditional prediction
            noise_pred_uncond = self.unet(
                noisy_latents,
                t,
                encoder_hidden_states=self.uncond_embeddings
            ).sample
            
            # Classifier-free guidance
            noise_pred = noise_pred_uncond + self.guidance_scale * (
                noise_pred_cond - noise_pred_uncond
            )
        
        # SDS gradient: difference between predicted noise and actual noise
        # This gradient tells the 3D model how to change so its renders
        # look more like the text prompt
        w = (1 - self.scheduler.alphas_cumprod[t])
        grad = w * (noise_pred - noise)
        
        # Create a loss whose gradient equals the SDS gradient
        loss = (latents * grad.detach()).sum()
        
        return loss


def text_to_3d_dreamfusion(prompt, n_iterations=10000):
    """
    Generate a 3D object from a text prompt using SDS.
    """
    device = torch.device("cuda")
    
    # 3D representation (simplified: using a neural implicit)
    model_3d = NeRF().to(device)
    
    # SDS loss
    sds = ScoreDistillationSampling(prompt, device=device)
    
    # Renderer
    renderer = NeRFRenderer(model_3d)
    
    optimizer = torch.optim.Adam(model_3d.parameters(), lr=1e-3)
    
    for iteration in range(n_iterations):
        # Random camera viewpoint
        theta = torch.rand(1) * 2 * 3.14159  # Random azimuth
        phi = torch.rand(1) * 0.5 + 0.25      # Elevation range
        radius = 2.0
        
        camera_pos = torch.tensor([
            radius * torch.sin(phi) * torch.cos(theta),
            radius * torch.cos(phi),
            radius * torch.sin(phi) * torch.sin(theta)
        ])
        
        c2w = look_at_matrix(camera_pos, target=torch.zeros(3))
        
        # Render from this viewpoint
        rendered = renderer.render_image(c2w, height=64, width=64)
        rendered = rendered.permute(2, 0, 1).unsqueeze(0)  # (1, 3, 64, 64)
        
        # Resize to diffusion model input size
        rendered = torch.nn.functional.interpolate(rendered, size=(512, 512))
        
        # SDS loss
        loss = sds.compute_sds_loss(rendered)
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if iteration % 500 == 0:
            print(f"Iteration {iteration}, SDS Loss: {loss.item():.4f}")
    
    return model_3d
```

### 8.2 Using Existing Text-to-3D Tools

```python
# --- Method 1: Using Shap-E (OpenAI) ---
# Shap-E directly generates 3D assets from text

import torch
from shap_e.diffusion.sample import sample_latents
from shap_e.diffusion.gaussian_diffusion import diffusion_from_config
from shap_e.models.download import load_model, load_config
from shap_e.util.notebooks import decode_latent_mesh

device = torch.device("cuda")

# Load model
xm = load_model("transmitter", device=device)
model = load_model("text300M", device=device)
diffusion = diffusion_from_config(load_config("diffusion"))

# Generate
prompt = "a red sports car"
latents = sample_latents(
    batch_size=1,
    model=model,
    diffusion=diffusion,
    guidance_scale=15.0,
    model_kwargs=dict(texts=[prompt]),
    progress=True,
    clip_denoised=True,
    use_fp16=True,
    use_karras=True,
    karras_steps=64,
    sigma_min=1e-3,
    sigma_max=160,
    s_churn=0,
)

# Decode to mesh
mesh = decode_latent_mesh(xm, latents[0]).tri_mesh()

# Save
with open("car.obj", "w") as f:
    mesh.write_obj(f)


# --- Method 2: Using InstantMesh (image-to-3D with text-to-image first) ---
# Step 1: Generate an image with Stable Diffusion
# Step 2: Use InstantMesh or other image-to-3D to get the 3D model

# --- Method 3: Using ThreeStudio (framework for text-to-3D) ---
# ThreeStudio supports DreamFusion, Magic3D, ProlificDreamer, etc.
# Install: pip install threestudio
# Run: python launch.py --config configs/dreamfusion-sd.yaml --train \
#        system.prompt_processor.prompt="a zoomed out DSLR photo of a baby bunny"
```

---

## 9. Image-to-3D Generation

### 9.1 Single-Image 3D Reconstruction

Given a single photograph, predict the 3D structure:

```python
import torch
import torch.nn as nn

class SingleImage3DReconstructor(nn.Module):
    """
    Predict a 3D mesh from a single image.
    
    Architecture:
    1. CNN encoder extracts image features
    2. Decoder predicts vertex positions of a template mesh
    """
    def __init__(self, template_vertices, template_faces, hidden_dim=512):
        super().__init__()
        self.template_vertices = template_vertices  # (V, 3)
        self.template_faces = template_faces
        n_vertices = template_vertices.shape[0]
        
        # Image encoder
        import torchvision.models as models
        resnet = models.resnet50(pretrained=True)
        self.encoder = nn.Sequential(*list(resnet.children())[:-1])
        
        # Vertex deformation predictor
        self.deform_head = nn.Sequential(
            nn.Linear(2048, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, n_vertices * 3),
            nn.Tanh()  # Bounded deformations
        )
        
        # Texture predictor (per-vertex RGB)
        self.texture_head = nn.Sequential(
            nn.Linear(2048, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, n_vertices * 3),
            nn.Sigmoid()  # Colors in [0, 1]
        )
    
    def forward(self, image):
        """
        image: (B, 3, 224, 224) input photograph
        Returns: deformed vertices (B, V, 3), vertex colors (B, V, 3)
        """
        features = self.encoder(image).flatten(1)  # (B, 2048)
        
        # Predict deformations
        deformations = self.deform_head(features)  # (B, V*3)
        deformations = deformations.reshape(-1, self.template_vertices.shape[0], 3)
        
        # Apply deformations to template
        vertices = self.template_vertices.unsqueeze(0) + deformations * 0.5
        
        # Predict texture
        colors = self.texture_head(features)
        colors = colors.reshape(-1, self.template_vertices.shape[0], 3)
        
        return vertices, colors


class DepthEstimator(nn.Module):
    """
    Monocular depth estimation from a single image.
    Predicts a depth map that can be unprojected to a 3D point cloud.
    """
    def __init__(self):
        super().__init__()
        
        # Using a U-Net style architecture
        # Encoder
        import torchvision.models as models
        resnet = models.resnet50(pretrained=True)
        self.encoder_layers = nn.ModuleList([
            nn.Sequential(resnet.conv1, resnet.bn1, resnet.relu, resnet.maxpool),
            resnet.layer1,
            resnet.layer2,
            resnet.layer3,
            resnet.layer4,
        ])
        
        # Decoder with skip connections
        self.decoder_layers = nn.ModuleList([
            self._up_block(2048, 1024),
            self._up_block(1024 + 1024, 512),
            self._up_block(512 + 512, 256),
            self._up_block(256 + 256, 128),
            self._up_block(128 + 64, 64),
        ])
        
        self.final = nn.Sequential(
            nn.Conv2d(64, 1, kernel_size=1),
            nn.Sigmoid()  # Depth in [0, 1]
        )
    
    def _up_block(self, in_ch, out_ch):
        return nn.Sequential(
            nn.ConvTranspose2d(in_ch, out_ch, kernel_size=2, stride=2),
            nn.BatchNorm2d(out_ch),
            nn.ReLU()
        )
    
    def forward(self, x):
        # Encoder
        skips = []
        for layer in self.encoder_layers:
            x = layer(x)
            skips.append(x)
        
        # Decoder with skip connections
        for i, layer in enumerate(self.decoder_layers):
            if i > 0:
                x = torch.cat([x, skips[-(i+1)]], dim=1)
            x = layer(x)
        
        depth = self.final(x)
        return depth


def depth_to_pointcloud(depth_map, intrinsics):
    """
    Unproject a depth map to a 3D point cloud.
    
    depth_map: (H, W) depth values
    intrinsics: camera intrinsic matrix (3, 3)
    """
    H, W = depth_map.shape
    
    # Create pixel coordinate grid
    u, v = torch.meshgrid(
        torch.arange(W, dtype=torch.float32),
        torch.arange(H, dtype=torch.float32),
        indexing='xy'
    )
    
    # Unproject
    fx, fy = intrinsics[0, 0], intrinsics[1, 1]
    cx, cy = intrinsics[0, 2], intrinsics[1, 2]
    
    z = depth_map
    x = (u - cx) * z / fx
    y = (v - cy) * z / fy
    
    points = torch.stack([x, y, z], dim=-1)  # (H, W, 3)
    points = points.reshape(-1, 3)
    
    # Filter out invalid depth values
    valid = z.reshape(-1) > 0
    points = points[valid]
    
    return points
```

### 9.2 Using Pre-trained Models for Image-to-3D

```python
# --- Using MiDaS for Monocular Depth ---
import torch

# Load MiDaS
model_type = "DPT_Large"
midas = torch.hub.load("intel-isl/MiDaS", model_type)
midas.eval().cuda()

# Load transforms
midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
transform = midas_transforms.dpt_transform

# Predict depth
import cv2
img = cv2.imread("photo.jpg")
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
input_batch = transform(img_rgb).cuda()

with torch.no_grad():
    depth_prediction = midas(input_batch)
    depth_prediction = torch.nn.functional.interpolate(
        depth_prediction.unsqueeze(1),
        size=img_rgb.shape[:2],
        mode="bicubic",
        align_corners=False,
    ).squeeze()

depth_map = depth_prediction.cpu().numpy()


# --- Using TripoSR for single-image 3D reconstruction ---
# TripoSR (Stability AI) generates 3D meshes from single images
# pip install triposr
from triposr import TripoSR

model = TripoSR.from_pretrained("stabilityai/TripoSR")
mesh = model.generate("input_image.png")
mesh.export("output.glb")


# --- Using Zero123++ for multi-view generation ---
# Generates multiple views of an object from a single image
# Then use multi-view reconstruction to get 3D
```

---

## 10. 3D-Aware Image Synthesis

### 10.1 EG3D (Efficient Geometry-aware 3D GANs)

EG3D combines a GAN with an explicit 3D representation (tri-plane) to generate 3D-consistent images:

```python
class TriPlaneGenerator(nn.Module):
    """
    Tri-plane representation: represent 3D volume using three axis-aligned feature planes.
    Much more memory-efficient than full 3D voxel grids.
    
    Instead of storing features in a W x H x D volume (O(n^3)),
    store three W x H planes (XY, XZ, YZ) giving O(n^2) memory.
    """
    def __init__(self, plane_resolution=256, feature_dim=32):
        super().__init__()
        
        # StyleGAN2 backbone generates three feature planes
        self.plane_resolution = plane_resolution
        self.feature_dim = feature_dim
        
        # Generator produces 3 planes concatenated
        self.backbone = StyleGAN2Generator(
            output_channels=feature_dim * 3,
            output_resolution=plane_resolution
        )
        
        # Neural renderer: converts features to color + density
        self.decoder = nn.Sequential(
            nn.Linear(feature_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 4)  # RGB + density
        )
    
    def query_triplane(self, planes, points):
        """
        Query tri-plane features at 3D points.
        
        planes: three (B, C, H, W) feature planes
        points: (B, N, 3) query positions in [-1, 1]
        
        Returns: (B, N, C) aggregated features
        """
        xy_plane, xz_plane, yz_plane = planes
        
        # Project points to each plane and sample features
        # XY plane: use (x, y)
        xy_coords = points[:, :, :2]  # (B, N, 2)
        xy_features = torch.nn.functional.grid_sample(
            xy_plane,
            xy_coords.unsqueeze(1),  # (B, 1, N, 2)
            align_corners=True
        ).squeeze(2).permute(0, 2, 1)  # (B, N, C)
        
        # XZ plane: use (x, z)
        xz_coords = points[:, :, [0, 2]]
        xz_features = torch.nn.functional.grid_sample(
            xz_plane,
            xz_coords.unsqueeze(1),
            align_corners=True
        ).squeeze(2).permute(0, 2, 1)
        
        # YZ plane: use (y, z)
        yz_coords = points[:, :, [1, 2]]
        yz_features = torch.nn.functional.grid_sample(
            yz_plane,
            yz_coords.unsqueeze(1),
            align_corners=True
        ).squeeze(2).permute(0, 2, 1)
        
        # Aggregate: sum features from all three planes
        features = xy_features + xz_features + yz_features
        
        return features
    
    def forward(self, z, camera_params):
        """
        z: (B, latent_dim) -- random latent code
        camera_params: camera intrinsics + extrinsics
        Returns: (B, 3, H, W) rendered image
        """
        # Generate tri-plane features
        raw_planes = self.backbone(z)  # (B, C*3, H, W)
        planes = torch.chunk(raw_planes, 3, dim=1)  # 3 x (B, C, H, W)
        
        # Cast rays from camera
        rays_o, rays_d = get_camera_rays(camera_params)
        
        # Sample points along rays
        points = sample_along_rays(rays_o, rays_d)  # (B, N_rays, N_samples, 3)
        
        # Query features
        B, N_rays, N_samples, _ = points.shape
        flat_points = points.reshape(B, -1, 3)
        features = self.query_triplane(planes, flat_points)
        
        # Decode to color + density
        rgba = self.decoder(features)
        colors = torch.sigmoid(rgba[:, :, :3])
        density = torch.relu(rgba[:, :, 3:])
        
        # Volume render
        colors = colors.reshape(B, N_rays, N_samples, 3)
        density = density.reshape(B, N_rays, N_samples, 1)
        rendered = volume_render_batch(colors, density)
        
        return rendered
```

---

## 11. Physics-Based Simulation with ML

### 11.1 Learning Physics Simulations

Neural networks can learn to simulate physical systems (fluids, cloth, rigid bodies) much faster than traditional solvers:

```python
import torch
import torch.nn as nn

class GraphNetworkSimulator(nn.Module):
    """
    Graph Neural Network for learning physics simulations.
    (Based on "Learning to Simulate Complex Physics with Graph Networks")
    
    Represents particles/nodes as a graph and learns the dynamics.
    """
    def __init__(self, node_dim=9, edge_dim=3, hidden_dim=128, num_message_passing=10):
        super().__init__()
        
        # Node encoder: position, velocity, node type -> hidden
        self.node_encoder = nn.Sequential(
            nn.Linear(node_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        
        # Edge encoder: relative position, distance -> hidden
        self.edge_encoder = nn.Sequential(
            nn.Linear(edge_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        
        # Message passing layers
        self.message_layers = nn.ModuleList([
            MessagePassingLayer(hidden_dim) for _ in range(num_message_passing)
        ])
        
        # Decoder: hidden -> acceleration
        self.decoder = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 3)  # 3D acceleration
        )
    
    def forward(self, node_features, edge_index, edge_features):
        """
        Predict accelerations for all particles.
        
        node_features: (N, node_dim) -- pos, vel, type for each particle
        edge_index: (2, E) -- connectivity
        edge_features: (E, edge_dim) -- relative positions
        
        Returns: (N, 3) -- predicted accelerations
        """
        # Encode
        node_h = self.node_encoder(node_features)
        edge_h = self.edge_encoder(edge_features)
        
        # Message passing
        for mp_layer in self.message_layers:
            node_h, edge_h = mp_layer(node_h, edge_h, edge_index)
        
        # Decode accelerations
        accelerations = self.decoder(node_h)
        
        return accelerations


class MessagePassingLayer(nn.Module):
    def __init__(self, hidden_dim):
        super().__init__()
        self.edge_mlp = nn.Sequential(
            nn.Linear(hidden_dim * 3, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        self.node_mlp = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
    
    def forward(self, node_h, edge_h, edge_index):
        src, dst = edge_index
        
        # Update edges: combine sender, receiver, and edge features
        edge_input = torch.cat([node_h[src], node_h[dst], edge_h], dim=-1)
        edge_h = edge_h + self.edge_mlp(edge_input)
        
        # Aggregate messages to nodes (sum)
        aggregated = torch.zeros_like(node_h)
        aggregated.index_add_(0, dst, edge_h)
        
        # Update nodes
        node_input = torch.cat([node_h, aggregated], dim=-1)
        node_h = node_h + self.node_mlp(node_input)
        
        return node_h, edge_h
```

### 11.2 Differentiable Physics

```python
class DifferentiableRigidBody:
    """
    A simple differentiable rigid body simulator.
    All operations are differentiable, allowing gradient-based optimization
    of physical parameters or control inputs.
    """
    def __init__(self, mass=1.0, dt=0.01):
        self.mass = mass
        self.dt = dt
    
    def step(self, position, velocity, force, gravity=torch.tensor([0., -9.81, 0.])):
        """
        One simulation step (semi-implicit Euler integration).
        All inputs/outputs are differentiable tensors.
        """
        # Acceleration = Force / Mass + Gravity
        acceleration = force / self.mass + gravity
        
        # Semi-implicit Euler: update velocity first, then position
        new_velocity = velocity + acceleration * self.dt
        new_position = position + new_velocity * self.dt
        
        return new_position, new_velocity
    
    def simulate(self, initial_pos, initial_vel, forces, n_steps):
        """
        Run simulation for n_steps.
        forces: (n_steps, 3) -- external force at each timestep
        """
        trajectory = [initial_pos]
        pos = initial_pos
        vel = initial_vel
        
        for t in range(n_steps):
            pos, vel = self.step(pos, vel, forces[t])
            trajectory.append(pos)
        
        return torch.stack(trajectory)  # (n_steps + 1, 3)


# Example: optimize initial velocity to hit a target
def optimize_trajectory():
    target = torch.tensor([5.0, 0.0, 0.0])
    initial_pos = torch.tensor([0.0, 0.0, 0.0])
    
    # Learnable initial velocity
    initial_vel = torch.tensor([1.0, 5.0, 0.0], requires_grad=True)
    
    sim = DifferentiableRigidBody()
    optimizer = torch.optim.Adam([initial_vel], lr=0.1)
    
    for i in range(200):
        forces = torch.zeros(100, 3)  # No external forces
        trajectory = sim.simulate(initial_pos, initial_vel, forces, 100)
        
        # Loss: distance from final position to target
        final_pos = trajectory[-1]
        loss = ((final_pos - target) ** 2).sum()
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if i % 20 == 0:
            print(f"Step {i}, Loss: {loss.item():.4f}, Vel: {initial_vel.data}")
```

---

## 12. Texture and Material Generation

### 12.1 Texture Synthesis with Neural Networks

```python
import torch
import torch.nn as nn
import torchvision.models as models

class NeuralTextureTransfer:
    """
    Transfer texture from a source image to a target 3D shape.
    Based on neural style transfer adapted for textures.
    """
    def __init__(self, device="cuda"):
        self.device = device
        
        # Use VGG features for texture matching
        vgg = models.vgg19(pretrained=True).features.to(device).eval()
        
        self.feature_layers = {
            '3': 'relu1_2',
            '8': 'relu2_2',
            '17': 'relu3_4',
            '26': 'relu4_4',
        }
        
        self.model = vgg
        for p in self.model.parameters():
            p.requires_grad = False
    
    def extract_features(self, image):
        """Extract multi-scale features for texture matching."""
        features = {}
        x = image
        for name, layer in self.model._modules.items():
            x = layer(x)
            if name in self.feature_layers:
                features[self.feature_layers[name]] = x
        return features
    
    def gram_matrix(self, features):
        """
        Gram matrix captures texture statistics.
        G_ij = sum_k F_ik * F_jk (correlation between feature channels)
        """
        B, C, H, W = features.shape
        F = features.reshape(B, C, -1)       # (B, C, H*W)
        G = torch.bmm(F, F.transpose(1, 2))  # (B, C, C)
        G = G / (C * H * W)
        return G
    
    def texture_loss(self, source_image, generated_image):
        """Compute texture similarity between source and generated images."""
        source_features = self.extract_features(source_image)
        generated_features = self.extract_features(generated_image)
        
        loss = 0
        for layer_name in self.feature_layers.values():
            source_gram = self.gram_matrix(source_features[layer_name])
            generated_gram = self.gram_matrix(generated_features[layer_name])
            loss += nn.functional.mse_loss(generated_gram, source_gram)
        
        return loss


class PBRMaterialGenerator(nn.Module):
    """
    Generate Physically Based Rendering (PBR) materials.
    Produces: albedo (color), normal map, roughness, metallic maps.
    """
    def __init__(self, latent_dim=256):
        super().__init__()
        
        self.latent_dim = latent_dim
        
        # Shared encoder
        self.backbone = nn.Sequential(
            nn.ConvTranspose2d(latent_dim, 512, 4, 1, 0),
            nn.BatchNorm2d(512), nn.ReLU(),
            nn.ConvTranspose2d(512, 256, 4, 2, 1),
            nn.BatchNorm2d(256), nn.ReLU(),
            nn.ConvTranspose2d(256, 128, 4, 2, 1),
            nn.BatchNorm2d(128), nn.ReLU(),
            nn.ConvTranspose2d(128, 64, 4, 2, 1),
            nn.BatchNorm2d(64), nn.ReLU(),
        )
        
        # Separate heads for each PBR channel
        self.albedo_head = nn.Sequential(
            nn.ConvTranspose2d(64, 3, 4, 2, 1),
            nn.Sigmoid()  # Color in [0, 1]
        )
        
        self.normal_head = nn.Sequential(
            nn.ConvTranspose2d(64, 3, 4, 2, 1),
            nn.Tanh()  # Normal components in [-1, 1]
        )
        
        self.roughness_head = nn.Sequential(
            nn.ConvTranspose2d(64, 1, 4, 2, 1),
            nn.Sigmoid()  # Roughness in [0, 1]
        )
        
        self.metallic_head = nn.Sequential(
            nn.ConvTranspose2d(64, 1, 4, 2, 1),
            nn.Sigmoid()  # Metallic in [0, 1]
        )
    
    def forward(self, z):
        """
        z: (B, latent_dim) random noise
        Returns: dict of PBR maps, each (B, C, H, W)
        """
        z = z.reshape(-1, self.latent_dim, 1, 1)
        features = self.backbone(z)
        
        return {
            'albedo': self.albedo_head(features),
            'normal': self.normal_head(features),
            'roughness': self.roughness_head(features),
            'metallic': self.metallic_head(features),
        }
```

---

## 13. Animation and Motion Generation

### 13.1 Human Motion Generation

```python
import torch
import torch.nn as nn

class MotionDiffusionModel(nn.Module):
    """
    Text-to-motion generation using diffusion.
    Generates sequences of human poses from text descriptions.
    
    Based on MDM (Motion Diffusion Model).
    """
    def __init__(
        self,
        n_joints=22,
        joint_dim=3,        # 3D position per joint
        n_frames=196,       # Sequence length
        d_model=512,
        n_heads=8,
        n_layers=8,
        text_dim=512
    ):
        super().__init__()
        
        self.n_joints = n_joints
        self.joint_dim = joint_dim
        self.motion_dim = n_joints * joint_dim  # Flattened per-frame
        
        # Motion embedding
        self.motion_embed = nn.Linear(self.motion_dim, d_model)
        
        # Timestep embedding
        self.time_embed = nn.Sequential(
            nn.Linear(1, d_model),
            nn.SiLU(),
            nn.Linear(d_model, d_model)
        )
        
        # Text encoder (frozen CLIP or learned)
        self.text_encoder = nn.Sequential(
            nn.Linear(text_dim, d_model),
            nn.ReLU(),
            nn.Linear(d_model, d_model)
        )
        
        # Positional encoding for temporal dimension
        self.pos_encoding = nn.Parameter(torch.randn(1, n_frames, d_model) * 0.02)
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=d_model * 4,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
        
        # Output projection
        self.output_proj = nn.Linear(d_model, self.motion_dim)
    
    def forward(self, noisy_motion, timestep, text_embedding):
        """
        Predict the noise to remove from noisy motion.
        
        noisy_motion: (B, T, n_joints * joint_dim) -- noised motion sequence
        timestep: (B, 1) -- diffusion timestep
        text_embedding: (B, text_dim) -- encoded text prompt
        
        Returns: (B, T, n_joints * joint_dim) -- predicted noise
        """
        B, T, _ = noisy_motion.shape
        
        # Embed motion
        motion_h = self.motion_embed(noisy_motion)  # (B, T, d_model)
        
        # Add positional encoding
        motion_h = motion_h + self.pos_encoding[:, :T, :]
        
        # Embed timestep
        t_emb = self.time_embed(timestep.float())  # (B, d_model)
        
        # Embed text
        text_h = self.text_encoder(text_embedding)  # (B, d_model)
        
        # Prepend text and timestep tokens
        condition_tokens = torch.stack([t_emb, text_h], dim=1)  # (B, 2, d_model)
        full_sequence = torch.cat([condition_tokens, motion_h], dim=1)  # (B, T+2, d_model)
        
        # Transformer
        output = self.transformer(full_sequence)  # (B, T+2, d_model)
        
        # Take only the motion part
        motion_output = output[:, 2:, :]  # (B, T, d_model)
        
        # Project to motion space
        predicted_noise = self.output_proj(motion_output)  # (B, T, motion_dim)
        
        return predicted_noise


def generate_motion(model, text_prompt, n_frames=196, n_diffusion_steps=1000):
    """Generate a motion sequence from text."""
    device = next(model.parameters()).device
    
    # Encode text (using CLIP or similar)
    text_embedding = encode_text(text_prompt).to(device)  # (1, text_dim)
    
    # Start from random noise
    motion = torch.randn(1, n_frames, model.motion_dim).to(device)
    
    # Iteratively denoise
    for t in reversed(range(n_diffusion_steps)):
        timestep = torch.tensor([[t]], device=device)
        
        with torch.no_grad():
            predicted_noise = model(motion, timestep, text_embedding)
        
        # DDPM update step
        motion = denoise_step(motion, predicted_noise, t, n_diffusion_steps)
    
    # Reshape to (n_frames, n_joints, 3)
    motion = motion.reshape(n_frames, model.n_joints, model.joint_dim)
    
    return motion.cpu().numpy()
```

### 13.2 Skeletal Animation Basics

```python
import numpy as np

class Skeleton:
    """
    Hierarchical skeleton for character animation.
    """
    def __init__(self):
        # Define joint hierarchy (parent of each joint)
        # -1 means root (no parent)
        self.joint_names = [
            "Hips",           # 0 - root
            "Spine",          # 1
            "Spine1",         # 2
            "Spine2",         # 3
            "Neck",           # 4
            "Head",           # 5
            "LeftShoulder",   # 6
            "LeftArm",        # 7
            "LeftForeArm",    # 8
            "LeftHand",       # 9
            "RightShoulder",  # 10
            "RightArm",       # 11
            "RightForeArm",   # 12
            "RightHand",      # 13
            "LeftUpLeg",      # 14
            "LeftLeg",        # 15
            "LeftFoot",       # 16
            "RightUpLeg",     # 17
            "RightLeg",       # 18
            "RightFoot",      # 19
        ]
        
        self.parents = [
            -1,  # Hips (root)
            0,   # Spine -> Hips
            1,   # Spine1 -> Spine
            2,   # Spine2 -> Spine1
            3,   # Neck -> Spine2
            4,   # Head -> Neck
            3,   # LeftShoulder -> Spine2
            6,   # LeftArm -> LeftShoulder
            7,   # LeftForeArm -> LeftArm
            8,   # LeftHand -> LeftForeArm
            3,   # RightShoulder -> Spine2
            10,  # RightArm -> RightShoulder
            11,  # RightForeArm -> RightArm
            12,  # RightHand -> RightForeArm
            0,   # LeftUpLeg -> Hips
            14,  # LeftLeg -> LeftUpLeg
            15,  # LeftFoot -> LeftLeg
            0,   # RightUpLeg -> Hips
            17,  # RightLeg -> RightUpLeg
            18,  # RightFoot -> RightLeg
        ]
    
    def forward_kinematics(self, local_rotations, root_position):
        """
        Compute global joint positions from local rotations.
        
        local_rotations: (n_joints, 3, 3) rotation matrices
        root_position: (3,) root translation
        
        Returns: (n_joints, 3) global joint positions
        """
        n_joints = len(self.parents)
        global_rotations = np.zeros((n_joints, 3, 3))
        global_positions = np.zeros((n_joints, 3))
        
        for j in range(n_joints):
            if self.parents[j] == -1:
                # Root joint
                global_rotations[j] = local_rotations[j]
                global_positions[j] = root_position
            else:
                parent = self.parents[j]
                global_rotations[j] = global_rotations[parent] @ local_rotations[j]
                
                # Position = parent position + rotated bone offset
                bone_offset = self.bone_offsets[j]  # Rest-pose offset
                global_positions[j] = (
                    global_positions[parent] + 
                    global_rotations[parent] @ bone_offset
                )
        
        return global_positions
```

---

## 14. Practical Projects

### Project 1: 3D Reconstruction from Phone Photos

```bash
# Step 1: Take 30-50 photos of an object from different angles
# - Overlap between consecutive photos: 60-70%
# - Cover all sides
# - Good lighting, no motion blur

# Step 2: Install tools
pip install nerfstudio
pip install colmap  # or install via system package manager

# Step 3: Process images
ns-process-data images --data ./my_photos/

# Step 4: Train (choose one)
ns-train nerfacto --data ./my_photos/    # Balanced quality/speed
ns-train instant-ngp --data ./my_photos/ # Fastest
ns-train splatfacto --data ./my_photos/  # Gaussian Splatting

# Step 5: Export mesh
ns-export poisson --load-config outputs/config.yml --output-dir ./export/

# Step 6: View/edit in Blender or MeshLab
```

### Project 2: Text-to-3D Asset Generation Pipeline

```python
"""
Complete pipeline: Text -> Image -> 3D Model -> Textured Mesh
"""
from diffusers import StableDiffusionPipeline
import torch

def text_to_3d_pipeline(prompt):
    # Step 1: Generate reference images from text
    pipe = StableDiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=torch.float16
    ).to("cuda")
    
    # Generate from multiple viewpoints via prompt engineering
    views = ["front view", "side view", "back view", "top view"]
    images = []
    for view in views:
        full_prompt = f"{prompt}, {view}, white background, product photography"
        image = pipe(full_prompt, num_inference_steps=30).images[0]
        images.append(image)
        image.save(f"view_{view.replace(' ', '_')}.png")
    
    # Step 2: Use image-to-3D model
    # Option A: TripoSR
    # Option B: InstantMesh
    # Option C: Gaussian Splatting from multi-view
    
    # Step 3: Clean up mesh
    import trimesh
    mesh = trimesh.load("output.obj")
    
    # Remove small disconnected components
    components = mesh.split(only_watertight=False)
    largest = max(components, key=lambda m: m.area)
    
    # Simplify (reduce polygon count)
    simplified = largest.simplify_quadric_decimation(target_faces=10000)
    
    # Center and normalize
    simplified.vertices -= simplified.centroid
    scale = simplified.vertices.max() - simplified.vertices.min()
    simplified.vertices /= scale
    
    simplified.export("final_model.glb")
    
    return simplified

# Run the pipeline
mesh = text_to_3d_pipeline("a medieval castle tower")
```

---

## 15. Summary and Key Takeaways

This chapter covered the rapidly evolving field of 3D generation with AI:

1. **3D representations**: Meshes, point clouds, voxels, SDFs, neural implicits -- each with different trade-offs in memory, quality, and compatibility with learning.

2. **Classical reconstruction**: SfM and MVS remain the foundation for obtaining camera poses and initial 3D structure from images.

3. **NeRF**: Represents scenes as neural networks mapping (position, direction) -> (color, density). Produces stunning novel views but is slow to train and render.

4. **3D Gaussian Splatting**: Represents scenes as millions of 3D Gaussians. Achieves real-time rendering with quality comparable to NeRF, while training in minutes.

5. **Mesh generation**: DeepSDF learns shape priors, differentiable rendering enables gradient-based mesh optimization.

6. **Point cloud networks**: PointNet and PointNet++ process unstructured 3D point data for classification and segmentation.

7. **Text-to-3D**: Score Distillation Sampling uses pre-trained 2D diffusion models to guide 3D generation from text prompts.

8. **Image-to-3D**: Monocular depth estimation and learned reconstruction networks generate 3D from single images.

9. **Physics simulation**: Graph neural networks and differentiable physics enable fast, learnable simulations.

10. **Animation**: Motion diffusion models generate realistic human motion from text descriptions.

11. **Practical pipeline**: Transfer learning, data augmentation, inference.

---

[<< Previous: Chapter 10 - Generative Models](./10_GENERATIVE_MODELS.md) | [Next: Chapter 12 - Reinforcement Learning >>](./12_REINFORCEMENT_LEARNING.md)
