# Chapter 9: Transformers and Large Language Models

## Introduction

The Transformer architecture, introduced in the 2017 paper "Attention Is All You Need," replaced RNNs as the dominant architecture for NLP and then for nearly all of AI. Every major AI model today -- GPT-4, Claude, Gemini, Stable Diffusion, DALL-E, Whisper -- is built on transformers. This chapter explains exactly how they work, from the ground up, and builds one from scratch.

---

## Table of Contents

1. Why Transformers Replaced RNNs
2. Self-Attention: The Core Mechanism
3. Multi-Head Attention
4. Positional Encoding
5. The Transformer Block
6. Building a Transformer from Scratch
7. Encoder-Only Models (BERT)
8. Decoder-Only Models (GPT)
9. Encoder-Decoder Models (T5, BART)
10. Tokenization (BPE, WordPiece, SentencePiece)
11. Pre-Training and Fine-Tuning
12. Prompt Engineering
13. Reinforcement Learning from Human Feedback (RLHF)
14. Parameter-Efficient Fine-Tuning (LoRA, QLoRA)
15. Building a GPT-Style Model from Scratch
16. Using Hugging Face Transformers Library
17. Summary

---

## 1. Why Transformers Replaced RNNs

RNNs have fundamental limitations:

| Problem | RNN | Transformer |
|---------|-----|-------------|
| Sequential processing | Must process tokens one at a time | Processes all tokens in parallel |
| Long-range dependencies | Gradient vanishes over distance | Self-attention connects any two positions directly |
| Training speed | Cannot parallelize across time steps | Fully parallelizable |
| Maximum effective context | ~100-200 tokens | Thousands to millions of tokens |

The key insight is: **attention is all you need**. Instead of processing tokens sequentially and hoping the hidden state remembers important information, attention lets every token directly attend to every other token.

---

## 2. Self-Attention: The Core Mechanism

Self-attention computes a weighted combination of all positions in a sequence, where the weights are determined by the similarity between positions.

### Queries, Keys, and Values

Think of it like a library:
- **Query (Q)**: What you are looking for.
- **Key (K)**: The label on each book.
- **Value (V)**: The actual content of each book.

You compare your query against all keys to find the best matches, then read the values of those matches.

For each token in the sequence:
1. Compute a Query vector, Key vector, and Value vector using learned linear projections.
2. Compute attention scores by taking the dot product of the query with all keys.
3. Scale by $\sqrt{d_k}$ to prevent softmax saturation.
4. Apply softmax to get attention weights.
5. Compute the weighted sum of values.

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right) V$$

### Step-by-Step Example

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import math

def self_attention_step_by_step(X, d_model, d_k):
    """
    Step-by-step self-attention computation.
    
    X: Input tensor, shape (seq_len, d_model)
    d_model: Model dimension
    d_k: Key/Query dimension
    """
    seq_len = X.shape[0]
    
    # Step 1: Create Q, K, V projection matrices
    W_Q = torch.randn(d_model, d_k) * 0.1
    W_K = torch.randn(d_model, d_k) * 0.1
    W_V = torch.randn(d_model, d_k) * 0.1
    
    # Step 2: Project input to Q, K, V
    Q = X @ W_Q  # (seq_len, d_k)
    K = X @ W_K  # (seq_len, d_k)
    V = X @ W_V  # (seq_len, d_k)
    
    print(f"Q shape: {Q.shape}")
    print(f"K shape: {K.shape}")
    print(f"V shape: {V.shape}")
    
    # Step 3: Compute attention scores (dot product of Q and K^T)
    scores = Q @ K.T  # (seq_len, seq_len)
    print(f"\nRaw attention scores (seq_len x seq_len):")
    print(scores)
    
    # Step 4: Scale by sqrt(d_k)
    scores = scores / math.sqrt(d_k)
    print(f"\nScaled scores:")
    print(scores)
    
    # Step 5: Apply softmax to get attention weights
    attention_weights = F.softmax(scores, dim=-1)  # (seq_len, seq_len)
    print(f"\nAttention weights (each row sums to 1):")
    print(attention_weights)
    print(f"Row sums: {attention_weights.sum(dim=-1)}")
    
    # Step 6: Weighted sum of values
    output = attention_weights @ V  # (seq_len, d_k)
    print(f"\nOutput shape: {output.shape}")
    
    return output, attention_weights

# Example: 4 tokens, each with 8-dimensional embeddings
X = torch.randn(4, 8)
output, weights = self_attention_step_by_step(X, d_model=8, d_k=6)
```

### Causal (Masked) Self-Attention

For autoregressive models (like GPT), each token should only attend to previous tokens, not future ones. This is achieved with a causal mask.

```python
def causal_self_attention(Q, K, V):
    """Self-attention with causal mask (for autoregressive models)."""
    seq_len = Q.shape[-2]
    d_k = Q.shape[-1]
    
    scores = Q @ K.transpose(-2, -1) / math.sqrt(d_k)
    
    # Create causal mask: upper triangle = -infinity
    mask = torch.triu(torch.ones(seq_len, seq_len), diagonal=1).bool()
    scores = scores.masked_fill(mask, float("-inf"))
    
    # After softmax, -inf becomes 0
    attention_weights = F.softmax(scores, dim=-1)
    output = attention_weights @ V
    
    return output, attention_weights

# Example:
# Token 1 can only attend to: [1]
# Token 2 can attend to: [1, 2]
# Token 3 can attend to: [1, 2, 3]
# Token 4 can attend to: [1, 2, 3, 4]
```

---

## 3. Multi-Head Attention

Instead of one attention computation, we run multiple attention heads in parallel, each with different learned projections. This allows the model to attend to different aspects simultaneously (e.g., one head for syntax, one for semantics).

$$\text{MultiHead}(Q, K, V) = \text{Concat}(\text{head}_1, ..., \text{head}_h) W^O$$

where each head is:
$$\text{head}_i = \text{Attention}(QW_i^Q, KW_i^K, VW_i^V)$$

```python
class MultiHeadAttention(nn.Module):
    """Multi-head attention mechanism."""
    
    def __init__(self, d_model, num_heads, dropout=0.1):
        super().__init__()
        assert d_model % num_heads == 0, "d_model must be divisible by num_heads"
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        # Linear projections for Q, K, V, and output
        self.W_Q = nn.Linear(d_model, d_model)
        self.W_K = nn.Linear(d_model, d_model)
        self.W_V = nn.Linear(d_model, d_model)
        self.W_O = nn.Linear(d_model, d_model)
        
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, query, key, value, mask=None):
        """
        Args:
            query: (batch, seq_len_q, d_model)
            key:   (batch, seq_len_k, d_model)
            value: (batch, seq_len_k, d_model)
            mask:  (batch, 1, seq_len_q, seq_len_k) or broadcastable
        """
        batch_size = query.shape[0]
        
        # Project and reshape: (batch, seq_len, d_model) -> (batch, num_heads, seq_len, d_k)
        Q = self.W_Q(query).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = self.W_K(key).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = self.W_V(value).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        
        # Compute attention scores
        scores = Q @ K.transpose(-2, -1) / math.sqrt(self.d_k)
        # scores shape: (batch, num_heads, seq_len_q, seq_len_k)
        
        # Apply mask if provided
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float("-inf"))
        
        # Softmax and dropout
        attention_weights = F.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)
        
        # Apply attention to values
        context = attention_weights @ V
        # context shape: (batch, num_heads, seq_len_q, d_k)
        
        # Concatenate heads
        context = context.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        
        # Final projection
        output = self.W_O(context)
        
        return output, attention_weights
```

---

## 4. Positional Encoding

Self-attention is permutation-invariant -- it does not know the order of tokens. Without positional information, "dog bites man" and "man bites dog" would produce identical representations.

Positional encoding injects position information into the input embeddings.

### Sinusoidal Positional Encoding (Original Transformer)

$$PE_{(pos, 2i)} = \sin\left(\frac{pos}{10000^{2i/d_{model}}}\right)$$
$$PE_{(pos, 2i+1)} = \cos\left(\frac{pos}{10000^{2i/d_{model}}}\right)$$

```python
class PositionalEncoding(nn.Module):
    """Sinusoidal positional encoding."""
    
    def __init__(self, d_model, max_len=5000, dropout=0.1):
        super().__init__()
        self.dropout = nn.Dropout(dropout)
        
        # Create positional encoding matrix
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        
        # Compute the division term
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)
        )
        
        # Apply sin to even indices, cos to odd indices
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        pe = pe.unsqueeze(0)  # (1, max_len, d_model)
        self.register_buffer("pe", pe)
    
    def forward(self, x):
        """
        Args:
            x: (batch, seq_len, d_model)
        """
        x = x + self.pe[:, :x.size(1), :]
        return self.dropout(x)
```

### Learned Positional Encoding (GPT-style)

Modern models often learn the positional embeddings instead:

```python
class LearnedPositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=2048):
        super().__init__()
        self.position_embeddings = nn.Embedding(max_len, d_model)
    
    def forward(self, x):
        seq_len = x.size(1)
        positions = torch.arange(seq_len, device=x.device).unsqueeze(0)
        return x + self.position_embeddings(positions)
```

### Rotary Positional Encoding (RoPE)

Modern LLMs (LLaMA, Mistral, etc.) use Rotary Positional Encoding, which encodes relative position through rotation of the query and key vectors:

```python
class RotaryPositionalEncoding(nn.Module):
    """Rotary Positional Encoding (RoPE) as used in LLaMA."""
    
    def __init__(self, dim, max_seq_len=2048, base=10000):
        super().__init__()
        inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer("inv_freq", inv_freq)
        
        t = torch.arange(max_seq_len).float()
        freqs = torch.outer(t, inv_freq)
        emb = torch.cat([freqs, freqs], dim=-1)
        self.register_buffer("cos_cached", emb.cos())
        self.register_buffer("sin_cached", emb.sin())
    
    def forward(self, q, k, seq_len):
        cos = self.cos_cached[:seq_len].unsqueeze(0).unsqueeze(0)
        sin = self.sin_cached[:seq_len].unsqueeze(0).unsqueeze(0)
        
        q_embed = (q * cos) + (self._rotate_half(q) * sin)
        k_embed = (k * cos) + (self._rotate_half(k) * sin)
        return q_embed, k_embed
    
    def _rotate_half(self, x):
        x1, x2 = x[..., :x.shape[-1]//2], x[..., x.shape[-1]//2:]
        return torch.cat([-x2, x1], dim=-1)
```

---

## 5. The Transformer Block

A transformer block consists of:

1. Multi-Head Self-Attention
2. Add & Layer Norm (residual connection)
3. Feed-Forward Network (two linear layers with activation)
4. Add & Layer Norm (residual connection)

```python
class FeedForward(nn.Module):
    """Position-wise feed-forward network."""
    
    def __init__(self, d_model, d_ff, dropout=0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
            nn.Dropout(dropout)
        )
    
    def forward(self, x):
        return self.net(x)


class TransformerBlock(nn.Module):
    """A single transformer block."""
    
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()
        self.attention = MultiHeadAttention(d_model, num_heads, dropout)
        self.feed_forward = FeedForward(d_model, d_ff, dropout)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x, mask=None):
        # Self-attention with residual connection
        attn_output, _ = self.attention(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_output))
        
        # Feed-forward with residual connection
        ff_output = self.feed_forward(x)
        x = self.norm2(x + ff_output)
        
        return x
```

### Pre-Norm vs Post-Norm

The original transformer uses "Post-Norm" (normalize after the residual addition). Most modern LLMs use "Pre-Norm" (normalize before the sub-layer):

```python
class PreNormTransformerBlock(nn.Module):
    """Transformer block with Pre-LayerNorm (modern style)."""
    
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()
        self.attention = MultiHeadAttention(d_model, num_heads, dropout)
        self.feed_forward = FeedForward(d_model, d_ff, dropout)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
    
    def forward(self, x, mask=None):
        # Pre-norm: normalize THEN apply sub-layer
        normed = self.norm1(x)
        attn_output, _ = self.attention(normed, normed, normed, mask)
        x = x + attn_output  # Residual
        
        normed = self.norm2(x)
        ff_output = self.feed_forward(normed)
        x = x + ff_output  # Residual
        
        return x
```

Pre-Norm is more stable during training, especially for deep models.

---

## 6. Building a Transformer from Scratch

```python
class Transformer(nn.Module):
    """Complete Transformer model (encoder-decoder)."""
    
    def __init__(self, src_vocab_size, tgt_vocab_size, d_model=512,
                 num_heads=8, num_layers=6, d_ff=2048, max_len=5000,
                 dropout=0.1):
        super().__init__()
        
        self.d_model = d_model
        
        # Embeddings
        self.src_embedding = nn.Embedding(src_vocab_size, d_model)
        self.tgt_embedding = nn.Embedding(tgt_vocab_size, d_model)
        self.pos_encoding = PositionalEncoding(d_model, max_len, dropout)
        
        # Encoder
        self.encoder_layers = nn.ModuleList([
            TransformerEncoderBlock(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])
        
        # Decoder
        self.decoder_layers = nn.ModuleList([
            TransformerDecoderBlock(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])
        
        self.norm = nn.LayerNorm(d_model)
        self.output_projection = nn.Linear(d_model, tgt_vocab_size)
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)
    
    def encode(self, src, src_mask=None):
        x = self.src_embedding(src) * math.sqrt(self.d_model)
        x = self.pos_encoding(x)
        
        for layer in self.encoder_layers:
            x = layer(x, src_mask)
        
        return self.norm(x)
    
    def decode(self, tgt, memory, tgt_mask=None, memory_mask=None):
        x = self.tgt_embedding(tgt) * math.sqrt(self.d_model)
        x = self.pos_encoding(x)
        
        for layer in self.decoder_layers:
            x = layer(x, memory, tgt_mask, memory_mask)
        
        return self.norm(x)
    
    def forward(self, src, tgt, src_mask=None, tgt_mask=None):
        memory = self.encode(src, src_mask)
        output = self.decode(tgt, memory, tgt_mask, src_mask)
        logits = self.output_projection(output)
        return logits


class TransformerEncoderBlock(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout):
        super().__init__()
        self.self_attention = MultiHeadAttention(d_model, num_heads, dropout)
        self.feed_forward = FeedForward(d_model, d_ff, dropout)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x, mask=None):
        attn, _ = self.self_attention(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn))
        ff = self.feed_forward(x)
        x = self.norm2(x + ff)
        return x


class TransformerDecoderBlock(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout):
        super().__init__()
        self.self_attention = MultiHeadAttention(d_model, num_heads, dropout)
        self.cross_attention = MultiHeadAttention(d_model, num_heads, dropout)
        self.feed_forward = FeedForward(d_model, d_ff, dropout)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.norm3 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x, memory, tgt_mask=None, memory_mask=None):
        # Masked self-attention (causal)
        attn, _ = self.self_attention(x, x, x, tgt_mask)
        x = self.norm1(x + self.dropout(attn))
        
        # Cross-attention (attend to encoder output)
        attn, _ = self.cross_attention(x, memory, memory, memory_mask)
        x = self.norm2(x + self.dropout(attn))
        
        # Feed-forward
        ff = self.feed_forward(x)
        x = self.norm3(x + ff)
        return x


# Creating masks
def create_masks(src, tgt, pad_idx=0):
    """Create source padding mask and target causal mask."""
    # Source padding mask: True where NOT padding
    src_mask = (src != pad_idx).unsqueeze(1).unsqueeze(2)
    # Shape: (batch, 1, 1, src_len)
    
    # Target mask: causal + padding
    tgt_pad_mask = (tgt != pad_idx).unsqueeze(1).unsqueeze(2)
    tgt_len = tgt.shape[1]
    tgt_causal_mask = torch.tril(torch.ones(tgt_len, tgt_len)).bool()
    tgt_mask = tgt_pad_mask & tgt_causal_mask
    # Shape: (batch, 1, tgt_len, tgt_len)
    
    return src_mask, tgt_mask
```

---

## 7. Encoder-Only Models (BERT)

BERT (Bidirectional Encoder Representations from Transformers) uses only the encoder part and processes text bidirectionally (each token attends to all other tokens).

### Pre-Training Tasks

**Masked Language Modeling (MLM)**: Randomly mask 15% of tokens and predict them.

```
Input:  "The [MASK] sat on the [MASK]"
Output: "The cat sat on the mat"
```

**Next Sentence Prediction (NSP)**: Predict whether sentence B follows sentence A.

### Using BERT with Hugging Face

```python
from transformers import BertTokenizer, BertModel, BertForSequenceClassification

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertModel.from_pretrained("bert-base-uncased")

text = "The transformer architecture changed everything."
inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)

with torch.no_grad():
    outputs = model(**inputs)

# outputs.last_hidden_state: (batch, seq_len, 768) -- contextual embeddings
# outputs.pooler_output: (batch, 768) -- [CLS] token representation

print(f"Token embeddings shape: {outputs.last_hidden_state.shape}")
print(f"Pooled output shape: {outputs.pooler_output.shape}")
```

### Fine-Tuning BERT for Classification

```python
from transformers import BertForSequenceClassification, AdamW
from transformers import get_linear_schedule_with_warmup

# Load pre-trained BERT with classification head
model = BertForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    num_labels=3  # Number of classes
)

# Prepare optimizer with weight decay
no_decay = ["bias", "LayerNorm.weight"]
optimizer_grouped_parameters = [
    {
        "params": [p for n, p in model.named_parameters() 
                   if not any(nd in n for nd in no_decay)],
        "weight_decay": 0.01
    },
    {
        "params": [p for n, p in model.named_parameters() 
                   if any(nd in n for nd in no_decay)],
        "weight_decay": 0.0
    }
]

optimizer = torch.optim.AdamW(optimizer_grouped_parameters, lr=2e-5)

# Training loop
model.train()
for epoch in range(3):
    for batch in train_dataloader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)
        
        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )
        
        loss = outputs.loss
        loss.backward()
        
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        optimizer.zero_grad()
```

---

## 8. Decoder-Only Models (GPT)

GPT (Generative Pre-trained Transformer) uses only the decoder with causal (masked) self-attention. It is trained to predict the next token.

```
Input:  "The cat sat on the"
Target: "cat sat on the mat"
```

Each position can only attend to itself and all previous positions.

### GPT Architecture Highlights

```python
class GPTBlock(nn.Module):
    """A GPT-style transformer block."""
    
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()
        self.ln1 = nn.LayerNorm(d_model)
        self.ln2 = nn.LayerNorm(d_model)
        self.attention = MultiHeadAttention(d_model, num_heads, dropout)
        self.mlp = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Linear(d_ff, d_model),
            nn.Dropout(dropout)
        )
    
    def forward(self, x, mask=None):
        # Pre-norm style
        normed = self.ln1(x)
        attn_output, _ = self.attention(normed, normed, normed, mask)
        x = x + attn_output
        
        normed = self.ln2(x)
        mlp_output = self.mlp(normed)
        x = x + mlp_output
        
        return x
```

---

## 9. Encoder-Decoder Models (T5, BART)

These models use the full encoder-decoder architecture:
- **Encoder**: Processes the input (bidirectional attention).
- **Decoder**: Generates the output (causal attention + cross-attention to encoder).

**T5** frames all NLP tasks as text-to-text:
```
Input:  "translate English to French: The cat sat on the mat."
Output: "Le chat est assis sur le tapis."

Input:  "summarize: (long article text...)"
Output: "(short summary)"

Input:  "question: What is the capital of France? context: Paris is the capital..."
Output: "Paris"
```

```python
from transformers import T5ForConditionalGeneration, T5Tokenizer

model = T5ForConditionalGeneration.from_pretrained("t5-base")
tokenizer = T5Tokenizer.from_pretrained("t5-base")

# Summarization
input_text = "summarize: The transformer architecture was introduced in 2017..."
inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)

with torch.no_grad():
    outputs = model.generate(**inputs, max_new_tokens=150)

summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(summary)
```

---

## 10. Tokenization (BPE, WordPiece, SentencePiece)

Language models do not work with raw text. They need a way to convert text into numbers. Tokenization does this.

### Word-Level Tokenization

Simple: split by spaces. Problem: vocabulary is huge and new words ("COVID-19") cannot be handled.

### Character-Level Tokenization

Simple: each character is a token. Problem: sequences are very long and the model must learn word structure from scratch.

### Subword Tokenization (The Standard)

Splits words into meaningful subword units, balancing vocabulary size and sequence length.

**Byte Pair Encoding (BPE)**:
1. Start with all individual characters as tokens.
2. Count the most frequent pair of consecutive tokens.
3. Merge that pair into a new token.
4. Repeat until desired vocabulary size is reached.

```python
class SimpleBPE:
    """Simplified Byte Pair Encoding tokenizer."""
    
    def __init__(self, vocab_size=1000):
        self.vocab_size = vocab_size
        self.merges = []
        self.vocab = {}
    
    def train(self, text):
        """Train BPE from raw text."""
        # Start with character-level tokens
        # Add a special end-of-word marker
        words = text.split()
        word_freqs = {}
        for word in words:
            chars = tuple(list(word) + ["</w>"])
            word_freqs[chars] = word_freqs.get(chars, 0) + 1
        
        # Build initial vocabulary (all characters)
        self.vocab = set()
        for word in word_freqs:
            for char in word:
                self.vocab.add(char)
        
        num_merges = self.vocab_size - len(self.vocab)
        
        for i in range(num_merges):
            # Count pair frequencies
            pair_counts = {}
            for word, freq in word_freqs.items():
                for j in range(len(word) - 1):
                    pair = (word[j], word[j + 1])
                    pair_counts[pair] = pair_counts.get(pair, 0) + freq
            
            if not pair_counts:
                break
            
            # Find the most frequent pair
            best_pair = max(pair_counts, key=pair_counts.get)
            self.merges.append(best_pair)
            
            # Merge the pair in all words
            new_word_freqs = {}
            merged_token = best_pair[0] + best_pair[1]
            self.vocab.add(merged_token)
            
            for word, freq in word_freqs.items():
                new_word = []
                j = 0
                while j < len(word):
                    if (j < len(word) - 1 and 
                        word[j] == best_pair[0] and 
                        word[j + 1] == best_pair[1]):
                        new_word.append(merged_token)
                        j += 2
                    else:
                        new_word.append(word[j])
                        j += 1
                new_word_freqs[tuple(new_word)] = freq
            
            word_freqs = new_word_freqs
            
            if (i + 1) % 100 == 0:
                print(f"Merge {i+1}/{num_merges}: {best_pair} -> {merged_token}")
        
        print(f"Vocabulary size: {len(self.vocab)}")
    
    def tokenize(self, word):
        """Tokenize a single word using learned merges."""
        tokens = list(word) + ["</w>"]
        
        for pair in self.merges:
            new_tokens = []
            j = 0
            while j < len(tokens):
                if (j < len(tokens) - 1 and 
                    tokens[j] == pair[0] and 
                    tokens[j + 1] == pair[1]):
                    new_tokens.append(pair[0] + pair[1])
                    j += 2
                else:
                    new_tokens.append(tokens[j])
                    j += 1
            tokens = new_tokens
        
        return tokens
```

### Using Hugging Face Tokenizers

```python
from transformers import AutoTokenizer

# GPT-2 tokenizer (BPE)
tokenizer = AutoTokenizer.from_pretrained("gpt2")
tokens = tokenizer.encode("Hello, world! This is a test.")
print(f"Tokens: {tokens}")
print(f"Decoded: {tokenizer.decode(tokens)}")
print(f"Token strings: {[tokenizer.decode([t]) for t in tokens]}")

# BERT tokenizer (WordPiece)
bert_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
tokens = bert_tokenizer.encode("unbelievable")
print(f"WordPiece tokens: {bert_tokenizer.convert_ids_to_tokens(tokens)}")
# Output: ['[CLS]', 'un', '##believe', '##able', '[SEP]']
```

---

## 11. Pre-Training and Fine-Tuning

### The Two-Stage Paradigm

**Pre-Training** (Stage 1): Train a large model on massive amounts of text to learn general language understanding. This is expensive (millions of dollars for large models).

**Fine-Tuning** (Stage 2): Take the pre-trained model and train it on a specific task with a smaller dataset. This is cheap and gives excellent results.

```
Pre-training:  [Massive text corpus] --> [Language Model]
                                              |
Fine-tuning:   [Task-specific data] --> [Adapted Model]
```

### Types of Fine-Tuning

**Full fine-tuning**: Update all model weights. Works well but requires lots of memory.

**Feature extraction**: Freeze the model and only train a new classification head.

**Gradual unfreezing**: Unfreeze layers one at a time, starting from the top.

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from transformers import TrainingArguments, Trainer
from datasets import load_dataset

# Load pre-trained model and tokenizer
model_name = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

# Load dataset
dataset = load_dataset("imdb")

# Tokenize
def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True, 
                     max_length=512)

tokenized_datasets = dataset.map(tokenize_function, batched=True)

# Training configuration
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=64,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=100,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    fp16=True,
    learning_rate=2e-5,
)

# Create Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["test"],
)

# Train
trainer.train()
```

---

## 12. Prompt Engineering

Prompt engineering is the practice of crafting input text to get desired outputs from language models without changing model weights.

### Key Techniques

**Zero-Shot**: Ask the model directly without examples.
```
Classify the sentiment of this review: "This movie was fantastic!"
Sentiment:
```

**Few-Shot**: Provide a few examples before the actual query.
```
Review: "Great product, works perfectly!" -> Positive
Review: "Terrible quality, broke after one day." -> Negative
Review: "The book was absolutely captivating!" -> 
```

**Chain-of-Thought (CoT)**: Ask the model to think step by step.
```
Question: If John has 3 apples and gives away 1, buys 5 more, then eats 2, 
how many does he have?

Let's think step by step:
1. John starts with 3 apples.
2. He gives away 1: 3 - 1 = 2
3. He buys 5 more: 2 + 5 = 7
4. He eats 2: 7 - 2 = 5

Answer: 5 apples
```

**System Prompts**: Set the behavior and persona of the model.
```
System: You are a helpful Python programming assistant. Always provide 
code examples and explain your reasoning.

User: How do I read a CSV file?
```

---

## 13. Reinforcement Learning from Human Feedback (RLHF)

RLHF is the technique used to align models like ChatGPT with human preferences (being helpful, harmless, and honest).

### The Three Stages

**Stage 1: Supervised Fine-Tuning (SFT)**
Train the model on high-quality (prompt, response) pairs written by humans.

**Stage 2: Reward Model Training**
1. Generate multiple responses for each prompt.
2. Have humans rank the responses from best to worst.
3. Train a reward model that predicts human preference scores.

**Stage 3: Reinforcement Learning (PPO)**
Use the reward model to provide feedback to the language model. The language model learns to generate responses that the reward model rates highly.

```python
# Simplified RLHF pipeline (conceptual)

class RewardModel(nn.Module):
    """Reward model that scores response quality."""
    
    def __init__(self, base_model):
        super().__init__()
        self.base_model = base_model
        self.reward_head = nn.Linear(base_model.config.hidden_size, 1)
    
    def forward(self, input_ids, attention_mask):
        outputs = self.base_model(input_ids, attention_mask=attention_mask)
        
        # Use the last token's hidden state as the reward
        last_hidden = outputs.last_hidden_state[:, -1, :]
        reward = self.reward_head(last_hidden)
        return reward


# Training reward model on human preference data
def train_reward_model(model, preference_data):
    """
    preference_data: list of (prompt, chosen_response, rejected_response)
    """
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-5)
    
    for prompt, chosen, rejected in preference_data:
        # Score both responses
        chosen_reward = model(chosen)
        rejected_reward = model(rejected)
        
        # The chosen response should have higher reward
        # Bradley-Terry loss
        loss = -torch.log(torch.sigmoid(chosen_reward - rejected_reward))
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
```

### Direct Preference Optimization (DPO)

DPO is a simpler alternative to RLHF that does not require a separate reward model or RL training:

```python
# DPO directly optimizes the policy using preference pairs
def dpo_loss(policy_chosen_logprobs, policy_rejected_logprobs,
             ref_chosen_logprobs, ref_rejected_logprobs, beta=0.1):
    """
    Direct Preference Optimization loss.
    
    Compares log probability ratios between policy and reference model
    for chosen vs rejected responses.
    """
    chosen_rewards = beta * (policy_chosen_logprobs - ref_chosen_logprobs)
    rejected_rewards = beta * (policy_rejected_logprobs - ref_rejected_logprobs)
    
    loss = -F.logsigmoid(chosen_rewards - rejected_rewards).mean()
    return loss
```

---

## 14. Parameter-Efficient Fine-Tuning (LoRA, QLoRA)

Full fine-tuning of large models requires enormous GPU memory. Parameter-efficient methods adapt models by training only a small number of additional parameters.

### LoRA (Low-Rank Adaptation)

Instead of updating a full weight matrix $W \in \mathbb{R}^{m \times n}$, LoRA adds a low-rank decomposition:

$$W' = W + \Delta W = W + BA$$

where $B \in \mathbb{R}^{m \times r}$ and $A \in \mathbb{R}^{r \times n}$, with rank $r \ll \min(m, n)$.

For a 7B parameter model with $r = 16$, this reduces trainable parameters from 7 billion to about 4 million (0.06%).

```python
class LoRALayer(nn.Module):
    """Low-Rank Adaptation layer."""
    
    def __init__(self, original_layer, rank=16, alpha=32):
        super().__init__()
        self.original_layer = original_layer
        self.rank = rank
        self.alpha = alpha
        self.scaling = alpha / rank
        
        in_features = original_layer.in_features
        out_features = original_layer.out_features
        
        # Low-rank matrices
        self.lora_A = nn.Parameter(torch.randn(in_features, rank) * 0.01)
        self.lora_B = nn.Parameter(torch.zeros(rank, out_features))
        
        # Freeze original weights
        for param in self.original_layer.parameters():
            param.requires_grad = False
    
    def forward(self, x):
        # Original output + low-rank adaptation
        original = self.original_layer(x)
        lora = (x @ self.lora_A @ self.lora_B) * self.scaling
        return original + lora


def apply_lora(model, rank=16, alpha=32, target_modules=None):
    """Apply LoRA to specified modules in a model."""
    if target_modules is None:
        target_modules = ["q_proj", "v_proj"]  # Common choice
    
    for name, module in model.named_modules():
        if any(target in name for target in target_modules):
            if isinstance(module, nn.Linear):
                parent_name = ".".join(name.split(".")[:-1])
                child_name = name.split(".")[-1]
                parent = dict(model.named_modules())[parent_name]
                
                lora_layer = LoRALayer(module, rank=rank, alpha=alpha)
                setattr(parent, child_name, lora_layer)
    
    # Count trainable parameters
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"Trainable: {trainable:,} / {total:,} ({100*trainable/total:.2f}%)")
```

### Using PEFT Library

```python
from peft import LoraConfig, get_peft_model, TaskType

# Configure LoRA
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=16,                # Rank
    lora_alpha=32,       # Scaling factor
    lora_dropout=0.1,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    bias="none"
)

# Apply LoRA to model
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# "trainable params: 4,194,304 || all params: 6,742,609,920 || trainable%: 0.06"
```

### QLoRA

QLoRA combines LoRA with 4-bit quantization to further reduce memory:

```python
from transformers import BitsAndBytesConfig

# 4-bit quantization config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",      # NormalFloat4 quantization
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True   # Nested quantization
)

# Load model in 4-bit
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantization_config=bnb_config,
    device_map="auto"
)

# Then apply LoRA on top of the quantized model
model = get_peft_model(model, lora_config)
# Now you can fine-tune a 7B model on a single 24GB GPU
```

---

## 15. Building a GPT-Style Model from Scratch

```python
class GPT(nn.Module):
    """A GPT-style language model built from scratch."""
    
    def __init__(self, vocab_size, d_model=768, num_heads=12, num_layers=12,
                 d_ff=3072, max_seq_len=1024, dropout=0.1):
        super().__init__()
        
        self.d_model = d_model
        self.max_seq_len = max_seq_len
        
        # Token and position embeddings
        self.token_embedding = nn.Embedding(vocab_size, d_model)
        self.position_embedding = nn.Embedding(max_seq_len, d_model)
        self.dropout = nn.Dropout(dropout)
        
        # Transformer blocks
        self.blocks = nn.ModuleList([
            GPTBlock(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])
        
        # Final layer norm and output projection
        self.ln_f = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab_size, bias=False)
        
        # Weight tying: share weights between token embedding and output projection
        self.head.weight = self.token_embedding.weight
        
        # Initialize weights
        self.apply(self._init_weights)
    
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
    
    def forward(self, input_ids, targets=None):
        batch_size, seq_len = input_ids.shape
        assert seq_len <= self.max_seq_len, f"Sequence too long: {seq_len} > {self.max_seq_len}"
        
        # Create position indices
        positions = torch.arange(seq_len, device=input_ids.device).unsqueeze(0)
        
        # Embed tokens + positions
        x = self.token_embedding(input_ids) + self.position_embedding(positions)
        x = self.dropout(x)
        
        # Create causal mask
        mask = torch.tril(torch.ones(seq_len, seq_len, device=input_ids.device))
        mask = mask.unsqueeze(0).unsqueeze(0)  # (1, 1, seq_len, seq_len)
        
        # Apply transformer blocks
        for block in self.blocks:
            x = block(x, mask)
        
        # Final norm and projection
        x = self.ln_f(x)
        logits = self.head(x)  # (batch, seq_len, vocab_size)
        
        # Compute loss if targets provided
        loss = None
        if targets is not None:
            loss = F.cross_entropy(
                logits.view(-1, logits.size(-1)),
                targets.view(-1),
                ignore_index=-1  # Ignore padding
            )
        
        return logits, loss
    
    @torch.no_grad()
    def generate(self, input_ids, max_new_tokens, temperature=1.0, 
                 top_k=50, top_p=0.95):
        """Generate text autoregressively."""
        self.eval()
        
        for _ in range(max_new_tokens):
            # Crop to max sequence length
            idx_cond = input_ids[:, -self.max_seq_len:]
            
            # Forward pass
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :]  # Last position only
            
            # Apply temperature
            logits = logits / temperature
            
            # Top-K filtering
            if top_k > 0:
                v, _ = torch.topk(logits, top_k)
                logits[logits < v[:, -1:]] = float("-inf")
            
            # Top-P filtering
            if top_p < 1.0:
                sorted_logits, sorted_indices = torch.sort(logits, descending=True)
                cumsum = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
                mask = cumsum - F.softmax(sorted_logits, dim=-1) >= top_p
                sorted_logits[mask] = float("-inf")
                logits = sorted_logits.scatter(1, sorted_indices, sorted_logits)
            
            # Sample
            probs = F.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, 1)
            
            input_ids = torch.cat([input_ids, next_token], dim=1)
        
        return input_ids


# Training a small GPT
def train_gpt(train_data, vocab_size, epochs=10, batch_size=32, 
              seq_len=128, learning_rate=3e-4):
    """Train a small GPT model."""
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    model = GPT(
        vocab_size=vocab_size,
        d_model=256,
        num_heads=8,
        num_layers=6,
        d_ff=1024,
        max_seq_len=seq_len,
        dropout=0.1
    ).to(device)
    
    param_count = sum(p.numel() for p in model.parameters())
    print(f"Model parameters: {param_count:,}")
    
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, 
                                   weight_decay=0.1, betas=(0.9, 0.95))
    
    # Cosine learning rate schedule with warmup
    total_steps = epochs * (len(train_data) // (batch_size * seq_len))
    warmup_steps = total_steps // 10
    
    def lr_lambda(step):
        if step < warmup_steps:
            return step / warmup_steps
        progress = (step - warmup_steps) / (total_steps - warmup_steps)
        return 0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * progress))
    
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)
    
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        num_batches = 0
        
        # Create random batches
        for i in range(0, len(train_data) - seq_len - 1, batch_size * seq_len):
            batch_inputs = []
            batch_targets = []
            
            for j in range(batch_size):
                start = i + j * seq_len
                if start + seq_len + 1 > len(train_data):
                    break
                batch_inputs.append(train_data[start:start + seq_len])
                batch_targets.append(train_data[start + 1:start + seq_len + 1])
            
            if len(batch_inputs) == 0:
                break
            
            inputs = torch.tensor(batch_inputs, dtype=torch.long).to(device)
            targets = torch.tensor(batch_targets, dtype=torch.long).to(device)
            
            logits, loss = model(inputs, targets)
            
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
            
            total_loss += loss.item()
            num_batches += 1
        
        avg_loss = total_loss / num_batches if num_batches > 0 else 0
        print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}, "
              f"LR: {scheduler.get_last_lr()[0]:.6f}")
    
    return model
```

### Model Sizes

| Model | Parameters | Layers | d_model | Heads | d_ff |
|-------|-----------|--------|---------|-------|------|
| GPT-2 Small | 117M | 12 | 768 | 12 | 3072 |
| GPT-2 Medium | 345M | 24 | 1024 | 16 | 4096 |
| GPT-2 Large | 774M | 36 | 1280 | 20 | 5120 |
| GPT-2 XL | 1.5B | 48 | 1600 | 25 | 6400 |
| LLaMA-2 7B | 7B | 32 | 4096 | 32 | 11008 |
| LLaMA-2 13B | 13B | 40 | 5120 | 40 | 13824 |
| LLaMA-2 70B | 70B | 80 | 8192 | 64 | 28672 |

---

## 16. Using Hugging Face Transformers Library

### Text Generation

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

prompt = "The future of artificial intelligence is"
inputs = tokenizer(prompt, return_tensors="pt")

output = model.generate(
    **inputs,
    max_new_tokens=100,
    temperature=0.8,
    top_k=50,
    top_p=0.95,
    do_sample=True,
    repetition_penalty=1.2
)

generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
print(generated_text)
```

### Text Embedding

```python
from transformers import AutoModel, AutoTokenizer
import torch

model_name = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def get_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    # Mean pooling
    attention_mask = inputs["attention_mask"]
    token_embeddings = outputs.last_hidden_state
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size())
    embedding = torch.sum(token_embeddings * input_mask_expanded, 1) / \
                torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    return embedding

# Compute similarity
emb1 = get_embedding("The cat sat on the mat")
emb2 = get_embedding("A feline rested on the rug")
emb3 = get_embedding("The stock market crashed today")

sim_12 = F.cosine_similarity(emb1, emb2)
sim_13 = F.cosine_similarity(emb1, emb3)
print(f"Similarity (cat/feline): {sim_12.item():.4f}")  # High
print(f"Similarity (cat/stock): {sim_13.item():.4f}")   # Low
```

### Question Answering

```python
from transformers import pipeline

qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

context = """
The Transformer architecture was introduced in the paper 'Attention Is All You Need' 
by Vaswani et al. in 2017. It replaced recurrent neural networks as the dominant 
architecture for natural language processing tasks. The key innovation was the 
self-attention mechanism, which allows the model to attend to all positions in 
the input sequence simultaneously.
"""

result = qa_pipeline(
    question="When was the Transformer introduced?",
    context=context
)
print(f"Answer: {result['answer']}")
print(f"Score: {result['score']:.4f}")
```

### Text Summarization

```python
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

article = """
(Long article text here...)
"""

summary = summarizer(article, max_length=130, min_length=30, do_sample=False)
print(summary[0]["summary_text"])
```

---

## 17. Summary

This chapter covered the transformer architecture and its applications:

1. **Why transformers**: Parallel processing, direct long-range connections, better training.
2. **Self-attention**: Query, Key, Value mechanism. Scaled dot-product attention.
3. **Multi-head attention**: Multiple attention computations in parallel.
4. **Positional encoding**: Sinusoidal, learned, and rotary (RoPE).
5. **Transformer blocks**: Attention + feed-forward + residual + layer norm.
6. **Full transformer**: Encoder-decoder architecture from scratch.
7. **BERT**: Encoder-only, bidirectional, masked language modeling.
8. **GPT**: Decoder-only, autoregressive, next token prediction.
9. **T5/BART**: Encoder-decoder, text-to-text framework.
10. **Tokenization**: BPE, WordPiece, SentencePiece.
11. **Pre-training and fine-tuning**: The two-stage paradigm.
12. **Prompt engineering**: Zero-shot, few-shot, chain-of-thought.
13. **RLHF and DPO**: Aligning models with human preferences.
14. **LoRA and QLoRA**: Parameter-efficient fine-tuning.
15. **GPT from scratch**: Complete implementation with training loop.
16. **Hugging Face**: Practical usage for generation, embeddings, QA, summarization.

---

[<< Previous: Chapter 8 - Sequence Models & NLP](./08_SEQUENCE_MODELS_NLP.md) | [Next: Chapter 10 - Generative Models >>](./10_GENERATIVE_MODELS.md)
