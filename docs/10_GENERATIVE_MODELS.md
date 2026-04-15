# Chapter 10: Generative Models

## Introduction

Generative models learn the underlying distribution of data and can create new, realistic samples. This chapter covers the major generative model families: Variational Autoencoders (VAEs), Generative Adversarial Networks (GANs), and Diffusion Models. These are the architectures behind image generation (DALL-E, Stable Diffusion, Midjourney), video generation, music generation, and more.

---

## Table of Contents

1. Discriminative vs Generative Models
2. Autoencoders
3. Variational Autoencoders (VAEs)
4. Generative Adversarial Networks (GANs)
5. GAN Variants (DCGAN, WGAN, StyleGAN)
6. Conditional Generation
7. Diffusion Models: The Theory
8. Denoising Diffusion Probabilistic Models (DDPM)
9. Building a Diffusion Model from Scratch
10. Classifier-Free Guidance
11. Latent Diffusion and Stable Diffusion
12. Image-to-Image Generation
13. Text-to-Image Generation
14. Audio Generation
15. Evaluation of Generative Models
16. Summary

---

## 1. Discriminative vs Generative Models

**Discriminative models** learn the boundary between classes: $P(y|x)$ -- "Given this image, is it a cat or dog?"

**Generative models** learn the data distribution itself: $P(x)$ -- "What does a cat look like?" Then they can sample from this distribution to create new data.

Both have uses. Classification needs discriminative models. Creating new content needs generative models.

---

## 2. Autoencoders

An autoencoder compresses data into a lower-dimensional representation (encoding) and then reconstructs it (decoding). It is not generative by itself, but it is the foundation for VAEs.

```
Input image (784 dim) --> Encoder --> Latent code (32 dim) --> Decoder --> Reconstructed image (784 dim)
```

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

class Autoencoder(nn.Module):
    """Simple autoencoder for MNIST."""
    
    def __init__(self, latent_dim=32):
        super().__init__()
        
        # Encoder: 784 -> 256 -> 128 -> latent_dim
        self.encoder = nn.Sequential(
            nn.Linear(784, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, latent_dim)
        )
        
        # Decoder: latent_dim -> 128 -> 256 -> 784
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Linear(256, 784),
            nn.Sigmoid()  # Output between 0 and 1
        )
    
    def forward(self, x):
        z = self.encoder(x)
        reconstructed = self.decoder(z)
        return reconstructed, z


# Training
def train_autoencoder(model, dataloader, epochs=20):
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    
    for epoch in range(epochs):
        total_loss = 0
        for batch_x, _ in dataloader:
            batch_x = batch_x.view(-1, 784)
            
            reconstructed, _ = model(batch_x)
            loss = F.mse_loss(reconstructed, batch_x)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        print(f"Epoch {epoch+1}, Loss: {total_loss/len(dataloader):.4f}")
```

The problem with standard autoencoders for generation: the latent space is not structured. Random points in latent space may decode to noise.

---

## 3. Variational Autoencoders (VAEs)

VAEs solve the latent space problem by forcing the encoder to produce distributions (mean and variance) rather than point estimates, and adding a regularization term that pushes these distributions toward a standard normal distribution.

### The Key Insight

Instead of encoding an input to a single point in latent space, the encoder outputs a mean $\mu$ and standard deviation $\sigma$, defining a Gaussian distribution. We sample from this distribution and decode the sample.

### The Reparameterization Trick

We cannot backpropagate through random sampling. The trick: instead of sampling $z \sim \mathcal{N}(\mu, \sigma^2)$, sample $\epsilon \sim \mathcal{N}(0, 1)$ and compute $z = \mu + \sigma \cdot \epsilon$. This is differentiable with respect to $\mu$ and $\sigma$.

### Loss Function

$$\mathcal{L} = \underbrace{\mathbb{E}[\|x - \hat{x}\|^2]}_{\text{Reconstruction Loss}} + \underbrace{\beta \cdot D_{KL}(\mathcal{N}(\mu, \sigma^2) \| \mathcal{N}(0, I))}_{\text{KL Divergence}}$$

The KL divergence has a closed form:

$$D_{KL} = -\frac{1}{2} \sum_{j=1}^{d} (1 + \log(\sigma_j^2) - \mu_j^2 - \sigma_j^2)$$

```python
class VAE(nn.Module):
    """Variational Autoencoder for image generation."""
    
    def __init__(self, input_dim=784, hidden_dim=256, latent_dim=32):
        super().__init__()
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )
        
        # Latent space parameters
        self.fc_mu = nn.Linear(hidden_dim, latent_dim)
        self.fc_logvar = nn.Linear(hidden_dim, latent_dim)
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim),
            nn.Sigmoid()
        )
    
    def encode(self, x):
        h = self.encoder(x)
        mu = self.fc_mu(h)
        logvar = self.fc_logvar(h)
        return mu, logvar
    
    def reparameterize(self, mu, logvar):
        """Reparameterization trick: z = mu + sigma * epsilon."""
        std = torch.exp(0.5 * logvar)  # sigma = exp(0.5 * log(sigma^2))
        eps = torch.randn_like(std)     # epsilon ~ N(0, 1)
        return mu + std * eps
    
    def decode(self, z):
        return self.decoder(z)
    
    def forward(self, x):
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        reconstructed = self.decode(z)
        return reconstructed, mu, logvar
    
    @torch.no_grad()
    def generate(self, num_samples, device="cpu"):
        """Generate new samples by sampling from the prior."""
        z = torch.randn(num_samples, self.fc_mu.out_features).to(device)
        samples = self.decode(z)
        return samples


def vae_loss(reconstructed, original, mu, logvar, beta=1.0):
    """VAE loss = reconstruction + beta * KL divergence."""
    # Reconstruction loss (binary cross-entropy for images with pixel values in [0,1])
    recon_loss = F.binary_cross_entropy(reconstructed, original, reduction="sum")
    
    # KL divergence
    kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
    
    return recon_loss + beta * kl_loss


# Training
def train_vae(model, dataloader, epochs=50, beta=1.0):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    
    for epoch in range(epochs):
        total_loss = 0
        for batch_x, _ in dataloader:
            batch_x = batch_x.view(-1, 784).to(device)
            
            reconstructed, mu, logvar = model(batch_x)
            loss = vae_loss(reconstructed, batch_x, mu, logvar, beta)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        avg_loss = total_loss / len(dataloader.dataset)
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}, Loss: {avg_loss:.4f}")
    
    return model
```

### Convolutional VAE

For higher quality image generation, use convolutional layers:

```python
class ConvVAE(nn.Module):
    """Convolutional VAE for 64x64 images."""
    
    def __init__(self, latent_dim=128, channels=3):
        super().__init__()
        self.latent_dim = latent_dim
        
        # Encoder
        self.encoder = nn.Sequential(
            # 64x64 -> 32x32
            nn.Conv2d(channels, 32, 4, 2, 1),
            nn.BatchNorm2d(32),
            nn.LeakyReLU(0.2),
            # 32x32 -> 16x16
            nn.Conv2d(32, 64, 4, 2, 1),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(0.2),
            # 16x16 -> 8x8
            nn.Conv2d(64, 128, 4, 2, 1),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2),
            # 8x8 -> 4x4
            nn.Conv2d(128, 256, 4, 2, 1),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2),
        )
        
        self.fc_mu = nn.Linear(256 * 4 * 4, latent_dim)
        self.fc_logvar = nn.Linear(256 * 4 * 4, latent_dim)
        
        # Decoder
        self.fc_decode = nn.Linear(latent_dim, 256 * 4 * 4)
        
        self.decoder = nn.Sequential(
            # 4x4 -> 8x8
            nn.ConvTranspose2d(256, 128, 4, 2, 1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            # 8x8 -> 16x16
            nn.ConvTranspose2d(128, 64, 4, 2, 1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            # 16x16 -> 32x32
            nn.ConvTranspose2d(64, 32, 4, 2, 1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            # 32x32 -> 64x64
            nn.ConvTranspose2d(32, channels, 4, 2, 1),
            nn.Tanh()
        )
    
    def encode(self, x):
        h = self.encoder(x)
        h = h.view(h.size(0), -1)
        return self.fc_mu(h), self.fc_logvar(h)
    
    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + std * eps
    
    def decode(self, z):
        h = self.fc_decode(z)
        h = h.view(-1, 256, 4, 4)
        return self.decoder(h)
    
    def forward(self, x):
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        return self.decode(z), mu, logvar
```

---

## 4. Generative Adversarial Networks (GANs)

GANs consist of two neural networks that compete against each other:

- **Generator (G)**: Creates fake data from random noise.
- **Discriminator (D)**: Tries to distinguish real data from fake data.

They play a minimax game:

$$\min_G \max_D \mathbb{E}_{x \sim p_{\text{data}}}[\log D(x)] + \mathbb{E}_{z \sim p_z}[\log(1 - D(G(z)))]$$

The generator tries to fool the discriminator. The discriminator tries to not be fooled. As training progresses, the generator produces increasingly realistic data.

```python
class Generator(nn.Module):
    """Generator: maps random noise to images."""
    
    def __init__(self, latent_dim=100, img_dim=784):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(latent_dim, 256),
            nn.LeakyReLU(0.2),
            nn.BatchNorm1d(256),
            nn.Linear(256, 512),
            nn.LeakyReLU(0.2),
            nn.BatchNorm1d(512),
            nn.Linear(512, 1024),
            nn.LeakyReLU(0.2),
            nn.BatchNorm1d(1024),
            nn.Linear(1024, img_dim),
            nn.Tanh()  # Output in [-1, 1]
        )
    
    def forward(self, z):
        return self.net(z)


class Discriminator(nn.Module):
    """Discriminator: classifies images as real or fake."""
    
    def __init__(self, img_dim=784):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(img_dim, 512),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        return self.net(x)


def train_gan(generator, discriminator, dataloader, latent_dim=100, 
              epochs=200, lr=2e-4):
    """Train a GAN."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    generator = generator.to(device)
    discriminator = discriminator.to(device)
    
    criterion = nn.BCELoss()
    
    opt_G = torch.optim.Adam(generator.parameters(), lr=lr, betas=(0.5, 0.999))
    opt_D = torch.optim.Adam(discriminator.parameters(), lr=lr, betas=(0.5, 0.999))
    
    for epoch in range(epochs):
        for real_imgs, _ in dataloader:
            batch_size = real_imgs.size(0)
            real_imgs = real_imgs.view(batch_size, -1).to(device)
            
            # Labels
            real_labels = torch.ones(batch_size, 1).to(device)
            fake_labels = torch.zeros(batch_size, 1).to(device)
            
            # ---------------------
            # Train Discriminator
            # ---------------------
            # Real images
            real_pred = discriminator(real_imgs)
            d_loss_real = criterion(real_pred, real_labels)
            
            # Fake images
            z = torch.randn(batch_size, latent_dim).to(device)
            fake_imgs = generator(z)
            fake_pred = discriminator(fake_imgs.detach())
            d_loss_fake = criterion(fake_pred, fake_labels)
            
            d_loss = d_loss_real + d_loss_fake
            
            opt_D.zero_grad()
            d_loss.backward()
            opt_D.step()
            
            # -----------------
            # Train Generator
            # -----------------
            z = torch.randn(batch_size, latent_dim).to(device)
            fake_imgs = generator(z)
            fake_pred = discriminator(fake_imgs)
            
            # Generator wants discriminator to think fakes are real
            g_loss = criterion(fake_pred, real_labels)
            
            opt_G.zero_grad()
            g_loss.backward()
            opt_G.step()
        
        if (epoch + 1) % 20 == 0:
            print(f"Epoch {epoch+1}, D Loss: {d_loss.item():.4f}, "
                  f"G Loss: {g_loss.item():.4f}")
```

### GAN Training Tips

GANs are notoriously difficult to train. Common problems and solutions:

| Problem | Solution |
|---------|----------|
| Mode collapse (generator produces limited variety) | Use WGAN-GP, add diversity loss, minibatch discrimination |
| Training instability | Use spectral normalization, gradient penalty, two-timescale updates |
| Discriminator too strong | Train generator more often, use label smoothing |
| Discriminator too weak | Train discriminator more often |

---

## 5. GAN Variants

### DCGAN (Deep Convolutional GAN)

Replaces fully connected layers with convolutions. Key architecture guidelines:
- Use strided convolutions (no pooling).
- Use batch normalization in both generator and discriminator.
- Use ReLU in generator and LeakyReLU in discriminator.

```python
class DCGANGenerator(nn.Module):
    """DCGAN Generator for 64x64 images."""
    
    def __init__(self, latent_dim=100, channels=3, features=64):
        super().__init__()
        self.net = nn.Sequential(
            # Input: (latent_dim, 1, 1)
            nn.ConvTranspose2d(latent_dim, features * 8, 4, 1, 0, bias=False),
            nn.BatchNorm2d(features * 8),
            nn.ReLU(True),
            # (features*8, 4, 4)
            nn.ConvTranspose2d(features * 8, features * 4, 4, 2, 1, bias=False),
            nn.BatchNorm2d(features * 4),
            nn.ReLU(True),
            # (features*4, 8, 8)
            nn.ConvTranspose2d(features * 4, features * 2, 4, 2, 1, bias=False),
            nn.BatchNorm2d(features * 2),
            nn.ReLU(True),
            # (features*2, 16, 16)
            nn.ConvTranspose2d(features * 2, features, 4, 2, 1, bias=False),
            nn.BatchNorm2d(features),
            nn.ReLU(True),
            # (features, 32, 32)
            nn.ConvTranspose2d(features, channels, 4, 2, 1, bias=False),
            nn.Tanh()
            # (channels, 64, 64)
        )
    
    def forward(self, z):
        return self.net(z.view(z.size(0), -1, 1, 1))


class DCGANDiscriminator(nn.Module):
    """DCGAN Discriminator for 64x64 images."""
    
    def __init__(self, channels=3, features=64):
        super().__init__()
        self.net = nn.Sequential(
            # (channels, 64, 64)
            nn.Conv2d(channels, features, 4, 2, 1, bias=False),
            nn.LeakyReLU(0.2, inplace=True),
            # (features, 32, 32)
            nn.Conv2d(features, features * 2, 4, 2, 1, bias=False),
            nn.BatchNorm2d(features * 2),
            nn.LeakyReLU(0.2, inplace=True),
            # (features*2, 16, 16)
            nn.Conv2d(features * 2, features * 4, 4, 2, 1, bias=False),
            nn.BatchNorm2d(features * 4),
            nn.LeakyReLU(0.2, inplace=True),
            # (features*4, 8, 8)
            nn.Conv2d(features * 4, features * 8, 4, 2, 1, bias=False),
            nn.BatchNorm2d(features * 8),
            nn.LeakyReLU(0.2, inplace=True),
            # (features*8, 4, 4)
            nn.Conv2d(features * 8, 1, 4, 1, 0, bias=False),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        return self.net(x).view(-1, 1)
```

### WGAN-GP (Wasserstein GAN with Gradient Penalty)

Replaces the binary cross-entropy loss with the Wasserstein distance, which provides a smoother training signal:

```python
def compute_gradient_penalty(discriminator, real_samples, fake_samples, device):
    """Compute gradient penalty for WGAN-GP."""
    batch_size = real_samples.size(0)
    alpha = torch.rand(batch_size, 1, 1, 1).to(device)
    
    # Interpolate between real and fake
    interpolated = (alpha * real_samples + (1 - alpha) * fake_samples).requires_grad_(True)
    
    d_interpolated = discriminator(interpolated)
    
    gradients = torch.autograd.grad(
        outputs=d_interpolated,
        inputs=interpolated,
        grad_outputs=torch.ones_like(d_interpolated),
        create_graph=True,
        retain_graph=True
    )[0]
    
    gradients = gradients.view(batch_size, -1)
    gradient_penalty = ((gradients.norm(2, dim=1) - 1) ** 2).mean()
    
    return gradient_penalty


# WGAN-GP training step
def wgan_gp_step(generator, discriminator, real_imgs, latent_dim, 
                  opt_G, opt_D, device, lambda_gp=10):
    batch_size = real_imgs.size(0)
    
    # Train Discriminator (called "critic" in WGAN)
    z = torch.randn(batch_size, latent_dim).to(device)
    fake_imgs = generator(z)
    
    d_real = discriminator(real_imgs).mean()
    d_fake = discriminator(fake_imgs.detach()).mean()
    gp = compute_gradient_penalty(discriminator, real_imgs, fake_imgs.detach(), device)
    
    d_loss = d_fake - d_real + lambda_gp * gp
    
    opt_D.zero_grad()
    d_loss.backward()
    opt_D.step()
    
    # Train Generator (every n_critic steps)
    z = torch.randn(batch_size, latent_dim).to(device)
    fake_imgs = generator(z)
    g_loss = -discriminator(fake_imgs).mean()
    
    opt_G.zero_grad()
    g_loss.backward()
    opt_G.step()
    
    return d_loss.item(), g_loss.item()
```

### StyleGAN (Briefly)

StyleGAN introduced a style-based generator architecture that allows control over different aspects of the generated image at different scales:
- Coarse features (pose, shape): controlled by early layers.
- Medium features (facial features, hair style): middle layers.
- Fine features (color, micro-structure): later layers.

Key innovations: mapping network (transforms z to an intermediate latent space w), adaptive instance normalization (AdaIN), progressive growing.

---

## 6. Conditional Generation

Conditional generation creates data that satisfies specific conditions (e.g., "generate a cat," "generate the digit 7").

```python
class ConditionalGenerator(nn.Module):
    """Generator conditioned on class label."""
    
    def __init__(self, latent_dim=100, num_classes=10, img_dim=784):
        super().__init__()
        self.label_embedding = nn.Embedding(num_classes, 50)
        
        self.net = nn.Sequential(
            nn.Linear(latent_dim + 50, 256),
            nn.LeakyReLU(0.2),
            nn.BatchNorm1d(256),
            nn.Linear(256, 512),
            nn.LeakyReLU(0.2),
            nn.BatchNorm1d(512),
            nn.Linear(512, img_dim),
            nn.Tanh()
        )
    
    def forward(self, z, labels):
        label_embed = self.label_embedding(labels)
        x = torch.cat([z, label_embed], dim=1)
        return self.net(x)


class ConditionalDiscriminator(nn.Module):
    """Discriminator conditioned on class label."""
    
    def __init__(self, num_classes=10, img_dim=784):
        super().__init__()
        self.label_embedding = nn.Embedding(num_classes, 50)
        
        self.net = nn.Sequential(
            nn.Linear(img_dim + 50, 512),
            nn.LeakyReLU(0.2),
            nn.Linear(512, 256),
            nn.LeakyReLU(0.2),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x, labels):
        label_embed = self.label_embedding(labels)
        x = torch.cat([x, label_embed], dim=1)
        return self.net(x)
```

---

## 7. Diffusion Models: The Theory

Diffusion models work by:
1. **Forward process**: Gradually add noise to data until it becomes pure Gaussian noise.
2. **Reverse process**: Train a neural network to gradually remove noise, recovering the original data.

### Forward Process (Adding Noise)

At each step $t$, add a small amount of Gaussian noise:

$$q(x_t | x_{t-1}) = \mathcal{N}(x_t; \sqrt{1 - \beta_t} x_{t-1}, \beta_t I)$$

where $\beta_t$ is a noise schedule (small values like 0.0001 to 0.02).

We can jump directly to any time step $t$ using $\bar{\alpha}_t = \prod_{s=1}^{t} (1 - \beta_s)$:

$$q(x_t | x_0) = \mathcal{N}(x_t; \sqrt{\bar{\alpha}_t} x_0, (1 - \bar{\alpha}_t) I)$$

$$x_t = \sqrt{\bar{\alpha}_t} x_0 + \sqrt{1 - \bar{\alpha}_t} \epsilon, \quad \epsilon \sim \mathcal{N}(0, I)$$

### Reverse Process (Removing Noise)

The neural network learns to predict the noise $\epsilon$ that was added:

$$\mathcal{L} = \mathbb{E}_{t, x_0, \epsilon}\left[\|\epsilon - \epsilon_\theta(x_t, t)\|^2\right]$$

The model takes a noisy image $x_t$ and a time step $t$ as input, and predicts the noise $\epsilon$.

---

## 8. Denoising Diffusion Probabilistic Models (DDPM)

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class NoiseSchedule:
    """Linear noise schedule for DDPM."""
    
    def __init__(self, num_timesteps=1000, beta_start=1e-4, beta_end=0.02, device="cpu"):
        self.num_timesteps = num_timesteps
        
        # Linear schedule
        self.betas = torch.linspace(beta_start, beta_end, num_timesteps).to(device)
        self.alphas = 1.0 - self.betas
        self.alpha_bars = torch.cumprod(self.alphas, dim=0)
        
        # Pre-compute useful quantities
        self.sqrt_alpha_bars = torch.sqrt(self.alpha_bars)
        self.sqrt_one_minus_alpha_bars = torch.sqrt(1.0 - self.alpha_bars)
        self.sqrt_recip_alphas = torch.sqrt(1.0 / self.alphas)
    
    def add_noise(self, x_0, t, noise=None):
        """Add noise to x_0 to get x_t (forward process)."""
        if noise is None:
            noise = torch.randn_like(x_0)
        
        sqrt_alpha_bar = self.sqrt_alpha_bars[t].view(-1, 1, 1, 1)
        sqrt_one_minus_alpha_bar = self.sqrt_one_minus_alpha_bars[t].view(-1, 1, 1, 1)
        
        x_t = sqrt_alpha_bar * x_0 + sqrt_one_minus_alpha_bar * noise
        return x_t, noise
    
    def remove_noise(self, x_t, t, predicted_noise):
        """Remove predicted noise from x_t (one step of reverse process)."""
        beta = self.betas[t].view(-1, 1, 1, 1)
        sqrt_one_minus_alpha_bar = self.sqrt_one_minus_alpha_bars[t].view(-1, 1, 1, 1)
        sqrt_recip_alpha = self.sqrt_recip_alphas[t].view(-1, 1, 1, 1)
        
        # Predicted mean
        mean = sqrt_recip_alpha * (x_t - beta / sqrt_one_minus_alpha_bar * predicted_noise)
        
        # Add noise (except at t=0)
        if t[0] > 0:
            noise = torch.randn_like(x_t)
            sigma = torch.sqrt(beta)
            return mean + sigma * noise
        else:
            return mean
```

---

## 9. Building a Diffusion Model from Scratch

The neural network in a diffusion model is typically a U-Net with time embedding.

### Time Embedding

```python
class SinusoidalTimeEmbedding(nn.Module):
    """Sinusoidal time step embedding."""
    
    def __init__(self, dim):
        super().__init__()
        self.dim = dim
    
    def forward(self, t):
        device = t.device
        half_dim = self.dim // 2
        embeddings = torch.log(torch.tensor(10000.0)) / (half_dim - 1)
        embeddings = torch.exp(torch.arange(half_dim, device=device) * -embeddings)
        embeddings = t.unsqueeze(1) * embeddings.unsqueeze(0)
        embeddings = torch.cat([torch.sin(embeddings), torch.cos(embeddings)], dim=-1)
        return embeddings
```

### U-Net for Diffusion

```python
class ResBlock(nn.Module):
    """Residual block with time embedding."""
    
    def __init__(self, in_channels, out_channels, time_dim):
        super().__init__()
        self.conv1 = nn.Sequential(
            nn.GroupNorm(8, in_channels),
            nn.SiLU(),
            nn.Conv2d(in_channels, out_channels, 3, 1, 1)
        )
        self.time_mlp = nn.Sequential(
            nn.SiLU(),
            nn.Linear(time_dim, out_channels)
        )
        self.conv2 = nn.Sequential(
            nn.GroupNorm(8, out_channels),
            nn.SiLU(),
            nn.Conv2d(out_channels, out_channels, 3, 1, 1)
        )
        
        self.shortcut = nn.Conv2d(in_channels, out_channels, 1) \
                        if in_channels != out_channels else nn.Identity()
    
    def forward(self, x, t_emb):
        h = self.conv1(x)
        h = h + self.time_mlp(t_emb).unsqueeze(-1).unsqueeze(-1)
        h = self.conv2(h)
        return h + self.shortcut(x)


class SimpleUNet(nn.Module):
    """Simplified U-Net for diffusion models."""
    
    def __init__(self, in_channels=3, base_channels=64, time_dim=256,
                 channel_mults=(1, 2, 4, 8)):
        super().__init__()
        
        self.time_mlp = nn.Sequential(
            SinusoidalTimeEmbedding(base_channels),
            nn.Linear(base_channels, time_dim),
            nn.SiLU(),
            nn.Linear(time_dim, time_dim)
        )
        
        # Initial convolution
        self.init_conv = nn.Conv2d(in_channels, base_channels, 3, 1, 1)
        
        # Downsampling path
        self.down_blocks = nn.ModuleList()
        self.down_samples = nn.ModuleList()
        
        channels = [base_channels]
        ch = base_channels
        for mult in channel_mults:
            out_ch = base_channels * mult
            self.down_blocks.append(ResBlock(ch, out_ch, time_dim))
            self.down_samples.append(nn.Conv2d(out_ch, out_ch, 4, 2, 1))
            channels.append(out_ch)
            ch = out_ch
        
        # Middle
        self.mid_block1 = ResBlock(ch, ch, time_dim)
        self.mid_block2 = ResBlock(ch, ch, time_dim)
        
        # Upsampling path
        self.up_blocks = nn.ModuleList()
        self.up_samples = nn.ModuleList()
        
        for mult in reversed(channel_mults):
            out_ch = base_channels * mult
            self.up_samples.append(nn.ConvTranspose2d(ch, ch, 4, 2, 1))
            self.up_blocks.append(ResBlock(ch + out_ch, out_ch, time_dim))
            ch = out_ch
        
        # Output
        self.final_conv = nn.Sequential(
            nn.GroupNorm(8, ch),
            nn.SiLU(),
            nn.Conv2d(ch, in_channels, 3, 1, 1)
        )
    
    def forward(self, x, t):
        t_emb = self.time_mlp(t.float())
        
        x = self.init_conv(x)
        
        # Downsampling with skip connections
        skips = [x]
        for block, downsample in zip(self.down_blocks, self.down_samples):
            x = block(x, t_emb)
            skips.append(x)
            x = downsample(x)
        
        # Middle
        x = self.mid_block1(x, t_emb)
        x = self.mid_block2(x, t_emb)
        
        # Upsampling with skip connections
        for upsample, block in zip(self.up_samples, self.up_blocks):
            x = upsample(x)
            skip = skips.pop()
            x = torch.cat([x, skip], dim=1)
            x = block(x, t_emb)
        
        return self.final_conv(x)


# Training loop for diffusion
def train_diffusion(model, dataloader, noise_schedule, epochs=100, lr=2e-4):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    
    for epoch in range(epochs):
        total_loss = 0
        for images, _ in dataloader:
            images = images.to(device)
            batch_size = images.size(0)
            
            # Sample random time steps
            t = torch.randint(0, noise_schedule.num_timesteps, (batch_size,), device=device)
            
            # Add noise
            noisy_images, noise = noise_schedule.add_noise(images, t)
            
            # Predict noise
            predicted_noise = model(noisy_images, t)
            
            # Loss: MSE between actual and predicted noise
            loss = F.mse_loss(predicted_noise, noise)
            
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            
            total_loss += loss.item()
        
        avg_loss = total_loss / len(dataloader)
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}, Loss: {avg_loss:.6f}")


# Sampling (generating images)
@torch.no_grad()
def sample_diffusion(model, noise_schedule, num_samples=16, 
                     img_shape=(3, 64, 64), device="cpu"):
    """Generate images by iteratively denoising."""
    model.eval()
    
    # Start with pure noise
    x = torch.randn(num_samples, *img_shape).to(device)
    
    # Reverse process: gradually denoise
    for t in reversed(range(noise_schedule.num_timesteps)):
        t_batch = torch.full((num_samples,), t, device=device, dtype=torch.long)
        predicted_noise = model(x, t_batch)
        x = noise_schedule.remove_noise(x, t_batch, predicted_noise)
    
    return x.clamp(-1, 1)
```

---

## 10. Classifier-Free Guidance

Classifier-free guidance (CFG) is the technique that makes conditional diffusion models produce high-quality outputs. It combines conditional and unconditional predictions to steer generation.

During training, randomly drop the conditioning (e.g., text prompt) with some probability (e.g., 10%). During sampling:

$$\epsilon_{\text{guided}} = \epsilon_{\text{uncond}} + w \cdot (\epsilon_{\text{cond}} - \epsilon_{\text{uncond}})$$

where $w$ is the guidance scale (typically 7-15 for images).

Higher $w$ = more faithful to the condition but less diverse.

```python
@torch.no_grad()
def sample_with_cfg(model, noise_schedule, condition, guidance_scale=7.5,
                    num_samples=1, img_shape=(3, 64, 64), device="cpu"):
    """Sample with classifier-free guidance."""
    x = torch.randn(num_samples, *img_shape).to(device)
    
    for t in reversed(range(noise_schedule.num_timesteps)):
        t_batch = torch.full((num_samples,), t, device=device, dtype=torch.long)
        
        # Predict noise conditioned on text
        noise_cond = model(x, t_batch, condition)
        
        # Predict noise unconditionally (empty condition)
        noise_uncond = model(x, t_batch, None)
        
        # Guided noise prediction
        noise_pred = noise_uncond + guidance_scale * (noise_cond - noise_uncond)
        
        x = noise_schedule.remove_noise(x, t_batch, noise_pred)
    
    return x
```

---

## 11. Latent Diffusion and Stable Diffusion

Standard diffusion models operate in pixel space (e.g., 512x512x3 = 786,432 dimensions). This is computationally expensive.

**Latent Diffusion Models** (LDMs) first compress images into a smaller latent space using a pre-trained VAE, then run the diffusion process in that latent space.

```
Image (512x512x3) --[VAE Encoder]--> Latent (64x64x4) --[Diffusion]--> Denoised Latent --[VAE Decoder]--> Generated Image
```

This reduces computation by ~50x while maintaining quality.

**Stable Diffusion** architecture:
1. **VAE**: Compresses 512x512 images to 64x64 latent codes.
2. **U-Net**: Predicts noise in the latent space, conditioned on text embeddings.
3. **Text Encoder (CLIP)**: Converts text prompts to embeddings.
4. **Scheduler**: Controls the noise schedule during sampling.

```python
# Using Stable Diffusion with diffusers library
from diffusers import StableDiffusionPipeline
import torch

# Load pre-trained Stable Diffusion
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16
)
pipe = pipe.to("cuda")

# Generate an image
prompt = "A beautiful sunset over mountains, oil painting style"
image = pipe(
    prompt,
    num_inference_steps=50,
    guidance_scale=7.5,
    height=512,
    width=512
).images[0]

image.save("generated_sunset.png")
```

---

## 12. Image-to-Image Generation

### Img2Img (Starting from an Existing Image)

Instead of starting from pure noise, start from an existing image with some noise added:

```python
from diffusers import StableDiffusionImg2ImgPipeline
from PIL import Image

pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16
).to("cuda")

init_image = Image.open("input.png").resize((512, 512))

result = pipe(
    prompt="A watercolor painting of a landscape",
    image=init_image,
    strength=0.75,  # How much to change (0=none, 1=complete)
    guidance_scale=7.5,
    num_inference_steps=50
).images[0]
```

### Inpainting (Editing Parts of an Image)

```python
from diffusers import StableDiffusionInpaintPipeline

pipe = StableDiffusionInpaintPipeline.from_pretrained(
    "runwayml/stable-diffusion-inpainting",
    torch_dtype=torch.float16
).to("cuda")

image = Image.open("photo.png").resize((512, 512))
mask = Image.open("mask.png").resize((512, 512))  # White = area to change

result = pipe(
    prompt="A golden retriever sitting on the grass",
    image=image,
    mask_image=mask,
    guidance_scale=7.5
).images[0]
```

---

## 13. Text-to-Image Generation

The full text-to-image pipeline:

1. **Text Encoding**: Convert text prompt to embeddings using CLIP.
2. **Noise Initialization**: Start with random noise in latent space.
3. **Iterative Denoising**: Use the U-Net to predict and remove noise, guided by text.
4. **Decoding**: Use VAE decoder to convert latent code back to image.

```python
from diffusers import (
    StableDiffusionPipeline,
    DPMSolverMultistepScheduler
)

# Use a faster scheduler
pipe = StableDiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-2-1",
    torch_dtype=torch.float16
)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
pipe = pipe.to("cuda")

# Enable memory optimization
pipe.enable_attention_slicing()  # For lower VRAM usage

prompts = [
    "A photorealistic portrait of a robot reading a book, 4k, detailed",
    "An abstract painting of emotions, vibrant colors, modern art",
    "A medieval castle on a cliff, dramatic lighting, fantasy art"
]

for i, prompt in enumerate(prompts):
    image = pipe(
        prompt,
        negative_prompt="blurry, low quality, distorted",
        num_inference_steps=25,  # Fewer steps with DPM scheduler
        guidance_scale=7.5
    ).images[0]
    image.save(f"output_{i}.png")
```

---

## 14. Audio Generation

Generative models also work for audio.

```python
# Music generation with MusicGen (from Meta)
from transformers import AutoProcessor, MusicgenForConditionalGeneration

processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")

# Text-conditioned music generation
inputs = processor(
    text=["happy electronic dance music with a strong beat"],
    padding=True,
    return_tensors="pt"
)

audio_values = model.generate(**inputs, max_new_tokens=256)

# Save audio
import scipy
sampling_rate = model.config.audio_encoder.sampling_rate
scipy.io.wavfile.write("music.wav", rate=sampling_rate, 
                        data=audio_values[0, 0].cpu().numpy())
```

### Speech Synthesis (Text-to-Speech)

```python
# Using Bark for text-to-speech
from transformers import AutoProcessor, BarkModel

processor = AutoProcessor.from_pretrained("suno/bark")
model = BarkModel.from_pretrained("suno/bark")

text = "Hello, this is a test of text to speech generation."
inputs = processor(text, return_tensors="pt")

audio_array = model.generate(**inputs)
audio_array = audio_array.cpu().numpy().squeeze()

import scipy
scipy.io.wavfile.write("speech.wav", rate=24000, data=audio_array)
```

---

## 15. Evaluation of Generative Models

How do you measure if generated content is good?

### FID (Frechet Inception Distance)

Compares the distribution of generated images to real images using features from an Inception network. Lower FID = better quality.

```python
# Using pytorch-fid
from pytorch_fid import fid_score

# Requires two directories: one with real images, one with generated images
fid = fid_score.calculate_fid_given_paths(
    ["path/to/real_images", "path/to/generated_images"],
    batch_size=50,
    device="cuda",
    dims=2048
)
print(f"FID Score: {fid}")
```

### Other Metrics

| Metric | What It Measures | Lower/Higher is Better |
|--------|-----------------|----------------------|
| FID | Quality + Diversity | Lower |
| IS (Inception Score) | Quality + Diversity | Higher |
| LPIPS | Perceptual similarity | Lower |
| CLIP Score | Text-image alignment | Higher |
| Human Evaluation | Subjective quality | N/A |

---

## 16. Summary

This chapter covered the major generative model architectures:

1. **Autoencoders**: Compression and reconstruction. Foundation for VAEs.
2. **VAEs**: Structured latent space with reparameterization trick. KL divergence + reconstruction loss.
3. **GANs**: Generator vs discriminator adversarial game. Hard to train.
4. **GAN Variants**: DCGAN (convolutional), WGAN-GP (stable training), StyleGAN (controllable).
5. **Conditional Generation**: Guiding generation with labels or text.
6. **Diffusion Models**: Add noise gradually, train to remove it. Simple, stable, high quality.
7. **DDPM**: The foundational diffusion model algorithm.
8. **U-Net**: The architecture used inside diffusion models.
9. **Classifier-Free Guidance**: Combining conditional and unconditional predictions.
10. **Latent Diffusion**: Running diffusion in compressed latent space for efficiency.
11. **Stable Diffusion**: VAE + U-Net + CLIP text encoder.
12. **Image-to-Image**: Img2Img, inpainting, style transfer.
13. **Text-to-Image**: Full pipeline from text prompt to generated image.
14. **Audio Generation**: Music generation, text-to-speech.
15. **Evaluation**: FID, IS, CLIP score, human evaluation.

---

[<< Previous: Chapter 9 - Transformers and LLMs](./09_TRANSFORMERS_LLM.md) | [Next: Chapter 11 - 3D Generation >>](./11_3D_GENERATION.md)
