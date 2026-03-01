# Chapter 8: Sequence Models and Natural Language Processing

## Introduction

Language is sequential -- words come in a specific order, and the meaning of each word depends on the words around it. This chapter covers the models designed to handle sequential data: Recurrent Neural Networks (RNNs), Long Short-Term Memory networks (LSTMs), Gated Recurrent Units (GRUs), and their applications to natural language processing (NLP) tasks like text classification, sentiment analysis, machine translation, and text generation.

Note: Transformers (the architecture behind GPT, BERT, etc.) have largely replaced RNNs for NLP. We cover transformers in the next chapter. However, understanding RNNs is important for historical context and because they are still used in some applications.

---

## Table of Contents

1. The Challenge of Sequential Data
2. Recurrent Neural Networks (RNNs)
3. The Vanishing Gradient Problem in RNNs
4. LSTM (Long Short-Term Memory)
5. GRU (Gated Recurrent Unit)
6. Bidirectional RNNs
7. Sequence-to-Sequence Models
8. Attention Mechanism
9. Text Classification
10. Sentiment Analysis
11. Language Modeling and Text Generation
12. Named Entity Recognition
13. Machine Translation
14. Word2Vec and Word Embeddings from Scratch
15. Practical NLP Pipeline
16. Summary

---

## 1. The Challenge of Sequential Data

Sequential data has a fundamental challenge: the order matters, and information from the past must be carried forward. Consider:

- "The dog bit the man" vs "The man bit the dog" -- same words, very different meaning.
- "The movie was not good" -- the word "not" at position 4 changes the meaning of "good" at position 5.
- In a conversation, what was said 10 sentences ago can affect the meaning of the current sentence.

Standard feed-forward networks (MLPs) cannot handle this because:
1. They have a fixed input size (what if sentences have different lengths?).
2. They do not remember previous inputs.
3. They treat each position independently.

---

## 2. Recurrent Neural Networks (RNNs)

An RNN processes a sequence one element at a time, maintaining a "hidden state" that carries information from previous elements.

### The Key Idea

At each time step $t$:
1. The RNN receives the current input $x_t$ AND the previous hidden state $h_{t-1}$.
2. It computes a new hidden state $h_t$.
3. Optionally, it produces an output $y_t$.

$$h_t = \tanh(W_{xh} x_t + W_{hh} h_{t-1} + b_h)$$
$$y_t = W_{hy} h_t + b_y$$

The hidden state $h_t$ is a "memory" that summarizes everything the network has seen so far.

### Unrolled View

```
Time:    t=1          t=2          t=3          t=4
         
Input:   x1           x2           x3           x4
         |            |            |            |
         v            v            v            v
State: h0 --> [RNN] --> h1 --> [RNN] --> h2 --> [RNN] --> h3 --> [RNN] --> h4
                |            |            |            |
                v            v            v            v
Output:        y1           y2           y3           y4
```

The same weights (W_xh, W_hh, W_hy) are shared across all time steps. This is weight sharing across time, analogous to weight sharing across space in CNNs.

### Implementation from Scratch

```python
import numpy as np

class SimpleRNN:
    """A simple RNN implemented from scratch."""
    
    def __init__(self, input_size, hidden_size, output_size):
        self.hidden_size = hidden_size
        
        # Initialize weights
        scale = 0.01
        self.W_xh = np.random.randn(hidden_size, input_size) * scale
        self.W_hh = np.random.randn(hidden_size, hidden_size) * scale
        self.W_hy = np.random.randn(output_size, hidden_size) * scale
        self.b_h = np.zeros((hidden_size, 1))
        self.b_y = np.zeros((output_size, 1))
    
    def forward(self, inputs, h_prev=None):
        """
        Process a sequence.
        
        Args:
            inputs: List of input vectors, each shape (input_size, 1)
            h_prev: Initial hidden state, shape (hidden_size, 1)
        
        Returns:
            outputs: List of output vectors
            hidden_states: List of hidden states
        """
        if h_prev is None:
            h_prev = np.zeros((self.hidden_size, 1))
        
        hidden_states = [h_prev]
        outputs = []
        
        for x_t in inputs:
            # Compute new hidden state
            h_t = np.tanh(
                self.W_xh @ x_t +
                self.W_hh @ h_prev +
                self.b_h
            )
            
            # Compute output
            y_t = self.W_hy @ h_t + self.b_y
            
            hidden_states.append(h_t)
            outputs.append(y_t)
            h_prev = h_t
        
        return outputs, hidden_states


# Example: Processing a sequence of word embeddings
rnn = SimpleRNN(input_size=50, hidden_size=128, output_size=10)

# Simulate a sentence of 5 words, each represented as a 50-dimensional embedding
sentence = [np.random.randn(50, 1) for _ in range(5)]

outputs, hidden_states = rnn.forward(sentence)
print(f"Number of outputs: {len(outputs)}")
print(f"Last hidden state shape: {hidden_states[-1].shape}")
```

### PyTorch RNN

```python
import torch
import torch.nn as nn

rnn = nn.RNN(
    input_size=50,     # Dimension of each input element
    hidden_size=128,   # Dimension of hidden state
    num_layers=2,      # Number of stacked RNN layers
    batch_first=True,  # Input shape: (batch, seq_len, input_size)
    dropout=0.2        # Dropout between layers (not on last layer)
)

# Input: (batch_size, sequence_length, input_size)
x = torch.randn(32, 20, 50)  # 32 sentences, each 20 words, each 50-dim embedding

# Forward
output, h_n = rnn(x)
# output shape: (32, 20, 128) -- hidden state at every time step
# h_n shape: (2, 32, 128) -- final hidden state for each layer
```

---

## 3. The Vanishing Gradient Problem in RNNs

During backpropagation through time (BPTT), gradients must flow backward through many time steps. At each step, they are multiplied by the weight matrix W_hh. If the largest eigenvalue of W_hh is less than 1, gradients shrink exponentially. If it is greater than 1, gradients explode.

In practice, this means simple RNNs:
- Cannot learn long-range dependencies (e.g., connecting a word at position 3 with a word at position 50).
- Forget earlier parts of long sequences.
- Are very difficult to train on sequences longer than about 20-30 steps.

This is the primary motivation for LSTM and GRU.

---

## 4. LSTM (Long Short-Term Memory)

LSTM was designed specifically to solve the vanishing gradient problem. It introduces a "cell state" that acts as a highway for information flow across time steps, plus three "gates" that control what information to add, remove, or output.

### The Three Gates

**Forget Gate**: Decides what to remove from the cell state.

$$f_t = \sigma(W_f [h_{t-1}, x_t] + b_f)$$

A sigmoid outputs values between 0 (completely forget) and 1 (completely keep).

**Input Gate**: Decides what new information to add to the cell state.

$$i_t = \sigma(W_i [h_{t-1}, x_t] + b_i)$$
$$\tilde{C}_t = \tanh(W_C [h_{t-1}, x_t] + b_C)$$

**Cell State Update**:

$$C_t = f_t \odot C_{t-1} + i_t \odot \tilde{C}_t$$

The cell state is the key innovation. Information can flow through it unchanged (if the forget gate is 1 and the input gate is 0), solving the vanishing gradient problem.

**Output Gate**: Decides what to output based on the cell state.

$$o_t = \sigma(W_o [h_{t-1}, x_t] + b_o)$$
$$h_t = o_t \odot \tanh(C_t)$$

### Implementation

```python
class LSTMCell:
    """A single LSTM cell implemented from scratch."""
    
    def __init__(self, input_size, hidden_size):
        self.hidden_size = hidden_size
        
        # Combined weights for all four gates (for efficiency)
        # Gates: forget, input, cell candidate, output
        combined_size = input_size + hidden_size
        scale = np.sqrt(2.0 / combined_size)
        
        self.W = np.random.randn(4 * hidden_size, combined_size) * scale
        self.b = np.zeros((4 * hidden_size, 1))
        
        # Initialize forget gate bias to 1 (so it starts by remembering)
        self.b[0:hidden_size] = 1.0
    
    def forward(self, x_t, h_prev, c_prev):
        """
        Process one time step.
        
        Args:
            x_t: Input at time t, shape (input_size, 1)
            h_prev: Previous hidden state, shape (hidden_size, 1)
            c_prev: Previous cell state, shape (hidden_size, 1)
        
        Returns:
            h_t: New hidden state
            c_t: New cell state
        """
        # Concatenate input and previous hidden state
        combined = np.vstack([h_prev, x_t])
        
        # Compute all gates at once
        gates = self.W @ combined + self.b
        
        # Split into four gates
        hs = self.hidden_size
        f_gate = self._sigmoid(gates[0:hs])         # Forget gate
        i_gate = self._sigmoid(gates[hs:2*hs])      # Input gate
        c_candidate = np.tanh(gates[2*hs:3*hs])      # Cell candidate
        o_gate = self._sigmoid(gates[3*hs:4*hs])    # Output gate
        
        # Update cell state
        c_t = f_gate * c_prev + i_gate * c_candidate
        
        # Compute hidden state
        h_t = o_gate * np.tanh(c_t)
        
        return h_t, c_t
    
    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
```

### PyTorch LSTM

```python
lstm = nn.LSTM(
    input_size=256,
    hidden_size=512,
    num_layers=2,
    batch_first=True,
    dropout=0.3,
    bidirectional=False
)

x = torch.randn(32, 50, 256)  # batch=32, seq_len=50, features=256

output, (h_n, c_n) = lstm(x)
# output: (32, 50, 512) -- hidden states at all time steps
# h_n: (2, 32, 512) -- final hidden state per layer
# c_n: (2, 32, 512) -- final cell state per layer
```

---

## 5. GRU (Gated Recurrent Unit)

GRU is a simplified version of LSTM with only two gates (reset and update). It often achieves comparable performance with fewer parameters.

$$z_t = \sigma(W_z [h_{t-1}, x_t])$$ (update gate)
$$r_t = \sigma(W_r [h_{t-1}, x_t])$$ (reset gate)
$$\tilde{h}_t = \tanh(W [r_t \odot h_{t-1}, x_t])$$ (candidate)
$$h_t = (1 - z_t) \odot h_{t-1} + z_t \odot \tilde{h}_t$$ (final state)

```python
gru = nn.GRU(
    input_size=256,
    hidden_size=512,
    num_layers=2,
    batch_first=True,
    dropout=0.3
)

output, h_n = gru(x)
# output: (32, 50, 512)
# h_n: (2, 32, 512)
```

### LSTM vs GRU

| Feature | LSTM | GRU |
|---------|------|-----|
| Gates | 3 (forget, input, output) | 2 (reset, update) |
| States | 2 (hidden + cell) | 1 (hidden) |
| Parameters | More | Fewer (~25% less) |
| Performance | Slightly better on long sequences | Often comparable |
| Speed | Slower | Faster |

Rule of thumb: Try GRU first. If performance is not good enough, switch to LSTM.

---

## 6. Bidirectional RNNs

A standard RNN only sees past context (left-to-right). A bidirectional RNN processes the sequence in both directions and concatenates the results.

```
Forward:  x1 -> x2 -> x3 -> x4 -> x5
Backward: x1 <- x2 <- x3 <- x4 <- x5

At each position, the output is [forward_hidden ; backward_hidden]
```

This is useful when you have the entire sequence available (e.g., text classification, named entity recognition) but not for autoregressive tasks like text generation (where you do not have future context).

```python
bilstm = nn.LSTM(
    input_size=256,
    hidden_size=512,
    num_layers=2,
    batch_first=True,
    bidirectional=True
)

output, (h_n, c_n) = bilstm(x)
# output: (32, 50, 1024) -- 512*2 because bidirectional
# h_n: (4, 32, 512) -- 2 layers * 2 directions
```

---

## 7. Sequence-to-Sequence Models

Seq2Seq models take a variable-length input sequence and produce a variable-length output sequence. They were the foundation of machine translation before transformers.

### Architecture

```
Encoder:  "The cat sat" --> [LSTM] --> context vector (final hidden state)
                                           |
Decoder:  context vector --> [LSTM] --> "Le chat assis" (French)
```

```python
class Seq2SeqEncoder(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, num_layers, dropout):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.rnn = nn.LSTM(embed_dim, hidden_dim, num_layers, 
                           batch_first=True, dropout=dropout)
    
    def forward(self, src):
        embedded = self.embedding(src)  # (batch, src_len, embed_dim)
        outputs, (hidden, cell) = self.rnn(embedded)
        return hidden, cell


class Seq2SeqDecoder(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, num_layers, dropout):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.rnn = nn.LSTM(embed_dim, hidden_dim, num_layers,
                           batch_first=True, dropout=dropout)
        self.fc = nn.Linear(hidden_dim, vocab_size)
    
    def forward(self, trg, hidden, cell):
        embedded = self.embedding(trg)  # (batch, 1, embed_dim)
        output, (hidden, cell) = self.rnn(embedded, (hidden, cell))
        prediction = self.fc(output)  # (batch, 1, vocab_size)
        return prediction, hidden, cell


class Seq2Seq(nn.Module):
    def __init__(self, encoder, decoder, device):
        super().__init__()
        self.encoder = encoder
        self.decoder = decoder
        self.device = device
    
    def forward(self, src, trg, teacher_forcing_ratio=0.5):
        batch_size = src.shape[0]
        trg_len = trg.shape[1]
        trg_vocab_size = self.decoder.fc.out_features
        
        outputs = torch.zeros(batch_size, trg_len, trg_vocab_size).to(self.device)
        
        # Encode
        hidden, cell = self.encoder(src)
        
        # First input to decoder is the <BOS> token
        input_token = trg[:, 0:1]
        
        for t in range(1, trg_len):
            output, hidden, cell = self.decoder(input_token, hidden, cell)
            outputs[:, t:t+1, :] = output
            
            # Teacher forcing: use actual next token or predicted token
            if np.random.random() < teacher_forcing_ratio:
                input_token = trg[:, t:t+1]
            else:
                input_token = output.argmax(dim=-1)
        
        return outputs
```

### Teacher Forcing

During training, at each decoder step you have two choices:
1. Feed the decoder's OWN prediction as input for the next step (autoregressive).
2. Feed the CORRECT target token as input for the next step (teacher forcing).

Teacher forcing speeds up training but can cause problems: the model never learns to recover from its own mistakes. The solution is a teacher forcing ratio that gradually decreases during training.

---

## 8. Attention Mechanism

The basic Seq2Seq model compresses the entire input sequence into a single fixed-size vector (the final hidden state). This is a bottleneck -- long sequences lose information.

Attention solves this by allowing the decoder to "look at" all encoder hidden states at each decoding step, focusing on the most relevant parts.

### How Attention Works

At each decoder step $t$:

1. Compute attention scores between the decoder hidden state and ALL encoder hidden states.
2. Apply softmax to get attention weights (probabilities that sum to 1).
3. Compute a weighted sum of encoder hidden states (the "context vector").
4. Concatenate the context vector with the decoder hidden state.

$$\text{score}(h_t^{\text{dec}}, h_s^{\text{enc}}) = (h_t^{\text{dec}})^T h_s^{\text{enc}}$$ (dot product attention)

$$\alpha_{t,s} = \frac{\exp(\text{score}_{t,s})}{\sum_{s'} \exp(\text{score}_{t,s'})}$$ (softmax)

$$c_t = \sum_s \alpha_{t,s} h_s^{\text{enc}}$$ (context vector)

```python
class Attention(nn.Module):
    """Bahdanau (additive) attention."""
    
    def __init__(self, enc_dim, dec_dim, attn_dim):
        super().__init__()
        self.W_enc = nn.Linear(enc_dim, attn_dim, bias=False)
        self.W_dec = nn.Linear(dec_dim, attn_dim, bias=False)
        self.v = nn.Linear(attn_dim, 1, bias=False)
    
    def forward(self, decoder_hidden, encoder_outputs):
        """
        Args:
            decoder_hidden: (batch, dec_dim)
            encoder_outputs: (batch, src_len, enc_dim)
        
        Returns:
            context: (batch, enc_dim)
            attention_weights: (batch, src_len)
        """
        # decoder_hidden: (batch, dec_dim) -> (batch, 1, attn_dim)
        dec_proj = self.W_dec(decoder_hidden).unsqueeze(1)
        
        # encoder_outputs: (batch, src_len, enc_dim) -> (batch, src_len, attn_dim)
        enc_proj = self.W_enc(encoder_outputs)
        
        # Compute scores
        energy = torch.tanh(dec_proj + enc_proj)  # (batch, src_len, attn_dim)
        scores = self.v(energy).squeeze(-1)  # (batch, src_len)
        
        # Attention weights
        attention_weights = torch.softmax(scores, dim=-1)  # (batch, src_len)
        
        # Context vector
        context = torch.bmm(
            attention_weights.unsqueeze(1),  # (batch, 1, src_len)
            encoder_outputs                   # (batch, src_len, enc_dim)
        ).squeeze(1)  # (batch, enc_dim)
        
        return context, attention_weights
```

Attention is the foundation of transformers. The transformer architecture generalizes attention into "self-attention" and uses it as the primary computation mechanism.

---

## 9. Text Classification

Text classification assigns a label to a piece of text. Examples: spam detection, sentiment analysis, topic classification.

```python
class TextClassifier(nn.Module):
    """Text classifier using LSTM with attention."""
    
    def __init__(self, vocab_size, embed_dim, hidden_dim, num_classes, 
                 num_layers=2, dropout=0.3, padding_idx=0):
        super().__init__()
        
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=padding_idx)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, num_layers, 
                           batch_first=True, bidirectional=True, dropout=dropout)
        
        # Self-attention for classification
        self.attention = nn.Linear(hidden_dim * 2, 1)
        
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, num_classes)
        )
    
    def forward(self, input_ids, lengths=None):
        # Embed
        embedded = self.embedding(input_ids)  # (batch, seq_len, embed_dim)
        
        # Pack padded sequences for efficiency
        if lengths is not None:
            embedded = nn.utils.rnn.pack_padded_sequence(
                embedded, lengths.cpu(), batch_first=True, enforce_sorted=False
            )
        
        # LSTM
        lstm_out, _ = self.lstm(embedded)
        
        if lengths is not None:
            lstm_out, _ = nn.utils.rnn.pad_packed_sequence(
                lstm_out, batch_first=True
            )
        
        # Attention pooling
        attn_scores = self.attention(lstm_out).squeeze(-1)  # (batch, seq_len)
        
        # Mask padding positions
        if lengths is not None:
            mask = torch.arange(lstm_out.size(1)).unsqueeze(0).to(input_ids.device)
            mask = mask >= lengths.unsqueeze(1)
            attn_scores = attn_scores.masked_fill(mask, float("-inf"))
        
        attn_weights = torch.softmax(attn_scores, dim=-1)  # (batch, seq_len)
        
        # Weighted sum
        context = torch.bmm(
            attn_weights.unsqueeze(1), lstm_out
        ).squeeze(1)  # (batch, hidden_dim * 2)
        
        # Classify
        logits = self.classifier(context)
        return logits
```

---

## 10. Sentiment Analysis

Sentiment analysis is a specific type of text classification that determines the emotional tone of text (positive, negative, neutral).

```python
import torch
from torch.utils.data import Dataset, DataLoader

class SentimentDataset(Dataset):
    """Dataset for sentiment analysis."""
    
    def __init__(self, texts, labels, tokenizer, max_length=256):
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
        tokens = self.tokenizer(text)
        
        # Truncate or pad
        if len(tokens) > self.max_length:
            tokens = tokens[:self.max_length]
        length = len(tokens)
        tokens = tokens + [0] * (self.max_length - len(tokens))
        
        return {
            "input_ids": torch.tensor(tokens, dtype=torch.long),
            "length": torch.tensor(length, dtype=torch.long),
            "label": torch.tensor(label, dtype=torch.long)
        }


def train_sentiment_model(train_texts, train_labels, val_texts, val_labels,
                           vocab_size, num_classes=3, epochs=10):
    """Complete sentiment analysis training pipeline."""
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    model = TextClassifier(
        vocab_size=vocab_size,
        embed_dim=128,
        hidden_dim=256,
        num_classes=num_classes
    ).to(device)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.01)
    
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        for batch in train_loader:
            input_ids = batch["input_ids"].to(device)
            lengths = batch["length"]
            labels = batch["label"].to(device)
            
            logits = model(input_ids, lengths)
            loss = criterion(logits, labels)
            
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            
            total_loss += loss.item() * input_ids.size(0)
            _, predicted = logits.max(1)
            correct += predicted.eq(labels).sum().item()
            total += labels.size(0)
        
        print(f"Epoch {epoch+1}: Loss={total_loss/total:.4f}, Acc={correct/total:.4f}")
```

---

## 11. Language Modeling and Text Generation

A language model predicts the next word in a sequence. By repeatedly predicting and appending the next word, you can generate text.

### How It Works

Given the sequence "The cat sat on the", predict the next word. The model might output probabilities like:
- "mat": 0.25
- "floor": 0.15
- "couch": 0.12
- "table": 0.10
- ...

### Character-Level Language Model

```python
class CharRNN(nn.Module):
    """Character-level language model using LSTM."""
    
    def __init__(self, vocab_size, embed_dim, hidden_dim, num_layers):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, num_layers, 
                           batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_dim, vocab_size)
    
    def forward(self, x, hidden=None):
        embedded = self.embedding(x)
        output, hidden = self.lstm(embedded, hidden)
        logits = self.fc(output)
        return logits, hidden
    
    def generate(self, start_char_idx, length=500, temperature=1.0, 
                 char_to_idx=None, idx_to_char=None, device="cpu"):
        """Generate text character by character."""
        self.eval()
        
        generated = [start_char_idx]
        input_idx = torch.tensor([[start_char_idx]], dtype=torch.long).to(device)
        hidden = None
        
        with torch.no_grad():
            for _ in range(length):
                logits, hidden = self(input_idx, hidden)
                
                # Apply temperature
                # High temperature (>1): more random, creative
                # Low temperature (<1): more deterministic, repetitive
                # Temperature = 1: original distribution
                logits = logits[:, -1, :] / temperature
                
                # Sample from the distribution
                probs = torch.softmax(logits, dim=-1)
                next_idx = torch.multinomial(probs, 1)
                
                generated.append(next_idx.item())
                input_idx = next_idx
        
        # Convert indices back to characters
        text = "".join([idx_to_char[idx] for idx in generated])
        return text


# Training a character-level model
def train_char_rnn(text, epochs=50, seq_length=100, batch_size=64):
    """Train a character-level language model on raw text."""
    
    # Build character vocabulary
    chars = sorted(set(text))
    char_to_idx = {ch: i for i, ch in enumerate(chars)}
    idx_to_char = {i: ch for ch, i in char_to_idx.items()}
    vocab_size = len(chars)
    
    print(f"Vocabulary size: {vocab_size}")
    print(f"Text length: {len(text)} characters")
    
    # Encode text
    encoded = [char_to_idx[ch] for ch in text]
    
    # Create training sequences
    # Input:  "The cat sa"
    # Target: "he cat sat"  (shifted by 1)
    sequences = []
    for i in range(0, len(encoded) - seq_length, seq_length):
        input_seq = encoded[i:i + seq_length]
        target_seq = encoded[i + 1:i + seq_length + 1]
        sequences.append((input_seq, target_seq))
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    model = CharRNN(vocab_size, embed_dim=64, hidden_dim=512, num_layers=2).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.002)
    
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        
        # Shuffle and batch
        np.random.shuffle(sequences)
        
        for i in range(0, len(sequences), batch_size):
            batch = sequences[i:i + batch_size]
            inputs = torch.tensor([s[0] for s in batch], dtype=torch.long).to(device)
            targets = torch.tensor([s[1] for s in batch], dtype=torch.long).to(device)
            
            logits, _ = model(inputs)
            loss = criterion(logits.view(-1, vocab_size), targets.view(-1))
            
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
            optimizer.step()
            
            total_loss += loss.item()
        
        avg_loss = total_loss / (len(sequences) // batch_size)
        
        if (epoch + 1) % 5 == 0:
            print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")
            
            # Generate sample text
            sample = model.generate(
                start_char_idx=char_to_idx[text[0]],
                length=200,
                temperature=0.8,
                char_to_idx=char_to_idx,
                idx_to_char=idx_to_char,
                device=device
            )
            print(f"Sample: {sample[:200]}")
            print()
```

### Sampling Strategies

**Greedy sampling**: Always pick the most probable next token. Produces repetitive, boring text.

**Temperature sampling**: Divide logits by a temperature value before softmax. Higher temperature = more random.

**Top-K sampling**: Only consider the top K most probable tokens.

**Top-P (Nucleus) sampling**: Only consider the smallest set of tokens whose cumulative probability exceeds P.

```python
def sample_with_top_k_top_p(logits, temperature=1.0, top_k=50, top_p=0.95):
    """Sample from a distribution with temperature, top-k, and top-p filtering."""
    
    # Apply temperature
    logits = logits / temperature
    
    # Top-K filtering
    if top_k > 0:
        top_k_values, _ = torch.topk(logits, top_k)
        min_top_k = top_k_values[:, -1].unsqueeze(-1)
        logits = torch.where(logits < min_top_k, 
                             torch.full_like(logits, float("-inf")), 
                             logits)
    
    # Top-P (nucleus) filtering
    if top_p < 1.0:
        sorted_logits, sorted_indices = torch.sort(logits, descending=True)
        cumulative_probs = torch.cumsum(torch.softmax(sorted_logits, dim=-1), dim=-1)
        
        # Remove tokens with cumulative probability above threshold
        sorted_mask = cumulative_probs - torch.softmax(sorted_logits, dim=-1) >= top_p
        sorted_logits[sorted_mask] = float("-inf")
        
        # Scatter back to original positions
        logits = sorted_logits.scatter(1, sorted_indices, sorted_logits)
    
    # Sample
    probs = torch.softmax(logits, dim=-1)
    next_token = torch.multinomial(probs, 1)
    
    return next_token
```

---

## 12. Named Entity Recognition

NER identifies and classifies entities in text (person names, organizations, locations, dates, etc.).

```python
class NERModel(nn.Module):
    """Named Entity Recognition using BiLSTM-CRF."""
    
    def __init__(self, vocab_size, embed_dim, hidden_dim, num_tags, padding_idx=0):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=padding_idx)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, num_layers=2,
                           batch_first=True, bidirectional=True, dropout=0.3)
        self.fc = nn.Linear(hidden_dim * 2, num_tags)
        self.dropout = nn.Dropout(0.3)
    
    def forward(self, input_ids):
        embedded = self.dropout(self.embedding(input_ids))
        lstm_out, _ = self.lstm(embedded)
        logits = self.fc(self.dropout(lstm_out))
        return logits  # (batch, seq_len, num_tags)

# Tags often use BIO format:
# B-PER = Beginning of person name
# I-PER = Inside person name
# B-ORG = Beginning of organization
# I-ORG = Inside organization
# B-LOC = Beginning of location
# I-LOC = Inside location
# O = Outside any entity
```

---

## 13. Machine Translation

Machine translation converts text from one language to another. Before transformers, this was done with attention-based Seq2Seq models.

The key insight: a sentence in one language does not map word-for-word to another language. Word order changes, phrases are restructured, and the number of words changes. The attention mechanism handles this by learning which source words to focus on for each target word.

```python
# Modern machine translation using Hugging Face
from transformers import MarianMTModel, MarianTokenizer

# Load a pre-trained translation model
model_name = "Helsinki-NLP/opus-mt-en-fr"  # English to French
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

# Translate
text = "The cat sat on the mat."
inputs = tokenizer(text, return_tensors="pt", padding=True)

with torch.no_grad():
    translated = model.generate(**inputs)

result = tokenizer.decode(translated[0], skip_special_tokens=True)
print(result)  # "Le chat est assis sur le tapis."
```

---

## 14. Word2Vec and Word Embeddings from Scratch

Word2Vec trains word embeddings by predicting surrounding words (Skip-gram) or predicting a word from its surroundings (CBOW).

### Skip-gram: Predict Context from Word

Given a center word, predict the surrounding words.

```python
class SkipGram(nn.Module):
    """Word2Vec Skip-gram model."""
    
    def __init__(self, vocab_size, embed_dim):
        super().__init__()
        self.center_embeddings = nn.Embedding(vocab_size, embed_dim)
        self.context_embeddings = nn.Embedding(vocab_size, embed_dim)
    
    def forward(self, center_word, context_word):
        center_embed = self.center_embeddings(center_word)    # (batch, embed_dim)
        context_embed = self.context_embeddings(context_word)  # (batch, embed_dim)
        
        # Dot product gives similarity score
        score = torch.sum(center_embed * context_embed, dim=1)
        return score


def train_word2vec(corpus, vocab_size, embed_dim=100, window_size=5, 
                   num_negative=5, epochs=5):
    """Train Word2Vec embeddings."""
    
    model = SkipGram(vocab_size, embed_dim)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    for epoch in range(epochs):
        total_loss = 0
        
        for sentence in corpus:
            for i, center_word in enumerate(sentence):
                # Positive examples: actual context words
                context_start = max(0, i - window_size)
                context_end = min(len(sentence), i + window_size + 1)
                
                for j in range(context_start, context_end):
                    if j == i:
                        continue
                    
                    context_word = sentence[j]
                    
                    # Positive score
                    center_tensor = torch.tensor([center_word])
                    context_tensor = torch.tensor([context_word])
                    pos_score = model(center_tensor, context_tensor)
                    pos_loss = -torch.log(torch.sigmoid(pos_score) + 1e-10)
                    
                    # Negative sampling: random words that are NOT in context
                    neg_words = np.random.randint(0, vocab_size, size=num_negative)
                    neg_tensor = torch.tensor(neg_words)
                    center_expanded = center_tensor.expand(num_negative)
                    neg_scores = model(center_expanded, neg_tensor)
                    neg_loss = -torch.log(torch.sigmoid(-neg_scores) + 1e-10).sum()
                    
                    loss = pos_loss + neg_loss
                    
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()
                    
                    total_loss += loss.item()
        
        print(f"Epoch {epoch+1}, Loss: {total_loss:.4f}")
    
    # The trained embeddings are in model.center_embeddings.weight
    return model.center_embeddings.weight.detach().numpy()
```

### What Word Embeddings Learn

Trained word embeddings capture semantic relationships:

```
king - man + woman = queen
paris - france + italy = rome
bigger - big + small = smaller
```

These relationships emerge automatically from the training data.

---

## 15. Practical NLP Pipeline

```python
import torch
import torch.nn as nn
from collections import Counter
import re

class NLPPipeline:
    """A complete NLP pipeline from raw text to predictions."""
    
    def __init__(self, max_vocab_size=50000, max_seq_length=256):
        self.max_vocab_size = max_vocab_size
        self.max_seq_length = max_seq_length
        self.word_to_idx = {}
        self.idx_to_word = {}
    
    def build_vocabulary(self, texts):
        """Build vocabulary from training texts."""
        word_counts = Counter()
        for text in texts:
            words = self.tokenize(text)
            word_counts.update(words)
        
        # Special tokens
        self.word_to_idx = {"<PAD>": 0, "<UNK>": 1, "<BOS>": 2, "<EOS>": 3}
        
        # Add most common words
        for word, count in word_counts.most_common(self.max_vocab_size - 4):
            self.word_to_idx[word] = len(self.word_to_idx)
        
        self.idx_to_word = {idx: word for word, idx in self.word_to_idx.items()}
        print(f"Vocabulary size: {len(self.word_to_idx)}")
    
    def tokenize(self, text):
        """Simple whitespace tokenization with preprocessing."""
        text = text.lower()
        text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text.split()
    
    def encode(self, text):
        """Convert text to token IDs."""
        words = self.tokenize(text)
        ids = [self.word_to_idx.get(w, 1) for w in words]  # 1 = <UNK>
        
        # Truncate or pad
        if len(ids) > self.max_seq_length:
            ids = ids[:self.max_seq_length]
        length = len(ids)
        ids = ids + [0] * (self.max_seq_length - len(ids))  # 0 = <PAD>
        
        return ids, length
    
    def decode(self, ids):
        """Convert token IDs back to text."""
        words = [self.idx_to_word.get(idx, "<UNK>") for idx in ids if idx != 0]
        return " ".join(words)
```

---

## 16. Summary

You now understand sequence models and NLP:

1. **Sequential data challenges**: Variable length, order matters, long-range dependencies.
2. **RNNs**: Processing sequences with hidden state memory.
3. **Vanishing gradient problem**: Why simple RNNs fail on long sequences.
4. **LSTM**: Three gates (forget, input, output) and cell state for long-term memory.
5. **GRU**: Simplified LSTM with two gates (reset, update).
6. **Bidirectional RNNs**: Processing sequences in both directions.
7. **Seq2Seq**: Encoder-decoder architecture for variable-length input/output.
8. **Attention**: Allowing the decoder to focus on relevant parts of the input.
9. **Text classification and sentiment analysis**: Practical NLP applications.
10. **Language modeling**: Predicting the next word, generating text.
11. **Named Entity Recognition**: Identifying entities in text.
12. **Machine translation**: Converting between languages.
13. **Word2Vec**: Learning word embeddings from context.
14. **Practical NLP pipeline**: Vocabulary, tokenization, encoding, decoding.

---

[<< Previous: Chapter 7 - CNNs](./07_CNN.md) | [Next: Chapter 9 - Transformers and Large Language Models >>](./09_TRANSFORMERS_LLM.md)
